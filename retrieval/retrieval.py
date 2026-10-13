import re
from typing import Any, List

from langchain_community.vectorstores import FAISS
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import ConfigDict

from config import INDEX_PATH

K_SECTIONS = 6          # section chunks when a project is identified
K_SECTIONS_BROAD = 4    # section chunks mixed in when no project is identified
HISTORY_WINDOW = 4
NON_PROJECTS = ("Project Index", "Project Catalog")

# Distinctive names only (generic words like "prescription" or "call agent" would wrongly
# pin multi-project questions to a single project). Matched case-insensitively on word boundaries.
PROJECT_ALIASES = {
    "scriber": "Scriber Agent",
    "ai listener": "Healthcare Conversational AI Demo",
    "conversational ai demo": "Healthcare Conversational AI Demo",
    "physiotherapy": "AI Physiotherapy Call Agent",
    "retell": "AI Physiotherapy Call Agent",
    "digital prescription": "Digital Prescription & Virtual Assistant Platform",
    "intelligent reporting": "Intelligent Reporting System",
    "ysiras": "YSIRas",
    "ysi ras": "YSIRas",
    "mytruadvantage": "MyTruAdvantage",
    "mta": "MyTruAdvantage",
    "health plan chatbot": "MyTruAdvantage",
}
FOLLOW_UP_CUES = re.compile(
    r"\b(it|its|it's|this|that|these|those|they|them|their|same|there|above|previous|the project|the platform)\b", re.I
)
SHORT_QUESTION_WORDS = 5


class RoutedRetriever(BaseRetriever):
    """Deterministic (no LLM) routing with metadata-filtered search.

    1. Projects named in the question  -> search only those projects (sections + summary).
    2. Follow-up ("its tech stack?")   -> inherit the project named in recent history.
    3. Otherwise                       -> the project catalog + ALL project summaries (similarity-ranked; only ~7, so no
                                          project is ever missed) plus the top few sections.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vector_db: Any
    projects: List[str]

    def _canonical(self, alias_target: str) -> str | None:
        target = alias_target.lower()
        return next((p for p in self.projects if target in p.lower()), None)

    def _mentioned(self, text: str) -> List[str]:
        found = []
        for alias, target in PROJECT_ALIASES.items():
            if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", text, flags=re.I):
                project = self._canonical(target)
                if project and project not in found:
                    found.append(project)
        for p in self.projects:  # exact full-name mentions
            if p.lower() in text.lower() and p not in found:
                found.append(p)
        return found

    def route(self, question: str, history: List[str] | None = None) -> dict:
        projects = self._mentioned(question)
        source = "question"
        if not projects and history and (
            FOLLOW_UP_CUES.search(question) or len(question.split()) <= SHORT_QUESTION_WORDS
        ):
            for entry in reversed(history[-HISTORY_WINDOW:]):
                # only the user's side of the turn: the bot's answer may mention other projects
                projects = self._mentioned(entry.split("-Answer:")[0])
                if projects:
                    source = "history"
                    break
        query = question
        if source == "history":
            query = f"{', '.join(p.split(' (')[0] for p in projects)}: {question}"
        scope = "project" if projects else "broad"
        return {"scope": scope, "projects": projects, "source": source if projects else None, "query": query}

    def _search(self, query: str, k: int, flt) -> List[Document]:
        # FAISS filters after fetching fetch_k neighbours, so fetch the whole (small) index.
        return self.vector_db.similarity_search(query, k=k, filter=flt, fetch_k=self.vector_db.index.ntotal)

    def retrieve(self, question: str, history: List[str] | None = None) -> List[Document]:
        route = self.route(question, history)
        query, projects = route["query"], set(route["projects"])
        if projects:
            n = len(projects)
            docs = self._search(query, self.k_for(n), lambda m: m["project"] in projects and m["chunk_type"] == "section")
            docs += self._search(query, n, lambda m: m["project"] in projects and m["chunk_type"] == "summary")
        else:
            docs = self._search(query, 1, {"chunk_type": "catalog"})
            docs += self._search(query, len(self.projects), {"chunk_type": "summary"})
            docs += self._search(query, K_SECTIONS_BROAD, {"chunk_type": "section"})
        return docs

    @staticmethod
    def k_for(n_projects: int) -> int:
        return K_SECTIONS if n_projects == 1 else K_SECTIONS + 2 * (n_projects - 1)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        return self.retrieve(query)


def load_retriever():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    vector_db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

    projects = sorted(
        {d.metadata["project"] for d in vector_db.docstore._dict.values()
         if not any(m in d.metadata["project"] for m in NON_PROJECTS)}
    )

    return RoutedRetriever(vector_db=vector_db, projects=projects)
