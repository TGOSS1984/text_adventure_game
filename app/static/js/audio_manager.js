/**
 * audio_manager.js
 *
 * Centralised audio controller for Elden Souls.
 * Manages background music and SFX across all pages with consistent
 * localStorage state so music position and play/pause preference survive
 * full page navigations.
 *
 * Usage — each page script calls:
 *   AudioManager.initMusic(src, { volume, stateKey })
 *   AudioManager.bindControls('#playMusic', '#pauseMusic')
 *
 * Music only starts after the first genuine user interaction with the page
 * (a click or keydown). Autoplay is never attempted on load.
 */

const AudioManager = (() => {

  // ── Internal state ────────────────────────────────────────────────────────

  let _audio       = null;   // HTMLAudioElement for background music
  let _stateKey    = '';     // localStorage key for play/pause preference
  let _timeKey     = '';     // localStorage key for playback position
  let _started     = false;  // has music been started this session?
  let _userReady   = false;  // has the user interacted with the page?

  // ── Private helpers ───────────────────────────────────────────────────────

  function _savePosition() {
    if (_audio && _timeKey) {
      localStorage.setItem(_timeKey, _audio.currentTime);
    }
  }

  function _restorePosition() {
    if (!_audio || !_timeKey) return;
    const t = parseFloat(localStorage.getItem(_timeKey));
    if (!isNaN(t) && t > 0) {
      _audio.currentTime = t;
    }
  }

  function _play() {
    if (!_audio) return;
    _restorePosition();
    _audio.play()
      .then(() => {
        _started = true;
        if (_stateKey) localStorage.setItem(_stateKey, 'playing');
        // Clear saved position once playback resumes successfully
        if (_timeKey) localStorage.removeItem(_timeKey);
      })
      .catch(err => console.warn('[AudioManager] play() blocked:', err));
  }

  function _pause() {
    if (!_audio) return;
    _savePosition();
    _audio.pause();
    _started = false;
    if (_stateKey) localStorage.setItem(_stateKey, 'paused');
  }

  /**
   * Called on the first user interaction. Starts music if the stored
   * preference is 'playing' (or if no preference has been set yet,
   * meaning this is a first visit — we start music on first interaction
   * by default so the experience feels atmospheric).
   */
  function _onFirstInteraction() {
    if (_userReady) return;
    _userReady = true;

    // Remove the listeners — we only need them once
    document.removeEventListener('click',   _onFirstInteraction, true);
    document.removeEventListener('keydown', _onFirstInteraction, true);

    const savedState = _stateKey ? localStorage.getItem(_stateKey) : null;

    // Start if: no preference saved yet (first ever visit) OR preference was 'playing'
    if (savedState === null || savedState === 'playing') {
      _play();
    }
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /**
   * Initialise background music for the current page.
   *
   * @param {string} src       - Path to the audio file
   * @param {object} options
   *   @param {number} [options.volume=0.4]          - Playback volume 0–1
   *   @param {string} [options.stateKey='musicState'] - localStorage key for play state
   *   @param {string} [options.timeKey='musicTime']   - localStorage key for position
   */
  function initMusic(src, { volume = 0.4, stateKey = 'musicState', timeKey = 'musicTime' } = {}) {
    _stateKey = stateKey;
    _timeKey  = timeKey;

    _audio       = new Audio(src);
    _audio.loop  = true;
    _audio.volume = volume;

    // Listen for first interaction using capture so we catch it before
    // any button's own handler runs
    document.addEventListener('click',   _onFirstInteraction, true);
    document.addEventListener('keydown', _onFirstInteraction, true);

    return _audio; // expose element if caller needs it (e.g. for src swapping)
  }

  /**
   * Wire up play / pause buttons by selector or element reference.
   *
   * @param {string|Element} playSelector
   * @param {string|Element} pauseSelector
   */
  function bindControls(playSelector, pauseSelector) {
    const playBtn  = typeof playSelector  === 'string' ? document.querySelector(playSelector)  : playSelector;
    const pauseBtn = typeof pauseSelector === 'string' ? document.querySelector(pauseSelector) : pauseSelector;

    if (playBtn) {
      playBtn.addEventListener('click', () => _play());
    }
    if (pauseBtn) {
      pauseBtn.addEventListener('click', () => _pause());
    }
  }

  /**
   * Save the current playback position to localStorage.
   * Call this just before a form submit or navigation so the next
   * page can restore the position seamlessly.
   */
  function savePosition() {
    _savePosition();
  }

  /**
   * Swap the music source mid-page (e.g. normal → boss music).
   * Preserves the current play/pause state.
   */
  function swapTrack(newSrc, { volume } = {}) {
    if (!_audio) return;
    const wasPlaying = !_audio.paused;
    _audio.pause();
    _audio.src    = newSrc;
    if (volume !== undefined) _audio.volume = volume;
    _audio.currentTime = 0;
    if (wasPlaying) {
      _audio.play().catch(e => console.warn('[AudioManager] swapTrack play blocked:', e));
    }
  }

  /**
   * Play a one-shot SFX by audio element ID.
   * Rewinds before playing so rapid repeated triggers always fire.
   */
  function playSfx(elementId) {
    const el = document.getElementById(elementId);
    if (!el) {
      console.warn(`[AudioManager] SFX element not found: #${elementId}`);
      return;
    }
    el.currentTime = 0;
    el.play().catch(e => console.warn(`[AudioManager] SFX error [${elementId}]:`, e));
  }

  return { initMusic, bindControls, savePosition, swapTrack, playSfx };

})();