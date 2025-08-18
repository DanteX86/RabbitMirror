/* Theme support: prefers-color-scheme and manual toggle via data-theme on html element */
(function(){
  try {
    var docEl = document.documentElement;
    var storageKey = 'rabbitmirror-theme';
    var btn = document.getElementById('theme-toggle');

    function getSystemPref() {
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
      // theme can be 'light', 'dark', or 'auto'
      if (theme === 'auto') {
        docEl.removeAttribute('data-theme');
      } else {
        docEl.setAttribute('data-theme', theme);
      }
    }

    function loadTheme() {
      var saved = localStorage.getItem(storageKey);
      if (!saved) return 'auto';
      return saved;
    }

    function saveTheme(theme) {
      localStorage.setItem(storageKey, theme);
    }

    function currentEffectiveTheme() {
      var t = loadTheme();
      if (t === 'auto') return getSystemPref();
      return t;
    }

    function updateButtonState(theme) {
      if (!btn) return;
      var eff = theme === 'auto' ? getSystemPref() : theme;
      btn.setAttribute('aria-pressed', eff === 'dark' ? 'true' : 'false');
      btn.title = 'Theme: ' + (theme === 'auto' ? 'auto (' + eff + ')' : theme);
    }

    function init() {
      var theme = loadTheme();
      applyTheme(theme);
      updateButtonState(theme);
      if (btn) {
        btn.addEventListener('click', function(){
          var t = loadTheme();
          // cycle: auto -> dark -> light -> auto
          var next = t === 'auto' ? 'dark' : (t === 'dark' ? 'light' : 'auto');
          saveTheme(next);
          applyTheme(next);
          updateButtonState(next);
        });
      }
      // react to system changes when in auto
      if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        mq.addEventListener && mq.addEventListener('change', function(){
          if (loadTheme() === 'auto') {
            applyTheme('auto');
            updateButtonState('auto');
          }
        });
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  } catch (e) {
    // fail silently
  }
})();
