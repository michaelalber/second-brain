from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.note import Note


class ContainerType(str, Enum):
    PROJECT = "project"
    AREA = "area"
    RESOURCE = "resource"
    ARCHIVE = "archive"


class Container(Base):
    __tablename__ = "containers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[ContainerType]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("containers.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    parent: Mapped[Container | None] = relationship(
        "Container", remote_side=[id], back_populates="children"
    )
    children: Mapped[list[Container]] = relationship("Container", back_populates="parent")
    notes: Mapped[list[Note]] = relationship("Note", back_populates="container")
