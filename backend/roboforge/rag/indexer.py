"""RAG indexer — chunks and indexes documents for retrieval."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

from roboforge.rag.embeddings import Embedder, get_embedder
from roboforge.rag.store import VectorStore
from roboforge.utils.logging import get_logger

log = get_logger(__name__)

TABLE_NAME = "roboforge_docs"


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def hash_id(text: str, source: str) -> str:
    return hashlib.sha256(f"{source}:{text[:100]}".encode()).hexdigest()[:16]


class RagIndexer:
    """Index documents into vector store for RAG retrieval."""

    def __init__(self, store: VectorStore | None = None, embedder: Embedder | None = None):
        self.store = store or VectorStore()
        self.embedder = embedder or get_embedder()

    def init_table(self) -> None:
        self.store.create_table(TABLE_NAME, self.embedder.dim)

    def index_file(self, path: str | Path) -> int:
        """Index single file. Returns chunk count."""
        p = Path(path)
        if not p.is_file():
            return 0
        text = p.read_text(encoding="utf-8", errors="replace")
        return self.index_text(text, source=str(p))

    def index_text(self, text: str, source: str = "unknown") -> int:
        chunks = chunk_text(text)
        if not chunks:
            return 0
        vectors = self.embedder.embed(chunks)
        records = []
        for chunk, vec in zip(chunks, vectors):
            records.append({
                "id": hash_id(chunk, source),
                "text": chunk,
                "source": source,
                "vector": vec,
                "metadata": json.dumps({"source": source, "length": len(chunk)}),
            })
        self.store.add(records)
        log.info("Indexed %d chunks from %s", len(records), source)
        return len(records)

    def index_directory(self, dir_path: str | Path, extensions: tuple = (".py", ".md", ".txt", ".yaml", ".xml")) -> int:
        """Index all matching files in directory."""
        total = 0
        for p in Path(dir_path).rglob("*"):
            if p.suffix in extensions and p.is_file():
                total += self.index_file(p)
        return total

    def search(self, query: str, limit: int = 5) -> list[dict]:
        vecs = self.embedder.embed([query])
        return self.store.search(vecs[0], limit=limit)
