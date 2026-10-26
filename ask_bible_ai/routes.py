"""
Ask Bible AI FastAPI Router.
Provides a mountable, fully-featured REST and Streaming API:
- POST /ask: Structured question-answering with verified scripture grounding
- POST /stream: Real-time Server-Sent Events (SSE) token streaming
- GET /suggestions: Dynamic bilingual prompt suggestions
- GET /health: Health & connectivity telemetry
- GET/POST /config: Runtime configuration inspection and hot-swapping
- GET /ui: Standalone, dependency-free full-page chat interface
Can be mounted on ANY FastAPI application with:
    app.include_router(ask_ai_router, prefix="/api/ask-ai", tags=["ask-bible-ai"])
"""

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from ask_bible_ai.config import config, save_persisted_config
from ask_bible_ai.service import AskBibleAIService
from ask_bible_ai.adapters.holy_bible_adapter import HolyBibleGroundingAdapter

router = APIRouter()

# Instantiate service singleton with Holy Bible grounding adapter
_grounding_adapter = HolyBibleGroundingAdapter()
ai_service = AskBibleAIService(config=config, grounding_provider=_grounding_adapter)


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000, description="The biblical question or topic")
    history: Optional[List[Dict[str, str]]] = Field(default=None, description="Prior conversation messages")
    language: str = Field(default="auto", description="Preferred output language: 'auto', 'en', or 'ta'")
    max_passages: Optional[int] = Field(default=None, ge=1, le=10, description="Maximum grounding passages to retrieve")


class ConfigUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    provider_name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    simulation_mode: Optional[bool] = None
    enable_grounding: Optional[bool] = None


@router.post("/ask")
async def ask_bible_endpoint(req: AskRequest):
    """
    Submit a biblical question and receive a grounded, theological answer
    with exact scripture citations.
    """
    if not config.enabled:
        raise HTTPException(status_code=503, detail="Ask Bible AI service is currently disabled in configuration.")

    try:
        response = await ai_service.ask(
            query=req.query,
            history=req.history,
            preferred_language=req.language,
            max_passages=req.max_passages,
        )
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")


