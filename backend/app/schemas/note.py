from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.note import CodeStage


class NoteBase(BaseModel):
    title: str
    content: str
    source_url: str | None = None
    source_type: str | None = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    content_html: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    executive_summary: str | None = None


class NoteMoveRequest(BaseModel):
    container_id: UUID | None = None


class HighlightRange(BaseModel):
    start: int
    end: int
    layer: int  # 2 or 3


class NoteHighlightsUpdate(BaseModel):
    highlights: list[HighlightRange] = []


class NoteResponse(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content_html: str | None = None
    highlights: dict = {}
    executive_summary: str | None = None
    container_id: UUID | None = None
    code_stage: CodeStage
    created_at: datetime
    updated_at: datetime
    captured_at: datetime
