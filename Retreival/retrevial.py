import json
import faiss
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def load_retriever():

    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    vector_db= FAISS.load_local("./Output/faiss_index", embeddings, allow_dangerous_deserialization=True)
    print("hello")

    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    return retriever