@router.post("/stream")
async def stream_bible_endpoint(req: AskRequest):
    """
    Streams the biblical answer token-by-token using Server-Sent Events (SSE).
    """
    if not config.enabled:
        raise HTTPException(status_code=503, detail="Ask Bible AI service is currently disabled.")

    async def event_generator():
        try:
            async for token in ai_service.ask_stream(
                query=req.query,
                history=req.history,
                preferred_language=req.language,
                max_passages=req.max_passages,
            ):
                payload = json.dumps({"token": token}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_payload = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/suggestions")
async def get_suggestions_endpoint(language: str = Query("auto", description="Language: 'auto', 'en', 'ta'")):
    """Returns curated starter questions for users."""
    suggestions = ai_service.get_suggested_questions(language=language)
    return {"language": language, "suggestions": suggestions}


@router.get("/health")
async def health_endpoint():
    """Returns runtime health and provider connection telemetry."""
    return await ai_service.health()


@router.get("/config")
async def get_config_endpoint():
    """Returns safe runtime configuration."""
    return config.to_dict()


@router.post("/config")
async def update_config_endpoint(req: ConfigUpdateRequest):
    """Updates runtime configuration settings and persists them to disk."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if not updates:
        return config.to_dict()

    new_cfg = save_persisted_config(updates)
    # Re-sync service config
    ai_service.config = new_cfg
    ai_service.client.config = new_cfg
    return new_cfg.to_dict()


@router.get("/ui", response_class=HTMLResponse)
async def standalone_ui_page(request: Request):
    """
    Serves a completely standalone, embeddable HTML chat interface.
    Allows testing the plugin out-of-the-box or embedding via iframe into ANY application.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ask Bible AI — வேதாகம உதவியாளர்</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Tamil:wght@400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body { font-family: 'Lora', 'Noto Serif Tamil', serif; }
        .font-cinzel { font-family: 'Cinzel', serif; }
        .font-tamil { font-family: 'Noto Serif Tamil', serif; }
        .prose p { margin-bottom: 0.75rem; line-height: 1.8; }
        .prose ul { list-style-type: disc; margin-left: 1.25rem; margin-bottom: 0.75rem; }
        .prose ol { list-style-type: decimal; margin-left: 1.25rem; margin-bottom: 0.75rem; }
        .prose strong { color: #92400e; font-weight: 600; }
        .prose h3, .prose h4 { font-family: 'Cinzel', serif; color: #78350f; margin-top: 1rem; margin-bottom: 0.5rem; }
    </style>
</head>
<body class="bg-stone-50 text-stone-900 min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-white border-b border-stone-200 px-4 py-3 sticky top-0 z-10 flex items-center justify-between shadow-xs">
        <div class="flex items-center space-x-3">
            <span class="w-8 h-8 rounded-full bg-amber-700 text-white flex items-center justify-center font-cinzel font-bold text-sm">†</span>
            <div>
                <h1 class="font-cinzel text-base font-bold tracking-wide text-amber-950">ASK BIBLE AI</h1>
                <p class="text-[11px] font-tamil text-stone-500">வேதாகம அறிவார்ந்த உதவியாளர் (Bilingual AI)</p>
            </div>
        </div>
        <div class="flex items-center space-x-2 text-xs">
            <span id="status-pill" class="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-medium">Checking...</span>
        </div>
    </header>

    <!-- Chat Container -->
    <main class="flex-1 max-w-4xl w-full mx-auto p-4 flex flex-col">
        <!-- Messages Area -->
        <div id="chat-messages" class="flex-1 space-y-4 mb-4 overflow-y-auto pb-6">
            <!-- Welcome Bot Message -->
            <div class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-full bg-amber-700 text-white flex items-center justify-center font-cinzel font-bold text-xs shrink-0 mt-0.5">†</div>
                <div class="bg-white border border-stone-200 rounded-2xl p-4 shadow-xs max-w-2xl">
                    <p class="font-semibold text-amber-900 text-sm mb-1">Welcome to Ask Bible AI | நல்வரவு</p>
                    <p class="text-xs text-stone-600 leading-relaxed">
                        Ask any question about the Holy Bible in English or Tamil. Responses are grounded directly in scripture with chapter and verse citations.
                    </p>
                    
                    <!-- Quick Suggestions -->
                    <div class="mt-3 pt-3 border-t border-stone-100">
                        <p class="text-[11px] font-semibold text-stone-500 uppercase tracking-wider mb-2">Try asking:</p>
                        <div id="suggestions-box" class="flex flex-wrap gap-1.5">
                            <span class="text-xs text-stone-400">Loading suggestions...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Input Box Area -->
        <div class="sticky bottom-4 bg-white border border-stone-300 rounded-2xl p-2 shadow-md">
            <form id="chat-form" onsubmit="handleSubmit(event)" class="flex items-center gap-2">
                <input type="text" id="user-input" 
                       placeholder="Ask about verses, parables, meaning... / கேள்விகளைக் கேளுங்கள்..." 
                       class="flex-1 px-3 py-2 text-sm bg-transparent outline-none text-stone-800 placeholder-stone-400"
                       autocomplete="off" required>
                <button type="submit" id="send-btn" 
                        class="bg-amber-700 hover:bg-amber-800 text-white px-4 py-2 rounded-xl text-xs font-semibold tracking-wider transition flex items-center gap-1.5 cursor-pointer shadow-xs">
                    <span>Ask AI</span>
                    <span>→</span>
                </button>
            </form>
            <div class="px-2 pt-1.5 flex justify-between items-center text-[11px] text-stone-400">
                <span>Grounded in Catholic & Protestant Biblical Corpora</span>
                <span id="model-badge">Free / Offline Ready</span>
            </div>
        </div>
    </main>

    <script>
        const chatMessages = document.getElementById('chat-messages');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const statusPill = document.getElementById('status-pill');
        const suggestionsBox = document.getElementById('suggestions-box');
        let conversationHistory = [];

        // Check health on load
        async function checkHealth() {
            try {
                const res = await fetch('/api/ask-ai/health');
                const data = await res.json();
                if (data.status === 'healthy') {
                    statusPill.textContent = '● AI Ready (' + (data.simulation_mode ? 'Simulation' : data.provider) + ')';
                    statusPill.className = 'px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium';
                } else {
                    statusPill.textContent = '● Local Fallback Mode';
                    statusPill.className = 'px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-medium';
                }
            } catch(e) {
                statusPill.textContent = '● Standalone';
                statusPill.className = 'px-2 py-0.5 rounded-full bg-stone-100 text-stone-600 font-medium';
            }
        }

        // Fetch suggestions
        async function loadSuggestions() {
            try {
                const res = await fetch('/api/ask-ai/suggestions');
                const data = await res.json();
                if (data.suggestions && data.suggestions.length) {
                    suggestionsBox.innerHTML = '';
                    data.suggestions.forEach(q => {
                        const btn = document.createElement('button');
                        btn.type = 'button';
                        btn.className = 'text-left text-xs bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200/60 rounded-lg px-2.5 py-1 transition cursor-pointer';
                        btn.textContent = q;
                        btn.onclick = () => {
                            userInput.value = q;
                            handleSubmit(new Event('submit'));
                        };
                        suggestionsBox.appendChild(btn);
                    });
                }
            } catch(e) {}
        }

        function appendUserMessage(text) {
            const wrap = document.createElement('div');
            wrap.className = 'flex justify-end';
            wrap.innerHTML = `
                <div class="bg-amber-700 text-white rounded-2xl rounded-tr-xs px-4 py-2.5 max-w-xl text-sm shadow-xs">
                    <p class="leading-relaxed">${escapeHtml(text)}</p>
                </div>
            `;
            chatMessages.appendChild(wrap);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function appendBotMessage(placeholder = 'Searching scriptures and pondering...') {
            const wrap = document.createElement('div');
            wrap.className = 'flex items-start gap-3 bot-msg-container';
            const id = 'msg-' + Date.now();
            wrap.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-amber-700 text-white flex items-center justify-center font-cinzel font-bold text-xs shrink-0 mt-0.5">†</div>
                <div class="bg-white border border-stone-200 rounded-2xl rounded-tl-xs p-4 shadow-xs max-w-2xl w-full">
                    <div id="${id}" class="prose text-xs text-stone-800 leading-relaxed font-serif">
                        <span class="inline-flex items-center gap-1.5 text-stone-400 italic">
                            <span class="animate-spin text-amber-700">⏳</span> ${placeholder}
                        </span>
                    </div>
                    <div id="${id}-citations" class="mt-3 pt-2 border-t border-stone-100 hidden"></div>
                </div>
            `;
            chatMessages.appendChild(wrap);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return id;
        }

        async function handleSubmit(e) {
            e.preventDefault();
            const text = userInput.value.trim();
            if (!text) return;

            appendUserMessage(text);
            userInput.value = '';
            userInput.disabled = true;
            sendBtn.disabled = true;

            const msgId = appendBotMessage();
            const targetEl = document.getElementById(msgId);
            const citationsEl = document.getElementById(msgId + '-citations');

            try {
                // Try streaming endpoint first
                const response = await fetch('/api/ask-ai/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: text,
                        history: conversationHistory,
                        language: 'auto'
                    })
                });

                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let accumulated = '';
                targetEl.innerHTML = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\\n');

                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (trimmed.startsWith('data: ')) {
                            const raw = trimmed.slice(6);
                            if (raw === '[DONE]') break;
                            try {
                                const parsed = JSON.parse(raw);
                                if (parsed.token) {
                                    accumulated += parsed.token;
                                    targetEl.innerHTML = marked.parse(accumulated);
                                    chatMessages.scrollTop = chatMessages.scrollHeight;
                                }
                            } catch (err) {}
                        }
                    }
                }

                if (!accumulated) {
                    // Fallback to standard /ask if stream was empty
                    const fallbackRes = await fetch('/api/ask-ai/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: text, history: conversationHistory })
                    });
                    const fbData = await fallbackRes.json();
                    accumulated = fbData.answer || 'No response generated.';
                    targetEl.innerHTML = marked.parse(accumulated);

                    if (fbData.citations && fbData.citations.length) {
                        citationsEl.classList.remove('hidden');
                        citationsEl.innerHTML = '<span class="text-[10px] uppercase font-bold text-stone-400">Cited Passages: </span>' + 
                            fbData.citations.map(c => `<span class="inline-block bg-amber-50 text-amber-800 text-[11px] font-medium px-2 py-0.5 rounded border border-amber-200 mr-1.5 mt-1">${c}</span>`).join('');
                    }
                }

                conversationHistory.push({ role: 'user', content: text });
                conversationHistory.push({ role: 'assistant', content: accumulated });

            } catch (err) {
                targetEl.innerHTML = `<span class="text-rose-600 font-semibold">Error: Could not reach Bible AI service (${err.message}).</span>`;
            } finally {
                userInput.disabled = false;
                sendBtn.disabled = false;
                userInput.focus();
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }

        function escapeHtml(str) {
            return str.replace(/[&<>'"]/g, tag => ({
                '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
            }[tag] || tag));
        }

        checkHealth();
        loadSuggestions();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)
