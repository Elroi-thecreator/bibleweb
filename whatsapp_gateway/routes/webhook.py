"""
FastAPI Router for WA-AKG Webhook reception, chat simulation, and devotional management.
Can be mounted on any FastAPI application with a single `app.include_router(...)`.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, Response
from pydantic import BaseModel

from whatsapp_gateway.config import config
from whatsapp_gateway.client.client import WAClient
from whatsapp_gateway.client.models import IncomingWebhookPayload, MediaType, SendMessageResponse
from whatsapp_gateway.bot.context import MessageContext
from whatsapp_gateway.bot.dispatcher import BotDispatcher
from whatsapp_gateway.bot.session_store import InMemorySessionStore
from whatsapp_gateway.adapters.bible_adapter import register_bible_handlers
from whatsapp_gateway.subscribers import get_active_subscribers, get_subscriber_count
from whatsapp_gateway.scheduler.devotional_push import push_daily_devotional
from whatsapp_gateway.queue.manager import queue_manager

logger = logging.getLogger("whatsapp_gateway.routes")

router = APIRouter()

# Singletons for the gateway runtime
_session_store = InMemorySessionStore(default_ttl=config.session_ttl_seconds)
_client = WAClient(
    base_url=config.gateway_url,
    default_session_id=config.session_id,
    api_key=config.api_key,
    timeout=config.timeout_seconds,
    simulation_mode=config.enable_simulation_mode,
)
_dispatcher = BotDispatcher(command_prefix=config.command_prefix)

# Automatically register domain handlers
register_bible_handlers(_dispatcher)

# Initialize queue manager with bot dependencies
queue_manager.initialize(dispatcher=_dispatcher, client=_client, session_store=_session_store)


def get_client() -> WAClient:
    return _client


def get_dispatcher() -> BotDispatcher:
    return _dispatcher


def get_session_store() -> InMemorySessionStore:
    return _session_store


class BroadcastRequest(BaseModel):
    """Payload for administrative broadcast messages."""
    recipients: List[str]
    message: str
    session_id: Optional[str] = None


class SimulateRequest(BaseModel):
    """Payload for browser chat simulator."""
    text: str
    sender: Optional[str] = "web-simulator@s.whatsapp.net"


class BroadcastAllRequest(BaseModel):
    """Payload to broadcast to all registered active subscribers."""
    message: str


class SimulatorClient(WAClient):
    """Intercepts outgoing messages in simulation mode to return them in HTTP JSON."""
    def __init__(self):
        super().__init__(simulation_mode=True)
        self.captured_replies: List[Dict[str, Any]] = []

    async def send_text(self, to: str, text: str, session_id: Optional[str] = None) -> SendMessageResponse:
        self.captured_replies.append({"type": "text", "text": text, "to": to})
        return SendMessageResponse(success=True, message_id="sim-msg-123", to=to)

    async def send_media(
        self,
        to: str,
        media_type: Any = MediaType.AUDIO,
        file_path: Optional[Any] = None,
        file_bytes: Optional[bytes] = None,
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        ptt: bool = False,
        session_id: Optional[str] = None,
    ) -> SendMessageResponse:
        m_type = media_type.value if isinstance(media_type, MediaType) else str(media_type)
        self.captured_replies.append({
            "type": "media",
            "media_type": m_type,
            "caption": caption,
            "to": to,
        })
        return SendMessageResponse(success=True, message_id="sim-media-456", to=to)


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
) -> Dict[str, Any]:
    """
    Webhook endpoint to ingest real-time events from WA-AKG / Baileys.
    """
    if config.webhook_secret and x_webhook_secret != config.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    try:
        raw_json = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}")

    try:
        payload = IncomingWebhookPayload.model_validate(raw_json)
    except Exception as exc:
        logger.warning("Unrecognized webhook schema: %s", exc)
        return {"status": "ignored", "reason": "unrecognized schema"}

    if payload.is_from_me():
        return {"status": "ignored", "reason": "from_me"}

    text = payload.get_text_content()
    sender = payload.get_sender_jid()

    if not sender or not text:
        return {"status": "ignored", "reason": "no text or sender"}

    # Enqueue via RabbitMQ (if enabled & connected) or execute via direct in-memory dispatcher
    dispatch_res = await queue_manager.enqueue_incoming(
        payload=payload,
        session_id=payload.session_id or _client.default_session_id,
    )

    return {
        **dispatch_res,
        "sender": sender,
        "text_preview": text[:40],
    }


@router.post("/simulate")
async def simulate_chat(req: SimulateRequest) -> Dict[str, Any]:
    """
    Interactive simulation endpoint for browser testing.
    Dispatches message and captures replies synchronously.
    """
    sim_client = SimulatorClient()
    fake_payload = IncomingWebhookPayload(
        event="messages.upsert",
        sessionId="default",
        data={
            "key": {"remoteJid": req.sender, "fromMe": False, "id": "sim_web_001"},
            "pushName": "Web User",
            "message": {"conversation": req.text},
        },
    )

    ctx = MessageContext(
        payload=fake_payload,
        client=sim_client,
        session_store=_session_store,
    )

    await _dispatcher.dispatch(ctx)

    return {
        "success": True,
        "input": req.text,
        "replies": sim_client.captured_replies,
    }


@router.get("/status")
async def get_gateway_status() -> Dict[str, Any]:
    """
    Health check, session status, and subscriber metrics endpoint.
    """
    session_info = await _client.get_session_status()
    sub_count = await get_subscriber_count()
    return {
        "gateway_url": _client.base_url,
        "session_id": _client.default_session_id,
        "simulation_mode": _client.simulation_mode,
        "session_status": session_info,
        "active_dialogue_sessions": len(_session_store._store),
        "subscriber_count": sub_count,
        "queue": queue_manager.get_status(),
    }


class QueueConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    rabbitmq_url: Optional[str] = None


@router.get("/queue/status")
async def get_queue_status_endpoint() -> Dict[str, Any]:
    """Returns real-time RabbitMQ queue status, connection health, and telemetry."""
    return queue_manager.get_status()


@router.post("/queue/toggle")
async def toggle_queue_mode_endpoint() -> Dict[str, Any]:
    """Toggles WhatsApp task queue mode on/off at runtime."""
    new_state = not queue_manager.is_enabled
    return await queue_manager.set_enabled(new_state)


@router.post("/queue/config")
async def update_queue_config_endpoint(req: QueueConfigRequest) -> Dict[str, Any]:
    """Updates RabbitMQ connection configuration and enabled state."""
    enabled = req.enabled if req.enabled is not None else queue_manager.is_enabled
    return await queue_manager.set_enabled(enabled=enabled, rabbitmq_url=req.rabbitmq_url)


@router.post("/toggle-simulation")
async def toggle_simulation_mode() -> Dict[str, Any]:
    """
    Toggles between Simulation Mode and Live WA-AKG Gateway mode.
    """
    _client.simulation_mode = not _client.simulation_mode
    return {
        "simulation_mode": _client.simulation_mode,
        "mode_label": "Simulation (Mock Active)" if _client.simulation_mode else "Live Gateway",
    }



@router.post("/push-devotional")
async def trigger_push_devotional() -> Dict[str, Any]:
    """
    Admin trigger to immediately broadcast today's devotional to all active subscribers.
    """
    result = await push_daily_devotional(client=_client)
    return result


@router.post("/broadcast-all")
async def broadcast_to_all_subscribers(req: BroadcastAllRequest) -> Dict[str, Any]:
    """
    Broadcasts custom message to all active subscribers.
    """
    subscribers = await get_active_subscribers()
    if not subscribers:
        return {"total": 0, "success": 0, "message": "No active subscribers found."}

    success = 0
    for sub in subscribers:
        try:
            res = await _client.send_text(to=sub["phone_number"], text=req.message)
            if res.success:
                success += 1
        except Exception:
            pass

    return {
        "total": len(subscribers),
        "success": success,
        "failed": len(subscribers) - success,
    }


@router.post("/broadcast")
async def broadcast_message(req: BroadcastRequest) -> Dict[str, Any]:
    """
    Admin endpoint to broadcast devotional messages to explicit recipient lists.
    """
    if not req.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty.")

    results: List[Dict[str, Any]] = []
    for recipient in req.recipients:
        try:
            res = await _client.send_text(
                to=recipient,
                text=req.message,
                session_id=req.session_id,
            )
            results.append({
                "to": recipient,
                "success": res.success,
                "message_id": res.message_id,
                "error": res.error,
            })
        except Exception as exc:
            results.append({"to": recipient, "success": False, "error": str(exc)})

    return {
        "total": len(req.recipients),
        "results": results,
    }
