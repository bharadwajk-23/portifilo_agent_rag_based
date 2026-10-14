from fastapi import APIRouter

from schemas import AskRequest, AskResponse
from services import chat_service

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=AskResponse)
def chat(req: AskRequest) -> AskResponse:
    # plain `def`: runs in FastAPI's thread pool, so the blocking LLM call doesn't stall other requests
    return AskResponse(answer=chat_service.answer(req.question, req.session_id))
