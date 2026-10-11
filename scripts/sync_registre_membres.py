#!/usr/bin/env python3
"""
Synchronise le « registre simplifié des membres » (Excel) et les notes de contact
Mounch avec les adhésions enregistrées dans Mounch (company 114).

Le registre simplifié est le fichier
    Statuts_registre_membres_logo_/registre_membres_LCE_syndicat.xlsx  (feuille « Membres »)
cité par les notes des contacts (« Source : registre simplifié des membres »).

Actions, idempotentes (rien n'est écrit deux fois) :

  1. Note de contact — si la note d'un adhérent est vide, écrire :
       « Membre LCE n°{n} — adhésion le {JJ/MM/AAAA} — {label} — {fonction} — Source : registre simplifié des membres »
     (le n° de membre et la date viennent de l'adhésion Mounch ; la fonction du
     formulaire d'adhésion ou de la note existante.)

  2. Registre Excel — ajouter une ligne pour chaque adhésion absente de la feuille
     « Membres » (colonnes : N° | Nom | Prénom | Mobile | Email | Date d'adhésion |
     Statut | Cotisation 2026 | Commentaires | profession).

Le n° de membre et la date d'adhésion ne sont connus qu'après création de l'adhésion
dans Mounch, et le moteur de workflow Mounch ne sait pas formater une date en JJ/MM/AAAA :
c'est pourquoi cette synchronisation est faite ici, côté script.

Usage :
    python3 sync_registre_membres.py            # simulation : n'écrit rien
    python3 sync_registre_membres.py --apply    # applique (sauvegarde l'Excel avant)

Jeton : lu dans la variable d'environnement MOUNCH_TOKEN (cf. mounch_client.py).
Pour un usage planifié (cron), utiliser un jeton API personnel durable
(`POST /users/me/api-tokens`) plutôt que le jeton OAuth quotidien.
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from copy import copy
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mounch_client import call  # noqa: E402

COMPANY = 114
FORM_ID = 11
SHEET = "Membres"
HEADER_ROW = 5
FIRST_DATA_ROW = 6
SOURCE_LABEL = "registre simplifié des membres"

DEFAULT_XLSX = (
    Path(__file__).resolve().parents[2]
    / "Statuts_registre_membres_logo_"
    / "registre_membres_LCE_syndicat.xlsx"
)


# --------------------------------------------------------------------------- Mounch

def fetch_memberships() -> list[dict]:
    status, body = call("GET", f"/companies/{COMPANY}/association-memberships")
    if status != 200:
        raise RuntimeError(f"association-memberships -> HTTP {status}: {body}")
    return body.get("data", [])


def fetch_contact(contact_id: int) -> dict:
    status, body = call("GET", f"/contacts/{contact_id}")
    if status != 200:
        raise RuntimeError(f"contacts/{contact_id} -> HTTP {status}: {body}")
    return body.get("data", body)


def fetch_fonction_par_email() -> dict[str, str]:
    """Réponses au formulaire d'adhésion : e-mail -> fonction saisie."""
    status, body = call("GET", f"/form-templates/{FORM_ID}/submissions")
    mapping: dict[str, str] = {}
    rows = body if isinstance(body, list) else body.get("data", [])
    for sub in rows:
        data = sub.get("data", {}) if isinstance(sub, dict) else {}
        if not isinstance(data, dict):
            continue
        email = (data.get("ADRESSE_COURRIEL") or "").strip().lower()
        # la note stocke la fonction en minuscules (« CLERC DE NOTAIRE » -> « clerc de notaire »)
        fonction = (data.get("INDIQUEZ_VOTRE_FONCTION_AU_SEIN_DE_L_OFFICE") or "").strip().lower()
        if email and fonction:
            mapping[email] = fonction
    return mapping


# --------------------------------------------------------------------------- helpers

def parse_date(value) -> dt.date | None:
    if not value:
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    txt = str(value).strip().replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(txt).date()
    except ValueError:
        try:
            return dt.datetime.strptime(txt[:10], "%Y-%m-%d").date()
        except ValueError:
            return None


def note_segments(note: str) -> list[str]:
    return [s.strip() for s in (note or "").split(" — ")]


def fonction_from_note(note: str) -> str:
    segs = note_segments(note)
    return segs[3] if len(segs) >= 4 else ""


def label_from_note(note: str) -> str:
    segs = note_segments(note)
    return segs[2] if len(segs) >= 3 else "Membre"


def build_note(numero, started_on: dt.date | None, label: str, fonction: str) -> str:
    date_txt = started_on.strftime("%d/%m/%Y") if started_on else "?"
    parts = [f"Membre LCE n°{numero}", f"adhésion le {date_txt}", label or "Membre"]
    if fonction:
        parts.append(fonction)
    parts.append(f"Source : {SOURCE_LABEL}")
    return " — ".join(parts)


