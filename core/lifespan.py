from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the retriever (FAISS index + embedding model) once at startup."""
    from services import retriever_service  # imported here so `core` stays light for the ingestion script

    retriever_service.load()
    yield
    retriever_service.unload()
