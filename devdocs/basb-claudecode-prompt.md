# Claude Code Prompt: BASB (Building a Second Brain) Application

## Project Overview

Build a personal knowledge management system implementing Tiago Forte's "Building a Second Brain" methodology using FastAPI (Python) backend and Vue.js 3 frontend.

**Core Concepts to Implement:**
- **PARA**: Projects, Areas, Resources, Archives - organizational taxonomy
- **CODE**: Capture, Organize, Distill, Express - workflow stages
- **Progressive Summarization**: Multi-layer highlighting (L1: captured, L2: bold, L3: highlight, L4: executive summary)

---

## Technical Stack

### Backend
- **FastAPI** with async/await patterns
- **SQLAlchemy 2.0** with async support (SQLite for dev, PostgreSQL for prod)
- **Pydantic v2** for validation and settings
- **Alembic** for migrations
- **python-multipart** for file uploads

### Frontend
- **Vue.js 3** with Composition API + `<script setup>`
- **Pinia** for state management
- **Vue Router 4**
- **TailwindCSS** for styling
- **Tiptap** or **Milkdown** for rich text editing with markdown support
- **Vite** for build tooling

### Why These Choices
- FastAPI: Native async, auto OpenAPI docs, Pydantic integration - ideal for CRUD-heavy apps
- Vue 3 Composition API: Better TypeScript support, cleaner logic organization than Options API
- Tiptap: Extensible editor that can handle progressive summarization highlighting layers

---

## Project Structure

```
basb/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app factory
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # Async SQLAlchemy setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── note.py
│   │   │   ├── container.py     # PARA containers
│   │   │   └── tag.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── note.py
│   │   │   └── container.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependencies (db session, etc.)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── notes.py
│   │   │       ├── containers.py
│   │   │       ├── search.py
│   │   │       └── router.py
│   │   └── services/            # Business logic layer
│   │       ├── __init__.py
│   │       ├── note_service.py
│   │       └── search_service.py
│   ├── alembic/
│   ├── tests/
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── NoteEditor.vue
│   │   │   ├── ParaSidebar.vue
│   │   │   ├── NoteCard.vue
│   │   │   └── ProgressiveLayers.vue
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Inbox.vue        # Capture stage
│   │   │   ├── NoteView.vue
│   │   │   └── ExpressView.vue  # Output creation
│   │   ├── stores/
│   │   │   ├── notes.ts
│   │   │   └── containers.ts
│   │   ├── composables/
│   │   │   ├── useNotes.ts
│   │   │   └── useSearch.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── api/
│   │       └── client.ts        # Axios/fetch wrapper
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Data Models

### Container (PARA)
```python
class ContainerType(str, Enum):
    PROJECT = "project"      # Short-term efforts with deadlines
    AREA = "area"            # Ongoing responsibilities
    RESOURCE = "resource"    # Topics of interest
    ARCHIVE = "archive"      # Inactive items

class Container(Base):
    __tablename__ = "containers"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[ContainerType]
    description: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("containers.id"))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # For projects specifically
    deadline: Mapped[datetime | None]
    status: Mapped[str | None]  # active, completed, on_hold
```

### Note
```python
class CodeStage(str, Enum):
    CAPTURE = "capture"    # Raw input, inbox
    ORGANIZE = "organize"  # Filed in PARA
    DISTILL = "distill"    # Progressive summarization applied
    EXPRESS = "express"    # Used in output

class Note(Base):
    __tablename__ = "notes"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)  # Markdown with layer annotations
    content_html: Mapped[str | None] = mapped_column(Text)  # Rendered HTML
    
    # Progressive Summarization layers stored as JSON ranges
    # Format: [{"start": 0, "end": 50, "layer": 2}, ...]
    highlights: Mapped[dict] = mapped_column(JSON, default=dict)
    executive_summary: Mapped[str | None] = mapped_column(Text)  # Layer 4
    
    source_url: Mapped[str | None] = mapped_column(String(2000))
    source_type: Mapped[str | None]  # article, book, podcast, thought, meeting
    
    container_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("containers.id"))
    code_stage: Mapped[CodeStage] = mapped_column(default=CodeStage.CAPTURE)
    
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    captured_at: Mapped[datetime] = mapped_column(default=func.now())
    
    # Relationships
    container: Mapped["Container"] = relationship(back_populates="notes")
    tags: Mapped[list["Tag"]] = relationship(secondary=note_tags, back_populates="notes")
