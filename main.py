from collections import OrderedDict, deque
from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from answer_generation import gen_ans
from retrieval import load_retriever

PORT = 3456
MAX_HISTORY = 5
MAX_SESSIONS = 1000

state = {}
sessions = OrderedDict()  # session_id -> last MAX_HISTORY turns, kept on the server


def get_history(session_id):
    if session_id not in sessions:
        sessions[session_id] = deque(maxlen=MAX_HISTORY)
        if len(sessions) > MAX_SESSIONS:
            sessions.popitem(last=False)  # drop the oldest session
    sessions.move_to_end(session_id)
    return sessions[session_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["retriever"] = load_retriever()  # loaded once at startup
    yield
    state.clear()


app = FastAPI(title="Youi RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str = Field(default="default", description="Optional: keeps separate users' histories apart")


class AskResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "ok", "retriever_loaded": "retriever" in state}


@app.post("/chat", response_model=AskResponse)
def chat(req: AskRequest):
    if "retriever" not in state:
        raise HTTPException(status_code=503, detail="Retriever not loaded yet")
    history = get_history(req.session_id)
    try:
        result = gen_ans(state["retriever"], req.question, list(history))
    except Exception as e:
        status = 429 if "429" in str(e) else 502
        raise HTTPException(status_code=status, detail=f"LLM request failed: {str(e)[:200]}")
    history.append(f"Question:{req.question}-Answer:{result['answer']}")
    return AskResponse(answer=result["answer"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
