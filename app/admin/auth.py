"""
Admin Authentication and Security Module.
Provides session token generation, HMAC-SHA256 signature verification,
timing-attack-resistant credential checking, and FastAPI route guard dependencies.
"""

import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

COOKIE_NAME = "bible_admin_session"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

# Configurable administrator credentials
DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Secret key for HMAC token signing (falls back to a stable pseudo-secret if unset)
SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
if not SECRET_KEY:
    # Stable machine-tied fallback to avoid invalidating sessions on worker reloads
    _seed = f"{DEFAULT_ADMIN_PASSWORD}:{os.name}:{os.path.abspath(__file__)}"
    SECRET_KEY = hashlib.sha256(_seed.encode("utf-8")).hexdigest()


def authenticate_credentials(username: str, password: str) -> bool:
    """Validates admin credentials using constant-time string comparison."""
    if not username or not password:
        return False
    current_user = os.getenv("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)
    current_pass = os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)

    user_match = secrets.compare_digest(username.strip(), current_user)
    pass_match = secrets.compare_digest(password.strip(), current_pass)
    return user_match and pass_match


def create_session_token(username: str) -> str:
    """Generates an HMAC-SHA256 signed session token."""
    now = int(time.time())
    payload = f"{username}:{now}"
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    raw = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def verify_session_token(token: str) -> Optional[str]:
    """
    Validates a session token:
    1. Decodes base64 payload.
    2. Verifies HMAC-SHA256 signature using constant-time comparison.
    3. Checks token expiration against SESSION_TTL_SECONDS.
    Returns username if valid, otherwise None.
    """
    if not token or not isinstance(token, str):
        return None
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        parts = raw.split(":")
        if len(parts) != 3:
            return None
        username, timestamp_str, received_sig = parts
        timestamp = int(timestamp_str)

        # Check expiration
        if time.time() - timestamp > SESSION_TTL_SECONDS:
            return None

        # Verify signature
        payload = f"{username}:{timestamp}"
        expected_sig = hmac.new(
            SECRET_KEY.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not secrets.compare_digest(received_sig, expected_sig):
            return None

        return username
    except Exception:
        return None


def get_authenticated_admin(request: Request) -> Optional[str]:
    """Inspects cookies and headers to determine if request is from an authenticated admin."""
    # 1. Cookie-based authentication
    cookie_token = request.cookies.get(COOKIE_NAME)
    if cookie_token:
        user = verify_session_token(cookie_token)
        if user:
            return user

    # 2. Authorization Header (Bearer token)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        user = verify_session_token(token)
        if user:
            return user

    # 3. Direct API Key Header (X-Admin-Key)
    api_key_header = request.headers.get("X-Admin-Key")
    current_pass = os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    if api_key_header and secrets.compare_digest(api_key_header.strip(), current_pass):
        return os.getenv("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)

    return None


def verify_admin_cookie(request: Request) -> bool:
    """Returns True if the current request has a valid admin session."""
    return get_authenticated_admin(request) is not None


def require_admin(request: Request):
    """
    Route dependency or guard.
    If authenticated, returns username.
    If unauthenticated:
      - API / JSON requests: Raises HTTPException 401.
      - Browser / HTML requests: Returns a 303 Redirect to /admin/login?next=...
    """
    user = get_authenticated_admin(request)
    if user:
        return user

    # Determine if client expects HTML or JSON
    path = request.url.path
    accept = request.headers.get("accept", "")
    is_api = path.startswith("/admin/api") or "application/json" in accept

    if is_api:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required. Please provide a valid session cookie or X-Admin-Key header.",
        )

    # For browser requests, redirect to admin login with return path
    next_url = request.url.path
    if request.url.query:
        next_url += f"?{request.url.query}"
    return RedirectResponse(url=f"/admin/login?next={next_url}", status_code=303)


# Alias for backward compatibility
authenticate_admin = authenticate_credentials
