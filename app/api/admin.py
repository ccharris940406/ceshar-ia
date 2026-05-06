from fastapi import APIRouter
from pydantic import BaseModel

from app.api.router import _sessions
from app.rag.store import rebuild_store

router = APIRouter(prefix="/admin", tags=["admin"])


class ReindexResponse(BaseModel):
    status: str
    sessions_updated: int


@router.post("/reindex", response_model=ReindexResponse)
async def reindex() -> ReindexResponse:
    new_retriever = rebuild_store()

    for agent in _sessions.values():
        agent.refresh_retriever(new_retriever)

    return ReindexResponse(status="ok", sessions_updated=len(_sessions))
