import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.models.note import CodeStage, Note
from app.schemas.note import NoteCreate, NoteUpdate, NoteHighlightsUpdate, HighlightRange
from app.services.note_service import NoteService


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def note_service(mock_db):
    """Create a NoteService with a mock database."""
    return NoteService(mock_db)


@pytest.mark.asyncio
async def test_get_note_returns_none_when_not_found(note_service, mock_db):
    """get_note returns None when note doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await note_service.get_note(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_update_note_returns_none_when_not_found(note_service, mock_db):
    """update_note returns None when note doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await note_service.update_note(uuid4(), NoteUpdate(title="New Title"))

    assert result is None


@pytest.mark.asyncio
async def test_update_note_applies_changes(note_service, mock_db):
    """update_note applies only the provided changes."""
    note_id = uuid4()
    existing_note = Note(
        id=note_id,
        title="Original",
        content="Original content",
        code_stage=CodeStage.CAPTURE,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_note
    mock_db.execute.return_value = mock_result

    result = await note_service.update_note(note_id, NoteUpdate(title="Updated"))

    assert result.title == "Updated"
    assert result.content == "Original content"


@pytest.mark.asyncio
async def test_move_to_container_returns_none_when_not_found(note_service, mock_db):
    """move_to_container returns None when note doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await note_service.move_to_container(uuid4(), uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_move_to_container_sets_capture_when_moving_to_inbox(note_service, mock_db):
    """Moving to inbox (container_id=None) sets stage to capture."""
    note_id = uuid4()
    existing_note = Note(
        id=note_id,
        title="Test",
        content="Content",
        code_stage=CodeStage.ORGANIZE,
        container_id=uuid4(),
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_note
    mock_db.execute.return_value = mock_result

    result = await note_service.move_to_container(note_id, None)

    assert result.code_stage == CodeStage.CAPTURE
    assert result.container_id is None


@pytest.mark.asyncio
async def test_move_to_container_sets_organize_when_from_capture(note_service, mock_db):
    """Moving from capture to container sets stage to organize."""
    note_id = uuid4()
    container_id = uuid4()
    existing_note = Note(
        id=note_id,
        title="Test",
        content="Content",
        code_stage=CodeStage.CAPTURE,
        container_id=None,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_note
    mock_db.execute.return_value = mock_result

    result = await note_service.move_to_container(note_id, container_id)

    assert result.code_stage == CodeStage.ORGANIZE
    assert result.container_id == container_id


@pytest.mark.asyncio
async def test_move_to_container_preserves_stage_when_already_organized(note_service, mock_db):
    """Moving between containers preserves stage if not capture."""
    note_id = uuid4()
    new_container_id = uuid4()
    existing_note = Note(
        id=note_id,
        title="Test",
        content="Content",
        code_stage=CodeStage.DISTILL,
        container_id=uuid4(),
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_note
    mock_db.execute.return_value = mock_result

    result = await note_service.move_to_container(note_id, new_container_id)

    assert result.code_stage == CodeStage.DISTILL
    assert result.container_id == new_container_id


@pytest.mark.asyncio
async def test_update_highlights_returns_none_when_not_found(note_service, mock_db):
    """update_highlights returns None when note doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    highlights = NoteHighlightsUpdate(highlights=[HighlightRange(start=0, end=10, layer=2)])
    result = await note_service.update_highlights(uuid4(), highlights)

    assert result is None


@pytest.mark.asyncio
async def test_update_highlights_sets_distill_stage(note_service, mock_db):
    """update_highlights sets stage to distill from capture/organize."""
    note_id = uuid4()
    existing_note = Note(
        id=note_id,
        title="Test",
        content="Content",
        code_stage=CodeStage.ORGANIZE,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_note
    mock_db.execute.return_value = mock_result

    highlights = NoteHighlightsUpdate(highlights=[HighlightRange(start=0, end=10, layer=2)])
    result = await note_service.update_highlights(note_id, highlights)

    assert result.code_stage == CodeStage.DISTILL
    assert result.highlights == {"highlights": [{"start": 0, "end": 10, "layer": 2}]}


@pytest.mark.asyncio
async def test_update_highlights_preserves_express_stage(note_service, mock_db):
    """update_highlights preserves express stage."""
    note_id = uuid4()
    existing_note = Note(
        id=note_id,
        title="Test",
        content="Content",
        code_stage=CodeStage.EXPRESS,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_note
    mock_db.execute.return_value = mock_result

    highlights = NoteHighlightsUpdate(highlights=[HighlightRange(start=0, end=10, layer=2)])
    result = await note_service.update_highlights(note_id, highlights)

    assert result.code_stage == CodeStage.EXPRESS


@pytest.mark.asyncio
async def test_delete_note_returns_false_when_not_found(note_service, mock_db):
    """delete_note returns False when note doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await note_service.delete_note(uuid4())

    assert result is False


@pytest.mark.asyncio
async def test_delete_note_returns_true_on_success(note_service, mock_db):
    """delete_note returns True when note is deleted."""
    note_id = uuid4()
    existing_note = Note(
        id=note_id,
        title="Test",
        content="Content",
        code_stage=CodeStage.CAPTURE,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_note
    mock_db.execute.return_value = mock_result

    result = await note_service.delete_note(note_id)

    assert result is True
    mock_db.delete.assert_called_once_with(existing_note)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_list_notes_with_all_filters(note_service, mock_db):
    """list_notes applies all filters when provided."""
    container_id = uuid4()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await note_service.list_notes(
        container_id=container_id,
        stage="capture",
        q="search term"
    )

    assert result == []
    mock_db.execute.assert_called_once()
