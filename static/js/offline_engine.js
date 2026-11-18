/**
 * Holy Bible WebApp — Offline Engine & SQLite Wasm Manager
 * Exclusively active when installed as a PWA / standalone application on mobile or desktop.
 * Stores SQLite databases in IndexedDB and executes in-browser queries via WebAssembly.
 */

(function (window) {
    'use strict';

    const DB_NAME = 'holy_bible_offline_db';
    const DB_VERSION = 1;
    const STORE_NAME = 'sqlite_files';

    class HolyBibleOfflineEngine {
        constructor() {
            this.dbPromise = null;
            this.sqlJs = null;
            this.bibleDb = null;
            this.songsDb = null;
            this.isDownloading = false;
            this.isInitialized = false;
            this.booksMap = null;
            this.initIndexedDb();
        }

        // ==========================================
        // 1. Installation & Environment Detection
        // ==========================================

        /**
         * Detects if running inside the native Windows desktop executable (PyWebView / localhost).
         * The native desktop application already embeds the full 50MB SQLite databases directly.
         */
        isNativeDesktop() {
            return window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
        }

        /**
         * Checks if the app is currently running as an installed PWA (standalone/fullscreen)
         * or iOS standalone home-screen webapp.
         */
        isAppInstalled() {
            if (this.isNativeDesktop()) return false;
            const isStandalone = window.matchMedia('(display-mode: standalone)').matches
                || window.matchMedia('(display-mode: fullscreen)').matches
                || window.matchMedia('(display-mode: minimal-ui)').matches;
            const isIOSStandalone = window.navigator.standalone === true;
            return Boolean(isStandalone || isIOSStandalone);
        }

        /**
         * Checks whether WebAssembly and IndexedDB are supported by the browser.
         */
        isSupported() {
            return typeof window !== 'undefined'
                && 'indexedDB' in window
                && typeof WebAssembly === 'object'
                && typeof WebAssembly.instantiate === 'function';
        }

        // ==========================================
        // 2. IndexedDB Storage Layer
        // ==========================================

        initIndexedDb() {
            if (!this.isSupported()) return;
            this.dbPromise = new Promise((resolve, reject) => {
                const req = indexedDB.open(DB_NAME, DB_VERSION);
                req.onupgradeneeded = (e) => {
                    const db = e.target.result;
                    if (!db.objectStoreNames.contains(STORE_NAME)) {
                        db.createObjectStore(STORE_NAME);
                    }
                };
                req.onsuccess = (e) => resolve(e.target.result);
                req.onerror = (e) => {
                    console.warn('[OfflineEngine] IndexedDB open error:', e);
                    reject(e);
                };
            });
        }

        async getStoreValue(key) {
            const db = await this.dbPromise;
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readonly');
                const store = tx.objectStore(STORE_NAME);
                const req = store.get(key);
                req.onsuccess = () => resolve(req.result);
                req.onerror = () => reject(req.error);
            });
        }

        async setStoreValue(key, val) {
            const db = await this.dbPromise;
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readwrite');
                const store = tx.objectStore(STORE_NAME);
                const req = store.put(val, key);
                tx.oncomplete = () => resolve(true);
                tx.onerror = () => reject(tx.error);
            });
        }

        async deleteStoreValue(key) {
            const db = await this.dbPromise;
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readwrite');
                const store = tx.objectStore(STORE_NAME);
                store.delete(key);
                tx.oncomplete = () => resolve(true);
                tx.onerror = () => reject(tx.error);
            });
        }

        async clearAll() {
            const db = await this.dbPromise;
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readwrite');
                const store = tx.objectStore(STORE_NAME);
                store.clear();
                tx.oncomplete = () => {
                    if (this.bibleDb) {
                        try { this.bibleDb.close(); } catch (_) { }
                        this.bibleDb = null;
                    }
                    if (this.songsDb) {
                        try { this.songsDb.close(); } catch (_) { }
                        this.songsDb = null;
                    }
                    resolve(true);
                };
                tx.onerror = () => reject(tx.error);
            });
        }

        /**
         * Checks whether both SQLite databases are downloaded and present in IndexedDB.
         */
        async hasOfflineData() {
            try {
                if (!this.isSupported()) return false;
                const meta = await this.getStoreValue('offline_meta');
                if (!meta) return false;
                const bibleBuf = await this.getStoreValue('bible_db');
                return Boolean(bibleBuf && bibleBuf.byteLength > 1000000);
            } catch (err) {
                console.warn('[OfflineEngine] hasOfflineData check failed:', err);
                return false;
            }
        }

        async getStorageInfo() {
            try {
                const meta = await this.getStoreValue('offline_meta');
                if (!meta) return null;
                return {
                    installedAt: meta.installedAt,
                    bibleSize: meta.bibleSize || 0,
                    songsSize: meta.songsSize || 0,
                    version: meta.version || 'v1.2.1',
                    totalMb: ((meta.bibleSize || 0) + (meta.songsSize || 0)) / (1024 * 1024)
                };
            } catch (_) {
                return null;
            }
        }

        // ==========================================
        // 3. Download & Persistent Storage Pipeline
        // ==========================================

        /**
         * Streams a resource with byte progress callback.
         */
        async fetchWithProgress(url, expectedBytes, onProgress) {
            const resp = await fetch(url);
            if (!resp.ok) throw new Error(`HTTP error ${resp.status} fetching ${url}`);

            const contentLength = resp.headers.get('content-length');
            const totalBytes = contentLength ? parseInt(contentLength, 10) : expectedBytes;

            const reader = resp.body.getReader();
            const chunks = [];
            let loadedBytes = 0;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                chunks.push(value);
                loadedBytes += value.length;
                if (onProgress) {
                    const pct = totalBytes > 0 ? Math.min(100, Math.round((loadedBytes / totalBytes) * 100)) : 50;
                    onProgress(loadedBytes, totalBytes, pct);
                }
            }

            const merged = new Uint8Array(loadedBytes);
            let offset = 0;
            for (const chunk of chunks) {
                merged.set(chunk, offset);
                offset += chunk.length;
            }
            return merged.buffer;
        }

        /**
         * Downloads the entire offline bundle (Bible DB + Songs DB + SQLite Wasm)
         * and writes them into IndexedDB and persistent Cache Storage.
         */
        async downloadOfflineBundle(progressCallback) {
            if (this.isDownloading) return;
            this.isDownloading = true;

            const notify = (statusText, percent, details = '') => {
                if (progressCallback) {
                    progressCallback({ statusText, percent, details });
                }
            };

            try {
                notify('Checking package metadata...', 5);
                const infoResp = await fetch('/api/offline/info');
                if (!infoResp.ok) throw new Error('Could not fetch offline package metadata');
                const info = await infoResp.json();

                // 1. Download Scripture SQLite database
                notify('Downloading Holy Bible database...', 10, 'Tamil & English (48 MB)');
                const bibleBuffer = await this.fetchWithProgress(
                    '/api/offline/bible-db',
                    info.bible_db_size || 49000000,
                    (loaded, total, pct) => {
                        const overallPct = 10 + Math.round(pct * 0.55); // 10% to 65%
                        const loadedMb = (loaded / (1024 * 1024)).toFixed(1);
                        const totalMb = (total / (1024 * 1024)).toFixed(1);
                        notify(`Downloading Bible: ${loadedMb} MB / ${totalMb} MB`, overallPct);
                    }
                );

                notify('Saving Bible database to local storage...', 66);
                await this.setStoreValue('bible_db', bibleBuffer);

                // 2. Download Songs SQLite database
                notify('Downloading Songbook & Hymnal database...', 70, 'Hymns & Lyrics (8 MB)');
                const songsBuffer = await this.fetchWithProgress(
                    '/api/offline/songs-db',
                    info.songs_db_size || 8500000,
                    (loaded, total, pct) => {
                        const overallPct = 70 + Math.round(pct * 0.20); // 70% to 90%
                        const loadedMb = (loaded / (1024 * 1024)).toFixed(1);
                        notify(`Downloading Hymns: ${loadedMb} MB`, overallPct);
                    }
                );

                notify('Saving Hymnal database...', 90);
                await this.setStoreValue('songs_db', songsBuffer);

                // 3. Pre-cache Reader shell and Wasm vendor scripts into Cache API
                notify('Configuring offline reader shell...', 94);
                if ('caches' in window) {
                    try {
                        const cache = await caches.open('bible-app-v4');
                        await cache.addAll([
                            '/',
                            '/read/1/1?mode=bilingual',
                            '/songs',
                            '/static/js/vendor/sql-wasm.js',
                            '/static/js/vendor/sql-wasm.wasm',
                            '/static/js/offline_engine.js',
                            '/static/js/storage.js',
                            '/static/manifest.json'
                        ]);
                    } catch (cacheErr) {
                        console.warn('[OfflineEngine] Shell cache addAll warning:', cacheErr);
                    }
                }

                // 4. Request Persistent Storage from OS
                if (navigator.storage && navigator.storage.persist) {
                    try {
                        const isPersisted = await navigator.storage.persist();
                        console.log('[OfflineEngine] Persistent storage granted:', isPersisted);
                    } catch (_) { }
                }

                // 5. Store metadata
                const meta = {
                    installedAt: Date.now(),
                    bibleSize: bibleBuffer.byteLength,
                    songsSize: songsBuffer.byteLength,
                    version: info.version || 'v1.2.1',
                    protestant_books: info.protestant_books || [],
                    catholic_books: info.catholic_books || []
                };
                await this.setStoreValue('offline_meta', meta);

                notify('Offline Bible & Hymns ready! 🎉', 100);
                this.isDownloading = false;
                this.updateSettingsUI();
                return true;
            } catch (err) {
                this.isDownloading = false;
                console.error('[OfflineEngine] Download error:', err);
                notify(`Download failed: ${err.message}`, -1);
                throw err;
            }
        }

        // ==========================================
        // 4. In-Browser SQLite WebAssembly Query Engine
        // ==========================================

        /**
         * Dynamically loads sql-wasm.js if not already present on page.
         */
        async loadSqlScript() {
            if (typeof window.initSqlJs === 'function') return;
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = '/static/js/vendor/sql-wasm.js';
                script.onload = () => resolve();
                script.onerror = () => reject(new Error('Failed to load /static/js/vendor/sql-wasm.js'));
                document.head.appendChild(script);
            });
        }

        /**
         * Initializes SQLite WebAssembly engine and mounts in-memory database from IndexedDB.
         */
        async initBibleDatabase() {
            if (this.bibleDb) return this.bibleDb;

            await this.loadSqlScript();
            if (!this.sqlJs) {
                this.sqlJs = await window.initSqlJs({
                    locateFile: (file) => `/static/js/vendor/${file}`
                });
            }

            const bibleBuffer = await this.getStoreValue('bible_db');
            if (!bibleBuffer) throw new Error('Bible database not found in local offline storage.');

            this.bibleDb = new this.sqlJs.Database(new Uint8Array(bibleBuffer));
            console.log('[OfflineEngine] SQLite Wasm Bible Database successfully mounted in-memory!');
            return this.bibleDb;
        }

        async initSongsDatabase() {
            if (this.songsDb) return this.songsDb;

            await this.loadSqlScript();
            if (!this.sqlJs) {
                this.sqlJs = await window.initSqlJs({
                    locateFile: (file) => `/static/js/vendor/${file}`
                });
            }

            const songsBuffer = await this.getStoreValue('songs_db');
            if (!songsBuffer) throw new Error('Songs database not found in local offline storage.');

            this.songsDb = new this.sqlJs.Database(new Uint8Array(songsBuffer));
            console.log('[OfflineEngine] SQLite Wasm Songs Database successfully mounted in-memory!');
            return this.songsDb;
        }

        /**
         * Fetches verses for a given book and chapter from local SQLite Wasm.
         */
        async getChapterVerses(bookId, chapter, canon = 'protestant') {
            const db = await this.initBibleDatabase();
            const stmt = db.prepare(
                'SELECT verse, text_ta, text_en, text_ta_poc, text_en_drb FROM verses WHERE book_id = :b AND chapter = :c ORDER BY verse ASC'
            );
            stmt.bind({ ':b': Number(bookId), ':c': Number(chapter) });

            const verses = [];
            const isCatholic = String(canon).toLowerCase() === 'catholic';

            while (stmt.step()) {
                const row = stmt.getAsObject();
                const textTa = isCatholic && row.text_ta_poc ? row.text_ta_poc : row.text_ta;
                const textEn = isCatholic && row.text_en_drb ? row.text_en_drb : row.text_en;
                verses.push({
                    verse: row.verse,
                    verse_display: String(row.verse),
                    text_ta: textTa,
                    text_en: textEn
                });
            }
            stmt.free();
            return verses;
        }

        /**
         * Searches verses across scripture using SQLite full text / LIKE.
         */
        async searchVerses(query, canon = 'protestant', limit = 50) {
            const db = await this.initBibleDatabase();
            const clean = `%${String(query).trim()}%`;
            const isCatholic = String(canon).toLowerCase() === 'catholic';

            const sql = isCatholic
                ? 'SELECT book_id, chapter, verse, COALESCE(text_ta_poc, text_ta) AS text_ta, COALESCE(text_en_drb, text_en) AS text_en FROM verses WHERE text_ta LIKE :q OR text_en LIKE :q OR text_ta_poc LIKE :q LIMIT :lim'
                : 'SELECT book_id, chapter, verse, text_ta, text_en FROM verses WHERE (text_ta LIKE :q OR text_en LIKE :q) AND book_id <= 66 LIMIT :lim';

            const stmt = db.prepare(sql);
            stmt.bind({ ':q': clean, ':lim': limit });

            const results = [];
            while (stmt.step()) {
                results.push(stmt.getAsObject());
            }
            stmt.free();
            return results;
        }

        // ==========================================
        // 5. Offline Reader Auto-Hydration
        // ==========================================

        /**
         * Renders chapter verses directly into #reader-content when reading offline.
         */
        async renderChapterOffline(bookId, chapter, mode = 'bilingual', canon = 'protestant') {
            const container = document.getElementById('reader-content');
            if (!container) return;

            try {
                const verses = await this.getChapterVerses(bookId, chapter, canon);
                if (!verses || verses.length === 0) {
                    container.innerHTML = `
                        <div class="p-6 text-center text-stone-500 bg-stone-100 dark:bg-stone-800 rounded-2xl">
                            No verses found for Book ${bookId} Chapter ${chapter} in local offline database.
                        </div>`;
                    return;
                }

                let html = '';
                verses.forEach((v, idx) => {
                    html += `
                    <div id="v${v.verse}" class="verse-item group rounded-xl p-3.5 sm:p-4 hover:bg-white dark:hover:bg-stone-900 border border-transparent hover:border-stone-200 dark:hover:border-stone-800 transition duration-150 cursor-pointer"
                         onclick="handleVerseItemClick(${idx}, event)"
                         data-verse="${v.verse}"
                         data-verse-display="${v.verse_display || v.verse}"
                         data-text-ta="${escapeXml(v.text_ta)}"
                         data-text-en="${escapeXml(v.text_en)}">
                        
                        <div class="flex items-center justify-between text-xs text-stone-400 mb-1 select-none">
                            <span class="font-mono font-bold text-amber-700 dark:text-amber-400">${v.verse}</span>
                            <span class="text-[10px] text-stone-300 dark:text-stone-600 group-hover:text-amber-700 transition">Bookmark / Listen</span>
                        </div>

                        ${mode !== 'en' ? `<p class="verse-text-ta font-tamil text-stone-900 dark:text-stone-100 text-base sm:text-lg leading-relaxed mb-1.5">${escapeXml(v.text_ta)}</p>` : ''}
                        ${mode !== 'ta' ? `<p class="verse-text-en font-serif text-stone-600 dark:text-stone-300 text-sm sm:text-base leading-relaxed">${escapeXml(v.text_en)}</p>` : ''}
                    </div>`;
                });

                container.innerHTML = html;

                // Surface Offline Mode Indicator Pill in Reader Toolbar
                this.showOfflineToolbarBadge();

            } catch (err) {
                console.error('[OfflineEngine] renderChapterOffline failed:', err);
            }
        }

        showOfflineToolbarBadge() {
            const toolbar = document.getElementById('reader-toolbar');
            if (!toolbar || document.getElementById('offline-active-pill')) return;

            const pill = document.createElement('div');
            pill.id = 'offline-active-pill';
            pill.className = 'flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/70 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-[10px] font-bold shrink-0';
            pill.innerHTML = `<span>⚡</span> <span>Offline App Mode</span>`;
            toolbar.querySelector('.flex.items-center')?.appendChild(pill);
        }

        // ==========================================
        // 6. UI & Prompt Integration (Installed WebApp Only)
        // ==========================================

        /**
         * Checks installed status and prompts the user on first launch to download
         * the offline database so the webapp functions like a standalone native app.
         */
        async checkInstallStatusAndPrompt() {
            // STRICT INVARIANT: Only prompt if running in installed standalone mode
            if (!this.isAppInstalled()) return;

            const hasData = await this.hasOfflineData();
            if (hasData) {
                console.log('[OfflineEngine] Installed webapp has offline database ready.');
                return;
            }

            const dismissed = localStorage.getItem('bible_offline_prompt_dismissed');
            if (dismissed === 'true') return;

            this.renderInstallPromptBanner();
        }

        renderInstallPromptBanner() {
            if (document.getElementById('offline-download-banner')) return;

            const banner = document.createElement('div');
            banner.id = 'offline-download-banner';
            banner.className = 'fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:w-96 z-50 bg-stone-900/95 text-stone-100 border border-amber-500/50 rounded-2xl p-4 shadow-2xl backdrop-blur-md animate-slide-up space-y-3';
            banner.innerHTML = `
                <div class="flex items-start justify-between gap-2">
                    <div class="flex items-center gap-2">
                        <span class="text-xl">📲</span>
                        <div>
                            <h4 class="font-cinzel font-bold text-xs sm:text-sm text-amber-400">Offline App Mode Available</h4>
                            <p class="text-[11px] text-stone-300 leading-snug">Download the offline Bible & Hymns database (~15 MB) to read and search without internet.</p>
                        </div>
                    </div>
                    <button onclick="window.holyBibleOffline.dismissBanner()" class="text-stone-400 hover:text-stone-200 text-xs cursor-pointer">✕</button>
                </div>

                <div id="offline-banner-progress-box" class="hidden space-y-1">
                    <div class="w-full bg-stone-800 rounded-full h-2 overflow-hidden">
                        <div id="offline-banner-progress-bar" class="bg-amber-500 h-2 rounded-full transition-all duration-200" style="width: 0%"></div>
                    </div>
                    <p id="offline-banner-progress-text" class="text-[10px] text-stone-400 text-center font-mono">0%</p>
                </div>

                <div id="offline-banner-actions" class="flex items-center justify-end gap-2 pt-1 border-t border-stone-800">
                    <button onclick="window.holyBibleOffline.dismissBanner()" 
                            class="px-2.5 py-1 text-stone-400 hover:text-stone-200 text-xs cursor-pointer">
                        Not Now
                    </button>
                    <button onclick="window.holyBibleOffline.triggerBannerDownload()" 
                            class="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer">
                        Download (15 MB)
                    </button>
                </div>
            `;
            document.body.appendChild(banner);
        }

        dismissBanner() {
            const banner = document.getElementById('offline-download-banner');
            if (banner) banner.remove();
            localStorage.setItem('bible_offline_prompt_dismissed', 'true');
        }

        async triggerBannerDownload() {
            const actionsBox = document.getElementById('offline-banner-actions');
            const progressBox = document.getElementById('offline-banner-progress-box');
            const progressBar = document.getElementById('offline-banner-progress-bar');
            const progressText = document.getElementById('offline-banner-progress-text');

            if (actionsBox) actionsBox.classList.add('hidden');
            if (progressBox) progressBox.classList.remove('hidden');

            try {
                await this.downloadOfflineBundle(({ statusText, percent }) => {
                    if (progressBar && percent >= 0) progressBar.style.width = `${percent}%`;
                    if (progressText) progressText.innerText = `${statusText} (${percent}%)`;
                });

                if (window.showToast) window.showToast("Offline Bible & Hymns ready! 📖");
                setTimeout(() => this.dismissBanner(), 1500);
            } catch (err) {
                if (progressText) progressText.innerText = `Download failed: ${err.message}`;
                if (actionsBox) actionsBox.classList.remove('hidden');
            }
        }

        /**
         * Updates the Settings Modal with offline storage metrics and controls.
         */
        async updateSettingsUI() {
            const container = document.getElementById('offline-storage-settings-box');
            if (!container) return;

            if (this.isNativeDesktop()) {
                container.innerHTML = `
                    <div class="p-3 bg-stone-100 dark:bg-stone-800/80 rounded-xl border border-stone-200 dark:border-stone-700 text-xs text-stone-600 dark:text-stone-300 space-y-1">
                        <div class="flex items-center gap-1.5 font-bold text-stone-800 dark:text-stone-100">
                            <span>🖥️</span> <span>Native Windows Desktop App</span>
                        </div>
                        <p class="text-[11px] text-stone-500 dark:text-stone-400">
                            Running with embedded local SQLite databases (~58 MB) via memory-mapped I/O. 100% offline ready out of the box with zero download needed.
                        </p>
                    </div>`;
                return;
            }

            const isInstalled = this.isAppInstalled();
            const hasData = await this.hasOfflineData();
            const info = await this.getStorageInfo();

            if (!isInstalled) {
                container.innerHTML = `
                    <div class="p-3 bg-stone-100 dark:bg-stone-800/80 rounded-xl border border-stone-200 dark:border-stone-700 text-xs text-stone-600 dark:text-stone-300 space-y-1">
                        <div class="flex items-center gap-1.5 font-bold text-stone-800 dark:text-stone-100">
                            <span>📱</span> <span>Offline App Mode</span>
                        </div>
                        <p class="text-[11px] text-stone-500 dark:text-stone-400">
                            Install this webapp to your phone or desktop home screen to download the 15 MB database and read 100% offline.
                        </p>
                    </div>`;
                return;
            }

            if (hasData && info) {
                container.innerHTML = `
                    <div class="p-3 bg-emerald-50/60 dark:bg-emerald-950/30 rounded-xl border border-emerald-200 dark:border-emerald-800 text-xs space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-1">
                                <span>✅</span> <span>Offline Database Ready</span>
                            </span>
                            <span class="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 font-mono text-[10px] font-bold">
                                ${info.totalMb.toFixed(1)} MB
                            </span>
                        </div>
                        <p class="text-[11px] text-stone-600 dark:text-stone-300">
                            All 73 books and song lyrics are saved locally on your device. You can read, search, and navigate anywhere without internet.
                        </p>
                        <div class="flex items-center gap-2 pt-1">
                            <button onclick="window.holyBibleOffline.triggerSettingsDownload()" 
                                    class="px-2.5 py-1 bg-stone-200 dark:bg-stone-700 hover:bg-stone-300 dark:hover:bg-stone-600 text-stone-800 dark:text-stone-200 rounded-lg text-[11px] font-semibold transition cursor-pointer">
                                🔄 Update Data
                            </button>
                            <button onclick="window.holyBibleOffline.triggerClearStorage()" 
                                    class="px-2.5 py-1 text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg text-[11px] font-semibold transition cursor-pointer">
                                🗑️ Clear Storage
                            </button>
                        </div>
                    </div>`;
            } else {
                container.innerHTML = `
                    <div class="p-3 bg-amber-50/60 dark:bg-amber-950/30 rounded-xl border border-amber-200 dark:border-amber-800 text-xs space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-amber-800 dark:text-amber-300 flex items-center gap-1">
                                <span>📲</span> <span>Offline Database Not Downloaded</span>
                            </span>
                        </div>
                        <p class="text-[11px] text-stone-600 dark:text-stone-300">
                            Download the full Bible and Songbook (~15 MB) to enable instant offline reading without network.
                        </p>
                        <button onclick="window.holyBibleOffline.triggerSettingsDownload()" 
                                class="w-full py-1.5 bg-amber-700 hover:bg-amber-800 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer shadow-xs">
                            <span>📥</span> <span>Download Offline Database (15 MB)</span>
                        </button>
                    </div>`;
            }
        }

        async triggerSettingsDownload() {
            const container = document.getElementById('offline-storage-settings-box');
            if (container) {
                container.innerHTML = `
                    <div class="p-3 bg-stone-100 dark:bg-stone-800 rounded-xl border border-stone-200 dark:border-stone-700 text-xs space-y-2">
                        <p id="settings-download-status" class="font-bold text-amber-700 dark:text-amber-400">Downloading offline bundle...</p>
                        <div class="w-full bg-stone-200 dark:bg-stone-700 rounded-full h-2 overflow-hidden">
                            <div id="settings-download-progress-bar" class="bg-amber-600 h-2 rounded-full transition-all duration-200" style="width: 5%"></div>
                        </div>
                    </div>`;
            }

            try {
                await this.downloadOfflineBundle(({ statusText, percent }) => {
                    const statusElem = document.getElementById('settings-download-status');
                    const barElem = document.getElementById('settings-download-progress-bar');
                    if (statusElem) statusElem.innerText = `${statusText} (${percent}%)`;
                    if (barElem && percent >= 0) barElem.style.width = `${percent}%`;
                });
                if (window.showToast) window.showToast("Offline bundle updated successfully! 📱");
            } catch (err) {
                if (window.showToast) window.showToast(`Download failed: ${err.message}`);
                this.updateSettingsUI();
            }
        }

        async triggerClearStorage() {
            if (!confirm("Are you sure you want to remove the offline Bible and Song database from this device?")) return;
            await this.clearAll();
            localStorage.removeItem('bible_offline_prompt_dismissed');
            if (window.showToast) window.showToast("Offline database cleared.");
            this.updateSettingsUI();
        }
    }

    function escapeXml(unsafe) {
        if (!unsafe) return '';
        return unsafe.replace(/[<>&'"]/g, (c) => {
            switch (c) {
                case '<': return '&lt;';
                case '>': return '&gt;';
                case '&': return '&amp;';
                case '\'': return '&apos;';
                case '"': return '&quot;';
            }
        });
    }

    // Expose singleton instance on window
    const engine = new HolyBibleOfflineEngine();
    window.HolyBibleOffline = HolyBibleOfflineEngine;
    window.holyBibleOffline = engine;

    // Hook DOMContentLoaded and appinstalled
    document.addEventListener('DOMContentLoaded', () => {
        engine.checkInstallStatusAndPrompt();
        engine.updateSettingsUI();
    });

    window.addEventListener('appinstalled', () => {
        console.log('[OfflineEngine] appinstalled event caught.');
        engine.checkInstallStatusAndPrompt();
        engine.updateSettingsUI();
    });

})(window);
