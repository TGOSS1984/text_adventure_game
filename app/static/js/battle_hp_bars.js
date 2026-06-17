/**
 * battle_hp_bars.js
 *
 * Makes the player/enemy HP bar width changes visibly animate across
 * HTMX swaps.
 *
 * Why this is needed:
 * _battle_hud.html already gives .stat-bar-fill a CSS `transition: width`,
 * but it never actually fires during battle. battle_timer.js submits each
 * turn via `htmx.ajax(..., { target: '#battle-state', swap: 'innerHTML' })`,
 * which replaces the ENTIRE HUD fragment every turn. The new bar <div> is
 * a brand-new DOM node that mounts already at its final width — there is
 * no "previous width" on that node for the browser to transition from, so
 * damage just snaps instantly no matter what the CSS says. This affects
 * both the player bar and the enemy bar equally.
 *
 * Fix ("FLIP"-lite technique):
 *   1. htmx:beforeSwap — the OLD fragment is still in the DOM. Read the
 *      current rendered width of each bar and stash it.
 *   2. htmx:afterSwap  — the NEW fragment is now in the DOM, already at
 *      its target width. Snap the new node back to the stashed OLD width
 *      with transitions disabled, force a reflow, then restore the real
 *      target width with transitions re-enabled. The browser animates
 *      old -> new exactly as if one persistent node had changed width.
 *
 * Known limitation: this only animates `width`. The hp-mid/hp-low/
 * phase2 colour classes are baked into the new node already, so colour
 * changes still snap instantly (a smaller cosmetic gap, not addressed
 * here).
 *
 * Depends on: htmx (loaded in battle.html), runs alongside battle_timer.js
 * and battle_sounds.js which also listen for htmx:afterSwap.
 */
(function () {
  'use strict';

  const BAR_SELECTORS = [
    '.stat-bar-fill--player',
    '.stat-bar-fill--enemy',
  ];

  let stashedWidths = {};

  function readWidths() {
    const widths = {};
    BAR_SELECTORS.forEach((sel) => {
      const el = document.querySelector(sel);
      if (el) widths[sel] = el.style.width;
    });
    return widths;
  }

  document.body.addEventListener('htmx:beforeSwap', () => {
    stashedWidths = readWidths();
  });

  document.body.addEventListener('htmx:afterSwap', () => {
    BAR_SELECTORS.forEach((sel) => {
      const el = document.querySelector(sel);
      if (!el) return;

      const oldWidth = stashedWidths[sel];
      const newWidth = el.style.width;
      if (!oldWidth || oldWidth === newWidth) return; // nothing to animate

      // Snap to the old width with transitions off...
      el.style.transition = 'none';
      el.style.width = oldWidth;

      // ...force a reflow so the browser commits that snapped width
      // before we touch it again (otherwise both writes get batched
      // into one frame and there's nothing to animate)...
      void el.offsetWidth;

      // ...then restore transitions and set the real target width.
      // This is the change the CSS `transition: width` actually animates.
      el.style.transition = '';
      el.style.width = newWidth;
    });
  });
})();