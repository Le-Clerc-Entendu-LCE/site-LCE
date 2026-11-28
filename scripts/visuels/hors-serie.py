#!/usr/bin/env python3
"""Visuel hors-série — l'ancienneté du régime social du notariat.

N'est pas un épisode de la série CCN : il illustre la place du notariat dans
l'histoire de la protection sociale. Réutilise la charte commune.

Faits vérifiés le 28/11/2026 :
  - loi du 12 juillet 1937 créant la CRPCEN ; fonctionnement réel depuis 1939 ;
  - Sécurité sociale : ordonnances des 4 et 19 octobre 1945 ;
  - première convention collective du notariat : 1955 (FGCEN-FO), puis 1989
    et 2001 — donc APRÈS 1946, contrairement à une idée répandue ;
  - accord d'actualisation signé le 15/10/2026.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from charte import nouveau, entete, pied, paliers, encart, enregistrer

IMG, d = nouveau()
y = entete(d, "HORS SÉRIE", "Huit ans d'avance",
           "Le régime social des salariés du notariat a précédé la Sécurité sociale.")

y = paliers(d, y + 10, [
    ("1937", "loi créant\nla CRPCEN", "clair"),
    ("1945", "la Sécurité\nsociale", "moyen"),
    ("2026", "accord\nd'actualisation", "orange"),
], hauteur=215)

y = encart(d, y + 8, "Ce que ça dit",
           "Le notariat n'a pas attendu la Sécurité sociale pour protéger ses salariés : "
           "dès 1937, la loi créait une caisse dédiée, la CRPCEN. Elle fonctionne depuis "
           "1939 et gère encore aujourd'hui la maladie, une partie de la prévoyance et la "
           "retraite de base des clercs et employés d'études.")

y = encart(d, y + 6, "Et depuis, sans interruption",
           "Première convention collective en 1955, refondue en 1989 puis en 2001. "
           "Accords de branche sur le télétravail, l'activité partielle, la rémunération "
           "des apprentis, les fins de carrière.")

encart(d, y + 6, "Une histoire, pas un acquis",
       "Un régime ancien n'est pas un régime figé, ni une conquête définitive. Les minima "
       "se renégocient deux fois par an, et chaque droit reste à défendre — c'est le rôle "
       "du syndicat.")

pied(d, "Un régime social né en 1937, huit ans avant la Sécurité sociale.",
     "Loi du 12 juillet 1937 · ordonnances des 4 et 19 octobre 1945")

enregistrer(IMG, "Hors-serie", "2026_11_hors_serie_histoire_sociale_notariat.jpeg")
