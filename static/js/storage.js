// ==========================================
// Reading Progress & Tracking Engine
// ==========================================

function getReadChapters() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEYS.READ_CHAPTERS) || '{}');
    } catch (e) {
        return {};
    }
}

function isChapterRead(bookId, ch) {
    const records = getReadChapters();
    return !!records[`${bookId}_${ch}`];
}

function toggleChapterRead(bookId, ch) {
    const b = parseInt(bookId);
    const c = parseInt(ch);
    let records = getReadChapters();
    const key = `${b}_${c}`;
    const today = new Date().toISOString().split('T')[0];

    if (records[key]) {
        delete records[key];
        showToast(`Chapter ${c} marked as unread`);
    } else {
        records[key] = today;
        showToast(`Chapter ${c} marked as completed! ✓`);
    }

    localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(records));
    updateChapterReadUI(b, c);
}

function markChapterAsReadDirect(bookId, ch) {
    const b = parseInt(bookId);
    const c = parseInt(ch);
    let records = getReadChapters();
    const key = `${b}_${c}`;
    if (!records[key]) {
        records[key] = new Date().toISOString().split('T')[0];
        localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(records));
        updateChapterReadUI(b, c);
    }
}

function updateChapterReadUI(bookId, ch) {
    const b = parseInt(bookId);
    const c = parseInt(ch);
    const isRead = isChapterRead(b, c);

    // Update all mark-as-read buttons on screen
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

    // Update chapter grid buttons if open
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

// Attach explicitly to window so onclick handlers never miss it
window.toggleChapterRead = toggleChapterRead;
window.markChapterAsReadDirect = markChapterAsReadDirect;
window.updateChapterReadUI = updateChapterReadUI;
window.isChapterRead = isChapterRead;
window.getReadChapters = getReadChapters;