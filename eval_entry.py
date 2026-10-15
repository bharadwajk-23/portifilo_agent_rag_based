"""
ragevalkit evaluation dashboard for bharadwaj_rag.

Usage
-----
Activate the venv, then:

    python eval_entry.py

Opens the ragevalkit evaluation UI at http://localhost:8001.
The production API (main.py, port 3456) is completely unaffected.

Prerequisites
-------------
ragevalkit must be installed in the venv:

    pip install git+https://github.com/devanshmakam-youngsoft/ragevalkit.git
    # or from local source:
    pip install -e D:/company-projects/ragevalkit-lib

GROQ_API_KEY is loaded from .env automatically (ragevalkit calls _load_dotenv()).
It is used both by the RAG pipeline (ChatGroq) and by the ragevalkit LLM judge.

What gets recorded
------------------
For every evaluated question the dashboard shows:

  routing      — how the query was routed: scope (project/broad), which projects
                 were detected, whether it came from the question or history context,
                 and the final rewritten search query.  Timing: ~microseconds.

  faiss_search — which filters were applied, how many docs were retrieved from the
                 FAISS index (section / summary / catalog chunks), and the total
                 count.  Timing: FAISS similarity_search wall-clock.

  retrieval    — the full stitched context that was passed to the LLM prompt, plus
                 the source file names for every retrieved chunk.
                 Timing: routing + FAISS combined.

  llm          — the exact context_text fed to ChatGroq, with precise LLM latency
                 (time from invoke to first token through to StrOutputParser).
                 Timing: Groq API round-trip.
"""
import ragevalkit
from services import retriever_service, chat_service


def rag_pipeline(question: str, session_id: str) -> str:
    """Single-question RAG call used by ragevalkit for every test-case row.

    ragevalkit supplies a stable session_id per chat_id, so multi-turn datasets
    replay correctly — the ChatService accumulates history across turns for the
    same chat_id just as it would in production.
    """
    return chat_service.answer(question, session_id)


if __name__ == "__main__":
    # Load the FAISS index + embeddings before starting the eval server.
    # (In production this is done by core/lifespan.py; here we do it explicitly.)
    print("Loading FAISS retriever…")
    retriever_service.load()
    print("Retriever ready.")

    ragevalkit.serve(
        rag_pipeline,
        port=8001,

        # --- session management ---
        # ragevalkit generates one session_id per chat_id, enabling correct
        # multi-turn history accumulation inside ChatService.
        session_params=["session_id"],
        session_id_fn=lambda chat_id: f"eval-{chat_id}",

        # --- judge ---
        # Use the same model as the RAG pipeline for evaluation.
        # GROQ_API_KEY is read from .env automatically.
        judge_model="groq/openai/gpt-oss-20b",

        # --- step recording ---
        # "all" records every step's inputs, outputs, material, sources and timing.
        record_detail="all",

        # --- built-in automatic metrics (run alongside the LLM judge) ---
        run_keyword_recall=True,
        run_bm25=True,
        run_semantic_similarity=True,
        require_login=True,
        users="dev:dev@123",

        # --- answer extraction ---
        # gen_ans() returns {"answer": ..., "context": ...} but chat_service.answer()
        # already unwraps it to a plain str, so no answer_keys override is needed.
    )
