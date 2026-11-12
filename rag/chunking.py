"""Split page text into overlapping chunks while carrying provenance."""

from __future__ import annotations

from typing import Any


def chunk_pages(
    pages: list[dict[str, Any]], *, chunk_size: int = 1000, overlap: int = 150
) -> list[dict[str, Any]]:
    """Return chunks with the source, page, and section of each source page."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")
    chunks: list[dict[str, Any]] = []
    for page_record in pages:
        text = str(page_record.get("text", "")).strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start + chunk_size // 2, end)
                if boundary > start:
                    end = boundary
            piece = text[start:end].strip()
            if piece:
                chunks.append({
                    "text": piece,
                    "source": page_record.get("source"),
                    "page": page_record.get("page"),
                    "section": page_record.get("section"),
                })
            if end >= len(text):
                break
            start = max(start + 1, end - overlap)
    return chunks
