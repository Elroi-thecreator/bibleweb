"""
Admin Routes and System Management API.
Provides endpoints for the Admin Login, Settings/Configuration Dashboard,
Cache Purging, WhatsApp Mode Switching, and Devotional Broadcast Control.
"""

import asyncio
import os
import platform
import time
from typing import Optional
from urllib.parse import parse_qs
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.admin.auth import (
    COOKIE_NAME,
    authenticate_credentials,
    create_session_token,
    get_authenticated_admin,
    require_admin,
)
from whatsapp_gateway.config import config as wa_config, save_persisted_config
from whatsapp_gateway.providers.registry import provider_registry
def _get_wa_client():
    from whatsapp_gateway.routes.webhook import get_client
    return get_client()
from whatsapp_gateway.subscribers import get_active_subscribers, get_subscriber_count
from whatsapp_gateway.scheduler.devotional_push import push_daily_devotional
from whatsapp_gateway.rate_limiter import rate_limiter
from app.db import DB_PATH, SONGS_DB_PATH
from ask_bible_ai.config import config as ai_config, save_persisted_config as save_ai_config
from ask_bible_ai.routes import ai_service

router = APIRouter()


def _get_app_context():
    """Lazily retrieve main application caches and runtime references to avoid circular imports."""
    from app.main import AUDIO_CACHE, HTML_PAGE_CACHE, START_TIME, templates
    return HTML_PAGE_CACHE, AUDIO_CACHE, START_TIME, templates


def _format_uptime(seconds: float) -> str:
    """Formats seconds into human-readable duration string."""
    mins, sec = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    days, hrs = divmod(hrs, 24)
    if days > 0:
        return f"{days}d {hrs}h {mins}m"
    if hrs > 0:
        return f"{hrs}h {mins}m {sec}s"
    return f"{mins}m {sec}s"


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_root(request: Request):
    """Admin root redirects directly to /admin/settings."""
    return RedirectResponse(url="/admin/settings", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, next: Optional[str] = "/admin/settings", msg: Optional[str] = None):
    """Renders the Administrator Login page."""
    user = get_authenticated_admin(request)
    if user:
        return RedirectResponse(url=next or "/admin/settings", status_code=303)

    _, _, _, templates = _get_app_context()
    info_msg = None
    if msg == "logged_out":
        info_msg = "You have been safely signed out."

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "next_url": next,
            "info": info_msg,
            "error": None,
            "username": os.getenv("ADMIN_USERNAME", "admin"),
        },
    )


async def _parse_form_data(request: Request) -> dict:
    """Parses URL-encoded or multipart form body without forcing python-multipart dependency."""
    try:
        body = await request.body()
        parsed = parse_qs(body.decode("utf-8", errors="replace"))
        return {k: v[0] if v else "" for k, v in parsed.items()}
    except Exception:
        return {}


@router.post("/login", response_class=HTMLResponse)
async def admin_login_submit(request: Request):
    """Processes admin credentials, issues an HMAC session cookie, and redirects."""
    _, _, _, templates = _get_app_context()
    form_data = await _parse_form_data(request)
    username = form_data.get("username", "")
    password = form_data.get("password", "")
    next_url = form_data.get("next", "/admin/settings")

    if authenticate_credentials(username, password):
        token = create_session_token(username.strip())
        target_url = next_url if (next_url and next_url.startswith("/admin")) else "/admin/settings"
        response = RedirectResponse(url=target_url, status_code=303)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            samesite="lax",
            path="/",
        )
        return response

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "next_url": next_url,
            "error": "Invalid admin username or password. Please try again.",
            "username": username,
        },
        status_code=401,
    )


