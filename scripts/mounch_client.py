"""
Mounch API helper for the LCE syndicate site.

Usage:
    from mounch_client import call
    status, body = call("GET", "/form-templates")
    status, body = call("PATCH", "/workflows/10", {"isActive": True})

Token is read from the MOUNCH_TOKEN environment variable so it never
appears in source control. Set it before running:
    export MOUNCH_TOKEN="..."
"""
import os
import json
import sys
import urllib.request
import urllib.error

USER_AGENT = "LCE-Syndicat-Integrator/1.0 (+https://syndicat-lce.fr)"
BASE = "https://api.mounch.wdes.eu/api"

# Association LCE (entreprise 114) : porte les adhésions et les cotisations.
COMPANY_ID = 114


def call(method, path, payload=None, token=None):
    """
    Issue an HTTP request to the Mounch API.

    Returns (status_code, parsed_json_body). On HTTPError the body is
    still parsed when possible — no exception is raised so callers can
    inspect 4xx/5xx payloads.
    """
    token = token or os.environ.get("MOUNCH_TOKEN")
    if not token:
        raise RuntimeError("MOUNCH_TOKEN env var is not set")

    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode() or "{}"
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode() or "{}"
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"_raw": body}


def adhesion_courante(company=COMPANY_ID):
    """(actifs, impayés) pour l'exercice de cotisation courant.

    Le champ `cotisationPaidForCurrentFiscalYear` porte l'état de paiement.
    ⚠️ « Current fiscal year » bascule au 1er janvier : à cette date, TOUS les
    adhérents repassent à « impayé » jusqu'au règlement de la nouvelle année.
    """
    status, body = call("GET", f"/companies/{company}/association-memberships")
    membres = body.get("data", []) if isinstance(body, dict) else []
    actifs = [m for m in membres if m.get("isActive")]
    impayes = [m for m in actifs if not m.get("cotisationPaidForCurrentFiscalYear")]
    return actifs, impayes


def _nom(m):
    return (m.get("memberDisplayName")
            or f"{m.get('memberFirstName','')} {m.get('memberLastName','')}".strip())


def controler_cotisations(company=COMPANY_ID, interactif=True):
    """Avertit si des adhérents n'ont pas réglé leur cotisation.

    Ces adhérents figurent toujours dans la liste de diffusion (le workflow
    n'a pas de filtre par cotisation — demande d'évolution faite à William).
    Ne bloque pas l'envoi : affiche l'avertissement et demande confirmation
    quand la session est interactive.

    Retourne 0 (poursuivre) ou 1 (interrompre sur refus explicite).
    """
    try:
        actifs, impayes = adhesion_courante(company)
    except Exception as exc:                      # réseau, API indisponible
        print(f"⚠️  Contrôle cotisations impossible ({exc}) — diffusion non bloquée.")
        return 0

    total = len(actifs)
    if not impayes:
        print(f"Contrôle cotisations : {total} adhérents actifs, tous à jour.")
        return 0

    print(f"⚠️  Contrôle cotisations : {len(impayes)} adhérent(s) sur {total} "
          f"n'ont pas réglé la cotisation de l'exercice en cours.")
    for m in sorted(impayes, key=lambda x: x.get("memberNumber") or 0):
        print(f"     - n°{m.get('memberNumber','?')} {_nom(m)}")

    # Piège du 1er janvier : le champ bascule pour tout le monde. Si la totalité
    # des adhérents ressort impayée, c'est presque sûrement un changement
    # d'exercice, pas une défaillance générale — ne pas conclure à tort.
    if len(impayes) == total:
        print("     → TOUS les adhérents ressortent impayés. L'exercice de cotisation a")
        print("       probablement basculé (1er janvier) : vérifier avant d'en conclure")
        print("       quoi que ce soit. La liste de diffusion n'est pas filtrée.")

    print("     Ces adhérents recevront quand même l'e-mail : le workflow de diffusion")
    print("     n'a pas (encore) de filtre par cotisation.")

    if interactif and sys.stdin.isatty():
        try:
            rep = input("Diffuser quand même ? [o/N] ").strip().lower()
        except EOFError:
            rep = ""
        if rep not in ("o", "oui", "y", "yes"):
            print("Diffusion interrompue.")
            return 1
    return 0
