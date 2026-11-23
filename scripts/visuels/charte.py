#!/usr/bin/env python3
"""Charte visuelle de la série pédagogique CCN — Le Clerc Entendu.

Un seul jeu de règles pour tous les visuels, afin que la série garde un fil
conducteur d'un épisode à l'autre :

  - même fond crème, même bandeau orange en haut, même pied de page ;
  - un « chip » de module en haut à droite (MODULE 2 — ENTRÉE DANS L'EMPLOI…) ;
  - trois archétypes seulement, pour éviter la dispersion :
      * rangees()     : liste de lignes avec libellé + badge (ex. diplôme → niveau)
      * formule()     : une équation en grand (ex. coefficient × point = minimum)
      * paliers()     : progression par étapes (ex. +25 % / +50 %)
  - typographie : Liberation Serif Bold pour les titres, Liberation Sans pour le reste
    (équivalents libres de Georgia / Arial, cohérents avec les e-mails).

Utilisation :
    from charte import nouveau, entete, pied, rangees, formule, paliers, enregistrer

    img, d = nouveau()
    carte = entete(d, "MODULE 2", "Votre diplôme = un niveau", "Un plancher garanti.")
    y = rangees(d, carte, [("BTS notariat", "T.1", "technicien"), …])
    pied(d, "BTS et licence pro : technicien, pas cadre.", "arrêté du 22 septembre 2017")
    enregistrer(img, "Post12", "visuel_....jpeg")
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = H = 1254

# Palette LCE
BG = (246, 243, 238)
NAVY = (26, 43, 74)
ORANGE = (200, 81, 10)
GREY = (110, 110, 110)
GREY_LIGHT = (190, 190, 190)
RULE = (214, 208, 199)
WHITE = (255, 255, 255)

# Dégradé des badges (du plus clair au plus foncé)
TONS = {
    "clair": (183, 203, 222),
    "moyen": (120, 155, 190),
    "foncé": (22, 36, 62),
    "orange": ORANGE,
}

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SANS = f"{FONT_DIR}/LiberationSans-Regular.ttf"
SANS_B = f"{FONT_DIR}/LiberationSans-Bold.ttf"
SERIF_B = f"{FONT_DIR}/LiberationSerif-Bold.ttf"


def _f(path, size):
    return ImageFont.truetype(path, size)


def nouveau():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def _wrap(d, texte, font, largeur):
    mots, lignes, courant = texte.split(), [], ""
    for m in mots:
        essai = (courant + " " + m).strip()
        if d.textlength(essai, font=font) <= largeur:
            courant = essai
        else:
            if courant:
                lignes.append(courant)
            courant = m
    if courant:
        lignes.append(courant)
    return lignes


def entete(d, module, titre, sous_titre, marge=76):
    """Bandeau + titre + sous-titre. Retourne l'ordonnée où commencer le corps."""
    d.rectangle([0, 0, W, 14], fill=ORANGE)
    d.text((marge, 56), "S Y N D I C A T   L E   C L E R C   E N T E N D U",
           font=_f(SANS_B, 22), fill=ORANGE)

    # chip de module, aligné à droite
    fm = _f(SANS_B, 18)
    tw = d.textlength(module, font=fm)
    x1 = W - marge
    x0 = x1 - tw - 32
    d.rounded_rectangle([x0, 46, x1, 82], radius=18, outline=NAVY, width=2)
    d.text(((x0 + x1) / 2, 64), module, font=fm, fill=NAVY, anchor="mm")

    ft = _f(SERIF_B, 58)
    y = 100
    for ligne in _wrap(d, titre, ft, W - 2 * marge):
        d.text((marge, y), ligne, font=ft, fill=NAVY)
        y += 62

    fs = _f(SANS, 25)
    y += 8
    for ligne in _wrap(d, sous_titre, fs, W - 2 * marge):
        d.text((marge, y), ligne, font=fs, fill=GREY)
        y += 33
    return y + 34


