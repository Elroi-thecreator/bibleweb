# Decoupled WhatsApp Gateway & Multi-Feature Bot Engine

A production-grade, highly modular WhatsApp integration module built on top of **[WA-AKG](https://github.com/mrifqidaffaaditya/WA-AKG)** (Next.js + Baileys + Prisma).

This package is designed with **strict layer isolation** so that the client SDK, session store, and command dispatcher can be **exported and reused in any other Python / FastAPI project** without carrying application-specific dependencies.

---

## Architecture & Layers

```
whatsapp_gateway/
├── config.py              # Pydantic configuration & environment variable loader
│
├── client/                # [LAYER 1] Reusable WA-AKG Client SDK (Zero Domain Dependencies)
│   ├── client.py          # Async WAClient (send_text, send_media, get_session_status)
│   ├── models.py          # Pydantic schemas (IncomingWebhookPayload, SendTextMessageRequest)
│   └── exceptions.py      # Typed gateway exceptions
│
├── bot/                   # [LAYER 2] Generic Bot Dispatcher & Session Engine (Zero Domain Dependencies)
│   ├── context.py         # MessageContext with convenient .reply_text() & .reply_audio()
│   ├── dispatcher.py      # Command, Regex, State, and Fallback routing engine
│   └── session_store.py   # Thread-safe in-memory session manager with TTL auto-eviction
│
├── adapters/              # [LAYER 3] Domain Adapter (Holy Bible implementation)
│   └── bible_adapter.py   # Bridges scripture lookup, audio TTS, quizzes, hymns, reading plans
│
├── routes/                # [LAYER 4] FastAPI Controller & Webhook Endpoint
│   └── webhook.py         # /webhook, /status, and /broadcast endpoints
│
└── scheduler/             # [LAYER 5] Scheduled Automation Engine
    └── devotional_push.py # Background daily devotional broadcast
```

---

## Reusing in Another Project (e-commerce, CRM, alerts)

To use this WhatsApp Gateway in a different project:

1. Copy the `whatsapp_gateway/` folder into your new project.
2. In `whatsapp_gateway/adapters/`, create your own domain adapter (e.g., `ecommerce_adapter.py`):

```python
from whatsapp_gateway.bot.context import MessageContext
from whatsapp_gateway.bot.dispatcher import BotDispatcher

def register_custom_handlers(dispatcher: BotDispatcher) -> None:
    @dispatcher.command("orders", description="Check recent orders")
    async def handle_orders(ctx: MessageContext):
        # Your custom business logic
        await ctx.reply_text("📦 You have 2 pending orders.")

    @dispatcher.regex(r"^order\s+#?(\d+)$", description="Lookup order by ID")
    async def handle_order_lookup(ctx: MessageContext):
        order_id = ctx.matches.group(1)
        await ctx.reply_text(f"Order #{order_id} is out for delivery!")
```

3. Mount the webhook router into your FastAPI app:
```python
from fastapi import FastAPI
from whatsapp_gateway.routes.webhook import router as whatsapp_router

app = FastAPI()
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["whatsapp"])
```

---

## Configuration via Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `WA_GATEWAY_URL` | `http://localhost:3000/api` | Base URL of running WA-AKG instance |
| `WA_SESSION_ID` | `default` | Active WhatsApp session identifier in WA-AKG |
| `WA_API_KEY` | `None` | Optional Bearer token for WA-AKG API |
| `WA_WEBHOOK_SECRET` | `None` | Optional header secret to verify incoming webhooks |
| `WA_COMMAND_PREFIX` | `""` (empty) | Prefix for commands (e.g. `!` or `/` or leave empty) |
| `WA_SESSION_TTL_SECONDS` | `900` (15 mins) | Inactivity expiration for multi-turn dialogues |
| `WA_SIMULATION_MODE` | `false` | When `true`, records messages locally without live gateway |

---

## Available Holy Bible Features

* **Scripture Lookup**: `John 3:16`, `Genesis 1:1-5`, `Psalm 23`, `Tobit 4:7` (Deuterocanonical / Catholic canon supported).
* **Scripture Search**: `search faith`, `find peace`.
* **Daily Bible Quiz**: Send `quiz`, then reply with `1, 2, 3, or 4` (or `A, B, C, D`).
* **Hymn & Song Lyrics**: `song Amazing Grace` or `song 2281`.
* **Audio Voice Notes**: `audio John 3` or `listen Psalm 23`.
* **Reading Plans**: `plan` (shows today's assigned chapter).
* **Admin Broadcast**: `POST /api/whatsapp/broadcast` for mass community announcements.
