from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    retriever_loaded: bool
