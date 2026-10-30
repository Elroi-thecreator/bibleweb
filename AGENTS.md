# 🤖 Holy Bible — AI Agent Workspace Instructions

> **ATTENTION ALL AI AGENTS (Antigravity, Cursor, Claude Code, Windsurf, Copilot, Gemini CLI)**  
> This workspace enforces an automated **AI-Native Knowledge Base System** located in [`knowledge/`](knowledge/).

---

## 1. Mandatory Pre-Execution Protocol (Strict Invariant)

> [!IMPORTANT]
> **MANDATORY FIRST TOOL ACTION**:
> On **ANY** task (including bug investigation, general questions, architecture review, refactoring, or writing code/tests), your **VERY FIRST tool call MUST be inspecting [`knowledge/index.yaml`](knowledge/index.yaml)**.
> 
> **DO NOT** perform speculative keyword searches or open application code files until you have consulted `knowledge/index.yaml` and loaded the relevant Knowledge Units.

1. **Query Master Index First**: Inspect [`knowledge/index.yaml`](knowledge/index.yaml) to identify the Knowledge Units matching your role and domain.
2. **Retrieve Persona Knowledge Units**:
   - **Frontend, UI & Reader Tasks** (Jinja2 templates, reader typography, Catholic/Protestant dual-corpus navigation, songs presentation, Web Audio player): Inspect [`ARCH-SYS-001`](knowledge/architecture/ARCH-SYS-001.yaml), [`DEV-PY-001`](knowledge/development/DEV-PY-001.yaml), [`PROD-TYPO-001`](knowledge/product/PROD-TYPO-001.yaml), [`PROD-CANON-001`](knowledge/product/PROD-CANON-001.yaml), [`PROD-SONGS-001`](knowledge/product/PROD-SONGS-001.yaml), [`PROD-AUDIO-001`](knowledge/product/PROD-AUDIO-001.yaml), [`PROD-STUDY-001`](knowledge/product/PROD-STUDY-001.yaml), [`PROD-QUIZ-001`](knowledge/product/PROD-QUIZ-001.yaml), and [`DEV-TEST-001`](knowledge/development/DEV-TEST-001.yaml).
   - **Backend, APIs & Messaging Tasks** (FastAPI async routes, dual-database queries, WhatsApp bot gateway, Edge-TTS audio, sliding-window rate limiting): Inspect [`ARCH-SYS-001`](knowledge/architecture/ARCH-SYS-001.yaml), [`ARCH-DATA-001`](knowledge/architecture/ARCH-DATA-001.yaml), [`ARCH-WA-001`](knowledge/architecture/ARCH-WA-001.yaml), [`ARCH-ADMIN-001`](knowledge/architecture/ARCH-ADMIN-001.yaml), [`ARCH-AI-001`](knowledge/architecture/ARCH-AI-001.yaml), [`DEV-PY-001`](knowledge/development/DEV-PY-001.yaml), [`PROD-AUDIO-001`](knowledge/product/PROD-AUDIO-001.yaml), [`PROD-QUIZ-001`](knowledge/product/PROD-QUIZ-001.yaml), [`DEV-PERF-001`](knowledge/development/DEV-PERF-001.yaml), and [`DEV-TEST-001`](knowledge/development/DEV-TEST-001.yaml).
   - **Architecture, Desktop Packaging & Distribution** (PyWebView Microsoft Edge WebView2, PyInstaller single-exe packaging, WinGet distribution pipeline): Inspect [`ARCH-SYS-001`](knowledge/architecture/ARCH-SYS-001.yaml), [`ARCH-DIST-001`](knowledge/architecture/ARCH-DIST-001.yaml), [`DEV-BUILD-001`](knowledge/development/DEV-BUILD-001.yaml), [`DEV-TEST-001`](knowledge/development/DEV-TEST-001.yaml), [`ADR-001`](knowledge/decisions/ADR-001.yaml), [`ADR-002`](knowledge/decisions/ADR-002.yaml), [`ADR-003`](knowledge/decisions/ADR-003.yaml), [`ADR-004`](knowledge/decisions/ADR-004.yaml), [`ADR-005`](knowledge/decisions/ADR-005.yaml), [`ADR-006`](knowledge/decisions/ADR-006.yaml), [`ADR-007`](knowledge/decisions/ADR-007.yaml), [`ADR-008`](knowledge/decisions/ADR-008.yaml), and [`ADR-009`](knowledge/decisions/ADR-009.yaml).
3. **Enforce Directives**: Strictly follow all `rule`, `do`, and `dont` fields in loaded Knowledge Units before taking any action.

---

## 2. Core Project Invariants

- **Dual-Platform Architecture**: Unified FastAPI codebase where core business logic, SQLite databases, and Jinja2 templates serve both the public web server and the native Windows desktop app via **PyWebView** (Microsoft Edge WebView2).
- **Dual-Database Persistence**:
  - Scripture Database: `data/bible.sqlite.db` containing both Protestant (66 books) and Catholic (73 books with Deuterocanonical books) canons.
  - Song Lyrics Database: `data/songs.sqlite.db` containing Christian lyrics and hymnals decoupled from scripture.
- **WhatsApp Bot & Gateway**: Pluggable architecture supporting WA-AKG Multi-Device Gateway and Meta WhatsApp Cloud API with thread-safe sliding-window rate limiting, daily audio synthesis quotas, and dual-storage persistence (PostgreSQL/Supabase + local cache).
- **Audio TTS Pipeline**: Edge-TTS engine with deep bass audio modulation, 4-worker concurrent chapter prefetching, in-flight deduplication, and persistent `BoundedAudioCache` disk storage (`.audio_cache/`).
- **Frozen Path Resolution**: All asset paths must resolve dynamically via `sys._MEIPASS` when packaged as a frozen PyInstaller binary (`windows_app/app.py`).

---

## 3. Mandatory Verification & Quality Gates

Before pushing commits, closing tasks, or packaging releases, run the automated verification suites:

```powershell
# 1. Route integrity & unit tests
pytest

# 2. Security headers, caching, error pages & health checks
python scripts/test_robustness.py

# 3. Brotli & Gzip compression ratio verification
python scripts/test_compression.py

# 4. Admin authentication & runtime settings persistence
python scripts/test_admin_settings.py

# 5. WhatsApp webhook & bot command routing
python scripts/test_whatsapp_webhook.py

# 6. Sliding-window rate limiter & quota tests
python scripts/test_whatsapp_rate_limiter.py

# 7. Dual-canon verse count & scripture integrity
python scripts/test_dual_corpus.py

# 8. Song lyrics & YouTube embed verification
python scripts/test_songs.py

# 9. Audio engine & concurrent prefetching tests
python scripts/test_audio_flow_e2e.py
```

---

## 4. Post-Change Knowledge Synchronization (Mandatory)

Whenever changes are made (e.g. new routes, schema modifications, UI behaviors, packaging updates, bug fixes, or architecture adjustments):
1. **Update Relevant Units**: Immediately update the matching YAML files in `knowledge/`.
2. **Add New Units**: If introducing a new pattern or architectural decision, create a new YAML unit following schema (`id`, `type`, `title`, `domain`, `status`, `version`, `rule`, `do`, `dont`, `reason`, `related_items`).
3. **Synchronize Index**: Update `knowledge/index.yaml` by incrementing `knowledge_units_count`, updating `last_updated`, and registering the unit.
