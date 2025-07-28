/*
char_select_music.js
Plays music on the character selection screen (index.html)
*/

document.addEventListener('DOMContentLoaded', function () {
    const audio = new Audio('/static/sounds/music/main_theme.mp3');
    audio.loop = true;
    audio.volume = 0.4;

    const playBtn = document.getElementById('playMusic');
    const pauseBtn = document.getElementById('pauseMusic');

    let musicStarted = false;

    // Function to play music and update state
    function startMusic() {
        if (!musicStarted) {
            audio.play().then(() => {
                localStorage.setItem('charSelectMusicState', 'playing');
                musicStarted = true;
            }).catch((err) => {
                console.warn("Audio play failed:", err);
            });
        }
    }

    // Restore previous state
    const savedState = localStorage.getItem('charSelectMusicState');
    if (savedState === 'playing') {
        startMusic();
    } else {
        // Attempt autoplay anyway
        audio.play()
            .then(() => {
                localStorage.setItem('charSelectMusicState', 'playing');
                musicStarted = true;
            })
            .catch(() => {
                console.warn("Autoplay blocked – waiting for user interaction...");
            });
    }

    // Fallback: start music on *any* interaction
    function handleUserInteraction() {
        startMusic();
        document.removeEventListener('click', handleUserInteraction);
        document.removeEventListener('keydown', handleUserInteraction);
        document.removeEventListener('scroll', handleUserInteraction);
    }

    document.addEventListener('click', handleUserInteraction);
    document.addEventListener('keydown', handleUserInteraction);
    document.addEventListener('scroll', handleUserInteraction);

    // Play button
    if (playBtn) {
        playBtn.addEventListener('click', () => {
            startMusic();
        });
    }

    // Pause button
    if (pauseBtn) {
        pauseBtn.addEventListener('click', () => {
            audio.pause();
            localStorage.setItem('charSelectMusicState', 'paused');
            musicStarted = false;
        });
    }
});