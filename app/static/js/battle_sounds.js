/* Battle Sounds */

console.log("battle_sounds.js loaded");

function playSound(id) {
  const audio = document.getElementById(id);
  if (audio) {
    audio.currentTime = 0;
    audio.play().catch((e) => console.warn(`Sound error [${id}]:`, e));
  } else {
    console.warn(`Missing <audio id="${id}">`);
  }
}

function setBackgroundMusic(isBossFight = false) {
  const music = document.getElementById('music');
  const src = isBossFight
    ? '/static/sounds/music/ambient_boss.mp3'
    : '/static/sounds/music/ambient_normal.mp3';

  if (!music.src.includes(src)) {
    music.src = src;
  }

  music.loop = true;
  music.volume = 0.5;

  // Restore time if saved
  const savedTime = parseFloat(localStorage.getItem('musicTime'));
  if (!isNaN(savedTime)) {
    music.currentTime = savedTime;
  }

  return music;
}

function playAttackSound(playerClass) {
  const id = `attack-${playerClass}`;
  console.log("Attempting to play:", id);
  playSound(id);
}

function playBlockSound() { playSound('block'); }
function playDodgeSound() { playSound('dodge'); }
function playEstusSound() { playSound('estus'); }

document.addEventListener('DOMContentLoaded', () => {
  const playerClass = document.body.dataset.class || 'knight';
  const isBoss = document.body.dataset.boss === 'true';

  const music = setBackgroundMusic(isBoss);
  const playBtn = document.getElementById('playMusic');
  const pauseBtn = document.getElementById('pauseMusic');
  const buttons = document.querySelectorAll('.battle-btn');
  const form = document.getElementById('battleForm');

  // Restore music state
  const musicState = localStorage.getItem('musicState');
  if (musicState === 'playing') {
    music.play().then(() => {
      localStorage.removeItem('musicTime');
    }).catch(e => console.warn("Autoplay blocked:", e));
  }

  // Play/Pause buttons
  if (playBtn && pauseBtn) {
    playBtn.addEventListener('click', () => {
      music.play().then(() => {
        localStorage.setItem('musicState', 'playing');
      }).catch(e => console.warn("Play blocked:", e));
    });

    pauseBtn.addEventListener('click', () => {
      music.pause();
      localStorage.setItem('musicState', 'paused');
    });
  }

  // Action buttons
  buttons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const action = btn.value;
      console.log("Action triggered:", action);

      switch (action) {
        case 'attack': playAttackSound(playerClass); break;
        case 'block': playBlockSound(); break;
        case 'dodge': playDodgeSound(); break;
        case 'estus': playEstusSound(); break;
      }

      // Save music playback position before reload
      localStorage.setItem('musicTime', music.currentTime);

      setTimeout(() => {
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'action';
        hiddenInput.value = action;
        form.appendChild(hiddenInput);
        form.submit();
      }, 1200);
    });
  });
});

// Battle Flurry flash/pulse

function triggerFlurryFlash() {
  const flash = document.getElementById('flurry-flash');
  if (flash) {
    flash.classList.add('flurry-animate');
    setTimeout(() => {
      flash.classList.remove('flurry-animate');
    }, 1000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const moveHint = document.getElementById('move-hint');
  if (moveHint && moveHint.innerText.toLowerCase().includes("flurry")) {
    triggerFlurryFlash();
  }
});

