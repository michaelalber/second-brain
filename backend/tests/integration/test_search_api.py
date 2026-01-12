import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_inbox_returns_capture_only(client: AsyncClient):
    """Inbox returns only notes in capture stage without a container."""
    # Create notes - one in inbox, one in a container
    await client.post(
        "/api/v1/notes",
        json={"title": "Inbox Note", "content": "In inbox"},
    )

    # Create a container and move another note there
    container_response = await client.post(
        "/api/v1/containers",
        json={"name": "Project", "type": "project"},
    )
    container_id = container_response.json()["id"]

    note_response = await client.post(
        "/api/v1/notes",
        json={"title": "Organized Note", "content": "Organized"},
    )
    note_id = note_response.json()["id"]

    await client.patch(
        f"/api/v1/notes/{note_id}/move",
        json={"container_id": container_id},
    )

    # Get inbox
    response = await client.get("/api/v1/inbox")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Inbox Note"


@pytest.mark.asyncio
async def test_search_returns_matching_notes(client: AsyncClient):
    """Search returns notes matching the query."""
    await client.post(
        "/api/v1/notes",
        json={"title": "Python Tutorial", "content": "Learn Python basics"},
    )
    await client.post(
        "/api/v1/notes",
        json={"title": "JavaScript Guide", "content": "Learn JS"},
    )

    response = await client.get("/api/v1/search?q=Python")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python Tutorial"


@pytest.mark.asyncio
async def test_search_matches_content(client: AsyncClient):
    """Search matches content as well as title."""
    await client.post(
        "/api/v1/notes",
        json={"title": "Note", "content": "Contains Python keyword"},
    )

    response = await client.get("/api/v1/search?q=Python")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_recent_returns_sorted_notes(client: AsyncClient):
    """Recent returns notes sorted by updated_at descending."""
    first_response = await client.post(
        "/api/v1/notes",
        json={"title": "First", "content": "Created first"},
    )
    first_id = first_response.json()["id"]

    await client.post(
        "/api/v1/notes",
        json={"title": "Second", "content": "Created second"},
    )

    # Update the first note to make it the most recent
    await client.put(
        f"/api/v1/notes/{first_id}",
        json={"title": "First Updated"},
    )

    response = await client.get("/api/v1/recent")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Most recently updated first
    assert data[0]["title"] == "First Updated"
    assert data[1]["title"] == "Second"


@pytest.mark.asyncio
async def test_recent_respects_limit(client: AsyncClient):
    """Recent respects the limit parameter."""
    for i in range(5):
        await client.post(
            "/api/v1/notes",
            json={"title": f"Note {i}", "content": "Content"},
        )

    response = await client.get("/api/v1/recent?limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
