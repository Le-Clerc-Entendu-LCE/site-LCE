#!/usr/bin/env python3
"""Génère les visuels de la série CCN à partir d'une table de spécifications.

Tout passe par `charte.py` : un seul jeu de styles, donc un fil conducteur
visuel d'un épisode à l'autre.

MISE À JOUR : la valeur du point et sa date sont en tête de fichier. Quand la
branche signe un nouvel accord de salaires, changer ces deux constantes relance
toute la grille des minima.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from charte import (nouveau, entete, pied, rangees, formule, paliers, encart, enregistrer)

# ─── données de branche (à mettre à jour à chaque accord de salaires) ───────
POINT = 16.17
POINT_DATE = "1er octobre 2026"
POINT_ACCORD = "avenant n° 66 du 17 septembre 2026"

import math
NIVEAUX = [
    ("E", "Employé", 120),
    ("T.1", "Technicien", 132),
    ("T.2", "Technicien", 146),
    ("T.3", "Technicien", 195),
    ("C.1", "Cadre", 220),
    ("C.2", "Cadre", 270),
    ("C.3", "Cadre", 340),
    ("C.4", "Cadre", 380),
]


def minimum(coef):
    return math.ceil(round(coef * POINT, 2))


def dec(x):
    return f"{x:.2f}".replace(".", ",")


def euros(n):
    return f"{n:,}".replace(",", " ") + " €"


M2 = "MODULE 2 · ENTRÉE DANS L'EMPLOI"
M3 = "MODULE 3 · RÉMUNÉRATION"


def post12():
    img, d = nouveau()
    y = entete(d, M2, "Le notaire salarié",
               "Un statut, pas un simple titre. Et un classement minimum garanti.")
    y = rangees(d, y, [
        ("Nomination par arrêté + serment", "C.2 min", "foncé",
         "le critère retenu depuis 2021"),
        ("Passerelle professionnelle", "C.2 min", "moyen",
         "même niveau que par le diplôme"),
        ("Avant l'avenant n° 42", "le diplôme", "clair",
         "déterminait seul le classement — c'est fini"),
    ], hauteur=132)
    encart(d, y + 20, "Ce que ça change",
           "Avant l'avenant n° 42, le niveau dépendait du diplôme détenu. Depuis, "
           "c'est la nomination par arrêté qui ouvre le classement C.2 minimum — "
           "y compris pour ceux qui accèdent au notariat par une passerelle "
           "professionnelle plutôt que par le diplôme.")
    pied(d, "Un titre n'est pas une classification : la nomination ouvre un plancher.",
         "Article 15.6 de la CCN — IDCC 2205, avenant n° 42 du 17 juin 2021")
    return enregistrer(img, "Post12", "2026_11_post_12_visuel_notaire_salarie_CCN.jpeg")


def post13():
    img, d = nouveau()
    y = entete(d, M2, "Votre contrat, mention par mention",
               "Quatorze mentions obligatoires. Combien figurent sur le vôtre ?")
    y = rangees(d, y, [
        ("Classification : niveau et coefficient", "1", "foncé",
         "c'est votre plancher de salaire"),
        ("Fonctions et description sommaire", "2", "moyen",
         "ce que vous faites réellement"),
        ("Durée de la période d'essai", "3", "moyen",
         "2, 3 ou 4 mois selon la catégorie"),
        ("Durée du travail et congés payés", "4", "clair", None),
        ("Salaire et périodicité de versement", "5", "clair", None),
        ("Organismes de cotisation et n° d'affiliation", "6", "clair",
         "la CRPCEN notamment"),
    ], hauteur=96, ecart=10)
    encart(d, y + 16, "Le conseil",
           "Demandez votre exemplaire signé dès l'embauche et conservez-le : c'est "
           "la référence en cas de désaccord sur vos fonctions ou votre rémunération.")
    pied(d, "Pas de contrat écrit ? La chambre de discipline peut être saisie.",
         "Article 4 de la CCN — IDCC 2205")
    return enregistrer(img, "Post13", "2026_11_post_13_visuel_contrat_travail_mentions_CCN.jpeg")


def post14():
    img, d = nouveau()
    y = entete(d, M3, "Le calcul de votre minimum",
               "Une multiplication, rien de plus.")
    y = formule(d, y + 10, "coefficient", "×", "valeur du point",
                "salaire minimum mensuel",
                note=f"T.2 : 146 × {dec(POINT)} € = {euros(minimum(146))} bruts")
    y = encart(d, y + 30, "Pourquoi ça monte",
           "La valeur du point est renégociée par les partenaires sociaux de la branche — "
           "négociation annuelle, puis clause de sauvegarde à l'automne. C'est elle qui "
           "fait évoluer tous les minima en même temps, sans négociation individuelle.")
    encart(d, y + 10, "35 heures, et au prorata",
           "La valeur du point correspond à la durée légale du travail. À temps partiel, "
           "le minimum est calculé au prorata — et toujours arrondi à l'euro supérieur.")
    pied(d, "La valeur du point est fixée par accord de branche.",
         f"{dec(POINT)} € au {POINT_DATE} — article 14.5 de la CCN")
    return enregistrer(img, "Post14", "2026_11_post_14_visuel_valeur_du_point_CCN.jpeg")


def post15():
    img, d = nouveau()
    y = entete(d, M3, "La grille des minima",
               f"Valeur du point {dec(POINT)} € au {POINT_DATE} — 35 heures.")
    tons = ["clair", "clair", "moyen", "moyen", "moyen", "foncé", "foncé", "foncé"]
    items = [(f"{niv} — {lib}", euros(minimum(coef)), tons[i],
              f"coefficient {coef}") for i, (niv, lib, coef) in enumerate(NIVEAUX)]
    y = rangees(d, y, items, hauteur=86, ecart=9)
    pied(d, "Ce sont des planchers : jamais moins, parfois plus.",
         f"{POINT_ACCORD} — non encore étendu au 31 octobre 2026")
    return enregistrer(img, "Post15", "2026_11_post_15_visuel_grille_salaires_CCN.jpeg")


def post16():
    img, d = nouveau()
    y = entete(d, M3, "Pourquoi les minima montent",
               "La valeur du point est renégociée par la branche, deux fois par an.")
    y = paliers(d, y + 14, [
        ("Février", "valeur du point\npour l'année", "clair"),
        ("Septembre", "clause de\nsauvegarde", "moyen"),
        ("1er octobre", f"{dec(POINT)} €\n+0,70 %", "orange"),
    ], hauteur=215)
    y = encart(d, y + 10, "Ce que ça change, en clair",
           "Le minimum d'un T.2 passe de 2 345 € à 2 361 € bruts par mois. "
           "Toute la grille suit en même temps, sans qu'aucun avenant individuel "
           "ne soit à signer.")
    y = encart(d, y + 6, "Une nuance à garder en tête",
           "La revalorisation garantit un nouveau plancher — pas une augmentation "
           "pour tous. Si votre salaire dépassait déjà le minimum, il ne bouge "
           "pas nécessairement.")
    encart(d, y + 6, "Les deux rendez-vous de la branche",
           "Première quinzaine de février : la valeur du point de l'année. "
           "Deuxième quinzaine de septembre : clause de sauvegarde, réajustement "
           "si le pouvoir d'achat l'exige.")
    pied(d, "La hausse s'applique sans démarche : aucun avenant individuel à signer.",
         "Article 14.1 et 14.2 de la CCN — avenant n° 66 du 17 septembre 2026")
    return enregistrer(img, "Post16", "2026_11_post_16_visuel_revalorisation_point_CCN.jpeg")


def post17():
    img, d = nouveau()
    y = entete(d, M3, "Le 13e mois",
               "Un droit conventionnel, pas une faveur. Et dû au prorata.")
    y = paliers(d, y + 20, [
        ("Toute l'année", "il s'acquiert\navec le salaire", "clair"),
        ("20 décembre", "versement\nau plus tard", "orange"),
        ("Départ en cours\nd'année", "acquis\nau prorata", "moyen"),
    ], hauteur=215)
    y = encart(d, y + 10, "Le prorata, comment ça marche",
           "Un salarié entré au 1er juillet ne perd pas son 13e mois : il en reçoit "
           "la moitié. Il s'acquiert au fur et à mesure que le salaire est versé.")
    encart(d, y + 6, "La base de calcul",
           "Égal au salaire habituel de décembre, hors gratifications "
           "exceptionnelles et heures supplémentaires occasionnelles. "
           "Rémunération variable : un douzième de l'annuel.")
    pied(d, "Égal au salaire habituel de décembre, hors primes exceptionnelles.",
         "Article 14.7 de la CCN — IDCC 2205")
    return enregistrer(img, "Post17", "2026_11_post_17_visuel_treizieme_mois_CCN.jpeg")


def post19():
    img, d = nouveau()
    y = entete(d, M3, "SMIC ou minimum conventionnel ?",
               "Toujours le plus favorable au salarié. Aucune exception.")
    y = formule(d, y + 10, "minimum conventionnel", "ou", "SMIC",
                "le plus élevé s'applique",
                note="Vous ne pouvez jamais être payé sous le SMIC")
    y = encart(d, y + 30, "Comment comparer",
           "Prenez votre minimum conventionnel — coefficient × valeur du point — "
           "et comparez-le au SMIC mensuel. Le montant le plus élevé est votre "
           "plancher. Aucun accord ne peut descendre en dessous.")
    encart(d, y + 6, "À refaire chaque 1er janvier",
           "Le SMIC est révisé tous les ans. Votre plancher réel peut donc changer "
           "en début d'année, même si la valeur du point n'a pas bougé.")
    pied(d, "Comparez les deux : le plus haut est votre plancher réel.",
         "Article 14 de la CCN et code du travail")
    return enregistrer(img, "Post19", "2026_11_post_19_visuel_smic_vs_conventionnel.jpeg")


def post20():
    img, d = nouveau()
    y = entete(d, M3, "Au-delà de 35 heures",
               "Les heures supplémentaires se paient, ou se récupèrent.")
    y = paliers(d, y + 20, [
        ("36e – 43e h", "+ 25 %", "clair"),
        ("44e h et au-delà", "+ 50 %", "moyen"),
        ("Récupération", "repos\néquivalent", "orange"),
    ], hauteur=215)
    y = encart(d, y + 10, "Attention à l'organisation à 39 h",
           "Si votre office maintient 39 h avec des jours de repos, les heures "
           "entre 35 et 39 h sont compensées en repos — pas payées comme heures "
           "supplémentaires. Vérifiez votre horaire de référence.")
    encart(d, y + 6, "Le réflexe",
           "Conservez vos relevés d'heures : cahier, badgeuse, courriels, "
           "planning. C'est la pièce maîtresse en cas de désaccord sur le décompte.")
    pied(d, "Payées ou récupérées — jamais oubliées.",
         "Article 14.9 de la CCN et code du travail")
    return enregistrer(img, "Post20", "2026_11_post_20_visuel_heures_supplementaires_CCN.jpeg")


def post21():
    img, d = nouveau()
    y = entete(d, M3, "Lire sa fiche de paie",
               "Quatre repères, deux minutes. Et souvent une surprise.")
    y = rangees(d, y, [
        ("La convention et votre coefficient", "1", "foncé",
         "IDCC 2205 en haut du bulletin"),
        ("Salaire de base ≥ coefficient × point", "2", "moyen",
         f"soit {euros(minimum(146))} pour un T.2"),
        ("Le 13e mois, sur la paie de décembre", "3", "clair", None),
        ("Les cotisations CRPCEN", "4", "clair",
         "elles remplacent une partie du régime général"),
    ], hauteur=104, ecart=10)
    encart(d, y + 8, "Et la prime d'ancienneté ?",
           "Elle n'existe pas dans la convention. L'ancienneté est reconnue par le "
           "savoir-faire (art. 15.2) : +10 points au coefficient après trois ans, "
           "intégrés au calcul du repère 2.")
    pied(d, "Conservez vos bulletins : ils font foi en cas de litige.",
         "Article 4 et 14 de la CCN — IDCC 2205")
    return enregistrer(img, "Post21", "2026_11_post_21_visuel_lire_bulletin_paie_CCN.jpeg")


def post18():
    img, d = nouveau()
    y = entete(d, M3, "Trois ans, dix points",
               "Pas une prime d'ancienneté : une reconnaissance du savoir-faire, "
               "attribuée une seule fois.")
    y = paliers(d, y + 10, [
        ("Années 1 à 3", "travail effectif\ncontinu", "clair"),
        ("Au terme de la 3e", "+ 10 points\nau coefficient", "orange"),
        ("Promotion ensuite", "les points\nsont absorbés", "moyen"),
    ], hauteur=215)
    y = encart(d, y + 8, "Exemple",
           "Un T.2 au coefficient 146 passe à 156 au terme de ses trois ans : "
           "+ 161,70 € bruts par mois à 16,17 € le point, soit 1 940 € sur l'année. "
           "Son minimum passe de 2 361 € à 2 523 €.")
    y = encart(d, y + 2, "Ce qui compte comme travail effectif",
           "RTT, repos compensateur, congés payés, jours chômés et payés, formation "
           "à la demande de l'employeur. Les autres absences — maternité, maladie, "
           "congé parental — prolongent d'autant le délai.")
    y = encart(d, y + 2, "Le réflexe",
           "Vous changez d'office avant vos trois ans ? Réclamez l'attestation qui "
           "mentionne les mois travaillés et le fait que les 10 points n'ont pas "
           "été versés. Sans elle, le délai repart de zéro chez le nouvel employeur.")
    pied(d, "Il n'existe pas de prime d'ancienneté en pourcentage dans la CCN.",
         "Article 15.2 de la CCN — IDCC 2205")
    return enregistrer(img, "Post18", "2027_01_post_18_visuel_savoir_faire_10_points_CCN.jpeg")


POSTS = {
    12: post12, 13: post13, 14: post14, 15: post15, 16: post16,
    17: post17, 18: post18, 19: post19, 20: post20, 21: post21,
}

if __name__ == "__main__":
    demandes = [int(a) for a in sys.argv[1:]] or sorted(POSTS)
    for n in demandes:
        if n not in POSTS:
            print(f"post {n} : aucune spécification (voir le README du dossier)")
            continue
        print(f"── post {n}")
        POSTS[n]()
