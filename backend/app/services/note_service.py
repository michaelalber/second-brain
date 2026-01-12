from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import CodeStage, Note
from app.schemas.note import NoteCreate, NoteHighlightsUpdate, NoteUpdate


class NoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_note(self, note_in: NoteCreate) -> Note:
        note = Note(
            title=note_in.title,
            content=note_in.content,
            source_url=note_in.source_url,
            source_type=note_in.source_type,
            code_stage=CodeStage.CAPTURE,
        )
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def get_note(self, note_id: UUID) -> Note | None:
        result = await self.db.execute(select(Note).where(Note.id == note_id))
        return result.scalar_one_or_none()

    async def list_notes(
        self,
        container_id: UUID | None = None,
        stage: str | None = None,
        q: str | None = None,
    ) -> list[Note]:
        query = select(Note)

        if container_id:
            query = query.where(Note.container_id == container_id)
        if stage:
            query = query.where(Note.code_stage == stage)
        if q:
            query = query.where(
                Note.title.ilike(f"%{q}%") | Note.content.ilike(f"%{q}%")
            )

        query = query.order_by(Note.updated_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_note(self, note_id: UUID, note_in: NoteUpdate) -> Note | None:
        note = await self.get_note(note_id)
        if not note:
            return None

        update_data = note_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)

        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def move_to_container(
        self, note_id: UUID, container_id: UUID
    ) -> Note | None:
        note = await self.get_note(note_id)
        if not note:
            return None

        note.container_id = container_id
        if note.code_stage == CodeStage.CAPTURE:
            note.code_stage = CodeStage.ORGANIZE

        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def update_highlights(
        self, note_id: UUID, highlights_in: NoteHighlightsUpdate
    ) -> Note | None:
        note = await self.get_note(note_id)
        if not note:
            return None

        note.highlights = {
            "highlights": [h.model_dump() for h in highlights_in.highlights]
        }

        if note.code_stage in (CodeStage.CAPTURE, CodeStage.ORGANIZE):
            note.code_stage = CodeStage.DISTILL

        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def delete_note(self, note_id: UUID) -> bool:
        note = await self.get_note(note_id)
        if not note:
            return False

        await self.db.delete(note)
        await self.db.commit()
        return True
