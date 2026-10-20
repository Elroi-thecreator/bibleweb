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
        this.downloadedVerses = new Set();
        this.prefetchRetryLimit = 3;
        this.isPaused = false;
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

    init(bookId, chapter, nextChapter, mode) {
        this.bookId = bookId;
        this.chapter = chapter;
        this.nextChapter = nextChapter;
        this.mode = mode;

        const items = document.querySelectorAll('.verse-item');
        this.verses = Array.from(items).map((el, idx) => ({
            index: idx,
            verse: el.id.replace('v', ''),
            verseDisplay: el.dataset.verseDisplay || el.id.replace('v', ''),
            element: el,
            textEn: el.querySelector('.verse-text-en')?.innerText.trim() || '',
            textTa: el.querySelector('.verse-text-ta')?.innerText.trim() || ''
        }));

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
        this.prefetchQueue = [];
        this.downloadedVerses.clear();
        this.isPrefetching = false;
    }

    play(fromIndex = 0) {
        this.isPlaying = true;
        this.isPaused = false;
        this.currentIndex = fromIndex;
        this.showDock();
        this.playCurrent();
    }

    playCurrent() {
        if (!this.isPlaying) return;

        if (this.currentIndex >= this.verses.length) {
            this.onChapterComplete();
            return;
        }

        const v = this.verses[this.currentIndex];
        this.spotlightVerse(v);

        let text = (this.lang === 'ta') ? v.textTa : v.textEn;
        if (!text && this.lang === 'ta') text = v.textEn;

        // Strip anything inside [] or {} (verse numbers, editorial brackets)
        text = (text || '').replace(/\[[\s\S]*?\]/g, '').replace(/\{[\s\S]*?\}/g, '').replace(/\s+/g, ' ').trim();

        const voice = this.getEffectiveVoice();
        const pitch = this.getEffectivePitch();
        const audioUrl = `/api/audio/stream?lang=${encodeURIComponent(this.lang)}&text=${encodeURIComponent(text)}&voice=${encodeURIComponent(voice)}&rate=${encodeURIComponent(this.rate)}&pitch=${encodeURIComponent(pitch)}`;
        
        this.audio.src = audioUrl;
        this.audio.playbackRate = parseFloat(this.rate);
        
        this.audio.play().then(() => {
            this.setPlayPauseIcon(true);
            this.startChapterPrefetchPipeline();
        }).catch(err => {
            console.warn("Autoplay block or delay:", err);
            this.setPlayPauseIcon(false);
        });
    }

    startChapterPrefetchPipeline() {
        if (!this.isPlaying && !this.isPaused) return;

        // Build queue of all upcoming verses to the end of the chapter
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

            // Guard against chapter boundaries
            if (nextIndex >= this.verses.length) continue;

            const nextV = this.verses[nextIndex];
            if (!nextV) continue;

            let text = (this.lang === 'ta') ? nextV.textTa : nextV.textEn;
            if (!text && this.lang === 'ta') text = nextV.textEn;

            // Strip editorial bracket markers [...] and {...}
            text = (text || '').replace(/\[[\s\S]*?\]/g, '').replace(/\{[\s\S]*?\}/g, '').replace(/\s+/g, ' ').trim();
            if (!text) continue;

            const voice = this.getEffectiveVoice();
            const rate = this.rate;
            const pitch = this.getEffectivePitch();
            const verseCacheKey = `${this.bookId}_${this.chapter}_${nextIndex}_${this.lang}_${voice}_${rate}_${pitch}`;

            // Skip if already confirmed downloaded
            if (this.downloadedVerses.has(verseCacheKey)) {
                continue;
            }

            const streamUrl = `/api/audio/stream?lang=${encodeURIComponent(this.lang)}&text=${encodeURIComponent(text)}&voice=${encodeURIComponent(voice)}&rate=${encodeURIComponent(rate)}&pitch=${encodeURIComponent(pitch)}`;

            // Automated download with verification & retry
            let confirmed = false;
            for (let attempt = 1; attempt <= this.prefetchRetryLimit; attempt++) {
                if (!this.isPlaying && !this.isPaused) break;

                try {
                    const res = await fetch(streamUrl, {
                        method: 'GET',
                        priority: 'low',
                        headers: { 'Accept': 'audio/mpeg' }
                    });

                    if (res.ok) {
                        const contentType = res.headers.get('content-type') || '';
                        const blob = await res.blob();
                        if (blob && blob.size > 0 && (contentType.includes('audio') || res.status === 200)) {
                            confirmed = true;
                            this.downloadedVerses.add(verseCacheKey);

                            // Prime preloader element if this is the immediate next verse
                            if (nextIndex === this.currentIndex + 1 && this.preloader) {
                                this.preloader.src = streamUrl;
                                this.preloader.preload = 'auto';
                                this.preloader.load();
                            }
                            break;
                        }
                    }
                    console.warn(`[Audio Pipeline] Verse ${nextV.verseDisplay || nextV.verse} attempt ${attempt} returned HTTP ${res.status}. Retrying...`);
                } catch (err) {
                    console.warn(`[Audio Pipeline] Verse ${nextV.verseDisplay || nextV.verse} attempt ${attempt} network error:`, err);
                }

                if (!confirmed && attempt < this.prefetchRetryLimit && (this.isPlaying || this.isPaused)) {
                    await new Promise(r => setTimeout(r, attempt * 500));
                }
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
        this.downloadedVerses.clear();
        this.prefetchQueue = [];
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
        this.downloadedVerses.clear();
        this.prefetchQueue = [];
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
        }
    }

    resume() {
        if (this.isPlaying && this.isPaused) {
            this.audio.play();
            this.isPaused = false;
            this.setPlayPauseIcon(true);
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

        document.querySelectorAll('.verse-item').forEach(el => {
            el.classList.remove('ring-2', 'ring-amber-500', 'bg-amber-50/70', 'dark:bg-amber-950/40');
        });
        this.hideDock();
    }

    next() {
        if (this.currentIndex < this.verses.length - 1) {
            this.currentIndex++;
            this.playCurrent();
        } else {
            this.onChapterComplete();
        }
    }

    prev() {
        if (this.currentIndex > 0) {
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
        this.downloadedVerses.clear();
        this.prefetchQueue = [];
        if (this.isPlaying) this.playCurrent();
    }

    syncDockVoiceOptions() {
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
    }

    setRate(rate) {
        this.rate = rate;
        this.audio.playbackRate = parseFloat(rate);
        this.downloadedVerses.clear();
        this.prefetchQueue = [];
        if (this.isPlaying) {
            this.startChapterPrefetchPipeline();
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