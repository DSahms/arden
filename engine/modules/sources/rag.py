"""RAG Q&A over user documents using the active brain."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Callable

from modules.sources.document_store import DocumentStore
from modules.sources.ingest import chunk_text, extract_text


def ingest_file(store: DocumentStore, source_path: Path) -> dict:
    text = extract_text(source_path)
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("File had no readable text")

    doc_id = str(uuid.uuid4())
    final_dir = store.files_dir / doc_id
    final_dir.mkdir(parents=True, exist_ok=True)
    safe_name = source_path.name.replace(" ", "_")
    dest = final_dir / safe_name
    shutil.copy2(source_path, dest)

    return store.add_document(
        filename=source_path.name,
        chunks=chunks,
        stored_path=dest,
        doc_id=doc_id,
    )


def answer_from_sources(
    store: DocumentStore,
    *,
    question: str,
    doc_id: str | None = None,
    doc_ids: list[str] | None = None,
    brain_generate: Callable[[str, str], str],
) -> tuple[str, list[str]]:
    ids = doc_ids
    if ids is None and doc_id:
        ids = [doc_id]
    hits = store.query(question, doc_ids=ids, n_results=5)
    if not hits:
        scope = "those sources" if ids else "your sources"
        return f"I don't have any matching text in {scope} for that.", []

    snippets: list[str] = []
    context_parts: list[str] = []
    filenames: set[str] = set()
    for i, hit in enumerate(hits, start=1):
        text = (hit.get("text") or "").strip()
        if not text:
            continue
        meta = hit.get("metadata") or {}
        fname = meta.get("filename", "document")
        filenames.add(str(fname))
        snippets.append(text[:240] + ("…" if len(text) > 240 else ""))
        context_parts.append(f"[{i}] ({fname})\n{text}")

    context = "\n\n".join(context_parts)
    multi = len(filenames) > 1 or (ids and len(ids) > 1)
    system = (
        "Answer ONLY from the source excerpts below. "
        "If the answer is not in the excerpts, say you don't see it in their documents. "
        "Do not invent amounts, dates, or names. "
        "Keep answers concise. Cite snippet numbers like [1] when helpful."
    )
    if multi:
        system += (
            " The user selected multiple documents — you may compare or synthesize across them, "
            "but only using facts present in the excerpts."
        )
    user = f"Sources:\n{context}\n\nQuestion: {question}"
    answer = brain_generate(system, user).strip()
    return answer, snippets
