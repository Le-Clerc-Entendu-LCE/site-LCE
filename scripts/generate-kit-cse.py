#!/usr/bin/env python3
"""Génère le kit technique « Élections du CSE » (A4, 2 pages) du site LCE.

Sortie : public/kit-elections-cse-LCE.pdf
Utilisation : python3 scripts/generate-kit-cse.py
"""

import os

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
LOGO_PATH = os.path.join(PROJECT_DIR, "public", "logo_LCE.png")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "public", "kit-elections-cse-LCE.pdf")

ORANGE = HexColor("#F47920")
ORANGE_PALE = HexColor("#FDF0E6")
MARINE = HexColor("#1A2B4A")
MARINE_PALE = HexColor("#EDF0F5")
SAND = HexColor("#FBF7F2")
GREY = HexColor("#6B7280")
RULE = HexColor("#E5E0D8")
WHITE = colors.white

W, H = A4
LM = 15 * mm
RM = W - 15 * mm
TW = RM - LM

# ── Polices embarquées (accents et symboles garantis) ────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("LCE", os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("LCE-B", os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("LCE-I", os.path.join(FONT_DIR, "LiberationSans-Italic.ttf")))
pdfmetrics.registerFont(TTFont("LCE-BI", os.path.join(FONT_DIR, "LiberationSans-BoldItalic.ttf")))
pdfmetrics.registerFontFamily("LCE", normal="LCE", bold="LCE-B", italic="LCE-I", boldItalic="LCE-BI")

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if os.path.exists(DEJAVU):
    pdfmetrics.registerFont(TTFont("LCE-SYM", DEJAVU))
else:
    pdfmetrics.registerFont(TTFont("LCE-SYM", os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")))


# ── Styles ───────────────────────────────────────────────────────────────────
def style(name, **kw):
    base = dict(fontName="LCE", fontSize=8.4, leading=10.9, textColor=MARINE, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)


S_TITLE = style("title", fontName="LCE-B", fontSize=17.6, leading=19.8, textColor=MARINE)
S_KICKER = style("kicker", fontSize=9.0, leading=11.7, textColor=MARINE)
S_H2 = style("h2", fontName="LCE-B", fontSize=11.6, leading=13.4, textColor=MARINE)
S_H3 = style("h3", fontName="LCE-B", fontSize=8.9, leading=11, textColor=ORANGE)
S_BODY = style("body")
S_BODY_S = style("bodyS", fontSize=7.9, leading=10.1)
S_STEP_NUM = style("stepnum", fontName="LCE-B", fontSize=12.5, leading=13, textColor=ORANGE)
S_STEP_TITLE = style("steptitle", fontName="LCE-B", fontSize=8.8, leading=11, textColor=MARINE)
S_STEP = style("step", fontSize=8.05, leading=10.35)
S_CALLOUT = style("callout", fontSize=8.2, leading=10.6)
S_CHECK = style("check", fontSize=7.6, leading=9.3)
S_TABLE = style("table", fontSize=7.6, leading=9.5)
S_TABLE_B = style("tableB", fontName="LCE-B", fontSize=7.8, leading=9.6)
S_SMALL = style("small", fontSize=6.9, leading=8.7, textColor=GREY)
S_FOOT = style("foot", fontSize=6.6, leading=8.2, textColor=GREY)
S_CONTACT = style("contact", fontSize=8.2, leading=10.6, textColor=WHITE)


def P(text, st=S_BODY):
    return Paragraph(text, st)



def section_title(number, text, space_before=7):
    bar = Table([[""]], colWidths=[2.4 * mm], rowHeights=[6.2 * mm])
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    title = P(f"<font color='#F47920'>{number}.</font> {text}", S_H2)
    t = Table([[bar, title]], colWidths=[2.4 * mm, TW - 2.4 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 3.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), space_before),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (1, 0), (1, 0), 0.6, RULE),
    ]))
    return t


def step(num, title, body):
    left = P(str(num), S_STEP_NUM)
    right = [P(title, S_STEP_TITLE), Spacer(1, 1.2), P(body, S_STEP)]
    t = Table([[left, right]], colWidths=[8.5 * mm, TW - 8.5 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAND),
        ("LINEBEFORE", (0, 0), (0, 0), 2.2, ORANGE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 3.2 * mm),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 2.6 * mm),
        ("RIGHTPADDING", (1, 0), (1, 0), 3.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.8),
    ]))
    return t


