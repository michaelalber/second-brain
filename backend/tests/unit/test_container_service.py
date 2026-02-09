from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.models.container import Container, ContainerType
from app.schemas.container import ContainerUpdate
from app.services.container_service import ContainerService


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def container_service(mock_db):
    """Create a ContainerService with a mock database."""
    return ContainerService(mock_db)


@pytest.mark.asyncio
async def test_get_container_returns_none_when_not_found(container_service, mock_db):
    """get_container returns None when container doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await container_service.get_container(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_container_with_notes_returns_none_when_not_found(
    container_service, mock_db
):
    """get_container_with_notes returns None when container doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await container_service.get_container_with_notes(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_update_container_returns_none_when_not_found(container_service, mock_db):
    """update_container returns None when container doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await container_service.update_container(
        uuid4(), ContainerUpdate(name="New Name")
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_container_applies_changes(container_service, mock_db):
    """update_container applies only the provided changes."""
    container_id = uuid4()
    existing_container = Container(
        id=container_id,
        name="Original",
        type=ContainerType.PROJECT,
        description="Original description",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_container
    mock_db.execute.return_value = mock_result

    result = await container_service.update_container(
        container_id, ContainerUpdate(name="Updated")
    )

    assert result.name == "Updated"
    assert result.description == "Original description"


@pytest.mark.asyncio
async def test_archive_container_returns_none_when_not_found(
    container_service, mock_db
):
    """archive_container returns None when container doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await container_service.archive_container(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_archive_container_sets_archive_type(container_service, mock_db):
    """archive_container sets type to archive and is_active to False."""
    container_id = uuid4()
    existing_container = Container(
        id=container_id,
        name="My Project",
        type=ContainerType.PROJECT,
        is_active=True,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_container
    mock_db.execute.return_value = mock_result

    result = await container_service.archive_container(container_id)

    assert result.type == ContainerType.ARCHIVE
    assert result.is_active is False


@pytest.mark.asyncio
async def test_delete_container_returns_false_when_not_found(
    container_service, mock_db
):
    """delete_container returns False when container doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await container_service.delete_container(uuid4())

    assert result is False


@pytest.mark.asyncio
async def test_delete_container_returns_true_on_success(container_service, mock_db):
    """delete_container returns True when container is deleted."""
    container_id = uuid4()
    existing_container = Container(
        id=container_id,
        name="Delete Me",
        type=ContainerType.PROJECT,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_container
    mock_db.execute.return_value = mock_result

    result = await container_service.delete_container(container_id)

    assert result is True
    mock_db.delete.assert_called_once_with(existing_container)
    mock_db.commit.assert_called_once()
