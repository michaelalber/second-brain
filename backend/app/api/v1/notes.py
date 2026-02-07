from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.models.note import Note
from app.schemas.note import (
    NoteCreate,
    NoteHighlightsUpdate,
    NoteMoveRequest,
    NoteResponse,
    NoteUpdate,
)
from app.services.note_service import NoteService

router = APIRouter()


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note_in: NoteCreate, db: DbSession) -> Note:
    service = NoteService(db)
    return await service.create_note(note_in)


@router.get("", response_model=list[NoteResponse])
async def list_notes(
    db: DbSession,
    container_id: UUID | None = None,
    stage: str | None = None,
    q: str | None = None,
) -> list[Note]:
    service = NoteService(db)
    return await service.list_notes(container_id=container_id, stage=stage, q=q)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: UUID, db: DbSession) -> Note:
    service = NoteService(db)
    note = await service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: UUID, note_in: NoteUpdate, db: DbSession) -> Note:
    service = NoteService(db)
    note = await service.update_note(note_id, note_in)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}/move", response_model=NoteResponse)
async def move_note(
    note_id: UUID, move_request: NoteMoveRequest, db: DbSession
) -> Note:
    service = NoteService(db)
    note = await service.move_to_container(note_id, move_request.container_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}/highlights", response_model=NoteResponse)
async def update_highlights(
    note_id: UUID, highlights_in: NoteHighlightsUpdate, db: DbSession
) -> Note:
    service = NoteService(db)
    note = await service.update_highlights(note_id, highlights_in)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: UUID, db: DbSession) -> None:
    service = NoteService(db)
    deleted = await service.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
