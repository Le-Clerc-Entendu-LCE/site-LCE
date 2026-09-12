#!/usr/bin/env python3
"""
Soumet une veille juridique au workflow de diffusion Mounch.

    export MOUNCH_TOKEN="..."
    python3 scripts/diffuser_veille.py --sujet "Veille juridique du notariat — semaine du …" corps.html

Le workflow #18 se met alors en pause « approbation » : rien ne part tant que
la demande n'est pas approuvée dans Mounch (cloche → Approbations), ou via
`POST /workflow-approvals/{id}/decisions {"decision": "approve"}`.
L'e-mail part ensuite via le connecteur « email LCE » (From sg@syndicat-lce.fr),
adressé à sg@ avec tous les adhérents actifs en copie cachée (BCC).

La liste BCC est dynamique : l'étape `list_association_members` du workflow
la reconstruit à chaque exécution ({{ steps.112.csv }}) — aucune synchro
manuelle n'est nécessaire quand les adhérents changent.
"""
import argparse
import sys

from mounch_client import call

SLUG = "diffusion-de-la-veille-juridique"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sujet", required=True, help="sujet de l'e-mail")
    parser.add_argument("corps_html", help="fichier contenant le HTML complet de l'e-mail")
    args = parser.parse_args()

    with open(args.corps_html, encoding="utf-8") as fh:
        html = fh.read()
    if "<html" not in html.lower():
        print("Le fichier ne ressemble pas à un e-mail HTML complet : abandon.")
        sys.exit(1)
    # Mounch tronque silencieusement CORPS_HTML au-delà de 65 535 octets
    # (colonne SQL TEXT). Constaté sur workflow 28 le 30/08/2026 — signalé
    # à William. Marge de sécurité à 60 000 (UTF-8 accents/emoji multi-octets).
    payload_bytes = len(html.encode("utf-8"))
    if payload_bytes > 60000:
        print(f"HTML trop volumineux : {payload_bytes} octets (limite Mounch ≈ 65 535).")
        print("Réduisez la taille (logos base64, images externes, minifier) avant de relancer.")
        sys.exit(1)

    status, body = call("POST", f"/public/forms/{SLUG}/start")
    assert status == 201, body
    sub = body.get("data", body)["submissionId"]

    status, body = call("POST", f"/public/forms/{SLUG}/submissions/{sub}/answers", {
        "stepIndex": 0, "repetitionIndex": 0,
        "answers": {"SUJET": args.sujet, "CORPS_HTML": html},
        "fieldTimings": {},
    })
    assert status in (200, 202) and not body.get("invalid"), body

    status, body = call("POST", f"/public/forms/{SLUG}/submissions/{sub}/complete")
    assert status == 200, body

    status, body = call("GET", "/workflow-approvals")
    pending = [a for a in body.get("data", []) if a.get("decision") is None]
    print(f"Veille soumise (submission {sub}).")
    if pending:
        print("Approbation(s) en attente :")
        for a in pending:
            print(f"  - pause {a['id']} (exécution {a['workflowExecutionId']}) — "
                  f"approuver dans Mounch ou via POST /workflow-approvals/{a['id']}/decisions")
    else:
        print("La demande d'approbation apparaîtra d'ici quelques secondes dans Mounch.")


if __name__ == "__main__":
    main()
