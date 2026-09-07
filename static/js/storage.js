const KEYS = {
    BOOKMARKS: 'bilingual_bible_bookmarks',
    LAST_READ: 'bilingual_bible_last_read'
};

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
            date: new Date().toLocaleDateString()
        });
    }

    localStorage.setItem(KEYS.BOOKMARKS, JSON.stringify(bookmarks));
    updateBookmarkUI();
}

function updateBookmarkUI() {
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        const b = parseInt(btn.dataset.book);
        const c = parseInt(btn.dataset.chapter);
        const v = parseInt(btn.dataset.verse);
        if (isBookmarked(b, c, v)) {
            btn.innerHTML = '★';
            btn.classList.add('text-amber-600');
        } else {
            btn.innerHTML = '☆';
            btn.classList.remove('text-amber-600');
        }
    });
}

function copyBilingualVerse(refEn, refTa, textEn, textTa) {
    const formatted = `"${textEn}"\n— ${refEn}\n\n"${textTa}"\n— ${refTa}`;
    navigator.clipboard.writeText(formatted).then(() => {
        alert('Copied to clipboard / பிரதியெடுக்கப்பட்டது');
    });
}

document.addEventListener('DOMContentLoaded', updateBookmarkUI);