@router.get("/logout")
@router.post("/logout")
async def admin_logout(request: Request):
    """Clears the admin session cookie and redirects to login."""
    response = RedirectResponse(url="/admin/login?msg=logged_out", status_code=303)
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return response


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings_page(request: Request):
    """Main Administrator Configuration & System Telemetry Dashboard."""
    # Enforce admin authentication
    user = get_authenticated_admin(request)
    if not user:
        return RedirectResponse(url=f"/admin/login?next={request.url.path}", status_code=303)

    html_cache, audio_cache, start_time, templates = _get_app_context()
    wa_client = _get_wa_client()

    # 1. System Telemetry & Process Info
    uptime_sec = time.time() - start_time
    uptime_str = _format_uptime(uptime_sec)

    try:
        import psutil
        proc = psutil.Process()
        mem_rss_mb = round(proc.memory_info().rss / (1024 * 1024), 1)
        mem_pct = round(psutil.virtual_memory().percent, 1)
    except Exception:
        mem_rss_mb = 0.0
        mem_pct = 0.0

    sys_info = {
        "os_name": platform.system(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "pid": os.getpid(),
        "is_render": bool(os.getenv("RENDER")),
    }

    # 2. Cache Statistics
    cache_stats = html_cache.stats()
    audio_stats = audio_cache.stats()

    # 3. WhatsApp Gateway Status & Active Subscribers
    wa_simulation = wa_client.simulation_mode
    subscribers = await get_active_subscribers()
    subscribers_count = len(subscribers)

    # 4. Embedded SQLite Database Telemetry
    def _get_db_telemetry():
        bible_mb = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2) if os.path.exists(DB_PATH) else 0.0
        songs_mb = round(os.path.getsize(SONGS_DB_PATH) / (1024 * 1024), 2) if os.path.exists(SONGS_DB_PATH) else 0.0

        sub_db_path = os.path.join(os.path.dirname(DB_PATH), "whatsapp_subscribers.sqlite.db")
        sub_kb = round(os.path.getsize(sub_db_path) / 1024, 1) if os.path.exists(sub_db_path) else 0.0

        return {
            "bible_path": DB_PATH,
            "bible_size_mb": bible_mb,
            "bible_verses_count": "31,102",
            "songs_path": SONGS_DB_PATH,
            "songs_size_mb": songs_mb,
            "songs_count": "2,300+",
            "song_books_count": 13,
            "subscribers_path": sub_db_path,
            "subscribers_size_kb": sub_kb,
        }

    db_stats = await asyncio.to_thread(_get_db_telemetry)

    # 5. WhatsApp RabbitMQ Queue Telemetry
    from whatsapp_gateway.queue.manager import queue_manager
    queue_status = queue_manager.get_status()

    # 6. Ask Bible AI Plugin Telemetry
    try:
        ai_health = await ai_service.health()
    except Exception as e:
        ai_health = {"status": "error", "error": str(e)}

    return templates.TemplateResponse(
        request=request,
        name="admin/settings.html",
        context={
            "username": user,
            "uptime_formatted": uptime_str,
            "memory_rss_mb": mem_rss_mb,
            "memory_percent": mem_pct,
            "sys_info": sys_info,
            "cache_stats": cache_stats,
            "audio_stats": audio_stats,
            "wa_config": wa_config,
            "wa_simulation": wa_simulation,
            "wa_provider": getattr(wa_client, "provider", "wa_akg"),
            "wa_providers": provider_registry.list_providers(),
            "wa_subscribers": subscribers,
            "wa_subscribers_count": subscribers_count,
            "db_stats": db_stats,
            "queue_status": queue_status,
            "rate_limiter_stats": rate_limiter.get_stats(),
            "ai_config": ai_config.to_dict(),
            "ai_health": ai_health,
        },
    )


# =====================================================================
# Administrative Action APIs (Protected by require_admin)
# =====================================================================

@router.post("/api/cache/clear-html")
async def api_clear_html_cache(request: Request):
    """Purges the in-memory pre-rendered HTML page cache."""
    require_admin(request)
    html_cache, _, _, _ = _get_app_context()
    prev_size = html_cache.size()
    html_cache.clear()
    return {"status": "ok", "message": f"HTML Page Cache cleared ({prev_size} pages evicted)."}


