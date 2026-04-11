import '../scss/main.scss';
import 'bootstrap/js/dist/collapse';
import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/modal';
import 'bootstrap/js/dist/tab';
import 'bootstrap/js/dist/offcanvas';
// Accordion is built on Collapse — no separate import needed.

import { mountLayout } from './layout.js';

document.addEventListener('DOMContentLoaded', () => {
  const activeKey = document.body.dataset.page || '';
  mountLayout(activeKey);
});
