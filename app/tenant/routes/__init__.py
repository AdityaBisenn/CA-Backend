# app/tenant/routes/__init__.py
from .firm import router as firm_router
from .user import router as user_router

__all__ = ["firm_router", "user_router"]