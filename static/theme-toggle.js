/**
 * Theme Toggle - Light/Dark mode switcher
 * Respects system preference and persists user choice
 */
(function() {
  'use strict';

  const STORAGE_KEY = 'big0_theme';
  const DARK = 'dark';
  const LIGHT = 'light';

  // Get stored theme (default: light)
  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return LIGHT;
  }

  // Apply theme to document
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    updateToggleIcon(theme);
  }

  // Update the toggle button icon
  function updateToggleIcon(theme) {
    const toggleBtns = [
      document.getElementById('theme-toggle'),
      document.getElementById('theme-toggle-mobile')
    ];

    toggleBtns.forEach(function(toggleBtn) {
      if (!toggleBtn) return;

      const sunIcon = toggleBtn.querySelector('.theme-icon-sun');
      const moonIcon = toggleBtn.querySelector('.theme-icon-moon');

      if (sunIcon && moonIcon) {
        if (theme === LIGHT) {
          sunIcon.style.display = 'none';
          moonIcon.style.display = 'block';
        } else {
          sunIcon.style.display = 'block';
          moonIcon.style.display = 'none';
        }
      }
    });
  }

  // Toggle between themes
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || LIGHT;
    const next = current === DARK ? LIGHT : DARK;

    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  // Initialize on page load
  function init() {
    // Apply theme immediately (before DOM ready to prevent flash)
    const theme = getPreferredTheme();
    applyTheme(theme);

    // Setup toggle button when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupToggle);
    } else {
      setupToggle();
    }

    // Listen for system theme changes
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        // Only auto-switch if user hasn't set a preference
        if (!localStorage.getItem(STORAGE_KEY)) {
          applyTheme(e.matches ? LIGHT : DARK);
        }
      });
    }
  }

  function setupToggle() {
    const toggleBtn = document.getElementById('theme-toggle');
    const toggleBtnMobile = document.getElementById('theme-toggle-mobile');

    if (toggleBtn) {
      toggleBtn.addEventListener('click', toggleTheme);
    }
    if (toggleBtnMobile) {
      toggleBtnMobile.addEventListener('click', toggleTheme);
    }

    // Update icon to match current theme
    updateToggleIcon(document.documentElement.getAttribute('data-theme') || LIGHT);
  }

  // Run immediately
  init();

  // Expose toggle function globally for inline onclick handlers
  window.toggleTheme = toggleTheme;
})();
