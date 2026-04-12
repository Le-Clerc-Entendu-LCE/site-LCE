#!/usr/bin/env python3
"""Generate the fillable PDF bulletin d'adhésion for LCE."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
LOGO_PATH = os.path.join(PROJECT_DIR, "public", "logo_LCE.png")
OUTPUT_PATH = os.path.join(
    PROJECT_DIR, "public", "bulletin-adhesion-LCE-remplissable.pdf"
)

ORANGE = HexColor("#F47920")
MARINE = HexColor("#1A2B4A")
FIELD_BG = HexColor("#F5F5F5")
FIELD_BORDER = HexColor("#CCCCCC")

W, H = A4
LM = 25 * mm
RM = W - 25 * mm
TW = RM - LM


def tf(c, name, x, y, w, h=16, maxlen=200):
    """Text field using acroForm API."""
    c.acroForm.textfield(
        name=name, x=x, y=y, width=w, height=h,
        fillColor=FIELD_BG, borderColor=FIELD_BORDER, textColor=MARINE,
        fontSize=9, borderWidth=0.5, maxlen=maxlen,
        annotationFlags="print", relative=False,
    )


def cb(c, name, x, y, size=12):
    """Checkbox using acroForm API."""
    c.acroForm.checkbox(
        name=name, x=x, y=y, size=size,
        fillColor=white, borderColor=FIELD_BORDER,
        buttonStyle="check", borderWidth=0.5,
        annotationFlags="print", relative=False,
    )


def footer(c, page_num):
    c.saveState()
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(HexColor("#999999"))
    c.drawString(LM, 12 * mm,
        f"Bulletin adhésion syndicat de salariés - Le Clerc Entendu — page {page_num}/2")
    c.restoreState()


def label(c, x, y, text, font="Helvetica", size=10):
    c.setFont(font, size)
    c.setFillColor(MARINE)
    c.drawString(x, y, text)


def heading(c, x, y, text):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ORANGE)
    c.drawString(x, y, text)
    c.setFillColor(MARINE)
    c.setFont("Helvetica", 10)


def build_pdf():
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle("Bulletin d'adhésion — Le Clerc Entendu")
    c.setAuthor("LE CLERC ENTENDU — Syndicat des Salariés du Notariat de France")

    # ────────────── PAGE 1 ──────────────
    y = H - 30 * mm

    # Logo
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, RM - 35 * mm, y - 10 * mm, width=35 * mm,
                     height=35 * mm, preserveAspectRatio=True, mask="auto")

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(ORANGE)
    title = "BULLETIN D'ADHÉSION"
    tw = c.stringWidth(title, "Helvetica-Bold", 16)
    cx = W / 2
    c.drawCentredString(cx, y, title)
    c.setStrokeColor(ORANGE)
    c.setLineWidth(1.2)
    c.line(cx - tw / 2, y - 3, cx + tw / 2, y - 3)

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(MARINE)
    c.drawCentredString(cx, y, 'Syndicat national des salariés du notariat « Le Clerc entendu »')

    # ── Identité ──
    y -= 18 * mm
    label(c, LM, y, "Je soussigné(e),")

    y -= 14 * mm
    label(c, LM, y + 4, "Nom :")
    tf(c, "nom", LM + 22 * mm, y - 2, TW - 22 * mm)

    y -= 10 * mm
    label(c, LM, y + 4, "Prénom :")
    tf(c, "prenom", LM + 22 * mm, y - 2, TW - 22 * mm)

    y -= 10 * mm
    label(c, LM, y + 4, "Nom de naissance (le cas échéant) :")
    tf(c, "nom_naissance", LM + 70 * mm, y - 2, TW - 70 * mm)

    y -= 10 * mm
    label(c, LM, y + 4, "Date de naissance :")
    tf(c, "jour_naiss", LM + 40 * mm, y - 2, 12 * mm, maxlen=2)
    label(c, LM + 54 * mm, y + 4, "/")
    tf(c, "mois_naiss", LM + 57 * mm, y - 2, 12 * mm, maxlen=2)
    label(c, LM + 71 * mm, y + 4, "/")
    tf(c, "annee_naiss", LM + 74 * mm, y - 2, 20 * mm, maxlen=4)

    y -= 10 * mm
    label(c, LM, y + 4, "Adresse personnelle :")
    tf(c, "adresse1", LM + 42 * mm, y - 2, TW - 42 * mm)

    y -= 10 * mm
    tf(c, "adresse2", LM, y - 2, TW)

    y -= 10 * mm
    label(c, LM, y + 4, "Code postal :")
    tf(c, "cp", LM + 28 * mm, y - 2, 25 * mm, maxlen=5)
    label(c, LM + 58 * mm, y + 4, "Ville :")
    tf(c, "ville", LM + 72 * mm, y - 2, TW - 72 * mm)

    y -= 10 * mm
    label(c, LM, y + 4, "Téléphone portable :")
    tf(c, "tel", LM + 42 * mm, y - 2, 60 * mm, maxlen=20)

    y -= 10 * mm
    label(c, LM, y + 4, "Courriel personnel :")
    tf(c, "email", LM + 42 * mm, y - 2, TW - 42 * mm)

    # ── Situation professionnelle ──
    y -= 16 * mm
    heading(c, LM, y, "Situation professionnelle :")

    y -= 12 * mm
    label(c, LM, y + 4, "Entreprise / Office notarial :")
    tf(c, "office", LM + 55 * mm, y - 2, TW - 55 * mm)

    y -= 10 * mm
    label(c, LM, y + 4, "Adresse professionnelle :")
    tf(c, "adr_pro1", LM + 50 * mm, y - 2, TW - 50 * mm)

    y -= 10 * mm
    tf(c, "adr_pro2", LM, y - 2, TW)

    y -= 10 * mm
    label(c, LM, y + 4, "Code postal :")
    tf(c, "cp_pro", LM + 28 * mm, y - 2, 25 * mm, maxlen=5)
    label(c, LM + 58 * mm, y + 4, "Ville :")
    tf(c, "ville_pro", LM + 72 * mm, y - 2, TW - 72 * mm)

    y -= 10 * mm
    label(c, LM, y + 4, "Fonction / emploi :")
    tf(c, "fonction", LM + 38 * mm, y - 2, TW - 38 * mm)

    y -= 10 * mm
    label(c, LM, y + 4, "Type de contrat :")
    tf(c, "contrat", LM + 35 * mm, y - 2, 35 * mm)
    label(c, LM + 72 * mm, y + 4, "(CDI / CDD / Apprenti / Autre)", "Helvetica", 7.5)

    y -= 10 * mm
    label(c, LM, y + 4, "Temps de travail :")
    tf(c, "temps_travail", LM + 38 * mm, y - 2, 20 * mm, maxlen=3)
    label(c, LM + 60 * mm, y + 4, "%")

    # ── Cotisation ──
    y -= 16 * mm
    heading(c, LM, y, "Cotisation syndicale :")

    y -= 12 * mm
    label(c, LM, y + 4, "Montant de la cotisation annuelle / mensuelle :")
    tf(c, "cotisation", LM + 90 * mm, y - 2, 25 * mm, maxlen=10)
    label(c, LM + 117 * mm, y + 4, "€")

    y -= 12 * mm
    label(c, LM, y + 4, "Mode de paiement (cocher) :")

    y -= 10 * mm
    cb(c, "pmt_cheque", LM + 10 * mm, y - 1)
    label(c, LM + 16 * mm, y + 2, "Chèque")

    cb(c, "pmt_virement", LM + 50 * mm, y - 1)
    label(c, LM + 56 * mm, y + 2, "Virement")

    cb(c, "pmt_sepa", LM + 90 * mm, y - 1)
    label(c, LM + 96 * mm, y + 2, "Prélèvement SEPA")

    y -= 10 * mm
    cb(c, "pmt_autre", LM + 10 * mm, y - 1)
    label(c, LM + 16 * mm, y + 2, "Autre :")
    tf(c, "pmt_autre_txt", LM + 32 * mm, y - 3, 50 * mm)

    footer(c, 1)
    c.showPage()

    # ────────────── PAGE 2 ──────────────
    y = H - 30 * mm

    heading(c, LM, y, "Déclarations de l'adhérent(e) :")

    y -= 10 * mm
    label(c, LM, y, "En signant le présent bulletin :")

    bullets = [
        "Je demande mon adhésion au syndicat « Le Clerc entendu ».",
        ("Je déclare avoir pris connaissance de l'objet du syndicat, de ses statuts et, "
         "le cas échéant,"),
        "de son règlement intérieur, et les accepter sans réserve.",
        "Je m'engage à acquitter régulièrement ma cotisation syndicale.",
    ]

    y -= 10 * mm
    label(c, LM + 6 * mm, y, "•")
    label(c, LM + 12 * mm, y, bullets[0])

    y -= 8 * mm
    label(c, LM + 6 * mm, y, "•")
    label(c, LM + 12 * mm, y, bullets[1])
    y -= 5 * mm
    label(c, LM + 14 * mm, y, bullets[2])

    y -= 8 * mm
    label(c, LM + 6 * mm, y, "•")
    label(c, LM + 12 * mm, y, bullets[3])

    # ── RGPD ──
    y -= 18 * mm
    c.setFont("Helvetica-BoldOblique", 9)
    c.setFillColor(ORANGE)
    c.drawString(LM, y, "Traitement des données personnelles :")
    c.setFillColor(MARINE)
    c.setFont("Helvetica-Oblique", 7.5)

    rgpd_text = (
        "Les informations recueillies sont nécessaires à la gestion de mon adhésion "
        "(tenue du fichier des adhérents, envoi d'informations syndicales, gestion de la cotisation). "
        "Elles sont réservées à l'usage interne du syndicat et ne sont pas communiquées à des tiers "
        "non autorisés (fichiers adhérents, inscriptions aux formations, tenue de réunions, colloques, "
        "évènements, gestion des cotisations…). La base légale de leur traitement est l'intérêt légitime, "
        "car elles permettent de mettre en œuvre nos activités syndicales au service de nos adhérents, "
        "mais aussi de l'ensemble des salariés conformément à la notion de représentativité syndicale. "
        "Le recueil de ces données est obligatoire, notamment en ce qu'elles nous permettent d'animer "
        "notre réseau syndical sans quoi il nous serait impossible de mener à bien notre activité et de "
        "procéder à votre adhésion. Elles font l'objet d'un traitement informatisé, éventuellement à "
        "l'aide d'un sous-traitant moyennant les garanties appropriées, et ne sont pas commercialisées. "
        "Nous les conservons en base active tout au long de l'adhésion, puis pendant deux ans à compter "
        "de la perte de qualité d'adhérent. Intervient ensuite leur archivage intermédiaire pour une durée "
        "de trois ans. Elles sont alors détruites. Vous pouvez exercer vos droits d'accès, de "
        "rectification, d'opposition, d'effacement et à la limitation du traitement en nous écrivant à "
        "l'adresse ci-dessus mentionnée dans l'encadré ou par mail. Conformément à la réglementation "
        "sur la protection des données, je dispose d'un droit d'accès, de rectification et d'opposition "
        "pour les données me concernant, que je peux exercer en m'adressant au syndicat. Si vous estimez, "
        "après nous avoir contactés, que vos droits « Informatique et Libertés » ne sont pas respectés, "
        "vous pouvez adresser une réclamation à la CNIL."
    )

    y -= 6 * mm
    words = rgpd_text.split()
    line = ""
    for word in words:
        test = line + (" " if line else "") + word
        if c.stringWidth(test, "Helvetica-Oblique", 7.5) < TW:
            line = test
        else:
            c.drawString(LM, y, line)
            y -= 4 * mm
            line = word
    if line:
        c.drawString(LM, y, line)
        y -= 4 * mm

    # ── Signature ──
    y -= 16 * mm
    c.setFont("Helvetica", 10)
    c.setFillColor(MARINE)
    label(c, LM, y + 4, "Fait sur deux pages à")
    tf(c, "fait_a", LM + 44 * mm, y - 2, 50 * mm)
    label(c, LM + 97 * mm, y + 4, ", le")
    tf(c, "fait_jour", LM + 105 * mm, y - 2, 10 * mm, maxlen=2)
    label(c, LM + 116 * mm, y + 4, "/")
    tf(c, "fait_mois", LM + 119 * mm, y - 2, 10 * mm, maxlen=2)
    label(c, LM + 130 * mm, y + 4, "/")
    tf(c, "fait_annee", LM + 133 * mm, y - 2, 18 * mm, maxlen=4)

    y -= 18 * mm
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(MARINE)
    c.drawString(LM, y, 'Dater, écrire la mention « lu et approuvé » et signer')

    y -= 14 * mm
    label(c, LM, y + 4, "Signature de l'adhérent(e) :")

    y -= 6 * mm
    tf(c, "signature", LM + 10 * mm, y - 30, TW - 20 * mm, h=35, maxlen=1000)

    footer(c, 2)
    c.save()
    print(f"PDF remplissable créé : {OUTPUT_PATH}")
    print(f"Taille : {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")


if __name__ == "__main__":
    build_pdf()