@router.post("/api/cache/clear-audio")
async def api_clear_audio_cache(request: Request):
    """Purges the in-memory and disk persistent Text-to-Speech audio cache."""
    require_admin(request)
    _, audio_cache, _, _ = _get_app_context()
    audio_cache.clear(purge_disk=True)
    return {"status": "ok", "message": "Text-to-Speech audio cache (memory & disk) cleared."}


@router.post("/api/whatsapp/config")
async def api_update_wa_config(request: Request):
    """
    Updates and persists WhatsApp Gateway URL, session ID, API key,
    and simulation mode at runtime.
    """
    require_admin(request)
    try:
        body = await request.json()
    except Exception:
        body = await _parse_form_data(request)

    gateway_url = body.get("gateway_url")
    session_id = body.get("session_id")
    api_key = body.get("api_key")
    enable_simulation_mode = body.get("enable_simulation_mode")
    provider = body.get("provider")
    meta_phone_number_id = body.get("meta_phone_number_id")
    meta_waba_id = body.get("meta_waba_id")
    meta_access_token = body.get("meta_access_token")
    meta_verify_token = body.get("meta_verify_token")
    meta_app_secret = body.get("meta_app_secret")
    meta_api_version = body.get("meta_api_version")
    queue_enabled = body.get("queue_enabled")
    rabbitmq_url = body.get("rabbitmq_url")
    rate_limit_enabled = body.get("rate_limit_enabled")
    rate_limit_requests_per_minute = body.get("rate_limit_requests_per_minute")
    rate_limit_audio_per_day = body.get("rate_limit_audio_per_day")
    rate_limit_cooldown_seconds = body.get("rate_limit_cooldown_seconds")
    rate_limit_whitelist = body.get("rate_limit_whitelist")

    if enable_simulation_mode is not None:
        if isinstance(enable_simulation_mode, str):
            enable_simulation_mode = enable_simulation_mode.lower() in ("true", "1", "yes", "on")
        else:
            enable_simulation_mode = bool(enable_simulation_mode)

    if queue_enabled is not None:
        if isinstance(queue_enabled, str):
            queue_enabled = queue_enabled.lower() in ("true", "1", "yes", "on")
        else:
            queue_enabled = bool(queue_enabled)

    if rate_limit_enabled is not None:
        if isinstance(rate_limit_enabled, str):
            rate_limit_enabled = rate_limit_enabled.lower() in ("true", "1", "yes", "on")
        else:
            rate_limit_enabled = bool(rate_limit_enabled)

    if rate_limit_whitelist is not None and isinstance(rate_limit_whitelist, str):
        rate_limit_whitelist = [x.strip() for x in rate_limit_whitelist.split(",") if x.strip()]

    if gateway_url is not None:
        gateway_url = gateway_url.strip()
        if gateway_url and not (gateway_url.startswith("http://") or gateway_url.startswith("https://")):
            raise HTTPException(status_code=400, detail="Gateway URL must begin with http:// or https://")

    # Persist configuration overrides to data/whatsapp_config.json
    saved = save_persisted_config(
        provider=provider,
        gateway_url=gateway_url,
        session_id=session_id,
        api_key=api_key,
        enable_simulation_mode=enable_simulation_mode,
        meta_phone_number_id=meta_phone_number_id,
        meta_waba_id=meta_waba_id,
        meta_access_token=meta_access_token,
        meta_verify_token=meta_verify_token,
        meta_app_secret=meta_app_secret,
        meta_api_version=meta_api_version,
        queue_enabled=queue_enabled,
        rabbitmq_url=rabbitmq_url,
        rate_limit_enabled=rate_limit_enabled,
        rate_limit_requests_per_minute=rate_limit_requests_per_minute,
        rate_limit_audio_per_day=rate_limit_audio_per_day,
        rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
        rate_limit_whitelist=rate_limit_whitelist,
    )

    # Dynamically update the active WAClient runtime singleton
    wa_client = _get_wa_client()
    wa_client.update_config(
        base_url=saved.get("gateway_url"),
        default_session_id=saved.get("session_id"),
        api_key=saved.get("api_key"),
        simulation_mode=saved.get("enable_simulation_mode"),
        provider=saved.get("provider"),
        meta_phone_number_id=saved.get("meta_phone_number_id"),
        meta_waba_id=saved.get("meta_waba_id"),
        meta_access_token=saved.get("meta_access_token"),
        meta_verify_token=saved.get("meta_verify_token"),
        meta_app_secret=saved.get("meta_app_secret"),
        meta_api_version=saved.get("meta_api_version"),
    )

    # Dynamically update QueueManager if queue settings changed
    from whatsapp_gateway.queue.manager import queue_manager
    if queue_enabled is not None or rabbitmq_url is not None:
        await queue_manager.set_enabled(
            enabled=saved.get("queue_enabled", False),
            rabbitmq_url=saved.get("rabbitmq_url"),
        )

    return {
        "status": "ok",
        "message": "WhatsApp Provider & Rate Limiter configuration saved successfully!",
        "config": {
            "provider": getattr(wa_client, "provider", "wa_akg"),
            "gateway_url": wa_client.base_url,
            "session_id": wa_client.default_session_id,
            "has_api_key": bool(wa_client.api_key),
            "simulation_mode": wa_client.simulation_mode,
            "meta_phone_number_id": saved.get("meta_phone_number_id"),
            "meta_waba_id": saved.get("meta_waba_id"),
            "has_meta_access_token": bool(saved.get("meta_access_token")),
            "meta_verify_token": saved.get("meta_verify_token"),
            "meta_api_version": saved.get("meta_api_version"),
            "queue_enabled": saved.get("queue_enabled", False),
            "rabbitmq_url": saved.get("rabbitmq_url"),
            "rate_limit_enabled": saved.get("rate_limit_enabled", True),
            "rate_limit_requests_per_minute": saved.get("rate_limit_requests_per_minute", 20),
            "rate_limit_audio_per_day": saved.get("rate_limit_audio_per_day", 15),
            "rate_limit_cooldown_seconds": saved.get("rate_limit_cooldown_seconds", 30),
            "rate_limit_whitelist": saved.get("rate_limit_whitelist", []),
        },
    }


