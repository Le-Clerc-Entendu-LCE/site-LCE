#!/usr/bin/env python3
"""Petites transformations du HTML des e-mails avant envoi."""
import re

_COMMENTAIRE = re.compile(r"<!--.*?-->", re.S)


def sans_commentaires(html):
    """Retire les commentaires HTML d'un e-mail avant diffusion.

    Les fichiers sources portent en tête un bloc d'instructions internes
    (date, réserves de vérification, commande de diffusion) et, à la fin, deux
    marqueurs délimitant le bandeau « site internet ». Ils sont invisibles à la
    lecture, mais restent lisibles dans le code source du message reçu : un
    adhérent curieux y verrait nos notes de travail.

    Le contenu situé *entre* deux commentaires est conservé — seule la balise
    de commentaire disparaît. Les commentaires conditionnels Outlook
    (`<!--[if mso]>`) seraient également retirés : il n'en existe aucun dans
    nos gabarits, mais il faudra y penser si l'on en ajoute.
    """
    return _COMMENTAIRE.sub("", html)
