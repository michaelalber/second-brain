from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.container import Container, ContainerType
from app.models.note import Note
from app.schemas.container import ContainerCreate, ContainerUpdate, ContainerWithCount


class ContainerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_container(self, container_in: ContainerCreate) -> Container:
        container = Container(
            name=container_in.name,
            type=container_in.type,
            description=container_in.description,
            parent_id=container_in.parent_id,
            deadline=container_in.deadline,
            status=container_in.status,
        )
        self.db.add(container)
        await self.db.commit()
        await self.db.refresh(container)
        return container

    async def get_container(self, container_id: UUID) -> Container | None:
        result = await self.db.execute(select(Container).where(Container.id == container_id))
        return result.scalar_one_or_none()

    async def get_container_with_notes(self, container_id: UUID) -> Container | None:
        result = await self.db.execute(
            select(Container)
            .options(selectinload(Container.notes))
            .where(Container.id == container_id)
        )
        return result.scalar_one_or_none()

    async def list_containers_with_counts(self) -> list[ContainerWithCount]:
        # Get containers with note counts
        stmt = (
            select(Container, func.count(Note.id).label("note_count"))
            .outerjoin(Note, Container.id == Note.container_id)
            .group_by(Container.id)
            .order_by(Container.type, Container.name)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        containers_with_counts = []
        for container, note_count in rows:
            container_dict = {
                "id": container.id,
                "name": container.name,
                "type": container.type,
                "description": container.description,
                "parent_id": container.parent_id,
                "is_active": container.is_active,
                "deadline": container.deadline,
                "status": container.status,
                "created_at": container.created_at,
                "updated_at": container.updated_at,
                "note_count": note_count,
            }
            containers_with_counts.append(ContainerWithCount(**container_dict))

        return containers_with_counts

    async def update_container(
        self, container_id: UUID, container_in: ContainerUpdate
    ) -> Container | None:
        container = await self.get_container(container_id)
        if not container:
            return None

        update_data = container_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(container, field, value)

        await self.db.commit()
        await self.db.refresh(container)
        return container

    async def archive_container(self, container_id: UUID) -> Container | None:
        container = await self.get_container(container_id)
        if not container:
            return None

        container.type = ContainerType.ARCHIVE
        container.is_active = False

        await self.db.commit()
        await self.db.refresh(container)
        return container

    async def delete_container(self, container_id: UUID) -> bool:
        container = await self.get_container(container_id)
        if not container:
            return False

        await self.db.delete(container)
        await self.db.commit()
        return True
