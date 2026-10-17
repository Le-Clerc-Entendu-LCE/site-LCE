# Prompt — corriger les mentions « section syndicale » du site LCE

> **Appliqué le 16 octobre 2026.** Ce fichier conserve la spécification de la modification, pour
> référence et pour rejouer le contrôle. La formulation retenue annonce « **février 2028** » (sans
> quantième), sur décision du bureau.

---

## Rôle

Tu interviens sur le dépôt du site statique de **Le Clerc Entendu (LCE)**, syndicat des salariés du
notariat. Site multi-pages construit avec **Bun + Vite** (mode MPA), Bootstrap. Le code source est à
la racine ; `dist/` est un dossier de build **non versionné** et ne doit pas être édité à la main.

## Objectif

Corriger, sur **toutes les pages publiques**, les affirmations présentant la création d'une section
syndicale LCE comme possible « dès 2 adhérents ». Elles sont incomplètes et juridiquement inexactes
pour LCE aujourd'hui. La formulation corrigée doit annoncer qu'**à partir de février 2028** LCE
pourra accompagner la création d'une section syndicale dans un office, la condition d'ancienneté de
deux ans étant alors remplie.

## Le fait juridique à respecter (ne pas l'arrondir)

- LCE a été constitué le **8 janvier 2026** et ses statuts ont été **déposés en mairie de Gourin le
  9 février 2026** (récépissé du maire du 10 février 2026).
- L'ancienneté d'un syndicat se compte **à partir de la date du dépôt légal des statuts**
  (art. L. 2121-1, 4°, du Code du travail). LCE atteint donc deux ans le **9 février 2028**.
- **Article L. 2142-1 du Code du travail** : une section syndicale peut être constituée par un
  syndicat qui, dans l'entreprise, est représentatif, **ou** affilié à une organisation
  représentative au niveau national et interprofessionnel, **ou** satisfait aux critères de respect
  des valeurs républicaines et d'indépendance, **est légalement constitué depuis au moins deux ans**
  et dont le champ professionnel et géographique couvre l'entreprise.
- LCE est **indépendant, sans affiliation**. Il ne remplit donc la condition d'ancienneté qu'à
  compter de **février 2028**. Avant cette date, il ne peut créer aucune section syndicale, quel que
  soit le nombre d'adhérents.
- La section suppose **plusieurs adhérents** dans l'office. La pratique retient « au moins deux » :
  conserver cette formulation, mais **toujours accompagnée de la condition d'ancienneté**.
- **Ne pas promettre de délégué syndical ni de représentant de section syndicale** : le représentant
  de section (art. L. 2142-1-1) et le délégué syndical supposent un effectif d'au moins
  **50 salariés**, ce qui exclut la quasi-totalité des offices. Ne pas reprendre le mot
  « désignation » dans les textes concernés.

## Formulation attendue

Règles de rédaction :

1. Faire apparaître **« février 2028 »** dans chaque passage où LCE est concerné. Le quantième exact
   (9 février) reste la date juridique : il est rappelé ici pour information, mais n'est pas affiché
   sur le site.
2. Ne jamais écrire « dès 2 adhérents » sans la condition d'ancienneté dans la même phrase ou le même
   item de liste.
3. Ton factuel, sans promesse commerciale : « pourra accompagner », « sera possible », pas
   « bénéficiez dès maintenant ».
4. Conserver la typographie du site : espaces insécables `&nbsp;` avant `?`, `!`, `:` et `;`,
   guillemets français, apostrophes typographiques dans le texte visible.

Formulation de référence, appliquée :

> **Section syndicale** — LCE pourra accompagner la création d'une section syndicale dans votre
> office **à partir de février 2028**, date à laquelle il remplira la condition d'ancienneté de deux
> ans exigée par l'article L. 2142-1 du Code du travail. Il faut alors au moins deux adhérents LCE
> dans l'office. Avant cette date, la création d'une section n'est pas possible, même avec deux
> adhérents.

Version courte (carte, chapô) :

> Création d'une section syndicale LCE dans les offices **à partir de février 2028** (condition
> d'ancienneté de deux ans, art. L. 2142-1).

## Emplacements corrigés

| Fichier | Ligne | Texte avant | Correction appliquée |
|---|---|---|---|
| `index.html` | 141 | « Création d'une section syndicale LCE à partir de 2 adhérents dans un office. » | Version courte avec février 2028 et l'art. L. 2142-1 |
| `adherer.html` | 76 | « possibilité de création d'une section syndicale dans votre office dès 2 adhérents. » | Date + condition d'ancienneté |
| `vos-droits.html` | 80 | Réponse JSON-LD FAQ « Dès 2 adhérents LCE dans un même office… » | Réponse complète avec février 2028 et l'art. L. 2142-1 |
| `vos-droits.html` | 255 | « Sections syndicales d'entreprise — peuvent être créées… dès lors qu'un syndicat compte au moins 2 adhérents » | Règle générale de L. 2142-1 |
| `vos-droits.html` | 269 | « Création d'une section syndicale — dès 2 adhérents LCE » | Date + condition d'ancienneté |
| `vos-droits.html` | 319 | Corps de l'accordéon FAQ | Même contenu que le JSON-LD |
| `actualites.html` | 148-149 | Titre « Créer une section syndicale LCE dans votre office » | « Section syndicale LCE : ce qui sera possible en 2028 » |
| `public/llms.txt` | 58 | « Création possible d'une section syndicale LCE dans un office dès 2 adhérents. » | Version avec février 2028 et l'art. L. 2142-1 |

## Contraintes techniques

- **Ne pas modifier `dist/`** : c'est un artefact de build. Reconstruire avec `bun run build`.
- Ne pas changer la structure HTML, les classes Bootstrap, ni le balisage JSON-LD au-delà du champ
  `text` concerné.
- **Synchroniser JSON-LD et HTML visible** : la réponse de la FAQ structurée et le corps de
  l'accordéon doivent rester identiques. Vérifier que le JSON-LD reste valide.
- Ne pas ajouter de nouvelle page ni de nouveau composant.
- Ne pas toucher aux autres affirmations du site (CCN, CRPCEN, cotisations, élections CSE).
- Ne pas modifier `README.md` ni `RUNBOOK.md`.

## Vérifications

1. `grep -rn -i "section syndicale" --include='*.html' --include='*.txt' .` (hors `node_modules/` et
   `dist/`) : aucune occurrence de « dès 2 adhérents » sans la condition d'ancienneté.
2. JSON-LD de `vos-droits.html` valide (parseur JSON).
3. `bun run build` sans erreur.
4. `grep -rn "dès 2 adhérents" dist/` : aucun résultat.
5. `git diff` : uniquement les lignes concernées.
