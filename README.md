# LE CLERC ENTENDU — Site officiel

Site internet du syndicat **LCE — Le Clerc Entendu**, Syndicat des Salariés
du Notariat de France. Site statique multi-pages construit avec **Bun + Vite
+ Bootstrap 5 + SCSS**, déployé automatiquement sur **GitHub Pages**.

---

## Stack technique

- **Runtime / gestionnaire de paquets** : [Bun](https://bun.sh) 1.3+
- **Bundler** : [Vite](https://vitejs.dev) 6 (mode MPA — multi-pages)
- **CSS** : Bootstrap 5.3 personnalisé via SCSS (sass-embedded)
- **JS** : modules Bootstrap importés à la carte (collapse, dropdown,
  modal, tab, offcanvas)
- **Aucune dépendance CDN** — tout est bundlé dans `dist/assets/`

## Prérequis

Installer Bun (si ce n'est pas déjà fait) :

```bash
curl -fsSL https://bun.sh/install | bash
```

Puis redémarrer le shell ou `source ~/.bashrc`.

## Installation

```bash
bun install
```

Cela installe Vite, Bootstrap, Popper, sass-embedded et crée `bun.lock`
(à committer).

## Scripts disponibles

| Commande            | Action                                                      |
| ------------------- | ----------------------------------------------------------- |
| `bun run dev`       | Serveur de dev Vite sur `localhost:5173` avec hot-reload    |
| `bun run start`     | Alias de `dev`                                              |
| `bun run build`     | Build de production dans `dist/`                            |
| `bun run preview`   | Sert `dist/` sur `localhost:4173` (test du build)           |
| `bun run clean`     | Supprime `dist/` et les caches Vite                         |

## Développement local

```bash
bun run dev
```

Lance le serveur de dev Vite sur `http://localhost:5173`. Hot-reload actif
pour HTML, SCSS et JS. **C'est la seule façon de voir le site correctement
pendant l'édition** — ouvrir les `.html` directement dans le navigateur ne
fonctionne pas (voir section *Dépannage* plus bas).

### Claude Code Preview

Le fichier `.claude/launch.json` déclare une configuration `lce-dev` qui
démarre automatiquement `bun run dev` sur le port 5173 quand tu utilises le
panneau Preview de Claude Code. C'est la façon recommandée de prévisualiser
le site pendant qu'un agent édite des fichiers : les aperçus seront stylés
correctement.

## Build de production

```bash
bun run build
```

Génère le site statique dans `dist/` :

- HTML des 7 pages (injection d'assets hashés)
- `dist/assets/main-[hash].css` — Bootstrap + styles LCE compilés
- `dist/assets/main-[hash].js` — JS bundlé (Bootstrap + layout)
- `dist/logo_LCE.png` — copié depuis `public/`

Pour vérifier le rendu final avant un commit : `bun run preview` (sert
`dist/` sur `http://localhost:4173`).

---

## Structure du projet

```
.
├── .github/workflows/deploy.yml   # Build + déploiement GH Pages
├── public/                        # Assets copiés tels quels dans dist/
│   └── logo_LCE.png
├── src/
│   ├── js/
│   │   ├── main.js                # Point d'entrée : SCSS + Bootstrap + layout
│   │   └── layout.js              # Navbar / footer / bouton flottant partagés
│   └── scss/
│       └── main.scss              # Variables LCE + @import bootstrap + thème
├── index.html                     # Accueil
├── qui-sommes-nous.html
├── vos-droits.html
├── actualites.html
├── adherer.html
├── contact.html
├── mentions-legales.html
├── vite.config.js                 # Config MPA, base './', silence Sass deps
├── package.json
└── bun.lock                       # Lockfile Bun (committé)
```

### Pages partagent une même structure

Chaque page HTML :

1. a un `<body data-page="...">` pour indiquer l'élément de nav actif ;
2. contient trois slots vides que le JS remplit au chargement :
   - `<div id="lce-nav"></div>` — navbar fixe
   - `<div id="lce-footer"></div>` — footer
   - `<div id="lce-floating"></div>` — bouton flottant « Adhérer »
3. charge `/src/js/main.js` en module à la fin du `<body>`.

Le contenu de la navbar et du footer vit dans **un seul endroit** :
`src/js/layout.js`. Modifier le menu ou le footer met à jour toutes les pages
simultanément.

---

## Ajouter une nouvelle page

1. Créer `ma-page.html` à la racine, en copiant une page existante comme
   modèle. Mettre à jour `<title>`, la meta description et `<body data-page>`.
2. Déclarer l'entrée dans `vite.config.js` :

   ```js
   rollupOptions: {
     input: {
       // ...pages existantes
       maPage: resolve(__dirname, 'ma-page.html'),
     },
   },
   ```

   Sans cette ligne, Vite ne buildera pas la page.
3. Si la page doit apparaître dans le menu, ajouter une entrée dans
   `NAV_LINKS` (fichier `src/js/layout.js`) — et éventuellement dans le footer.

## Modifier la charte graphique

Les couleurs LCE (orange `#F47920`, marine `#1A2B4A`) sont définies en haut
de `src/scss/main.scss`. Elles sont réassignées aux variables Bootstrap
**avant** l'`@import "bootstrap/scss/bootstrap"`, donc elles propagent
partout (boutons, liens, focus, etc.).

Pour changer une couleur, éditer les variables `$lce-orange` / `$lce-marine`
en haut du fichier — tout le thème se met à jour au rebuild.

## Ajouter un module Bootstrap JS

Par défaut, seuls les modules utilisés sont importés dans `src/js/main.js` :
collapse, dropdown, modal, tab, offcanvas. Pour en ajouter un autre (toast,
tooltip, etc.) :

```js
import 'bootstrap/js/dist/toast';
```

## Ajouter une image / un asset statique

Déposer le fichier dans `public/`. Il sera copié tel quel dans `dist/` et
accessible à l'URL `/nom-du-fichier.ext`. Exemple : `public/drapeau.svg` →
utilisable dans le HTML comme `<img src="/drapeau.svg">`.

---

## Déploiement

Le workflow **`.github/workflows/deploy.yml`** se déclenche :

- sur chaque `push` vers `main` ;
- manuellement via l'onglet *Actions* → *Deploy to GitHub Pages* →
  *Run workflow*.

Étapes exécutées par le runner GitHub :

1. `actions/checkout@v4`
2. `oven-sh/setup-bun@v2` — installe Bun
3. `bun install --frozen-lockfile` — respecte strictement `bun.lock`
4. `bun run build` — génère `dist/`
5. `actions/configure-pages@v5` + `actions/upload-pages-artifact@v3`
   (upload de `./dist`)
6. Job `deploy` : `actions/deploy-pages@v4` — publication sur
   l'environnement `github-pages`

URL publique : `https://le-clerc-entendu-lce.github.io/site-LCE/`

### Configuration GitHub Pages requise

**Une seule fois**, dans le repo GitHub :
**Settings → Pages → Build and deployment → Source : GitHub Actions**

Si cette option n'est pas activée, le job `deploy` échouera avec une erreur
`Pages site not found`.

### Workflow : dépendance PAT

Modifier un fichier sous `.github/workflows/` depuis un push git nécessite
que le token utilisé ait le scope **`workflow`**. Si un push est rejeté
avec :

```
refusing to allow a Personal Access Token to create or update workflow ...
```

éditer le PAT sur https://github.com/settings/tokens pour activer ce scope,
puis `git push` à nouveau.

---

## Dépannage

### « Pourquoi l'aperçu d'un `.html` est sans CSS ni menu ? »

Les fichiers HTML à la racine sont des **sources Vite**, pas des fichiers
statiques complets. Ils référencent `/src/js/main.js`, qui :

1. importe le SCSS (`import '../scss/main.scss'`) — compilé par Vite ;
2. importe des modules Bootstrap depuis `node_modules` ;
3. importe le logo via `import logoUrl from '/logo_LCE.png'` (syntaxe Vite) ;
4. injecte le contenu de la navbar et du footer dans les slots vides.

Un aperçu en `file://` ou via un serveur statique basique ne sait faire
**aucune** de ces quatre choses. Résultat : HTML brut sans styles, avec
`#lce-nav` et `#lce-footer` vides.

Pour voir le rendu réel : toujours passer par **`bun run dev`** pendant
l'édition, ou **`bun run preview`** après un build pour tester le rendu
production.

### Le build se plaint de warnings Sass `color-functions is deprecated`

Ces warnings proviennent de Bootstrap lui-même (fonctions Sass legacy) et
sont silencés dans `vite.config.js` via `silenceDeprecations`. Si un nouveau
warning apparaît après une mise à jour de Bootstrap, l'ajouter à cette liste.

### `bun install --frozen-lockfile` échoue en CI

Le lockfile `bun.lock` n'est plus en phase avec `package.json`. Relancer
`bun install` localement et committer le `bun.lock` mis à jour.

### Les liens internes cassent sur GitHub Pages

Vérifier que `vite.config.js` contient bien `base: './'`. C'est ce qui rend
les URLs d'assets relatives et compatibles avec un déploiement dans un
sous-chemin (`/site-LCE/`).

---

## Contact

Pour toute question sur le contenu éditorial du site :
[sg@syndicat-lce.fr](mailto:sg@syndicat-lce.fr)
