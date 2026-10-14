"""Business logic. Ready-to-use instances are created here so routes and the lifespan share them."""
from utils import SessionStore

from .retriever_service import RetrieverService
from .chat_service import ChatService

retriever_service = RetrieverService()
chat_service = ChatService(retriever_service, SessionStore())

__all__ = ["RetrieverService", "ChatService", "retriever_service", "chat_service"]
