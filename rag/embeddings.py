"""Configurable, lazy-loaded Sentence Transformers embeddings."""

from __future__ import annotations

import os
from typing import Any

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or os.getenv("RAG_EMBEDDING_MODEL", DEFAULT_MODEL)
        self._model: Any = None

    def _get_model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "Embedding generation requires sentence-transformers; install requirements.txt"
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str]) -> Any:
        """Encode texts to normalized float32 vectors suitable for cosine search."""
        if not texts:
            return []
        return self._get_model().encode(
            texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
        )
