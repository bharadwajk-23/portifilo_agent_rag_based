from datetime import datetime

from prompts import RAG_PROMPT
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq

import config  # noqa: F401  (loads .env before ChatGroq reads the API key)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2,
    max_retries=2,
)

combine_docs_chain = create_stuff_documents_chain(llm, RAG_PROMPT)


def gen_ans(retriever, question, history):
    # The retriever sees the history so follow-ups ("its tech stack?") route to the right project.
    docs = retriever.retrieve(question, history)
    answer = combine_docs_chain.invoke({
        "context": docs,
        "input": question,
        "history": "\n".join(history),
        "current_time": datetime.now().astimezone().strftime("%A, %d %B %Y, %I:%M %p %Z"),
    })
    return {"answer": answer, "context": docs}