```

---

## API Endpoints

### Notes
```
POST   /api/v1/notes              # Quick capture (inbox)
GET    /api/v1/notes              # List with filters (container, stage, search)
GET    /api/v1/notes/{id}         # Get single note
PUT    /api/v1/notes/{id}         # Update note
PATCH  /api/v1/notes/{id}/move    # Move to container (organize)
PATCH  /api/v1/notes/{id}/highlights  # Update progressive summarization
DELETE /api/v1/notes/{id}
```

### Containers (PARA)
```
GET    /api/v1/containers              # List all with counts
POST   /api/v1/containers              # Create container
GET    /api/v1/containers/{id}         # Get with notes
PUT    /api/v1/containers/{id}
PATCH  /api/v1/containers/{id}/archive # Move to archive
DELETE /api/v1/containers/{id}
```

### Search & Discovery
```
GET    /api/v1/search?q={query}        # Full-text search
GET    /api/v1/inbox                   # Uncategorized captures
GET    /api/v1/recent                  # Recently modified
GET    /api/v1/stats                   # Dashboard metrics
```

---

## Key Features to Implement

### 1. Quick Capture (Inbox)
- Minimal friction note creation
- Browser extension hook (future: add API endpoint for external capture)
- Auto-extract title from URL if source provided
- Default to CAPTURE stage

### 2. PARA Organization
- Drag-and-drop notes between containers
- Visual distinction between P/A/R/A types
- Project deadline tracking
- Archive completed projects (preserve notes)

### 3. Progressive Summarization UI
- Layer 1: Full captured text (default)
- Layer 2: Bold key passages (first pass)
- Layer 3: Highlight within bold (most important)
- Layer 4: Executive summary field
- Toggle to view each layer independently
- Keyboard shortcuts for highlighting

### 4. Express/Output Mode
- Pull notes into a working document
- Side-by-side: source notes + output draft
- Track which notes contributed to outputs

### 5. Search & Discovery
- Full-text search across all notes
- Filter by: container, stage, date range, tags
- "Resurface" random notes from archives (serendipity)

---

## Implementation Order (TDD)

Each phase: write tests FIRST, then implement to pass.

### Phase 1: Backend Foundation
```
1. Write test: POST /notes returns 201 with id
2. Implement: Note model, schema, route → GREEN
3. Write test: GET /notes returns list
4. Implement: list endpoint → GREEN
5. Write test: Container CRUD
6. Implement: Container model, routes → GREEN
7. Refactor: Extract service layer
```

### Phase 2: Frontend Foundation
```
1. Write test: notesStore.quickCapture adds to inbox
2. Implement: Pinia store → GREEN
3. Write test: containersStore.fetch populates PARA
4. Implement: store + API client → GREEN
5. Build views against working stores
```

### Phase 3: Core Features
```
1. Write test: moveToContainer changes stage to 'organize'
2. Implement: PATCH endpoint + store action → GREEN
3. Write test: inbox returns only stage='capture'
4. Implement: filtered query → GREEN
```

### Phase 4: Rich Editor
```
1. Write test: highlighting updates saves ranges
2. Implement: PATCH /notes/{id}/highlights → GREEN
3. Build Tiptap extension for highlight layers
4. Write component test: ProgressiveLayers toggles visibility
```

### Phase 5: Search & Polish
```
1. Write test: search returns matching notes
2. Implement: full-text search (SQLite FTS5 or pg_trgm) → GREEN
3. Add dashboard metrics endpoint
4. Keyboard shortcut integration
```

---

## Commands to Start

```bash
# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy[asyncio] aiosqlite alembic pydantic-settings python-multipart
pip install pytest pytest-asyncio httpx pytest-cov factory-boy  # Testing

# Frontend setup  
cd frontend
npm create vite@latest . -- --template vue-ts
npm install pinia vue-router@4 @tiptap/vue-3 @tiptap/starter-kit @tiptap/extension-highlight tailwindcss postcss autoprefixer
npm install -D vitest @vue/test-utils @testing-library/vue jsdom @pinia/testing  # Testing
npx tailwindcss init -p

# Add to frontend/package.json scripts:
# "test": "vitest",
# "test:coverage": "vitest --coverage"
```

---

## Configuration

### Backend (.env)
```
DATABASE_URL=sqlite+aiosqlite:///./basb.db
# For production: postgresql+asyncpg://user:pass@localhost/basb
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Testing Strategy (TDD)

**Workflow: Red → Green → Refactor**

Every feature starts with a failing test. No production code without a test that demands it.

### Backend Testing Stack
```bash
pip install pytest pytest-asyncio httpx pytest-cov factory-boy
```