@router.post("/api/whatsapp/queue/toggle")
async def api_toggle_wa_queue(request: Request):
    """Toggles WhatsApp task queue mode on/off at runtime."""
    require_admin(request)
    from whatsapp_gateway.queue.manager import queue_manager
    new_state = not queue_manager.is_enabled
    res = await queue_manager.set_enabled(new_state)
    return {
        "status": "ok",
        "queue": res,
        "message": f"WhatsApp RabbitMQ Queue {'enabled' if new_state else 'disabled (direct mode)'}.",
    }


@router.post("/api/whatsapp/queue/ping")
async def api_ping_rabbitmq(request: Request):
    """Tests connectivity to the configured RabbitMQ broker."""
    require_admin(request)
    from whatsapp_gateway.queue.manager import queue_manager
    from whatsapp_gateway.config import config
    from whatsapp_gateway.queue.connection import RabbitMQConnection, mask_amqp_url

    test_conn = RabbitMQConnection(url=config.rabbitmq_url)
    t0 = time.time()
    try:
        connected = await test_conn.connect(timeout=3.0)
        latency = round((time.time() - t0) * 1000, 1)
        await test_conn.close()
        if connected:
            return {
                "status": "ok",
                "latency_ms": latency,
                "message": f"RabbitMQ broker connected at {mask_amqp_url(config.rabbitmq_url)} ({latency}ms)",
            }
        else:
            return {
                "status": "warning",
                "latency_ms": latency,
                "message": f"RabbitMQ broker offline or unreachable at {mask_amqp_url(config.rabbitmq_url)} (fallback direct mode active)",
            }
    except Exception as exc:
        latency = round((time.time() - t0) * 1000, 1)
        return {
            "status": "error",
            "latency_ms": latency,
            "message": f"RabbitMQ connection failed: {exc}",
        }


