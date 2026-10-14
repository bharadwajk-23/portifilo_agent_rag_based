class ServiceError(Exception):
    """Error that maps to an HTTP status; turned into {"detail": ...} by the app."""

    status_code = 500

    def __init__(self, detail: str, status_code: int | None = None):
        super().__init__(detail)
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class RetrieverNotReadyError(ServiceError):
    status_code = 503

    def __init__(self):
        super().__init__("Retriever not loaded yet")


class LLMRequestError(ServiceError):
    """The LLM call failed: 429 for rate limits, 502 for anything else."""

    @classmethod
    def from_exception(cls, exc: Exception) -> "LLMRequestError":
        status = 429 if "429" in str(exc) else 502
        return cls(f"LLM request failed: {str(exc)[:200]}", status_code=status)
