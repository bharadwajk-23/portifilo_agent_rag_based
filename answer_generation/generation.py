from datetime import datetime

from prompts import RAG_PROMPT
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

import core.config  # noqa: F401  (loads .env before ChatGroq reads the API key)

try:
    from ragevalkit import step as rk_step
except ImportError:
    from contextlib import contextmanager

    @contextmanager
    def rk_step(name):  # type: ignore[misc]
        class _Noop:
            material = None
            sources = None
        yield _Noop()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2,
    max_retries=2,
)

# Same as langchain_classic's create_stuff_documents_chain (docs joined by a blank line), without importing it:
# that package pulls in torch / sentence-transformers through langchain_text_splitters and costs ~16s at startup.
combine_docs_chain = RAG_PROMPT | llm | StrOutputParser()


def _stuff(docs):
    return "\n\n".join(d.page_content for d in docs)


def gen_ans(retriever, question, history):
    # Retrieval step: runs routing + FAISS search (both sub-steps recorded inside RoutedRetriever)
    with rk_step("retrieval") as s:
        docs = retriever.retrieve(question, history)
        context_text = _stuff(docs)
        s.material = context_text
        s.sources = sorted({
            d.metadata.get("source", d.metadata.get("project", ""))
            for d in docs
            if d.metadata.get("source") or d.metadata.get("project")
        })

    # LLM step: records the exact context fed to the model + measures LLM latency
    with rk_step("llm") as s:
        s.material = context_text
        answer = combine_docs_chain.invoke({
            "context": context_text,
            "input": question,
            "history": "\n".join(history),
            "current_time": datetime.now().astimezone().strftime("%A, %d %B %Y, %I:%M %p %Z"),
        })

    return {"answer": answer, "context": docs}
