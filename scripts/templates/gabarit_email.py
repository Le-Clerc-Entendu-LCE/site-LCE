#!/usr/bin/env python3
"""Gabarit HTML unique des e-mails de la série pédagogique CCN.

Tous les épisodes partagent la même structure : en-tête logo sur fond marine,
fil de la série, titre, corps composé de blocs, bandeau site, signature,
pied de page. Un seul endroit à modifier pour faire évoluer la série.

Le logo est repris en data URI (base64) depuis un épisode précédent : les
clients de messagerie bloquant les images distantes, il doit être embarqué.

Utilisation :
    from _gabarits.gabarit_email import rendre, bloc_texte, bloc_liste, bloc_encart

    html = rendre(
        episode=12, module="Entrée dans l'emploi", sujet="…",
        titre="…", sous_titre="…",
        blocs=[bloc_texte("Bonjour,"), bloc_encart("Le point clé", "…")],
        prochain="…",
    )
"""
import re
from pathlib import Path

# Racine du dossier Communication, déduite de l'emplacement de ce fichier :
# le dossier a déjà été déplacé une fois, le code ne doit pas en dépendre.
# Ce gabarit vit dans le dépôt (`site-LCE/scripts/templates/`) ; les e-mails
# produits vont dans `Communication/PostNN/`, à côté du dépôt.
_DEPOT = Path(__file__).resolve().parents[2]        # site-LCE/
COM = _DEPOT.parent / "Communication"
_SOURCE_LOGO = COM / "Post09" / "email_membres.html"
# Le bandeau vit à côté de ce fichier : versionné avec le dépôt, une seule copie.
# On le met à jour sans toucher à un e-mail déjà envoyé, qui sert d'archive.
_BANDEAU_FICHIER = Path(__file__).resolve().parent / "bandeau.html"


def _logo():
    return re.findall(r"data:image/[a-z+]+;base64,[A-Za-z0-9+/=]+",
                      _SOURCE_LOGO.read_text(encoding="utf-8"))[0]


def _bandeau():
    """Renvoie le bloc <tr> du bandeau « site internet ».

    Le fichier contient un commentaire d'en-tête d'instructions : on le retire
    pour ne garder que la ligne de tableau.
    """
    src = _BANDEAU_FICHIER.read_text(encoding="utf-8")
    src = re.sub(r"<!--(?!\s*(?:\[if|\[endif)).*?-->", "", src, flags=re.S)
    debut = src.find("<tr>")
    fin = src.rfind("</tr>")
    return src[debut:fin + len("</tr>")]


# ─── blocs de corps ────────────────────────────────────────────────────────

def bloc_texte(texte):
    return ('<tr><td style="padding:18px 32px 8px 32px;font-family:Arial,Helvetica,sans-serif;'
            'font-size:14px;line-height:1.6;color:#333333;">'
            f'<p style="margin:0 0 14px 0;">{texte}</p></td></tr>')


def bloc_encart(titre, texte, ton="bleu"):
    """ton : bleu (information), vert (favorable), ambre (réflexe), rouge (alerte)."""
    couleurs = {
        "bleu": ("#eef3f8", "#2c5777", "#2f4356"),
        "vert": ("#eef5ee", "#3d7a45", "#2f4a33"),
        "ambre": ("#fdf9ec", "#b8860b", "#5a4a28"),
        "rouge": ("#fbeeea", "#b8492a", "#5a3228"),
    }
    fond, bord, txt = couleurs[ton]
    return (
        '<tr><td style="padding:12px 32px 0 32px;">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="border-collapse:collapse;"><tr>'
        f'<td style="background:{fond};border-left:3px solid {bord};padding:12px 14px;'
        'font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.7;'
        f'color:{txt};">'
        f'<strong style="color:{bord};">{titre}</strong><br />{texte}'
        '</td></tr></table></td></tr>'
    )


def bloc_liste(titre, entrees, ton="bleu"):
    """Liste à puces présentée comme un encart."""
    texte = "<br />".join(f"• {e}" for e in entrees)
    return bloc_encart(titre, texte, ton)


def bloc_encart_reflexe(texte):
    return (
        '<tr><td style="padding:20px 32px 0 32px;">'
        '<p style="margin:0 0 6px 0;font-size:12px;letter-spacing:0.5px;text-transform:uppercase;'
        'color:#C8510A;font-family:Arial,Helvetica,sans-serif;font-weight:bold;'
        'border-bottom:1px solid #eeeeee;padding-bottom:4px;">Le réflexe de la semaine</p>'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="margin-top:8px;border-collapse:collapse;"><tr>'
        '<td style="background:#fdf9ec;border-left:3px solid #b8860b;padding:12px 14px;'
        'font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.55;color:#5a4a28;">'
        f'{texte}</td></tr></table></td></tr>'
    )


# ─── assemblage ────────────────────────────────────────────────────────────

