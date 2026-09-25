class BibleContinuousAudio {
    constructor() {
        this.audio = new Audio();
        this.isPlaying = false;
        this.isPaused = false;
        this.currentIndex = 0;
        this.verses = [];
        this.lang = 'ta';
        this.rate = 1.0;
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

            const langEl = document.getElementById('audio-lang-select');
            const rateEl = document.getElementById('audio-rate-select');
            if (langEl) langEl.value = this.lang;
            if (rateEl) rateEl.value = this.rate;

            setTimeout(() => this.play(0), 400);
        }

        this.syncDockVoiceOptions();
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

        const voice = this.getEffectiveVoice();
        const audioUrl = `/api/audio/stream?lang=${encodeURIComponent(this.lang)}&text=${encodeURIComponent(text)}&voice=${encodeURIComponent(voice)}&rate=${encodeURIComponent(this.rate)}`;
        
        this.audio.src = audioUrl;
        this.audio.playbackRate = parseFloat(this.rate);
        
        this.audio.play().then(() => {
            this.setPlayPauseIcon(true);
        }).catch(err => {
            console.warn("Autoplay block or delay:", err);
            this.setPlayPauseIcon(false);
        });
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
        this.audio.pause();
        this.audio.currentTime = 0;
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
                rate: this.rate
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
        if (this.isPlaying) this.playCurrent();
    }

    syncDockVoiceOptions() {
        const voiceSelect = document.getElementById('audio-voice-select');
        if (!voiceSelect) return;
        if (this.lang === 'ta') {
            voiceSelect.innerHTML = `
                <option value="ta-IN-ValluvarNeural">வள்ளுவர் (Male)</option>
                <option value="ta-IN-PallaviNeural">பல்லவி (Female)</option>
            `;
            voiceSelect.value = localStorage.getItem('bible_audio_voice_ta') || 'ta-IN-ValluvarNeural';
        } else {
            voiceSelect.innerHTML = `
                <option value="en-US-JennyNeural">Jenny (Female)</option>
                <option value="en-US-GuyNeural">Guy (Male)</option>
                <option value="en-IN-NeerjaNeural">Neerja (India)</option>
            `;
            voiceSelect.value = localStorage.getItem('bible_audio_voice_en') || 'en-US-JennyNeural';
        }
    }

    setRate(rate) {
        this.rate = rate;
        this.audio.playbackRate = parseFloat(rate);
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