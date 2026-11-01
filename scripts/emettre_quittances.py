#!/usr/bin/env python3
"""
Émet les quittances de cotisation annuelle à partir du modèle PDF remplissable
« Recu_cotisation_Le_Clerc_Entendu.pdf ».

Source des données : Mounch (company 114) — adhésions et cotisations marquées payées
(`isPaid`), coordonnées du contact. L'émission n'a lieu que pour les cotisations
**encaissées et pointées** dans Mounch, ce qui respecte la procédure actuelle.

Fonctionnement :
  1. le registre `registre_quittances.csv` (dans le dossier des quittances) mémorise
     les numéros déjà émis. Au premier lancement il est amorcé en relisant les PDF
     existants (n° extrait en haut à droite de la page) — aucune quittance n'est
     réémise ;
  2. le numéro suivant = plus grand numéro du registre + 1 ;
  3. le PDF modèle est rempli, aplati (Ghostscript : le fichier n'est plus modifiable),
     puis déposé sous le nom `{Initiales}_Recu_cotisation_Le_Clerc_Entendu.pdf` ;
  4. une ligne est ajoutée au registre.

Le champ « Signature et cachet du trésorier » reste vide, comme sur les quittances
déjà émises.

Usage :
    python3 emettre_quittances.py                 # simulation (n'écrit rien)
    python3 emettre_quittances.py --apply         # émet les quittances manquantes
    python3 emettre_quittances.py --membre 26 --apply
    python3 emettre_quittances.py --since 2026-10-01 --apply

Jeton : variable d'environnement MOUNCH_TOKEN (cf. mounch_client.py).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mounch_client import call  # noqa: E402

COMPANY = 114
FORM_ID = 11
FISCAL_YEAR_ID = 23          # exercice 2026
PERIODE = "06/2026 - 05/2027"
LIEU = "Gourin"
MODE_LABELS = {"transfer": "Virement", "check": "Chèque", "cash": "Espèces",
               "card": "Carte bancaire", "other": "Autre"}

BASE = Path(__file__).resolve().parents[2]
FOLDER = BASE / "Documents-SIREN-bulletin_adhésion_etc" / "quittances_cotisations_2026"
TEMPLATE = FOLDER / "Recu_cotisation_Le_Clerc_Entendu.pdf"
LEDGER = FOLDER / "registre_quittances.csv"
LEDGER_FIELDS = ["numero", "numero_adherent", "nom", "date_emission", "montant",
                 "reference", "fichier", "origine", "statut", "remplace"]


# --------------------------------------------------------------------------- outils PDF

def receipt_number_from_pdf(path: Path) -> str | None:
    """Numéro de reçu : nombre isolé en haut à droite de la page."""
    try:
        out = subprocess.run(["pdftotext", "-bbox", str(path), "-"],
                             capture_output=True, text=True, check=True).stdout
        page = ET.fromstring(out).find(
            ".//x:page", {"x": "http://www.w3.org/1999/xhtml"})
        width, height = float(page.get("width")), float(page.get("height"))
        found = []
        for w in page.findall(".//x:word", {"x": "http://www.w3.org/1999/xhtml"}):
            txt = (w.text or "").strip()
            if (float(w.get("xMin")) > 0.65 * width and float(w.get("yMin")) < 0.20 * height
                    and re.fullmatch(r"\d{1,4}", txt)):
                found.append(txt)
        return found[0] if found else None
    except Exception:
        return None


def member_number_from_pdf(path: Path) -> str | None:
    try:
        txt = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                             capture_output=True, text=True, check=True).stdout
    except Exception:
        return None
    for line in txt.splitlines():
        m = re.match(r"^([A-ZÉÈÀÂÊÎÔÛÇ][\wÉÈÀÂÊÎÔÛÇ'’\- ]+?)\s{2,}(\d{1,3})\s*$", line.strip())
        if m and not re.search(r"Reçu|SIRET|place|Fait", line):
            return m.group(2)
    return None


def norm(value: str) -> str:
    """Minuscules sans accents, pour rapprocher les noms des PDF et de Mounch."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", (value or "").lower())
                   if unicodedata.category(c) != "Mn")


def pdf_texts() -> dict[Path, str]:
    texts: dict[Path, str] = {}
    for path in FOLDER.glob("*Recu_cotisation_Le_Clerc_Entendu*.pdf"):
        if path.name == TEMPLATE.name or ".annule" in path.name.lower():
            continue
        try:
            texts[path] = norm(subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                capture_output=True, text=True, check=True).stdout)
        except Exception:
            continue
    return texts


