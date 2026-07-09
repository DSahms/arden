"""Extract plain text from user files."""

from __future__ import annotations

from pathlib import Path

SUPPORTED = {".txt", ".md", ".csv", ".pdf"}


def supported_extensions() -> tuple[str, ...]:
    return tuple(sorted(SUPPORTED))


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv"}:
        return path.read_text(encoding="utf-8", errors="replace").strip()

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF support needs pypdf. Run: pip install pypdf"
            ) from exc
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError("Could not read text from this PDF (scanned image?)")
        return text

    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, *, size: int = 900, overlap: int = 120) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks
