# Charte visuelle et gabarit d'e-mail de la série CCN

Ce dossier garantit qu'un épisode ressemble au précédent — le « fil conducteur »
demandé pour la série. Tout est centralisé ici : modifier un fichier met la
série à jour, au lieu de retoucher chaque post.

Les fichiers vivent **dans le dépôt git** (versionnés), mais ils écrivent dans
`Communication/PostNN/`, à côté du dépôt : `charte.py` et `gabarit_email.py`
déduisent ce chemin de leur propre emplacement, il n'y a donc aucune constante
à corriger si le dossier est déplacé.

```
scripts/visuels/charte.py            le style (couleurs, polices, mise en page)
scripts/visuels/generer.py           les visuels, un bloc de code par épisode
scripts/templates/gabarit_email.py   la structure HTML des e-mails
scripts/templates/bandeau.html       le bandeau « site internet » de fin d'e-mail
```

## Couleurs et typographie

| | |
|---|---|
| Fond | crème `#F6F3EE` |
| Encre | marine `#1A2B4A` |
| Accent | orange `#C8510A` |
| Texte secondaire | gris `#6E6E6E` |
| Titres | Liberation Serif Bold (équivalent libre de Georgia) |
| Texte | Liberation Sans (équivalent libre d'Arial) |

Le format est **carré, 1254 × 1254**, compatible LinkedIn, Facebook et Instagram
sans recadrage.

## Les quatre archétypes

Pour éviter la dispersion, seuls quatre types de visuels existent :

| Fonction | Rendu | Exemples |
|---|---|---|
| `rangees()` | lignes libellé + badge | post 12 (C.2 min), post 15 (grille) |
| `formule()` | équation sur fond marine | post 14 (coefficient × point) |
| `paliers()` | trois étapes côte à côte | post 17 (13e mois), post 20 (heures sup) |
| `encart()` | bloc de texte d'appui | utilisé pour combler et argumenter |

Chaque visuel comporte : un **chip de module** en haut à droite, un titre, un
sous-titre, le corps, puis un **pied de page** avec la source conventionnelle et
l'adresse du site.

## Mettre à jour la valeur du point

Une seule constante pilote toute la grille des minima :

```python
# site-LCE/scripts/visuels/generer.py
POINT = 16.17
POINT_DATE = "1er octobre 2026"
POINT_ACCORD = "avenant n° 66 du 17 septembre 2026"
```

Changer ces trois lignes puis lancer `python3 generer.py` depuis `scripts/visuels/` régénère les visuels
des posts 14, 15, 16 et 21 avec les bons montants.

## Ajouter un épisode

1. Écrire une fonction `postNN()` dans `scripts/visuels/generer.py`, sur le modèle existant.
2. L'ajouter au dictionnaire `POSTS`.
3. Pour l'e-mail, composer les blocs avec `scripts/templates/gabarit_email.py` — `rendre()` :
   `bloc_texte`, `bloc_encart` (`bleu`/`vert`/`ambre`/`rouge`), `bloc_liste`,
   `bloc_encart_reflexe`.

## Points d'attention

- **Le logo est embarqué en data URI** (base64). Il doit le rester : les clients
  de messagerie bloquent les images distantes, Outlook en particulier.
- **Le bandeau « site internet » a son propre fichier, dans le dépôt git** :
  `site-LCE/scripts/templates/bandeau.html`. Modifier ce seul fichier, puis
  reconstruire **uniquement les e-mails non encore diffusés** — un e-mail déjà
  envoyé garde sa copie d'archive dans `PostNN/email_membres.html`, à ne pas
  écraser. Vérifier que chaque lien répond en 200 avant diffusion.
- **Ne pas nommer un module `email.py`** : il masquerait le module standard de
  Python. D'où le nom `gabarit_email.py`.
- Les visuels sont en JPEG qualité 95 ; le poids reste sous 300 ko, compatible
  avec les limites des plateformes.
