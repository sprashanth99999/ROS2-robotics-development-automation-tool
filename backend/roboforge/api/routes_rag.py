"""RAG routes — index, search, status."""

from __future__ import annotations

from fastapi import APIRouter, Body

from roboforge.rag.indexer import RagIndexer

router = APIRouter(prefix="/rag", tags=["rag"])

_indexer: RagIndexer | None = None


def _get_indexer() -> RagIndexer:
    global _indexer
    if _indexer is None:
        _indexer = RagIndexer()
        _indexer.init_table()
    return _indexer


@router.post("/index/file")
async def index_file(path: str = Body(..., embed=True)):
    idx = _get_indexer()
    count = idx.index_file(path)
    return {"chunks": count, "path": path}


@router.post("/index/directory")
async def index_dir(path: str = Body(..., embed=True)):
    idx = _get_indexer()
    count = idx.index_directory(path)
    return {"chunks": count, "path": path}


@router.post("/index/text")
async def index_text(text: str = Body(..., embed=True), source: str = Body("manual", embed=True)):
    idx = _get_indexer()
    count = idx.index_text(text, source=source)
    return {"chunks": count}


@router.post("/search")
async def search(query: str = Body(..., embed=True), limit: int = Body(5, embed=True)):
    idx = _get_indexer()
    results = idx.search(query, limit=limit)
    return {"results": results, "count": len(results)}


@router.get("/status")
async def rag_status():
    idx = _get_indexer()
    return {"count": idx.store.count()}
