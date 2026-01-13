from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.models.container import Container
from app.schemas.container import (
    ContainerCreate,
    ContainerResponse,
    ContainerUpdate,
    ContainerWithCount,
    ContainerWithNotes,
)
from app.services.container_service import ContainerService

router = APIRouter()


@router.post("", response_model=ContainerResponse, status_code=status.HTTP_201_CREATED)
async def create_container(
    container_in: ContainerCreate, db: DbSession
) -> Container:
    service = ContainerService(db)
    return await service.create_container(container_in)


@router.get("", response_model=list[ContainerWithCount])
async def list_containers(db: DbSession) -> list[ContainerWithCount]:
    service = ContainerService(db)
    return await service.list_containers_with_counts()


@router.get("/{container_id}", response_model=ContainerWithNotes)
async def get_container(container_id: UUID, db: DbSession) -> Container:
    service = ContainerService(db)
    container = await service.get_container_with_notes(container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    return container


@router.put("/{container_id}", response_model=ContainerResponse)
async def update_container(
    container_id: UUID, container_in: ContainerUpdate, db: DbSession
) -> Container:
    service = ContainerService(db)
    container = await service.update_container(container_id, container_in)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    return container


@router.patch("/{container_id}/archive", response_model=ContainerResponse)
async def archive_container(container_id: UUID, db: DbSession) -> Container:
    service = ContainerService(db)
    container = await service.archive_container(container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    return container


@router.delete("/{container_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_container(container_id: UUID, db: DbSession) -> None:
    service = ContainerService(db)
    deleted = await service.delete_container(container_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Container not found")
