from datetime import datetime

from prompts import RAG_PROMPT
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

import core.config  # noqa: F401  (loads .env before ChatGroq reads the API key)

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
    # The retriever sees the history so follow-ups ("its tech stack?") route to the right project.
    docs = retriever.retrieve(question, history)
    answer = combine_docs_chain.invoke({
        "context": _stuff(docs),
        "input": question,
        "history": "\n".join(history),
        "current_time": datetime.now().astimezone().strftime("%A, %d %B %Y, %I:%M %p %Z"),
    })
    return {"answer": answer, "context": docs}
