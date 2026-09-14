const STORAGE_KEYS = {
    BOOKMARKS: 'bilingual_bible_bookmarks',
    HIGHLIGHTS: 'bilingual_bible_highlights',
    READ_CHAPTERS: 'bible_read_chapters',
    THEME: 'bible_app_theme',
    FONT_SIZE: 'bible_font_size'
};

// ==========================================
// 1. Toast Notification Utility (Safe DOM)
// ==========================================
function showToast(message) {
    try {
        let toast = document.getElementById('app-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'app-toast';
            toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#18181b;color:#ffffff;font-size:12px;padding:8px 16px;border-radius:9999px;z-index:9999;box-shadow:0 10px 15px -3px rgba(0,0,0,0.3);transition:opacity 0.2s ease;pointer-events:none;opacity:0;';
            document.body.appendChild(toast);
        }
        toast.innerText = message;
        toast.style.opacity = '1';
        setTimeout(() => { toast.style.opacity = '0'; }, 2000);
    } catch (e) {
        console.log("Toast fallback:", message);
    }
}
window.showToast = showToast;

// ==========================================
// 2. Reading Progress Engine
// ==========================================
function getReadChapters() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEYS.READ_CHAPTERS) || '{}');
    } catch (e) {
        return {};
    }
}
window.getReadChapters = getReadChapters;

function isChapterRead(bookId, ch) {
    const records = getReadChapters();
    return !!records[`${bookId}_${ch}`];
}
window.isChapterRead = isChapterRead;

function toggleChapterRead(bookId, ch) {
    const b = parseInt(bookId);
    const c = parseInt(ch);
    if (isNaN(b) || isNaN(c)) return;

    let records = getReadChapters();
    const key = `${b}_${c}`;
    const today = new Date().toISOString().split('T')[0];

    if (records[key]) {
        delete records[key];
        showToast(`Chapter ${c} marked as unread`);
    } else {
        records[key] = today;
        showToast(`Chapter ${c} completed! ✓`);
    }

    localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(records));
    updateChapterReadUI(b, c);
}
window.toggleChapterRead = toggleChapterRead;

function markChapterAsReadDirect(bookId, ch) {
    const b = parseInt(bookId);
    const c = parseInt(ch);
    if (isNaN(b) || isNaN(c)) return;

    let records = getReadChapters();
    const key = `${b}_${c}`;
    if (!records[key]) {
        records[key] = new Date().toISOString().split('T')[0];
        localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(records));
        updateChapterReadUI(b, c);
    }
}
window.markChapterAsReadDirect = markChapterAsReadDirect;

function updateChapterReadUI(bookId, ch) {
    const b = parseInt(bookId);
    const c = parseInt(ch);
    if (isNaN(b) || isNaN(c)) return;

    const isRead = isChapterRead(b, c);

    const btns = document.querySelectorAll('.chapter-read-btn');
    btns.forEach(btn => {
        if (isRead) {
            btn.innerHTML = '✓ Completed';
            btn.className = 'chapter-read-btn flex items-center justify-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold border shadow-xs transition cursor-pointer bg-emerald-700 text-white border-emerald-600';
        } else {
            btn.innerHTML = 'Mark as Read ✓';
            btn.className = 'chapter-read-btn flex items-center justify-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold border shadow-xs transition cursor-pointer bg-stone-100 dark:bg-stone-800 text-stone-800 dark:text-stone-200 border-stone-300 dark:border-stone-700 hover:border-amber-600';
        }
    });

    const trayButtons = document.querySelectorAll('.chapter-tray-btn');
    trayButtons.forEach(btn => {
        const trayCh = parseInt(btn.dataset.chapter);
        if (isChapterRead(b, trayCh)) {
            btn.classList.add('ring-2', 'ring-emerald-500');
        } else {
            btn.classList.remove('ring-2', 'ring-emerald-500');
        }
    });
}
window.updateChapterReadUI = updateChapterReadUI;

function getReadingStreak() {
    const records = getReadChapters();
    const dates = [...new Set(Object.values(records))].sort().reverse();
    if (dates.length === 0) return 0;

    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

    if (!dates.includes(today) && !dates.includes(yesterday)) return 0;

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
window.getReadingStreak = getReadingStreak;

// ==========================================
// 3. Bookmarks & Color Highlighting
// ==========================================
function getBookmarks() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEYS.BOOKMARKS) || '[]');
    } catch (e) {
        return [];
    }
}
window.getBookmarks = getBookmarks;

function getHighlights() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEYS.HIGHLIGHTS) || '{}');
    } catch (e) {
        return {};
    }
}
window.getHighlights = getHighlights;

function isBookmarked(bookId, ch, v) {
    return getBookmarks().some(b => b.bookId === bookId && b.ch === ch && b.v === v);
}
window.isBookmarked = isBookmarked;

