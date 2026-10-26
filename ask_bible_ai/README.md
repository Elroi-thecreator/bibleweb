# Ask Bible AI Plugin (`ask_bible_ai`)

A decoupled, reusable, and production-ready **Biblical AI Assistant Plugin** for Python and FastAPI applications.

Features:
- **Zero Framework Lock-in:** The core AI engine has **zero dependencies** on application-specific databases or schemas.
- **OpenAI-Compatible Universal Client:** Works seamlessly with [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi), [Ollama](https://ollama.ai), [Groq Cloud](https://groq.com), Google Gemini, or official OpenAI endpoints.
- **Verified Scripture Grounding:** Pluggable grounding interface (`BaseGroundingProvider`) retrieves real scripture passages to eliminate hallucinations and supply verified chapter & verse citations.
- **Bilingual Intelligence:** Native support for English and Tamil (தமிழ்), with auto-detection and appropriate biblical phrasing.
- **Server-Sent Events (SSE) Streaming:** Real-time token streaming endpoint (`POST /stream`) for responsive, low-latency UI experiences.
- **Built-in Offline Simulation Engine:** Functions fully offline in simulation mode without external network calls, perfect for local development and CI/CD pipelines.
- **Standalone Embeddable UI:** Ships with a complete, zero-dependency full-page chat interface at `/api/ask-ai/ui` that can be embedded in any application via an `<iframe>`.

---

## Directory Structure

```
ask_bible_ai/
├── __init__.py                # Clean module exports
├── config.py                  # Pydantic configuration with env vars & JSON persistence
├── client.py                  # Async client for any OpenAI-compatible /v1 endpoint
├── grounding.py               # Abstract BaseGroundingProvider protocol & in-memory stores
├── prompts.py                 # System prompts, theological guardrails & bilingual helpers
├── service.py                 # Central AskBibleAIService orchestrator
├── routes.py                  # Mountable FastAPI APIRouter (/ask, /stream, /suggestions, /health, /ui)
├── adapters/
│   ├── __init__.py
│   └── holy_bible_adapter.py  # (Optional) Adapter for SQLite FTS5 database in Holy Bible
├── tests/
│   ├── __init__.py
│   └── test_ask_bible_ai.py   # Complete automated test suite
├── requirements.txt           # Minimal dependencies (httpx, pydantic, fastapi)
└── README.md                  # This documentation
```

---

## Quickstart: How to Use in ANY Python / FastAPI Project

### Step 1: Copy the `ask_bible_ai` folder
Copy the entire `ask_bible_ai/` directory into your project root or `plugins/` directory.

### Step 2: Install dependencies
```bash
pip install httpx pydantic fastapi
```

### Step 3: Mount the Router in your FastAPI application

```python
from fastapi import FastAPI
from ask_bible_ai import ask_ai_router

app = FastAPI(title="My Application")

# Mount the Ask Bible AI plugin
app.include_router(ask_ai_router, prefix="/api/ask-ai", tags=["ask-bible-ai"])
```

That's it! Your application now exposes:
- Interactive UI: `http://localhost:8000/api/ask-ai/ui`
- Question-Answering API: `POST http://localhost:8000/api/ask-ai/ask`
- Token Streaming API: `POST http://localhost:8000/api/ask-ai/stream`
- Health Telemetry: `GET http://localhost:8000/api/ask-ai/health`
- Starter Suggestions: `GET http://localhost:8000/api/ask-ai/suggestions`

---

## Configuring LLM Backends

Configure the plugin via environment variables or runtime JSON overrides (`data/bible_ai_config.json`):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `BIBLE_AI_ENABLED` | `true` | Enables or disables the AI endpoint |
| `BIBLE_AI_PROVIDER` | `freellmapi` | Provider identifier (`freellmapi`, `ollama`, `groq`, `openai`, `simulation`) |
| `BIBLE_AI_BASE_URL` | `http://localhost:3000/v1` | Base URL of any OpenAI-compatible API |
| `BIBLE_AI_API_KEY` | `free-tier` | API Key for upstream provider |
| `BIBLE_AI_MODEL` | `gemini-2.0-flash` | Model identifier to request |
| `BIBLE_AI_TEMPERATURE` | `0.3` | Generation temperature (0.0 - 1.0) |
| `BIBLE_AI_MAX_TOKENS` | `1024` | Maximum tokens per response |
| `BIBLE_AI_SIMULATION` | `false` | When `true`, generates responses locally without network calls |

### Example 1: Connecting to FreeLLMAPI (Zero Cost Gateway)
[FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) aggregates free-tier quotas from Google Gemini, Groq, Cerebras, and Mistral behind a local proxy:
```bash
export BIBLE_AI_PROVIDER="freellmapi"
export BIBLE_AI_BASE_URL="http://localhost:3000/v1"
export BIBLE_AI_MODEL="gemini-2.0-flash"
export BIBLE_AI_API_KEY="free-tier"
```

### Example 2: Connecting to Ollama (100% Local & Private)
Run any open-source model locally without sending any data over the internet:
```bash
ollama run llama3
export BIBLE_AI_PROVIDER="ollama"
export BIBLE_AI_BASE_URL="http://localhost:11434/v1"
export BIBLE_AI_MODEL="llama3"
export BIBLE_AI_API_KEY="ollama"
```

### Example 3: Connecting to Groq Cloud (Ultra-Fast Free Tier)
```bash
export BIBLE_AI_PROVIDER="groq"
export BIBLE_AI_BASE_URL="https://api.groq.com/openai/v1"
export BIBLE_AI_MODEL="llama-3.3-70b-versatile"
export BIBLE_AI_API_KEY="gsk_your_groq_api_key_here"
```

---

## Connecting Your Own Database (Custom Grounding)

To ground AI answers in your own database (PostgreSQL, MySQL, MongoDB, or Elasticsearch), simply implement `BaseGroundingProvider`:

```python
from typing import List
from ask_bible_ai.grounding import BaseGroundingProvider, GroundingPassage
from ask_bible_ai.routes import ai_service

class MyPostgresGroundingProvider(BaseGroundingProvider):
    async def retrieve_context(self, query: str, language: str = "auto", max_passages: int = 4) -> List[GroundingPassage]:
        # Query your database (e.g., PostgreSQL with pgvector or full-text search)
        records = await my_db.query_verses(query, limit=max_passages)
        return [
            GroundingPassage(
                reference=f"{r.book} {r.chapter}:{r.verse}",
                text_en=r.english_text,
                text_ta=r.tamil_text,
                book=r.book,
                chapter=r.chapter,
                verse=r.verse,
            )
            for r in records
        ]

# Inject into the service
ai_service.set_grounding_provider(MyPostgresGroundingProvider())
```

---

## API Reference

### 1. Ask Question (JSON)
`POST /api/ask-ai/ask`

**Request:**
```json
{
  "query": "What does the Bible say about love?",
  "language": "auto",
  "max_passages": 4
}
```

**Response:**
```json
{
  "success": true,
  "query": "What does the Bible say about love?",
  "language": "en",
  "answer": "### Biblical Understanding of Love\n\nThe Holy Scriptures teach that God is the very source and definition of love (1 John 4:8)...",
  "citations": ["1 Corinthians 13:4-7", "John 3:16", "1 John 4:8"],
  "passages_used": [
    {
      "reference": "1 Corinthians 13:4",
      "text_en": "Charity suffereth long, and is kind...",
      "text_ta": "அன்பு நீடிய சாந்தமும் தயவுமுள்ளது...",
      "book": "1 Corinthians",
      "chapter": 13,
      "verse": 4
    }
  ],
  "model": "gemini-2.0-flash",
  "took_ms": 342.1
}
```

### 2. Stream Question (Server-Sent Events)
`POST /api/ask-ai/stream`

Streams raw token chunks:
```
data: {"token": "The "}
data: {"token": "Bible "}
data: {"token": "teaches "}
...
data: [DONE]
```

### 3. Health & Telemetry
`GET /api/ask-ai/health`
```json
{
  "status": "healthy",
  "enabled": true,
  "provider": "freellmapi",
  "base_url": "http://localhost:3000/v1",
  "model": "gemini-2.0-flash",
  "grounding_provider": "HolyBibleGroundingAdapter",
  "grounding_enabled": true,
  "simulation_mode": false
}
```

---

## License
MIT License. Free to use, adapt, and distribute across commercial and open-source applications.
