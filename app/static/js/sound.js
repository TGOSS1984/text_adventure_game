/**
 * sound.js
 * Background music for the story / game screen (game.html).
 *
 * Depends on: audio_manager.js (must be loaded first)
 *
 * Changes from original:
 * - Removed unconditional audio.play() on DOMContentLoaded
 * - Music now starts only on first user interaction (click / keydown)
 * - Play/Pause state persisted via AudioManager using 'storyMusicState' key
 */

document.addEventListener('DOMContentLoaded', function () {

  AudioManager.initMusic('/static/sounds/music/story_theme.mp3', {
    volume:   0.3,
    stateKey: 'storyMusicState',
    timeKey:  'storyMusicTime',
  });

  AudioManager.bindControls('#playMusic', '#pauseMusic');

});




