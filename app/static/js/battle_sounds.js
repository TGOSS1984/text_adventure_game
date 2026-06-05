/**
 * battle_sounds.js
 * SFX, background music, and battle visual effects for battle.html.
 * Depends on: audio_manager.js (must be loaded first)
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

function playAttackSound(cls) { AudioManager.playSfx('attack-' + cls); }
function playBlockSound()     { AudioManager.playSfx('block'); }
function playDodgeSound()     { AudioManager.playSfx('dodge'); }
function playEstusSound()     { AudioManager.playSfx('estus'); }

function getSfxDelay(id) {
  const el  = document.getElementById(id);
  const dur = el && isFinite(el.duration) ? el.duration : 0;
  return dur ? Math.min(Math.round(dur * 1000) + 150, 3200) : 800;
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
  // Fade in over first 15% of lifetime, hold, fade out over last 30%.
  // Each bubble also has a baseAlpha baked in at spawn for variety.
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

    // 25 bubbles total — wide size range, nothing huge
    // Sizes: 4px–28px radius
    const count = 40;
    for (let i = 0; i < count; i++) {
      // Bias toward smaller bubbles — feels more natural
      const r = 4 + Math.pow(Math.random(), 1.6) * 24;  // 4–28px, skewed small

      // Each bubble starts anywhere along the full bottom edge
      const startX = W * (0.04 + Math.random() * 0.92);
      const startY = H + r;                               // just below visible area

      // Travel: each bubble rises 85–97% of screen height
      // This guarantees they reach near the top before fading
      const travelFrac = 0.92 + Math.random() * 0.07;
      const endY       = H * (1 - travelFrac);           // absolute Y near top

      // Lifetime drives perceived speed: longer = slower
      // Larger bubbles rise slightly slower (heavier feel)
      const lifetime = 7000 + (r / 28) * 4000 + Math.random() * 2000; // 7–13s

      // Per-bubble base transparency — varies 0.55–0.90 for visual variety
      const baseAlpha = 0.55 + Math.random() * 0.35;

      // Horizontal drift
      const driftAmp  = r * (1.4 + Math.random() * 2.0); // scales with size
      const driftFreq = 0.00035 + Math.random() * 0.00045; // slow, dreamy
      const driftPhase = Math.random() * Math.PI * 2;

      // Stagger spawn so bubbles emerge as a wave, not all at once
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
      if (elapsed < 0) { alive++; continue; }     // not yet spawned

      const t = elapsed / b.lifetime;
      if (t >= 1) continue;                        // expired

      alive++;

      // ── Position ───────────────────────────────────────────────────────────
      // LINEAR rise — constant speed, no easing on Y
      // This ensures the bubble is always moving at the same pace and
      // actually reaches the top rather than slowing to a crawl
      const y = b.startY + (b.endY - b.startY) * t;

      // True sinusoidal drift — no direction-reversal artefacts
      const x = b.startX + b.driftAmp * Math.sin(elapsed * b.driftFreq + b.driftPhase);

      // ── Opacity ────────────────────────────────────────────────────────────
      const alpha = envelope(t) * b.baseAlpha;
      if (alpha < 0.01) continue;

      const r = b.r;

      // ── Soap bubble gradient ───────────────────────────────────────────────
      // Real soap bubble: near-transparent dark centre + bright glowing rim
      // We use two gradients layered:
      //   1. Outer glow  — large soft green halo behind the bubble
      //   2. Bubble body — transparent centre, opaque green ring at edge

      // 1. Soft outer glow (larger radius, very faint)
      const glow = ctx.createRadialGradient(x, y, r * 0.5, x, y, r * 2.4);
      glow.addColorStop(0,   `rgba(0, 220, 100, ${(alpha * 0.15).toFixed(3)})`);
      glow.addColorStop(1,   `rgba(0, 220, 100, 0)`);
      ctx.beginPath();
      ctx.arc(x, y, r * 2.4, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      // 2. Bubble body — transparent centre, bright rim
      // Gradient goes from centre outward:
      //   centre (0.0): fully transparent dark
      //   inner edge (0.6): still mostly transparent
      //   rim (0.82): full bright green
      //   outer edge (1.0): fades back to transparent (thin rim, not a filled disc)
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

      // 3. Specular highlight — small bright white spot, offset top-left
      //    Makes the bubble look like a 3D sphere catching light
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

    // Prune expired bubbles
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
  // Green screen pulse — stays active for the full bubble animation duration (3500ms)
  // so the overlay fades out in sync with the bubbles disappearing
  const flash = document.getElementById('healing-flash');
  if (flash) {
    flash.classList.add('active');
    // Remove class after animation completes so it resets cleanly for next use
    setTimeout(() => flash.classList.remove('active'), 3600);
  }

  // Show canvas and spawn bubbles
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

// ── Main init ──────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const playerClass = document.body.dataset.class || 'knight';
  const isBoss      = document.body.dataset.boss === 'true';

  initBattleMusic(isBoss);

  const buttons = document.querySelectorAll('.battle-btn');
  const form    = document.getElementById('battleForm');

  buttons.forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const action = btn.value;
      let sfxId = null;

      switch (action) {
        case 'attack': sfxId = 'attack-' + playerClass; playAttackSound(playerClass); break;
        case 'block':  sfxId = 'block';  playBlockSound();  break;
        case 'dodge':  sfxId = 'dodge';  playDodgeSound();  break;
        case 'estus':
          sfxId = 'estus';
          playEstusSound();
          triggerEstusAnimation();
          break;
      }

      AudioManager.savePosition();

      // Estus: longer delay so bubbles visibly rise before page reloads.
      // All other actions use SFX duration.
      const submitDelay = action === 'estus' ? 3500 : (sfxId ? getSfxDelay(sfxId) : 400);

      setTimeout(() => {
        const inp   = document.createElement('input');
        inp.type    = 'hidden';
        inp.name    = 'action';
        inp.value   = action;
        form.appendChild(inp);
        form.submit();
      }, submitDelay);
    });
  });

  const moveHint = document.getElementById('move-hint');
  if (moveHint && moveHint.innerText.toLowerCase().includes('flurry')) {
    triggerFlurryFlash();
  }
});
