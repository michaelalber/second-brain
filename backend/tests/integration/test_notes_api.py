import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_note_returns_201_with_id(client: AsyncClient):
    """Creating a note returns 201 with the note data."""
    response = await client.post(
        "/api/v1/notes",
        json={"title": "Test Note", "content": "Test content"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Note"
    assert data["content"] == "Test content"
    assert data["code_stage"] == "capture"


@pytest.mark.asyncio
async def test_create_note_without_title_returns_422(client: AsyncClient):
    """Creating a note without title returns validation error."""
    response = await client.post(
        "/api/v1/notes",
        json={"content": "No title provided"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_notes_returns_list(client: AsyncClient):
    """List notes returns a list of notes."""
    # Create a note first
    await client.post(
        "/api/v1/notes",
        json={"title": "Note 1", "content": "Content 1"},
    )

    response = await client.get("/api/v1/notes")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Note 1"


@pytest.mark.asyncio
async def test_get_note_returns_note(client: AsyncClient):
    """Get note by ID returns the note."""
    create_response = await client.post(
        "/api/v1/notes",
        json={"title": "Get Me", "content": "Content"},
    )
    note_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/notes/{note_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Get Me"


@pytest.mark.asyncio
async def test_get_nonexistent_note_returns_404(client: AsyncClient):
    """Get nonexistent note returns 404."""
    response = await client.get("/api/v1/notes/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_note(client: AsyncClient):
    """Update note changes its fields."""
    create_response = await client.post(
        "/api/v1/notes",
        json={"title": "Original", "content": "Original content"},
    )
    note_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/notes/{note_id}",
        json={"title": "Updated"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["content"] == "Original content"


@pytest.mark.asyncio
async def test_delete_note(client: AsyncClient):
    """Delete note removes it."""
    create_response = await client.post(
        "/api/v1/notes",
        json={"title": "Delete Me", "content": "Content"},
    )
    note_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/notes/{note_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/notes/{note_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_move_note_to_container_changes_stage(client: AsyncClient):
    """Moving a note to a container changes its stage to organize."""
    # Create a container first
    container_response = await client.post(
        "/api/v1/containers",
        json={"name": "My Project", "type": "project"},
    )
    container_id = container_response.json()["id"]

    # Create a note
    note_response = await client.post(
        "/api/v1/notes",
        json={"title": "Move Me", "content": "Content"},
    )
    note_id = note_response.json()["id"]
    assert note_response.json()["code_stage"] == "capture"

    # Move the note
    response = await client.patch(
        f"/api/v1/notes/{note_id}/move",
        json={"container_id": container_id},
    )

    assert response.status_code == 200
    assert response.json()["container_id"] == container_id
    assert response.json()["code_stage"] == "organize"


@pytest.mark.asyncio
async def test_update_highlights(client: AsyncClient):
    """Updating highlights changes code_stage to distill."""
    # Create a note
    note_response = await client.post(
        "/api/v1/notes",
        json={"title": "Highlight Me", "content": "Some important content here"},
    )
    note_id = note_response.json()["id"]

    # Update highlights
    response = await client.patch(
        f"/api/v1/notes/{note_id}/highlights",
        json={"highlights": [{"start": 0, "end": 10, "layer": 2}]},
    )

    assert response.status_code == 200
    assert response.json()["code_stage"] == "distill"
    assert "highlights" in response.json()


@pytest.mark.asyncio
async def test_update_nonexistent_note_returns_404(client: AsyncClient):
    """Update nonexistent note returns 404."""
    response = await client.put(
        "/api/v1/notes/00000000-0000-0000-0000-000000000000",
        json={"title": "Updated"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_move_nonexistent_note_returns_404(client: AsyncClient):
    """Move nonexistent note returns 404."""
    response = await client.patch(
        "/api/v1/notes/00000000-0000-0000-0000-000000000000/move",
        json={"container_id": None},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_highlights_nonexistent_note_returns_404(client: AsyncClient):
    """Update highlights on nonexistent note returns 404."""
    response = await client.patch(
        "/api/v1/notes/00000000-0000-0000-0000-000000000000/highlights",
        json={"highlights": [{"start": 0, "end": 10, "layer": 2}]},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_note_returns_404(client: AsyncClient):
    """Delete nonexistent note returns 404."""
    response = await client.delete("/api/v1/notes/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_notes_with_filters(client: AsyncClient):
    """List notes with query filters."""
    # Create a container
    container_response = await client.post(
        "/api/v1/containers",
        json={"name": "Filter Test", "type": "project"},
    )
    container_id = container_response.json()["id"]

    # Create notes
    await client.post(
        "/api/v1/notes",
        json={"title": "Apple Note", "content": "About apples"},
    )
    note_response = await client.post(
        "/api/v1/notes",
        json={"title": "Orange Note", "content": "About oranges"},
    )
    note_id = note_response.json()["id"]

    # Move one note to container
    await client.patch(
        f"/api/v1/notes/{note_id}/move",
        json={"container_id": container_id},
    )

    # Filter by container
    response = await client.get(f"/api/v1/notes?container_id={container_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Orange Note"

    # Filter by stage
    response = await client.get("/api/v1/notes?stage=capture")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Apple Note"

    # Filter by query
    response = await client.get("/api/v1/notes?q=apple")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Apple Note"
