/**
 * char_select_music.js
 * Background music for the character selection / title screen (index.html).
 *
 * Depends on: audio_manager.js (must be loaded first)
 *
 * Changes from original:
 * - Removed unconditional audio.play() attempts on load
 * - Removed scroll-triggered music start (scroll is not genuine intent)
 * - Music starts on first click or keydown only, via AudioManager
 * - Play/Pause buttons still work as before
 */

document.addEventListener('DOMContentLoaded', function () {

  AudioManager.initMusic('/static/sounds/music/main_theme.mp3', {
    volume:   0.4,
    stateKey: 'charSelectMusicState',
    timeKey:  'charSelectMusicTime',
  });

  AudioManager.bindControls('#playMusic', '#pauseMusic');

});