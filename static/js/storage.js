// LocalStorage Keys
const STORAGE_KEYS = {
    BOOKMARKS: 'bilingual_bible_bookmarks',
    HIGHLIGHTS: 'bilingual_bible_highlights',
    READ_CHAPTERS: 'bible_read_chapters',
    THEME: 'bible_app_theme',
    FONT_SIZE: 'bible_font_size',
    CACHED_USER_EMAIL: 'bible_cached_auth_email'
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
// 2. Reading Progress Engine (Immediate Cloud Push)
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

    // Push immediately to Supabase database without debounce
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

        // Push immediately to Supabase database without debounce
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
// 4. Backup & Restore (JSON Export)
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
    reader.onload = async function(e) {
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
// 5. Supabase Auth & Cloud Sync
// ==========================================
let currentAuthUser = null;

function applyCachedAuthUI() {
    const cachedEmail = localStorage.getItem(STORAGE_KEYS.CACHED_USER_EMAIL);
    const label = document.getElementById('auth-btn-label');
    const btn = document.getElementById('auth-btn');
    if (!label || !btn) return;

    if (cachedEmail) {
        const username = cachedEmail.split('@')[0];
        label.innerText = username.length > 9 ? username.slice(0, 9) + '…' : username;
        btn.classList.remove('border-stone-300', 'dark:border-stone-700');
        btn.classList.add('border-emerald-600', 'text-emerald-700', 'dark:text-emerald-400', 'bg-emerald-50/30');
    } else {
        label.innerText = 'Sign In';
        btn.classList.remove('border-emerald-600', 'text-emerald-700', 'dark:text-emerald-400', 'bg-emerald-50/30');
        btn.classList.add('border-stone-300', 'dark:border-stone-700');
    }
}

function updateSupabaseAuthUI() {
    const label = document.getElementById('auth-btn-label');
    const btn = document.getElementById('auth-btn');
    if (!label || !btn) return;

    if (currentAuthUser) {
        localStorage.setItem(STORAGE_KEYS.CACHED_USER_EMAIL, currentAuthUser.email);
        const username = currentAuthUser.email.split('@')[0];
        label.innerText = username.length > 9 ? username.slice(0, 9) + '…' : username;
        btn.classList.remove('border-stone-300', 'dark:border-stone-700');
        btn.classList.add('border-emerald-600', 'text-emerald-700', 'dark:text-emerald-400', 'bg-emerald-50/30');
    } else {
        localStorage.removeItem(STORAGE_KEYS.CACHED_USER_EMAIL);
        label.innerText = 'Sign In';
        btn.classList.remove('border-emerald-600', 'text-emerald-700', 'dark:text-emerald-400', 'bg-emerald-50/30');
        btn.classList.add('border-stone-300', 'dark:border-stone-700');
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

function handleAuthButtonClick() {
    const cachedEmail = localStorage.getItem(STORAGE_KEYS.CACHED_USER_EMAIL);
    if (currentAuthUser || cachedEmail) {
        document.getElementById('account-email-display').innerText = currentAuthUser ? currentAuthUser.email : cachedEmail;
        document.getElementById('account-modal').classList.remove('hidden');
    } else {
        document.getElementById('auth-modal').classList.remove('hidden');
    }
}
window.handleAuthButtonClick = handleAuthButtonClick;

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
        btn.innerText = "Send Sign-In Link →";
    }
}
window.handleSendMagicLink = handleSendMagicLink;

async function handleSignOut() {
    if (!window.sbClient) return;
    if (confirm("Sign out on this device? Your local reading progress remains safe.")) {
        await window.sbClient.auth.signOut();
        currentAuthUser = null;
        updateSupabaseAuthUI();
        document.getElementById('account-modal').classList.add('hidden');
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

    const mergedPlans = {};
    const planKeys = new Set([...Object.keys(remote.plans || {}), ...Object.keys(local.plans || {})]);
    planKeys.forEach(pk => {
        const days = new Set([...(remote.plans?.[pk] || []), ...(local.plans?.[pk] || [])]);
        mergedPlans[pk] = Array.from(days).sort((a, b) => a - b);
    });

    return {
        read_chapters: mergedChapters,
        bookmarks: Array.from(bookmarkMap.values()),
        highlights: mergedHighlights,
        plans: mergedPlans,
        theme: local.theme || remote.theme || 'light'
    };
}

async function syncWithSupabase() {
    if (!window.sbClient || !currentAuthUser) return;

    try {
        const localData = {
            bookmarks: getBookmarks(),
            highlights: getHighlights(),
            read_chapters: getReadChapters(),
            theme: localStorage.getItem(STORAGE_KEYS.THEME) || 'light',
            plans: {}
        };
        for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            if (k && k.startsWith('bible_plan_')) {
                try { localData.plans[k] = JSON.parse(localStorage.getItem(k) || '[]'); } catch(e){}
            }
        }

        const { data: remoteRow, error: fetchError } = await window.sbClient
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
        Object.keys(merged.plans).forEach(pk => {
            localStorage.setItem(pk, JSON.stringify(merged.plans[pk]));
        });

        // Direct push to server
        await window.sbClient
            .from('user_bible_sync')
            .upsert({
                user_id: currentAuthUser.id,
                email: currentAuthUser.email,
                data: merged,
                updated_at: new Date().toISOString()
            });

        if (typeof window.updateBookmarkUI === 'function') window.updateBookmarkUI();
        if (typeof window.updateChapterReadUI === 'function' && window.CURRENT_BOOK_ID) {
            window.updateChapterReadUI(window.CURRENT_BOOK_ID, window.CURRENT_CHAPTER);
        }
        if (typeof renderProgressDashboard === 'function') renderProgressDashboard();

        console.log("Supabase synced in real-time.");
    } catch (err) {
        console.warn("Supabase push deferred:", err);
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

// Safe Init
document.addEventListener('DOMContentLoaded', () => {
    applyCachedAuthUI();
    updateBookmarkUI();
    if (typeof window.CURRENT_BOOK_ID !== 'undefined' && typeof window.CURRENT_CHAPTER !== 'undefined') {
        updateChapterReadUI(window.CURRENT_BOOK_ID, window.CURRENT_CHAPTER);
        applyHighlights();
    }
    initSupabaseAuth();
});