# CLAUDE.md - BASB (Building a Second Brain) Application

## Project Overview

Personal knowledge management system implementing Tiago Forte's BASB methodology:
- **PARA**: Projects, Areas, Resources, Archives (organizational taxonomy)
- **CODE**: Capture, Organize, Distill, Express (workflow stages)
- **Progressive Summarization**: Multi-layer highlighting (L1→L4)

## Tech Stack

**Backend:** FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic, SQLite/PostgreSQL
**Frontend:** Vue 3 (Composition API + `<script setup>`), Pinia, Vue Router 4, TailwindCSS, Tiptap, Vite, TypeScript

## Critical Rules

### TDD is Mandatory
1. **Never write production code without a failing test first**
2. Cycle: RED (write failing test) → GREEN (minimal code to pass) → REFACTOR
3. Run tests before committing: `pytest` (backend), `npm run test` (frontend)
4. Coverage targets: Backend 80%+, Frontend 70%+

### Code Style

**Python (Backend):**
- Use `async/await` throughout - no sync database calls
- Type hints required on all function signatures
- Pydantic models for all request/response schemas
- Services layer for business logic, routes stay thin
- Use `Mapped[]` for SQLAlchemy 2.0 column definitions

**TypeScript (Frontend):**
- Composition API with `<script setup lang="ts">` only
- Define prop/emit types explicitly
- Pinia stores: actions async, getters for derived state
- Composables for reusable logic

### Architecture Patterns
- Backend: Layered (routes → services → repositories)
- Keep route handlers under 15 lines - delegate to services
- One Pydantic schema per use case (CreateNote, UpdateNote, NoteResponse)

### YAGNI (You Aren't Gonna Need It)
- Start with direct implementations
- Add abstractions only when complexity demands it
- Create interfaces only when multiple implementations exist
- No dependency injection containers
- No plugin architecture

### Security-By-Design
- Validate all inputs at system boundaries via Pydantic schemas
- Use parameterized queries — SQLAlchemy ORM prevents SQL injection by default
- Never trust client-side validation alone
- Sanitize user-provided content (rich text editor output) before storage
- Lock CORS to specific origins with explicit methods and headers
- Never include secrets in source code — use environment variables

### Quality Gates
- **Cyclomatic Complexity**: Methods <10, classes <20
- **Code Coverage**: 80% minimum for business logic (backend), 70% (frontend)
- **Maintainability Index**: Target 70+
- **Code Duplication**: Maximum 3%

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

## Git Workflow

- Commit after each GREEN phase
- Commit message format: `feat|fix|test|refactor: brief description`
- Don't commit failing tests (RED phase is local only)

## When Stuck

1. Check if test is testing the right thing
2. Simplify - can you write a smaller test?
3. Check FastAPI/Vue docs for async patterns
4. Ask for help with specific error messages
