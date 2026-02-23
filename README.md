# Second Brain

A personal knowledge management system implementing Tiago Forte's "Building a Second Brain" methodology.

## Features

- **PARA Organization** - Projects, Areas, Resources, Archives taxonomy
- **CODE Workflow** - Capture, Organize, Distill, Express stages
- **Progressive Summarization** - Multi-layer highlighting (L1 raw text → L4 executive summary)
- **Quick Capture** - Fast note capture to inbox
- **Rich Editor** - Tiptap-based editor with highlighting support
- **Full-Text Search** - Search across all notes and containers
- **Keyboard Shortcuts** - Fast navigation and note management

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| Frontend | Vue 3 (Composition API), Pinia, Vue Router 4, TailwindCSS, Tiptap |
| Database | SQLite (dev), PostgreSQL (prod) |
| Testing | pytest + pytest-asyncio, Vitest |
| Linting | ruff, mypy, bandit |

## Prerequisites

- Python 3.10+
- Node.js 18+

## Installation

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
```

### Frontend

```bash
cd frontend
npm install
```

## Usage

### Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000 (API docs at http://localhost:8000/docs)

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at http://localhost:5173

## Project Structure

```
second-brain/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── tests/
│   └── alembic/             # Migrations
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # Vue components
│   │   ├── stores/          # Pinia stores
│   │   ├── views/           # Route pages
│   │   └── types/           # TypeScript types
│   └── package.json
└── README.md
```

## API Endpoints

### Notes
- `POST /api/v1/notes` - Quick capture to inbox
- `GET /api/v1/notes` - List with filters (`container_id`, `stage`, `q`)
- `GET /api/v1/notes/{id}` - Get single note
- `PUT /api/v1/notes/{id}` - Update note
- `PATCH /api/v1/notes/{id}/move` - Move to container
- `PATCH /api/v1/notes/{id}/highlights` - Update progressive summarization
- `DELETE /api/v1/notes/{id}` - Delete note

### Containers (PARA)
- `POST /api/v1/containers` - Create container
- `GET /api/v1/containers` - List with note counts
- `GET /api/v1/containers/{id}` - Get with notes
- `PUT /api/v1/containers/{id}` - Update container
- `PATCH /api/v1/containers/{id}/archive` - Archive container
- `DELETE /api/v1/containers/{id}` - Delete container

### Search
- `GET /api/v1/inbox` - Uncategorized captures
- `GET /api/v1/search?q=` - Full-text search
- `GET /api/v1/recent` - Recently modified

## Configuration

Configuration via environment variables or `.env` file:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./basb.db  # Dev (default)
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/basb  # Prod

# Server
HOST=0.0.0.0
PORT=8000
```

## Development

### Running Tests

```bash
# Backend
cd backend
source .venv/bin/activate
pytest                                      # All tests
pytest -v --cov=app --cov-report=term-missing  # With coverage

# Frontend
cd frontend
npm run test
npm run test -- --watch                     # Watch mode
```

### Code Quality

```bash
cd backend
source .venv/bin/activate

# Lint
ruff check app/ tests/

# Type check
mypy app/

# Security scan
bandit -r app/ -c pyproject.toml
```

## Security

- Input validation on all API boundaries
- Parameterized queries via SQLAlchemy (no raw SQL)
- Pydantic schema validation for all request/response payloads
- CORS configuration for local development

## Troubleshooting

**Database Migration Errors:**
- Ensure migrations are up to date: `alembic upgrade head`
- For a fresh start: delete `basb.db` and re-run migrations

**Frontend API Errors:**
- Verify backend is running on port 8000
- Check browser console for CORS issues

**Test Failures:**
- Ensure you're in the virtual environment: `source .venv/bin/activate`
- Tests use in-memory SQLite, no external deps needed

## Contributing

This is a personal/educational project, but suggestions and feedback are welcome via issues.

## License

MIT License - see [LICENSE](LICENSE) for details.
