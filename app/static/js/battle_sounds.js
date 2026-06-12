/**
 * battle_sounds.js
 * SFX, background music, and battle visual effects for battle.html.
 * Depends on: audio_manager.js (must be loaded first)
 *
 * Commit 11 addition:
 * - triggerPhaseTransition(): fires #phase-flash + enemy image shake
 * - htmx:afterSwap handler reads data-phase-change="true" on the swapped
 *   fragment root div and calls triggerPhaseTransition() once, then clears
 *   the attribute so it cannot double-fire.
 *
 * Commit 20 additions:
 * - playSpecialSound(cls): plays special-<class> SFX if the audio element
 *   exists and has a src; falls back to the class attack sound so there is
 *   always audio feedback even before real special SFX files are added.
 * - 'special' case added to the action switch in bindBattleButtons() so
 *   the special button now triggers SFX + a gold screen flash effect.
 * - triggerSpecialFlash(): brief gold/white screen flash on special use,
 *   distinct from the red flurry flash and green estus flash.
 */

// ── Music ──────────────────────────────────────────────────────────────────

function initBattleMusic(isBoss) {
  AudioManager.initMusic(
    isBoss ? '/static/sounds/music/ambient_boss.mp3'
           : '/static/sounds/music/ambient_normal.mp3',
    { volume: 0.5, stateKey: 'battleMusicState', timeKey: 'battleMusicTime' }
  );
  AudioManager.bindControls('#playMusic', '#pauseMusic');
}

// ── SFX ────────────────────────────────────────────────────────────────────

function playAttackSound(cls)  { AudioManager.playSfx('attack-' + cls); }
function playBlockSound()      { AudioManager.playSfx('block'); }
function playDodgeSound()      { AudioManager.playSfx('dodge'); }
function playEstusSound()      { AudioManager.playSfx('estus'); }

/**
 * Commit 20: playSpecialSound
 * Attempts to play the class-specific special SFX (special-<cls>).
 * Falls back to the standard attack sound for that class if the special
 * audio element is missing or has no src — ensures feedback is always
 * present even before real special SFX files are supplied.
 *
 * Expected audio element IDs (add to battle.html when files are ready):
 *   #special-knight  →  sounds/sound_effects/special/knight.mp3
 *   #special-mage    →  sounds/sound_effects/special/mage.mp3
 *   #special-rogue   →  sounds/sound_effects/special/rogue.mp3
 *   #special-archer  →  sounds/sound_effects/special/archer.mp3
 */
function playSpecialSound(cls) {
  const specialEl = document.getElementById('special-' + cls);
  if (specialEl && specialEl.src && specialEl.src !== window.location.href) {
    AudioManager.playSfx('special-' + cls);
  } else {
    // Fallback: use the class attack sound until real files exist
    AudioManager.playSfx('attack-' + cls);
  }
}

function getSfxDelay(id) {
  const el  = document.getElementById(id);
  const dur = el && isFinite(el.duration) ? el.duration : 0;
  return dur ? Math.min(Math.round(dur * 1000) + 150, 3200) : 800;
}

// ── Commit 20: Special move flash ─────────────────────────────────────────
//
// Brief gold/white pulse — distinct from red (flurry) and green (estus).
// Uses #special-flash, a fixed overlay added in battle.html (Commit 20).

function triggerSpecialFlash() {
  const flash = document.getElementById('special-flash');
  if (!flash) return;
  flash.classList.remove('special-flash-animate');
  void flash.offsetWidth;   // force reflow to restart animation
  flash.classList.add('special-flash-animate');
  flash.addEventListener(
    'animationend',
    () => flash.classList.remove('special-flash-animate'),
    { once: true }
  );
}

// ── Estus bubble system ────────────────────────────────────────────────────
//
// Design brief:
//   • Green screen pulse on drink
//   • Soap-bubble look: dark/transparent centre, glowing green ring at edge,
//     small specular highlight — like the reference screenshot but in green
//   • Bubbles start at bottom, rise slowly to near the top of the screen
//   • Gradual opacity fade-in at birth, gradual fade-out near top
//   • Varying sizes (small to medium — nothing huge)
//   • Varying transparency per bubble
//   • ~25 bubbles, staggered spawn so they emerge as a flowing wave
//   • True sinusoidal horizontal drift (no CSS keyframe reversals)
//   • Canvas-rendered for smooth performance