- **pytest + pytest-asyncio**: Async test support
- **httpx**: Async test client for FastAPI (replaces TestClient for async)
- **factory-boy**: Test data factories
- **pytest-cov**: Coverage reporting (target: 80%+)

### Backend Test Structure
```
backend/tests/
├── conftest.py              # Fixtures: async db session, test client, factories
├── factories/
│   ├── __init__.py
│   ├── note_factory.py
│   └── container_factory.py
├── unit/
│   ├── test_note_service.py
│   └── test_container_service.py
├── integration/
│   ├── test_notes_api.py
│   ├── test_containers_api.py
│   └── test_search_api.py
└── e2e/
    └── test_workflows.py    # Full CODE workflow tests
```

### Key Backend Test Patterns

**conftest.py fixtures:**
```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture
async def db_session():
    """Fresh in-memory SQLite for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
async def client(db_session):
    """Test client with overridden db dependency."""
    app.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

**Example TDD cycle for note creation:**
```python
# tests/integration/test_notes_api.py

@pytest.mark.asyncio
async def test_create_note_returns_201_with_id(client):
    """RED: Write this first, watch it fail."""
    response = await client.post("/api/v1/notes", json={
        "title": "Test Note",
        "content": "Some content"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Note"
    assert data["code_stage"] == "capture"  # Default to inbox

@pytest.mark.asyncio
async def test_create_note_without_title_returns_422(client):
    """Validation test."""
    response = await client.post("/api/v1/notes", json={
        "content": "No title provided"
    })
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_note_moves_to_container_updates_stage(client, db_session):
    """Moving note from inbox to PARA container changes stage to ORGANIZE."""
    # Arrange
    container = await ContainerFactory.create(session=db_session, type="project")
    note = await NoteFactory.create(session=db_session, code_stage="capture")
    
    # Act
    response = await client.patch(f"/api/v1/notes/{note.id}/move", json={
        "container_id": str(container.id)
    })
    
    # Assert
    assert response.status_code == 200
    assert response.json()["code_stage"] == "organize"
    assert response.json()["container_id"] == str(container.id)
```

### Frontend Testing Stack
```bash
npm install -D vitest @vue/test-utils @testing-library/vue jsdom @pinia/testing
```

### Frontend Test Structure
```
frontend/src/
├── components/
│   ├── NoteCard.vue
│   └── __tests__/
│       └── NoteCard.spec.ts
├── stores/
│   ├── notes.ts
│   └── __tests__/
│       └── notes.spec.ts
├── composables/
│   ├── useNotes.ts
│   └── __tests__/
│       └── useNotes.spec.ts
└── views/
    └── __tests__/
        └── Inbox.spec.ts
```

**Example frontend TDD:**
```typescript
// src/stores/__tests__/notes.spec.ts
import { setActivePinia, createPinia } from 'pinia'
import { useNotesStore } from '../notes'
import { vi, describe, it, expect, beforeEach } from 'vitest'

describe('Notes Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('adds note to inbox with capture stage', async () => {
    const store = useNotesStore()
    
    await store.quickCapture({ title: 'New idea', content: 'Details...' })
    
    expect(store.inbox).toHaveLength(1)
    expect(store.inbox[0].code_stage).toBe('capture')
  })

  it('moves note updates its container and stage', async () => {
    const store = useNotesStore()
    const note = { id: '123', title: 'Test', code_stage: 'capture' }
    store.notes = [note]
    
    await store.moveToContainer('123', 'project-456')
    
    expect(store.notes[0].container_id).toBe('project-456')
    expect(store.notes[0].code_stage).toBe('organize')
  })
})
```

### TDD Commands
```bash
# Backend: run tests in watch mode during development
cd backend
pytest --cov=app --cov-report=term-missing -v --tb=short

# Frontend: Vitest watch mode
cd frontend
npm run test -- --watch

# Run specific test file
pytest tests/integration/test_notes_api.py -v
npm run test -- src/stores/__tests__/notes.spec.ts
```

### Coverage Requirements
- Backend: 80% minimum, 90% for services layer
- Frontend: 70% minimum for stores/composables, components tested for key interactions

### What to Test vs Skip
**Always test:**
- API endpoint behavior (status codes, response shapes)
- Service layer business logic
- Store actions and state mutations
- Component user interactions

**Skip/mock:**
- Database driver internals
- Third-party library internals
- Pure UI styling

---

## Future Enhancements (Out of Scope for MVP)

- Browser extension for web clipping
- Mobile PWA
- AI-assisted summarization (local LLM via Ollama)
- Sync with external tools (Readwise, Notion import)
- Spaced repetition for review
- Graph view of note connections