@router.post("/api/whatsapp/toggle-simulation")
async def api_toggle_wa_simulation(request: Request):
    """Toggles WhatsApp gateway between Live Gateway Mode and Simulation Mode."""
    require_admin(request)
    wa_client = _get_wa_client()
    new_mode = not wa_client.simulation_mode
    wa_client.simulation_mode = new_mode
    save_persisted_config(enable_simulation_mode=new_mode)
    return {
        "status": "ok",
        "simulation_mode": new_mode,
        "message": f"WhatsApp Gateway switched to {'Simulation Mode' if new_mode else 'Live Gateway Mode'}.",
    }


@router.post("/api/whatsapp/broadcast-devotional")
async def api_broadcast_devotional(request: Request):
    """Manually dispatches the daily devotional broadcast to all active subscribers."""
    require_admin(request)
    result = await push_daily_devotional()
    return {
        "status": "ok",
        "delivered": result.get("delivered", 0),
        "total": result.get("total", 0),
        "message": f"Successfully delivered daily devotional to {result.get('delivered', 0)} of {result.get('total', 0)} subscribers.",
    }


@router.post("/api/whatsapp/ping-gateway")
async def api_ping_wa_gateway(request: Request):
    """Tests connectivity, reachability and latency of the active WhatsApp gateway or Meta Cloud API."""
    require_admin(request)
    wa_client = _get_wa_client()

    t0 = time.time()
    try:
        ping_res = await wa_client.ping()
        latency = round((time.time() - t0) * 1000, 1)
        status_str = ping_res.get("status", "ok")
        return {
            "status": status_str,
            "latency_ms": latency,
            "provider": getattr(wa_client, "provider", "wa_akg"),
            "message": ping_res.get("message", "Ping successful"),
            "details": ping_res.get("details", {}),
        }
    except Exception as e:
        latency = round((time.time() - t0) * 1000, 1)
        return {
            "status": "error",
            "latency_ms": latency,
            "provider": getattr(wa_client, "provider", "wa_akg"),
            "message": f"Gateway probe failed: {str(e)}",
        }


@router.post("/api/whatsapp/rate-limiter/toggle")
async def api_toggle_wa_rate_limiter(request: Request):
    """Toggles WhatsApp rate limiting and quota enforcement on/off at runtime."""
    require_admin(request)
    new_state = not wa_config.rate_limit_enabled
    save_persisted_config(rate_limit_enabled=new_state)
    return {
        "status": "ok",
        "enabled": new_state,
        "message": f"WhatsApp Rate Limiter {'enabled' if new_state else 'disabled'}.",
        "rate_limiter": rate_limiter.get_stats(),
    }


@router.post("/api/whatsapp/rate-limiter/config")
async def api_update_wa_rate_limiter_config(request: Request):
    """Updates WhatsApp rate limiter thresholds and whitelist numbers."""
    require_admin(request)
    try:
        body = await request.json()
    except Exception:
        body = await _parse_form_data(request)

    enabled = body.get("enabled")
    if enabled is not None:
        if isinstance(enabled, str):
            enabled = enabled.lower() in ("true", "1", "yes", "on")
        else:
            enabled = bool(enabled)

    rpm = body.get("requests_per_minute")
    daily_audio = body.get("daily_audio_limit")
    cooldown = body.get("cooldown_seconds")
    whitelist_raw = body.get("whitelist")

    whitelist = None
    if whitelist_raw is not None:
        if isinstance(whitelist_raw, str):
            whitelist = [x.strip() for x in whitelist_raw.split(",") if x.strip()]
        elif isinstance(whitelist_raw, list):
            whitelist = [str(x).strip() for x in whitelist_raw if str(x).strip()]

    save_persisted_config(
        rate_limit_enabled=enabled,
        rate_limit_requests_per_minute=rpm,
        rate_limit_audio_per_day=daily_audio,
        rate_limit_cooldown_seconds=cooldown,
        rate_limit_whitelist=whitelist,
    )

    return {
        "status": "ok",
        "message": "WhatsApp Rate Limiter settings updated successfully!",
        "rate_limiter": rate_limiter.get_stats(),
    }