def already_receipted(contact: dict, texts: dict[Path, str]) -> Path | None:
    """Quittance existante portant ce membre (rapprochement tolérant aux variantes)."""
    import difflib
    nom, prenom = norm(contact.get("lastName")), norm(contact.get("firstName"))
    if not nom:
        return None
    ini = initials(contact.get("firstName", ""), contact.get("lastName", ""))
    for path, text in texts.items():
        for line in text.splitlines():
            if nom not in line:
                continue
            if prenom and (prenom in line or any(
                    len(mot) >= 4 and difflib.SequenceMatcher(None, prenom, mot).ratio() >= 0.8
                    for mot in line.split())):
                return path
        # repli : mêmes initiales de fichier + nom de famille présent (prénom omis)
        if ini and path.name.startswith(ini + "_") and nom in text:
            return path
    return None


# --------------------------------------------------------------------------- registre

def load_ledger() -> list[dict]:
    if not LEDGER.exists():
        return []
    with LEDGER.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    for row in rows:                      # colonnes ajoutées après coup
        row.setdefault("statut", "emis")
        row.setdefault("remplace", "")
    return rows


def save_ledger(rows: list[dict]) -> None:
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS, delimiter=";",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def name_from_pdf(path: Path) -> str | None:
    try:
        txt = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                             capture_output=True, text=True, check=True).stdout
    except Exception:
        return None
    for line in txt.splitlines():
        m = re.match(r"^([^\d]{4,60}?)\s{2,}\d{1,3}\s*$", line.strip())
        if m and sum(ch.isalpha() for ch in m.group(1)) >= 4 \
                and not re.search(r"Reçu|SIRET|place|Nom et prénom", line):
            return " ".join(m.group(1).split())
    return None


def seed_ledger_from_pdfs() -> list[dict]:
    """Amorce le registre avec les quittances déjà présentes dans le dossier.

    Le « N° d'adhérent » imprimé sur les anciennes quittances n'est pas fiable
    (plusieurs ne correspondent pas au numéro Mounch) : on ne l'enregistre pas,
    le rapprochement se fait par le nom.
    """
    rows: list[dict] = []
    for path in sorted(FOLDER.glob("*Recu_cotisation_Le_Clerc_Entendu*.pdf")):
        if path.name == TEMPLATE.name:
            continue
        numero = receipt_number_from_pdf(path)
        if not numero:
            print(f"  !! numéro illisible, ignoré : {path.name}")
            continue
        rows.append({
            "numero": str(int(numero)),
            "numero_adherent": "",
            "nom": name_from_pdf(path) or "",
            "date_emission": "",
            "montant": "",
            "reference": "",
            "fichier": path.name,
            "origine": "existant",
            "statut": "annule" if ".annule" in path.name.lower() else "emis",
            "remplace": "",
        })
    return rows


# --------------------------------------------------------------------------- Mounch

def fetch_form_addresses() -> dict[str, dict]:
    """Adresses saisies dans le formulaire d'adhésion : e-mail -> adresse."""
    status, body = call("GET", f"/form-templates/{FORM_ID}/submissions")
    if status != 200:
        return {}
    rows = body if isinstance(body, list) else body.get("data", [])
    out: dict[str, dict] = {}
    for sub in rows:
        data = sub.get("data", {}) if isinstance(sub, dict) else {}
        if not isinstance(data, dict):
            continue
        email = (data.get("ADRESSE_COURRIEL") or "").strip().lower()
        adresse = data.get("ADRESSE_PERSO")
        if email and isinstance(adresse, dict) and adresse.get("postalCode"):
            out[email] = adresse
    return out


def fetch_paid_cotisations() -> list[dict]:
    status, body = call("GET", f"/companies/{COMPANY}/association-memberships")
    if status != 200:
        raise RuntimeError(f"association-memberships -> HTTP {status}: {body}")
    form_addresses = fetch_form_addresses()
    out = []
    for m in body.get("data", []):
        status, body2 = call(
            "GET", f"/companies/{COMPANY}/association-memberships/{m['id']}/cotisations")
        if status != 200:
            raise RuntimeError(f"cotisations adhésion {m['id']} -> HTTP {status}")
        for c in body2.get("data", []):
            if not c.get("isPaid") or c.get("fiscalYearId") != FISCAL_YEAR_ID:
                continue
            status, body3 = call("GET", f"/contacts/{m['memberId']}")
            contact = body3.get("data", body3) if status == 200 else {}
            adresse = contact.get("personalAddress") or {}
            if not adresse.get("postalCode"):
                repli = form_addresses.get((contact.get("email") or "").strip().lower())
                if repli:
                    contact["personalAddress"] = repli
            out.append({**m, "cotisation": c, "contact": contact})
            break                      # une quittance par adhésion et par exercice
    return sorted(out, key=lambda x: x.get("memberNumber") or 0)


# --------------------------------------------------------------------------- mise en forme

