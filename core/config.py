import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GROQ_API = os.getenv("GROQ_API_KEY")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_CACHE_DIR = str(BASE_DIR / "models" / "fastembed")

INDEX_PATH = str(BASE_DIR / "output" / "faiss_index")

DOCS = [
    str(BASE_DIR / "docs" / name)
    for name in (
        "retell_caller_agent.md",
        "ai_listener.md",
        "digital-prescription-virtual-assistant-platform.md",
        "intelligent-reporting-system.md",
        "scriber_agent.md",
        "siho_rag.md",
        "ysi_ras.md",
        "index.md",
    )
]
