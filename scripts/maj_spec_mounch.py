#!/usr/bin/env python3
"""Maintient la spec OpenAPI de Mounch à jour et raconte ce qui a changé.

La spec locale (`cahiers_ces_charges_…/mounch-api-docs.json`) fait foi pour
connaître les endpoints, les schémas et les pièges de l'API. Elle vieillit :
ce script la rafraîchit lorsqu'elle a plus de 24 heures et imprime un diff
structurel des évolutions.

Usage :
    python3 scripts/maj_spec_mounch.py            # met à jour si > 24 h
    python3 scripts/maj_spec_mounch.py --force    # force le rafraîchissement
    python3 scripts/maj_spec_mounch.py --check    # ne télécharge pas, dit l'âge
    python3 scripts/maj_spec_mounch.py --diff     # diff local ↔ distant, sans écrire

⚠️ **Garde-fou** : l'URL documentée (`/openapi.json`) ne sert que l'API
**publique** (16 chemins), alors que la spec locale couvre l'API complète
(205 chemins). Écraser la locale avec la publique détruirait l'essentiel :
le script refuse tout remplacement qui ferait perdre plus de 40 % des chemins,
sauf `--force`.

En cas d'échec réseau, la spec locale est conservée intacte et le script sort
en succès : il ne doit jamais bloquer une diffusion.
"""
import argparse
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "LCE-Syndicat-Integrator/1.0 (+https://syndicat-lce.fr)"

# Mounch publie DEUX documents OpenAPI, décrits par le catalogue de découverte :
#   - /openapi.json                  → surface non authentifiée (16 chemins)
#   - /openapi.authenticated.json    → surface authentifiée par jeton (209 chemins)
# C'est le second qui nous intéresse : c'est la spec principale, celle qui
# documente les workflows, contacts, adhésions, formulaires…
URL_DEFAUT = "https://api.mounch.wdes.eu/openapi.authenticated.json"
URL_PUBLIQUE = "https://api.mounch.wdes.eu/openapi.json"
CATALOGUE = "https://api.mounch.wdes.eu/.well-known/api-catalog"

FRAICHEUR = 24 * 3600          # 24 heures
SEUIL_PERTE = 0.40             # au-delà de 40 % de chemins perdus : refus

RACINE = Path(__file__).resolve().parents[2]     # « 20 - SYNDICAT LCE »
SPEC = RACINE / "cahiers_ces_charges_Claude_et_notes_fichiers_md" / "mounch-api-docs.json"


# ─── état local ────────────────────────────────────────────────────────────

def age_heures(p):
    return (time.time() - p.stat().st_mtime) / 3600


