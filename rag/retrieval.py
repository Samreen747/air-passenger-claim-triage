"""Build and query the local PDF index used by the claim workflow."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from .chunking import chunk_pages
from .document_loader import load_pdfs
from .embeddings import SentenceTransformerEmbedder
from .vector_store import FaissVectorStore


def _store() -> FaissVectorStore:
    return FaissVectorStore(os.getenv("RAG_INDEX_PATH", "data/rag/faiss.index"))


def rebuild_index(
    directories: tuple[str | Path, ...] | list[str | Path] | None = None,
    *, chunk_size: int = 1000, overlap: int = 150,
) -> int:
    """Recreate the local FAISS index from the fixed PDF directories."""
    chunks = chunk_pages(load_pdfs(directories), chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        raise ValueError("No extractable PDF pages found in the configured document directories")
    vectors = SentenceTransformerEmbedder().encode([item["text"] for item in chunks])
    store = _store()
    store.build(vectors, chunks)
    store.save()
    return len(chunks)


def retrieve_passages(claim: str | dict[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
    """Return ranked, citation-bearing passages accepted by run_workflow."""
    if top_k <= 0:
        return []
    if isinstance(claim, dict):
        query = str(claim.get("complaint", claim.get("text", "")))
        if not query:
            query = " ".join(str(value) for value in claim.values() if value is not None)
    else:
        query = str(claim)
    if not query.strip():
        return []
    query_vector = SentenceTransformerEmbedder().encode([query])[0]
    matches = _store().search(query_vector, top_k=top_k)
    passages = []
    for item in matches:
        source = str(item.get("source") or "Unknown source")
        page = item.get("page")
        section = item.get("section")
        location = f"page {page}" if page is not None else "page unknown"
        if section:
            location += f", {section}"
        passages.append({
            "text": item["text"],
            "citation": f"{source}, {location}",
            "source": source,
            "page": page,
            "section": section,
        })
    return passages


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local regulation PDF index")
    parser.add_argument("--rebuild", action="store_true", help="rebuild the index from documents/")
    args = parser.parse_args()
    if args.rebuild:
        print(f"Indexed {rebuild_index()} chunks.")
    else:
        parser.error("Specify --rebuild to create or refresh the index")


if __name__ == "__main__":
    main()
