from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import CodeStage, Note


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_inbox(self) -> list[Note]:
        """Get all notes in capture stage (inbox)."""
        result = await self.db.execute(
            select(Note)
            .where(Note.code_stage == CodeStage.CAPTURE)
            .where(Note.container_id.is_(None))
            .order_by(Note.captured_at.desc())
        )
        return list(result.scalars().all())

    async def search_notes(self, query: str) -> list[Note]:
        """Full-text search across notes."""
        result = await self.db.execute(
            select(Note)
            .where(Note.title.ilike(f"%{query}%") | Note.content.ilike(f"%{query}%"))
            .order_by(Note.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 20) -> list[Note]:
        """Get recently modified notes."""
        result = await self.db.execute(select(Note).order_by(Note.updated_at.desc()).limit(limit))
        return list(result.scalars().all())
