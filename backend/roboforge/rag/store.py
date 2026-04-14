"""Vector store — LanceDB backend."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from roboforge.config.paths import roboforge_home
from roboforge.utils.logging import get_logger

log = get_logger(__name__)


class VectorStore:
    """LanceDB-backed vector store for RAG."""

    def __init__(self, db_path: str | None = None):
        self._db_path = db_path or str(Path(roboforge_home()) / "vectordb")
        self._db = None
        self._table = None

    def _connect(self):
        if self._db is None:
            try:
                import lancedb
                self._db = lancedb.connect(self._db_path)
            except ImportError:
                raise RuntimeError("lancedb not installed: pip install lancedb")

    def create_table(self, name: str, dim: int) -> None:
        self._connect()
        import pyarrow as pa
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("source", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), dim)),
            pa.field("metadata", pa.string()),
        ])
        try:
            self._table = self._db.create_table(name, schema=schema, mode="overwrite")
        except Exception:
            self._table = self._db.open_table(name)

    def open_table(self, name: str) -> None:
        self._connect()
        self._table = self._db.open_table(name)

    def add(self, records: list[dict[str, Any]]) -> int:
        if self._table is None:
            raise RuntimeError("No table open")
        self._table.add(records)
        return len(records)

    def search(self, vector: list[float], limit: int = 5) -> list[dict]:
        if self._table is None:
            return []
        results = self._table.search(vector).limit(limit).to_list()
        return [{"id": r["id"], "text": r["text"], "source": r["source"],
                 "distance": r.get("_distance", 0)} for r in results]

    def count(self) -> int:
        if self._table is None:
            return 0
        return self._table.count_rows()
