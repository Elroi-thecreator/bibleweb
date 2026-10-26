"""
Ask Bible AI OpenAI-Compatible Client.
Connects asynchronously to any OpenAI-compatible `/v1` server:
- FreeLLMAPI (Self-hosted free-tier gateway: http://localhost:3000/v1)
- Ollama (Local private models: http://localhost:11434/v1)
- Groq Cloud (Ultra-fast inference: https://api.groq.com/openai/v1)
- Google Gemini via OpenAI endpoint
- Official OpenAI or any compatible proxy.
Includes built-in resilient Simulation Mode for offline development and testing.
Zero dependencies on application-specific databases or models.
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx

from ask_bible_ai.config import AskBibleAIConfig, config as default_config
from ask_bible_ai.prompts import detect_language

logger = logging.getLogger("ask_bible_ai.client")


class OpenAICompatibleClient:
    """Async client for OpenAI-compatible chat completion endpoints."""

    def __init__(self, config: Optional[AskBibleAIConfig] = None):
        self.config = config or default_config

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _get_endpoint(self, path: str = "/chat/completions") -> str:
        base = self.config.base_url.rstrip("/")
        if base.endswith("/v1") and path.startswith("/chat"):
            return f"{base}{path}"
        elif path.startswith("/"):
            return f"{base}{path}"
        return f"{base}/{path}"

    async def health_check(self) -> Dict[str, Any]:
        """Probes the upstream provider to check reachability and model availability."""
        if self.config.simulation_mode:
            return {
                "status": "healthy",
                "mode": "simulation",
                "provider": self.config.provider_name,
                "model": self.config.model,
                "message": "Running in offline Simulation Mode",
            }

        url = self._get_endpoint("/models")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    return {
                        "status": "healthy",
                        "mode": "live",
                        "provider": self.config.provider_name,
                        "base_url": self.config.base_url,
                        "model": self.config.model,
                        "http_status": 200,
                    }
                else:
                    return {
                        "status": "warning",
                        "mode": "live",
                        "provider": self.config.provider_name,
                        "base_url": self.config.base_url,
                        "http_status": res.status_code,
                        "message": f"Endpoint responded with HTTP {res.status_code}",
                    }
        except Exception as e:
            logger.warning(f"[AskBibleAI] Upstream health probe failed ({self.config.base_url}): {e}")
            return {
                "status": "offline",
                "mode": "live",
                "provider": self.config.provider_name,
                "base_url": self.config.base_url,
                "error": str(e),
                "hint": "Ensure your FreeLLMAPI, Ollama, or API service is running, or enable simulation_mode in config.",
            }

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Sends a standard non-streaming chat completion request."""
        if self.config.simulation_mode:
            return self._generate_simulated_response(messages)

        endpoint = self._get_endpoint("/chat/completions")
        payload = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                res = await client.post(endpoint, json=payload, headers=self._get_headers())
                if res.status_code != 200:
                    error_text = res.text
                    logger.error(f"[AskBibleAI] HTTP {res.status_code} from {endpoint}: {error_text}")
                    # If upstream provider hits rate limit or error, check if simulation fallback is preferred
                    raise RuntimeError(f"Upstream AI Provider Error (HTTP {res.status_code}): {error_text}")

                return res.json()
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            logger.warning(f"[AskBibleAI] Network connection error to {endpoint}: {e}")
            # Fall back to simulation response if live server is down so application remains usable
            sim_res = self._generate_simulated_response(messages)
            sim_res["_fallback_notice"] = f"Upstream API unreachable ({e}). Displaying local theological synthesis."
            return sim_res

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens using Server-Sent Events (SSE)."""
        if self.config.simulation_mode:
            sim = self._generate_simulated_response(messages)
            content = sim["choices"][0]["message"]["content"]
            # Stream tokens with realistic pacing
            words = content.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield chunk
                await asyncio.sleep(0.015)
            return

        endpoint = self._get_endpoint("/chat/completions")
        payload = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                async with client.stream("POST", endpoint, json=payload, headers=self._get_headers()) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        raise RuntimeError(f"Streaming error (HTTP {response.status_code}): {error_body.decode('utf-8')}")

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or line == "data: [DONE]":
                            continue
                        if line.startswith("data: "):
                            raw_data = line[6:]
                            try:
                                data = json.loads(raw_data)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    yield token
                            except Exception:
                                continue
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            logger.warning(f"[AskBibleAI] Network error during stream: {e}. Falling back to simulation.")
            sim = self._generate_simulated_response(messages)
            content = sim["choices"][0]["message"]["content"]
            yield f"\n\n*[Notice: Upstream AI offline ({e}). Local fallback synthesis:]*\n\n"
            for word in content.split(" "):
                yield word + " "
                await asyncio.sleep(0.02)

    def _generate_simulated_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generates structured, theological simulated responses without external network calls.
        Detects query language (Tamil/English) and provides inspiring biblical answers.
        """
        user_query = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_query = m.get("content", "")
                break

        lang = detect_language(user_query)

        if lang == "ta":
            content = (
                f"### வேதாகம பதில்\n\n"
                f"உங்கள் கேள்வி: **\"{user_query}\"**\n\n"
                f"வேதாகமம் நமக்கு மிகுந்த ஆறுதலையும், ஞானத்தையும், வழிகாட்டுதலையும் தருகிறது.\n\n"
                f"#### முக்கிய வேதாகம பகுதிகள்:\n"
                f"1. **யோவான் 14:27 (John 14:27)**: \"சமாதானத்தை உங்களுக்கு வைத்துப்போகிறேன், என்னுடைய சமாதானத்தையே உங்களுக்குக் கொடுக்கிறேன்; உலகம் கொடுக்கிறபிரகாரம் நான் உங்களுக்குக் கொடுக்கிறதில்லை. உங்கள் இருதயம் கலங்காமலும் பயப்படாமலும் இருப்பதாக.\"\n"
                f"2. **பிலிப்பியர் 4:6-7 (Philippians 4:6-7)**: \"நீங்கள் ஒன்றுக்குங் கவலைப்படாமல், எல்லாவற்றையுங்குறித்து உங்கள் விண்ணப்பங்களை ஸ்தோத்திரத்தோடே கூடிய ஜெபத்தினாலும் வேண்டுதலினாலும் தேவனுக்குத் தெரியப்படுத்துங்கள்.\"\n"
                f"3. **சங்கீதம் 23:1 (Psalm 23:1)**: \"கர்த்தர் என் மேய்ப்பராயிருக்கிறார்; நான் தாழ்ச்சியடையேன்.\"\n\n"
                f"#### ஆவிக்குரிய தியானம்:\n"
                f"எந்த சூழ்நிலையிலும் தேவனுடைய பிரசன்னமும், அவருடைய வார்த்தையும் நம்மைத் தாங்க போதுமானது. தேவனிடத்தில் உங்கள் இருதயத்தை ஊற்றி ஜெபியுங்கள்; அவர் உங்களை ஆசீர்வதித்து நடத்துவார்.\n\n"
                f"✨ *\"உன் வழியைக் கர்த்தருக்கு ஒப்புவித்து, அவர்மேல் நம்பிக்கையாயிரு; அவரே காரியத்தை வாய்க்கப்பண்ணுவார்.\" (சங்கீதம் 37:5)*"
            )
        else:
            content = (
                f"### Biblical Reflection\n\n"
                f"Regarding your inquiry: **\"{user_query}\"**\n\n"
                f"The Holy Scriptures speak with eternal wisdom, comfort, and direct guidance on this subject.\n\n"
                f"#### Key Scripture Foundations:\n"
                f"1. **Philippians 4:6-7**: *\"Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God. And the peace of God, which transcends all understanding, will guard your hearts and your minds in Christ Jesus.\"*\n"
                f"2. **Proverbs 3:5-6**: *\"Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight.\"*\n"
                f"3. **Romans 8:28**: *\"And we know that in all things God works for the good of those who love him, who have been called according to his purpose.\"*\n\n"
                f"#### Core Theological Insights:\n"
                f"- **God's Sovereign Care:** The Bible consistently reminds us that God is mindful of our every circumstance.\n"
                f"- **The Call to Faith:** In times of uncertainty, scripture calls us to anchor our hope in God's unchanging promises rather than temporary circumstances.\n"
                f"- **Action Step:** Bring your burdens to Him in honest prayer and meditate on His Word daily.\n\n"
                f"🕊️ *\"The Lord is my light and my salvation—whom shall I fear? The Lord is the stronghold of my life—of whom shall I be afraid?\" (Psalm 27:1)*"
            )

        return {
            "id": "chatcmpl-simulated-bible-ai",
            "object": "chat.completion",
            "created": 1700000000,
            "model": self.config.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(user_query.split()) + 50,
                "completion_tokens": len(content.split()),
                "total_tokens": len(user_query.split()) + len(content.split()) + 50,
            },
        }
