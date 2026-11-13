# 📖 Holy Bible — Project Bible & Codebase Cartography
**System Identifier:** `HolyBible` | **WinGet ID:** `ElroiTheCreator.HolyBible` | **Repository:** [`Elroi-thecreator/bibleweb`](https://github.com/Elroi-thecreator/bibleweb)  
**Document Classification:** Master Product & System Specification | **Version:** 2.0.0 | **Status:** Active / Approved  
**Last Synchronized:** 2026-11-13 | **Master Knowledge Graph:** [`knowledge/index.yaml`](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/index.yaml) (27 Knowledge Units)

---

## 1. Executive Summary & Product DNA

### 1.1 Vision & Mission Statement
**Holy Bible — வேதம்** is a high-performance, offline-first bilingual (Tamil & English) Holy Bible web platform and native Windows desktop application. Designed for individual believers, church congregations, biblical scholars, and worship ministers, the system combines dual-canon scripture reading, 100-day audio read-along plans, church presentation projection, Christian hymnals, AI-powered exegesis, and automated WhatsApp devotional broadcasts into a single, cohesive, zero-cost operational architecture.

### 1.2 Core Pillars & Strategic Invariants

```
+-------------------------------------------------------------------------------------------------+
|                                     HOLY BIBLE CORE PILLARS                                     |
+--------------------------------+-------------------------------+--------------------------------+
|        OFFLINE-FIRST           |          DUAL-CANON           |       DUAL-PLATFORM            |
| Embedded SQLite databases      | Full Catholic 73-book canon   | Single FastAPI codebase        |
| with memory-mapped I/O & FTS5  | (Deuterocanon) alongside      | serves both public web and     |
| indexing; zero cloud database  | Protestant 66-book canon with | native Windows PyWebView       |
| latency or connectivity limits.| complete bilingual parity.    | desktop executable.            |
+--------------------------------+-------------------------------+--------------------------------+
|        AUDIO-INTELLIGENT       |          DECOUPLED AI         |        ZERO-COST ($0)          |
| Neural Edge-TTS engine with    | Scripture-grounded OpenAI-    | Strictly engineered to run     |
| deep-bass acoustic modulation, | compatible plugin preventing  | 100% free on OCI Always Free   |
| 4-worker chapter prefetch &    | theological hallucinations in | Tier, GitHub Actions, and      |
| persistent deduplication cache.| exegesis, study, and quizzes. | local desktop runtimes.        |
+--------------------------------+-------------------------------+--------------------------------+
```

1. **Offline-First Resilience ([ADR-002](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-002.yaml)):** All core functionality—scripture reading, full-text search, song lyrics, and reading plans—operates 100% offline using embedded, local SQLite databases (`data/bible.sqlite.db`, `data/songs.sqlite.db`).
2. **Dual-Canon & Bilingual Parity ([PROD-CANON-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-CANON-001.yaml)):** Complete parallel alignment across Protestant (66 books) and Catholic (73 books, including 7 Deuterocanonical books) canons in Tamil (Bower 1871, IRV 2019) and English (KJV 1769, Douay-Rheims 1752).
3. **Dual-Platform Architecture ([ARCH-SYS-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-SYS-001.yaml), [ADR-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-001.yaml)):** A unified FastAPI application powering both public web deployments and a native Windows desktop executable via PyWebView and Microsoft Edge WebView2.
4. **Mandatory Zero-Cost ($0) Governance ([ARCH-DIST-002](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DIST-002.yaml)):** Production deployments must never exceed the bounds of the Oracle Cloud Infrastructure (OCI) Always Free tier (`VM.Standard.A1.Flex`, 4 OCPUs, 24 GB RAM, 200 GB storage).
5. **Rigorous Knowledge-Base Alignment ([AGENTS.md](file:///home/ubuntu/openhand/workspace/bibleweb/AGENTS.md)):** All development, architectural changes, and bug fixes strictly adhere to the AI-Native Knowledge Base protocol in `knowledge/`.

### 1.3 Key Public & Deployment Endpoints
- **Primary Web Portal:** [https://elroi-bible.vercel.app](https://elroi-bible.vercel.app)
- **OCI Cloud Production VM:** `http://129.225.69.57/` (Custom domain binding: `http://elroi.js.org/`)
- **WhatsApp Webhook Gateway:** `https://wa-akg-gateway-ub6a.onrender.com`
- **GitHub Repository:** [`https://github.com/Elroi-thecreator/bibleweb`](https://github.com/Elroi-thecreator/bibleweb)
- **Windows Desktop Releases:** [`https://github.com/Elroi-thecreator/bibleweb/releases`](https://github.com/Elroi-thecreator/bibleweb/releases)
- **Microsoft WinGet Packages:**
  - `ElroiTheCreator.HolyBible` (Portable CLI/Desktop: PR [#446873](https://github.com/microsoft/winget-pkgs/pull/446873))
  - `ElroiTheCreator.HolyBibleDesktop` (Desktop Package: PR [#460301](https://github.com/microsoft/winget-pkgs/pull/460301))

---

## 2. System Architecture & Topology

```mermaid
flowchart TD
    subgraph ClientTiers["Client Presentation Tiers"]
        Browser["Modern Web Browsers\n(Chrome, Firefox, Safari, Edge)"]
        DesktopApp["Windows Standalone Executable\n(PyWebView + Edge WebView2)"]
        WhatsAppClient["WhatsApp Mobile & Web Clients\n(WA-AKG / Meta Cloud API)"]
    end

    subgraph ReverseProxy["Edge & Ingress Layer"]
        Nginx["Nginx Reverse Proxy (OCI VM 129.225.69.57)\n- Primary root / hosting\n- 301 legacy rewrite /bible -> /\n- SSL Termination & OWASP Headers"]
    end

    subgraph AppServer["FastAPI Application Server (Uvicorn Async Core)"]
        RouterMain["Main Router\n(Reader, Presentation, Plans, Quiz, Audio)"]
        RouterAdmin["Admin Sub-Router (/admin)\n- HMAC-SHA256 Auth\n- Telemetry & Settings"]
        RouterAI["Ask Bible AI Sub-Router (/api/ask-ai)\n- Grounded LLM Gateway\n- SSE Stream Engine"]
        RouterWA["WhatsApp Gateway Sub-Router (/api/whatsapp)\n- Bot Dispatcher & Rate Limiter\n- Queue Publisher & Sync Store"]
    end

    subgraph DataTier["Embedded Local Persistence Layer"]
        DBBible[("data/bible.sqlite.db\n73 Books | 35,782 Verses\nFTS5 Full-Text Search")]
        DBSongs[("data/songs.sqlite.db\n1,582 Christian Songs\n100% YouTube Coverage")]
        DBSettings[("data/admin_settings.sqlite.db\nDynamic Centralized Settings\nSingle Source of Truth")]
        DBAIHistory[("data/bible_ai_history.sqlite.db\nBilingual Conversational History")]
        AudioCache[("Local Disk Audio Cache\n.audio_cache/ Edge-TTS\nBoundedAudioCache (LRU)")]
    end

    subgraph ExternalServices["External Infrastructure & Cloud Backends"]
        MetaCloud["Meta WhatsApp Cloud API / WA-AKG Baileys"]
        RabbitMQ["RabbitMQ Message Broker (Optional AMQP)"]
        LLMProvider["OpenAI-Compatible LLM\n(FreeLLMAPI / Groq / Ollama / Gemini)"]
        EdgeTTS["Microsoft Edge Neural TTS Engine"]
        Supabase["Supabase PostgreSQL (Optional Cloud Sync)"]
    end

    Browser -->|HTTP/HTTPS| Nginx
    DesktopApp -->|Local Loopback 127.0.0.1:port| AppServer
    WhatsAppClient -->|Webhooks| Nginx

    Nginx -->|Proxy Pass Unix Socket / TCP:8000| AppServer

    AppServer --> RouterMain
    AppServer --> RouterAdmin
    AppServer --> RouterAI
    AppServer --> RouterWA

    RouterMain --> DBBible
    RouterMain --> DBSongs
    RouterAdmin --> DBSettings
    RouterAI --> DBAIHistory
    RouterAI --> DBBible
    RouterMain --> AudioCache

    RouterAI -.->|REST /v1| LLMProvider
    RouterMain -.->|Audio Stream Synthesis| EdgeTTS
    RouterWA -.->|REST / Webhooks| MetaCloud
    RouterWA -.->|AMQP| RabbitMQ
    RouterWA -.->|Cloud Hydration| Supabase
```

### 2.1 Unified FastAPI & PyWebView Desktop Hybrid ([ARCH-SYS-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-SYS-001.yaml), [ADR-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-001.yaml))
Instead of maintaining separate Node.js/Electron and Python codebases, Holy Bible utilizes a single unified codebase:
- **Web Mode:** Started via `uvicorn app.main:app` with asynchronous workers, serving standard browsers over HTTP/HTTPS.
- **Desktop Mode (`windows_app/app.py`):** Spawns a background thread running Uvicorn daemon on `127.0.0.1` bound to an dynamically allocated ephemeral port, and attaches `pywebview` with Microsoft Edge WebView2 evergreen runtime.
- **Benefits:** 27 MB standalone portable executable (versus 130+ MB with Electron), memory footprint under 70 MB RAM (versus 350+ MB with Chromium), zero logic duplication.

### 2.2 Frozen Path Resolution ([DEV-BUILD-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/development/DEV-BUILD-001.yaml))
All assets, databases, Jinja2 templates, and static resources resolve dynamically:
```python
if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", sys.executable)).resolve()
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
```
This guarantees identical behavior across development source runs, containerized Docker environments, and PyInstaller bundled binaries (`windows_app/holybible.spec`).

### 2.3 Dual Embedded SQLite Architecture ([ARCH-DATA-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DATA-001.yaml), [ADR-002](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-002.yaml), [ADR-004](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-004.yaml))
Scripture and Hymnal domains are strictly isolated into distinct SQLite databases:
- **`data/bible.sqlite.db` (~47.68 MB):** Houses 73 biblical books and 35,782 verses across four parallel linguistic translations. Configured with `PRAGMA mmap_size = 67108864` (64 MB memory-mapped I/O) and `PRAGMA cache_size = -8000` (8 MB page cache). Includes an SQLite FTS5 virtual table `verses_fts` with `tokenize='unicode61'` for sub-millisecond full-text search.
- **`data/songs.sqlite.db` (~8.15 MB):** Stores 1,582 Christian songs across 8 hymnals, including 1,167 songs from all 40 volumes of Fr. S.J. Berchmans' *Jebathota Jeyageethangal*, bilingual stanzas (`lyrics_bilingual`), and verified YouTube streaming links.
- **Decoupling Rationale:** Prevents the primary scripture repository from breaching GitHub's 50 MB soft limit warning, allows independent schema evolution, and prevents lock contention during heavy search queries.

### 2.4 High-Performance Memory & Compression Caching
- **`BoundedHTMLCache` ([DEV-PY-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/development/DEV-PY-001.yaml)):** In-memory LRU cache storing pre-rendered and pre-compressed HTML payloads. Automatically detects client support for Brotli (`br`) and Gzip (`gzip`), serving compressed payloads directly with conditional HTTP `ETag` and `304 Not Modified` headers.
- **`BoundedAudioCache` ([PROD-AUDIO-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-AUDIO-001.yaml)):** Thread-safe audio cache combining fast RAM caching with disk persistence in `.audio_cache/`, paired with in-flight synthesis deduplication to prevent duplicate edge-TTS calls for simultaneous listeners.

### 2.5 Centralized Runtime Settings Database ([ARCH-ADMIN-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-ADMIN-001.yaml))
- All application configurations—WhatsApp gateway settings, AI provider parameters, rate limits, audio TTS preferences, and study toggles—reside in `data/admin_settings.sqlite.db` as the sole single source of truth (`admin_settings` table).
- Dynamic hot-swapping via `/admin/api/settings/save-all` and `/admin/api/settings/reload` without server reboots, container rebuilds, or background polling loops.

---

## 3. Product Features & Domain Engines

### 3.1 Scripture Reading & Multi-Canon Engine ([PROD-CANON-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-CANON-001.yaml))
- **Canons Supported:**
  - **Protestant Canon (66 Books / 31,102 Verses):** 39 Old Testament + 27 New Testament books.
  - **Catholic Canon (73 Books / 35,782 Verses):** Includes the 7 Deuterocanonical books (Tobit, Judith, Wisdom of Solomon, Sirach, Baruch, 1 Maccabees, 2 Maccabees) along with additions to Esther and Daniel.
- **Parallel Bilingual Corpora:**
  1. *Tamil Old Version (1871 Rev. Henry Bower)* — Public Domain (`verses.text_ta`)
  2. *Tamil Indian Revised Version (IRV 2019)* — CC BY-SA 4.0 (`verses.text_ta_poc`)
  3. *King James Version (KJV 1769 Oxford Blayney)* — Public Domain (`verses.text_en`)
  4. *Douay-Rheims Bible (1752 Challoner Revision)* — Public Domain (`verses.text_en_drb`)
- **Reading Modes:**
  - **Chapter Reader (`/read/{book_id}/{chapter}`):** Side-by-side bilingual parallel reading, inline verse bookmarking, cross-references, verse highlighting, and AI study exegesis trigger.
  - **Read-Along Prayer Mode (`/read-along/plan/{plan_type}/day/{day}`):** Synchronized visual verse tracking with real-time audio playback.
  - **Church Projector / Presenter Mode (`/present/{book_id}/{chapter}`):** High-contrast, distraction-free typography for church screens, monitors, and projection systems with keyboard navigation (Arrows/Space).

### 3.2 Scripture Typography & Multi-Reader Isolation ([PROD-TYPO-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-TYPO-001.yaml))
- Default body font size is anchored at **18px** (`--reader-font-size: 18px;`) for optimal Tamil and English legibility.
- Strict `localStorage` key isolation prevents collision between the pixel-based Chapter Reader (`bible_font_size`) and the rem-based Read-Along mode (`bible_readalong_font_rem`).
- Self-healing JavaScript sanity guard on boot: automatically clamps corrupted or microscopic font sizes back to the safe bounds `[12px, 36px]`.

### 3.3 Christian Songs & Liturgical Hymnal Directory ([PROD-SONGS-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-SONGS-001.yaml))
- **1,582 Christian Songs across 8 Songbooks:**
  - *Jebathota Jeyageethangal (Volumes 1–40):* Complete collection of 1,167 songs authored by Fr. S.J. Berchmans.
  - *Classic Christian Hymns (பாமாலை & கீர்த்தனைகள்):* Traditional Tamil hymnals.
  - *Contemporary Worship Leaders:* Dedicated collections from Dr. Joseph Aldrin (25 songs), Pastor Benny Joshua (25 songs), and Pastor John Jebaraj (25 songs).
- **Features:**
  - Bilingual display: Tamil script with phonetic Romanized English transliteration.
  - Liturgical presentation: distinctive visual badging for Chorus/Pallavi and Stanzas.
  - 100% verified YouTube coverage: embedded responsive video player with fallback to verified YouTube Music and streaming search links.
  - Dual-page search: instant title, lyrics, and author search on both the directory landing page (`/songs`) and individual song detail views (`/songs/{song_id}`).

### 3.4 Audio Bible & Deep Bass TTS Engine ([PROD-AUDIO-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-AUDIO-001.yaml))
- Primary synthesis using **Microsoft Edge Neural TTS** (`ta-IN-ValluvarNeural` for Tamil, `en-US-GuyNeural` for English) with fallback to Google `gTTS`.
- **Acoustic Modulation:** Edge-TTS parameters tuned with deep bass pitch shift (`-5Hz` to `-10Hz`) and natural cadence (`+0%` rate) to deliver a resonant, authoritative orator timbre suitable for Scripture.
- **Concurrent 4-Worker Prefetching:** When a user initiates chapter playback, background workers asynchronously synthesize and cache the subsequent 3 chapters in advance.
- **Streaming Audio Route (`/api/audio/stream`):** Delivers clean chunked MP3 audio directly to client audio elements with full byte-range support.

### 3.5 Ask Bible AI & Theological Study Tools ([ARCH-AI-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-AI-001.yaml), [ADR-009](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-009.yaml))
- **Decoupled Architecture:** Built as an independent, portable plugin in `ask_bible_ai/` with zero hard dependencies on the host web framework.
- **OpenAI `/v1` Compatible:** Works seamlessly with self-hosted LLMs, local Ollama instances, Groq Cloud, Gemini OpenAI endpoints, or FreeLLMAPI.
- **Verified Scripture Grounding (`BaseGroundingProvider`):** Prior to prompting the LLM, the system dynamically queries the local SQLite database to retrieve exact, verified verses, injecting them into the system prompt to eliminate theological drift and confabulation.
- **Server-Sent Events (SSE) Streaming (`POST /api/ask-ai/stream`):** Low-latency token-by-token streaming to the interactive slide-over chat drawer.
- **AI Chapter Overviews (`GET /api/study/chapter-overview`):** Synthesizes author background, composition era, historical setting, thematic outlines, and core takeaways.
- **Verse-by-Verse Exegesis (`POST /api/study/verse-exegesis`):** Delivers deep theological exposition, original Hebrew/Greek word studies (lemmas and roots), cross-references, and personal life application.
- **Scripture Trivia & Quiz Engine ([PROD-QUIZ-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-QUIZ-001.yaml)):** Daily multiple-choice quizzes, dynamic AI question generation (`/api/quiz/generate-ai`), and interactive AI theological tutoring for incorrect answers (`/api/quiz/explain-ai`).

### 3.6 WhatsApp Bot & Messaging Gateway ([ARCH-WA-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-WA-001.yaml), [ADR-005](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-005.yaml)–[ADR-008](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-008.yaml))
- **Pluggable Provider Architecture:** Abstracted under `BaseWhatsAppProvider` supporting:
  - Official Meta WhatsApp Business Cloud API (including Developer Sandbox free testing).
  - WA-AKG Baileys Multi-Device QR Gateway (connects personal/business numbers without per-conversation fees).
  - In-Memory Simulation Provider for local development and integration testing.
- **Tiered Sliding-Window Rate Limiting ([ADR-007](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-007.yaml)):** Rolling 60-second request cap (default 20 req/min) paired with a distinct daily calendar-day quota (default 15 voice notes/day) for CPU-intensive TTS audio generation. Admin phone numbers bypass all limits.
- **Automated Devotional Broadcasts:** Scheduled daily devotional pushes with scripture verses, reflection cards, and synthesized audio voice notes.
- **Optional RabbitMQ AMQP Task Queue ([ADR-006](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-006.yaml)):** Provides asynchronous, non-blocking message ingestion under high traffic spikes.

### 3.7 Administrator Control & System Telemetry ([ARCH-ADMIN-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-ADMIN-001.yaml))
- Secure administration dashboard accessible at `/admin/settings` protected by cryptographic HMAC-SHA256 session cookies (`SameSite=Lax`, `HttpOnly`) and constant-time password comparisons.
- Full runtime management: WhatsApp gateway selection, credentials, AI models, rate limits, audio cache clearing, database health diagnostics, and JSON settings import/export.

---

## 4. GitHub Repository Map & Codebase Cartography

**Upstream GitHub Repository:** [`https://github.com/Elroi-thecreator/bibleweb`](https://github.com/Elroi-thecreator/bibleweb)  
**Primary Working Directory (`repository_root`):** `/home/ubuntu/openhand/workspace/bibleweb`

```
bibleweb/
├── .agents/                                # AI agent workspace hooks & telemetry
│   └── hooks.json
├── .github/                                # GitHub Actions CI/CD workflows & automation
│   └── workflows/
│       ├── daily_push.yml                  # Hourly scheduled daily devotional push via web-push/Supabase
│       ├── generate_plans.yml              # On-demand workflow generating 100-day reading plans
│       ├── ping-every-12mins.yml           # Automated cron keep-alive ping for free cloud services
│       └── release_windows.yml             # WinGet & PyInstaller release build & Komac release automation
├── app/                                    # Core FastAPI application package
│   ├── admin/                              # Administrator authentication & settings subsystem
│   │   ├── __init__.py
│   │   ├── auth.py                         # HMAC-SHA256 session management & security guards
│   │   └── routes.py                       # Admin settings endpoints & API management handlers
│   ├── db.py                               # SQLite connection pooling, FTS5 queries, multi-canon helpers
│   ├── main.py                             # Primary FastAPI server, middleware, routes & caching logic
│   ├── plans_data.py                       # 100-day reading plan metadata & chapter mappings
│   ├── quiz_ai.py                          # AI Scripture Quiz generation & theological explanation client
│   ├── quiz_data.py                        # Curated scripture trivia question bank & categories
│   ├── settings_db.py                      # Centralized SQLite admin settings persistence engine
│   └── study_ai.py                         # AI Scripture Study: chapter overviews & verse exegesis
├── ask_bible_ai/                           # Decoupled OpenAI-compatible Bible AI plugin
│   ├── adapters/
│   │   └── holy_bible_adapter.py           # Scripture grounding adapter bridging plugin to SQLite DB
│   ├── client.py                           # Resilient OpenAI /v1 API client (Ollama/Groq/FreeLLMAPI)
│   ├── config.py                           # Plugin configuration & model definitions
│   ├── grounding.py                        # Grounding provider interface (BaseGroundingProvider)
│   ├── history.py                          # SQLite-backed conversation history (bible_ai_history.sqlite.db)
│   ├── prompts.py                          # System prompts, theological guidelines & bilingual templates
│   ├── requirements.txt                    # Plugin-specific Python dependencies
│   ├── routes.py                           # REST & SSE streaming endpoints (/api/ask-ai/*)
│   ├── service.py                          # High-level question answering & grounding coordinator
│   └── tests/
│       └── test_ask_bible_ai.py            # Unit test suite for Ask Bible AI plugin
├── data/                                   # Embedded database storage & JSON state
│   ├── admin_settings.sqlite.db            # Centralized settings single source of truth
│   ├── bible.sqlite.db                     # Multi-canon bilingual scripture database with FTS5 virtual table
│   ├── songs.sqlite.db                     # Christian song lyrics & hymnal database
│   └── whatsapp_subscribers.json           # Local cache of subscribed WhatsApp phone numbers
├── knowledge/                              # AI-Native Knowledge Base System (26 Units)
│   ├── architecture/                       # System & subsystem architectural standards (ARCH-*)
│   ├── decisions/                          # Formal Architecture Decision Records (ADR-*)
│   ├── development/                        # Coding, packaging, and performance standards (DEV-*)
│   ├── index.yaml                          # Master Knowledge Graph Index & metadata registry
│   └── product/                            # Domain & feature functional standards (PROD-*)
├── scripts/                                # Maintenance, benchmarking, and verification test suites
│   ├── audit_and_fix_all_youtube_links.py  # Automated auditor validating 100% YouTube song coverage
│   ├── build_fts_index.py                  # Utility rebuilding SQLite FTS5 search virtual tables
│   ├── deploy_oracle_cloud.sh              # Automated deployment script for Oracle Cloud Always Free VM
│   ├── generate_100day_plans.py            # Generates Whole Bible & New Testament reading plans
│   ├── generate_catholic_plans.py          # Generates Catholic & Deuterocanon reading plans
│   ├── holybible.service                   # Systemd service unit for Oracle Cloud deployment
│   ├── ingest_all_worship_leaders.py       # Scraper/ingestion pipeline for contemporary worship songs
│   ├── ingest_open_licensed_corpora.py     # Ingestion script for Bower, IRV, KJV, and DRB scripture texts
│   ├── ingest_songs.py                     # Primary song catalog parser & SQLite migration script
│   ├── load_test.py                        # Asynchronous HTTP benchmarking & concurrency saturation test
│   ├── nginx_oracle_bible.conf             # Nginx reverse proxy configuration for Oracle Cloud VM
│   ├── populate_all_youtube_urls.py        # Enriches song database with verified YouTube stream IDs
│   ├── resolve_jebathota_videos.py         # YouTube video resolver for Fr. Berchmans' 40 volumes
│   ├── run_server.py                       # Local development Uvicorn server launcher
│   ├── send_whatsapp_message.py            # CLI utility for testing WhatsApp outgoing dispatches
│   ├── setup_nginx_root.sh                 # Root-level Nginx installer with legacy /bible redirection
│   ├── song_datasets.py                    # Static dataset definitions for Christian hymnals
│   ├── stress_breakpoint_test.py           # Concurrency breakpoint test identifying worker limits
│   ├── test_admin_settings.py              # Automated test suite for settings persistence & reload
│   ├── test_ask_bible_ai.py                # Integration test for AI chat, grounding & SSE streaming
│   ├── test_audio.py                       # Edge-TTS voice synthesis verification
│   ├── test_audio_concurrency_and_cache.py # Concurrent prefetch & memory cache test
│   ├── test_audio_deduplication.py         # Verifies in-flight request deduplication
│   ├── test_audio_flow_e2e.py              # End-to-end audio streaming & cache test suite
│   ├── test_compression.py                 # Brotli/Gzip compression ratio & ETag verification
│   ├── test_dual_corpus.py                 # Dual-canon verse count & scripture integrity test
│   ├── test_merged_verses.py               # Tests combined/merged verse rendering across canons
│   ├── test_prefix_deployment.py           # Verifies URL_PREFIX routing for subpath hosting
│   ├── test_quiz_integrity.py              # Validates multiple-choice options & question bank
│   ├── test_robustness.py                  # OWASP security headers, error pages & health checks
│   ├── test_songs.py                       # Verifies song pagination, bilingual lyrics & YouTube embeds
│   ├── test_study_ai.py                    # Validates chapter overviews & verse exegesis endpoints
│   ├── test_typography.py                  # Verifies 18px font size & storage key isolation
│   ├── test_whatsapp_providers.py          # Tests Meta Cloud, WA-AKG & simulation providers
│   ├── test_whatsapp_queue.py              # RabbitMQ AMQP queue integration test
│   ├── test_whatsapp_rate_limiter.py       # Sliding-window rate limiter & daily quota test
│   ├── test_whatsapp_webhook.py            # WhatsApp webhook ingress & bot command routing test
│   ├── test_windows_app.py                 # Windows desktop app & PyInstaller path test
│   └── track_winget_prs.py                 # Real-time monitor for WinGet pull requests #446873 & #460301
├── static/                                 # Static client assets (PWA, Fonts, CSS, JS)
│   ├── fonts/                              # Bundled Noto Sans Tamil & Noto Serif web fonts
│   ├── icons/                              # Progressive Web App (PWA) application icons
│   ├── js/                                 # Modular client scripts (audio_player.js, storage.js)
│   ├── plans/                              # Precomputed 100-day reading plan JSON files
│   ├── manifest.json                       # PWA web manifest specification
│   └── sw.js                               # Service Worker for offline asset caching
├── templates/                              # Jinja2 HTML templates
│   ├── admin/                              # Protected administrative interfaces
│   │   ├── login.html                      # Branded admin authentication screen
│   │   └── settings.html                   # Interactive administrative settings dashboard
│   ├── 404.html                            # Custom bilingual 404 Not Found page
│   ├── 500.html                            # Custom bilingual 500 Internal Server Error page
│   ├── ask_ai.html                         # Dedicated Ask Bible AI interactive chat portal
│   ├── base.html                           # Root layout template with typography & navigation
│   ├── bookmarks.html                      # Saved verses, reading history & notes manager
│   ├── chapter.html                        # Main Chapter Reader view with bilingual parallel columns
│   ├── landing.html                        # Application landing page & book navigation grid
│   ├── plans.html                          # 100-Day Scripture Reading Plans catalog
│   ├── presenter.html                      # Church projector / presenter view
│   ├── privacy.html                        # Privacy policy page complying with WinGet Policy 1.5.1
│   ├── progress.html                       # Reading streak tracking & analytics dashboard
│   ├── quiz.html                           # Daily Scripture Trivia & interactive quiz interface
│   ├── read_along.html                     # Read-Along Prayer Mode with synchronized audio tracking
│   ├── search.html                         # Full-text scripture search interface (FTS5 powered)
│   ├── song_detail.html                    # Single song view with bilingual lyrics & YouTube player
│   ├── songs.html                          # Christian songbook directory & volume browser
│   ├── sync.html                           # Multi-device cloud synchronization interface
│   └── whatsapp.html                       # WhatsApp Bot enrollment & subscription portal
├── whatsapp_gateway/                       # Decoupled WhatsApp Bot & Messaging Engine
│   ├── adapters/
│   │   ├── bible_adapter.py                # Formats scripture verses & devotionals for WhatsApp
│   │   └── card_generator.py               # Generates graphical verse cards via Pillow
│   ├── bot/
│   │   ├── context.py                      # Incoming message state & user session context
│   │   ├── dispatcher.py                   # Command router (/read, /audio, /quiz, /song, /search)
│   │   └── session_store.py                # In-memory user conversation state store
│   ├── client/                             # HTTP client wrappers for outgoing messaging
│   ├── providers/                          # Pluggable provider implementations
│   │   ├── base.py                         # Abstract BaseWhatsAppProvider interface
│   │   ├── meta_cloud_provider.py          # Official Meta WhatsApp Business Cloud API provider
│   │   ├── registry.py                     # Dynamic provider registration & switching
│   │   ├── simulation_provider.py          # Mock provider for zero-cost integration testing
│   │   └── wa_akg_provider.py              # WA-AKG Baileys multi-device QR gateway provider
│   ├── queue/                              # Optional RabbitMQ AMQP message broker integration
│   │   ├── connection.py                   # Robust RabbitMQ connection factory
│   │   ├── consumer.py                     # Background worker consuming outgoing queue
│   │   ├── manager.py                      # High-level queue management abstraction
│   │   └── publisher.py                    # Dispatches outgoing messages to RabbitMQ
│   ├── routes/
│   │   └── webhook.py                      # Ingress webhook routes (/api/whatsapp/webhook)
│   ├── scheduler/
│   │   ├── devotional_push.py              # Morning & evening devotional dispatch logic
│   │   └── runner.py                       # Background asyncio cron runner for devotionals
│   ├── audio_converter.py                  # FFmpeg audio conversion to WhatsApp Opus/OGG voice notes
│   ├── config.py                           # WhatsApp subsystem configuration & defaults
│   ├── rate_limiter.py                     # Tiered sliding-window rate limiter & daily quota engine
│   ├── subscribers.py                      # Subscriber list manager (JSON + Supabase dual persistence)
│   └── sync_store.py                       # Generates & validates multi-device 6-digit sync codes
├── windows_app/                            # Native Windows Desktop Distribution
│   ├── assets/                             # Windows executable icons (app.ico, icon-192.png)
│   ├── app.py                              # PyWebView desktop launcher wrapping background Uvicorn
│   ├── build_exe.py                        # Automated PyInstaller packaging script
│   ├── generate_winget_manifest.py         # WinGet YAML manifest generator
│   ├── holybible.spec                      # PyInstaller single-file bundle specification
│   ├── requirements.txt                    # Desktop-specific dependencies (pywebview, etc.)
│   └── submit_winget.md                    # Operational guide for Microsoft WinGet package updates
├── AGENTS.md                               # AI agent workspace directives & strict invariants
├── Dockerfile                              # Multi-stage production container build definition
├── docker-compose.yml                      # Local development composition (FastAPI + RabbitMQ)
├── GEMINI.md                               # Gemini / Antigravity agent operational standards
├── LICENSE                                 # GNU General Public License v3.0 (GPL-3.0)
├── NOTICE.md                               # Open-source scripture provenance & copyright notices
├── PRIVACY.md                              # Application privacy policy & telemetry disclosures
├── README.md                               # Upstream GitHub repository overview & quickstart
├── render.yaml                             # PaaS deployment blueprint for Render cloud hosting
└── requirements.txt                        # Production Python dependencies
```

---

## 5. Exhaustive Codebase Cartography Matrix

The following matrix maps every file in the GitHub repository to its system layer, architectural responsibilities, associated Knowledge Units, and quality invariants:

| GitHub File / Directory | Subsystem / Layer | Primary Architectural Responsibilities | Associated Knowledge Units | Operational Invariants & Directives |
| :--- | :--- | :--- | :--- | :--- |
| `app/main.py` | Core Application | Server entrypoint, middleware, route handling, compression, in-memory HTML page cache (`BoundedHTMLCache`), exception handlers. | [ARCH-SYS-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-SYS-001.yaml), [DEV-PY-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/development/DEV-PY-001.yaml), [DEV-PERF-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/development/DEV-PERF-001.yaml) | Offload blocking I/O with `asyncio.to_thread`. Return OWASP security headers. |
| `app/db.py` | Persistence Engine | SQLite thread-local connection pool, FTS5 scripture queries, multi-canon book registries, memory-mapped I/O configuration. | [ARCH-DATA-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DATA-001.yaml), [PROD-CANON-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-CANON-001.yaml), [ADR-002](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-002.yaml) | Enforce `PRAGMA mmap_size = 64MB`. Sub-millisecond FTS5 queries with `unicode61`. |
| `app/settings_db.py` | Administration | Centralized SQLite runtime settings database wrapper (`admin_settings.sqlite.db`), sectioned key-value storage. | [ARCH-ADMIN-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-ADMIN-001.yaml) | Single source of truth. Load into memory on boot; no continuous polling. |
| `app/study_ai.py` | Theological AI | AI Scripture Study service: historical chapter overviews and verse-by-verse exegesis with curated fallbacks. | [PROD-STUDY-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-STUDY-001.yaml), [ARCH-AI-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-AI-001.yaml) | Always provide bilingual output. Fall back gracefully if LLM provider offline. |
| `app/quiz_ai.py` | Gamification AI | Scripture Quiz AI integration: dynamic question generation and interactive theological tutor explanations. | [PROD-QUIZ-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-QUIZ-001.yaml), [ARCH-AI-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-AI-001.yaml) | Randomize 4 multiple-choice options to prevent positional guessing. |
| `app/admin/auth.py` | Security / Admin | HMAC-SHA256 session token generation, cookie validation, constant-time password verification (`secrets.compare_digest`). | [ARCH-ADMIN-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-ADMIN-001.yaml) | Reject unauthenticated calls with 401 (API) or 303 redirect to `/admin/login`. |
| `app/admin/routes.py` | Administrative API | Endpoints for runtime configuration, cache invalidation, WhatsApp provider management, and database telemetry. | [ARCH-ADMIN-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-ADMIN-001.yaml), [DEV-PY-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/development/DEV-PY-001.yaml) | Guard all routes with `require_admin`. Export/import full JSON settings. |
| `ask_bible_ai/` | Decoupled AI Plugin | Fully isolated, OpenAI `/v1` compatible biblical QA plugin with verified scripture grounding and SSE streaming. | [ARCH-AI-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-AI-001.yaml), [ADR-009](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-009.yaml) | Zero hard dependencies on host application framework; reusable in any Python app. |
| `whatsapp_gateway/` | Messaging Subsystem | Pluggable WhatsApp bot (Meta Cloud API & WA-AKG), tiered rate limiter, audio push, RabbitMQ queue option. | [ARCH-WA-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-WA-001.yaml), [ADR-005](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-005.yaml)–[ADR-008](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-008.yaml) | Enforce 60s sliding window (20 req/min) and daily audio quota (15 voice notes/day). |
| `windows_app/app.py` | Desktop Launcher | Native Windows desktop runtime launching Uvicorn daemon on ephemeral port with PyWebView Microsoft Edge WebView2. | [ARCH-SYS-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-SYS-001.yaml), [ADR-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-001.yaml) | Wrap stdout/stderr with SafeStream in `--noconsole` mode to avoid crashes. |
| `windows_app/holybible.spec` | PyInstaller Spec | Single-file Windows portable executable specification bundling databases, templates, and static assets. | [ARCH-DIST-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DIST-001.yaml), [DEV-BUILD-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/development/DEV-BUILD-001.yaml) | Ensure `sys._MEIPASS` dynamic directory resolution handles all bundled data. |
| `data/bible.sqlite.db` | Scripture Database | 73 books and 35,782 verses across 4 linguistic corpora (Bower, IRV, KJV, DRB) with FTS5 search index. | [ARCH-DATA-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DATA-001.yaml), [PROD-CANON-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-CANON-001.yaml) | Maintain exact verse counts: 31,102 Protestant + 4,680 Deuterocanonical = 35,782. |
| `data/songs.sqlite.db` | Hymnal Database | 1,582 Christian songs across 8 hymnals, including all 40 volumes of Fr. S.J. Berchmans' *Jebathota Jeyageethangal*. | [ARCH-DATA-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DATA-001.yaml), [PROD-SONGS-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-SONGS-001.yaml), [ADR-004](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-004.yaml) | 100% verified YouTube coverage with structured bilingual stanzas (`lines_ta`/`lines_en`). |
| `scripts/load_test.py` | Performance Tool | Asynchronous load generator testing throughput (RPS), p50/p95/p99 latency, and server memory budgets. | [DEV-PERF-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/development/DEV-PERF-001.yaml) | Respect memory ceiling on Render Free tier (512 MB max; maintain ~100 MB RSS). |
| `scripts/track_winget_prs.py` | Distribution Tool | Active tracker querying GitHub API for Microsoft WinGet Community PRs #446873 and #460301. | [ARCH-DIST-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DIST-001.yaml), [ADR-003](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-003.yaml) | Startup invariant: inspect PR status at session start and ensure scheduled tracking. |
| `scripts/deploy_oracle_cloud.sh` | DevOps / Cloud | Zero-downtime deployment script provisioning systemd and Nginx on Oracle Cloud Always Free VM. | [ARCH-DIST-002](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DIST-002.yaml) | Strict Zero-Cost ($0) invariant: never provision paid OCI resources. |
| `.github/workflows/release_windows.yml` | CI/CD Automation | Builds portable executable, computes SHA256, generates GitHub Release, and updates WinGet via Komac. | [ARCH-DIST-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DIST-001.yaml), [ADR-003](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/decisions/ADR-003.yaml) | Triggers on `v*` tag push with automated Komac WinGet manifest submission. |

---

## 6. Complete API & Routing Catalog

### 6.1 Public Scripture & Presentation Routes (`app/main.py`)
- `GET /` — Landing page with Catholic/Protestant canon switcher, book grid, search, and reading plans.
- `GET /read/{book_id}/{chapter}` — Primary Chapter Reader with parallel bilingual text, font scaling, audio player, and exegesis drawer.
- `GET /present/{book_id}/{chapter}` — Full-screen projector / presenter mode for church monitors and screens.
- `GET /plans` — Reading plans directory (Whole Bible, New Testament, Catholic Canon, Deuterocanon).
- `GET /read-along/plan/{plan_type}/day/{day}` — Synchronized verse-by-verse audio read-along mode.
- `GET /search?q={query}&scope={scope}&canon={canon}` — Full-text FTS5 scripture search across biblical corpora.
- `GET /bookmarks` — User's saved verses, highlighted passages, notes, and local reading history.
- `GET /songs` — Christian song directory, volume browser, and multi-scope song search.
- `GET /songs/{song_id}` — Song details page with bilingual stanzas and responsive YouTube player.
- `GET /quiz` — Daily Scripture Trivia game with randomized multiple-choice options.
- `GET /ask`, `GET /ask-ai` — Dedicated Ask Bible AI conversational portal.
- `GET /whatsapp` — WhatsApp bot registration, command reference, and devotional subscription.
- `GET /sync` — Cloud progress synchronization portal (Supabase magic-link or 6-digit sync code).
- `GET /settings` — Client-side preferences (theme, fonts, audio voice, default translation).
- `GET /api/audio/stream?text={text}&lang={lang}` — Edge-TTS neural audio streaming endpoint with bass modulation.
- `GET /api/health` — Comprehensive system health check (database status, memory usage, uptime).
- `GET /status` — Visual system telemetry, cache ratios, and live connection metrics.

### 6.2 Ask Bible AI Routes (`ask_bible_ai/routes.py`)
- `POST /api/ask-ai/ask` — Standard JSON question-answering with verified scripture grounding.
- `POST /api/ask-ai/stream` — Real-time Server-Sent Events (SSE) token streaming for responsive chat drawers.
- `GET /api/ask-ai/sessions` — List active conversation sessions.
- `POST /api/ask-ai/sessions` — Create a new conversation session.
- `GET /api/ask-ai/sessions/{id}` — Fetch conversation turn history for a session.
- `DELETE /api/ask-ai/sessions/{id}` — Delete a specific conversation session.
- `DELETE /api/ask-ai/history` — Clear all local conversation history.
- `GET /api/ask-ai/suggestions` — Contextual prompt suggestions based on current chapter or topic.
- `GET /api/ask-ai/health` — Probes configured LLM endpoint connectivity and latency.
- `GET /api/ask-ai/config` — Retrieves active AI plugin configuration.
- `POST /api/ask-ai/config` — Updates AI plugin settings at runtime.
- `GET /api/ask-ai/ui` — Embeddable standalone chat interface.

### 6.3 WhatsApp Gateway Routes (`whatsapp_gateway/routes/webhook.py`)
- `GET /api/whatsapp/webhook`, `GET /api/whatsapp/meta-webhook` — Meta Webhook verification handshake (`hub.challenge`).
- `POST /api/whatsapp/webhook`, `POST /api/whatsapp/meta-webhook` — Ingress webhook for incoming WhatsApp messages and status receipts.
- `POST /api/whatsapp/simulate` — In-memory webhook simulator for local testing without network calls.
- `GET /api/whatsapp/status` — Gateway health, active provider name, and connection state.
- `GET /api/whatsapp/providers` — Lists registered WhatsApp providers (Meta Cloud, WA-AKG, Simulation).
- `GET /api/whatsapp/rate-limiter/status` — Telemetry on rolling window usage and daily audio quotas.
- `POST /api/whatsapp/broadcast` — Dispatches message or devotional broadcast to subscriber list.
- `POST /api/whatsapp/sync/request-code` — Generates a temporary 6-digit synchronization code.
- `POST /api/whatsapp/sync/verify` — Verifies 6-digit code to pair WhatsApp subscriber with web profile.

### 6.4 Administrative Control Routes (`app/admin/routes.py`)
- `GET /admin/login`, `POST /admin/login` — Administrator authentication with constant-time password check.
- `GET /admin/logout`, `POST /admin/logout` — Terminates administrative session and clears auth cookies.
- `GET /admin/settings` — Complete administrative control dashboard.
- `POST /admin/api/cache/clear-html` — Flushes in-memory `BoundedHTMLCache`.
- `POST /admin/api/cache/clear-audio` — Clears cached Edge-TTS audio files in `.audio_cache/`.
- `POST /admin/api/settings/save-all` — Atomic update saving all settings to `admin_settings.sqlite.db`.
- `POST /admin/api/settings/reload` — On-demand reload of runtime settings into application memory.
- `GET /admin/api/settings/export` — Exports complete configuration state as JSON.
- `POST /admin/api/settings/import` — Imports configuration state from uploaded JSON payload.
- `POST /admin/api/ai/test` — Tests connectivity to configured OpenAI-compatible endpoint.

---

## 7. Master Knowledge Graph Index (27 Units)

The project adheres to the **AI-Native Knowledge Base Protocol** registered in [`knowledge/index.yaml`](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/index.yaml). Every unit defines enforceable rules, positive recommendations (`do`), negative anti-patterns (`dont`), and architectural rationale:

```mermaid
graph TD
    subgraph ArchUnits["Architecture Standards (ARCH-*)"]
        A_SYS["ARCH-SYS-001\nUnified FastAPI & PyWebView"]
        A_DATA["ARCH-DATA-001\nDual-SQLite Architecture"]
        A_DIST1["ARCH-DIST-001\nPyInstaller & WinGet Pipeline"]
        A_DIST2["ARCH-DIST-002\nOCI Free VM & Zero-Cost"]
        A_WA["ARCH-WA-001\nDecoupled WhatsApp Gateway"]
        A_ADMIN["ARCH-ADMIN-001\nAdmin Auth & Settings DB"]
        A_AI["ARCH-AI-001\nDecoupled Ask Bible AI"]
    end

    subgraph DevUnits["Development Standards (DEV-*)"]
        D_DOC["DEV-DOC-001\nProject Bible & Repository Map"]
        D_PY["DEV-PY-001\nFastAPI Conventions & Caching"]
        D_BUILD["DEV-BUILD-001\nFrozen Path Resolution"]
        D_TEST["DEV-TEST-001\nAutomated Verification Suites"]
        D_PERF["DEV-PERF-001\nAsync Load & Memory Budgets"]
    end

    subgraph ProdUnits["Product Standards (PROD-*)"]
        P_AUDIO["PROD-AUDIO-001\nAudio TTS & Bass Modulation"]
        P_QUIZ["PROD-QUIZ-001\nDaily Scripture Trivia & AI Quiz"]
        P_CANON["PROD-CANON-001\nDual-Canon Navigation"]
        P_SONGS["PROD-SONGS-001\nChristian Hymnals & YouTube"]
        P_TYPO["PROD-TYPO-001\n18px Typography Standard"]
        P_STUDY["PROD-STUDY-001\nAI Study & Verse Exegesis"]
    end

    subgraph DecisionRecords["Architecture Decision Records (ADR-*)"]
        ADR1["ADR-001: PyWebView over Electron"]
        ADR2["ADR-002: Embedded SQLite over Cloud DB"]
        ADR3["ADR-003: WinGet Community Distribution"]
        ADR4["ADR-004: Decouple Songs DB from Bible DB"]
        ADR5["ADR-005: Supabase / JSON WA Hydration"]
        ADR6["ADR-006: RabbitMQ Queue Option"]
        ADR7["ADR-007: Sliding-Window Rate Limiting"]
        ADR8["ADR-008: Pluggable WhatsApp Providers"]
        ADR9["ADR-009: Decoupled AI Grounding Plugin"]
    end

    A_SYS --> ADR1
    A_DATA --> ADR2
    A_DATA --> ADR4
    A_DIST1 --> ADR3
    A_DIST1 --> D_BUILD
    A_WA --> ADR5
    A_WA --> ADR6
    A_WA --> ADR7
    A_WA --> ADR8
    A_AI --> ADR9
    A_AI --> P_STUDY
    A_AI --> P_QUIZ
    P_CANON --> A_DATA
    P_SONGS --> A_DATA
    P_AUDIO --> D_PERF
    D_PY --> D_TEST
```

### Complete Knowledge Unit Directory

| ID | Domain | Title | Version | Status | Primary Directives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ARCH-SYS-001** | Architecture | Unified FastAPI & PyWebView Desktop Hybrid | 1.0.0 | Approved | Single codebase for web and desktop; launch PyWebView on ephemeral port with Edge WebView2. |
| **ARCH-DATA-001** | Architecture | Embedded Dual-SQLite Architecture | 1.3.0 | Approved | Isolate Scripture (`bible.sqlite.db`) and Songs (`songs.sqlite.db`); thread-local pooling, FTS5 unicode61. |
| **ARCH-DIST-001** | Architecture | PyInstaller Standalone Windows Executable & WinGet | 1.3.0 | Approved | Single portable exe (`HolyBible-Portable.exe`), automated Komac CI/CD on `v*` tags, WinGet 1.5.1/2.2 compliance. |
| **ARCH-DIST-002** | Architecture | OCI Free Tier VM Deployment & Zero-Cost Protocol | 1.1.0 | Approved | Host at root `/` with 301 legacy `/bible` redirect; enforce strict $0 Always Free tier limit on OCI. |
| **ARCH-WA-001** | Architecture | Decoupled WhatsApp Gateway & Reusable Bot Engine | 1.28.0 | Approved | Dual-provider support (Meta Cloud & WA-AKG), dual-storage subscriber persistence, rate limiting. |
| **ARCH-ADMIN-001**| Architecture | Admin Authentication, Protected Settings & Telemetry | 1.12.0 | Approved | HMAC-SHA256 session cookies, centralized SQLite settings single source of truth, on-demand reload. |
| **ARCH-AI-001** | Architecture | Decoupled Ask Bible AI with Scripture Grounding | 1.4.0 | Approved | Independent plugin in `ask_bible_ai/`, OpenAI `/v1` compliant, SSE streaming, scripture grounding provider. |
| **DEV-DOC-001** | Development | Master Project Bible & Repository Mapping Specification | 1.0.0 | Approved | Authoritative living Master Project Bible (`PROJECT_BIBLE.md`) mapping all subsystems, routes, schemas & standards. |
| **DEV-PY-001** | Development | FastAPI Backend Route Conventions & Jinja2 Templates| 1.5.0 | Approved | Async route handlers, `asyncio.to_thread` for DB I/O, `BoundedHTMLCache` with Brotli/Gzip and ETags. |
| **DEV-BUILD-001** | Development | Frozen Path Resolution (`sys._MEIPASS`) Standard | 1.0.0 | Approved | Resolve all asset paths dynamically via `sys._MEIPASS` when frozen, root traversal when in source mode. |
| **DEV-TEST-001** | Development | Automated Verification & Executable Smoke Testing | 1.3.0 | Approved | Mandatory pre-commit verification scripts (`pytest`, `test_robustness.py`, `test_dual_corpus.py`). |
| **DEV-PERF-001** | Development | Asynchronous Load Testing & Capacity Benchmarking | 1.6.0 | Approved | Respect 512 MB memory ceiling on Render (maintain ~100 MB RSS); benchmark with `scripts/load_test.py`. |
| **PROD-AUDIO-001**| Product | Audio TTS Engine, Deep Bass & Concurrent Prefetch | 1.1.0 | Approved | Edge-TTS with deep bass modulation, 4-worker concurrent chapter prefetch, `BoundedAudioCache` disk store. |
| **PROD-QUIZ-001** | Product | Daily Bible Quiz, AI Generation & Theological Tutor | 1.1.0 | Approved | Daily trivia question bank, AI question generation, theological explanations, randomized option ordering. |
| **PROD-CANON-001**| Product | Multi-Canon (Catholic 73 & Protestant 66) Navigation| 1.0.0 | Approved | Full Deuterocanon support, bilingual 4-column corpora, unified book selection UI across both canons. |
| **PROD-SONGS-001** | Product | Christian Song Lyrics, Hymnals & Dual-Page Search | 1.6.1 | Approved | 1,582 songs, all 40 volumes of Fr. Berchmans' *Jebathota Jeyageethangal*, 100% YouTube coverage, dual-page search. |
| **PROD-TYPO-001** | Product | Scripture Typography & Multi-Reader Isolation | 1.0.0 | Approved | Default font size 18px (`--reader-font-size`), isolated localStorage keys (`bible_font_size`), auto-healing guard. |
| **PROD-STUDY-001**| Product | AI Scripture Study, Chapter Overviews & Exegesis | 1.0.0 | Approved | Bilingual historical chapter overviews, verse-by-verse theological exegesis, original Hebrew/Greek roots. |
| **ADR-001** | Decision | PyWebView with Edge WebView2 over Electron | 1.0.0 | Accepted | 27 MB executable size, <70 MB RAM usage, zero code duplication by wrapping FastAPI directly. |
| **ADR-002** | Decision | Local Embedded SQLite over External Cloud Database | 1.1.0 | Accepted | 100% offline functionality, zero cloud DB bills, sub-millisecond queries via memory-mapped I/O. |
| **ADR-003** | Decision | Microsoft WinGet Repository for Desktop Distribution | 1.0.0 | Accepted | Frictionless one-command installs (`winget install ElroiTheCreator.HolyBible`), automated CI release updates. |
| **ADR-004** | Decision | Decouple Songs DB (`songs.sqlite.db`) from Bible DB | 1.0.0 | Accepted | Prevents repo exceeding GitHub 50 MB soft limit warning, allows independent schema evolution. |
| **ADR-005** | Decision | Supabase PostgreSQL & Persistent JSON for WhatsApp | 1.0.0 | Accepted | Dual-storage persistence: instant local JSON cache paired with Supabase cloud backup. |
| **ADR-006** | Decision | Asynchronous RabbitMQ Task Queue Option | 1.0.0 | Accepted | Pluggable AMQP message broker decoupling incoming webhook ingestion from worker dispatch. |
| **ADR-007** | Decision | Thread-Safe Tiered Sliding-Window Rate Limiter | 1.0.0 | Accepted | 60-second rolling window (20 req/min) + daily audio quota (15 notes/day) with admin whitelisting. |
| **ADR-008** | Decision | Pluggable WhatsApp Gateway Provider Architecture | 1.0.0 | Accepted | Seamless runtime hot-swapping between Meta Cloud API, WA-AKG Baileys, and Simulation mode. |
| **ADR-009** | Decision | Decoupled OpenAI-Compatible Plugin Architecture | 1.0.0 | Accepted | Independent `ask_bible_ai/` package, pluggable scripture grounding, local SQLite history store. |

---

## 8. Quality Gates, Testing & Invariant Verification

Before merging changes, tagging releases, or publishing WinGet packages, execute the mandatory verification suite:

```bash
# 1. Dual-Canon Verse Count & Scripture Integrity Verification
python3 scripts/test_dual_corpus.py

# 2. Christian Song Lyrics, Hymnal Structure & YouTube Embed Audit
python3 scripts/test_songs.py

# 3. Audio Bible Synthesis, Bass Modulation & Concurrent Prefetching
python3 scripts/test_audio_flow_e2e.py

# 4. HTTP Compression, Brotli/Gzip Ratios & ETag Header Verification
python3 scripts/test_compression.py

# 5. OWASP Security Headers, 404/500 Bilingual Templates & Health Endpoints
python3 scripts/test_robustness.py

# 6. Centralized Admin Settings Persistence & SQLite Single Source of Truth
python3 scripts/test_admin_settings.py

# 7. Ask Bible AI Grounding, Local History & SSE Stream Validation
python3 scripts/test_ask_bible_ai.py

# 8. WhatsApp Webhook Ingress, Bot Command Routing & Multi-Provider Test
python3 scripts/test_whatsapp_webhook.py
python3 scripts/test_whatsapp_providers.py

# 9. Sliding-Window Rate Limiter & Daily Audio Quota Boundary Tests
python3 scripts/test_whatsapp_rate_limiter.py

# 10. Scripture Reader 18px Default Typography & Key Isolation Audit
python3 scripts/test_typography.py

# 11. Native Windows Desktop Packaging & PyInstaller Path Resolution Test
python3 scripts/test_windows_app.py

# 12. Active WinGet Pull Request Monitor (Startup Protocol)
python3 scripts/track_winget_prs.py
```

### Critical Zero-Cost & Operational Invariants
1. **OCI Zero-Cost Guard ([ARCH-DIST-002](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-DIST-002.yaml)):** Never provision paid OCI resources. All services share `VM.Standard.A1.Flex` with subpath reverse proxying in Nginx.
2. **WinGet PR Tracking Invariant ([AGENTS.md](file:///home/ubuntu/openhand/workspace/bibleweb/AGENTS.md)):** Track community review PRs [#446873](https://github.com/microsoft/winget-pkgs/pull/446873) and [#460301](https://github.com/microsoft/winget-pkgs/pull/460301). Keep the background cron job (`schedule` tool `0 */6 * * *`) active.
3. **Typography Invariant ([PROD-TYPO-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-TYPO-001.yaml)):** Reader text must default to 18px (`--reader-font-size: 18px;`).
4. **Verse Count Invariant ([PROD-CANON-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/product/PROD-CANON-001.yaml)):** Exactly 31,102 Protestant verses and 4,680 Catholic Deuterocanonical verses (35,782 total verses in `data/bible.sqlite.db`).
5. **Admin Security Invariant ([ARCH-ADMIN-001](file:///home/ubuntu/openhand/workspace/bibleweb/knowledge/architecture/ARCH-ADMIN-001.yaml)):** Admin session tokens must be HMAC-SHA256 signed and compared with constant-time equality.

---

## 9. Developer Runbook & Operations

### 9.1 Local Web Server Execution
```bash
# Install dependencies
pip install -r requirements.txt

# Launch local development server with auto-reload
python scripts/run_server.py
# Alternatively:
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate to `http://127.0.0.1:8000/`.

### 9.2 Native Windows Desktop Application Launch
```powershell
# Install Windows desktop dependencies
pip install -r windows_app/requirements.txt

# Run desktop application via PyWebView
python windows_app/app.py
```

### 9.3 Compiling Windows Standalone Executable
```powershell
# Build single-file portable executable via PyInstaller
python windows_app/build_exe.py
# Executable output: dist/HolyBible-Portable.exe
```

### 9.4 Environment Variables Reference
| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `URL_PREFIX` | `""` (empty) | Base subpath for reverse proxy hosting (e.g., `/bible`). |
| `ADMIN_PASSWORD` | `admin123` | Master password for `/admin/settings` access. |
| `SESSION_SECRET` | Auto-generated | Secret key used to sign HMAC-SHA256 admin cookies. |
| `AI_PROVIDER_TYPE` | `openai` | Active AI provider (`openai`, `groq`, `ollama`, `freellmapi`). |
| `AI_BASE_URL` | `https://api.openai.com/v1` | Base URL for OpenAI-compatible LLM endpoint. |
| `AI_API_KEY` | `""` | API key for LLM requests (or dummy token for Ollama). |
| `AI_MODEL` | `gpt-4o-mini` | Model identifier passed in `/v1/chat/completions`. |
| `WHATSAPP_PROVIDER` | `meta_cloud` | Active WhatsApp provider (`meta_cloud`, `wa_akg`, `simulation`). |
| `WA_PHONE_NUMBER_ID`| `""` | Meta Cloud API Phone Number ID. |
| `WA_ACCESS_TOKEN` | `""` | Meta System User Access Token. |
| `WA_WEBHOOK_VERIFY_TOKEN`| `""` | Verification token for Meta webhook subscription. |
| `RABBITMQ_ENABLED` | `false` | Enables AMQP task queue for asynchronous messaging. |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:5672/` | AMQP connection string. |
| `SUPABASE_URL` | `""` | Optional Supabase instance URL for subscriber backup. |
| `SUPABASE_SERVICE_ROLE_KEY` | `""` | Supabase service key for cloud subscriber backup. |

---
*Holy Bible Project Bible & Codebase Cartography — Synchronized with Upstream Repository `Elroi-thecreator/bibleweb`.*
