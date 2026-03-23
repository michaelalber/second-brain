# CLAUDE.md - BASB (Building a Second Brain) Application

> Global rules (TDD, security, quality gates, Python/TypeScript standards, AI behavior, YAGNI,
> git hygiene, grounded-code-mcp) are defined in `~/.claude/CLAUDE.md` and apply here automatically.
> Rules below are project-specific overrides and additions only.

## Project Overview

Personal knowledge management system implementing Tiago Forte's BASB methodology:
- **PARA**: Projects, Areas, Resources, Archives (organizational taxonomy)
- **CODE**: Capture, Organize, Distill, Express (workflow stages)
- **Progressive Summarization**: Multi-layer highlighting (L1→L4)

## Tech Stack

**Backend:** FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic, SQLite/PostgreSQL
**Frontend:** Vue 3 (Composition API + `<script setup>`), Pinia, Vue Router 4, TailwindCSS, Tiptap, Vite, TypeScript

## Architecture

- Backend uses layered architecture: routes → services → repositories (not vertical slice)
- Keep route handlers under 15 lines — delegate to services
- One Pydantic schema per use case (CreateNote, UpdateNote, NoteResponse)
- Use `Mapped[]` for SQLAlchemy 2.0 column definitions

## Coverage Targets

- Backend: 80% (matches global)
- Frontend: **70%** minimum (project-specific lower threshold for UI components)

## Vue / Pinia Conventions

- Composition API with `<script setup lang="ts">` only
- Define prop/emit types explicitly
- Pinia stores: actions async, getters for derived state
- Composables for reusable logic

## Project-Specific Security

In addition to global security rules:
- Sanitize user-provided content (rich text editor output) before storage
- Lock CORS to specific origins with explicit methods and headers

## Directory Structure

```
basb/
├── backend/
│   ├── app/
│   │   ├── main.py           # App factory, middleware
│   │   ├── config.py         # Pydantic Settings
│   │   ├── database.py       # Async engine + session
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── api/v1/           # Route handlers
│   │   └── services/         # Business logic
│   ├── tests/
│   │   ├── conftest.py       # Fixtures
│   │   ├── factories/        # Test data factories
│   │   ├── unit/
│   │   └── integration/
│   └── alembic/
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI
│   │   ├── views/            # Route pages
│   │   ├── stores/           # Pinia stores
│   │   ├── composables/      # Shared logic
│   │   ├── types/            # TypeScript types
│   │   └── api/              # HTTP client
│   └── package.json
└── CLAUDE.md
```

## Common Commands

```bash
# Backend
cd backend
source .venv/bin/activate
pytest -v --tb=short                    # Run tests
pytest --cov=app --cov-report=term-missing  # With coverage
ruff check app/ tests/                  # Lint
mypy app/                               # Type checking
bandit -r app/ -c pyproject.toml        # Security scan
uvicorn app.main:app --reload           # Dev server (port 8000)
alembic revision --autogenerate -m "msg"  # Create migration
alembic upgrade head                    # Apply migrations

# Frontend
cd frontend
npm run dev                             # Dev server (port 5173)
npm run test                            # Run Vitest
npm run test -- --watch                 # Watch mode
npm run build                           # Production build
npm run lint                            # ESLint
```

## Database

- Dev: SQLite at `backend/basb.db`
- Test: In-memory SQLite (`:memory:`)
- Prod: PostgreSQL (swap driver in DATABASE_URL)

## API Design

Base URL: `/api/v1`

Key endpoints:
- `POST /notes` - Quick capture to inbox
- `GET /notes?container_id=&stage=&q=` - List with filters
- `PATCH /notes/{id}/move` - Move to PARA container
- `PATCH /notes/{id}/highlights` - Update progressive summarization
- `GET /containers` - PARA structure with note counts
- `GET /inbox` - Uncategorized captures
- `GET /search?q=` - Full-text search

## Domain Concepts

**CodeStage enum:** `capture` → `organize` → `distill` → `express`
**ContainerType enum:** `project`, `area`, `resource`, `archive`

**Progressive Summarization layers:**
- L1: Raw captured text
- L2: Bold passages (first pass highlighting)
- L3: Highlighted within bold (key insights)
- L4: Executive summary (your own words)

Store L2/L3 as JSON ranges: `{"highlights": [{"start": 0, "end": 50, "layer": 2}]}`

## Implementation Phases

1. **Backend Foundation** - Models, migrations, CRUD endpoints
2. **Frontend Foundation** - Vue setup, routing, stores, basic views
3. **Core Features** - Capture flow, PARA sidebar, note list/detail
4. **Rich Editor** - Tiptap + progressive summarization highlighting
5. **Search & Polish** - Full-text search, dashboard, keyboard shortcuts

## Testing Patterns

**Backend integration test example:**
```python
@pytest.mark.asyncio
async def test_create_note_returns_201(client):
    response = await client.post("/api/v1/notes", json={
        "title": "Test", "content": "Body"
    })
    assert response.status_code == 201
    assert response.json()["code_stage"] == "capture"
```

**Frontend store test example:**
```typescript
it('moves note updates stage to organize', async () => {
  const store = useNotesStore()
  await store.moveToContainer('note-id', 'container-id')
  expect(store.notes[0].code_stage).toBe('organize')
})
```

## When Stuck

1. Check if test is testing the right thing
2. Simplify - can you write a smaller test?
3. Check FastAPI/Vue docs for async patterns
4. Ask for help with specific error messages
