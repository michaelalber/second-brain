from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.container import ContainerType
from app.schemas.note import NoteResponse


class ContainerBase(BaseModel):
    name: str
    type: ContainerType
    description: str | None = None
    parent_id: UUID | None = None
    deadline: datetime | None = None
    status: str | None = None


class ContainerCreate(ContainerBase):
    pass


class ContainerUpdate(BaseModel):
    name: str | None = None
    type: ContainerType | None = None
    description: str | None = None
    parent_id: UUID | None = None
    is_active: bool | None = None
    deadline: datetime | None = None
    status: str | None = None


class ContainerResponse(ContainerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ContainerWithCount(ContainerResponse):
    note_count: int = 0


class ContainerWithNotes(ContainerResponse):
    notes: list[NoteResponse] = []