def lire(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def horodate(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M")


# ─── téléchargement ────────────────────────────────────────────────────────

def telecharger(url, jeton, timeout=15):
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",          # sans ça, Mounch refuse
        "User-Agent": USER_AGENT,              # sans ça, l'API renvoie 403
        "Authorization": f"Bearer {jeton}" if jeton else "",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        corps = r.read().decode("utf-8")
    return json.loads(corps)


def telecharger_complete(jeton):
    """Spec **complète** = document authentifié + document public fusionnés.

    Les deux documents sont complémentaires, pas imbriqués : l'authentifié ne
    contient pas les routes publiques (`/public/forms/...`), et le public ne
    contient pas l'essentiel. Fusionner est indispensable — nos scripts de
    diffusion utilisent `/public/forms/{slug}/start` pour soumettre un envoi.

    Retourne (spec_fusionnée, provenance) où provenance décrit les deux sources.
    """
    url_auth = decouvrir(jeton)
    auth = telecharger(url_auth, jeton)

    url_pub = os.environ.get("MOUNCH_SPEC_PUBLIQUE", URL_PUBLIQUE)
    try:
        pub = telecharger(url_pub, jeton)
    except Exception as exc:
        return auth, [url_auth], f"public indisponible ({exc})"

    if not (pub.get("paths")):
        return auth, [url_auth], "public vide"

    fusion = json.loads(json.dumps(auth))          # copie profonde
    ajoutes = []
    for chemin, item in (pub.get("paths") or {}).items():
        if chemin not in fusion.setdefault("paths", {}):
            fusion["paths"][chemin] = item
            ajoutes.append(chemin)

    # schémas du document public absents de l'authentifié
    s_auth = fusion.setdefault("components", {}).setdefault("schemas", {})
    for nom, schema in ((pub.get("components") or {}).get("schemas") or {}).items():
        s_auth.setdefault(nom, schema)

    info = fusion.setdefault("info", {})
    info["x-sources"] = [url_auth, url_pub]
    info["x-merged-public-paths"] = sorted(ajoutes)

    return fusion, [url_auth, url_pub], f"{len(ajoutes)} chemin(s) public(s) fusionné(s)"


def decouvrir(jeton):
    """URL de la spec **authentifiée**, lue dans /.well-known/api-catalog.

    Le catalogue liste les deux documents ; on retient celui qui se présente
    comme authentifié par jeton. À défaut, on garde URL_DEFAUT.
    """
    try:
        cat = telecharger(CATALOGUE, jeton)
    except Exception:
        return URL_DEFAUT
    for lien in (cat.get("linkset") or []):
        for desc in (lien.get("service-desc") or []):
            titre = (desc.get("title") or "").lower()
            # attention : « unauthenticated » contient « authenticated »
            if "unauthenticated" in titre or "non-authenticated" in titre:
                continue
            if "authenticated" in titre or "token" in titre:
                return desc.get("href") or URL_DEFAUT
    return URL_DEFAUT


# ─── diff structurel ───────────────────────────────────────────────────────

def _methodes(item):
    return {m for m in item if m.lower() in
            ("get", "post", "put", "patch", "delete", "head", "options")}


def _proprietes(schema):
    return set((schema.get("properties") or {}).keys())


def diff(ancien, nouveau):
    """Retourne (lignes à afficher, nombre total de changements)."""
    lignes = []
    total = 0

    v_old = (ancien.get("info") or {}).get("version")
    v_new = (nouveau.get("info") or {}).get("version")
    if v_old != v_new:
        lignes.append(f"version de l'API : {v_old} → {v_new}")
        total += 1

    p_old = ancien.get("paths") or {}
    p_new = nouveau.get("paths") or {}

    ajoutes = sorted(set(p_new) - set(p_old))
    supprimes = sorted(set(p_old) - set(p_new))
    if ajoutes:
        lignes.append(f"\n+ {len(ajoutes)} endpoint(s) ajouté(s) :")
        for p in ajoutes:
            lignes.append(f"    + {p} [{', '.join(sorted(m.upper() for m in _methodes(p_new[p])))}]")
        total += len(ajoutes)
    if supprimes:
        lignes.append(f"\n- {len(supprimes)} endpoint(s) supprimé(s) :")
        for p in supprimes:
            lignes.append(f"    - {p}")
        total += len(supprimes)

    # méthodes ajoutées/retirées sur les chemins communs
    for p in sorted(set(p_old) & set(p_new)):
        m_old, m_new = _methodes(p_old[p]), _methodes(p_new[p])
        for m in sorted(m_new - m_old):
            lignes.append(f"    + {p} [{m.upper()}]")
            total += 1
        for m in sorted(m_old - m_new):
            lignes.append(f"    - {p} [{m.upper()}]")
            total += 1

    s_old = (ancien.get("components") or {}).get("schemas") or {}
    s_new = (nouveau.get("components") or {}).get("schemas") or {}

    s_ajoutes = sorted(set(s_new) - set(s_old))
    s_supprimes = sorted(set(s_old) - set(s_new))
    if s_ajoutes:
        lignes.append(f"\n+ {len(s_ajoutes)} schéma(s) ajouté(s) : {', '.join(s_ajoutes[:12])}"
                      + (" …" if len(s_ajoutes) > 12 else ""))
        total += len(s_ajoutes)
    if s_supprimes:
        lignes.append(f"\n- {len(s_supprimes)} schéma(s) supprimé(s) : {', '.join(s_supprimes[:12])}"
                      + (" …" if len(s_supprimes) > 12 else ""))
        total += len(s_supprimes)

    # champs ajoutés/retirés dans les schémas communs
    modifications = []
    for nom in sorted(set(s_old) & set(s_new)):
        po, pn = _proprietes(s_old[nom]), _proprietes(s_new[nom])
        if po != pn:
            morceaux = []
            if pn - po:
                morceaux.append("+" + ", ".join(sorted(pn - po)))
            if po - pn:
                morceaux.append("−" + ", ".join(sorted(po - pn)))
            modifications.append(f"    ~ {nom} : {' / '.join(morceaux)}")
    if modifications:
        lignes.append(f"\n~ {len(modifications)} schéma(s) modifié(s) :")
        lignes.extend(modifications)
        total += len(modifications)

    return lignes, total


# ─── programme ─────────────────────────────────────────────────────────────

def say(silencieux, texte=""):
    if not silencieux:
        print(texte)


def executer(force=False, check=False, diff_only=False, silencieux=False):
    """Cœur du programme. Retourne un code de sortie.

    En mode silencieux (appel automatique depuis mounch_client), rien n'est
    affiché sauf lorsqu'une mise à jour a effectivement été appliquée : le diff
    est alors imprimé, comme demandé.
    """
    if not SPEC.exists():
        say(silencieux, f"✗ spec absente : {SPEC}")
        return 1

    age = age_heures(SPEC)
    taille = SPEC.stat().st_size
    spec_old = lire(SPEC)
    n_paths = len(spec_old.get("paths") or {})

    if check:
        etat = "à jour" if age < 24 else "PÉRIMÉE"
        print(f"Spec Mounch : {SPEC}")
        print(f"  modifiée le {horodate(SPEC.stat().st_mtime)} — {age:.1f} h — {etat}")
        print(f"  {n_paths} chemins, "
              f"{len((spec_old.get('components') or {}).get('schemas') or {})} schémas, "
              f"{taille // 1024} ko")
        return 0

    if age < 24 and not (force or diff_only):
        say(silencieux, f"Spec Mounch à jour ({age:.1f} h, {n_paths} chemins) — "
                        "rien à télécharger.")
        return 0

    jeton = os.environ.get("MOUNCH_TOKEN", "")
    say(silencieux, f"Spec vieille de {age:.1f} h — téléchargement des deux documents Mounch")

    try:
        if os.environ.get("MOUNCH_SPEC_URL"):
            spec_new = telecharger(os.environ["MOUNCH_SPEC_URL"], jeton)
            provenance = f"source imposée : {os.environ['MOUNCH_SPEC_URL']}"
        else:
            spec_new, sources, provenance = telecharger_complete(jeton)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        say(silencieux, f"⚠️  téléchargement impossible ({exc}) — spec locale conservée intacte.")
        return 0
    say(silencieux, f"  {provenance}")

    n_new = len(spec_new.get("paths") or {})
    if not n_new:
        say(silencieux, "⚠️  la réponse ne contient aucun chemin — ce n'est pas une spec "
                        "valide. Spec locale conservée.")
        return 0

    # garde-fou : ne jamais remplacer une spec riche par un sous-ensemble
    if n_new < n_paths * (1 - SEUIL_PERTE) and not force:
        say(silencieux,
            f"⚠️  GARDE-FOU : la spec téléchargée ne compte que {n_new} chemins "
            f"contre {n_paths} en local ({100 * n_new / n_paths:.0f} %).\n"
            "    C'est probablement l'API publique, pas la spec complète.\n"
            "    Spec locale conservée. Utiliser --force pour passer outre.")
        return 0

    lignes, total = diff(spec_old, spec_new)

    if diff_only:
        print(f"Distant : {n_new} chemins. Local : {n_paths} chemins.")
        print("Aucun changement structurel." if not total
              else f"\n{total} changement(s) :\n" + "\n".join(lignes))
        return 0

    if not total:
        say(silencieux, f"Spec identique ({n_new} chemins) — fichier local conservé tel quel.")
        os.utime(SPEC, None)          # on rajeunit pour ne pas re-télécharger demain
        return 0

    # sauvegarde puis écriture
    sauvegarde = SPEC.with_name(f"mounch-api-docs.avant-{datetime.now():%Y-%m-%d_%H%M}.json")
    shutil.copy2(SPEC, sauvegarde)

    with open(SPEC, "w", encoding="utf-8") as f:
        json.dump(spec_new, f, ensure_ascii=False, indent=1)

    # une mise à jour est toujours signalée, même en mode silencieux
    print(f"\n[Mounch] spec mise à jour — {total} changement(s) :")
    print("\n".join(lignes))
    print(f"Écrit : {SPEC.name} ({SPEC.stat().st_size // 1024} ko) — "
          f"sauvegarde : {sauvegarde.name}\n")
    return 0


def verifier_auto():
    """Appelée une fois par mounch_client. Ne lève jamais, ne bloque jamais."""
    if os.environ.get("MOUNCH_SPEC_CHECK", "1") == "0":
        return
    try:
        executer(silencieux=True)
    except Exception as exc:                      # jamais bloquant
        print(f"[Mounch] vérification de la spec impossible : {exc}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="rafraîchir même si < 24 h")
    ap.add_argument("--check", action="store_true", help="afficher l'âge, ne rien télécharger")
    ap.add_argument("--diff", action="store_true", help="afficher le diff sans rien écrire")
    args = ap.parse_args()
    return executer(force=args.force, check=args.check, diff_only=args.diff)


if __name__ == "__main__":
    sys.exit(main())
