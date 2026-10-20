"""
Admin module for Holy Bible application.
Provides role-based access control, authentication, and system configuration.
"""

from app.admin.auth import require_admin, verify_admin_cookie, authenticate_admin
from app.admin.routes import router as admin_router

__all__ = ["require_admin", "verify_admin_cookie", "authenticate_admin", "admin_router"]
