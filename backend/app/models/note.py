from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.tag import note_tags

if TYPE_CHECKING:
    from app.models.container import Container
    from app.models.tag import Tag


class CodeStage(str, Enum):
    CAPTURE = "capture"
    ORGANIZE = "organize"
    DISTILL = "distill"
    EXPRESS = "express"


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    content_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    container_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("containers.id"), nullable=True
    )
    code_stage: Mapped[CodeStage] = mapped_column(default=CodeStage.CAPTURE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    container: Mapped[Container | None] = relationship("Container", back_populates="notes")
    tags: Mapped[list[Tag]] = relationship("Tag", secondary=note_tags, back_populates="notes")
