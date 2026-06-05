/**
 * ember_particles.js
 * Lightweight canvas-based floating ember particles for the title screen (index.html).
 *
 * Renders a fixed-position canvas behind all content.
 * Particles drift upward with gentle horizontal wobble, fading out near the top.
 * Designed to complement the bonfire / Dark Souls aesthetic.
 *
 * Performance: uses requestAnimationFrame, caps at 55 particles,
 * pauses when the tab is hidden (Page Visibility API).
 * Respects prefers-reduced-motion — does nothing if set.
 */

(function () {

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const MAX_PARTICLES = 55;
  const COLOURS = [
    'rgba(255, 160,  40, ',   // warm orange
    'rgba(255, 110,  20, ',   // deep ember
    'rgba(255, 200,  80, ',   // gold
    'rgba(220,  70,  10, ',   // red-ember
  ];

  // ── Canvas setup ───────────────────────────────────────────────────────────

  const canvas = document.createElement('canvas');
  canvas.id    = 'ember-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.cssText = [
    'position:fixed',
    'top:0', 'left:0',
    'width:100vw', 'height:100vh',
    'pointer-events:none',
    'z-index:0',           // above the video (-1) but below content (1+)
  ].join(';');

  document.body.insertBefore(canvas, document.body.firstChild);

  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // ── Particle factory ────────────────────────────────────────────────────────

  function makeParticle() {
    return {
      x:       Math.random() * canvas.width,
      y:       canvas.height + Math.random() * 60,
      radius:  Math.random() * 2.2 + 0.6,       // 0.6 – 2.8 px
      speed:   Math.random() * 0.7 + 0.3,       // 0.3 – 1.0 px/frame
      wobble:  Math.random() * Math.PI * 2,     // phase offset for horizontal drift
      wobbleSpeed: Math.random() * 0.02 + 0.008,
      wobbleAmp:   Math.random() * 1.2 + 0.3,
      colour:  COLOURS[Math.floor(Math.random() * COLOURS.length)],
      opacity: Math.random() * 0.5 + 0.4,       // 0.4 – 0.9
    };
  }

  const particles = Array.from({ length: MAX_PARTICLES }, makeParticle);
  // Scatter initial y positions so screen doesn't fill from bottom all at once
  particles.forEach(p => { p.y = Math.random() * canvas.height; });

  // ── Animation loop ──────────────────────────────────────────────────────────

  let paused = false;
  document.addEventListener('visibilitychange', () => {
    paused = document.hidden;
  });

  function tick() {
    requestAnimationFrame(tick);
    if (paused) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const p of particles) {
      // Move upward
      p.y      -= p.speed;
      p.wobble += p.wobbleSpeed;
      const x   = p.x + Math.sin(p.wobble) * p.wobbleAmp;

      // Fade out in the top 30% of the canvas
      const fadeStart = canvas.height * 0.30;
      const alpha = p.y < fadeStart
        ? p.opacity * (p.y / fadeStart)
        : p.opacity;

      // Draw glow + core
      const grd = ctx.createRadialGradient(x, p.y, 0, x, p.y, p.radius * 2.5);
      grd.addColorStop(0,   p.colour + Math.min(alpha, 1) + ')');
      grd.addColorStop(0.5, p.colour + (alpha * 0.5) + ')');
      grd.addColorStop(1,   p.colour + '0)');

      ctx.beginPath();
      ctx.arc(x, p.y, p.radius * 2.5, 0, Math.PI * 2);
      ctx.fillStyle = grd;
      ctx.fill();

      // Recycle particle when it leaves the top
      if (p.y < -10) {
        Object.assign(p, makeParticle());
      }
    }
  }

  tick();

})();