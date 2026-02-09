import uuid
from datetime import datetime

from app.models.container import Container, ContainerType
from sqlalchemy.ext.asyncio import AsyncSession


class ContainerFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        name: str = "Test Container",
        type: ContainerType = ContainerType.PROJECT,
        description: str | None = None,
        parent_id: uuid.UUID | None = None,
        is_active: bool = True,
        deadline: datetime | None = None,
        status: str | None = None,
    ) -> Container:
        container = Container(
            id=uuid.uuid4(),
            name=name,
            type=type,
            description=description,
            parent_id=parent_id,
            is_active=is_active,
            deadline=deadline,
            status=status,
        )
        session.add(container)
        await session.commit()
        await session.refresh(container)
        return container
