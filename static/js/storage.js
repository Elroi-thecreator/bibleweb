// LocalStorage Keys
const STORAGE_KEYS = {
    BOOKMARKS: 'bilingual_bible_bookmarks',
    HIGHLIGHTS: 'bilingual_bible_highlights',
    READ_CHAPTERS: 'bible_read_chapters',
    THEME: 'bible_app_theme',
    FONT_SIZE: 'bible_font_size',
    CACHED_USER_EMAIL: 'bible_cached_auth_email',
    CUSTOM_PLANS: 'bible_custom_reading_plans'
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
// 2. Canonical Reading Progress (Independent)
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

async function toggleChapterRead(bookId, ch) {
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
    await syncWithSupabase();
}
window.toggleChapterRead = toggleChapterRead;

async function markChapterAsReadDirect(bookId, ch) {
    const b = parseInt(bookId);
    const c = parseInt(ch);
    if (isNaN(b) || isNaN(c)) return;

    let records = getReadChapters();
    const key = `${b}_${c}`;
    if (!records[key]) {
        records[key] = new Date().toISOString().split('T')[0];
        localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(records));
        updateChapterReadUI(b, c);
        await syncWithSupabase();
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
            btn.innerHTML = `
                <svg class="w-4 h-4 text-white stroke-[2.5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>`;
            btn.className = 'chapter-read-btn flex items-center justify-center w-8 h-8 rounded-xl border shadow-xs transition cursor-pointer bg-emerald-600 text-white border-emerald-500 shrink-0';
            btn.title = 'Completed (click to mark unread)';
        } else {
            btn.innerHTML = `
                <svg class="w-4 h-4 text-stone-400 dark:text-stone-500 hover:text-amber-600 stroke-[2.5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>`;
            btn.className = 'chapter-read-btn flex items-center justify-center w-8 h-8 rounded-xl border shadow-xs transition cursor-pointer bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 border-stone-300 dark:border-stone-700 hover:border-amber-600 shrink-0';
            btn.title = 'Mark as Read';
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
// 3. Persistent Font-Size Engine
// ==========================================
function applyPersistentFontSize() {
    const size = parseInt(localStorage.getItem(STORAGE_KEYS.FONT_SIZE) || '18');
    document.documentElement.style.setProperty('--reader-font-size', `${size}px`);

    const reader = document.getElementById('reader-content');
    if (reader) {
        reader.style.setProperty('font-size', `${size}px`, 'important');
    }

    const verses = document.querySelectorAll('.verse-text, .verse-en, .verse-ta, .verse-text-en, .verse-text-ta');
    verses.forEach(v => {
        v.style.setProperty('font-size', `${size}px`, 'important');
    });
}
window.applyPersistentFontSize = applyPersistentFontSize;

function adjustFontSize(delta) {
    const currentSize = parseInt(localStorage.getItem(STORAGE_KEYS.FONT_SIZE) || '18');
    let newSize = delta === 0 ? 18 : Math.min(Math.max(currentSize + (delta * 2), 13), 28);

    localStorage.setItem(STORAGE_KEYS.FONT_SIZE, newSize.toString());
    applyPersistentFontSize();
    showToast(`Font size: ${newSize}px`);
}
window.adjustFontSize = adjustFontSize;

// ==========================================
// 4. Bookmarks & Color Highlighting
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

async function toggleBookmark(bookId, bookNameEn, bookNameTa, ch, v, textEn, textTa) {
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
    await syncWithSupabase();
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
    queueCloudSync();
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

        if (highlights[key]) {
            if (highlights[key] === 'yellow') el.classList.add('bg-amber-100/50', 'dark:bg-amber-950/30');
            if (highlights[key] === 'green') el.classList.add('bg-emerald-100/50', 'dark:bg-emerald-950/30');
            if (highlights[key] === 'rose') el.classList.add('bg-rose-100/50', 'dark:bg-rose-950/30');
        }
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
// 5. Backup & Restore (JSON Export)
// ==========================================
function exportAllUserData() {
    try {
        let customPlans = [];
        try { customPlans = JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_PLANS) || '[]'); } catch(e){}

        const backupPayload = {
            app: "bilingual_bible_app",
            version: "2.2",
            exported_at: new Date().toISOString(),
            data: {
                bookmarks: getBookmarks(),
                highlights: getHighlights(),
                read_chapters: getReadChapters(),
                custom_reading_plans: customPlans,
                theme: localStorage.getItem(STORAGE_KEYS.THEME) || 'light',
                font_size: localStorage.getItem(STORAGE_KEYS.FONT_SIZE) || '18'
            }
        };

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
    reader.onload = async function(e) {
        try {
            const parsed = JSON.parse(e.target.result);
            const payloadData = parsed.data || parsed;

            if (payloadData.bookmarks) localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(payloadData.bookmarks));
            if (payloadData.highlights) localStorage.setItem(STORAGE_KEYS.HIGHLIGHTS, JSON.stringify(payloadData.highlights));
            if (payloadData.read_chapters) localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(payloadData.read_chapters));
            if (payloadData.theme) localStorage.setItem(STORAGE_KEYS.THEME, payloadData.theme);
            if (payloadData.font_size) localStorage.setItem(STORAGE_KEYS.FONT_SIZE, payloadData.font_size);
            if (payloadData.custom_reading_plans) {
                localStorage.setItem(STORAGE_KEYS.CUSTOM_PLANS, JSON.stringify(payloadData.custom_reading_plans));
            }

            showToast("Backup restored! ✓");
            await syncWithSupabase();
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

// ==========================================
// 6. Supabase Auth & Multi-Plan Cloud Sync
// ==========================================
let currentAuthUser = null;

function applyCachedAuthUI() {
    const cachedEmail = localStorage.getItem(STORAGE_KEYS.CACHED_USER_EMAIL);
    const navDot = document.getElementById('nav-auth-dot');
    const loggedInView = document.getElementById('settings-logged-in-view');
    const loggedOutView = document.getElementById('settings-logged-out-view');
    const userEmailDisplay = document.getElementById('settings-user-email');
    const statusLabel = document.getElementById('settings-auth-status');

    if (cachedEmail) {
        if (navDot) navDot.classList.remove('hidden');
        if (loggedInView) loggedInView.classList.remove('hidden');
        if (loggedOutView) loggedOutView.classList.add('hidden');
        if (userEmailDisplay) userEmailDisplay.innerText = cachedEmail;
        if (statusLabel) statusLabel.innerText = "Synced";
    } else {
        if (navDot) navDot.classList.add('hidden');
        if (loggedInView) loggedInView.classList.add('hidden');
        if (loggedOutView) loggedOutView.classList.remove('hidden');
        if (statusLabel) statusLabel.innerText = "Not Connected";
    }
}

function updateSupabaseAuthUI() {
    const navDot = document.getElementById('nav-auth-dot');
    const loggedInView = document.getElementById('settings-logged-in-view');
    const loggedOutView = document.getElementById('settings-logged-out-view');
    const userEmailDisplay = document.getElementById('settings-user-email');
    const statusLabel = document.getElementById('settings-auth-status');

    if (currentAuthUser) {
        localStorage.setItem(STORAGE_KEYS.CACHED_USER_EMAIL, currentAuthUser.email);
        if (navDot) navDot.classList.remove('hidden');
        if (loggedInView) loggedInView.classList.remove('hidden');
        if (loggedOutView) loggedOutView.classList.add('hidden');
        if (userEmailDisplay) userEmailDisplay.innerText = currentAuthUser.email;
        if (statusLabel) statusLabel.innerText = "Synced";
    } else {
        localStorage.removeItem(STORAGE_KEYS.CACHED_USER_EMAIL);
        if (navDot) navDot.classList.add('hidden');
        if (loggedInView) loggedInView.classList.add('hidden');
        if (loggedOutView) loggedOutView.classList.remove('hidden');
        if (statusLabel) statusLabel.innerText = "Not Connected";
    }
}

function initSupabaseAuth() {
    applyCachedAuthUI();
    if (!window.sbClient) return;

    window.sbClient.auth.onAuthStateChange(async (event, session) => {
        currentAuthUser = session?.user || null;
        updateSupabaseAuthUI();

        if (event === 'SIGNED_IN' && currentAuthUser) {
            showToast(`Signed in as ${currentAuthUser.email}! Syncing... ☁️`);
            await syncWithSupabase();
        }
    });

    window.sbClient.auth.getSession().then(({ data: { session } }) => {
        currentAuthUser = session?.user || null;
        updateSupabaseAuthUI();
        if (currentAuthUser) {
            syncWithSupabase();
        }
    });
}

async function handleSendMagicLink(e) {
    e.preventDefault();
    if (!window.sbClient) {
        alert("Supabase client is not configured yet. Please check your keys in base.html.");
        return;
    }

    const email = document.getElementById('auth-email-input').value.trim();
    const btn = document.getElementById('magic-link-btn');
    btn.disabled = true;
    btn.innerText = "Sending Link...";

    try {
        const { error } = await window.sbClient.auth.signInWithOtp({
            email: email,
            options: { emailRedirectTo: window.location.origin }
        });

        if (error) {
            alert("Error sending link: " + error.message);
        } else {
            alert(`Sign-in link sent to ${email}!\n\nCheck your inbox and spam folder. Click the link to complete setup.`);
            document.getElementById('auth-modal').classList.add('hidden');
        }
    } catch (err) {
        alert("Request failed: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerText = "Send Link →";
    }
}
window.handleSendMagicLink = handleSendMagicLink;

async function handleSignOut() {
    if (!window.sbClient) return;
    if (confirm("Sign out on this device? Your local reading progress remains safe.")) {
        await window.sbClient.auth.signOut();
        currentAuthUser = null;
        updateSupabaseAuthUI();
        showToast("Signed out");
    }
}
window.handleSignOut = handleSignOut;

function mergeSyncData(local, remote) {
    const mergedChapters = { ...(remote.read_chapters || {}), ...(local.read_chapters || {}) };

    const bookmarkMap = new Map();
    [...(remote.bookmarks || []), ...(local.bookmarks || [])].forEach(b => {
        bookmarkMap.set(`${b.bookId}_${b.ch}_${b.v}`, b);
    });

    const mergedHighlights = { ...(remote.highlights || {}), ...(local.highlights || {}) };

    // Merge multi-plans safely by Plan ID
    const planMap = new Map();
    [...(remote.custom_reading_plans || []), ...(local.custom_reading_plans || [])].forEach(p => {
        if (!planMap.has(p.id)) {
            planMap.set(p.id, p);
        } else {
            const existing = planMap.get(p.id);
            planMap.set(p.id, {
                ...existing,
                ...p,
                completedChapters: { ...(existing.completedChapters || {}), ...(p.completedChapters || {}) }
            });
        }
    });

    return {
        read_chapters: mergedChapters,
        bookmarks: Array.from(bookmarkMap.values()),
        highlights: mergedHighlights,
        custom_reading_plans: Array.from(planMap.values()),
        theme: local.theme || remote.theme || 'light',
        font_size: local.font_size || remote.font_size || '18'
    };
}

async function syncWithSupabase() {
    if (!window.sbClient || !currentAuthUser) return;

    try {
        let customPlans = [];
        try {
            customPlans = JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_PLANS) || '[]');
        } catch (e) {
            customPlans = [];
        }

        const localData = {
            bookmarks: getBookmarks(),
            highlights: getHighlights(),
            read_chapters: getReadChapters(),
            theme: localStorage.getItem(STORAGE_KEYS.THEME) || 'light',
            font_size: localStorage.getItem(STORAGE_KEYS.FONT_SIZE) || '18',
            custom_reading_plans: customPlans
        };

        const { data: remoteRow } = await window.sbClient
            .from('user_bible_sync')
            .select('data')
            .eq('user_id', currentAuthUser.id)
            .maybeSingle();

        let merged = localData;
        if (remoteRow && remoteRow.data) {
            merged = mergeSyncData(localData, remoteRow.data);
        }

        localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(merged.bookmarks));
        localStorage.setItem(STORAGE_KEYS.HIGHLIGHTS, JSON.stringify(merged.highlights));
        localStorage.setItem(STORAGE_KEYS.READ_CHAPTERS, JSON.stringify(merged.read_chapters));
        if (merged.font_size) localStorage.setItem(STORAGE_KEYS.FONT_SIZE, merged.font_size);
        if (merged.custom_reading_plans) {
            localStorage.setItem(STORAGE_KEYS.CUSTOM_PLANS, JSON.stringify(merged.custom_reading_plans));
        }

        await window.sbClient
            .from('user_bible_sync')
            .upsert({
                user_id: currentAuthUser.id,
                email: currentAuthUser.email,
                data: merged,
                updated_at: new Date().toISOString()
            });

        applyPersistentFontSize();
        if (typeof window.updateBookmarkUI === 'function') window.updateBookmarkUI();
        if (typeof window.updateChapterReadUI === 'function' && window.CURRENT_BOOK_ID) {
            window.updateChapterReadUI(window.CURRENT_BOOK_ID, window.CURRENT_CHAPTER);
        }
        if (typeof renderAllPlans === 'function') renderAllPlans();
        if (typeof renderProgressDashboard === 'function') renderProgressDashboard();

        console.log("Supabase multi-plans synced.");
    } catch (err) {
        console.warn("Supabase multi-plan sync deferred:", err);
    }
}
window.syncWithSupabase = syncWithSupabase;

let cloudSyncTimer = null;
function queueCloudSync() {
    if (!currentAuthUser) return;
    clearTimeout(cloudSyncTimer);
    cloudSyncTimer = setTimeout(syncWithSupabase, 2000);
}
window.queueCloudSync = queueCloudSync;

// Safe Init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    applyCachedAuthUI();
    applyPersistentFontSize();
    updateBookmarkUI();
    if (typeof window.CURRENT_BOOK_ID !== 'undefined' && typeof window.CURRENT_CHAPTER !== 'undefined') {
        updateChapterReadUI(window.CURRENT_BOOK_ID, window.CURRENT_CHAPTER);
        applyHighlights();
    }
    initSupabaseAuth();
});