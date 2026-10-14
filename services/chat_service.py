from answer_generation import gen_ans
from utils.exceptions import LLMRequestError
from utils.formatting import format_turn
from utils.session_store import SessionStore

from .retriever_service import RetrieverService


class ChatService:
    """Answers a question using the RAG pipeline and the session's server-side history."""

    def __init__(self, retriever_service: RetrieverService, sessions: SessionStore):
        self.retriever_service = retriever_service
        self.sessions = sessions

    def answer(self, question: str, session_id: str) -> str:
        retriever = self.retriever_service.get()  # raises 503 if not loaded
        history = self.sessions.get(session_id)
        try:
            result = gen_ans(retriever, question, list(history))
        except Exception as exc:
            raise LLMRequestError.from_exception(exc) from exc
        history.append(format_turn(question, result["answer"]))
        return result["answer"]
