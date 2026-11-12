"""FAISS index with JSON sidecar metadata preserving source text and citations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FaissVectorStore:
    def __init__(self, index_path: str | Path = "data/rag/faiss.index") -> None:
        self.index_path = Path(index_path)
        self.metadata_path = self.index_path.with_suffix(".json")
        self._index: Any = None
        self._records: list[dict[str, Any]] = []

    def build(self, vectors: Any, records: list[dict[str, Any]]) -> None:
        try:
            import faiss
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("Vector search requires faiss-cpu and numpy; install requirements.txt") from exc
        matrix = np.asarray(vectors, dtype="float32")
        if matrix.ndim != 2 or len(matrix) != len(records):
            raise ValueError("vectors must be a 2D matrix with one vector per record")
        if not len(records):
            raise ValueError("Cannot build an index with no document chunks")
        faiss.normalize_L2(matrix)
        self._index = faiss.IndexFlatIP(matrix.shape[1])
        self._index.add(matrix)
        self._records = [dict(record) for record in records]

    def save(self) -> None:
        if self._index is None:
            raise RuntimeError("Build or load an index before saving")
        import faiss
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self.index_path))
        self.metadata_path.write_text(
            json.dumps(self._records, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load(self) -> None:
        try:
            import faiss
        except ImportError as exc:
            raise RuntimeError("Vector search requires faiss-cpu; install requirements.txt") from exc
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Index not found at {self.index_path}; rebuild it with python -m rag.retrieval --rebuild"
            )
        self._index = faiss.read_index(str(self.index_path))
        self._records = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        if self._index.ntotal != len(self._records):
            raise ValueError("FAISS index and metadata sidecar contain different record counts")

    def search(self, query_vector: Any, top_k: int = 5) -> list[dict[str, Any]]:
        if top_k <= 0:
            return []
        if self._index is None:
            self.load()
        import numpy as np
        import faiss
        query = np.asarray(query_vector, dtype="float32").reshape(1, -1)
        faiss.normalize_L2(query)
        scores, indices = self._index.search(query, min(top_k, self._index.ntotal))
        return [
            {**self._records[int(i)], "score": float(score)}
            for score, i in zip(scores[0], indices[0]) if i >= 0
        ]
