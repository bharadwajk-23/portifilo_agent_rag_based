import os

from langchain_community.embeddings import FastEmbedEmbeddings

from core.config import EMBEDDING_MODEL_NAME, EMBEDDING_CACHE_DIR


def get_embeddings():
    """ONNX version of all-MiniLM-L6-v2 (no torch / sentence-transformers import, so startup is fast).
    The model is downloaded into EMBEDDING_CACHE_DIR on the very first run and read from disk after that."""
    os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)
    return FastEmbedEmbeddings(model_name=EMBEDDING_MODEL_NAME, cache_dir=EMBEDDING_CACHE_DIR)