def fmt_phone(raw: str | None) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("33") and len(digits) == 11:
        digits = "0" + digits[2:]
    if len(digits) == 10:
        return ".".join(digits[i:i + 2] for i in range(0, 10, 2))
    return (raw or "").strip()


def fmt_address(contact: dict) -> str:
    addr = contact.get("personalAddress") or {}
    cp, ville = (addr.get("postalCode") or "").strip(), (addr.get("city") or "").strip()
    if cp and ville:
        return f"{cp} {ville}"
    return (addr.get("formatted") or "").strip()


def initials(prenom: str, nom: str) -> str:
    parts = [p for p in re.split(r"[\s\-]+", (nom or "").upper()) if p]
    return ((prenom or "?")[0] + "".join(p[0] for p in parts)).upper()


def display_name(contact: dict) -> str:
    return f"{(contact.get('lastName') or '').upper()} {contact.get('firstName') or ''}".strip()


# --------------------------------------------------------------------------- émission

def fill_template(values: dict, out_pdf: Path) -> None:
    reader = PdfReader(str(TEMPLATE))
    writer = PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)
    writer._root_object[NameObject("/AcroForm")][NameObject("/NeedAppearances")] = BooleanObject(False)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        writer.write(tmp.name)
        filled = Path(tmp.name)
    try:
        subprocess.run(["gs", "-q", "-o", str(out_pdf), "-sDEVICE=pdfwrite",
                        "-dPDFSETTINGS=/prepress", str(filled)],
                       check=True, capture_output=True)
    finally:
        filled.unlink(missing_ok=True)
    if PdfReader(str(out_pdf)).get_fields():
        raise RuntimeError("le PDF produit contient encore des champs (aplatissement raté)")


