/*
File for the sound in the game
Manages the audio, used in game.html
*/

document.addEventListener('DOMContentLoaded', function () {
    const audio = new Audio('/static/sounds/music/intro.mp3');
    audio.loop = true;
    audio.volume = 0.3;

    const playBtn = document.getElementById('playMusic');
    const pauseBtn = document.getElementById('pauseMusic');

    playBtn.addEventListener('click', () => {
        audio.play().catch(e => console.log("Audio play blocked:", e));
    });

    pauseBtn.addEventListener('click', () => {
        audio.pause();
    });
});