@router.post("/api/whatsapp/rate-limiter/reset")
async def api_reset_wa_rate_limiter(request: Request):
    """Resets all active rate limiter windows and daily audio counters."""
    require_admin(request)
    rate_limiter.clear_all()
    return {
        "status": "ok",
        "message": "WhatsApp Rate Limiter tracking and daily quotas have been reset.",
        "rate_limiter": rate_limiter.get_stats(),
    }


# =====================================================================
# Ask Bible AI Configuration & Telemetry APIs (Protected by require_admin)
# =====================================================================

@router.post("/api/ai/config")
async def api_update_ai_config(request: Request):
    """
    Updates and persists Ask Bible AI configuration at runtime.
    Protected strictly by require_admin.
    """
    require_admin(request)
    try:
        body = await request.json()
    except Exception:
        body = await _parse_form_data(request)

    updates = {}

    if "enabled" in body:
        val = body["enabled"]
        if isinstance(val, str):
            val = val.lower() in ("true", "1", "yes", "on")
        updates["enabled"] = bool(val)

    if "provider_name" in body and body["provider_name"]:
        updates["provider_name"] = str(body["provider_name"]).strip()

    if "base_url" in body and body["base_url"]:
        url = str(body["base_url"]).strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            raise HTTPException(status_code=400, detail="Base URL must start with http:// or https://")
        updates["base_url"] = url

    if "api_key" in body and body["api_key"] is not None:
        val = str(body["api_key"]).strip()
        # If masked with ellipsis, keep previous key
        if "..." not in val:
            updates["api_key"] = val

    if "model" in body and body["model"]:
        updates["model"] = str(body["model"]).strip()

    if "temperature" in body and body["temperature"] != "":
        try:
            updates["temperature"] = float(body["temperature"])
        except ValueError:
            pass

    if "max_tokens" in body and body["max_tokens"] != "":
        try:
            updates["max_tokens"] = int(body["max_tokens"])
        except ValueError:
            pass

    if "enable_grounding" in body:
        val = body["enable_grounding"]
        if isinstance(val, str):
            val = val.lower() in ("true", "1", "yes", "on")
        updates["enable_grounding"] = bool(val)

    if "max_grounding_passages" in body and body["max_grounding_passages"] != "":
        try:
            updates["max_grounding_passages"] = int(body["max_grounding_passages"])
        except ValueError:
            pass

    if "simulation_mode" in body:
        val = body["simulation_mode"]
        if isinstance(val, str):
            val = val.lower() in ("true", "1", "yes", "on")
        updates["simulation_mode"] = bool(val)

    new_cfg = save_ai_config(updates)
    ai_service.config = new_cfg
    ai_service.client.config = new_cfg

    return {
        "status": "ok",
        "message": "Ask Bible AI configuration updated successfully!",
        "config": new_cfg.to_dict(),
    }


@router.post("/api/ai/test")
async def api_test_ai_connection(request: Request):
    """
    Triggers live health check and provider probe for Ask Bible AI.
    Protected strictly by require_admin.
    """
    require_admin(request)
    health = await ai_service.health()
    return {
        "status": "ok",
        "health": health,
    }
