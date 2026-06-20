/**
 * title_intro.js  —  Commit 17: Cinematic title screen intro
 * Elden Souls
 *
 * First load  : full cinematic sequence with letterbox bars, staggered reveals.
 * Return load : compressed ~400 ms snap-in (no letterbox, fast opacity).
 * After death : sessionStorage flag 'elden_fast' triggers the fast path too.
 *
 * Dependencies: expects audio_manager.js already loaded (window.AudioManager
 * optional — gracefully skips music if absent).
 *
 * Sequence (first load):
 *   0 ms   — page starts invisible, letterbox bars in place
 *  200 ms  — video overlay fades in (darkens the background video)
 *  600 ms  — letterbox bars retract (1 s ease)
 * 1400 ms  — h1 title fades + rises in (800 ms)
 * 2400 ms  — music soft-starts (if AudioManager present)
 * 2600 ms  — class cards stagger in (150 ms apart)
 * ~3200 ms — audio controls + bestiary link fade in
 * ~3400 ms — sequence complete, gift-panel JS unlocked
 */

(function () {
  'use strict';

  /* ─── Timing constants (ms) — tweak here ─────────────────────────────── */
  const T = {
    videoFade    : 200,
    barsRetract  : 600,
    titleReveal  : 1400,
    musicStart   : 2400,
    cardsStart   : 2600,
    cardStagger  : 150,
    footerReveal : 3200,
    fastDuration : 400,
  };

  const isFast = (
    sessionStorage.getItem('elden_visited') === '1' ||
    sessionStorage.getItem('elden_fast')    === '1'
  );

  /* ─── Utility ─────────────────────────────────────────────────────────── */
  function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function qs(sel)  { return document.querySelector(sel); }
  function qsa(sel) { return Array.from(document.querySelectorAll(sel)); }

  /* ─── Elements ────────────────────────────────────────────────────────── */
  const title       = qs('h1.title-animate');
  const classCards  = qsa('.class-option');
  const audioCtrl   = qs('.audio-controls');
  const bestiaryWrap = qs('.menu');          // div wrapping bestiary link
  const video        = qs('#bg-video');
  const overlay      = qs('.overlay');

  /* ─── Letterbox bar creation ──────────────────────────────────────────── */
  function createLetterboxBars() {
    const shared = `
      position:fixed;
      left:0;
      width:100%;
      height:80px;
      background:#000;
      z-index:999;
      transition:transform 1s cubic-bezier(0.76,0,0.24,1);
      pointer-events:none;
    `;
    const top = document.createElement('div');
    top.id = 'lb-top';
    top.setAttribute('aria-hidden', 'true');
    top.style.cssText = shared + 'top:0; transform:translateY(0);';

    const bot = document.createElement('div');
    bot.id = 'lb-bot';
    bot.setAttribute('aria-hidden', 'true');
    bot.style.cssText = shared + 'bottom:0; transform:translateY(0);';

    document.body.appendChild(top);
    document.body.appendChild(bot);
    return { top, bot };
  }

  /* ─── Hide everything before reveal ──────────────────────────────────── */
  function hideAll() {
    [title, audioCtrl, bestiaryWrap].forEach(el => {
      if (!el) return;
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(18px)';
      el.style.transition = 'none';
    });

    classCards.forEach(card => {
      card.style.opacity   = '0';
      card.style.transform = 'translateY(24px)';
      card.style.transition = 'none';
    });

    if (video)   { video.style.opacity   = '0'; video.style.transition = 'none'; }
    if (overlay) { overlay.style.opacity = '0'; overlay.style.transition = 'none'; }
  }

  /* ─── Reveal helper ───────────────────────────────────────────────────── */
  function reveal(el, dur = 700, delay_ms = 0) {
    if (!el) return;
    setTimeout(() => {
      el.style.transition = `opacity ${dur}ms ease, transform ${dur}ms ease`;
      el.style.opacity    = '1';
      el.style.transform  = 'translateY(0)';
    }, delay_ms);
  }

  /* ─── Attempt to start ambient music ─────────────────────────────────── */
  function tryStartMusic() {
    if (window.AudioManager && typeof window.AudioManager.play === 'function') {
      window.AudioManager.play();
    } else if (window.startCharSelectMusic) {
      window.startCharSelectMusic();
    }
  }

  /* ══════════════════════════════════════════════════════════════════════ */
  /*  FAST PATH — return visit / post-death                                 */
  /* ══════════════════════════════════════════════════════════════════════ */
  async function runFast() {
    hideAll();
    await delay(60); // let layout settle

    const dur = T.fastDuration;
    if (video)   { video.style.transition   = `opacity ${dur}ms ease`; video.style.opacity   = '1'; }
    if (overlay) { overlay.style.transition = `opacity ${dur}ms ease`; overlay.style.opacity = '1'; }

    [title, audioCtrl, bestiaryWrap].forEach(el => reveal(el, dur, 40));
    classCards.forEach((card, i) => reveal(card, dur, i * 40));

    sessionStorage.setItem('elden_visited', '1');
    sessionStorage.removeItem('elden_fast');
  }

  /* ══════════════════════════════════════════════════════════════════════ */
  /*  CINEMATIC PATH — first ever load                                      */
  /* ══════════════════════════════════════════════════════════════════════ */
  async function runCinematic() {
    hideAll();

    const bars = createLetterboxBars();

    await delay(80); // first paint

    /* Step 1 — video & overlay fade in */
    if (video) {
      video.style.transition = `opacity 900ms ease`;
      video.style.opacity    = '1';
    }
    if (overlay) {
      overlay.style.transition = `opacity 900ms ease`;
      overlay.style.opacity    = '1';
    }

    await delay(T.barsRetract);

    /* Step 2 — letterbox bars retract */
    bars.top.style.transform = 'translateY(-100%)';
    bars.bot.style.transform = 'translateY(100%)';

    await delay(T.titleReveal - T.barsRetract);

    /* Step 3 — title rises in */
    if (title) {
      title.style.transition = 'opacity 900ms ease, transform 900ms cubic-bezier(0.16,1,0.3,1)';
      title.style.opacity    = '1';
      title.style.transform  = 'translateY(0)';
    }

    await delay(T.musicStart - T.titleReveal);

    /* Step 4 — music */
    tryStartMusic();

    await delay(T.cardsStart - T.musicStart);

    /* Step 5 — class cards stagger in */
    classCards.forEach((card, i) => {
      setTimeout(() => {
        card.style.transition = 'opacity 600ms ease, transform 600ms cubic-bezier(0.16,1,0.3,1)';
        card.style.opacity    = '1';
        card.style.transform  = 'translateY(0)';
      }, i * T.cardStagger);
    });

    const afterCards = classCards.length * T.cardStagger + 600;
    await delay(afterCards);

    /* Step 6 — footer controls fade in */
    [audioCtrl, bestiaryWrap].forEach(el => reveal(el, 500, 0));

    /* Step 7 — clean up bars from DOM after transition finishes */
    await delay(500);
    bars.top.remove();
    bars.bot.remove();

    sessionStorage.setItem('elden_visited', '1');
  }

  /* ─── Boot ────────────────────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  function boot() {
    if (isFast) {
      runFast();
    } else {
      runCinematic();
    }
  }

})();