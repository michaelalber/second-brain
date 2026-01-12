import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_container_returns_201(client: AsyncClient):
    """Creating a container returns 201 with the container data."""
    response = await client.post(
        "/api/v1/containers",
        json={"name": "My Project", "type": "project"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "My Project"
    assert data["type"] == "project"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_container_with_all_fields(client: AsyncClient):
    """Creating a container with all optional fields."""
    response = await client.post(
        "/api/v1/containers",
        json={
            "name": "Work",
            "type": "area",
            "description": "Work related stuff",
            "status": "active",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Work related stuff"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_containers_with_counts(client: AsyncClient):
    """List containers returns containers with note counts."""
    # Create a container
    container_response = await client.post(
        "/api/v1/containers",
        json={"name": "Container 1", "type": "project"},
    )
    container_id = container_response.json()["id"]

    # Add a note to the container
    note_response = await client.post(
        "/api/v1/notes",
        json={"title": "Note", "content": "Content"},
    )
    note_id = note_response.json()["id"]

    await client.patch(
        f"/api/v1/notes/{note_id}/move",
        json={"container_id": container_id},
    )

    # List containers
    response = await client.get("/api/v1/containers")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["note_count"] == 1


@pytest.mark.asyncio
async def test_get_container_with_notes(client: AsyncClient):
    """Get container returns container with its notes."""
    # Create a container
    container_response = await client.post(
        "/api/v1/containers",
        json={"name": "Container", "type": "resource"},
    )
    container_id = container_response.json()["id"]

    # Add a note
    note_response = await client.post(
        "/api/v1/notes",
        json={"title": "My Note", "content": "Content"},
    )
    note_id = note_response.json()["id"]

    await client.patch(
        f"/api/v1/notes/{note_id}/move",
        json={"container_id": container_id},
    )

    # Get container
    response = await client.get(f"/api/v1/containers/{container_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Container"
    assert len(data["notes"]) == 1
    assert data["notes"][0]["title"] == "My Note"


@pytest.mark.asyncio
async def test_get_nonexistent_container_returns_404(client: AsyncClient):
    """Get nonexistent container returns 404."""
    response = await client.get(
        "/api/v1/containers/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_container(client: AsyncClient):
    """Update container changes its fields."""
    create_response = await client.post(
        "/api/v1/containers",
        json={"name": "Original", "type": "project"},
    )
    container_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/containers/{container_id}",
        json={"name": "Updated", "description": "New description"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    assert response.json()["description"] == "New description"


@pytest.mark.asyncio
async def test_archive_container(client: AsyncClient):
    """Archiving a container changes its type to archive."""
    create_response = await client.post(
        "/api/v1/containers",
        json={"name": "Completed Project", "type": "project"},
    )
    container_id = create_response.json()["id"]

    response = await client.patch(f"/api/v1/containers/{container_id}/archive")

    assert response.status_code == 200
    assert response.json()["type"] == "archive"
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_delete_container(client: AsyncClient):
    """Delete container removes it."""
    create_response = await client.post(
        "/api/v1/containers",
        json={"name": "Delete Me", "type": "project"},
    )
    container_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/containers/{container_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/containers/{container_id}")
    assert get_response.status_code == 404
