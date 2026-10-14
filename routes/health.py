from fastapi import APIRouter

from schemas import HealthResponse
from services import retriever_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", retriever_loaded=retriever_service.is_loaded)
