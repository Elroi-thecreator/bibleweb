class BibleContinuousAudio {
    constructor() {
        this.audio = new Audio();
        this.preloader = new Audio();
        this.preloader.muted = true;
        this.preloader.volume = 0;
        this.isPlaying = false;
        this.isPaused = false;
        this.prefetchQueue = [];
        this.isPrefetching = false;

        // In-memory Audio Blob & Status Store to prevent duplicate/multiple downloads
        this.verseAudioBlobs = new Map(); // cacheKey -> { blob: Blob, blobUrl: string, size: number, timestamp: number }
        this.inFlightRequests = new Map(); // cacheKey -> Promise<string> (resolves to blobUrl)
        this.verseStatuses = new Map();    // index -> 'idle' | 'downloading' | 'downloaded' | 'playing' | 'error'

        this.prefetchRetryLimit = 3;
        this.currentIndex = 0;
        this.verses = [];
        this.lang = 'ta';
        this.rate = 1.0;
        this.pitch = localStorage.getItem('bible_audio_pitch') || '+0Hz';
        this.bookId = null;
        this.chapter = null;
        this.nextChapter = null;
        this.mode = 'bilingual';

        this.setupAudioListeners();
    }

    setupAudioListeners() {
        this.audio.addEventListener('ended', () => {
            if (this.isPlaying && !this.isPaused) {
                // Keep completed verse marked as downloaded
                if (this.verseAudioBlobs.has(this.getVerseCacheKey(this.currentIndex))) {
                    this.updateVerseStatusUI(this.currentIndex, 'downloaded');
                }
                this.currentIndex++;
                this.playCurrent();
            }
        });

        this.audio.addEventListener('error', (e) => {
            console.error("Audio stream playback issue:", e);
            if (this.isPlaying && !this.isPaused) {
                setTimeout(() => {
                    this.currentIndex++;
                    this.playCurrent();
                }, 1000);
            }
        });
    }

    getVerseCacheKey(index) {
        const voice = this.getEffectiveVoice();
        const rate = this.rate;
        const pitch = this.getEffectivePitch();
        return `${this.bookId}_${this.chapter}_${index}_${this.lang}_${voice}_${rate}_${pitch}`;
    }

    updateVerseStatusUI(index, status) {
        if (index < 0 || index >= this.verses.length) return;
        this.verseStatuses.set(index, status);

        const el = document.getElementById(`verse-audio-status-${index}`);
        const playBtn = document.getElementById(`verse-play-btn-${index}`);

        if (playBtn) {
            if (status === 'playing') {
                playBtn.innerHTML = '⏸';
                playBtn.classList.add('text-amber-600', 'font-bold');
                playBtn.title = `Pause verse ${this.verses[index]?.verseDisplay || index + 1}`;
            } else {
                playBtn.innerHTML = '▶';
                playBtn.classList.remove('text-amber-600', 'font-bold');
                playBtn.title = `Listen from verse ${this.verses[index]?.verseDisplay || index + 1}`;
            }
        }

        if (!el) return;

        switch (status) {
            case 'downloading':
                el.innerHTML = `
                    <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-amber-100/90 dark:bg-amber-950/70 text-amber-800 dark:text-amber-300 text-[9px] font-semibold border border-amber-300/80 dark:border-amber-700/80 animate-pulse shadow-xs" title="Downloading verse audio / ஆடியோ பதிவிறங்குகிறது...">
                        <svg class="w-2.5 h-2.5 animate-spin text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                        <span class="hidden sm:inline">Downloading</span>
                    </span>
                `;
                break;
            case 'downloaded':
                el.innerHTML = `
                    <span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 text-[9px] font-medium border border-emerald-200/80 dark:border-emerald-800/60 cursor-pointer hover:bg-emerald-100 dark:hover:bg-emerald-900/60 transition shadow-xs" title="Audio downloaded & ready in memory (zero network lag)">
                        <svg class="w-2.5 h-2.5 text-emerald-600 dark:text-emerald-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                        <span class="hidden sm:inline">Ready</span>
                    </span>
                `;
                break;
            case 'playing':
                el.innerHTML = `
                    <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-amber-600 text-white text-[9px] font-bold shadow-xs animate-pulse" title="Playing verse audio / வாசிக்கப்படுகிறது">
                        <span class="text-[10px]">🔊</span>
                        <span class="hidden sm:inline">Playing</span>
                    </span>
                `;
                break;
            case 'error':
                el.innerHTML = `
                    <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 text-[9px] border border-rose-200 dark:border-rose-900/50 cursor-pointer" title="Audio download issue. Tap to retry.">
                        <span>⚠️ Retry</span>
                    </span>
                `;
                break;
            case 'idle':
            default:
                el.innerHTML = '';
                break;
        }
    }

    clearAllBlobs() {
        if (this.audio) {
            try { this.audio.pause(); } catch (_) {}
        }
        for (const record of this.verseAudioBlobs.values()) {
            if (record && record.blobUrl) {
                try { URL.revokeObjectURL(record.blobUrl); } catch (_) {}
            }
        }
        this.verseAudioBlobs.clear();
        this.inFlightRequests.clear();
        this.prefetchQueue = [];
        this.isPrefetching = false;
        if (this.verses && this.verses.length > 0) {
            this.verses.forEach((_, idx) => this.updateVerseStatusUI(idx, 'idle'));
        }
    }

    init(bookId, chapter, nextChapter, mode) {
        this.bookId = bookId;
        this.chapter = chapter;
        this.nextChapter = nextChapter;
        this.mode = mode;

        if (this.mode === 'en') {
            this.lang = 'en';
        } else if (this.mode === 'ta') {
            this.lang = 'ta';
        }

        const items = document.querySelectorAll('.verse-item');
        this.verses = Array.from(items).map((el, idx) => ({
            index: idx,
            verse: el.id.replace('v', ''),
            verseDisplay: el.dataset.verseDisplay || el.id.replace('v', ''),
            element: el,
            textEn: el.querySelector('.verse-text-en')?.innerText.trim() || '',
            textTa: el.querySelector('.verse-text-ta')?.innerText.trim() || ''
        }));

        this.clearAllBlobs();
        document.querySelectorAll('.verse-audio-status-pill').forEach(el => el.innerHTML = '');

        const savedState = sessionStorage.getItem('bible_autoplay_state');
        if (savedState) {
            const state = JSON.parse(savedState);
            sessionStorage.removeItem('bible_autoplay_state');
            this.lang = state.lang || 'ta';
            this.rate = state.rate || 1.0;
            this.pitch = state.pitch || localStorage.getItem('bible_audio_pitch') || '+0Hz';

            const langEl = document.getElementById('audio-lang-select');
            const rateEl = document.getElementById('audio-rate-select');
            const pitchEl = document.getElementById('audio-pitch-select');
            if (langEl) langEl.value = this.lang;
            if (rateEl) rateEl.value = this.rate;
            if (pitchEl) pitchEl.value = this.pitch;

            setTimeout(() => this.play(0), 400);
        }

        this.syncDockVoiceOptions();
    }

    async ensureVerseAudioDownloaded(index) {
        if (index < 0 || index >= this.verses.length) return null;
        const v = this.verses[index];
        if (!v) return null;

        const cacheKey = this.getVerseCacheKey(index);

        // 1. Check whether verse is ALREADY downloaded
        if (this.verseAudioBlobs.has(cacheKey)) {
            console.log(`[Audio Pipeline] Verse ${v.verseDisplay || v.verse} is ALREADY DOWNLOADED in memory blob cache. Reusing local audio.`);
            if (this.currentIndex === index && this.isPlaying && !this.isPaused) {
                this.updateVerseStatusUI(index, 'playing');
            } else {
                this.updateVerseStatusUI(index, 'downloaded');
            }
            return this.verseAudioBlobs.get(cacheKey).blobUrl;
        }

        // 2. Check whether verse download is ALREADY IN-FLIGHT (prevents duplicate requests)
        if (this.inFlightRequests.has(cacheKey)) {
            console.log(`[Audio Pipeline] Verse ${v.verseDisplay || v.verse} is ALREADY IN-FLIGHT. Awaiting existing download.`);
            return this.inFlightRequests.get(cacheKey);
        }

        // 3. Update status to downloading on this verse ONLY
        this.updateVerseStatusUI(index, 'downloading');

        const downloadPromise = (async () => {
            try {
                let text = (this.lang === 'ta') ? v.textTa : v.textEn;
                if (!text && this.lang === 'ta') text = v.textEn;

                // Strip editorial bracket markers [...] and {...}
                text = (text || '').replace(/\[[\s\S]*?\]/g, '').replace(/\{[\s\S]*?\}/g, '').replace(/\s+/g, ' ').trim();
                if (!text) {
                    this.updateVerseStatusUI(index, 'idle');
                    return null;
                }

                const voice = this.getEffectiveVoice();
                const rate = this.rate;
                const pitch = this.getEffectivePitch();
                const streamUrl = `/api/audio/stream?lang=${encodeURIComponent(this.lang)}&text=${encodeURIComponent(text)}&voice=${encodeURIComponent(voice)}&rate=${encodeURIComponent(rate)}&pitch=${encodeURIComponent(pitch)}`;

                let confirmedBlob = null;
                for (let attempt = 1; attempt <= this.prefetchRetryLimit; attempt++) {
                    try {
                        const res = await fetch(streamUrl, {
                            method: 'GET',
                            headers: { 'Accept': 'audio/mpeg' }
                        });

                        if (res.ok) {
                            const contentType = res.headers.get('content-type') || '';
                            const blob = await res.blob();
                            if (blob && blob.size > 0 && (contentType.includes('audio') || res.status === 200)) {
                                confirmedBlob = blob;
                                break;
                            }
                        }
                        console.warn(`[Audio Pipeline] Verse ${v.verseDisplay || v.verse} attempt ${attempt} returned HTTP ${res.status}. Retrying...`);
                    } catch (err) {
                        console.warn(`[Audio Pipeline] Verse ${v.verseDisplay || v.verse} attempt ${attempt} network error:`, err);
                    }

                    if (!confirmedBlob && attempt < this.prefetchRetryLimit) {
                        await new Promise(r => setTimeout(r, attempt * 400));
                    }
                }

                if (!confirmedBlob) {
                    this.updateVerseStatusUI(index, 'error');
                    return null;
                }

                // Store blob & create object URL
                const blobUrl = URL.createObjectURL(confirmedBlob);
                this.verseAudioBlobs.set(cacheKey, {
                    blob: confirmedBlob,
                    blobUrl: blobUrl,
                    size: confirmedBlob.size,
                    timestamp: Date.now()
                });

                if (this.currentIndex === index && this.isPlaying && !this.isPaused) {
                    this.updateVerseStatusUI(index, 'playing');
                } else {
                    this.updateVerseStatusUI(index, 'downloaded');
                }

                return blobUrl;
            } finally {
                this.inFlightRequests.delete(cacheKey);
            }
        })();

        this.inFlightRequests.set(cacheKey, downloadPromise);
        return downloadPromise;
    }

    togglePlayPause() {
        if (!this.isPlaying) {
            this.play(this.currentIndex || 0);
        } else if (this.isPaused) {
            this.resume();
        } else {
            this.pause();
        }
    }

    async play(fromIndex = 0) {
        if (this.currentIndex === fromIndex && this.isPlaying) {
            if (this.isPaused) {
                this.resume();
            } else {
                this.pause();
            }
            return;
        }

        // Revert previous verse status to 'downloaded' if cached, or 'idle'
        if (this.currentIndex !== fromIndex) {
            if (this.verseAudioBlobs.has(this.getVerseCacheKey(this.currentIndex))) {
                this.updateVerseStatusUI(this.currentIndex, 'downloaded');
            } else {
                this.updateVerseStatusUI(this.currentIndex, 'idle');
            }
        }

        this.isPlaying = true;
        this.isPaused = false;
        this.currentIndex = fromIndex;
        this.showDock();
        await this.playCurrent();
    }

    async playCurrent() {
        if (!this.isPlaying) return;

        if (this.currentIndex >= this.verses.length) {
            this.onChapterComplete();
            return;
        }

        const requestedIndex = this.currentIndex;
        const v = this.verses[requestedIndex];
        if (!v) return;
        this.spotlightVerse(v);

        // Fetch or get from cache (checks if already downloaded, never duplicates)
        const blobUrl = await this.ensureVerseAudioDownloaded(requestedIndex);
        if (!blobUrl || !this.isPlaying || this.currentIndex !== requestedIndex) return;

        this.audio.src = blobUrl;
        this.audio.playbackRate = parseFloat(this.rate);

        this.audio.play().then(() => {
            if (this.currentIndex !== requestedIndex || !this.isPlaying) return;
            this.setPlayPauseIcon(true);
            this.updateVerseStatusUI(requestedIndex, 'playing');
            this.startChapterPrefetchPipeline();
        }).catch(err => {
            console.warn("Autoplay block or delay:", err);
            this.setPlayPauseIcon(false);
        });
    }

    startChapterPrefetchPipeline() {
        if (!this.isPlaying && !this.isPaused) return;

        const upcoming = [];
        for (let i = this.currentIndex + 1; i < this.verses.length; i++) {
            upcoming.push(i);
        }

        this.prefetchQueue = upcoming;

        if (!this.isPrefetching) {
            this.processPrefetchQueue();
        }
    }

    async processPrefetchQueue() {
        if (this.isPrefetching) return;
        this.isPrefetching = true;

        while (this.prefetchQueue.length > 0 && (this.isPlaying || this.isPaused)) {
            const nextIndex = this.prefetchQueue.shift();

            if (nextIndex >= this.verses.length) continue;

            const cacheKey = this.getVerseCacheKey(nextIndex);
            if (this.verseAudioBlobs.has(cacheKey)) {
                // Already downloaded, ensure UI reflects it and skip network request
                this.updateVerseStatusUI(nextIndex, 'downloaded');
                continue;
            }

            // Download using unified deduplicating pipeline
            const blobUrl = await this.ensureVerseAudioDownloaded(nextIndex);

            // Prime preloader element if this is the immediate next verse
            if (blobUrl && nextIndex === this.currentIndex + 1 && this.preloader) {
                this.preloader.src = blobUrl;
                this.preloader.preload = 'auto';
                this.preloader.load();
            }

            // Brief pacing delay between downloads
            await new Promise(r => setTimeout(r, 60));
        }

        this.isPrefetching = false;
    }

    getEffectiveVoice() {
        if (this.lang === 'ta') {
            return localStorage.getItem('bible_audio_voice_ta') || 'ta-IN-ValluvarNeural';
        }
        return localStorage.getItem('bible_audio_voice_en') || 'en-US-JennyNeural';
    }

    setVoice(voiceName) {
        if (this.lang === 'ta') {
            localStorage.setItem('bible_audio_voice_ta', voiceName);
        } else {
            localStorage.setItem('bible_audio_voice_en', voiceName);
        }
        this.clearAllBlobs();
        if (this.isPlaying) this.playCurrent();
    }

    getEffectivePitch() {
        return this.pitch || localStorage.getItem('bible_audio_pitch') || '+0Hz';
    }

    setPitch(pitchValue) {
        this.pitch = pitchValue;
        localStorage.setItem('bible_audio_pitch', pitchValue);
        const pitchSelect = document.getElementById('audio-pitch-select');
        if (pitchSelect && pitchSelect.value !== pitchValue) {
            pitchSelect.value = pitchValue;
        }
        const settingPitch = document.getElementById('setting-audio-pitch');
        if (settingPitch && settingPitch.value !== pitchValue) {
            settingPitch.value = pitchValue;
        }
        this.clearAllBlobs();
        if (this.isPlaying) this.playCurrent();
    }

    spotlightVerse(v) {
        document.querySelectorAll('.verse-item').forEach(el => {
            el.classList.remove('ring-2', 'ring-amber-500', 'bg-amber-50/70', 'dark:bg-amber-950/40');
        });
        v.element.classList.add('ring-2', 'ring-amber-500', 'bg-amber-50/70', 'dark:bg-amber-950/40');
        v.element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        const label = document.getElementById('audio-verse-label');
        if (label) label.innerText = `Verse ${v.verseDisplay || v.verse}`;
    }

    pause() {
        if (this.isPlaying && !this.isPaused) {
            this.audio.pause();
            this.isPaused = true;
            this.setPlayPauseIcon(false);
            if (this.verses[this.currentIndex]) {
                const playBtn = document.getElementById(`verse-play-btn-${this.currentIndex}`);
                if (playBtn) playBtn.innerHTML = '▶';
                if (this.verseAudioBlobs.has(this.getVerseCacheKey(this.currentIndex))) {
                    this.updateVerseStatusUI(this.currentIndex, 'downloaded');
                }
            }
        }
    }

    resume() {
        if (this.isPlaying && this.isPaused) {
            this.audio.play().then(() => {
                this.isPaused = false;
                this.setPlayPauseIcon(true);
                this.updateVerseStatusUI(this.currentIndex, 'playing');
            }).catch(e => console.warn(e));
        } else {
            this.play(this.currentIndex);
        }
    }

    stop() {
        this.isPlaying = false;
        this.isPaused = false;
        this.prefetchQueue = [];
        this.isPrefetching = false;
        this.audio.pause();
        this.audio.currentTime = 0;
        if (this.preloader) {
            this.preloader.pause();
            this.preloader.removeAttribute('src');
            this.preloader.load();
        }
        sessionStorage.removeItem('bible_autoplay_state');

        // Mark previously playing verse back to downloaded if in cache
        if (this.currentIndex >= 0 && this.currentIndex < this.verses.length) {
            if (this.verseAudioBlobs.has(this.getVerseCacheKey(this.currentIndex))) {
                this.updateVerseStatusUI(this.currentIndex, 'downloaded');
            } else {
                this.updateVerseStatusUI(this.currentIndex, 'idle');
            }
        }

        document.querySelectorAll('.verse-item').forEach(el => {
            el.classList.remove('ring-2', 'ring-amber-500', 'bg-amber-50/70', 'dark:bg-amber-950/40');
        });
        this.setPlayPauseIcon(false);
        this.hideDock();
    }

    next() {
        this.isPlaying = true;
        this.isPaused = false;
        if (this.currentIndex < this.verses.length - 1) {
            if (this.verseAudioBlobs.has(this.getVerseCacheKey(this.currentIndex))) {
                this.updateVerseStatusUI(this.currentIndex, 'downloaded');
            }
            this.currentIndex++;
            this.playCurrent();
        } else {
            this.onChapterComplete();
        }
    }

    prev() {
        this.isPlaying = true;
        this.isPaused = false;
        if (this.currentIndex > 0) {
            if (this.verseAudioBlobs.has(this.getVerseCacheKey(this.currentIndex))) {
                this.updateVerseStatusUI(this.currentIndex, 'downloaded');
            }
            this.currentIndex--;
            this.playCurrent();
        }
    }

    onChapterComplete() {
        if (typeof markChapterAsReadDirect === 'function') {
            markChapterAsReadDirect(this.bookId, this.chapter);
        }

        if (this.nextChapter) {
            sessionStorage.setItem('bible_autoplay_state', JSON.stringify({
                lang: this.lang,
                rate: this.rate,
                pitch: this.getEffectivePitch()
            }));
            window.location.href = `/read/${this.bookId}/${this.nextChapter}?mode=${this.mode}`;
        } else {
            this.stop();
            showToast("Reached the end of this book!");
        }
    }

    setLanguage(lang) {
        this.lang = lang;
        this.syncDockVoiceOptions();
        this.clearAllBlobs();
        if (this.isPlaying) this.playCurrent();
    }

    syncDockVoiceOptions() {
        const langSelect = document.getElementById('audio-lang-select');
        if (langSelect && langSelect.value !== this.lang) {
            langSelect.value = this.lang;
        }

        const voiceSelect = document.getElementById('audio-voice-select');
        if (voiceSelect) {
            if (this.lang === 'ta') {
                voiceSelect.innerHTML = `
                    <option value="ta-IN-ValluvarNeural">வள்ளுவர் (Male - IN)</option>
                    <option value="ta-LK-KumarNeural">குமார் (Deep Bass Male - LK)</option>
                    <option value="ta-SG-AnbuNeural">அன்பு (Male - SG)</option>
                    <option value="ta-MY-SuryaNeural">சூர்யா (Male - MY)</option>
                    <option value="ta-IN-PallaviNeural">பல்லவி (Female - IN)</option>
                `;
                voiceSelect.value = localStorage.getItem('bible_audio_voice_ta') || 'ta-IN-ValluvarNeural';
            } else {
                voiceSelect.innerHTML = `
                    <option value="en-US-ChristopherNeural">Christopher (Deep Bass Male)</option>
                    <option value="en-US-BrianNeural">Brian (Resonant Male)</option>
                    <option value="en-US-GuyNeural">Guy (Male)</option>
                    <option value="en-US-JennyNeural">Jenny (Female)</option>
                    <option value="en-IN-NeerjaNeural">Neerja (India)</option>
                `;
                voiceSelect.value = localStorage.getItem('bible_audio_voice_en') || 'en-US-JennyNeural';
            }
        }

        const pitchSelect = document.getElementById('audio-pitch-select');
        if (pitchSelect) {
            pitchSelect.value = this.getEffectivePitch();
        }

        const rateSelect = document.getElementById('audio-rate-select');
        if (rateSelect) {
            rateSelect.value = String(this.rate);
        }
    }

    setRate(rate) {
        this.rate = rate;
        this.audio.playbackRate = parseFloat(rate);
        this.clearAllBlobs();
        if (this.isPlaying) {
            this.playCurrent();
        }
    }

    showDock() {
        document.getElementById('audio-dock')?.classList.remove('translate-y-full');
    }

    hideDock() {
        document.getElementById('audio-dock')?.classList.add('translate-y-full');
    }

    setPlayPauseIcon(playing) {
        const btn = document.getElementById('audio-play-pause-btn');
        if (btn) btn.innerHTML = playing ? '⏸' : '▶';
    }
}

window.bibleAudio = new BibleContinuousAudio();


// Global keyboard shortcut: Spacebar toggles Audio Bible Play/Pause (when not inside inputs)
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
        if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select' || document.activeElement?.isContentEditable) {
            return;
        }
        if (window.bibleAudio && (window.bibleAudio.isPlaying || window.bibleAudio.isPaused)) {
            e.preventDefault();
            window.bibleAudio.togglePlayPause();
        }
    }
});
