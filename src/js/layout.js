// Shared navigation and footer for all pages
import logoUrl from '/logo_LCE.png';

const NAV_LINKS = [
  { href: 'index.html', label: 'Accueil', key: 'accueil' },
  { href: 'qui-sommes-nous.html', label: 'Qui sommes-nous', key: 'qui' },
  { href: 'vos-droits.html', label: 'Vos droits', key: 'droits' },
  { href: 'metier-clerc-notaire.html', label: 'Le métier', key: 'metier' },
  { href: 'actualites.html', label: 'Actualités', key: 'actualites' },
  { href: 'contact.html', label: 'Contact', key: 'contact' },
];

function buildNavbar(activeKey) {
  const links = NAV_LINKS.map(
    (l) =>
      `<li class="nav-item"><a class="nav-link${
        l.key === activeKey ? ' active' : ''
      }" href="${l.href}">${l.label}</a></li>`
  ).join('');

  return `
  <nav class="navbar navbar-expand-lg navbar-lce fixed-top">
    <div class="container">
      <a class="navbar-brand" href="index.html">
        <img src="${logoUrl}" alt="Logo LCE" width="44" height="44">
        <span class="brand-text">
          <span class="brand-main">LE CLERC ENTENDU</span>
          <span class="brand-sub">Syndicat des salariés du notariat</span>
        </span>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
        data-bs-target="#lceNav" aria-controls="lceNav" aria-expanded="false"
        aria-label="Ouvrir le menu">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="lceNav">
        <ul class="navbar-nav ms-auto align-items-lg-center">
          ${links}
          <li class="nav-item">
            <a class="nav-link btn-nav-adherer" href="adherer.html">Adhérer</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>`;
}

function buildFooter() {
  const year = new Date().getFullYear();
  return `
  <footer class="footer-lce">
    <div class="container">
      <div class="row g-4">
        <div class="col-lg-4">
          <img src="${logoUrl}" alt="Logo LCE" class="footer-logo" loading="lazy" width="56" height="56">
          <p class="mb-3"><strong class="text-white">LE CLERC ENTENDU</strong><br>
          Syndicat des Salariés du Notariat de France</p>
          <p class="mb-0 small">Syndicat professionnel indépendant, sans
          affiliation à aucune centrale, au service exclusif des clercs et
          employés du notariat.</p>
        </div>
        <div class="col-sm-6 col-lg-2">
          <h5>Navigation</h5>
          <ul class="list-unstyled">
            <li class="mb-2"><a href="index.html">Accueil</a></li>
            <li class="mb-2"><a href="qui-sommes-nous.html">Qui sommes-nous</a></li>
            <li class="mb-2"><a href="vos-droits.html">Vos droits</a></li>
            <li class="mb-2"><a href="metier-clerc-notaire.html">Le métier</a></li>
            <li class="mb-2"><a href="actualites.html">Actualités</a></li>
            <li class="mb-2"><a href="adherer.html">Adhérer</a></li>
            <li class="mb-2"><a href="rejoindre.html">Recevoir le flyer</a></li>
            <li class="mb-2"><a href="contact.html">Contact</a></li>
          </ul>
        </div>
        <div class="col-sm-6 col-lg-3">
          <h5>Liens utiles</h5>
          <ul class="list-unstyled">
            <li class="mb-2"><a href="https://www.legifrance.gouv.fr/conv_coll/id/KALICONT000005635092" target="_blank" rel="noopener">CCN Notariat (IDCC 2205)</a></li>
            <li class="mb-2"><a href="https://www.crpcen.fr" target="_blank" rel="noopener">CRPCEN</a></li>
            <li class="mb-2"><a href="https://www.notaires.fr" target="_blank" rel="noopener">Conseil Supérieur du Notariat</a></li>
            <li class="mb-2"><a href="mentions-legales.html">Mentions légales</a></li>
          </ul>
          <h5>Collaboration</h5>
          <ul class="list-unstyled">
            <li class="mb-2"><a href="https://wdes.fr" target="_blank" rel="noopener">wdes.fr — Assistance technique</a></li>
          </ul>
        </div>
        <div class="col-lg-3">
          <h5>Contact</h5>
          <p class="mb-2"><strong class="text-white">Siège social</strong><br>
          15 Place Stenfort<br>56110 GOURIN (Morbihan)</p>
          <p class="mb-2"><strong class="text-white">SIRET</strong><br>
          10469169600017</p>
          <p class="mb-3"><strong class="text-white">Email</strong><br>
          <a href="mailto:sg@syndicat-lce.fr">sg@syndicat-lce.fr</a></p>
          <p class="mb-0" style="display:flex;gap:1.25rem;align-items:center;">
            <a href="https://www.linkedin.com/company/116049523/" target="_blank" rel="noopener" aria-label="LinkedIn LCE" title="LinkedIn LCE" style="display:inline-flex;align-items:center;gap:.4rem;">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
              <span>LinkedIn</span>
            </a>
            <a href="https://x.com/LCE_Syndicat" target="_blank" rel="noopener" aria-label="X (Twitter) LCE" title="X (Twitter) LCE" style="display:inline-flex;align-items:center;gap:.4rem;">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              <span>X</span>
            </a>
          </p>
        </div>
      </div>
      <div class="footer-bottom text-center">
        &copy; ${year} LE CLERC ENTENDU &mdash; Syndicat des Salariés du Notariat de France.
        Tous droits réservés.
      </div>
    </div>
  </footer>`;
}

function buildFloatingButton(activeKey) {
  if (activeKey === 'adherer') return '';
  return `<a class="btn-float-adherer" href="adherer.html">Adhérer &rarr;</a>`;
}

export function mountLayout(activeKey = '') {
  const navSlot = document.getElementById('lce-nav');
  if (navSlot) navSlot.innerHTML = buildNavbar(activeKey);

  const footerSlot = document.getElementById('lce-footer');
  if (footerSlot) footerSlot.innerHTML = buildFooter();

  const floatingSlot = document.getElementById('lce-floating');
  if (floatingSlot) floatingSlot.innerHTML = buildFloatingButton(activeKey);
}