const EstusBubbles = (() => {

  let canvas  = null;
  let ctx     = null;
  let bubbles = [];
  let running = false;

  // ── Smoothstep (Ken Perlin) — zero first-derivative at endpoints ──────────
  function ss(a, b, x) {
    const t = Math.max(0, Math.min(1, (x - a) / (b - a)));
    return t * t * (3 - 2 * t);
  }

  // ── Opacity envelope ───────────────────────────────────────────────────────
  function envelope(t) {
    if (t < 0.15) return ss(0, 0.15, t);
    if (t > 0.82) return ss(1.0, 0.82, t);
    return 1.0;
  }

  // ── Canvas bootstrap ───────────────────────────────────────────────────────
  function ensureCanvas() {
    canvas = document.getElementById('estus-bubble-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'estus-bubble-canvas';
      canvas.setAttribute('aria-hidden', 'true');
      canvas.style.cssText =
        'position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:9997;';
      document.body.appendChild(canvas);
    }
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
    ctx = canvas.getContext('2d');
  }

  // ── Spawn ──────────────────────────────────────────────────────────────────
  function spawn() {
    ensureCanvas();

    const now = performance.now();
    const W   = canvas.width;
    const H   = canvas.height;

    const count = 40;
    for (let i = 0; i < count; i++) {
      const r = 4 + Math.pow(Math.random(), 1.6) * 24;

      const startX = W * (0.04 + Math.random() * 0.92);
      const startY = H + r;

      const travelFrac = 0.92 + Math.random() * 0.07;
      const endY       = H * (1 - travelFrac);

      const lifetime = 3500 + (r / 28) * 2000 + Math.random() * 1000;

      const baseAlpha = 0.55 + Math.random() * 0.35;

      const driftAmp   = r * (1.4 + Math.random() * 2.0);
      const driftFreq  = 0.00035 + Math.random() * 0.00045;
      const driftPhase = Math.random() * Math.PI * 2;

      const startTime = now + i * 90;

      bubbles.push({
        startX, startY, endY,
        r, baseAlpha,
        driftAmp, driftFreq, driftPhase,
        startTime, lifetime,
      });
    }

    if (!running) tick(performance.now());
  }

  // ── Render loop ────────────────────────────────────────────────────────────
  function tick(now) {
    if (!ctx) { running = false; return; }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let alive = 0;

    for (const b of bubbles) {
      const elapsed = now - b.startTime;
      if (elapsed < 0) { alive++; continue; }

      const t = elapsed / b.lifetime;
      if (t >= 1) continue;

      alive++;

      const y = b.startY + (b.endY - b.startY) * t;
      const x = b.startX + b.driftAmp * Math.sin(elapsed * b.driftFreq + b.driftPhase);

      const alpha = envelope(t) * b.baseAlpha;
      if (alpha < 0.01) continue;

      const r = b.r;

      // 1. Soft outer glow
      const glow = ctx.createRadialGradient(x, y, r * 0.5, x, y, r * 2.4);
      glow.addColorStop(0,   `rgba(0, 220, 100, ${(alpha * 0.15).toFixed(3)})`);
      glow.addColorStop(1,   `rgba(0, 220, 100, 0)`);
      ctx.beginPath();
      ctx.arc(x, y, r * 2.4, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      // 2. Bubble body — transparent centre, bright rim
      const body = ctx.createRadialGradient(x, y, 0, x, y, r);
      body.addColorStop(0.00, `rgba(0,  30,  15, ${(alpha * 0.08).toFixed(3)})`);
      body.addColorStop(0.60, `rgba(0,  80,  40, ${(alpha * 0.12).toFixed(3)})`);
      body.addColorStop(0.78, `rgba(20, 200,  90, ${(alpha * 0.55).toFixed(3)})`);
      body.addColorStop(0.88, `rgba(80, 255, 140, ${(alpha * 0.90).toFixed(3)})`);
      body.addColorStop(0.94, `rgba(40, 255, 110, ${(alpha * 0.70).toFixed(3)})`);
      body.addColorStop(1.00, `rgba(0,  180,  70, 0)`);

      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = body;
      ctx.fill();

      // 3. Specular highlight
      const hx = x - r * 0.30;
      const hy = y - r * 0.28;
      const hr = r * 0.22;
      const spec = ctx.createRadialGradient(hx, hy, 0, hx, hy, hr);
      spec.addColorStop(0,   `rgba(255, 255, 255, ${(alpha * 0.85).toFixed(3)})`);
      spec.addColorStop(0.5, `rgba(200, 255, 220, ${(alpha * 0.40).toFixed(3)})`);
      spec.addColorStop(1,   `rgba(255, 255, 255, 0)`);
      ctx.beginPath();
      ctx.arc(hx, hy, hr, 0, Math.PI * 2);
      ctx.fillStyle = spec;
      ctx.fill();
    }

    bubbles = bubbles.filter(b => {
      const e = now - b.startTime;
      return e < 0 || (e / b.lifetime) < 1;
    });

    if (alive > 0) {
      running = true;
      requestAnimationFrame(tick);
    } else {
      running = false;
      if (canvas) canvas.style.display = 'none';
    }
  }

  return { spawn };

})();

// ── Estus animation trigger ────────────────────────────────────────────────

function triggerEstusAnimation() {
  const flash = document.getElementById('healing-flash');
  if (flash) {
    flash.classList.add('active');
    setTimeout(() => flash.classList.remove('active'), 1800);
  }

  const c = document.getElementById('estus-bubble-canvas');
  if (c) c.style.display = 'block';
  EstusBubbles.spawn();
}

// ── Flurry flash ───────────────────────────────────────────────────────────

function triggerFlurryFlash() {
  const flash = document.getElementById('flurry-flash');
  if (!flash) return;
  flash.classList.add('flurry-animate');
  setTimeout(() => flash.classList.remove('flurry-animate'), 1200);
}

// ── Commit 11: Boss phase 2 transition ────────────────────────────────────
//
// Called when data-phase-change="true" is detected on htmx:afterSwap.
// Two effects:
//   1. #phase-flash red screen wash (.phase-flash-animate CSS keyframe)
//   2. .enemy-img shake (.phase-change class — keyframe in style.css §9)

function triggerPhaseTransition() {
  // 1 — full-screen red flash
  const flash = document.getElementById('phase-flash');
  if (flash) {
    flash.classList.remove('phase-flash-animate');
    void flash.offsetWidth;   // force reflow so re-adding the class restarts animation
    flash.classList.add('phase-flash-animate');
    flash.addEventListener(
      'animationend',
      () => flash.classList.remove('phase-flash-animate'),
      { once: true }
    );
  }

  // 2 — enemy image shake (img is inside #battle-state, freshly swapped in)
  const enemyImg = document.querySelector('.enemy-img');
  if (enemyImg) {
    enemyImg.classList.remove('phase-change');
    void enemyImg.offsetWidth;
    enemyImg.classList.add('phase-change');
    setTimeout(() => enemyImg.classList.remove('phase-change'), 700);
  }
}

// ── Secondary special move flash (teal) ───────────────────────────────────
//
// Mirrors triggerSpecialFlash() but targets #special2-flash with a
// teal colour scheme — visually distinct from the gold primary flash.

function triggerSpecial2Flash() {
  const flash = document.getElementById('special2-flash');
  if (!flash) return;
  flash.classList.remove('special2-flash-animate');
  void flash.offsetWidth;   // force reflow to restart animation
  flash.classList.add('special2-flash-animate');
  flash.addEventListener(
    'animationend',
    () => flash.classList.remove('special2-flash-animate'),
    { once: true }
  );
}
// Extracted into a named function so it can be called:
//   1. On initial DOMContentLoaded
//   2. After every HTMX swap (htmx:afterSwap) — new DOM nodes need new listeners

function bindBattleButtons() {
  const playerClass = document.body.dataset.class || 'knight';

  document.querySelectorAll('.battle-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();

      const action = btn.dataset.action;
      if (!action) return;

      // Stop the ATB timer immediately — player has acted
      if (window.BattleTimer) BattleTimer.stop();

      let sfxId = null;

      switch (action) {
        case 'attack':
          sfxId = 'attack-' + playerClass;
          playAttackSound(playerClass);
          break;
        case 'block':
          sfxId = 'block';
          playBlockSound();
          break;
        case 'dodge':
          sfxId = 'dodge';
          playDodgeSound();
          break;
        case 'estus':
          sfxId = 'estus';
          playEstusSound();
          triggerEstusAnimation();
          break;
        // ── Commit 20: special move SFX + gold flash ──────────────────────
        case 'special':
          playSpecialSound(playerClass);
          triggerSpecialFlash();
          // Use the special element duration if it has a real src,
          // otherwise fall back to the attack sound duration for timing.
          sfxId = (document.getElementById('special-' + playerClass)?.src &&
                   document.getElementById('special-' + playerClass).src !== window.location.href)
                   ? 'special-' + playerClass
                   : 'attack-' + playerClass;
          break;
        // ── Secondary special — teal flash, same SFX fallback ─────────────
        case 'special2':
          playSpecialSound(playerClass);   // reuse primary SFX until dedicated files added
          triggerSpecial2Flash();
          sfxId = (document.getElementById('special-' + playerClass)?.src &&
                   document.getElementById('special-' + playerClass).src !== window.location.href)
                   ? 'special-' + playerClass
                   : 'attack-' + playerClass;
          break;
        // ─────────────────────────────────────────────────────────────────
      }

      // Estus: longer delay so bubbles visibly rise before the swap.
      const submitDelay = action === 'estus' ? 1750 : (sfxId ? getSfxDelay(sfxId) : 400);

      setTimeout(() => {
        if (window.htmx) {
          htmx.ajax('POST', window.location.pathname, {
            target: '#battle-state',
            swap:   'innerHTML',
            values: { action: action },
          });
        } else {
          // Graceful fallback: native submit (no HTMX)
          const form = document.getElementById('battleForm');
          const inp  = document.createElement('input');
          inp.type   = 'hidden';
          inp.name   = 'action';
          inp.value  = action;
          form.appendChild(inp);
          form.submit();
        }
      }, submitDelay);
    });
  });

  // Re-bind play/pause — clone node to strip stacked listeners from previous calls
  ['playMusic', 'pauseMusic'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const clone = el.cloneNode(true);
    el.parentNode.replaceChild(clone, el);
  });
  AudioManager.bindControls('#playMusic', '#pauseMusic');

  // Check flurry warning on each render
  const moveHint = document.getElementById('move-hint');
  if (moveHint && moveHint.innerText.toLowerCase().includes('flurry')) {
    triggerFlurryFlash();
  }
}

