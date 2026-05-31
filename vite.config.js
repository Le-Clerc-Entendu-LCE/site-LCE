import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: './',
  css: {
    preprocessorOptions: {
      scss: {
        quietDeps: true,
        silenceDeprecations: [
          'color-functions',
          'global-builtin',
          'import',
          'legacy-js-api',
        ],
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        qui: resolve(__dirname, 'qui-sommes-nous.html'),
        droits: resolve(__dirname, 'vos-droits.html'),
        metier: resolve(__dirname, 'metier-clerc-notaire.html'),
        actualites: resolve(__dirname, 'actualites.html'),
        adherer: resolve(__dirname, 'adherer.html'),
        rejoindre: resolve(__dirname, 'rejoindre.html'),
        contact: resolve(__dirname, 'contact.html'),
        mentions: resolve(__dirname, 'mentions-legales.html'),
      },
    },
  },
});
