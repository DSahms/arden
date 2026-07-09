"""Document registry + vector index for Sources RAG (Chroma or local fallback)."""

from __future__ import annotations

import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

try:
    import chromadb

    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False

from modules.consumer_bootstrap import consumer_data_dir


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


class DocumentStore:
    COLLECTION = "documents"

    def __init__(
        self,
        *,
        sources_dir: Path | None = None,
        chroma_dir: Path | None = None,
        embed: Callable[[str], list[float]] | None = None,
    ) -> None:
        data = consumer_data_dir()
        self.sources_dir = sources_dir or (data / "sources")
        self.files_dir = self.sources_dir / "files"
        self.manifest_path = self.sources_dir / "manifest.json"
        self.chunks_path = self.sources_dir / "chunks.json"
        self.chroma_dir = chroma_dir or (data / "chroma")
        self._embed = embed
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None
        if CHROMADB_AVAILABLE and embed:
            self._client = chromadb.PersistentClient(path=str(self.chroma_dir))
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION,
                metadata={"description": "User document chunks for Sources RAG"},
            )

    def set_embedder(self, fn: Callable[[str], list[float]]) -> None:
        self._embed = fn

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {"documents": []}
        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except Exception:
            return {"documents": []}

    def _save_manifest(self, data: dict[str, Any]) -> None:
        self.manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_chunks(self) -> list[dict[str, Any]]:
        if not self.chunks_path.exists():
            return []
        try:
            return json.loads(self.chunks_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_chunks(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks_path.write_text(json.dumps(chunks), encoding="utf-8")

    def list_documents(self) -> list[dict[str, Any]]:
        return list(self._load_manifest().get("documents", []))

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        for doc in self.list_documents():
            if doc.get("id") == doc_id:
                return doc
        return None

    def delete_document(self, doc_id: str) -> bool:
        manifest = self._load_manifest()
        docs = manifest.get("documents", [])
        kept = [d for d in docs if d.get("id") != doc_id]
        if len(kept) == len(docs):
            return False
        manifest["documents"] = kept
        self._save_manifest(manifest)

        if self._collection:
            try:
                existing = self._collection.get(where={"doc_id": doc_id})
                if existing and existing.get("ids"):
                    self._collection.delete(ids=existing["ids"])
            except Exception:
                pass

        remaining = [c for c in self._load_chunks() if c.get("doc_id") != doc_id]
        self._save_chunks(remaining)

        stored = self.files_dir / doc_id
        if stored.exists():
            for p in stored.iterdir():
                p.unlink(missing_ok=True)
            stored.rmdir()
        return True

    def add_document(
        self,
        *,
        filename: str,
        chunks: list[str],
        stored_path: Path,
        doc_id: str | None = None,
    ) -> dict[str, Any]:
        if not self._embed:
            raise RuntimeError("Document store not ready (embedder missing)")

        doc_id = doc_id or str(uuid.uuid4())
        manifest = self._load_manifest()
        entry = {
            "id": doc_id,
            "filename": filename,
            "path": str(stored_path),
            "chunks": len(chunks),
            "added_at": _utc_now(),
        }

        if self._collection:
            ids: list[str] = []
            embeddings: list[list[float]] = []
            documents: list[str] = []
            metadatas: list[dict[str, Any]] = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}:{i}"
                ids.append(chunk_id)
                embeddings.append(self._embed(chunk))
                documents.append(chunk)
                metadatas.append({"doc_id": doc_id, "filename": filename, "chunk_index": i})
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        else:
            local = [c for c in self._load_chunks() if c.get("doc_id") != doc_id]
            for i, chunk in enumerate(chunks):
                local.append(
                    {
                        "id": f"{doc_id}:{i}",
                        "doc_id": doc_id,
                        "filename": filename,
                        "text": chunk,
                        "embedding": self._embed(chunk),
                    }
                )
            self._save_chunks(local)

        manifest.setdefault("documents", []).append(entry)
        self._save_manifest(manifest)
        return entry

    def query(
        self,
        question: str,
        *,
        doc_id: str | None = None,
        doc_ids: list[str] | None = None,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        if not self._embed:
            return []

        filter_ids: list[str] | None = None
        if doc_ids is not None:
            filter_ids = [d for d in doc_ids if d]
        elif doc_id:
            filter_ids = [doc_id]

        if filter_ids:
            n_results = min(max(n_results, 3 + 2 * len(filter_ids)), 15)

        if self._collection:
            where = None
            if filter_ids:
                if len(filter_ids) == 1:
                    where = {"doc_id": filter_ids[0]}
                else:
                    where = {"doc_id": {"$in": filter_ids}}
            results = self._collection.query(
                query_embeddings=[self._embed(question)],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
            hits: list[dict[str, Any]] = []
            if not results.get("ids") or not results["ids"][0]:
                return hits
            for i, cid in enumerate(results["ids"][0]):
                hits.append(
                    {
                        "id": cid,
                        "text": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    }
                )
            return hits

        allowed = set(filter_ids) if filter_ids else None
        q_emb = self._embed(question)
        scored: list[tuple[float, dict[str, Any]]] = []
        for row in self._load_chunks():
            row_doc = row.get("doc_id")
            if allowed is not None and row_doc not in allowed:
                continue
            emb = row.get("embedding") or []
            if not emb:
                continue
            scored.append((_cosine(q_emb, emb), row))
        scored.sort(key=lambda x: x[0], reverse=True)
        hits = []
        for score, row in scored[:n_results]:
            hits.append(
                {
                    "id": row.get("id"),
                    "text": row.get("text", ""),
                    "metadata": {"doc_id": row.get("doc_id"), "filename": row.get("filename")},
                    "distance": 1.0 - score,
                }
            )
        return hits
