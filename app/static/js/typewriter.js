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
 */

(function () {

  const CHAR_DELAY_MS  = 22;   // ms per character (~45 chars/sec — readable but brisk)
  const CURSOR_BLINK   = 530;  // ms cursor blink interval

  // ── Reduced-motion: skip entirely ─────────────────────────────────────────

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Main init ─────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', () => {
    const storyEl   = document.querySelector('[data-typewriter="true"]');
    const choicesEl = document.getElementById('choices-form');

    if (!storyEl) return;

    const fullText = storyEl.textContent.trim();

    // If reduced motion or text is empty, reveal everything immediately
    if (prefersReduced || !fullText) {
      if (choicesEl) choicesEl.classList.remove('choices-hidden');
      return;
    }

    // Hide choices until typing finishes
    if (choicesEl) choicesEl.classList.add('choices-hidden');

    // Clear the element and start typing
    storyEl.textContent = '';

    // Cursor element
    const cursor = document.createElement('span');
    cursor.className = 'typewriter-cursor';
    cursor.setAttribute('aria-hidden', 'true');
    cursor.textContent = '|';
    storyEl.after(cursor);

    let index     = 0;
    let finished  = false;
    let timerId   = null;
    let blinkId   = null;

    function finish() {
      if (finished) return;
      finished = true;

      clearTimeout(timerId);
      storyEl.textContent = fullText;

      // Remove cursor after a brief pause
      setTimeout(() => {
        cursor.remove();
        clearInterval(blinkId);
      }, 800);

      // Reveal choices
      if (choicesEl) {
        choicesEl.classList.remove('choices-hidden');
        choicesEl.classList.add('choices-reveal');
      }
    }

    function typeNext() {
      if (index >= fullText.length) {
        finish();
        return;
      }
      storyEl.textContent = fullText.slice(0, ++index);
      // Move cursor after the text node
      storyEl.after(cursor);
      timerId = setTimeout(typeNext, CHAR_DELAY_MS);
    }

    // Start
    typeNext();

    // Cursor blink
    let cursorVisible = true;
    blinkId = setInterval(() => {
      cursorVisible = !cursorVisible;
      cursor.style.opacity = cursorVisible ? '1' : '0';
    }, CURSOR_BLINK);

    // Skip on click anywhere in lore-box, or Space / Enter
    const loreBox = storyEl.closest('.lore-box');
    if (loreBox) {
      loreBox.style.cursor = 'pointer';
      loreBox.addEventListener('click', finish, { once: true });
    }

    document.addEventListener('keydown', (e) => {
      if ((e.code === 'Space' || e.code === 'Enter') && !finished) {
        e.preventDefault();
        finish();
      }
    }, { once: true });
  });

})();