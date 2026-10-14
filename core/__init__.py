"""Application core: RAG config (paths, keys, models), API settings and the startup lifecycle."""
from . import settings
from .config import (
    GROQ_API,
    DOCS,
    INDEX_PATH,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_CACHE_DIR,
)
from .lifespan import lifespan

__all__ = [
    "settings",
    "GROQ_API",
    "DOCS",
    "INDEX_PATH",
    "EMBEDDING_MODEL_NAME",
    "EMBEDDING_CACHE_DIR",
    "lifespan",
]
