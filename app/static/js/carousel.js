/**
 * carousel.js
 * Horizontal scroll-snap carousel for class and gift selection (index.html).
 * Initialised by title_intro.js after the stagger animation completes.
 *
 * Public API (attached to window.Carousel):
 *   Carousel.init(trackEl, dotsEl, arrowLeft, arrowRight)
 *     → returns { updateArrows, updateDots }
 *   Carousel.update(trackEl)
 *     → triggers updateArrows + updateDots on an already-initialised track
 *
 * Bug fix: right arrow disappeared too early, making the last 1-2 classes
 * unreachable unless the player clicked extremely fast.
 *
 * Root cause: getVisibleCount() in JS hardcoded "4 cards at >= 1100px" but
 * the CSS --cards-visible variable is set to 3 at that breakpoint. The JS
 * therefore hid the right arrow one scroll position before the actual last
 * card was in view. On desktop with 9 classes: JS hid at idx 5, but idx 6
 * was needed to see cards 7-9 — Samurai and Wretch were never reachable.
 *
 * Fix: read --cards-visible / --cards-visible-gift directly from the computed
 * CSS on documentElement so JS and CSS can never drift out of sync again.
 * The 80ms debounce is also lengthened to 150ms and supplemented with a
 * post-click 350ms re-check so arrow state is always correct after smooth
 * scrolling completes.
 *
 * Bug fix 2: left arrow never appeared on some mobile Safari/iOS versions,
 * even after swiping well past the first card.
 *
 * Root cause: arrow/dot state only updated via the 'scroll' event when
 * 'onscrollend' in window was false. On some iOS Safari versions, that
 * feature-detection is a false positive -- the scrollend event property
 * exists, but the event itself doesn't reliably fire for touch-driven
 * momentum scrolling, only for programmatic/mouse scrolls. Result: arrow
 * state froze at whatever it was computed at page load (idx=0 -> left
 * hidden, right shown) and never updated again on touch.
 *
 * Fix: always attach the debounced 'scroll' listener as a reliable
 * baseline, and treat scrollend as a purely additive, optional speed-up
 * where it happens to work, rather than the sole update path.
 */

(function () {

    const carouselMap = new Map();

    function getCardWidth(trackEl) {
        const first = trackEl.querySelector('.carousel-item, .carousel-item--gift');
        if (!first) return 0;
        const style = getComputedStyle(trackEl);
        const gap   = parseFloat(style.columnGap || style.gap || 0);
        return first.getBoundingClientRect().width + gap;
    }

    function currentIndex(trackEl) {
        const cardW = getCardWidth(trackEl);
        return cardW > 0 ? Math.round(trackEl.scrollLeft / cardW) : 0;
    }

    function totalCards(trackEl) {
        return trackEl.querySelectorAll('.carousel-item, .carousel-item--gift').length;
    }

    /**
     * Read the visible card count directly from the CSS custom property so
     * that JS and CSS are always in sync. Class track uses --cards-visible;
     * gift track uses --cards-visible-gift (both defined in base.css and
     * overridden in components.css media queries).
     */
    function getVisibleCount(trackEl) {
        const isGift = trackEl.classList.contains('gift-options-wrapper');
        const cssVar = isGift ? '--cards-visible-gift' : '--cards-visible';
        const raw    = getComputedStyle(document.documentElement).getPropertyValue(cssVar).trim();
        const n      = parseInt(raw, 10);
        return n > 0 ? n : 1;
    }

    function scrollToIndex(trackEl, idx) {
        const cardW = getCardWidth(trackEl);
        trackEl.scrollTo({ left: idx * cardW, behavior: 'smooth' });
    }

    function init(trackEl, dotsEl, arrowLeft, arrowRight) {

        function updateArrows() {
            const idx    = currentIndex(trackEl);
            const total  = totalCards(trackEl);
            const vCount = Math.min(getVisibleCount(trackEl), total);
            arrowLeft.classList.toggle('carousel-arrow--hidden',  idx <= 0);
            arrowRight.classList.toggle('carousel-arrow--hidden', idx >= total - vCount);
        }

        function updateDots() {
            if (!dotsEl) return;
            const idx = currentIndex(trackEl);
            dotsEl.querySelectorAll('.carousel-dot').forEach((dot, i) => {
                dot.classList.toggle('carousel-dot--active', i === idx);
            });
        }

        // Always run the debounced scroll listener as a reliable baseline —
        // scrollend has known gaps on some Safari/iOS versions where the
        // event property exists ('onscrollend' in window is true) but the
        // event doesn't actually fire for touch-driven momentum scrolling,
        // only for programmatic/mouse scrolls. Trusting that feature
        // detection exclusively meant arrow/dot state could freeze at
        // whatever it was computed at page load (idx=0 -> left arrow
        // hidden, right arrow shown) and never update again on touch,
        // which is exactly "right arrow shows, left arrow never does"
        // regardless of how far the carousel was actually swiped.
        let scrollTimer;
        trackEl.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => { updateArrows(); updateDots(); }, 150);
        }, { passive: true });

        // scrollend, where it reliably fires, gives a snappier update than
        // waiting out the 150ms debounce above — harmless to also have it,
        // since both just call the same idempotent update functions.
        if ('onscrollend' in window) {
            trackEl.addEventListener('scrollend', () => {
                updateArrows();
                updateDots();
            }, { passive: true });
        }

        function clickAndRefresh(targetIdx) {
            scrollToIndex(trackEl, targetIdx);
            // Second pass after smooth-scroll animation completes (~300ms).
            setTimeout(() => { updateArrows(); updateDots(); }, 350);
        }

        arrowLeft.addEventListener('click', () =>
            clickAndRefresh(Math.max(0, currentIndex(trackEl) - 1)));
        arrowRight.addEventListener('click', () =>
            clickAndRefresh(Math.min(totalCards(trackEl) - 1, currentIndex(trackEl) + 1)));

        // Re-evaluate on hover so state is always current when user mouses over.
        arrowLeft.addEventListener('mouseenter',  updateArrows);
        arrowRight.addEventListener('mouseenter', updateArrows);

        if (dotsEl) {
            dotsEl.querySelectorAll('.carousel-dot').forEach(dot => {
                dot.addEventListener('click', () => {
                    const idx = parseInt(dot.dataset.index, 10);
                    scrollToIndex(trackEl, idx);
                    setTimeout(() => { updateArrows(); updateDots(); }, 350);
                });
            });
        }

        updateArrows();
        updateDots();

        const ctrl = { updateArrows, updateDots };
        carouselMap.set(trackEl, ctrl);
        return ctrl;
    }

    function update(trackEl) {
        const ctrl = carouselMap.get(trackEl);
        if (ctrl) { ctrl.updateArrows(); ctrl.updateDots(); }
    }

    // Re-measure on resize (CSS variable changes with breakpoint).
    window.addEventListener('resize', () => {
        carouselMap.forEach((ctrl, trackEl) => { ctrl.updateArrows(); ctrl.updateDots(); });
    });

    // Expose public API
    window.Carousel = { init, update };

}());