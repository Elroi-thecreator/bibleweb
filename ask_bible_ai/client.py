"""
Ask Bible AI OpenAI-Compatible Client.
Connects asynchronously to any OpenAI-compatible `/v1` server:
- FreeLLMAPI (Self-hosted free-tier gateway: http://localhost:3000/v1)
- Ollama (Local private models: http://localhost:11434/v1)
- Groq Cloud (Ultra-fast inference: https://api.groq.com/openai/v1)
- Google Gemini via OpenAI endpoint
- Official OpenAI or any compatible proxy.
Includes built-in resilient Simulation & Graceful Fallback Mode for offline and fault-tolerant operation.
Zero dependencies on application-specific databases or models.
"""

import asyncio
import json
import logging
import re
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
        """Sends a standard non-streaming chat completion request with resilient fallback."""
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
                    logger.warning(f"[AskBibleAI] Upstream error HTTP {res.status_code}: {error_text}. Falling back to local synthesis.")
                    sim_res = self._generate_simulated_response(messages)
                    sim_res["_fallback_notice"] = f"Upstream API returned HTTP {res.status_code}. Displaying local scripture synthesis."
                    return sim_res

                data = res.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data
                else:
                    sim_res = self._generate_simulated_response(messages)
                    sim_res["_fallback_notice"] = "Upstream API returned empty choices. Displaying local scripture synthesis."
                    return sim_res

        except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
            logger.warning(f"[AskBibleAI] Network connection error to {endpoint}: {e}. Falling back to local synthesis.")
            sim_res = self._generate_simulated_response(messages)
            sim_res["_fallback_notice"] = f"Upstream API unreachable ({e}). Displaying local scripture synthesis."
            return sim_res

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens using Server-Sent Events (SSE) with resilient fallback."""
        if self.config.simulation_mode:
            sim = self._generate_simulated_response(messages)
            content = sim["choices"][0]["message"]["content"]
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

        emitted_any = False
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                async with client.stream("POST", endpoint, json=payload, headers=self._get_headers()) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        logger.warning(f"[AskBibleAI] Stream HTTP {response.status_code}: {error_body.decode('utf-8', errors='ignore')}. Falling back to simulation.")
                        sim = self._generate_simulated_response(messages)
                        content = sim["choices"][0]["message"]["content"]
                        for word in content.split(" "):
                            yield word + " "
                            await asyncio.sleep(0.015)
                        return

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
                                    emitted_any = True
                                    yield token
                            except Exception:
                                continue
        except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
            logger.warning(f"[AskBibleAI] Network error during stream: {e}. Falling back to simulation.")
            if not emitted_any:
                sim = self._generate_simulated_response(messages)
                content = sim["choices"][0]["message"]["content"]
                for word in content.split(" "):
                    yield word + " "
                    await asyncio.sleep(0.015)

    def _generate_simulated_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generates rich, theologically grounded simulated responses when offline or when
        upstream LLM encounters errors, ensuring users always receive an inspiring answer.
        """
        user_query = ""
        system_content = ""
        for m in messages:
            if m.get("role") == "system":
                system_content = m.get("content", "")
            elif m.get("role") == "user":
                user_query = m.get("content", "")

        lang = detect_language(user_query)
        q_lower = user_query.lower()

        # Check for specific biblical topics
        is_psalm_23 = bool(re.search(r"23|psalm 23|சங்கீதம் 23|shepherd|மேய்ப்பர்", q_lower))
        is_fear_anxiety = bool(re.search(r"anxiety|fear|worry|peace|பயம்|கவலை|சமாதானம்|திகில்", q_lower))
        is_love = bool(re.search(r"love|charity|அன்பு|நேசம்", q_lower))
        is_faith = bool(re.search(r"faith|believe|trust|விசுவாசம்|நம்பிக்கை", q_lower))

        if lang == "ta":
            if is_psalm_23:
                content = (
                    "### சங்கீதம் 23 — ஆவிக்குரிய ஆழ்ந்த தியானம்\n\n"
                    "**\"கர்த்தர் என் மேய்ப்பராயிருக்கிறார்; நான் தாழ்ச்சியடையேன்.\" (சங்கீதம் 23:1)**\n\n"
                    "தாவீது ராஜாவினால் பாடப்பட்ட சங்கீதம் 23, வேதாகமத்தின் மிக ஆறுதலான மற்றும் ஆழமான சங்கீதங்களில் ஒன்றாகும். இதன் ஆவிக்குரிய முக்கியத்துவங்கள்:\n\n"
                    "#### 1. நிறைவான தேவ பராமரிப்பு (வசனம் 1-2):\n"
                    "- *\"கர்த்தர் என் மேய்ப்பர்; நான் தாழ்ச்சியடையேன்\"*: தேவன் நம்மை வழிநடத்தும் நல்ல மேய்ப்பனாக இருக்கும்போது, நம் ஆத்துமாவிற்கு தேவையான எந்த நன்மையும் குறைவுபடாது.\n"
                    "- *\"புல்லுள்ள இடங்களில் என்னை மேய்த்து, அமர்ந்த தண்ணீர்கள் அண்டையில் என்னைக் கொண்டுபோய் விடுகிறார்\"*: உலகப் போராட்டங்களுக்கு மத்தியில் தேவனுடைய பிரசன்னம் நமக்கு மெய்யான இளைப்பாறுதலையும் சமாதானத்தையும் தருகிறது.\n\n"
                    "#### 2. வழிகாட்டுதலும் ஆத்தும இளைப்பாறுதலும் (வசனம் 3):\n"
                    "- *\"அவர் என் ஆத்துமாவைத் தேற்றி, தம்முடைய நாமத்தினிமித்தம் என்னை நீதியின் பாதைகளில் நடத்துகிறார்\"*: சோர்ந்துபோகும் வேளைகளில் தேவன் நம்மை உயிர்ப்பித்து, தம் நாம மகிமைக்காக சரியான பாதையில் வழிநடத்துகிறார்.\n\n"
                    "#### 3. மரண இருளின் பள்ளத்தாக்கில் பயமின்மை (வசனம் 4):\n"
                    "- *\"நான் மரண இருளின் பள்ளத்தாக்கிலே நடந்தாலும் பொல்லாப்புக்கு பயப்படேன்; தேவரீர் என்னோடேகூட இருக்கிறீர்; உமது கோலும் உமது தடியும் என்னைத் தேற்றும்\"*: துயரமான சூழ்நிலைகளிலும் தேவன் நம்மோடு இருக்கிறார். மேய்ப்பனின் கோல் எதிரிகளிடமிருந்து நம்மைப் பாதுகாக்கிறது; தடி வழியை விட்டு விலகாமல் நம்மைத் திருத்துகிறது.\n\n"
                    "#### 4. ஜெயமும் நித்திய ஆசீர்வாதமும் (வசனம் 5-6):\n"
                    "- *\"என் சத்துருக்களுக்கு முன்பாக எனக்கு ஒரு பந்தியை ஆயத்தப்படுத்தி, என் தலையை எண்ணெயால் அபிஷேகம் பண்ணுகிறீர்; என் பாத்திரம் நிரம்பி வழிகிறது\"*: உலக நிந்தைகளுக்கு மத்தியில் தேவன் ஜெயத்தையும், பரிசுத்த ஆவியின் அபிஷேகத்தையும் அருளுகிறார்.\n"
                    "- *\"என் ஜீவனுள்ள நாளெல்லாம் நன்மையும் கிருபையும் என்னைத் தொடரும்; நான் கர்த்தருடைய வீட்டிலே நீடித்த நாட்களாய் நிலைத்திருப்பேன்\"*: இந்த பூமியின் நன்மைகளை விட, தேவனுடன் நித்தியமாய் வாழ்வதே நம் உச்சக்கட்ட நம்பிக்கை.\n\n"
                    "🕊️ **முடிவுரை:** கர்த்தரை உங்கள் மேய்ப்பராக முழுமையாய் நம்பி, உங்கள் பாதைகளை அவரிடம் ஒப்புக்கொடுங்கள்."
                )
            elif is_fear_anxiety:
                content = (
                    "### பயம் மற்றும் கவலையை வெல்ல வேதாகமம் என்ன போதிக்கிறது?\n\n"
                    "வேதாகமத்தில் தேவன் மனிதனுக்கு அதிகமாக கொடுத்த கட்டளைகளில் ஒன்று: **\"பயப்படாதே, நான் உன்னுடனே இருக்கிறேன்\"** என்பதாகும்.\n\n"
                    "#### 1. கவலையை ஸ்தோத்திர ஜெபமாக மாற்றுங்கள்:\n"
                    "- **பிலிப்பியர் 4:6-7**: *\"நீங்கள் ஒன்றுக்குங் கவலைப்படாமல், எல்லாவற்றையுங்குறித்து உங்கள் விண்ணப்பங்களை ஸ்தோத்திரத்தோடே கூடிய ஜெபத்தினாலும் வேண்டுதலினாலும் தேவனுக்குத் தெரியப்படுத்துங்கள். அப்பொழுது, எல்லாப் புத்திக்கும் மேலான தேவ சமாதானம் உங்கள் இருதயங்களையும் உங்கள் சிந்தைகளையும் கிறிஸ்து இயேசுவுக்குள் காத்துக்கொள்ளும்.\"*\n\n"
                    "#### 2. உங்கள் பாரங்களை கர்த்தர்மேல் வையுங்கள்:\n"
                    "- **1 பேதுரு 5:7**: *\"அவர் உங்களை விசாரிக்கிறவரானபடியால், உங்கள் கவலைகளையெல்லாம் அவர்மேல் வைத்துவிடுங்கள்.\"*\n"
                    "- **சங்கீதம் 55:22**: *\"உன் பாரத்தைக் கர்த்தர்மேல் வைத்துவிடு, அவர் உன்னை ஆதரிப்பார்; நீதிமானை ஒருபோதும் தள்ளாடவொட்டார்.\"*\n\n"
                    "#### 3. தேவன் நமக்கு பயமுள்ள ஆவியை தரவில்லை:\n"
                    "- **2 தீமோத்தேயு 1:7**: *\"தேவன் நமக்கு பயமுள்ள ஆவியைக் கொடாமல், பலமும் அன்பும் தெளிந்த புத்தியுமுள்ள ஆவியையே கொடுத்திருக்கிறார்.\"*\n\n"
                    "#### 4. தேவனுடைய உடனிருப்பு அளிக்கும் தைரியம்:\n"
                    "- **ஏசாயா 41:10**: *\"நீ பயப்படாதே, நான் உன்னுடனே இருக்கிறேன்; திகையாதே, நான் உன் தேவன்; நான் உன்னைப் பலப்படுத்தி உனக்குச் சகாயம்பண்ணுவேன்; என் நீதியின் வலதுகரத்தினால் உன்னைத் தாங்குவேன்.\"*\n\n"
                    "✨ **ஆவிக்குரிய ஆலோசனை:** கவலை வரும்போது அமைதியாக தேவனுடைய சமூகத்தில் முழங்காலிட்டு, அவருடைய வாக்குத்தத்தங்களை தியானியுங்கள்; அவருடைய தெய்வீக சமாதானம் உங்கள் இருதயத்தை ஆளும்."
                )
            else:
                content = (
                    f"### வேதாகம பதில் & தியானம்\n\n"
                    f"உங்கள் கேள்வி: **\"{user_query}\"**\n\n"
                    f"வேதாகமம் நமக்கு மிகுந்த ஆறுதலையும், ஞானத்தையும், தெய்வீக வழிகாட்டுதலையும் தருகிறது.\n\n"
                    f"#### முக்கிய வேதாகம பகுதிகள்:\n"
                    f"1. **யோவான் 14:27**: \"சமாதானத்தை உங்களுக்கு வைத்துப்போகிறேன், என்னுடைய சமாதானத்தையே உங்களுக்குக் கொடுக்கிறேன்; உலகம் கொடுக்கிறபிரகாரம் நான் உங்களுக்குக் கொடுக்கிறதில்லை. உங்கள் இருதயம் கலங்காமலும் பயப்படாமலும் இருப்பதாக.\"\n"
                    f"2. **நீதிமொழிகள் 3:5-6**: \"உன் சுயபுத்தியின்மேல் சாயாமல், உன் முழு இருதயத்தோடும் கர்த்தரில் நம்பிக்கையாயிருந்து, உன் வழிகளிலெல்லாம் அவரை நினைத்துக்கொள்; அப்பொழுது அவர் உன் பாதைகளைச் செவ்வைப்படுத்துவார்.\"\n"
                    f"3. **சங்கீதம் 119:105**: \"உம்முடைய வசனம் என் கால்களுக்குத் தீபமும், என் பாதைக்கு வெளிச்சமுமாயிருக்கிறது.\"\n\n"
                    f"#### ஆவிக்குரிய தியானம்:\n"
                    f"எந்த சூழ்நிலையிலும் தேவனுடைய பிரசன்னமும், அவருடைய வார்த்தையும் நம்மைத் தாங்க போதுமானது. தேவனிடத்தில் உங்கள் இருதயத்தை ஊற்றி ஜெபியுங்கள்; அவர் உங்களை ஆசீர்வதித்து நடத்துவார்.\n\n"
                    f"✨ *\"உன் வழியைக் கர்த்தருக்கு ஒப்புவித்து, அவர்மேல் நம்பிக்கையாயிரு; அவரே காரியத்தை வாய்க்கப்பண்ணுவார்.\" (சங்கீதம் 37:5)*"
                )
        else:
            if is_psalm_23:
                content = (
                    "### Psalm 23 — A Deep Spiritual Reflection\n\n"
                    "**\"The Lord is my shepherd; I shall not want.\" (Psalm 23:1)**\n\n"
                    "Penned by King David from the heart of an experienced shepherd, Psalm 23 is revered across church history as one of scripture's most profound declarations of God's personal covenant care.\n\n"
                    "#### 1. Total Provision & Rest (Verses 1-2)\n"
                    "- *\"The Lord is my shepherd; I shall not want\"*: When Yahweh is our shepherd, no true spiritual or essential physical need will ever be lacking.\n"
                    "- *\"He makes me lie down in green pastures; He leads me beside still waters\"*: In a frantic and chaotic world, God provides genuine rest, refreshing our weary souls.\n\n"
                    "#### 2. Restoration & Righteous Direction (Verse 3)\n"
                    "- *\"He restores my soul; He leads me in paths of righteousness for His name's sake\"*: When we stumble or face exhaustion, God restores us and directs our footsteps along righteous paths to bring honor to His name.\n\n"
                    "#### 3. Fearless Walking in the Darkest Valley (Verse 4)\n"
                    "- *\"Even though I walk through the valley of the shadow of death, I will fear no evil, for You are with me; Your rod and Your staff, they comfort me\"*: Death is reduced to a mere 'shadow' through Christ. The shepherd's rod defends us against predatory enemies, and His staff gently pulls us back when we drift.\n\n"
                    "#### 4. Divine Honor & Eternal Fellowship (Verses 5-6)\n"
                    "- *\"You prepare a table before me in the presence of my enemies; You anoint my head with oil; my cup overflows\"*: God publicly vindicates and richly anoints His servants, giving a fullness of joy that cannot be snatched away.\n"
                    "- *\"Surely goodness and mercy shall follow me all the days of my life, and I shall dwell in the house of the Lord forever\"*: God's steadfast love pursues us throughout this earthly pilgrimage, culminating in eternal fellowship in His kingdom.\n\n"
                    "🕊️ **Takeaway:** Surrender control to the Good Shepherd today. Trust His rod, His staff, and His unfailing direction."
                )
            elif is_fear_anxiety:
                content = (
                    "### What Does the Bible Teach About Dealing with Anxiety & Fear?\n\n"
                    "The Holy Scriptures address anxiety, fear, and worry with compassionate realism. God does not dismiss human vulnerability, but offers **His sovereign presence and transcendent peace** as our anchor.\n\n"
                    "#### 1. Turn Worry into Prayer with Thanksgiving\n"
                    "- **Philippians 4:6-7**: *\"Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God. And the peace of God, which transcends all understanding, will guard your hearts and your minds in Christ Jesus.\"*\n"
                    "- **Core Principle**: Anxiety serves as an alarm bell prompting us to transfer our worries onto the Lord through grateful prayer.\n\n"
                    "#### 2. Cast Your Burdens Directly on God\n"
                    "- **1 Peter 5:7**: *\"Cast all your anxiety on him because he cares for you.\"*\n"
                    "- **Psalm 55:22**: *\"Cast your cares on the Lord and he will sustain you; he will never let the righteous be shaken.\"*\n"
                    "- **Core Principle**: God actively invites you to offload burdens because He possesses both the infinite strength to bear them and infinite tenderness toward you.\n\n"
                    "#### 3. Reject the Spirit of Fear\n"
                    "- **2 Timothy 1:7**: *\"For God has not given us a spirit of fear, but of power and of love and of a sound mind.\"*\n"
                    "- **Core Principle**: Paralyzing dread does not come from heaven. The Holy Spirit imparts resilience, sacrificial love, and mental calmness.\n\n"
                    "#### 4. Anchor in God's Unshakable Presence\n"
                    "- **Isaiah 41:10**: *\"Fear not, for I am with you; be not dismayed, for I am your God. I will strengthen you, yes, I will help you, I will uphold you with my righteous right hand.\"*\n"
                    "- **Joshua 1:9**: *\"Be strong and courageous. Do not be frightened, and do not be dismayed, for the Lord your God is with you wherever you go.\"*\n\n"
                    "✨ **Pastoral Takeaway:** You do not have to carry tomorrow's uncertainties today. Rest in the arms of the God who has already conquered them."
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
                    f"- **The Call to Faith:** In times of uncertainty, scripture calls us to anchor our hope in God's unchanging promises.\n"
                    f"- **Action Step:** Bring your questions and needs to Him in prayer and meditate on His Word daily.\n\n"
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
