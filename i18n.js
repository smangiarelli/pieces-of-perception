/* Pieces of Perception — English / Español switcher.
 *
 * English is the default. The footer button stores the choice in
 * localStorage ("pop_lang") and reloads the page; every page that loads
 * this script then reads the choice. ?lang=es / ?lang=en in a URL also sets it.
 *
 * Spanish text comes from /i18n-es.json, a dictionary keyed by the English
 * text exactly as it appears on the page (built by _i18n/tools/extract.py).
 * Nothing on the page is rewritten by hand — this script swaps displayed
 * text only. Form VALUES (radio/checkbox/select values, anything typed)
 * are never touched, so answers are always saved in English.
 *
 * Legal documents and consent checkboxes stay in English on purpose (the
 * English is the version that legally counts); a Spanish notice says so.
 *
 * Page scripts can call window.popLang() -> "en" | "es".
 */
(function () {
  'use strict';
  var LS_KEY = 'pop_lang';
  var DICT_URL = '/i18n-es.json?v=20260925';

  function readLang() {
    try {
      var q = new URLSearchParams(location.search).get('lang');
      if (q === 'es' || q === 'en') { localStorage.setItem(LS_KEY, q); return q; }
      return localStorage.getItem(LS_KEY) === 'es' ? 'es' : 'en';
    } catch (e) { return 'en'; }
  }
  var LANG = readLang();
  window.popLang = function () { return LANG; };

  function setLang(l) {
    try { localStorage.setItem(LS_KEY, l); } catch (e) {}
    try {
      var u = new URL(location.href);
      if (u.searchParams.has('lang')) { u.searchParams.set('lang', l); location.replace(u.toString()); return; }
    } catch (e) {}
    location.reload();
  }

  // ── Toggle button (bottom of every page) ───────────────────────────────
  function addToggle() {
    if (document.getElementById('pop-lang-toggle')) return;
    var st = document.createElement('style');
    st.textContent =
      '#pop-lang-toggle{display:flex;justify-content:center;align-items:center;gap:6px;' +
      'font-family:inherit;font-size:14px;margin:14px auto 4px;padding:0}' +
      '#pop-lang-toggle.pop-lang-free{padding:18px 16px 26px}' +
      '#pop-lang-toggle button{font:inherit;background:transparent;border:1px solid currentColor;' +
      'color:inherit;border-radius:999px;padding:6px 14px;cursor:pointer;opacity:.85}' +
      '#pop-lang-toggle button[aria-pressed="true"]{opacity:1;font-weight:700;' +
      'background:rgba(108,99,255,.12)}' +
      '#pop-lang-toggle button:focus-visible{outline:2px solid #6C63FF;outline-offset:2px}';
    document.head.appendChild(st);
    var box = document.createElement('div');
    box.id = 'pop-lang-toggle';
    box.setAttribute('data-i18n-skip', '');
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', 'Language / Idioma');
    [['en', 'English'], ['es', 'Español']].forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button';
      b.lang = p[0];
      b.textContent = p[1];
      b.setAttribute('aria-pressed', LANG === p[0] ? 'true' : 'false');
      b.addEventListener('click', function () { if (LANG !== p[0]) setLang(p[0]); });
      box.appendChild(b);
    });
    var footer = document.querySelector('footer');
    if (footer) footer.appendChild(box);
    else { box.className = 'pop-lang-free'; document.body.appendChild(box); }
  }

  if (LANG !== 'es') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', addToggle);
    else addToggle();
    return;
  }

  // ── Spanish mode ───────────────────────────────────────────────────────
  document.documentElement.lang = 'es';
  document.documentElement.classList.add('pop-i18n-pending');
  var hide = document.createElement('style');
  hide.textContent = 'html.pop-i18n-pending body{visibility:hidden}';
  (document.head || document.documentElement).appendChild(hide);
  function reveal() { document.documentElement.classList.remove('pop-i18n-pending'); }
  var revealTimer = setTimeout(reveal, 2500);   // never leave a blank page

  var INLINE = { a:1, abbr:1, b:1, br:1, code:1, em:1, i:1, small:1, span:1, strong:1, sub:1,
                 sup:1, u:1, mark:1, s:1, q:1, cite:1, time:1 };
  var SKIP_TAGS = { script:1, style:1, noscript:1, svg:1, template:1, textarea:1, code:1, pre:1, iframe:1 };
  // Kept in English on purpose — consent wording and agreement text.
  var SKIP_SEL = '[data-i18n-skip], .ack-item-text, #ack-sections, .ag-sec, label.chk';
  var SKIP_SEL_HAS = 'label:has(#arlConsent)';   // Report Refresh auto-renew consent
  try { document.querySelector(SKIP_SEL_HAS); SKIP_SEL += ', ' + SKIP_SEL_HAS; } catch (e) {}
  var ATTRS = ['placeholder', 'title', 'aria-label', 'alt'];
  var LEGAL_PAGES = /\/(privacy|terms|terms-and-conditions|disclaimer|refund|beta-agreement|customer-agreement)(\.html)?$/;
  var IS_LEGAL = LEGAL_PAGES.test(location.pathname);

  var DICT = null, PATTERNS = [], UPPER = {};

  function norm(s) { return s.replace(/\s+/g, ' ').trim(); }
  function esc(t) { return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function reEsc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  function buildPatterns() {
    Object.keys(DICT).forEach(function (k) {
      if (k.length < 80 && !/[<{]/.test(k)) UPPER[k.toUpperCase()] = DICT[k].toUpperCase();
    });
    Object.keys(DICT).forEach(function (k) {
      if (!/\{\d+\}/.test(k)) return;
      var names = [];
      var src = reEsc(k).replace(/\\\{(\d+)\\\}/g, function (_, n) { names.push(n); return '(.+?)'; });
      try { PATTERNS.push({ re: new RegExp('^' + src + '$'), names: names, es: DICT[k], len: k.length }); }
      catch (e) {}
    });
    PATTERNS.sort(function (a, b) { return b.len - a.len; });
  }

  function lookup(key, depth) {
    if (!key) return null;
    if (Object.prototype.hasOwnProperty.call(DICT, key)) return DICT[key];
    // Eyebrows are upper-cased in code (step.eyebrow.toUpperCase()).
    if (key === key.toUpperCase() && Object.prototype.hasOwnProperty.call(UPPER, key)) return UPPER[key];
    if ((depth || 0) > 2) return null;
    for (var i = 0; i < PATTERNS.length; i++) {
      var p = PATTERNS[i], m = p.re.exec(key);
      if (!m) continue;
      var out = p.es;
      p.names.forEach(function (n, j) {
        var v = m[j + 1];
        var tv = lookup(v, (depth || 0) + 1);
        out = out.split('{' + n + '}').join(tv != null ? tv : v);
      });
      return out;
    }
    return null;
  }
  window.popT = function (s) { if (!DICT) return s; var r = lookup(norm(String(s))); return r == null ? s : r; };

  function skipped(el) { return el.closest && el.closest(SKIP_SEL); }

  function inlineOnly(el) {
    for (var c = el.firstChild; c; c = c.nextSibling) {
      if (c.nodeType !== 1) continue;
      var n = c.localName;
      if (!INLINE[n]) return false;
      if (n !== 'br' && !inlineOnly(c)) return false;
    }
    return true;
  }
  function qualifies(el) { return inlineOnly(el) && /[A-Za-z]/.test(el.textContent); }

  function abstract(el) {
    var out = '';
    for (var c = el.firstChild; c; c = c.nextSibling) {
      if (c.nodeType === 3) out += esc(c.data);
      else if (c.nodeType === 1) {
        if (c.localName === 'br') out += '<br>';
        else out += '<' + c.localName + '>' + abstract(c) + '</' + c.localName + '>';
      }
    }
    return out;
  }

  // Rebuild el's children from the translated markup, re-using the
  // original inline elements (same tag, same order) so links keep their
  // href/classes and any event listeners.
  function reconcile(orig, tpl) {
    var pools = {};
    for (var c = orig.firstChild; c; c = c.nextSibling)
      if (c.nodeType === 1) (pools[c.localName] = pools[c.localName] || []).push(c);
    var kids = [];
    for (var n = tpl.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) kids.push(document.createTextNode(n.data));
      else if (n.nodeType === 1) {
        var p = pools[n.localName];
        var o = (p && p.length) ? p.shift() : document.createElement(n.localName);
        if (n.localName !== 'br') reconcile(o, n);
        kids.push(o);
      }
    }
    while (orig.firstChild) orig.removeChild(orig.firstChild);
    kids.forEach(function (k) { orig.appendChild(k); });
  }

  function translateText(node) {
    var d = node.data;
    if (!/[A-Za-z]/.test(d)) return;
    var t = lookup(norm(d));
    if (t == null) return;
    var lead = d.match(/^\s*/)[0], trail = d.match(/\s*$/)[0];
    node.data = lead + t + trail;
  }

  function translateAttrs(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i];
      if (el.hasAttribute && el.hasAttribute(a)) {
        var t = lookup(norm(el.getAttribute(a)));
        if (t != null) el.setAttribute(a, t);
      }
    }
    if (el.localName === 'input' && /^(submit|button)$/i.test(el.type) && el.value) {
      var tv = lookup(norm(el.value));
      if (tv != null) el.value = tv;
    }
  }

  function walk(el) {
    if (el.nodeType === 3) { if (!(el.parentElement && skipped(el.parentElement))) translateText(el); return; }
    if (el.nodeType !== 1) return;
    if (el.matches && el.matches(SKIP_SEL)) return;
    if (el.localName === 'textarea') { translateAttrs(el); return; }
    if (SKIP_TAGS[el.localName]) return;
    translateAttrs(el);
    if (qualifies(el) && el !== document.body) {
      var t = lookup(norm(abstract(el)));
      if (t != null) {
        var tpl = document.createElement('template');
        tpl.innerHTML = t;
        reconcile(el, tpl.content);
        return;
      }
    }
    var c = el.firstChild;
    while (c) { var next = c.nextSibling; walk(c); c = next; }
  }

  function translateRoot(root) {
    if (IS_LEGAL) {
      var parts = root.querySelectorAll ? root.querySelectorAll('header, nav, footer') : [];
      for (var i = 0; i < parts.length; i++) walk(parts[i]);
      if (root.closest && root.closest('header, nav, footer')) walk(root);
    } else {
      walk(root);
    }
  }

  // ── Spanish notices where English is kept on purpose ───────────────────
  var NOTE_LEGAL_PAGE =
    'Este documento legal está disponible solo en inglés por ahora. Estamos preparando una ' +
    'versión en español. Si tiene preguntas, escríbanos a hello@piecesofperception.com.';
  var NOTE_CONSENT =
    'Los acuerdos y las casillas de consentimiento que siguen están en inglés, porque la ' +
    'versión en inglés es la que tiene validez legal. Estamos preparando una traducción al ' +
    'español. Si necesita ayuda para entenderlos, escríbanos a hello@piecesofperception.com ' +
    'antes de continuar.';
  function makeNote(text) {
    var d = document.createElement('div');
    d.className = 'pop-i18n-note';
    d.setAttribute('data-i18n-skip', '');
    d.setAttribute('lang', 'es');
    d.style.cssText = 'background:#FFF6E5;border:1px solid #F0C36D;color:#5A4200;border-radius:10px;' +
      'padding:12px 14px;margin:12px 0;font-size:14px;line-height:1.5;text-align:left';
    d.textContent = text;
    return d;
  }
  function addConsentNotes() {
    var targets = document.querySelectorAll('#ack-sections, .ack-item, label.chk');
    for (var i = 0; i < targets.length; i++) {
      var t = targets[i], parent = t.parentNode;
      if (!parent || parent.querySelector(':scope > .pop-i18n-note')) continue;
      var first = parent.querySelector(':scope > #ack-sections, :scope > .ack-item, :scope > label.chk') || t;
      parent.insertBefore(makeNote(NOTE_CONSENT), first);
    }
  }
  function addLegalBanner() {
    if (!IS_LEGAL || document.getElementById('pop-legal-es')) return;
    var n = makeNote(NOTE_LEGAL_PAGE);
    n.id = 'pop-legal-es';
    n.style.margin = '16px auto';
    n.style.maxWidth = '860px';
    var anchor = document.querySelector('main, article, .container, .wrap') || document.body.firstElementChild;
    if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(n, anchor);
    else document.body.insertBefore(n, document.body.firstChild);
  }

  // ── alert()/confirm() messages ─────────────────────────────────────────
  ['alert', 'confirm', 'prompt'].forEach(function (fn) {
    var orig = window[fn];
    if (typeof orig !== 'function') return;
    window[fn] = function (msg) {
      var a = Array.prototype.slice.call(arguments);
      if (DICT && typeof msg === 'string') a[0] = window.popT(msg);
      return orig.apply(window, a);
    };
  });

  // ── Wire-up ────────────────────────────────────────────────────────────
  var observer = null;
  function withObserverOff(fn) {
    if (observer) observer.disconnect();
    try { fn(); } finally {
      if (observer) observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    }
  }
  function onMutations(list) {
    withObserverOff(function () {
      for (var i = 0; i < list.length; i++) {
        var m = list[i];
        if (m.type === 'characterData') {
          var p = m.target.parentElement;
          if (p && qualifies(p)) walk(p); else walk(m.target);
          continue;
        }
        for (var j = 0; j < m.addedNodes.length; j++) {
          var n = m.addedNodes[j];
          if (!n.isConnected) continue;
          if (n.nodeType === 3 && n.parentElement && qualifies(n.parentElement)) translateRoot(n.parentElement);
          else translateRoot(n);
        }
      }
      addConsentNotes();
      var tt = lookup(norm(document.title)); if (tt != null) document.title = tt;
    });
  }

  function start() {
    withObserverOff(function () {
      translateRoot(document.body);
      var tt = lookup(norm(document.title)); if (tt != null) document.title = tt;
      addToggle();
      addLegalBanner();
      addConsentNotes();
    });
    observer = new MutationObserver(onMutations);
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    clearTimeout(revealTimer);
    reveal();
  }

  var dictReady = fetch(DICT_URL, { credentials: 'omit' })
    .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function (d) { DICT = d; buildPatterns(); });
  var domReady = new Promise(function (res) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', res); else res();
  });
  Promise.all([dictReady, domReady]).then(start).catch(function (e) {
    // Dictionary failed to load: show the English page rather than nothing.
    if (window.console) console.warn('[i18n] Spanish unavailable:', e);
    clearTimeout(revealTimer); reveal();
    domReady.then(addToggle);
  });
})();
