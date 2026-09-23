from Ingestion import chunking,ingestion
from Config import DOCS

all_splits=chunking(DOCS)
vectordb=ingestion(all_splits)

vectordb.save_local("./Output/faiss_index")