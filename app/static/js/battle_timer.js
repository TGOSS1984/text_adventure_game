/**
 * battle_timer.js
 * ATB-style countdown bar for the battle screen.
 *
 * Depends on: battle_sounds.js (for bindBattleButtons re-init pattern),
 *             audio_manager.js, htmx
 *
 * Design:
 * - A slim bar beneath the action buttons depletes left-to-right
 * - Three visual phases driven by CSS classes:
 *     >40%  : amber  (.timer-phase--normal)
 *     15–40%: orange (.timer-phase--warning)
 *     <15%  : red    (.timer-phase--danger) + rapid pulse + edge vignette
 * - On expiry: auto-submits action=timeout via HTMX (same path as a
 *   normal button press). Server treats timeout as a penalty hit.
 * - Timer resets after every HTMX swap (htmx:afterSwap event).
 * - Paused while the page is hidden (Page Visibility API).
 * - Respects prefers-reduced-motion — instant timeout, no animation.
 * - Special moves (Commit 7) can pass a charge delay to delaySubmit()
 *   which extends the visual pause before the HTMX POST fires.
 */

const BattleTimer = (() => {

  // ── Config ─────────────────────────────────────────────────────────────────
  const TURN_DURATION_MS   = 12000;  // 12 seconds per turn
  const TICK_MS            = 50;     // update interval — smooth enough, not wasteful
  const WARNING_THRESHOLD  = 0.40;   // switch to orange below 40%
  const DANGER_THRESHOLD   = 0.15;   // switch to red below 15%

  // ── State ──────────────────────────────────────────────────────────────────
  let startTime   = null;
  let tickerId    = null;
  let paused      = false;
  let pausedAt    = null;   // timestamp when tab was hidden
  let active      = false;  // false while an action is pending (no double-submit)

  // ── DOM refs (set on each init) ────────────────────────────────────────────
  let barFill     = null;
  let barEl       = null;
  let vignette    = null;

  // ── Reduced-motion check ───────────────────────────────────────────────────
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Core tick ──────────────────────────────────────────────────────────────
  function tick() {
    if (!active || paused || !barFill) return;

    const elapsed  = performance.now() - startTime;
    const fraction = Math.max(0, 1 - elapsed / TURN_DURATION_MS);

    // Update bar width
    barFill.style.width = (fraction * 100) + '%';

    // Phase classes
    barFill.classList.remove('timer-phase--normal', 'timer-phase--warning', 'timer-phase--danger');
    if (fraction > WARNING_THRESHOLD) {
      barFill.classList.add('timer-phase--normal');
    } else if (fraction > DANGER_THRESHOLD) {
      barFill.classList.add('timer-phase--warning');
    } else {
      barFill.classList.add('timer-phase--danger');
      // Activate edge vignette in danger zone
      if (vignette) vignette.classList.add('timer-vignette--active');
    }

    if (fraction <= 0) {
      expire();
    }
  }

  // ── Expiry ─────────────────────────────────────────────────────────────────
  function expire() {
    stop();
    // Submit timeout action — server applies penalty hit (unblocked enemy attack)
    if (window.htmx) {
      htmx.ajax('POST', window.location.pathname, {
        target: '#battle-state',
        swap:   'innerHTML',
        values: { action: 'timeout' },
      });
    } else {
      // Fallback
      const form = document.getElementById('battleForm');
      if (form) {
        const inp  = document.createElement('input');
        inp.type   = 'hidden';
        inp.name   = 'action';
        inp.value  = 'timeout';
        form.appendChild(inp);
        form.submit();
      }
    }
  }

  // ── Public: start ──────────────────────────────────────────────────────────
  function start() {
    // Grab DOM refs fresh each call (fragment may have been swapped)
    barFill  = document.getElementById('timer-bar-fill');
    barEl    = document.getElementById('timer-bar');
    vignette = document.getElementById('timer-vignette');

    if (!barFill) return;   // timer elements not in DOM — do nothing

    if (reducedMotion) {
      // No visual countdown — just set a plain timeout at full duration
      tickerId = setTimeout(expire, TURN_DURATION_MS);
      return;
    }

    startTime = performance.now();
    active    = true;

    // Reset visual state
    barFill.style.width = '100%';
    barFill.classList.remove('timer-phase--warning', 'timer-phase--danger');
    barFill.classList.add('timer-phase--normal');
    if (vignette) vignette.classList.remove('timer-vignette--active');

    clearInterval(tickerId);
    tickerId = setInterval(tick, TICK_MS);
  }

  // ── Public: stop (called by battle_sounds.js when player acts) ─────────────
  function stop() {
    active = false;
    clearInterval(tickerId);
    clearTimeout(tickerId);
    tickerId = null;
    if (vignette) vignette.classList.remove('timer-vignette--active');
    // Snap bar to empty so it doesn't flicker on the next swap
    if (barFill) barFill.style.width = '0%';
  }

  // ── Page visibility: pause/resume ─────────────────────────────────────────
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      paused   = true;
      pausedAt = performance.now();
    } else {
      if (paused && pausedAt !== null) {
        // Shift startTime forward by the time we were hidden
        startTime += (performance.now() - pausedAt);
      }
      paused   = false;
      pausedAt = null;
    }
  });

  return { start, stop };

})();

// ── Integration with battle flow ───────────────────────────────────────────
//
// battle_sounds.js calls BattleTimer.stop() when a button is clicked
// (before the HTMX delay), then BattleTimer.start() is called via
// htmx:afterSwap once the new fragment is in the DOM.
//
// We hook into htmx:afterSwap here so the timer module is self-contained.

document.addEventListener('DOMContentLoaded', () => {
  // Start timer on initial page load
  BattleTimer.start();

  // Restart after every HTMX swap (new turn)
  document.body.addEventListener('htmx:afterSwap', () => {
    BattleTimer.start();
  });
});