def patch_contact_note(contact: dict, note: str) -> tuple[int, dict]:
    """PATCH en remplacement TOTAL : on renvoie tous les champs scalaires pour ne
    rien écraser (l'API remet à null tout champ scalaire absent du corps)."""
    payload = {
        "firstName": contact.get("firstName"),
        "lastName": contact.get("lastName"),
        "usageName": contact.get("usageName"),
        "birthDate": contact.get("birthDate"),
        "email": contact.get("email"),
        "phone": contact.get("phone"),
        "leadStatus": contact.get("leadStatus"),
        "notes": note,
        "personalAddress": contact.get("personalAddress"),
    }
    return call("PATCH", f"/contacts/{contact.get('id')}", payload)


# --------------------------------------------------------------------------- Excel

def read_existing_numbers(ws) -> dict[int, int]:
    """N° de membre -> ligne, dans la feuille « Membres »."""
    out: dict[int, int] = {}
    for r in range(FIRST_DATA_ROW, ws.max_row + 1):
        val = ws.cell(r, 1).value
        if isinstance(val, int):
            out[val] = r
        elif isinstance(val, str) and val.strip().isdigit():
            out[int(val.strip())] = r
    return out


def append_member_row(ws, numero: int, nom: str, prenom: str, mobile: str, email: str,
                      date_adhesion: dt.date | None, profession: str) -> int:
    row = ws.max_row + 1
    # recopie du style de la ligne précédente (bordures, police, format de date)
    prev = row - 1
    values = [
        numero,
        (nom or "").upper(),
        prenom or "",
        mobile or "",
        email or "",
        dt.datetime(date_adhesion.year, date_adhesion.month, date_adhesion.day) if date_adhesion else None,
        "actif",
        None,
        "membre ",
        profession or "",
    ]
    for c, value in enumerate(values, start=1):
        src = ws.cell(prev, c)
        dst = ws.cell(row, c)
        dst.value = value
        dst.font = copy(src.font)
        dst.fill = copy(src.fill)
        dst.border = copy(src.border)
        dst.alignment = copy(src.alignment) if src.alignment else Alignment()
        dst.number_format = src.number_format
    return row


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="écrire les changements (sinon simulation)")
    ap.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX, help="chemin du registre Excel")
    ap.add_argument("--no-notes", action="store_true", help="ne pas toucher aux notes de contact Mounch")
    ap.add_argument("--no-excel", action="store_true", help="ne pas toucher au registre Excel")
    args = ap.parse_args()

    mode = "APPLICATION" if args.apply else "SIMULATION"
    print(f"=== Synchronisation registre des membres — {mode} ===")

    memberships = fetch_memberships()
    membres = sorted(memberships, key=lambda m: m.get("memberNumber") or 0)
    print(f"{len(membres)} adhésions dans Mounch (company {COMPANY}).")

    fonctions = fetch_fonction_par_email() if not (args.no_notes and args.no_excel) else {}
    print(f"{len(fonctions)} fonctions lues depuis le formulaire {FORM_ID}.")

    # --- 1. notes de contact ---
    notes_written = 0
    for m in membres:
        cid = m.get("memberId")
        numero = m.get("memberNumber")
        contact = fetch_contact(cid)
        note = (contact.get("notes") or "").strip()
        if note:
            continue
        started_on = parse_date(m.get("startedOn"))
        fonction = fonctions.get((contact.get("email") or "").strip().lower(), "")
        new_note = build_note(numero, started_on, "Membre", fonction)
        print(f"  [note] n°{numero} {contact.get('fullName')} -> {new_note!r}")
        if args.apply and not args.no_notes:
            st, body = patch_contact_note(contact, new_note)
            print(f"         PATCH contact {cid} -> HTTP {st}")
            if st not in (200, 202):
                print(f"         !! échec : {body}")
                continue
        notes_written += 1

    # --- 2. registre Excel ---
    rows_added = 0
    if not args.no_excel:
        if not args.xlsx.exists():
            print(f"!! registre introuvable : {args.xlsx}")
            return 2
        wb = openpyxl.load_workbook(args.xlsx)
        ws = wb[SHEET]
        existing = read_existing_numbers(ws)
        print(f"Registre « {SHEET} » : {len(existing)} membres déjà présents.")
        for m in membres:
            numero = m.get("memberNumber")
            if numero in existing:
                continue
            contact = fetch_contact(m.get("memberId"))
            note = (contact.get("notes") or "").strip()
            fonction = fonctions.get((contact.get("email") or "").strip().lower(), "") or fonction_from_note(note)
            print(f"  [excel] + n°{numero} {contact.get('lastName')} {contact.get('firstName')} ({fonction})")
            if args.apply:
                append_member_row(
                    ws, numero,
                    contact.get("lastName", ""), contact.get("firstName", ""),
                    contact.get("phone", ""), contact.get("email", ""),
                    parse_date(m.get("startedOn")), fonction,
                )
            rows_added += 1
        if args.apply and rows_added:
            backup = args.xlsx.with_suffix(f".avant-sync-{dt.date.today():%Y%m%d}.xlsx")
            shutil.copy2(args.xlsx, backup)
            wb.save(args.xlsx)
            print(f"Registre sauvegardé puis mis à jour. Sauvegarde : {backup.name}")

    print(f"\nRésumé : {notes_written} note(s) à écrire, {rows_added} ligne(s) à ajouter au registre.")
    if not args.apply:
        print("(simulation — relancer avec --apply pour appliquer)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
