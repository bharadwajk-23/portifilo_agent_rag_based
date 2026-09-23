from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
import faiss
import json
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def chunking(DOCS):
    docs=[]
    for doc_path in DOCS:
        with open(doc_path,'r',encoding="utf-8") as doc:
            docs.append(
                Document(page_content=doc.read(), metadata={"source": doc_path})
            )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=150)
    all_splits = text_splitter.split_documents(docs)
    print(f"Split documentation into {len(all_splits)} chunks.")

    return all_splits

def ingestion(all_splits):

    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    vectordb = FAISS.from_documents(all_splits, embeddings)


    return vectordb




