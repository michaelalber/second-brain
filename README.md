# Second Brain

A personal knowledge management system implementing Tiago Forte's "Building a Second Brain" methodology.

## Core Concepts

- **PARA**: Organizational taxonomy - Projects, Areas, Resources, Archives
- **CODE**: Workflow stages - Capture, Organize, Distill, Express
- **Progressive Summarization**: Multi-layer highlighting (L1→L4)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| Frontend | Vue 3 (Composition API), Pinia, Vue Router 4, TailwindCSS |
| Database | SQLite (dev), PostgreSQL (prod) |
| Testing | pytest + pytest-asyncio, Vitest |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### Frontend

```bash
cd frontend
npm install
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
- `GET /api/v1/notes` - List with filters
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

## Development

### Running Tests

```bash
# Backend
cd backend
source .venv/bin/activate
pytest -v --cov=app

# Frontend
cd frontend
npm run test
```

### Code Style

- Backend: async/await, type hints, layered architecture
- Frontend: Composition API with `<script setup>`, TypeScript

## License

MIT
 Michael
