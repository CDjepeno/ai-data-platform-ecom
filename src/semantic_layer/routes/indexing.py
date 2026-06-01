from fastapi import APIRouter

from qdrant.indexer.sementic_indexing import (
    run_semantic_indexing
)

router = APIRouter()


@router.post("/index")
async def index():
    await run_semantic_indexing()
    return {"status": "ok"}