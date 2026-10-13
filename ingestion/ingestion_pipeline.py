import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion import chunking, ingestion, summarize_projects, build_catalog
from config import DOCS, INDEX_PATH

SUMMARY_CACHE = os.path.join(os.path.dirname(INDEX_PATH), "project_summaries.json")

summaries = summarize_projects(DOCS, SUMMARY_CACHE)
all_splits = chunking(DOCS) + summaries + [build_catalog(summaries)]
vectordb = ingestion(all_splits)

os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
vectordb.save_local(INDEX_PATH)
