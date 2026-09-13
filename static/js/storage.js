const STORAGE_KEYS = {
    BOOKMARKS: 'bilingual_bible_bookmarks',
    HIGHLIGHTS: 'bilingual_bible_highlights',
    READ_CHAPTERS: 'bible_read_chapters',
    THEME: 'bible_app_theme',
    FONT_SIZE: 'bible_font_size'
};

// ==========================================
// Reading Progress & Tracking Engine
// ==========================================

function getReadChapters() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.READ_CHAPTERS) || '{}');
}

function isChapterRead(bookId, ch) {
    const records = getReadChapters();
    return !!records[`${bookId}_${ch}`];
}

function toggleChapterRead(bookId, ch) {
    let records = getReadChapters();
    const key = `${bookId}_${ch}`;
    const today = new Date().toISOString().split('T')[0];

    if (records[key]) {
        delete records[key];
        showToast(`Chapter ${ch} marked as unread`);
    } else {
        records[key] = today;
        showToast(`Chapter ${ch} marked as completed! ✓`);
    }

    localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(records));
    updateChapterReadUI(bookId, ch);
}

function markChapterAsReadDirect(bookId, ch) {
    let records = getReadChapters();
    const key = `${bookId}_${ch}`;
    if (!records[key]) {
        records[key] = new Date().toISOString().split('T')[0];
        localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(records));
        updateChapterReadUI(bookId, ch);
    }
}

function updateChapterReadUI(bookId, ch) {
    const isRead = isChapterRead(bookId, ch);
    const btns = document.querySelectorAll('.chapter-read-btn');
    btns.forEach(btn => {
        if (isRead) {
            btn.innerHTML = '✓ Completed';
            btn.classList.remove('bg-stone-100', 'dark:bg-stone-800', 'text-stone-700', 'dark:text-stone-300', 'border-stone-300', 'dark:border-stone-700');
            btn.classList.add('bg-emerald-700', 'text-white', 'border-emerald-700');
        } else {
            btn.innerHTML = 'Mark as Read ✓';
            btn.classList.remove('bg-emerald-700', 'text-white', 'border-emerald-700');
            btn.classList.add('bg-stone-100', 'dark:bg-stone-800', 'text-stone-700', 'dark:text-stone-300', 'border-stone-300', 'dark:border-stone-700');
        }
    });

    const trayButtons = document.querySelectorAll('.chapter-tray-btn');
    trayButtons.forEach(btn => {
        const c = parseInt(btn.dataset.chapter);
        if (isChapterRead(bookId, c)) {
            btn.classList.add('ring-2', 'ring-emerald-500');
        } else {
            btn.classList.remove('ring-2', 'ring-emerald-500');
        }
    });
}

function getReadingStreak() {
    const records = getReadChapters();
    const dates = [...new Set(Object.values(records))].sort().reverse();
    if (dates.length === 0) return 0;

    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

    if (!dates.includes(today) && !dates.includes(yesterday)) {
        return 0;
    }

    let streak = 0;
    let curr = new Date(dates[0]);

    for (const dStr of dates) {
        const d = new Date(dStr);
        const diffDays = Math.round((curr - d) / (1000 * 60 * 60 * 24));
        if (diffDays <= 1) {
            streak++;
            curr = d;
        } else {
            break;
        }
    }
    return streak;
}

// ==========================================
// Bookmarks & Color Highlights
// ==========================================

function getBookmarks() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.BOOKMARKS) || '[]');
}

function getHighlights() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.HIGHLIGHTS) || '{}');
}

function isBookmarked(bookId, ch, v) {
    return getBookmarks().some(b => b.bookId === bookId && b.ch === ch && b.v === v);
}

function toggleBookmark(bookId, bookNameEn, bookNameTa, ch, v, textEn, textTa) {
    let bookmarks = getBookmarks();
    const idx = bookmarks.findIndex(b => b.bookId === bookId && b.ch === ch && b.v === v);

    if (idx >= 0) {
        bookmarks.splice(idx, 1);
    } else {
        bookmarks.push({
            bookId, bookNameEn, bookNameTa, ch, v, textEn, textTa,
            date: new Date().toLocaleDateString()
        });
    }

    localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(bookmarks));
    updateBookmarkUI();
}

