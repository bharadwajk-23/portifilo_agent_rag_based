from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str = Field(default="default", description="Optional: keeps separate users' histories apart")


class AskResponse(BaseModel):
    answer: str
