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
from whatsapp_gateway.routes.webhook import get_client
from whatsapp_gateway.subscribers import get_active_subscribers, get_subscriber_count
from whatsapp_gateway.scheduler.devotional_push import push_daily_devotional
from app.db import DB_PATH, SONGS_DB_PATH

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
    wa_client = get_client()

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
            "wa_subscribers": subscribers,
            "wa_subscribers_count": subscribers_count,
            "db_stats": db_stats,
            "queue_status": queue_status,
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
    queue_enabled = body.get("queue_enabled")
    rabbitmq_url = body.get("rabbitmq_url")

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

    if gateway_url is not None:
        gateway_url = gateway_url.strip()
        if gateway_url and not (gateway_url.startswith("http://") or gateway_url.startswith("https://")):
            raise HTTPException(status_code=400, detail="Gateway URL must begin with http:// or https://")

    # Persist configuration overrides to data/whatsapp_config.json
    saved = save_persisted_config(
        gateway_url=gateway_url,
        session_id=session_id,
        api_key=api_key,
        enable_simulation_mode=enable_simulation_mode,
        queue_enabled=queue_enabled,
        rabbitmq_url=rabbitmq_url,
    )

    # Dynamically update the active WAClient runtime singleton
    wa_client = get_client()
    wa_client.update_config(
        base_url=saved.get("gateway_url"),
        default_session_id=saved.get("session_id"),
        api_key=saved.get("api_key"),
        simulation_mode=saved.get("enable_simulation_mode"),
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
        "message": "WhatsApp Gateway & Queue configuration saved successfully!",
        "config": {
            "gateway_url": wa_client.base_url,
            "session_id": wa_client.default_session_id,
            "has_api_key": bool(wa_client.api_key),
            "simulation_mode": wa_client.simulation_mode,
            "queue_enabled": saved.get("queue_enabled", False),
            "rabbitmq_url": saved.get("rabbitmq_url"),
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
    wa_client = get_client()
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
    """Tests HTTP reachability and latency of the configured WA-AKG gateway."""
    require_admin(request)
    wa_client = get_client()

    target_url = f"{wa_client.base_url.rstrip('/')}/sessions/{wa_client.default_session_id}"
    t0 = time.time()
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {}
            if wa_client.api_key:
                headers["Authorization"] = f"Bearer {wa_client.api_key}"
                headers["x-api-key"] = wa_client.api_key
            resp = await client.get(target_url, headers=headers)
            latency = round((time.time() - t0) * 1000, 1)
            return {
                "status": "ok" if resp.is_success else "warning",
                "http_status": resp.status_code,
                "latency_ms": latency,
                "message": f"Gateway reached at {target_url} (HTTP {resp.status_code})",
            }
    except Exception as e:
        latency = round((time.time() - t0) * 1000, 1)
        return {
            "status": "error",
            "latency_ms": latency,
            "message": f"Could not reach {target_url} ({str(e)})",
        }