function updateBookmarkUI() {
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

function setVerseHighlight(bookId, ch, v, colorClass) {
    const key = `${bookId}_${ch}_${v}`;
    let highlights = getHighlights();

    if (highlights[key] === colorClass) {
        delete highlights[key];
    } else {
        highlights[key] = colorClass;
    }

    localStorage.setItem(STORAGE_KEYS.HIGHLIGHTS, JSON.stringify(highlights));
    applyHighlights();
}

function applyHighlights() {
    const highlights = getHighlights();
    document.querySelectorAll('.verse-item').forEach(el => {
        const vNum = el.id.replace('v', '');
        const bookId = window.CURRENT_BOOK_ID;
        const ch = window.CURRENT_CHAPTER;
        const key = `${bookId}_${ch}_${vNum}`;

        el.classList.remove('bg-amber-100/50', 'dark:bg-amber-950/30', 'bg-emerald-100/50', 'dark:bg-emerald-950/30', 'bg-rose-100/50', 'dark:bg-rose-950/30');

        if (highlights[key]) {
            if (highlights[key] === 'yellow') el.classList.add('bg-amber-100/50', 'dark:bg-amber-950/30');
            if (highlights[key] === 'green') el.classList.add('bg-emerald-100/50', 'dark:bg-emerald-950/30');
            if (highlights[key] === 'rose') el.classList.add('bg-rose-100/50', 'dark:bg-rose-950/30');
        }
    });
}

function copyBilingualVerse(refEn, refTa, textEn, textTa) {
    const quote = `"${textEn}"\n— ${refEn}\n\n"${textTa}"\n— ${refTa}\n\nShared via Holy Bible App`;
    navigator.clipboard.writeText(quote).then(() => {
        showToast("Verse copied with reference!");
    });
}

function showToast(message) {
    let toast = document.getElementById('app-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'app-toast';
        toast.className = 'fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-stone-900 text-white text-xs px-4 py-2 rounded-full shadow-lg z-50 transition-opacity duration-300 pointer-events-none';
        document.body.appendChild(toast);
    }
    toast.innerText = message;
    toast.style.opacity = '1';
    setTimeout(() => { toast.style.opacity = '0'; }, 2200);
}

// ==========================================
// Universal Backup & Restore Engine
// ==========================================

function exportAllUserData() {
    const backupPayload = {
        app: "bilingual_bible_app",
        version: "2.0",
        exported_at: new Date().toISOString(),
        data: {
            bookmarks: getBookmarks(),
            highlights: getHighlights(),
            read_chapters: getReadChapters(),
            theme: localStorage.getItem(STORAGE_KEYS.THEME) || 'light',
            font_size: localStorage.getItem(STORAGE_KEYS.FONT_SIZE) || '16',
            plans: {}
        }
    };

    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('bible_plan_')) {
            backupPayload.data.plans[key] = JSON.parse(localStorage.getItem(key) || '[]');
        }
    }

    const blob = new Blob([JSON.stringify(backupPayload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bible_backup_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("Backup downloaded successfully! 💾");
}

function importAllUserData(fileInputEvent, reloadCallback) {
    const file = fileInputEvent.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const parsed = JSON.parse(e.target.result);
            const payloadData = parsed.data || parsed;

            if (payloadData.bookmarks) {
                localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(payloadData.bookmarks));
            }
            if (payloadData.highlights) {
                localStorage.setItem(STORAGE_KEYS.HIGHLIGHTS, JSON.stringify(payloadData.highlights));
            }
            if (payloadData.read_chapters) {
                localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(payloadData.read_chapters));
            }
            if (payloadData.theme) {
                localStorage.setItem(STORAGE_KEYS.THEME, payloadData.theme);
            }
            if (payloadData.plans) {
                Object.keys(payloadData.plans).forEach(planKey => {
                    localStorage.setItem(planKey, JSON.stringify(payloadData.plans[planKey]));
                });
            }

            showToast("Data restored successfully! ✓");

            if (typeof reloadCallback === 'function') {
                reloadCallback();
            } else {
                setTimeout(() => window.location.reload(), 600);
            }
        } catch (err) {
            console.error("Backup parse error:", err);
            alert("Invalid backup file. Please select a valid JSON backup file from this app.");
        }
    };
    reader.readAsText(file);
}

document.addEventListener('DOMContentLoaded', () => {
    updateBookmarkUI();
    applyHighlights();
    if (window.CURRENT_BOOK_ID && window.CURRENT_CHAPTER) {
        updateChapterReadUI(window.CURRENT_BOOK_ID, window.CURRENT_CHAPTER);
    }
});