def rendre(episode, module, sujet, titre, sous_titre, blocs,
           prochain, cta, commentaire="", article=""):
    logo = _logo()
    corps = "\n        ".join(blocs)
    # « 3 — Rémunération » doit donner « Module 3 — Rémunération »,
    # et « Vie collective » donner « Module — Vie collective »
    libelle_module = (f"Module {module}" if module[:1].isdigit()
                      else f"Module — {module}")
    note = (f"Épisode {episode} de la série pédagogique consacrée à la convention collective "
            f"nationale du notariat (IDCC&nbsp;2205, brochure&nbsp;3134)"
            + (f" — {article}" if article else "")
            + ". Un épisode par semaine, de septembre&nbsp;2026 à juin&nbsp;2027.")

    # dans le commentaire, le titre doit être en texte brut : y laisser un
    # <sup> ou un &nbsp; casse la lisibilité du fichier et trompe les outils
    titre_brut = re.sub(r"<[^>]+>", "", titre).replace("&nbsp;", " ")

    return f"""<!-- Post {episode:02d} — « {titre_brut} »
     BROUILLON — à relire par Bernard avant diffusion.
{commentaire}
     Diffusion via le workflow 28 :
       cd /mnt/Documents/Documents/20 - SYNDICAT LCE/site-LCE && python3 scripts/diffuser_ccn.py \\
         --sujet "{sujet}" ../Communication/Post{episode:02d}/email_membres.html
     Puis approuver dans Mounch (Approbations). -->
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{sujet}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f4;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f4f4;margin:0;padding:0;">
  <tr>
    <td align="center" style="padding:24px 12px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:#ffffff;border-collapse:collapse;border-top:4px solid #C8510A;">

        <tr>
          <td align="center" style="padding:28px 32px 8px 32px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
              <tr>
                <td style="background:#1A2B4A;padding:10px;border-radius:8px;">
                  <img src="{logo}" alt="Le Clerc Entendu" width="72" style="display:block;border:0;border-radius:4px;" />
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 32px 8px 32px;">
            <p style="margin:0;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#C8510A;font-family:Arial,Helvetica,sans-serif;font-weight:bold;">Syndicat Le Clerc Entendu</p>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:4px 32px 0 32px;">
            <p style="margin:0;font-size:11px;color:#999999;font-family:Arial,Helvetica,sans-serif;letter-spacing:0.5px;">Série pédagogique CCN &nbsp;·&nbsp; Épisode {episode} sur 45 &nbsp;·&nbsp; {libelle_module}</p>
          </td>
        </tr>

        <tr>
          <td style="padding:16px 32px 0 32px;">
            <h1 style="margin:0 0 4px 0;font-size:21px;color:#1a1a1a;font-family:Georgia,serif;">{titre}</h1>
            <p style="margin:0;font-size:13px;color:#777777;font-family:Arial,Helvetica,sans-serif;">{sous_titre}</p>
          </td>
        </tr>

        {corps}

        <tr>
          <td style="padding:20px 32px 0 32px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#333333;">
            <p style="margin:0 0 14px 0;"><strong>Prochain épisode&nbsp;:</strong> {prochain}</p>
            <p style="margin:0 0 14px 0;">{cta}</p>
          </td>
        </tr>

        {_bandeau()}

        <tr>
          <td style="padding:22px 32px 0 32px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#333333;">
            <p style="margin:0;">Cordialement,</p>
          </td>
        </tr>

        <tr>
          <td style="padding:12px 32px 28px 32px;">
            <table cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
              <tr>
                <td style="padding-right:14px;vertical-align:middle;">
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
                    <tr>
                      <td style="background:#1A2B4A;padding:6px;border-radius:6px;">
                        <img src="{logo}" alt="Le Clerc Entendu" width="56" style="display:block;border:0;border-radius:3px;" />
                      </td>
                    </tr>
                  </table>
                </td>
                <td style="border-left:3px solid #1A2B4A;padding-left:14px;vertical-align:middle;">
                  <p style="margin:0 0 2px 0;font-size:15px;font-weight:bold;color:#1a1a1a;font-family:Georgia,serif;letter-spacing:0.3px;">Bernard Desportes</p>
                  <p style="margin:0 0 6px 0;font-size:12px;color:#C8510A;font-family:Georgia,serif;font-style:italic;">Secrétaire Général Adjoint</p>
                  <p style="margin:0 0 8px 0;font-size:11px;color:#555555;font-family:Arial,sans-serif;font-weight:bold;letter-spacing:0.5px;text-transform:uppercase;">Syndicat Le Clerc Entendu</p>
                  <p style="margin:0;font-size:11px;font-family:Arial,sans-serif;">
                    <a href="https://syndicat-lce.fr" style="color:#C8510A;text-decoration:none;border-bottom:1px solid #C8510A;">syndicat-lce.fr</a>
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="padding:16px 32px;background:#1a1a1a;font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:1.5;color:#bbbbbb;">
            <p style="margin:0 0 4px 0;color:#ffffff;font-weight:bold;">Syndicat Le Clerc Entendu</p>
            <p style="margin:0;">Syndicat indépendant des salariés du notariat — <a href="https://syndicat-lce.fr" style="color:#C8510A;text-decoration:none;">syndicat-lce.fr</a></p>
            <p style="margin:8px 0 0 0;color:#888888;">{note}</p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>

</body>
</html>
"""


def ecrire(episode, html):
    out = COM / f"Post{episode:02d}" / "email_membres.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    n = len(html.encode("utf-8"))
    print(f"écrit : {out} ({n} octets)")
    assert n < 60000, "la taille dépasse le garde-fou de diffuser_ccn.py"
    return out
