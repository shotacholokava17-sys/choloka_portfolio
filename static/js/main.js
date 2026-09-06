// ================================================================
// SHOTA CHOLOKAVA PORTFOLIO – main.js v3
// ================================================================

document.addEventListener('DOMContentLoaded', () => {

    // ─────────────────────────────────────────────
    // 1. DARK / LIGHT THEME TOGGLE
    // ─────────────────────────────────────────────
    const html       = document.documentElement;
    const toggleBtn  = document.getElementById('themeToggleBtn');
    const iconMoon   = document.getElementById('icon-moon');
    const iconSun    = document.getElementById('icon-sun');

    function applyTheme(theme) {
        if (theme === 'light') {
            html.classList.remove('dark');
            html.classList.add('light');
            if (iconMoon) iconMoon.style.display = 'none';
            if (iconSun)  iconSun.style.display  = '';
        } else {
            html.classList.remove('light');
            html.classList.add('dark');
            if (iconMoon) iconMoon.style.display = '';
            if (iconSun)  iconSun.style.display  = 'none';
        }
    }

    // Apply saved theme on load
    const savedTheme = localStorage.getItem('portfolio-theme') || 'dark';
    applyTheme(savedTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const isDark = html.classList.contains('dark');
            const newTheme = isDark ? 'light' : 'dark';
            localStorage.setItem('portfolio-theme', newTheme);
            applyTheme(newTheme);
        });
    }

    // ─────────────────────────────────────────────
    // 2. PORTFOLIO FILTER & SEARCH
    // ─────────────────────────────────────────────
    const filterButtons  = document.querySelectorAll('.filter-btn');
    const activityCards  = document.querySelectorAll('.activity-card');
    const searchInput    = document.getElementById('searchInput');

    let activeCategory = 'all';
    let searchQuery    = '';

    function filterCards() {
        let visibleCount = 0;
        activityCards.forEach(card => {
            const cat   = card.getAttribute('data-category') || '';
            const title = (card.getAttribute('data-title') || '').toLowerCase();
            const desc  = (card.getAttribute('data-desc')  || '').toLowerCase();
            const matchCat    = activeCategory === 'all' || cat === activeCategory;
            const matchSearch = !searchQuery || title.includes(searchQuery) || desc.includes(searchQuery);
            if (matchCat && matchSearch) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        const emptyMsg = document.getElementById('emptyState');
        if (emptyMsg) emptyMsg.style.display = visibleCount === 0 ? '' : 'none';
    }

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeCategory = btn.getAttribute('data-filter') || 'all';
            filterCards();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', e => {
            searchQuery = e.target.value.toLowerCase().trim();
            filterCards();
        });
    }

    // ─────────────────────────────────────────────
    // 3. LIGHTBOX
    // ─────────────────────────────────────────────
    const modal       = document.getElementById('lightboxModal');
    const lbImage     = document.getElementById('lightboxImage');
    const lbCaption   = document.getElementById('lightboxCaption');
    const btnClose    = document.getElementById('closeLightbox');
    const btnPrev     = document.getElementById('prevLightbox');
    const btnNext     = document.getElementById('nextLightbox');

    const thumbs = Array.from(document.querySelectorAll('.gallery-thumb'));
    let currentIdx = 0;
    const sources = thumbs.map(t => ({
        src:     t.getAttribute('data-src') || '',
        caption: t.getAttribute('data-caption') || ''
    }));

    function openLightbox(idx) {
        if (!modal || sources.length === 0) return;
        currentIdx = (idx + sources.length) % sources.length;
        lbImage.src = sources[currentIdx].src;
        if (lbCaption) lbCaption.textContent = sources[currentIdx].caption;
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        if (!modal) return;
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }

    thumbs.forEach((t, i) => t.addEventListener('click', () => openLightbox(i)));
    if (btnClose) btnClose.addEventListener('click', closeLightbox);
    if (btnPrev)  btnPrev.addEventListener('click', () => openLightbox(currentIdx - 1));
    if (btnNext)  btnNext.addEventListener('click', () => openLightbox(currentIdx + 1));

    if (modal) {
        modal.addEventListener('click', e => { if (e.target === modal) closeLightbox(); });
        document.addEventListener('keydown', e => {
            if (!modal.classList.contains('open')) return;
            if (e.key === 'Escape')     closeLightbox();
            if (e.key === 'ArrowLeft')  openLightbox(currentIdx - 1);
            if (e.key === 'ArrowRight') openLightbox(currentIdx + 1);
        });
    }

    // ─────────────────────────────────────────────
    // 4. MARK ACTIVE NAV LINK
    // ─────────────────────────────────────────────
    const path = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href') || '';
        if (href === path || (href !== '/' && path.startsWith(href.split('#')[0]) && href.split('#')[0] !== '/')) {
            link.classList.add('active');
        }
    });

});
