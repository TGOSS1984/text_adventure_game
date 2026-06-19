/**
 * battle_lore.js
 * Keeps the enemy lore <details> disclosure's default open/closed state
 * in sync with screen size.
 *
 * The server always renders it with the `open` attribute present (see
 * _battle_hud.html) -- that's the desktop default, unchanged from
 * before. On mobile it should default to closed instead, to save
 * vertical space (see Commit 38) -- but it's still a normal <details>
 * either way, so tapping "Lore" still works exactly the same on both.
 *
 * _battle_hud.html's macro is re-rendered fresh on every turn (HTMX
 * swaps #battle-state's innerHTML each time), always with `open`
 * present -- so this has to re-apply on every htmx:afterSwap, not just
 * on initial page load, or it would only take effect once and reset to
 * open again on the very next turn.
 */
(function () {

  const MOBILE_QUERY = '(max-width: 768px)';

  function applyMobileDefault() {
    if (!window.matchMedia(MOBILE_QUERY).matches) return;  // desktop: leave as rendered (open)

    document.querySelectorAll('.enemy-lore-details[open]').forEach(el => {
      el.open = false;
    });
  }

  document.addEventListener('DOMContentLoaded', applyMobileDefault);
  document.body.addEventListener('htmx:afterSwap', applyMobileDefault);

})();