def callout(label, body, bg=ORANGE_PALE, bar=ORANGE):
    content = Paragraph(f"<font color='#F47920'><b>{label}</b></font> {body}", S_CALLOUT)
    t = Table([[content]], colWidths=[TW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, 0), 2.2, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
    ]))
    return t


def bullets(items, st=S_BODY_S, gap=1.8, color="#F47920", width=TW):
    """Puces sous forme de paragraphes (pas de tableau imbriqué)."""
    bullet_style = ParagraphStyle(
        st.name + "_bullet", parent=st,
        leftIndent=3.2 * mm, bulletIndent=0,
        bulletFontName="LCE", bulletFontSize=st.fontSize,
        bulletColor=HexColor(color), spaceAfter=gap,
    )
    return [Paragraph(x, bullet_style, bulletText="•") for x in items]


def checkbox(text):
    return Paragraph(
        f"<font name='LCE-SYM' color='#F47920'>☐</font>&nbsp; {text}", S_CHECK
    )


# ── En-têtes et pieds de page ────────────────────────────────────────────────
def draw_first_header(c, doc):
    c.saveState()
    # logo
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, LM, H - 27.5 * mm, width=17 * mm, height=17 * mm,
                    preserveAspectRatio=True, mask="auto")
    c.setFillColor(MARINE)
    c.setFont("LCE-B", 13.2)
    c.drawString(LM + 20 * mm, H - 16.5 * mm, "LE CLERC ENTENDU")
    c.setFillColor(GREY)
    c.setFont("LCE", 7.4)
    c.drawString(LM + 20 * mm, H - 20.4 * mm,
                 "Syndicat des salariés du notariat · IDCC 2205")

    # pastille
    label = "KIT TECHNIQUE · OCTOBRE 2026"
    lw = c.stringWidth(label, "LCE-B", 6.8) + 7 * mm
    c.setFillColor(MARINE)
    c.roundRect(RM - lw, H - 19.2 * mm, lw, 7.2 * mm, 3.6 * mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("LCE-B", 6.8)
    c.drawCentredString(RM - lw / 2, H - 16.8 * mm, label)

    c.setStrokeColor(ORANGE)
    c.setLineWidth(1.4)
    c.line(LM, H - 31 * mm, RM, H - 31 * mm)
    c.restoreState()


def draw_later_header(c, doc):
    c.saveState()
    c.setFillColor(MARINE)
    c.rect(0, H - 14 * mm, W, 14 * mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("LCE-B", 8.4)
    c.drawString(LM, H - 8.2 * mm, "Élections du CSE · le kit technique")
    c.setFont("LCE", 7.2)
    c.drawRightString(RM, H - 8.2 * mm,
                      "LCE — Le Clerc Entendu · syndicat-lce.fr")
    c.setFillColor(ORANGE)
    c.rect(0, H - 15 * mm, W, 1 * mm, fill=1, stroke=0)
    c.restoreState()


def draw_footer(c, doc):
    c.saveState()
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(LM, 12.5 * mm, RM, 12.5 * mm)
    c.setFillColor(GREY)
    c.setFont("LCE", 6.6)
    c.drawString(LM, 8.2 * mm,
                 "LCE · syndicat-lce.fr · sg@syndicat-lce.fr — document d'information générale, "
                 "à jour au 17 octobre 2026")
    c.drawRightString(RM, 8.2 * mm, "Page %d/2" % doc.page)
    c.restoreState()


def on_first(c, doc):
    draw_first_header(c, doc)
    draw_footer(c, doc)


def on_later(c, doc):
    draw_later_header(c, doc)
    draw_footer(c, doc)


# ── Construction du document ────────────────────────────────────────────────
def build():
    doc = BaseDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        leftMargin=LM, rightMargin=15 * mm,
        topMargin=0, bottomMargin=0,
        title="Élections du CSE : le kit technique — LCE",
        author="LE CLERC ENTENDU — Syndicat des salariés du notariat de France",
        subject="Étapes légales, second tour et candidature non syndicale",
        creator="site-LCE / scripts/generate-kit-cse.py",
    )

    frame_first = Frame(LM, 16 * mm, TW, H - 47 * mm, id="first",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_later = Frame(LM, 16 * mm, TW, H - 35 * mm, id="later",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    doc.addPageTemplates([
        PageTemplate(id="first", frames=[frame_first], onPage=on_first),
        PageTemplate(id="later", frames=[frame_later], onPage=on_later),
    ])

    story = []

    # ════════════════════════ PAGE 1 ════════════════════════
    story.append(P("Élections du CSE : ce que vous devez faire,<br/>ce que vous pouvez faire", S_TITLE))
    story.append(Spacer(1, 4))
    story.append(P(
        "Vous venez de recevoir une convocation pour les élections du comité social et "
        "économique dans votre étude. <b>Que devez-vous faire&nbsp;? Que pouvez-vous faire&nbsp;?</b> "
        "LCE vous apporte des éclaircissements.", S_KICKER))
    story.append(Spacer(1, 6))
    story.append(callout(
        "LE CADRE.",
        "Le CSE est obligatoire dans tout office employant au moins 11 salariés pendant "
        "12 mois consécutifs (L.&nbsp;2311-2). Il est élu pour quatre ans (L.&nbsp;2314-33). Dans un "
        "office de 11 à 24 salariés, la délégation comprend <b>1 titulaire et 1 suppléant</b>&nbsp;; "
        "le titulaire dispose de 10&nbsp;heures de délégation par mois (L.&nbsp;2314-1 et "
        "R.&nbsp;2314-1).",
        bg=MARINE_PALE, bar=MARINE))
    story.append(Spacer(1, 7))

    story.append(section_title("1", "Les étapes prévues par la loi", space_before=0))
    story.append(Spacer(1, 3))
    story.append(P(
        "De l'information du personnel au second tour, sept étapes rythment le scrutin. "
        "Les délais ci-dessous sont ceux du Code du travail&nbsp;; le protocole d'accord "
        "préélectoral les précise, sans pouvoir retirer les garanties légales.", S_BODY_S))
    story.append(Spacer(1, 5))

    story.append(step(
        1, "La convocation : l'information du personnel — L. 2314-4",
        "Lorsque le seuil de 11 salariés a été franchi dans les conditions de l'article L. 2311-2 "
        "(effectif atteint pendant 12 mois consécutifs), l'employeur informe le personnel, "
        "<b>tous les quatre ans</b>, de l'organisation des élections <b>par tout moyen permettant de "
        "conférer date certaine à cette information</b> (courrier, courriel avec accusé, remise contre "
        "décharge…). Le document diffusé précise la date envisagée du premier tour&nbsp;: celui-ci doit "
        "se tenir <b>au plus tard le 90<sup>e</sup> jour</b> suivant la diffusion. Selon le document "
        "reçu, «&nbsp;convocation&nbsp;» peut aussi désigner l'invitation à la première réunion de "
        "négociation, encadrée par l'article L.&nbsp;2314-5 (étape 2)."))
    story.append(Spacer(1, 3))

    story.append(step(
        2, "L'invitation des organisations syndicales — L. 2314-5",
        "Sont informées, par tout moyen, de l'organisation des élections et invitées à négocier le "
        "protocole et <b>à établir les listes de leurs candidats</b> les organisations qui satisfont "
        "aux critères de valeurs républicaines, d'indépendance, <b>d'ancienneté de deux ans</b> et de "
        "champ professionnel et géographique. Les organisations reconnues représentatives dans "
        "l'office, celles qui y ont constitué une section et les syndicats affiliés à une organisation "
        "représentative au niveau national et interprofessionnel sont invités <b>par courrier</b>. "
        "L'invitation doit parvenir <b>au plus tard 15 jours avant la première réunion</b> de "
        "négociation. En renouvellement, elle part <b>deux mois avant l'expiration du mandat</b>, et "
        "le premier tour se tient dans la quinzaine qui précède."))
    story.append(Spacer(1, 3))

    story.append(callout(
        "OFFICES DE 11 À 20 SALARIÉS.",
        "L'employeur n'invite les organisations syndicales à négocier que si <b>au moins un salarié "
        "s'est porté candidat dans les 30 jours</b> suivant l'information du personnel (L.&nbsp;2314-5, "
        "dernier alinéa). Ce salarié est protégé contre le licenciement dès que l'employeur a "
        "connaissance de l'imminence de sa candidature (L.&nbsp;2411-7, L.&nbsp;2412-3 et "
        "L.&nbsp;2413-1). C'est souvent le point de départ concret du scrutin dans un office notarial."))
    story.append(Spacer(1, 3))

    story.append(step(
        3, "La négociation du protocole d'accord préélectoral — L. 2314-6 et suivants",
        "Le protocole fixe les modalités concrètes&nbsp;: date, heures et lieu du vote, collèges, "
        "répartition des sièges, liste électorale, <b>date limite de dépôt des listes</b>, propagande, "
        "recours éventuel au vote électronique. Sa validité suppose la signature de la majorité des "
        "organisations ayant négocié, dont les représentatives majoritaires."))
    story.append(Spacer(1, 3))

    story.append(step(
        4, "La date limite de dépôt des listes — le protocole",
        "La loi ne fixe pas de délai unique&nbsp;: <b>c'est le protocole qui arrête la date et les formes "
        "du dépôt</b>, ainsi que les modalités de publication des candidatures. Relevez cette date dès "
        "réception du protocole&nbsp;: une liste déposée hors délai est irrecevable. Le respect de la "
        "parité s'apprécie <b>au jour de cette date limite</b>, même si des candidats se retirent "
        "ensuite (Cass. soc., 21 mai 2025, n°&nbsp;23-21.954)."))
    story.append(Spacer(1, 3))

    story.append(step(
        5, "La liste électorale et sa contestation — R. 2314-24",
        "L'employeur arrête la liste des électeurs et la porte à la connaissance du personnel. "
        "Elle peut être contestée devant le tribunal judiciaire <b>dans les 3 jours</b> suivant sa "
        "publication."))
    story.append(Spacer(1, 3))

    story.append(step(
        6, "Le premier tour — L. 2314-29",
        "Scrutin de liste à deux tours, à la représentation proportionnelle à la plus forte moyenne. "
        "Au premier tour, chaque liste est établie par les organisations syndicales visées à "
        "l'article L.&nbsp;2314-5. Dans le notariat, six organisations sont reconnues représentatives "
        "au niveau de la branche (arrêté du 24 juin 2025)&nbsp;: <b>CFDT, CFE-CGC, CFTC, CGT, FO et "
        "UNSA</b>&nbsp;; d'autres organisations remplissant les conditions de l'article L.&nbsp;2314-5 "
        "peuvent également présenter une liste."))
    story.append(Spacer(1, 3))

    story.append(step(
        7, "Le second tour — L. 2314-29",
        "Si le nombre des votants est inférieur à la moitié des électeurs inscrits, il est procédé "
        "<b>dans un délai de quinze jours</b> à un second tour de scrutin, pour lequel les électeurs "
        "peuvent voter <b>pour des listes autres que celles présentées par une organisation "
        "syndicale</b>. La fiche officielle du ministère du Travail ajoute que ce second tour est "
        "ouvert à toutes les candidatures, syndicales ou non, et qu'il est aussi organisé en cas de "
        "carence ou de sièges non pourvus. Les résultats peuvent être contestés dans les 15 jours "
        "suivant l'élection (R.&nbsp;2314-24)."))

    story.append(Spacer(1, 6))
    story.append(callout(
        "À RETENIR.",
        "Le premier tour est réservé aux listes syndicales. Le second tour est ouvert à toutes les "
        "candidatures, <b>y compris celle d'un salarié qui n'est présenté par aucun syndicat</b>."))

    # ════════════════════════ PAGE 2 ════════════════════════
    story.append(NextPageTemplate("later"))
    story.append(PageBreak())

    story.append(section_title("2", "Second tour : quand est-il ouvert, et qui peut se présenter ?",
                               space_before=0))
    story.append(Spacer(1, 3))
    story.append(P(
        "Selon la fiche officielle du ministère du Travail, le bureau de vote constate l'une des trois "
        "situations suivantes&nbsp;:", S_BODY_S))
    story.append(Spacer(1, 4))

    cases = [
        ("A. Carence de candidature syndicale",
         "Aucune liste présentée par une organisation syndicale habilitée&nbsp;: le bureau de vote prend "
         "acte de la carence dans un procès-verbal et un second tour est <b>obligatoirement</b> organisé. "
         "C'est le cas lorsque <b>aucune des six organisations reconnues représentatives du notariat</b> "
         "(CFDT, CFE-CGC, CFTC, CGT, FO, UNSA) ne présente de candidat au premier tour."),
        ("B. Quorum non atteint",
         "Le nombre des votants (suffrages valablement exprimés, hors blancs et nuls) n'atteint pas la "
         "moitié des électeurs inscrits&nbsp;: un second tour est organisé pour chacun des collèges ou "
         "des scrutins pour lequel le quorum n'a pas été atteint. Il s'apprécie par collège et par "
         "liste&nbsp;: titulaires, suppléants."),
        ("C. Sièges non pourvus",
         "Le quorum est atteint&nbsp;: il est procédé au dépouillement et à l'attribution des sièges. "
         "Un second tour est organisé <b>si des sièges restent non pourvus</b>, les listes présentées au "
         "premier tour étant alors incomplètes."),
    ]
    rows = [[P(f"<b>{t}</b>", S_TABLE_B), P(d, S_TABLE)] for t, d in cases]
    t = Table(rows, colWidths=[48 * mm, TW - 48 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAND),
        ("LINEBEFORE", (0, 0), (0, -1), 1.6, ORANGE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.6, WHITE),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    story.append(P("Ce que le second tour autorise", S_H3))
    story.append(Spacer(1, 2))
    story.append(P(
        "C'est la voie ouverte à un salarié <b>lorsqu'aucun syndicat n'a présenté de liste au premier "
        "tour</b>&nbsp;: il peut alors se présenter lui-même, sans étiquette syndicale.", S_BODY_S))
    story.append(Spacer(1, 2))
    story.extend(bullets([
        "<b>Présenter une candidature non syndicale.</b> La loi ouvre le scrutin à «&nbsp;des listes "
        "autres que celles présentées par une organisation syndicale&nbsp;» (L.&nbsp;2314-29).",
        "<b>Une candidature unique est considérée comme une liste</b>&nbsp;; plusieurs candidatures "
        "uniques non syndiquées peuvent constituer une liste commune (fiche du ministère du Travail).",
        "Respecter la <b>date et les formes de dépôt fixées par le protocole</b>.",
        "<b>Justifier des conditions d'éligibilité</b>&nbsp;: 18 ans révolus et un an d'ancienneté dans "
        "l'entreprise&nbsp;; ne pas être conjoint, partenaire de Pacs, concubin, ascendant, descendant, "
        "frère, sœur ou allié de l'employeur, ni salarié disposant d'une délégation d'autorité "
        "l'assimilant au chef d'entreprise (L.&nbsp;2314-19).",
        "<b>Bénéficier de la protection contre le licenciement</b>&nbsp;: à partir de l'envoi de votre "
        "candidature par lettre recommandée, et pendant six mois, l'employeur doit obtenir "
        "l'autorisation de l'inspection du travail pour vous licencier (L.&nbsp;2411-7).",
        "<b>Point de vigilance&nbsp;:</b> la parité s'impose aux listes syndicales&nbsp;; elle ne "
        "s'applique pas aux candidatures libres du second tour (Cass. soc., 25 nov. 2020, n°&nbsp;19-60.222).",
    ]))
    story.append(Spacer(1, 5))

    story.append(section_title("3", "LCE et la condition d'ancienneté de deux ans"))
    story.append(Spacer(1, 3))
    story.append(P(
        "LCE a déposé ses statuts en mairie le <b>9 février 2026</b>. L'ancienneté de deux ans exigée "
        "par l'article L.&nbsp;2121-1, 4°, du Code du travail ne sera donc acquise qu'en "
        "<b>février 2028</b>.", S_BODY_S))
    story.append(Spacer(1, 4))

    left = [
        P("<b>Jusqu'en février 2028, LCE ne peut pas…</b>", S_TABLE_B),
        Spacer(1, 3),
        *bullets([
            "présenter une liste au premier tour, réservé aux organisations visées à l'article L.&nbsp;2314-5&nbsp;;",
            "créer une section syndicale dans votre office (L.&nbsp;2142-1)&nbsp;;",
            "négocier le protocole en tant qu'organisation invitée.",
        ], st=S_TABLE, gap=2, width=TW / 2 - 8 * mm),
    ]
    right = [
        P("<b>Ce que vous pouvez faire dès maintenant</b>", S_TABLE_B),
        Spacer(1, 3),
        *bullets([
            "vous présenter <b>à titre personnel au second tour</b>, sur une liste non syndicale "
            "(L.&nbsp;2314-29)&nbsp;: aucune ancienneté syndicale ne vous est demandée&nbsp;;",
            "dans un office de 11 à 24 salariés, <b>deux candidatures suffisent</b> (un titulaire et un "
            "suppléant)&nbsp;: le collège est unique et il n'y a qu'un siège de chaque (R.&nbsp;2314-1, "
            "L.&nbsp;2314-11)&nbsp;;",
            "demander à LCE de vous aider à lire le protocole, vérifier votre éligibilité, préparer "
            "votre déclaration et tenir les délais&nbsp;;",
            "adhérer dès maintenant&nbsp;: l'adhésion prépare la section que LCE pourra constituer "
            "à partir de février 2028, dans les offices où elle compte au moins deux adhérents.",
        ], st=S_TABLE, gap=2, width=TW / 2 - 8 * mm),
    ]
    t = Table([[left, right]], colWidths=[TW / 2 - 2 * mm, TW / 2 - 2 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), MARINE_PALE),
        ("BACKGROUND", (1, 0), (1, 0), SAND),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LINEBEFORE", (1, 0), (1, 0), 2, WHITE),
    ]))
    story.append(t)
    story.append(Spacer(1, 4))
    story.append(callout(
        "CE QUE LCE PEUT ET NE PEUT PAS FAIRE.",
        "LCE peut vous informer, vous conseiller et vous accompagner dans votre candidature "
        "personnelle. Elle ne peut pas, avant février 2028, présenter la liste à votre place ni se "
        "présenter comme une organisation invitée à la négociation&nbsp;: <b>votre candidature reste "
        "la vôtre, et c'est précisément ce que le second tour permet</b>."))
    story.append(Spacer(1, 5))

    story.append(section_title("4", "Votre check-list avant le dépôt"))
    story.append(Spacer(1, 3))

    items = [
        "J'ai noté la date de réception de l'information et vérifié que le premier tour était fixé dans les 90 jours (L. 2314-4).",
        "J'ai identifié la première réunion de négociation et vérifié que l'invitation des syndicats a été envoyée 15 jours avant (L. 2314-5).",
        "J'ai demandé le protocole préélectoral et j'ai surligné la date limite de dépôt des listes.",
        "J'ai vérifié la liste électorale ; je sais que je dispose de 3 jours pour la contester (R. 2314-24).",
        "Je sais si le premier tour comporte une ou plusieurs listes syndicales.",
        "Si aucune liste n'est déposée, ou si le quorum n'est pas atteint, je sais que le second tour est ouvert.",
        "Je vérifie mon éligibilité : 18 ans et un an d'ancienneté (L. 2314-19).",
        "Je prépare ma déclaration de candidature et je la dépose dans les formes et délais du protocole.",
        "Je conserve une preuve datée de mon dépôt.",
        "Je préviens LCE : nous relisons ensemble votre dossier avant le dépôt.",
    ]
    half = (len(items) + 1) // 2
    col1 = [checkbox(x) for x in items[:half]]
    col2 = [checkbox(x) for x in items[half:]]
    t = Table([[col1, col2]], colWidths=[TW / 2, TW / 2])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
    ]))
    story.append(t)
    story.append(Spacer(1, 2))

    contact = Table([[
        Paragraph(
            "<b>Un doute, une date qui approche&nbsp;?</b> Écrivez à "
            "<font color='#F47920'><b>sg@syndicat-lce.fr</b></font> ou consultez "
            "<font color='#F47920'><b>syndicat-lce.fr</b></font>. "
            "Ne laissez jamais passer la date de dépôt&nbsp;: une liste tardive est irrecevable.",
            S_CONTACT)
    ]], colWidths=[TW])
    contact.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MARINE),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.4),
    ]))
    story.append(contact)
    story.append(Spacer(1, 4))

    story.append(P(
        "<b>Sources.</b> Code du travail, art. L. 2311-2, L. 2314-4 à L. 2314-10, L. 2314-19, "
        "L. 2314-29, L. 2314-33, L. 2411-7, R. 2314-1, R. 2314-24 ; fiche du ministère du Travail "
        "« CSE&nbsp;: élection de la délégation du personnel » ; service-public.fr, fiche F23513 ; "
        "arrêté du 24 juin 2025 (CCN du notariat, IDCC 2205). Document d'information générale à jour "
        "au 17 octobre 2026&nbsp;; il ne constitue pas un conseil juridique personnalisé.", S_SMALL))

    doc.build(story)
    print(f"PDF généré : {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
