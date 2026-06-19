/**
 * typewriter.js
 * Typewriter effect for story chapter text in game.html.
 *
 * Behaviour:
 * - Story text renders character by character at a configurable speed.
 * - A blinking cursor follows the insertion point.
 * - Choice buttons are hidden until typing completes, then fade in.
 * - Clicking anywhere on the lore-box (or pressing Space/Enter) skips
 *   to the end instantly — the full text appears and choices reveal.
 * - Respects prefers-reduced-motion: if the user has that set, text
 *   appears instantly with no animation.
 *
 * Usage: include after the DOM is populated; it queries by data attribute.
 * The story <p> element must have data-typewriter="true" and contain the
 * raw text as its textContent. The choices <form> must have id="choices-form".
 *
 * Commit 13 fix:
 * - Cursor is now appended INSIDE the <p> element rather than inserted
 *   after it as a sibling. Previously the cursor sat outside the <p> as
 *   a block-level span, making the lore-box taller while typing was active.
 *   When it was removed on finish the box shrank and the buttons jumped up.
 *   Keeping the cursor inline inside the <p> means the box height never
 *   changes and there is no layout shift.
 *
 * Commit 13 addition:
 * - CHAR_DELAY_MS reads from localStorage key 'twSpeed' if set by settings.js
 *   Values: 'slow'=45, 'normal'=22 (default), 'fast'=8, 'instant'=0
 *
 * Commit 32 change:
 * - Story-to-story navigation no longer reloads the page (see
 *   game_routes.py / game.html — HTMX swaps #story-content in place).
 *   That means init() must be safely re-runnable on every swap, not
 *   just once on DOMContentLoaded:
 *     - Any in-flight timer/interval from a previous chapter's typing
 *       is cleared at the start of every call, so two chapters' worth
 *       of typing can never run at once if a swap lands mid-animation.
 *     - The Space/Enter "skip" keydown listener is now a single
 *       persistent listener (added once) that delegates to whichever
 *       chapter is currently active, instead of adding a fresh
 *       `{ once: true }` listener on every init() call — the old
 *       approach would leak one listener per chapter for the lifetime
 *       of the page once chapters stopped triggering full reloads.
 */

(function () {

  const SPEED_MAP = {
    slow:    45,
    normal:  22,
    fast:     8,
    instant:  0,
  };

  const CURSOR_BLINK = 530;  // ms cursor blink interval

  // ── Reduced-motion: skip entirely ─────────────────────────────────────────
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Speed from settings (localStorage) or default ─────────────────────────
  function getCharDelay() {
    const saved = localStorage.getItem('twSpeed');
    return SPEED_MAP[saved] ?? SPEED_MAP.normal;
  }

  // Tracks the in-progress animation across calls so a fresh init() can
  // always cleanly cancel whatever the previous chapter left running.
  let timerId       = null;
  let blinkId       = null;
  let activeFinish  = null;  // current chapter's finish(), or null when idle

  function initTypewriter() {
    // Cancel any previous chapter's still-running animation first.
    clearTimeout(timerId);
    clearInterval(blinkId);
    activeFinish = null;

    const storyEl   = document.querySelector('[data-typewriter="true"]');
    const choicesEl = document.getElementById('choices-form');

    if (!storyEl) return;

    const fullText    = storyEl.textContent.trim();
    const charDelayMs = getCharDelay();

    // If reduced motion, instant setting, or empty text — reveal immediately
    if (prefersReduced || charDelayMs === 0 || !fullText) {
      storyEl.textContent = fullText;
      if (choicesEl) {
        choicesEl.classList.remove('choices-hidden');
        choicesEl.classList.add('choices-reveal');
      }
      return;
    }

    // Hide choices until typing finishes
    if (choicesEl) choicesEl.classList.add('choices-hidden');

    // Clear the element — we'll re-populate char by char
    storyEl.textContent = '';

    // ── Cursor: appended INSIDE <p> so it's inline with the text ─────────────
    const cursor = document.createElement('span');
    cursor.className = 'typewriter-cursor';
    cursor.setAttribute('aria-hidden', 'true');
    cursor.textContent = '|';
    storyEl.appendChild(cursor);

    let index    = 0;
    let finished = false;

    function finish() {
      if (finished) return;
      finished = true;
      activeFinish = null;

      clearTimeout(timerId);
      clearInterval(blinkId);

      // Set final text and remove cursor in one operation — no reflow gap
      storyEl.textContent = fullText;

      // Reveal choices
      if (choicesEl) {
        choicesEl.classList.remove('choices-hidden');
        choicesEl.classList.add('choices-reveal');
      }
    }

    activeFinish = finish;

    function typeNext() {
      if (index >= fullText.length) {
        finish();
        return;
      }
      index++;
      // Build: text node + cursor span, all inside the <p>
      // Using textContent on the <p> would wipe the cursor span,
      // so we manage child nodes directly.
      storyEl.textContent = fullText.slice(0, index);
      storyEl.appendChild(cursor);
      timerId = setTimeout(typeNext, charDelayMs);
    }

    // Start typing
    typeNext();

    // Cursor blink
    let cursorVisible = true;
    blinkId = setInterval(() => {
      cursorVisible = !cursorVisible;
      cursor.style.opacity = cursorVisible ? '1' : '0';
    }, CURSOR_BLINK);

    // Skip on click anywhere in lore-box. This listener dies along with
    // the lore-box element itself on the next swap (or full reload), so
    // it never needs manual cleanup — only one is ever live at a time.
    const loreBox = storyEl.closest('.lore-box');
    if (loreBox) {
      loreBox.style.cursor = 'pointer';
      loreBox.addEventListener('click', finish, { once: true });
    }
  }

  // Single persistent Space/Enter listener, added once. Delegates to
  // whichever chapter's finish() is currently active (or no-ops if
  // typing has already finished / hasn't started).
  document.addEventListener('keydown', (e) => {
    if ((e.code === 'Space' || e.code === 'Enter') && activeFinish) {
      e.preventDefault();
      activeFinish();
    }
  });

  document.addEventListener('DOMContentLoaded', initTypewriter);

  // Re-run on every HTMX swap of #story-content (story-to-story
  // navigation) — without this, chapter 2 onward would show fully
  // revealed text instantly with no typewriter effect, since
  // DOMContentLoaded only fires once for the whole page now.
  document.body.addEventListener('htmx:afterSwap', (evt) => {
    if (evt.detail && evt.detail.target && evt.detail.target.id === 'story-content') {
      initTypewriter();
    }
  });

})();