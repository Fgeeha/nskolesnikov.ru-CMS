/*
 * Progressive enhancement only: the page is fully usable without this file.
 * Two features — theme switching and the mobile navigation panel.
 */
(function () {
  'use strict';

  var root = document.documentElement;

  /* --- Theme ------------------------------------------------------------- */
  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    var setTheme = function (theme) {
      root.setAttribute('data-theme', theme);
      toggle.setAttribute('aria-pressed', String(theme === 'light'));
      try {
        localStorage.setItem('theme', theme);
      } catch (e) {
        /* Storage can be blocked; the theme still applies for this page. */
      }
    };

    setTheme(root.getAttribute('data-theme') || 'dark');

    toggle.addEventListener('click', function () {
      setTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
    });

    /* Follow the system only while the visitor has not chosen explicitly. */
    var media = window.matchMedia('(prefers-color-scheme: light)');
    var onSystemChange = function (event) {
      var stored = null;
      try {
        stored = localStorage.getItem('theme');
      } catch (e) {
        stored = null;
      }
      if (!stored) {
        root.setAttribute('data-theme', event.matches ? 'light' : 'dark');
      }
    };
    if (typeof media.addEventListener === 'function') {
      media.addEventListener('change', onSystemChange);
    }
  }

  /* --- Mobile navigation ------------------------------------------------- */
  var navToggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('primary-nav');

  if (navToggle && nav) {
    var closeNav = function () {
      nav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    };

    navToggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });

    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) {
        closeNav();
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        closeNav();
        navToggle.focus();
      }
    });
  }

  /* --- Cookie consent banner --------------------------------------------- */
  var banner = document.querySelector('[data-cookie-banner]');
  if (banner) {
    var CONSENT_KEY = 'cookie_consent';
    var accepted = false;
    try {
      accepted = localStorage.getItem(CONSENT_KEY) === 'accepted';
    } catch (e) {
      accepted = false;
    }

    if (!accepted) {
      banner.hidden = false;
    }

    var acceptButton = banner.querySelector('[data-cookie-accept]');
    if (acceptButton) {
      acceptButton.addEventListener('click', function () {
        banner.hidden = true;
        try {
          localStorage.setItem(CONSENT_KEY, 'accepted');
        } catch (e) {
          /* Storage can be blocked; the banner still closes for this visit. */
        }
      });
    }
  }
})();
