/**
 * carousel.js
 * Horizontal scroll-snap carousel for class and gift selection (index.html).
 * Initialised by title_intro.js after the stagger animation completes.
 *
 * Public API (attached to window.Carousel):
 *   Carousel.init(trackEl, dotsEl, arrowLeft, arrowRight, visibleCount)
 *     → returns { updateArrows, updateDots }
 *   Carousel.update(trackEl)
 *     → triggers updateArrows + updateDots on an already-initialised track
 */

(function () {

    const carouselMap = new Map();

    function getCardWidth(trackEl) {
        const first = trackEl.querySelector('.carousel-item, .carousel-item--gift');
        if (!first) return 0;
        const style = getComputedStyle(trackEl);
        const gap = parseFloat(style.columnGap || style.gap || 0);
        return first.getBoundingClientRect().width + gap;
    }

    function currentIndex(trackEl) {
        const cardW = getCardWidth(trackEl);
        return cardW > 0 ? Math.round(trackEl.scrollLeft / cardW) : 0;
    }

    function totalCards(trackEl) {
        return trackEl.querySelectorAll('.carousel-item, .carousel-item--gift').length;
    }

    function getVisibleCount() {
        const vw = window.innerWidth;
        if (vw >= 1100) return 4;
        if (vw >= 700)  return 2;
        return 1;
    }

    function scrollToIndex(trackEl, idx) {
        const cardW = getCardWidth(trackEl);
        trackEl.scrollTo({ left: idx * cardW, behavior: 'smooth' });
    }

    function init(trackEl, dotsEl, arrowLeft, arrowRight) {

        function updateArrows() {
            const idx    = currentIndex(trackEl);
            const total  = totalCards(trackEl);
            const vCount = Math.min(getVisibleCount(), total);
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

        arrowLeft.addEventListener('click',  () => scrollToIndex(trackEl, Math.max(0, currentIndex(trackEl) - 1)));
        arrowRight.addEventListener('click', () => scrollToIndex(trackEl, Math.min(totalCards(trackEl) - 1, currentIndex(trackEl) + 1)));

        if (dotsEl) {
            dotsEl.querySelectorAll('.carousel-dot').forEach(dot => {
                dot.addEventListener('click', () => scrollToIndex(trackEl, parseInt(dot.dataset.index, 10)));
            });
        }

        let scrollTimer;
        trackEl.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => { updateArrows(); updateDots(); }, 80);
        }, { passive: true });

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

    // Re-measure on resize
    window.addEventListener('resize', () => {
        carouselMap.forEach(ctrl => { ctrl.updateArrows(); ctrl.updateDots(); });
    });

    // Expose public API
    window.Carousel = { init, update };

}());