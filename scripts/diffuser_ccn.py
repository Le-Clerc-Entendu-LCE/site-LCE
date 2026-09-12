#!/usr/bin/env python3
"""
Soumet un post de la série pédagogique CCN au workflow de diffusion Mounch dédié.

    export MOUNCH_TOKEN="..."
    python3 scripts/diffuser_ccn.py --sujet "LCE — Série CCN #01 : …" corps.html

Le workflow #28 (« Diffusion série pédagogique CCN aux adhérents ») se met en
pause « approbation » : rien ne part tant que la demande n'est pas approuvée
dans Mounch (cloche → Approbations), ou via
`POST /workflow-approvals/{id}/decisions {"decision": "approve"}`.

L'e-mail part ensuite via le connecteur « email LCE » (env 15, from
sg@syndicat-lce.fr), adressé à sg@ avec tous les adhérents actifs en Cci —
liste reconstruite dynamiquement par l'étape `list_association_members`
({{ steps.175.csv }}).

Formulaire dédié : slug `diffusion-serie-pedagogique-ccn` (id 33)
Workflow miroir de la veille (id 18) : id 28.
"""
import argparse
import sys

from mounch_client import call

SLUG = "diffusion-serie-pedagogique-ccn"


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
    # Mounch tronque silencieusement le champ CORPS_HTML au-delà de 65 535 octets
    # (colonne SQL TEXT). Marge de sécurité à 60 000 pour tenir compte de l'UTF-8
    # multi-octets (accents comptent 2, emoji 4).
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
    print(f"Post CCN soumis (submission {sub}).")
    if pending:
        print("Approbation(s) en attente :")
        for a in pending:
            print(f"  - pause {a['id']} (exécution {a['workflowExecutionId']}) — "
                  f"approuver dans Mounch ou via POST /workflow-approvals/{a['id']}/decisions")
    else:
        print("La demande d'approbation apparaîtra d'ici quelques secondes dans Mounch.")


if __name__ == "__main__":
    main()
