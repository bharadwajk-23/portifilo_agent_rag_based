import hashlib
import json
import os
import re

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
HEADERS_TO_SPLIT_ON = [("#", "h1"), ("##", "h2"), ("###", "h3")]
SUMMARY_PROMPT = """Write a compact summary (4-6 sentences) of the project documented below.
State the project name, the business domain, what it does, its key features, the main technologies,
and the business value. Plain prose, no markdown, no preamble.

Project documentation:
{doc}"""
MAX_SUMMARY_INPUT = 30000


def _read(path):
    with open(path, 'r', encoding="utf-8") as f:
        return f.read()


# One canonical name per project, so the doc title and index.md never read as two projects.
PROJECT_NAME_OVERRIDES = {
    "ai_listener.md": "AI Listener (Healthcare Conversational AI Demo)",
}


def _project_name(text, path):
    override = PROJECT_NAME_OVERRIDES.get(os.path.basename(path))
    if override:
        return override
    match = re.search(r"^#\s+(.+)$", text, flags=re.M)
    return match.group(1).strip() if match else os.path.splitext(os.path.basename(path))[0]


def _chunk_doc(path):
    """Split one markdown file on headings; each chunk gets project/section metadata
    and a 'Project > Section' prefix so its embedding keeps its context."""
    text = _read(path)
    project = _project_name(text, path)
    header_splitter = MarkdownHeaderTextSplitter(HEADERS_TO_SPLIT_ON, strip_headers=True)
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    chunks = []
    for section_doc in header_splitter.split_text(text):
        h1, h2, h3 = (section_doc.metadata.get(k, "") for k in ("h1", "h2", "h3"))
        trail = [h for h in (h1, h2, h3) if h and h != project]
        section = trail[0] if trail else "Overview"
        subsection = " > ".join(trail[1:])
        prefix = " > ".join([project] + trail)
        metadata = {
            "source": path,
            "project": project,
            "section": section,
            "subsection": subsection,
            "chunk_type": "section",
        }
        body = section_doc.page_content.strip()
        if not body:
            continue
        for piece in size_splitter.split_text(body):
            chunks.append(Document(page_content=f"[{prefix}]\n{piece}", metadata=dict(metadata)))
    return chunks


def chunking(DOCS):
    all_splits = []
    for path in DOCS:
        all_splits.extend(_chunk_doc(path))
    print(f"Split documentation into {len(all_splits)} chunks.")

    return all_splits


def summarize_projects(DOCS, cache_path):
    """One LLM-written summary chunk per project doc, cached by content hash so
    unchanged docs are not re-summarized."""
    try:
        with open(cache_path, 'r', encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}

    llm = None
    summaries = []
    for path in DOCS:
        text = _read(path)
        if os.path.basename(path) == "index.md":
            continue  # already a project overview
        project = _project_name(text, path)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        entry = cache.get(path)
        if not entry or entry.get("hash") != digest:
            if llm is None:
                from langchain_groq import ChatGroq
                import config  # noqa: F401  (loads .env)
                llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, max_retries=2)
            summary = llm.invoke(SUMMARY_PROMPT.format(doc=text[:MAX_SUMMARY_INPUT])).content.strip()
            entry = cache[path] = {"hash": digest, "summary": summary}
        summaries.append(Document(
            page_content=f"[{project} > Project Summary]\n{entry['summary']}",
            metadata={"source": path, "project": project, "section": "Project Summary",
                      "subsection": "", "chunk_type": "summary"},
        ))

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, 'w', encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
    print(f"Added {len(summaries)} project summaries.")

    return summaries


def build_catalog(summaries):
    """One authoritative chunk listing every project exactly once, for 'list all projects' questions."""
    lines = []
    for i, doc in enumerate(sorted(summaries, key=lambda d: d.metadata["project"]), start=1):
        body = doc.page_content.split("\n", 1)[1].strip()
        first_sentence = re.split(r"(?<=[.!?])\s", body, maxsplit=1)[0]
        lines.append(f"{i}. {doc.metadata['project']}: {first_sentence}")
    text = (
        f"[Project Catalog]\nYoungsoft India has exactly {len(lines)} documented projects. "
        "This is the complete list:\n" + "\n".join(lines)
    )
    return Document(page_content=text, metadata={"source": "catalog", "project": "Project Catalog",
                                                 "section": "All projects", "subsection": "",
                                                 "chunk_type": "catalog"})


def ingestion(all_splits):
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    return FAISS.from_documents(all_splits, embeddings)
