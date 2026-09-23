from groq import Groq
from Config import GROQ_API
from Prompts import RAG_PROMPT
from langchain_classic.chains.combine_documents import (create_stuff_documents_chain, )
from langchain_classic.chains import create_retrieval_chain
from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def gen_ans(retriver,question):
    

    combine_docs_chain = create_stuff_documents_chain(llm, RAG_PROMPT)

    retrieval_chain = create_retrieval_chain(retriver, combine_docs_chain)

    answer=retrieval_chain.invoke({"input":question})
    print(answer)

    return answer
    