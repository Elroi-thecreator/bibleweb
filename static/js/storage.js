// LocalStorage Keys
const KEYS = {
    BOOKMARKS: 'bilingual_bible_bookmarks',
    HIGHLIGHTS: 'bilingual_bible_highlights',
    VIEW_MODE: 'bilingual_bible_view_mode', // 'split' | 'interlinear'
    FONT_SIZE: 'bilingual_bible_font_size'
};

// Mode Toggle (Split View vs Interlinear)
function initViewMode() {
    const savedMode = localStorage.getItem(KEYS.VIEW_MODE) || 'split';
    applyViewMode(savedMode);
}

function toggleViewMode(mode) {
    localStorage.setItem(KEYS.VIEW_MODE, mode);
    applyViewMode(mode);
}

function applyViewMode(mode) {
    const container = document.getElementById('verses-container');
    if (!container) return;

    const btnSplit = document.getElementById('btn-view-split');
    const btnInterlinear = document.getElementById('btn-view-interlinear');

    if (mode === 'interlinear') {
        container.classList.remove('md:grid-cols-2');
        container.classList.add('grid-cols-1');
        document.querySelectorAll('.verse-card').forEach(el => el.classList.add('interlinear-card'));
        btnInterlinear?.classList.add('bg-blue-600', 'text-white');
        btnSplit?.classList.remove('bg-blue-600', 'text-white');
    } else {
        container.classList.remove('grid-cols-1');
        container.classList.add('md:grid-cols-2');
        document.querySelectorAll('.verse-card').forEach(el => el.classList.remove('interlinear-card'));
        btnSplit?.classList.add('bg-blue-600', 'text-white');
        btnInterlinear?.classList.remove('bg-blue-600', 'text-white');
    }
}

// Bookmarking System
function getBookmarks() {
    return JSON.parse(localStorage.getItem(KEYS.BOOKMARKS) || '[]');
}

function isBookmarked(bookId, ch, v) {
    return getBookmarks().some(b => b.bookId === bookId && b.ch === ch && b.v === v);
}

function toggleBookmark(bookId, bookNameEn, bookNameTa, ch, v, textEn, textTa) {
    let bookmarks = getBookmarks();
    const index = bookmarks.findIndex(b => b.bookId === bookId && b.ch === ch && b.v === v);

    if (index >= 0) {
        bookmarks.splice(index, 1);
    } else {
        bookmarks.push({
            bookId, bookNameEn, bookNameTa, ch, v, textEn, textTa,
            timestamp: new Date().toISOString()
        });
    }

    localStorage.setItem(KEYS.BOOKMARKS, JSON.stringify(bookmarks));
    updateBookmarkButtons();
}

function updateBookmarkButtons() {
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        const b = parseInt(btn.dataset.book);
        const c = parseInt(btn.dataset.chapter);
        const v = parseInt(btn.dataset.verse);
        if (isBookmarked(b, c, v)) {
            btn.innerHTML = '★';
            btn.classList.add('text-amber-500');
        } else {
            btn.innerHTML = '☆';
            btn.classList.remove('text-amber-500');
        }
    });
}

// Clipboard Copy
function copyBilingualVerse(enRef, taRef, enText, taText) {
    const formatted = `"${enText}"\n— ${enRef}\n\n"${taText}"\n— ${taRef}`;
    navigator.clipboard.writeText(formatted).then(() => {
        alert('Verse copied in Tamil and English!');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initViewMode();
    updateBookmarkButtons();
});