import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import CodeStage, Note


class NoteFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        title: str = "Test Note",
        content: str = "Test content",
        content_html: str | None = None,
        highlights: dict | None = None,
        executive_summary: str | None = None,
        source_url: str | None = None,
        source_type: str | None = None,
        container_id: uuid.UUID | None = None,
        code_stage: CodeStage = CodeStage.CAPTURE,
    ) -> Note:
        note = Note(
            id=uuid.uuid4(),
            title=title,
            content=content,
            content_html=content_html,
            highlights=highlights or {},
            executive_summary=executive_summary,
            source_url=source_url,
            source_type=source_type,
            container_id=container_id,
            code_stage=code_stage,
        )
        session.add(note)
        await session.commit()
        await session.refresh(note)
        return note