// ── Main init ──────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const isBoss = document.body.dataset.boss === 'true';
  initBattleMusic(isBoss);

  bindBattleButtons();

  // ── Victory overlay — intercept before HTMX processes the redirect ────────
  // htmx:beforeOnLoad fires before HTMX reads the response.
  // We check for HX-Redirect pointing to /game, show the overlay,
  // then delay 2.8s before allowing navigation via window.location.
  let victoryPending = false;

  document.body.addEventListener('htmx:beforeOnLoad', (e) => {
    const xhr = e.detail?.xhr;
    if (!xhr) return;

    const redirect = xhr.getResponseHeader('HX-Redirect');
    if (!redirect || !redirect.includes('/game')) return;

    // Stop HTMX from processing this response at all
    e.preventDefault();

    if (victoryPending) return;
    victoryPending = true;

    // Show overlay
    const overlay = document.getElementById('victory-overlay');
    if (overlay) overlay.classList.add('victory-visible');

    // Navigate after 2.8s
    setTimeout(() => {
      victoryPending = false;
      window.location.href = redirect;
    }, 2800);
  });

  document.body.addEventListener('htmx:afterSwap', e => {
    bindBattleButtons();

    // ── Commit 11: phase transition check ─────────────────────────────────
    // Fragment wraps content in <div data-phase-change="true/false">.
    // If "true" on this swap, fire the transition and clear the attribute
    // immediately to prevent double-firing.
    const wrapper = document.querySelector('#battle-state [data-phase-change]');
    if (wrapper && wrapper.dataset.phaseChange === 'true') {
      wrapper.dataset.phaseChange = 'false';
      triggerPhaseTransition();
    }
    // ─────────────────────────────────────────────────────────────────────
  });
});