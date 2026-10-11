# Runbook — processus opérationnels du syndicat LCE

Document de référence pour les tâches récurrentes du syndicat **Le Clerc Entendu** :
rédaction et diffusion aux adhérents, gestion des adhésions, sources documentaires.

> **À lire avant toute diffusion aux adhérents.** Les sections « Pièges connus » listent des
> erreurs déjà commises — les relire évite de les refaire.

Dernière mise à jour : **11 octobre 2026**.

---

## 1. Vue d'ensemble

| Système | Rôle | Accès |
|---|---|---|
| **Site** `site-LCE/` | site public, déployé sur GitHub Pages à chaque push sur `main` | git (SSH) |
| **Mounch** | base adhérents, formulaires, workflows d'envoi, connecteurs e-mail | API REST + interface web |
| **Registre Excel** | registre simplifié des membres (document de travail humain) | `Statuts_registre_membres_logo_/registre_membres_LCE_syndicat.xlsx` |
| **Dossier CCN** | textes conventionnels officiels + jurisprudence | `CCN_notariat_IDCC2205/` |

**Principe directeur** : Mounch est la **source de vérité** des adhérents et des envois.
Le registre Excel et les scripts locaux s'y alignent, jamais l'inverse.

### Environnements connecteurs (Mounch)

| Env | Rôle | Hôte | Expéditeur |
|---|---|---|---|
| **15** | e-mail réel (production) | `smtppro.zoho.eu` | `sg@syndicat-lce.fr` |
| **21** | SMTP de test (Ethereal) | `smtp.ethereal.email` | compte courant — voir §7 |
| **22** | IMAP de test (Ethereal) | `imap.ethereal.email` | — |

### Rythme des publications

| Publication | Fréquence | Jour | Formulaire → workflow |
|---|---|---|---|
| Série pédagogique CCN | hebdomadaire | **lundi** | 33 → **28** |
| Veille juridique | tous les 15 jours | **lundi** | 26 → **18** |

Le rythme cible est le **lundi**. En pratique l'envoi est parfois **avancé au week-end précédent**
(samedi ou dimanche) pour ne pas télescoper la charge du lundi — c'est arrivé pour les posts 04, 06
et 08. Les réseaux sociaux suivent : **LinkedIn mercredi, Facebook jeudi**.

---

## 2. Accès et secrets

- **Jeton Mounch** : variable d'environnement `MOUNCH_TOKEN`. **Ne jamais l'écrire dans un fichier
  du dépôt.** Préchargement en début de session :
  `eval "$(grep '^export MOUNCH_TOKEN=' ~/.bashrc)"`
- **Pas de `gh` CLI** : GitHub se gère via l'interface web. Pour vérifier un déploiement, c'est le
  site publié qu'on interroge (`curl`), pas l'état du repo.
- **Dépôt en SSH** : push via clé SSH. Jamais de jeton dans l'URL du remote.
- **Helper** : `site-LCE/scripts/mounch_client.py` — `call(méthode, chemin, payload)`.
  User-Agent obligatoire, déjà géré.

---

## 3. Diffusion aux adhérents (processus commun)

Les deux diffusions (CCN et veille) partagent la même mécanique :

1. Le contenu HTML est produit localement (brouillon relu par Bernard).
2. Le script soumet le formulaire Mounch correspondant.
3. Le workflow se met en **pause « approbation »** — **rien ne part**.
4. L'approbation déclenche l'envoi : la liste des destinataires est reconstruite **après** la
   pause, puis l'e-mail part en **Cci** (copie cachée) via l'env 15.

### Commandes

```bash
# Série CCN
cd /mnt/Documents/Documents/LCE_SYNDICAT/site-LCE
python3 scripts/diffuser_ccn.py --sujet "LCE — <titre du post>" \
  ../Communication/Post{NN}/email_membres.html

# Veille juridique
python3 scripts/diffuser_veille.py --sujet "Veille juridique du notariat — semaine du …" \
  ../veilles_juridiques_droit_social/<fichier>.html
```

⚠️ **Le chemin du corps HTML est relatif au dossier `site-LCE`** : depuis la racine du dépôt,
c'est `../Communication/…` (un `../..` met un dossier de trop — erreur déjà commise).

### Approuver

