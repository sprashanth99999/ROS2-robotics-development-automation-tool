"""Embedding provider — fastembed (ONNX, no torch)."""

from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def dim(self) -> int: ...


class FastEmbedder:
    """fastembed wrapper — lightweight ONNX embeddings."""

    def __init__(self, model: str = "BAAI/bge-small-en-v1.5"):
        self._model_name = model
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name=self._model_name)
            except ImportError:
                raise RuntimeError("fastembed not installed: pip install fastembed")

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._load()
        return [list(v) for v in self._model.embed(texts)]

    @property
    def dim(self) -> int:
        dims = {"BAAI/bge-small-en-v1.5": 384, "BAAI/bge-base-en-v1.5": 768}
        return dims.get(self._model_name, 384)


class DummyEmbedder:
    """Fallback — random embeddings for testing without fastembed."""

    def __init__(self, dim: int = 384):
        self._dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        import random
        return [[random.random() for _ in range(self._dim)] for _ in texts]

    @property
    def dim(self) -> int:
        return self._dim


def get_embedder(use_dummy: bool = False) -> Embedder:
    if use_dummy:
        return DummyEmbedder()
    try:
        return FastEmbedder()
    except Exception:
        return DummyEmbedder()