function toggleBookmark(bookId, bookNameEn, bookNameTa, ch, v, textEn, textTa) {
    let bookmarks = getBookmarks();
    const idx = bookmarks.findIndex(b => b.bookId === bookId && b.ch === ch && b.v === v);

    if (idx >= 0) {
        bookmarks.splice(idx, 1);
        showToast("Bookmark removed");
    } else {
        bookmarks.push({
            bookId, bookNameEn, bookNameTa, ch, v, textEn, textTa,
            date: new Date().toLocaleDateString()
        });
        showToast("Verse bookmarked! ★");
    }

    localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(bookmarks));
    updateBookmarkUI();
}
window.toggleBookmark = toggleBookmark;

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
window.updateBookmarkUI = updateBookmarkUI;

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
window.setVerseHighlight = setVerseHighlight;

function applyHighlights() {
    const highlights = getHighlights();
    const b = window.CURRENT_BOOK_ID;
    const c = window.CURRENT_CHAPTER;
    if (!b || !c) return;

    document.querySelectorAll('.verse-item').forEach(el => {
        const vNum = el.id.replace('v', '');
        const key = `${b}_${c}_${vNum}`;

        el.classList.remove('bg-amber-100/50', 'dark:bg-amber-950/30', 'bg-emerald-100/50', 'dark:bg-emerald-950/30', 'bg-rose-100/50', 'dark:bg-rose-950/30');

        if (highlights[key] === 'yellow') el.classList.add('bg-amber-100/50', 'dark:bg-amber-950/30');
        if (highlights[key] === 'green') el.classList.add('bg-emerald-100/50', 'dark:bg-emerald-950/30');
        if (highlights[key] === 'rose') el.classList.add('bg-rose-100/50', 'dark:bg-rose-950/30');
    });
}
window.applyHighlights = applyHighlights;

function copyBilingualVerse(refEn, refTa, textEn, textTa) {
    const quote = `"${textEn}"\n— ${refEn}\n\n"${textTa}"\n— ${refTa}\n\nShared via Holy Bible App`;
    navigator.clipboard.writeText(quote).then(() => {
        showToast("Verse copied! 📋");
    });
}
window.copyBilingualVerse = copyBilingualVerse;

// ==========================================
// 4. Universal Backup & Restore
// ==========================================
function exportAllUserData() {
    try {
        const backupPayload = {
            app: "bilingual_bible_app",
            version: "2.0",
            exported_at: new Date().toISOString(),
            data: {
                bookmarks: getBookmarks(),
                highlights: getHighlights(),
                read_chapters: getReadChapters(),
                theme: localStorage.getItem(STORAGE_KEYS.THEME) || 'light',
                plans: {}
            }
        };

        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('bible_plan_')) {
                try {
                    backupPayload.data.plans[key] = JSON.parse(localStorage.getItem(key) || '[]');
                } catch (e) {
                    backupPayload.data.plans[key] = [];
                }
            }
        }

        const jsonString = JSON.stringify(backupPayload, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.setAttribute('download', `bible_backup_${new Date().toISOString().split('T')[0]}.json`);
        document.body.appendChild(a);
        a.click();

        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 1500);

        showToast("Backup saved! 💾");
    } catch (err) {
        alert("Failed to export backup: " + err.message);
    }
}
window.exportAllUserData = exportAllUserData;
window.exportProgress = exportAllUserData;

function importAllUserData(fileInputEvent, reloadCallback) {
    const file = fileInputEvent.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const parsed = JSON.parse(e.target.result);
            const payloadData = parsed.data || parsed;

            if (payloadData.bookmarks) localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(payloadData.bookmarks));
            if (payloadData.highlights) localStorage.setItem(STORAGE_KEYS.HIGHLIGHTS, JSON.stringify(payloadData.highlights));
            if (payloadData.read_chapters) localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(payloadData.read_chapters));
            if (payloadData.theme) localStorage.setItem(STORAGE_KEYS.THEME, payloadData.theme);
            if (payloadData.plans) {
                Object.keys(payloadData.plans).forEach(planKey => {
                    localStorage.setItem(planKey, JSON.stringify(payloadData.plans[planKey]));
                });
            }

            showToast("Backup restored! ✓");
            if (typeof reloadCallback === 'function') {
                reloadCallback();
            } else {
                setTimeout(() => window.location.reload(), 600);
            }
        } catch (err) {
            alert("Invalid backup file format.");
        }
    };
    reader.readAsText(file);
}
window.importAllUserData = importAllUserData;

document.addEventListener('DOMContentLoaded', () => {
    updateBookmarkUI();
    if (typeof window.CURRENT_BOOK_ID !== 'undefined' && typeof window.CURRENT_CHAPTER !== 'undefined') {
        updateChapterReadUI(window.CURRENT_BOOK_ID, window.CURRENT_CHAPTER);
        applyHighlights();
    }
});