Le script affiche l'identifiant de la pause. Deux voies :

- **Interface Mounch** : cloche → Approbations.
- **API** : `GET /workflow-approvals` puis
  `POST /workflow-approvals/{id}/decisions {"decision": "approve"}`

**Avant d'approuver, toujours contrôler :**
1. le **sujet** et la **taille** du HTML stocké (voir le piège de troncature §6) ;
2. que le corps stocké est bien identique au fichier local ;
3. l'**heure de Paris** de la soumission (l'API renvoie de l'UTC : +2 h en été).

Après envoi, vérifier le journal d'exécution (`GET /workflows/{id}/executions`) :
statut `completed`, aucune erreur, et le **nombre de destinataires**.

---

## 4. Contrôle des cotisations avant diffusion

Depuis le 11/10/2026, `diffuser_ccn.py` et `diffuser_veille.py` appellent
`controler_cotisations()` **avant chaque soumission**. Il affiche les adhérents dont
`cotisationPaidForCurrentFiscalYear` est faux et demande confirmation.

- **Non bloquant en script** : la confirmation n'apparaît qu'en interactif ; une tâche
  planifiée passe outre. C'est volontaire — on veut voir le risque, pas casser l'envoi.
- Le workflow **ne filtre pas** encore : les retardataires reçoivent quand même l'e-mail.
  Une demande d'évolution a été faite à William le 11/10/2026 (paramètre `requireCotisationPaid`).

### ⚠️ Le piège du 1er janvier

« Current fiscal year » **bascule au 1er janvier**. À cette date,
`cotisationPaidForCurrentFiscalYear` passe à *faux pour tout le monde*, le temps que chacun
règle sa nouvelle année. Un filtre activé naïvement enverrait à **zéro destinataire, sans
erreur**. Le contrôle détecte ce cas (« tous impayés ») et le signale comme un probable
basculement d'exercice.

**Délais de campagne chez LCE** : 2026 — demandes lancées en juin, donc décembre est confortable.
2027 — assemblée en janvier, délai jusqu'à fin juin. Règle : ne pas filtrer avant l'été suivant
l'ouverture de la campagne.

---

## 5. Adhérents et contacts

- **Entreprise 114** = l'association LCE. Porte les adhésions et les cotisations.
- `GET /companies/114/association-memberships` → liste des adhésions. Champs utiles :
  `memberNumber`, `memberDisplayName`, `isActive`, `startedOn`,
  `cotisationPaidForCurrentFiscalYear`.
- ⚠️ Cet endpoint **ignore `?page`** : ne pas boucler dessus, la même page revient et fausse
  les comptages.
- **Créer un adhérent** : `POST /contacts` (fiche) puis
  `POST /companies/114/association-memberships` `{memberContactId, kind: "member", startedOn}`.
  Le `memberNumber` est **auto-incrémenté** → créer **dans l'ordre du registre**.
- **Retirer un adhérent** : **jamais de suppression** — on clôt l'adhésion (`endedOn`) ou on la
  suspend (`suspendedAt`). Le n° de membre ne bouge pas.

### ⚠️ `PATCH /contacts/{id}` remplace en bloc

Tout champ **omis est remis à NULL**. `firstName` et `lastName` sont **requis** (422 sinon).
**Toujours renvoyer la fiche complète.**

Le piège vaut **aussi à l'intérieur de `personalAddress`** : renvoyer l'adresse sans
`latitude`/`longitude` **remet les coordonnées GPS à zéro**, tout en conservant rue/ville/CP —
donc sans que ça se voie. Renvoyer l'adresse entière.

À l'inverse, `socialAccounts` et `billingAddress` omis **sont laissés intacts**. Ne pas supposer
la règle uniforme : contrôler la fiche après écriture.

**Après toute écriture sur une fiche, la relire** et vérifier téléphone, notes, adresse et
coordonnées.

### Script `sync_registre_membres.py`

Aligne le **registre Excel** sur les adhésions Mounch : ajoute la ligne des membres présents dans
Mounch mais absents du registre, et met à jour leurs notes de contact.

```bash
python3 scripts/sync_registre_membres.py          # simulation (défaut) — n'écrit rien
python3 scripts/sync_registre_membres.py --apply  # écrit, après sauvegarde automatique
```

