/**
 * settings.js
 * Commit 13 — Settings panel for Elden Souls.
 *
 * Responsibilities:
 * - Renders a gear icon button (fixed, bottom-right) on every page
 * - Slides in a settings panel from the right on click
 * - Persists all settings to localStorage
 * - Applies settings on load (volume, SFX volume, typewriter speed)
 * - Wires live sliders into AudioManager (music + SFX volume)
 * - Typewriter speed is stored; typewriter.js reads it on next page load
 *
 * Settings keys (localStorage):
 *   'musicVolume'  — float 0.0–1.0  (default 0.4)
 *   'sfxVolume'    — float 0.0–1.0  (default 0.8)
 *   'twSpeed'      — string: 'slow' | 'normal' | 'fast' | 'instant' (default 'normal')
 *
 * Depends on: audio_manager.js loaded before this script.
 * Safe to load on pages without AudioManager (guards with typeof check).
 */

(function () {

  // ── Defaults ───────────────────────────────────────────────────────────────
  const DEFAULTS = {
    musicVolume: 0.4,
    sfxVolume:   0.8,
    twSpeed:     'normal',
  };

  // ── Load / save helpers ────────────────────────────────────────────────────
  function load(key) {
    const v = localStorage.getItem(key);
    return v === null ? DEFAULTS[key] : v;
  }

  function save(key, value) {
    localStorage.setItem(key, value);
  }

  // ── Apply stored volume on page load ──────────────────────────────────────
  // Called as early as possible so music starts at the right volume.
  function applyStoredVolume() {
    const musicVol = parseFloat(load('musicVolume'));
    const sfxVol   = parseFloat(load('sfxVolume'));

    // Patch AudioManager.initMusic to intercept the volume option
    if (typeof AudioManager !== 'undefined') {
      const _origInit = AudioManager.initMusic.bind(AudioManager);
      AudioManager.initMusic = function (src, opts = {}) {
        opts.volume = musicVol;
        return _origInit(src, opts);
      };
    }

    // Store sfxVol on window so battle_sounds.js can pick it up
    window._sfxVolume = sfxVol;
  }

  // Apply SFX volume to all <audio> elements with an id starting "attack-",
  // "block", "dodge", or "estus" — done after DOM ready.
  function applySfxVolume(vol) {
    const sfxIds = ['attack-knight','attack-mage','attack-rogue','attack-archer',
                    'block','dodge','estus'];
    sfxIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.volume = vol;
    });
  }

  // Apply music volume live to whatever AudioManager is playing right now.
  function applyMusicVolume(vol) {
    if (typeof AudioManager === 'undefined') return;
    // AudioManager keeps _audio private; reach it via the public savePosition
    // indirection — instead we just walk document audio elements
    document.querySelectorAll('audio#music, audio[loop]').forEach(el => {
      el.volume = vol;
    });
  }

  // ── Build the panel HTML ───────────────────────────────────────────────────
  function buildPanel() {
    const musicVol = parseFloat(load('musicVolume'));
    const sfxVol   = parseFloat(load('sfxVolume'));
    const twSpeed  = load('twSpeed');

    // ── Gear toggle button ────────────────────────────────────────────────────
    const toggleBtn = document.createElement('button');
    toggleBtn.id        = 'settings-toggle';
    toggleBtn.innerHTML = '<i class="fas fa-gear"></i>';
    toggleBtn.setAttribute('aria-label', 'Open settings');
    toggleBtn.setAttribute('title', 'Settings');

    // ── Panel backdrop ────────────────────────────────────────────────────────
    const backdrop = document.createElement('div');
    backdrop.id = 'settings-backdrop';

    // ── Panel container ───────────────────────────────────────────────────────
    const panel = document.createElement('div');
    panel.id   = 'settings-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Settings');
    panel.setAttribute('aria-modal', 'true');

    panel.innerHTML = `
      <div class="settings-header">
        <h2 class="settings-title"><i class="fas fa-gear"></i> Settings</h2>
        <button id="settings-close" aria-label="Close settings" class="settings-close-btn">
          <i class="fas fa-xmark"></i>
        </button>
      </div>

      <div class="settings-body">

        <section class="settings-section">
          <h3 class="settings-section-title"><i class="fas fa-music"></i> Audio</h3>

          <div class="settings-row">
            <label for="setting-music-vol" class="settings-label">
              Music Volume
              <span class="settings-val" id="music-vol-display">${Math.round(musicVol * 100)}%</span>
            </label>
            <input
              type="range" id="setting-music-vol"
              class="settings-slider"
              min="0" max="100" step="1"
              value="${Math.round(musicVol * 100)}"
              aria-label="Music volume"
            >
          </div>

          <div class="settings-row">
            <label for="setting-sfx-vol" class="settings-label">
              SFX Volume
              <span class="settings-val" id="sfx-vol-display">${Math.round(sfxVol * 100)}%</span>
            </label>
            <input
              type="range" id="setting-sfx-vol"
              class="settings-slider"
              min="0" max="100" step="1"
              value="${Math.round(sfxVol * 100)}"
              aria-label="SFX volume"
            >
          </div>
        </section>

        <section class="settings-section">
          <h3 class="settings-section-title"><i class="fas fa-keyboard"></i> Story Text</h3>

          <div class="settings-row settings-row--stacked">
            <span class="settings-label">Typewriter Speed</span>
            <div class="settings-speed-btns" role="group" aria-label="Typewriter speed">
              <button class="speed-btn ${twSpeed === 'slow'    ? 'speed-btn--active' : ''}" data-speed="slow">Slow</button>
              <button class="speed-btn ${twSpeed === 'normal'  ? 'speed-btn--active' : ''}" data-speed="normal">Normal</button>
              <button class="speed-btn ${twSpeed === 'fast'    ? 'speed-btn--active' : ''}" data-speed="fast">Fast</button>
              <button class="speed-btn ${twSpeed === 'instant' ? 'speed-btn--active' : ''}" data-speed="instant">Instant</button>
            </div>
          </div>
        </section>

        <section class="settings-section settings-section--footer">
          <button id="settings-reset" class="settings-reset-btn">
            <i class="fas fa-rotate-left"></i> Reset to Defaults
          </button>
        </section>

      </div>
    `;

    document.body.appendChild(toggleBtn);
    document.body.appendChild(backdrop);
    document.body.appendChild(panel);

    return { toggleBtn, backdrop, panel };
  }

  // ── Wire up interactions ───────────────────────────────────────────────────
  function wirePanel({ toggleBtn, backdrop, panel }) {

    function openPanel() {
      panel.classList.add('settings-panel--open');
      backdrop.classList.add('settings-backdrop--visible');
      document.body.classList.add('settings-open');
      toggleBtn.setAttribute('aria-expanded', 'true');
      // Focus the close button for keyboard accessibility
      setTimeout(() => {
        const closeBtn = document.getElementById('settings-close');
        if (closeBtn) closeBtn.focus();
      }, 300);
    }

    function closePanel() {
      panel.classList.remove('settings-panel--open');
      backdrop.classList.remove('settings-backdrop--visible');
      document.body.classList.remove('settings-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
      toggleBtn.focus();
    }

    toggleBtn.addEventListener('click', () => {
      const isOpen = panel.classList.contains('settings-panel--open');
      isOpen ? closePanel() : openPanel();
    });

    backdrop.addEventListener('click', closePanel);

    document.getElementById('settings-close').addEventListener('click', closePanel);

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panel.classList.contains('settings-panel--open')) {
        closePanel();
      }
    });

    // ── Music volume slider ────────────────────────────────────────────────
    const musicSlider  = document.getElementById('setting-music-vol');
    const musicDisplay = document.getElementById('music-vol-display');

    musicSlider.addEventListener('input', () => {
      const vol = musicSlider.value / 100;
      musicDisplay.textContent = musicSlider.value + '%';
      save('musicVolume', vol);
      applyMusicVolume(vol);
    });

    // ── SFX volume slider ──────────────────────────────────────────────────
    const sfxSlider  = document.getElementById('setting-sfx-vol');
    const sfxDisplay = document.getElementById('sfx-vol-display');

    sfxSlider.addEventListener('input', () => {
      const vol = sfxSlider.value / 100;
      sfxDisplay.textContent = sfxSlider.value + '%';
      save('sfxVolume', vol);
      window._sfxVolume = vol;
      applySfxVolume(vol);
    });

    // ── Typewriter speed buttons ───────────────────────────────────────────
    panel.querySelectorAll('.speed-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        panel.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('speed-btn--active'));
        btn.classList.add('speed-btn--active');
        save('twSpeed', btn.dataset.speed);
      });
    });

    // ── Reset to defaults ──────────────────────────────────────────────────
    document.getElementById('settings-reset').addEventListener('click', () => {
      Object.entries(DEFAULTS).forEach(([k, v]) => save(k, v));

      musicSlider.value       = Math.round(DEFAULTS.musicVolume * 100);
      musicDisplay.textContent = musicSlider.value + '%';
      applyMusicVolume(DEFAULTS.musicVolume);

      sfxSlider.value         = Math.round(DEFAULTS.sfxVolume * 100);
      sfxDisplay.textContent   = sfxSlider.value + '%';
      applySfxVolume(DEFAULTS.sfxVolume);

      panel.querySelectorAll('.speed-btn').forEach(btn => {
        btn.classList.toggle('speed-btn--active', btn.dataset.speed === DEFAULTS.twSpeed);
      });
    });
  }

  // ── Boot ───────────────────────────────────────────────────────────────────
  // applyStoredVolume runs immediately (before DOMContentLoaded) so the
  // AudioManager.initMusic patch is in place before any page scripts call it.
  applyStoredVolume();

  document.addEventListener('DOMContentLoaded', () => {
    // Apply SFX volume to any pre-existing audio elements
    applySfxVolume(parseFloat(load('sfxVolume')));

    // Build and wire the panel
    const elements = buildPanel();
    wirePanel(elements);

    // Re-apply SFX volume after HTMX swaps (battle screen audio elements persist
    // outside #battle-state but it's safe to re-set them each turn)
    document.body.addEventListener('htmx:afterSwap', () => {
      applySfxVolume(parseFloat(load('sfxVolume')));
    });
  });

})();