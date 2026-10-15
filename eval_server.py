import ragevalkit
from retrieval import load_retriever
from answer_generation import gen_ans

retriever = load_retriever()

def rag_fn(question: str, history: list = None) -> str:
    str_history = [
        f"Question:{h['question']}-Answer:{h['answer']}"
        for h in (history or [])
    ]

    result = gen_ans(retriever, question, str_history)

    # capture retrieved context for the judge — no-op outside eval runs
    with ragevalkit.step("retriever") as s:
        s.material = "\n\n".join(d.page_content for d in result["context"])
        s.sources = list({d.metadata.get("project", "") for d in result["context"]})

    return result["answer"]

ragevalkit.serve(
    rag_fn,
    port=8003,
    store_path="eval_store.json",
    judge_model="gemini/gemini-2.0-flash-lite",
    history_params=["history"],
    record_detail="selected",   # only send explicitly marked material to judge
    answer_weight=0.7,
    material_weight=0.3,
    users="bharadwaj:bharadwaj123",
)