def overlay_mention(pdf_path: Path, mention: str) -> None:
    """Incruste une mention en bas de page (espace libre entre signature et pied)."""
    from io import BytesIO
    from reportlab.pdfgen import canvas

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    for page in reader.pages:
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))
        c.setFont("Helvetica-Oblique", 8)
        c.setFillGray(0.35)
        c.drawString(56, 66, mention)
        c.save()
        buffer.seek(0)
        page.merge_page(PdfReader(buffer).pages[0])
        writer.add_page(page)
    with pdf_path.open("wb") as f:
        writer.write(f)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="émettre réellement les quittances")
    ap.add_argument("--membre", type=int, help="ne traiter qu'un numéro d'adhérent")
    ap.add_argument("--since", type=str, help="ne traiter que les paiements depuis AAAA-MM-JJ")
    ap.add_argument("--force", action="store_true",
                    help="émettre même si un fichier aux mêmes initiales existe déjà")
    ap.add_argument("--remplace", type=int, action="append", metavar="ADHERENT",
                    help="rééditer la quittance de cet adhérent (l'ancienne, portant le même "
                         "nom ou les mêmes initiales, est renommée « .annule-nXXX.pdf » et la "
                         "nouvelle porte la mention « Annule et remplace le reçu n° XXX »)")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print(f"!! modèle introuvable : {TEMPLATE}")
        return 2
    if not shutil.which("gs"):
        print("!! Ghostscript (gs) est requis pour aplatir les PDF")
        return 2

    ledger = load_ledger()
    if ledger:
        print(f"Registre : {len(ledger)} quittances déjà émises.")
    else:
        print("Registre absent : amorçage à partir des PDF du dossier…")
        ledger = seed_ledger_from_pdfs()
        print(f"  {len(ledger)} quittances existantes relevées.")
        if args.apply:
            save_ledger(ledger)

    known_numbers = {int(r["numero"]) for r in ledger if r.get("numero", "").isdigit()}
    known_members = {int(r["numero_adherent"]) for r in ledger
                     if str(r.get("numero_adherent", "")).isdigit()}
    next_number = max(known_numbers, default=0) + 1

    cotisations = fetch_paid_cotisations()
    print(f"{len(cotisations)} cotisations payées pour l'exercice {FISCAL_YEAR_ID}.")

    texts = pdf_texts()
    since = dt.date.fromisoformat(args.since) if args.since else None
    remplacements = set(args.remplace or [])
    a_emettre, ignorees = [], []
    for item in cotisations:
        numero_adherent = item.get("memberNumber")
        if args.membre and numero_adherent != args.membre:
            continue
        if numero_adherent in known_members and numero_adherent not in remplacements:
            continue
        existing = already_receipted(item["contact"], texts)
        if existing and numero_adherent not in remplacements:
            ignorees.append((numero_adherent, display_name(item["contact"]), existing.name))
            continue
        if since:
            paid = dt.date.fromisoformat(item["cotisation"]["paidAt"][:10])
            if paid < since:
                continue
        a_emettre.append(item)

    if ignorees:
        print(f"\nDéjà quittancés (rapprochement par nom) : {len(ignorees)}")
        for numero, nom, fichier in ignorees:
            print(f"  n°{numero:>3} {nom:30} -> {fichier}")

    if not a_emettre:
        print("\nRien à émettre : toutes les cotisations payées ont leur quittance.")
        return 0

    print(f"\nÀ émettre ({len(a_emettre)}) — prochain numéro : {next_number:03d}\n")
    used_files = {p.name for p in FOLDER.glob("*.pdf")}
    excludes: list[str] = []
    emises = 0
    for item in a_emettre:
        c, contact = item["cotisation"], item["contact"]
        nom = display_name(contact)
        adresse = fmt_address(contact)
        if not adresse:
            excludes.append(f"n°{item.get('memberNumber')} {nom} : adresse absente dans Mounch "
                            f"et dans le formulaire d'adhésion — quittance non émise")
            continue

        # réédition : retrouver l'ancienne quittance, la mettre de côté
        ancienne: Path | None = None
        ancien_numero: str | None = None
        mention = ""
        if item.get("memberNumber") in remplacements:
            ancienne = already_receipted(contact, texts)
            if ancienne is None:
                cand = FOLDER / f"{initials(contact.get('firstName',''), contact.get('lastName',''))}_Recu_cotisation_Le_Clerc_Entendu.pdf"
                ancienne = cand if cand.exists() else None
            if ancienne is None:
                excludes.append(f"n°{item.get('memberNumber')} {nom} : --remplace demandé "
                                f"mais aucune quittance existante trouvée")
                continue
            ancien_numero = receipt_number_from_pdf(ancienne)
            mention = (f"Annule et remplace le reçu n° {int(ancien_numero):03d}."
                       if ancien_numero else "Annule et remplace le reçu précédent.")

        fname = f"{initials(contact.get('firstName', ''), contact.get('lastName', ''))}_Recu_cotisation_Le_Clerc_Entendu.pdf"
        if ancienne is not None and ancienne.name == fname:
            pass                                  # le nom sera libéré par le renommage
        elif fname in used_files and not args.force:
            excludes.append(f"n°{item.get('memberNumber')} {nom} : un fichier « {fname} » existe "
                            f"déjà mais ne contient pas son nom (quittance incomplète ?) — "
                            f"à vérifier, puis relancer avec --force")
            continue
        elif fname in used_files:
            fname = fname.replace(".pdf", f"_{item.get('memberNumber')}.pdf")

        numero = next_number
        next_number += 1
        paid = dt.date.fromisoformat(c["paidAt"][:10])
        values = {
            "recu_numero": f"{numero:03d}",
            "membre_nom": nom,
            "membre_adherent": str(item.get("memberNumber") or ""),
            "membre_adresse": adresse,
            "membre_email": contact.get("email") or "",
            "membre_tel": fmt_phone(contact.get("phone")),
            "cotis_annee": "2026",
            "cotis_montant": f"{float(c['amountInclTax']):.0f}",
            "cotis_periode": PERIODE,
            "cotis_mode": MODE_LABELS.get(c.get("method"), c.get("method") or "Virement"),
            "cotis_ref": paid.strftime("%d-%m-%y"),
            "lieu": LIEU,
            "date": dt.date.today().strftime("%d/%m/%Y"),
            "signature": "",
        }
        print(f"  n°{numero:03d} | {nom:32} | adhérent {values['membre_adherent']:>3} | "
              f"{values['cotis_montant']} € | {values['cotis_ref']} | {fname}"
              + (f"  [{mention}]" if mention else ""))
        if args.apply:
            if ancienne is not None:
                renommee = ancienne.with_name(
                    ancienne.stem + f".annule-n{int(ancien_numero):03d}.pdf"
                    if ancien_numero else ancienne.stem + ".annule.pdf")
                ancienne.rename(renommee)
                for row in ledger:                # marquer l'ancienne annulée
                    if row.get("fichier") == ancienne.name:
                        row["statut"] = "annule"
                        row["fichier"] = renommee.name
            target = FOLDER / fname
            fill_template(values, target)
            if mention:
                overlay_mention(target, mention)
            ledger.append({"numero": str(numero), "numero_adherent": str(item.get("memberNumber") or ""),
                           "nom": nom, "date_emission": dt.date.today().isoformat(),
                           "montant": values["cotis_montant"], "reference": values["cotis_ref"],
                           "fichier": fname, "origine": "script", "statut": "emis",
                           "remplace": str(int(ancien_numero)) if ancien_numero else ""})
            used_files.add(fname)
            emises += 1

    for message in excludes:
        print(f"  !! {message}")

    if args.apply:
        save_ledger(ledger)
        print(f"\n{emises} quittance(s) émise(s). Registre : {LEDGER.name}")
    else:
        print(f"\n(simulation — relancer avec --apply pour émettre)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
