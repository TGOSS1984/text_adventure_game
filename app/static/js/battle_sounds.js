/**
 * battle_sounds.js
 * SFX and background music for the battle screen (battle.html).
 *
 * Depends on: audio_manager.js (must be loaded first)
 *
 * Changes from original:
 * - Removed unconditional music.play() on load; music resumes via AudioManager
 *   only if the player had it playing before (stored preference)
 * - Submit delay reduced: 300 ms is enough for the attack SFX to audibly
 *   start before the page transitions. The original 1200 ms caused the
 *   music-position save → reload gap that produced the audio stutter.
 * - Music position is saved via AudioManager.savePosition() immediately
 *   on button click (before the delay) so the next page load restores
 *   it accurately.
 * - Flurry flash and Estus bubble logic preserved unchanged.
 * - setBackgroundMusic kept as a thin wrapper around AudioManager.initMusic
 *   so boss vs normal tracks still work.
 */

// ── Music setup ────────────────────────────────────────────────────────────

function initBattleMusic(isBoss) {
  const src = isBoss
    ? '/static/sounds/music/ambient_boss.mp3'
    : '/static/sounds/music/ambient_normal.mp3';

  AudioManager.initMusic(src, {
    volume:   0.5,
    stateKey: 'battleMusicState',
    timeKey:  'battleMusicTime',
  });

  AudioManager.bindControls('#playMusic', '#pauseMusic');
}

// ── SFX helpers ────────────────────────────────────────────────────────────

function playAttackSound(playerClass) {
  AudioManager.playSfx(`attack-${playerClass}`);
}
function playBlockSound()  { AudioManager.playSfx('block'); }
function playDodgeSound()  { AudioManager.playSfx('dodge'); }
function playEstusSound()  { AudioManager.playSfx('estus'); }

// ── Estus bubble animation ─────────────────────────────────────────────────

function triggerEstusAnimation() {
  // Screen flash
  const healingFlash = document.getElementById('healing-flash');
  if (healingFlash) {
    healingFlash.classList.add('active');
    setTimeout(() => healingFlash.classList.remove('active'), 700);
  }

  // Bubble particles
  const bubbleContainer = document.getElementById('bubble-container');
  if (!bubbleContainer) return;

  // Mix of small bubbles and a few larger orbs for depth
  const particles = [
    ...Array.from({ length: 12 }, () => ({ type: 'bubble', size: Math.random() * 40 + 8 })),
    ...Array.from({ length: 3  }, () => ({ type: 'orb',    size: Math.random() * 28 + 22 })),
  ];

  particles.forEach((p, i) => {
    const el = document.createElement('div');
    el.classList.add('bubble', p.type === 'orb' ? 'bubble--orb' : '');

    el.style.width  = `${p.size}px`;
    el.style.height = `${p.size}px`;

    // Spread across the full width but avoid the very edges
    el.style.left = `${5 + Math.random() * 90}vw`;

    // Stagger spawning so they don't all start together
    el.style.animationDelay = `${i * 60}ms`;

    // Slight horizontal drift — applied as a CSS variable read by the animation
    el.style.setProperty('--drift', `${(Math.random() - 0.5) * 80}px`);

    bubbleContainer.appendChild(el);
    setTimeout(() => el.remove(), 3500);
  });
}

// ── Flurry flash ───────────────────────────────────────────────────────────

function triggerFlurryFlash() {
  const flash = document.getElementById('flurry-flash');
  if (!flash) return;

  // Separate the background flash from the sigil so they can animate
  // independently — the sigil scales up while the overlay pulses
  flash.classList.add('flurry-animate');
  setTimeout(() => flash.classList.remove('flurry-animate'), 1200);
}

// ── DOMContentLoaded ───────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const playerClass = document.body.dataset.class || 'knight';
  const isBoss      = document.body.dataset.boss === 'true';

  initBattleMusic(isBoss);

  const buttons = document.querySelectorAll('.battle-btn');
  const form    = document.getElementById('battleForm');

  buttons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const action = btn.value;

      // ── Play SFX & trigger visual effects immediately ──
      switch (action) {
        case 'attack': playAttackSound(playerClass); break;
        case 'block':  playBlockSound();  break;
        case 'dodge':  playDodgeSound();  break;
        case 'estus':
          playEstusSound();
          triggerEstusAnimation();
          break;
      }

      // Save music position NOW — before the delay — so the value is
      // accurate when the next page reads it from localStorage
      AudioManager.savePosition();

      // Short delay (300 ms) lets the SFX begin audibly before page
      // transition. Previous 1200 ms was the main cause of audio stutter.
      setTimeout(() => {
        const hiddenInput = document.createElement('input');
        hiddenInput.type  = 'hidden';
        hiddenInput.name  = 'action';
        hiddenInput.value = action;
        form.appendChild(hiddenInput);
        form.submit();
      }, 300);
    });
  });

  // Show flurry warning animation if the move hint mentions flurry
  const moveHint = document.getElementById('move-hint');
  if (moveHint && moveHint.innerText.toLowerCase().includes('flurry')) {
    triggerFlurryFlash();
  }
});