- **Idempotent** : relancé, il ne fait rien s'il n'y a pas de ligne manquante.
- **Sauvegarde automatique** avant écriture (`.avant-sync-AAAAAMMJJ.xlsx`).
- **Périmètre limité** : il ne synchronise **que les lignes manquantes**. Il ne corrige **ni les
  dates d'adhésion, ni le statut de cotisation** — un écart sur ces champs doit être corrigé à la
  main, dans Mounch d'abord. Vérifier l'alignement registre ↔ Mounch de temps à autre (un contrôle
  champ par champ prend quelques minutes et a déjà révélé une date d'adhésion fausse).

### Cotisations — règle absolue

**Une cotisation marquée payée est définitive.** Ne jamais poser `paidAt`/`method` sans
**instruction explicite de Bernard adossée au relevé bancaire** (date de crédit + moyen). En cas
d'erreur de saisie, la seule issue est un correctif en base par William.

Convention de saisie : `fiscalYearId` 23 pour l'exercice 2026 (24 pour 2027),
`amountExclTax 0` / `amountInclTax 10`, libellé en compta 7561.

---

## 6. Pièges connus (Mounch)

| Piège | Conséquence | Parade |
|---|---|---|
| `CORPS_HTML` tronqué au-delà de **65 535 octets** (colonne SQL TEXT), **silencieusement** | e-mail amputé | garde-fou à 60 000 octets dans les scripts ; vérifier la fin (`</html>`) avant d'approuver |
| Sorties `steps.*` **perdues à la reprise d'une pause** | Cci vide → personne ne reçoit, aucune erreur | ne jamais référencer une sortie pré-pause dans une étape post-pause ; la liste est un enfant de l'approbation |
| Une étape **enfant** d'une étape `action` ne s'exécute jamais | étape muette | les étapes suivantes doivent être des **sœurs** (`sortOrder`) |
| Chemin de gabarit non scalaire → **vide sans erreur** | champ vide | lire la spec OpenAPI avant de sonder |
| `PATCH /contacts` remplace en bloc | données perdues | voir §5 |
| `list_association_members` ne prend que `includeSuspended` | pas de filtre cotisation | contrôle côté script (§4) ; évolution demandée |

**Bug historique (résolu)** : les sorties `steps.*` perdues à la reprise d'une pause ont fait
partir deux diffusions de veille avec un Cci vide, en août 2026 — échec 100 % silencieux.
C'est l'origine de la structure actuelle (liste calculée **après** l'approbation).

---

## 7. Préflight Ethereal (obligatoire avant tout envoi membres)

**Toujours tester sur Ethereal avant un envoi réel**, et relire ce qui est réellement livré.

1. Envoyer le HTML sur l'env **21**.
2. Relire le message livré via l'env **22** (`fetch_email`) et comparer au source :
   - **data URI identiques** (le logo base64 doit survivre intact — les clients e-mail bloquent
     les images distantes, et Outlook notamment) ;
   - **version texte propre** (accents, pas de balises) ;
   - taille cohérente avec le source.
3. Conserver le rendu livré dans un `apercu_ethereal.html` à côté du brouillon.

### ⚠️ Les comptes Ethereal sont régénérés régulièrement

Le compte peut devenir inaccessible ; il faut alors en créer un neuf sur ethereal.email et
**reconfigurer les env 21 et 22** :

```python
PATCH /connector-environments/21   # vars: {username, from_address, password, host, port, encryption}
PATCH /connector-environments/22   # vars: {username, password, host: imap.ethereal.email, port: 993}
# dans les deux cas : "secretKeys": ["password"]
```

**Piège récurrent** : ne changer que le mot de passe et oublier le **nom d'utilisateur** → l'échec
ressemble à une panne du connecteur, alors que c'est une incohérence de config.

**Tester les identifiants en direct avant de toucher à Mounch** — ça distingue « compte mort » de
« config Mounch cassée » :

```python
smtplib.SMTP('smtp.ethereal.email', 587) → starttls() → login(user, pass)
```

**Le compte courant se lit dans `vars.username` de l'env 21** — ne pas se fier à un nom mémorisé.

---

## 8. Série pédagogique CCN

- **Plan éditorial** : `Communication/CCN_Notariat_Serie_Pedagogique.xlsx`
  (feuille `Calendrier` + une feuille par post, `01`..`45`).
- **Sortie** : `Communication/Post{NN}/` — `email_membres.html`, `reseaux_sociaux.md`,
  visuels, `apercu_ethereal.html`.
- **Tâche planifiée** : `ccn-serie-pedagogique-hebdo`, lundi matin. Elle **prépare** et envoie un
  rappel à Bernard — **elle n'envoie rien aux adhérents**.

⚠️ **La tâche ne doit jamais écraser un fichier existant.** Si `email_membres.html` est déjà là,
c'est que le post a été préparé et relu : le brouillon peut contenir des corrections issues de la
relecture du texte conventionnel, absentes de la feuille Excel.

### Règles de rédaction

- **Ne jamais citer une durée ou un montant de mémoire.** Ouvrir l'article dans
  `CCN_notariat_IDCC2205/texte-consolide/` et lire la ligne « en vigueur depuis ».
- Le §5 du cahier des charges (`Communication/2026_cahier_des_charges_serie_pedagogique_CCN.md`)
  contient une **table article → avenant(s) l'ayant modifié** : c'est l'outil pour repérer qu'un
  chiffre a bougé.
- Erreur type déjà commise : « cadres : 5 mois » pour la période d'essai, périmé depuis l'avenant
  n° 50 du 25/05/2023 (**4 mois**).
- **Vérifier les visuels** : les chiffres d'une infographie doivent correspondre au texte.

---

## 9. Veille juridique

- **Rythme** : tous les 15 jours, le lundi (+14 jours).
- **Cahier des charges** : `cahiers_ces_charges_Claude_et_notes_fichiers_md/2026_cahier_des_charges_generation_veille_juridique.md`
  (sources, sélection, structure normative à 7 rubriques, checklist).
- Point de départ de chaque édition :
  `cahiers_ces_charges_Claude_et_notes_fichiers_md/Veille-notes-a-suivre.md`.
- **Gabarit** : `Courriers/email_veille_juridique_gabarit.html`.
- **Dossier de sortie** : `veilles_juridiques_droit_social/`.
- ⚠️ **CRPCEN : vérifier avant de publier.** Régime spécial, réformes décalées par rapport au
  régime général. Exigence de crédibilité forte auprès des clercs.
- **Doublons** : si une info est déjà parue récemment, demander à Bernard quoi conserver.

---

## 10. Sources documentaires

### Dossier CCN

`CCN_notariat_IDCC2205/` — **ouvrir `INDEX.md` d'abord** : texte consolidé, avenants, accords,
nouveautés récentes, jurisprudence.

**Légifrance bloque `curl` en 403.** La voie praticable est le portail opendata de la DILA
(qui publie les mêmes fonds officiels) :

- `https://echanges.dila.gouv.fr/OPENDATA/KALI/` — textes conventionnels
- `https://echanges.dila.gouv.fr/OPENDATA/CASS/` — Cour de cassation

Les dumps **globaux** sont volumineux (~173 et ~260 Mo) et **datés** ; les dumps **quotidiens**
(≈300 Ko) sont **incrémentaux** et servent à compléter. Les scripts d'extraction sont dans
`CCN_notariat_IDCC2205/_outils/`.

`WebFetch` **atteint** Légifrance pour lire une page HTML précise, même quand `curl` est bloqué :
c'est le repli pour vérifier un article isolé.

### Veille — accès aux sources

Certaines sources sont protégées. `browserget` sert de repli (allowlist par `@connect`), mais il
dépend d'un onglet de contrôle ouvert dans le navigateur — s'il est fermé, l'outil ne répond pas.

---

## 11. Consignes transverses

- **Format destinataire** : toujours « Prénom Nom \<email\> », jamais l'adresse nue.
- **Heures** : convertir l'UTC des API en **heure de Paris** avant de citer une heure.
- **Ne rien publier ou envoyer sans validation de Bernard.** Les scripts soumettent ; ils
  n'engagent rien tant que l'approbation n'est pas donnée.
- **Signaler les bugs Mounch à William** par e-mail (voir la fixture d'envoi dédiée), avec
  contexte, sortie réelle et sortie attendue.
- **Écritures sensibles** (adhésions, fiches, compta) : confirmer avant d'agir, et **relire après**.
