from fastapi import APIRouter

from app.api.deps import DbSession
from app.models.note import Note
from app.schemas.note import NoteResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/inbox", response_model=list[NoteResponse])
async def get_inbox(db: DbSession) -> list[Note]:
    service = SearchService(db)
    return await service.get_inbox()


@router.get("/search", response_model=list[NoteResponse])
async def search_notes(q: str, db: DbSession) -> list[Note]:
    service = SearchService(db)
    return await service.search_notes(q)


@router.get("/recent", response_model=list[NoteResponse])
async def get_recent(db: DbSession, limit: int = 20) -> list[Note]:
    service = SearchService(db)
    return await service.get_recent(limit=limit)