def rangees(d, y, items, hauteur=112, ecart=14, marge=76, colonne_valeur=None):
    """Liste de lignes : (libelle, badge, ton, sous_libelle|None) ou (libelle, valeur_droite)."""
    x0, x1 = marge, W - marge
    for it in items:
        libelle, badge = it[0], it[1]
        ton = it[2] if len(it) > 2 and it[2] in TONS else "clair"
        sous = it[3] if len(it) > 3 else None

        d.rounded_rectangle([x0, y, x1, y + hauteur], radius=12, fill=WHITE)
        fy = y + hauteur // 2 - (14 if sous else 0)
        d.text((x0 + 24, fy), libelle, font=_f(SANS, 27), fill=NAVY, anchor="lm")
        if sous:
            d.text((x0 + 24, fy + 34), sous, font=_f(SANS, 20), fill=GREY, anchor="lm")

        col = TONS[ton]
        lum = (0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]) / 255
        fg = WHITE if lum < 0.62 else NAVY
        bw = max(104, int(d.textlength(str(badge), font=_f(SANS_B, 34))) + 44)
        bx1 = x1 - 24
        bx0 = bx1 - bw
        d.rounded_rectangle([bx0, y + 14, bx1, y + hauteur - 14], radius=10, fill=col)
        d.text(((bx0 + bx1) / 2, y + hauteur // 2), str(badge),
               font=_f(SANS_B, 34), fill=fg, anchor="mm")
        y += hauteur + ecart
    return y


def formule(d, y, gauche, operateur, droite, resultat, marge=76, note=None):
    """Grande équation : gauche op droite = résultat."""
    hauteur = 340 if note else 280
    d.rounded_rectangle([marge, y, W - marge, y + hauteur], radius=14, fill=NAVY)

    f = _f(SANS_B, 42)
    items = [(gauche, WHITE), (operateur, ORANGE), (droite, WHITE)]
    total = sum(d.textlength(t, font=f) for t, _ in items) + 90
    x = (W - total) / 2
    for t, col in items:
        d.text((x, y + 88), t, font=f, fill=col, anchor="lm")
        x += d.textlength(t, font=f) + 45

    # la ligne de résultat, sur toute la largeur disponible
    fr = _f(SANS_B, 46)
    ligne = "=  " + resultat
    while d.textlength(ligne, font=fr) > (W - 2 * marge - 60) and fr.size > 26:
        fr = _f(SANS_B, fr.size - 2)
    d.text((W / 2, y + 178), ligne, font=fr, fill=ORANGE, anchor="mm")

    if note:
        d.text((W / 2, y + 262), note, font=_f(SANS, 22),
               fill=(190, 200, 215), anchor="mm")
    return y + hauteur + 26


def paliers(d, y, items, marge=76, hauteur=230):
    """Progression : (titre, detail, ton). Le titre se réduit pour tenir dans la carte."""
    x0, x1 = marge, W - marge
    n = len(items)
    largeur = (x1 - x0 - (n - 1) * 16) / n
    for i, (titre, detail, ton) in enumerate(items):
        col = TONS.get(ton, "clair")
        lum = (0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]) / 255
        fg = WHITE if lum < 0.62 else NAVY
        xa = x0 + i * (largeur + 16)
        d.rounded_rectangle([xa, y, xa + largeur, y + hauteur], radius=12, fill=col)

        # le titre s'ajuste à la largeur disponible (défaut constaté : débordement)
        # il peut contenir un saut de ligne explicite : on mesure ligne par ligne
        lignes_titre = titre.split("\n")
        taille = 46
        ft = _f(SANS_B, taille)
        while (max(d.textlength(l, font=ft) for l in lignes_titre) > largeur - 28
               and taille > 20):
            taille -= 2
            ft = _f(SANS_B, taille)
        haut_titre = 96 - (len(lignes_titre) - 1) * taille // 2
        for k, ligne in enumerate(lignes_titre):
            d.text((xa + largeur / 2, y + haut_titre + k * taille),
                   ligne, font=ft, fill=fg, anchor="mm")

        fd = _f(SANS, 21)
        for k, ligne in enumerate(_wrap(d, detail, fd, largeur - 28)):
            d.text((xa + largeur / 2, y + 160 + k * 27), ligne,
                   font=fd, fill=fg, anchor="mm")
    return verifier(y + hauteur + 26, "paliers")


LIMITE_BAS = H - 150   # au-delà, le corps mord sur le pied de page


def verifier(y, ou="corps"):
    """Signale un débordement plutôt que de laisser un chevauchement invisible."""
    if y > LIMITE_BAS:
        print(f"  ⚠️  débordement ({ou}) : y={int(y)} > {LIMITE_BAS}")
    return y


def encart(d, y, titre, texte, marge=76, hauteur=None):
    """Bloc de texte d'appui : filet orange à gauche, fond blanc.

    La hauteur s'adapte au nombre de lignes : un texte long ne peut plus
    déborder sur le pied de page (défaut constaté sur le post 13).
    """
    fy = _f(SANS, 24)
    lignes = _wrap(d, texte, fy, W - 2 * marge - 60)
    if hauteur is None:
        hauteur = 74 + len(lignes) * 32 + 22

    d.rounded_rectangle([marge, y, W - marge, y + hauteur], radius=12, fill=WHITE)
    d.rectangle([marge, y + 16, marge + 6, y + hauteur - 16], fill=ORANGE)
    d.text((marge + 30, y + 34), titre, font=_f(SANS_B, 24), fill=ORANGE)
    yy = y + 74
    for ligne in lignes:
        d.text((marge + 30, yy), ligne, font=fy, fill=NAVY)
        yy += 32
    return verifier(y + hauteur + 18, "encart")


def pied(d, note, source, marge=76):
    y = H - 132
    d.line([(marge, y - 26), (W - marge, y - 26)], fill=RULE, width=2)
    d.text((marge, y), note, font=_f(SANS_B, 21), fill=NAVY)
    d.text((marge, y + 34), source, font=_f(SANS, 21), fill=GREY)
    d.text((W - marge, y + 34), "syndicat-lce.fr", font=_f(SANS_B, 21), fill=ORANGE, anchor="ra")


# Racine du dossier Communication, déduite de l'emplacement de ce fichier :
# le dossier a déjà été déplacé une fois, le code ne doit pas en dépendre.
# Emplacement des fichiers produits. Ce module vit dans le dépôt
# (`site-LCE/scripts/visuels/`) mais les visuels sont écrits dans
# `Communication/PostNN/`, à côté du dépôt : on remonte donc de trois niveaux.
_DEPOT = Path(__file__).resolve().parents[2]        # site-LCE/
RACINE = _DEPOT.parent / "Communication"            # <parent>/Communication


def enregistrer(img, dossier, nom):
    out = RACINE / dossier / nom
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=95)
    print("écrit :", out)
    return out
