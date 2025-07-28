/*
File for the sound in the game
Manages the audio, used in game.html
*/

document.addEventListener('DOMContentLoaded', function () {
    const audio = new Audio('/static/sounds/music/story_theme.mp3');
    audio.loop = true;
    audio.volume = 0.3;

    const playBtn = document.getElementById('playMusic');
    const pauseBtn = document.getElementById('pauseMusic');

    // Restore previous music state if available
    const musicState = localStorage.getItem('mainMusicState');
    if (musicState === 'playing') {
        audio.play().catch(e => console.warn("Autoplay blocked:", e));
    }

    // Play on page load by default (fallback)
    audio.play()
        .then(() => {
            localStorage.setItem('mainMusicState', 'playing');
        })
        .catch(err => {
            console.warn("Autoplay failed (user interaction required):", err);
            // Show unmuted state but let user trigger play
        });

    // Button controls
    playBtn.addEventListener('click', () => {
        audio.play().then(() => {
            localStorage.setItem('mainMusicState', 'playing');
        }).catch(e => console.warn("Play blocked:", e));
    });

    pauseBtn.addEventListener('click', () => {
        audio.pause();
        localStorage.setItem('mainMusicState', 'paused');
    });
});


