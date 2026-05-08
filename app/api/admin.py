from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.router import _sessions
from app.rag.store import rebuild_store

router = APIRouter(prefix="/admin", tags=["admin"])

DOCS_DIR = Path(__file__).parent.parent.parent / "documentation"
ALLOWED_EXTENSIONS = {".md", ".txt", ".pdf"}


class ReindexResponse(BaseModel):
    status: str
    sessions_updated: int


class UploadResponse(BaseModel):
    status: str
    filename: str
    sessions_updated: int


@router.post("/reindex", response_model=ReindexResponse)
async def reindex() -> ReindexResponse:
    new_retriever = rebuild_store()

    for agent in _sessions.values():
        agent.refresh_retriever(new_retriever)

    return ReindexResponse(status="ok", sessions_updated=len(_sessions))


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile) -> UploadResponse:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Usa: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dest = DOCS_DIR / (file.filename or "document")
    dest.write_bytes(await file.read())

    new_retriever = rebuild_store()
    for agent in _sessions.values():
        agent.refresh_retriever(new_retriever)

    return UploadResponse(status="ok", filename=dest.name, sessions_updated=len(_sessions))
