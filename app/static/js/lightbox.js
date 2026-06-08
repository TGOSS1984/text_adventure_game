/**
 * lightbox.js
 * Shared lightbox for status.html and bestiary.html.
 * Wire up any <img data-lightbox> element to open full-size on click.
 * Called after DOMContentLoaded so dynamically revealed <details> images
 * are also caught when the user expands a codex entry.
 */

(function () {
    const box   = document.getElementById('lightbox');
    const img   = document.getElementById('lightbox-img');
    const cap   = document.getElementById('lightbox-caption');
    const close = document.getElementById('lightbox-close');

    if (!box) return; // page doesn't have a lightbox — bail silently

    function openLightbox(src, alt) {
        img.src = src;
        img.alt = alt;
        cap.textContent = alt;
        box.classList.add('lightbox--open');
        document.body.style.overflow = 'hidden';
        close.focus();
    }

    function closeLightbox() {
        box.classList.remove('lightbox--open');
        document.body.style.overflow = '';
        img.src = '';
    }

    box.addEventListener('click', e => { if (e.target === box) closeLightbox(); });
    close.addEventListener('click', closeLightbox);
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && box.classList.contains('lightbox--open')) closeLightbox();
    });

    function wireImages() {
        document.querySelectorAll('[data-lightbox]').forEach(el => {
            if (el.dataset.lightboxWired) return; // avoid double-binding
            el.dataset.lightboxWired = 'true';
            el.setAttribute('tabindex', '0');
            el.setAttribute('role', 'button');
            el.setAttribute('aria-label', 'View full size: ' + (el.alt || ''));
            el.addEventListener('click', () => openLightbox(el.src, el.alt || ''));
            el.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openLightbox(el.src, el.alt || '');
                }
            });
        });
    }

    // Initial wire-up
    document.addEventListener('DOMContentLoaded', wireImages);

    // Re-wire when <details> elements are toggled (bestiary codex entries)
    document.addEventListener('toggle', wireImages, true);
}());