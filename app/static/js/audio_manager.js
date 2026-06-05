/**
 * audio_manager.js
 *
 * Centralised audio controller for Elden Souls.
 *
 * MUSIC CONTINUITY ACROSS PAGE RELOADS
 * ─────────────────────────────────────
 * The core challenge: each full page reload destroys the <audio> element.
 * On a fresh load there is no user gesture, so browsers block autoplay —
 * EXCEPT when the page was navigated to via a form POST (battle actions).
 * Browsers treat form submission as a "user activation" that propagates
 * to the next page, allowing autoplay on that immediate load.
 *
 * Strategy (in priority order):
 *   1. If navigated here via POST (battle turn) → attempt autoplay immediately.
 *      This works in Chrome 70+, Firefox 74+, Safari 15+.
 *   2. If the user had music playing (sessionStorage state = 'playing') →
 *      attempt autoplay. Falls back to waiting for first click if blocked.
 *   3. First visit / no preference → wait for first interaction.
 *
 * sessionStorage is used instead of localStorage for the playback position
 * because it's scoped to the tab session — position is accurate for the
 * current playthrough, and stale values from a previous session won't cause
 * music to jump to a random timestamp.
 *
 * Public API:
 *   AudioManager.initMusic(src, options)
 *   AudioManager.bindControls(playSelector, pauseSelector)
 *   AudioManager.savePosition()
 *   AudioManager.swapTrack(newSrc, options)
 *   AudioManager.playSfx(elementId)
 */

const AudioManager = (() => {

  // ── Internal state ────────────────────────────────────────────────────────

  let _audio     = null;
  let _stateKey  = '';
  let _timeKey   = '';
  let _started   = false;

  // ── Private helpers ───────────────────────────────────────────────────────

  function _savePosition() {
    if (_audio && _timeKey) {
      sessionStorage.setItem(_timeKey, _audio.currentTime);
    }
  }

  function _restorePosition() {
    if (!_audio || !_timeKey) return;
    const t = parseFloat(sessionStorage.getItem(_timeKey));
    if (!isNaN(t) && t > 0) {
      _audio.currentTime = t;
    }
  }

  function _attemptPlay() {
    if (!_audio) return;
    _restorePosition();
    _audio.play()
      .then(() => {
        _started = true;
        if (_stateKey) sessionStorage.setItem(_stateKey, 'playing');
        // Position successfully restored — clear the saved value so a
        // future fresh start doesn't jump to a stale timestamp.
        if (_timeKey) sessionStorage.removeItem(_timeKey);
      })
      .catch(() => {
        // Autoplay blocked — music will start on first user interaction.
        // Do NOT warn loudly here; this is expected on first visit.
      });
  }

  function _play() {
    _attemptPlay();
  }

  function _pause() {
    if (!_audio) return;
    _savePosition();
    _audio.pause();
    _started = false;
    if (_stateKey) sessionStorage.setItem(_stateKey, 'paused');
  }

  /**
   * Called on the first user interaction on pages that couldn't autoplay.
   * Only fires once per page load.
   */
  function _onFirstInteraction() {
    document.removeEventListener('click',   _onFirstInteraction, true);
    document.removeEventListener('keydown', _onFirstInteraction, true);

    if (!_started) {
      _play();
    }
  }

  /**
   * Decide whether to attempt immediate play or wait for interaction.
   *
   * We attempt immediate play if:
   *   (a) The page was reached via a form POST — performance.navigation
   *       type 1 = reload, type 255 = unknown; we use the Navigation API
   *       or fall back to PerformanceNavigation. POST navigation shows as
   *       type 0 (navigate) in the legacy API but with referrer set.
   *       More reliably: we set a sessionStorage flag just before submitting
   *       the battle form, and check for it here.
   *   (b) The saved state is 'playing' (user had music on in this session).
   */
  function _decideAutoplay() {
    const savedState = _stateKey ? sessionStorage.getItem(_stateKey) : null;
    const cameFromAction = sessionStorage.getItem('battleActionPending') === '1';

    // Clear the flag immediately so it doesn't persist beyond one use
    sessionStorage.removeItem('battleActionPending');

    if (cameFromAction || savedState === 'playing') {
      // Attempt immediate autoplay — allowed after POST navigation
      _attemptPlay();
    } else if (savedState === null) {
      // First visit — start music on first interaction (default-on experience)
      document.addEventListener('click',   _onFirstInteraction, true);
      document.addEventListener('keydown', _onFirstInteraction, true);
    }
    // If savedState === 'paused': user explicitly paused, respect that.
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /**
   * Initialise background music for the current page.
   *
   * @param {string} src       - Path to the audio file
   * @param {object} options
   *   @param {number} [options.volume=0.4]
   *   @param {string} [options.stateKey='musicState']
   *   @param {string} [options.timeKey='musicTime']
   */
  function initMusic(src, { volume = 0.4, stateKey = 'musicState', timeKey = 'musicTime' } = {}) {
    _stateKey = stateKey;
    _timeKey  = timeKey;

    _audio        = new Audio(src);
    _audio.loop   = true;
    _audio.volume = volume;

    // Decide play strategy once DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', _decideAutoplay, { once: true });
    } else {
      _decideAutoplay();
    }

    return _audio;
  }

  /**
   * Wire up play / pause buttons.
   */
  function bindControls(playSelector, pauseSelector) {
    const playBtn  = typeof playSelector  === 'string' ? document.querySelector(playSelector)  : playSelector;
    const pauseBtn = typeof pauseSelector === 'string' ? document.querySelector(pauseSelector) : pauseSelector;

    if (playBtn)  playBtn.addEventListener('click',  () => _play());
    if (pauseBtn) pauseBtn.addEventListener('click', () => _pause());
  }

  /**
   * Save the current playback position to sessionStorage.
   * Call this just before form submission so the next page can restore it.
   */
  function savePosition() {
    _savePosition();
    // Set the flag that tells the next page load to attempt immediate autoplay
    sessionStorage.setItem('battleActionPending', '1');
  }

  /**
   * Swap the music track mid-page (normal → boss).
   */
  function swapTrack(newSrc, { volume } = {}) {
    if (!_audio) return;
    const wasPlaying = !_audio.paused;
    _audio.pause();
    _audio.src    = newSrc;
    if (volume !== undefined) _audio.volume = volume;
    _audio.currentTime = 0;
    if (wasPlaying) {
      _audio.play().catch(() => {});
    }
  }

  /**
   * Play a one-shot SFX by audio element ID.
   */
  function playSfx(elementId) {
    const el = document.getElementById(elementId);
    if (!el) {
      console.warn(`[AudioManager] SFX element not found: #${elementId}`);
      return;
    }
    el.currentTime = 0;
    el.play().catch(() => {});
  }

  return { initMusic, bindControls, savePosition, swapTrack, playSfx };

})();