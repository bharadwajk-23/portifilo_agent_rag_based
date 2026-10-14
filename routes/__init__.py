"""HTTP endpoints. `api_router` bundles every router so the app includes it in one call."""
from fastapi import APIRouter

from .chat import router as chat_router
from .health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(chat_router)

__all__ = ["api_router", "chat_router", "health_router"]
