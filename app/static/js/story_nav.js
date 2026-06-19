/**
 * story_nav.js
 *
 * Delegated event handling for game.html's swappable #story-content
 * region, so it keeps working correctly across HTMX-driven in-place
 * chapter swaps (story-to-story navigation — see game_routes.py /
 * game.html) without needing to re-bind listeners on every swap.
 *
 * Why delegation: HTMX's hx-swap="innerHTML" on #story-content destroys
 * and recreates every element inside it on each transition. Listeners
 * bound directly to those elements at page-load time (the old approach,
 * fine back when every chapter was a full page reload) would silently
 * stop firing after the first swap, since the elements they were bound
 * to no longer exist. Listeners bound here, on document.body — which
 * is never replaced by the swap — keep working forever, because clicks
 * and submits from whatever currently exists inside #story-content
 * bubble up to document.body regardless of how many times that content
 * has been swapped.
 *
 * Note: #quit-link, #playMusic, and #pauseMusic do NOT need delegation
 * — they live in .menu / .audio-controls, which are siblings of
 * #story-content (persistent shell), not inside it, so their original
 * direct listeners in game.html's inline script are unaffected by any
 * of this and were left as-is.
 *
 * Depends on: AudioManager (audio_manager.js, loaded first).
 */
(function () {
  'use strict';

  // Save music position before any story-choice submission. Only
  // strictly necessary if this submission turns out to require a full
  // page reload after all (HX-Redirect to /battle, or into/out of a
  // rest chapter — see game_routes.py) — harmless no-op overhead for
  // the common case where it stays an in-place swap.
  document.body.addEventListener('submit', (e) => {
    if (e.target.closest('#story-content form')) {
      AudioManager.savePosition();
    }
  });

  // ── Secret map button / lightbox ──────────────────────────────────────
  // Fully delegated and always queried fresh at click-time (never
  // captured ahead of time), so this keeps working correctly regardless
  // of how many times #story-content gets swapped, and regardless of
  // whether the button exists at all on a given chapter.
  document.body.addEventListener('click', (e) => {
    if (e.target.closest('#secret-map-btn')) {
      const lightbox = document.getElementById('secret-map-lightbox');
      if (lightbox) {
        lightbox.classList.add('secret-map-lightbox--open');
        document.body.style.overflow = 'hidden';
      }
      return;
    }

    if (e.target.closest('#secret-map-close')) {
      const lightbox = document.getElementById('secret-map-lightbox');
      if (lightbox) {
        lightbox.classList.remove('secret-map-lightbox--open');
        document.body.style.overflow = '';
      }
      return;
    }

    // Click on the dark backdrop itself (not its inner content) closes it.
    if (e.target.id === 'secret-map-lightbox') {
      e.target.classList.remove('secret-map-lightbox--open');
      document.body.style.overflow = '';
    }
  });

  // Escape key closes the secret map lightbox, whenever it happens to be
  // open. Queried fresh each time for the same reason as above.
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const lightbox = document.getElementById('secret-map-lightbox');
    if (lightbox && lightbox.classList.contains('secret-map-lightbox--open')) {
      lightbox.classList.remove('secret-map-lightbox--open');
      document.body.style.overflow = '';
    }
  });

})();