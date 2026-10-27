"""Índice vetorial em memória (numpy) com cache em disco por hash do texto."""

from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_CACHE_DIR = Path(tempfile.gettempdir()) / "docgen_embedding_cache"
_CACHE_DIR.mkdir(exist_ok=True)


def _cache_path(model: str, text: str) -> Path:
    digest = hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()
    return _CACHE_DIR / f"{model.replace(':', '_').replace('/', '_')}__{digest}.json"


def _load_cached(model: str, text: str) -> list[float] | None:
    path = _cache_path(model, text)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _save_cached(model: str, text: str, vector: list[float]) -> None:
    try:
        _cache_path(model, text).write_text(json.dumps(vector), encoding="utf-8")
    except OSError:
        pass


@dataclass
class RetrievalResult:
    path: str
    score: float
    content: str


class EmbeddingIndex:
    def __init__(self, client, embed_model: str = "nomic-embed-text"):
        self._client = client
        self._embed_model = embed_model
        self._paths: list[str] = []
        self._contents: list[str] = []
        self._vectors: np.ndarray | None = None

    def build(self, entries: list[tuple[str, str]]) -> None:
        cached = [_load_cached(self._embed_model, text) for _, text in entries]
        missing_texts = [text for (_, text), vec in zip(entries, cached) if vec is None]
        new_vectors = iter(self._client.embed(missing_texts, model=self._embed_model) if missing_texts else [])

        self._paths, self._contents = [], []
        vectors: list[list[float]] = []
        for (path, text), vec in zip(entries, cached):
            if vec is None:
                vec = next(new_vectors)
                _save_cached(self._embed_model, text, vec)
            self._paths.append(path)
            self._contents.append(text)
            vectors.append(vec)

        matrix = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1e-8
        self._vectors = matrix / norms

    def is_empty(self) -> bool:
        return self._vectors is None or not self._paths

    def query(self, query_text: str, top_k: int = 8) -> list[RetrievalResult]:
        if self.is_empty():
            return []
        query_vec = np.array(self._client.embed([query_text], model=self._embed_model)[0], dtype=np.float32)
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm
        scores = self._vectors @ query_vec
        order = np.argsort(-scores)[:top_k]
        return [RetrievalResult(self._paths[i], float(scores[i]), self._contents[i]) for i in order]
