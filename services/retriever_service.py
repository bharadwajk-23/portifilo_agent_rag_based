from retrieval import load_retriever
from utils.exceptions import RetrieverNotReadyError


class RetrieverService:
    """Owns the retriever: loaded once at startup, shared by every request."""

    def __init__(self):
        self._retriever = None

    def load(self):
        self._retriever = load_retriever()

    def unload(self):
        self._retriever = None

    @property
    def is_loaded(self) -> bool:
        return self._retriever is not None

    def get(self):
        if self._retriever is None:
            raise RetrieverNotReadyError()
        return self._retriever
