---
feature: rag-document-chat
artifact: research
status: complete
created: 2026-07-03
phase: RESEARCH
neutral_topic: >
  How the second-brain backend models and persists notes, containers, and tags; how
  services are layered under routes; how FastAPI routes and Pydantic schemas are structured;
  how the async DB engine/session is configured; how Alembic migrations are organized; how the
  Vue frontend (stores, views, api client, types, router) is structured; existing
  search/embedding/LLM integration points; config/settings patterns; and test conventions.
ticket_loaded: false
method_note: >
  Subagent delegation (research-file-locator / research-code-analyzer / research-pattern-finder)
  was unavailable as a spawnable tool in this execution environment. Mapping was performed
  directly with read-only Read/Grep/Glob-equivalent commands over the repository. Findings are
  objective and cited to file:line. No recommendations or design decisions appear below.
---

# QRSPI Research — second-brain codebase map

> Objective inventory of the existing second-brain codebase, mapped against the areas named in
> the answered `questions.md`. Every claim cites `file:line`. Opinions and design choices are
> intentionally absent. Open questions (facts not found / ambiguities) are listed at the end.

## 0. Current-state summary (facts)

- The repo is NOT an empty scaffold. Backend (models, schemas, services, API, Alembic, tests) and
  frontend (stores, views, components, api client, router, tests, Tiptap editor) are both
  implemented for the notes/containers/PARA domain. Full file tree confirmed under
  `backend/app/`, `backend/tests/`, `frontend/src/`.
- No LLM, embedding, vector-store, Ollama, Qdrant, pgvector, Docling, MCP, chat, or document-file
  code exists anywhere in `backend/app` or `frontend/src`. A case-insensitive grep for
  `ollama|qdrant|pgvector|embedding|docling|grounded-code` across both source trees returned no
  matches; the only hits for `document`/`chat` are incidental DOM calls
  (`frontend/src/composables/useKeyboardShortcuts.ts:94,106,125,129`;
  `frontend/src/views/NoteView.vue:51,93,202`).

## 1. Backend — data model & persistence

- `Note` model: `backend/app/models/note.py:27-51`. Columns include `id` (UUID PK,
  `default=uuid.uuid4`, note.py:30), `title` String(500), `content` Text, `content_html`
  (nullable), `highlights` (`sqlalchemy.dialects.sqlite.JSON`, `default=dict`, note.py:9,34),
  `executive_summary`, `source_url` String(2000), `source_type` String(50), `container_id`
  (nullable FK → `containers.id`, note.py:38-40), `code_stage` (enum, default CAPTURE),
  `created_at`/`updated_at`/`captured_at` DateTime with `func.now()` (note.py:42-46).
  Relationships: `container` (back_populates="notes") and `tags` (secondary=`note_tags`)
  (note.py:49-50).
- `CodeStage` enum (`capture|organize|distill|express`): `backend/app/models/note.py:20-24`.
- `Container` model: `backend/app/models/container.py:24-45`. Self-referential hierarchy via
  `parent_id` FK → `containers.id` (container.py:31) with `parent`/`children` relationships
  (container.py:41-44), plus `notes` relationship (container.py:45). Fields: `name`, `type`
  (`ContainerType`), `description`, `is_active` (default True), `deadline`, `status`, timestamps.
- `ContainerType` enum (`project|area|resource|archive`): `backend/app/models/container.py:17-21`.
- `Tag` model + `note_tags` M2M association table with `ondelete="CASCADE"`:
  `backend/app/models/tag.py:16-32`. `Tag.name` is `unique=True` (tag.py:28).
- Model package exports: `backend/app/models/__init__.py:1-12`.
- `highlights` is stored as SQLite-dialect JSON specifically (note.py:9,34), not dialect-agnostic
  `JSON`. Progressive-summarization ranges are the documented shape (see CLAUDE.md), but no `layer`
  4 / executive-summary logic beyond the `executive_summary` column and `highlights` dict exists in
  the model.
- There are NO provenance columns (`derived_from`, `derivation_layer`, `supersedes`), NO embedding
  column, and NO document/chunk/conversation tables in any model file (confirmed by full read of
  `backend/app/models/`).

## 2. Backend — DB engine, session, config

- Async engine + sessionmaker + `DeclarativeBase` `Base` + `get_db()` dependency (commit-on-success
  / rollback-on-exception generator): `backend/app/database.py:8-31`.
- Settings via `pydantic_settings.BaseSettings`, `.env` loaded, `extra="ignore"`:
  `backend/app/config.py:4-16`. Only three settings exist: `DATABASE_URL`
  (default `sqlite+aiosqlite:///./basb.db`, config.py:11), `DEBUG` (default True), `CORS_ORIGINS`
  (default `["http://localhost:5173"]`). No Ollama/Qdrant/embedding/feature-flag settings exist.
- App factory + CORS middleware + router mount at prefix `/api/v1`: `backend/app/main.py:18-33`.
  `lifespan` is a no-op stub (main.py:11-16). CORS uses `allow_methods=["*"]`,
  `allow_headers=["*"]` (main.py:29-30).
- DB session dependency alias `DbSession = Annotated[AsyncSession, Depends(get_db)]`:
  `backend/app/api/deps.py:8`.

## 3. Backend — routes & schemas

- Router aggregation: `backend/app/api/v1/router.py:1-9`. Mounts `notes` (prefix `/notes`),
  `containers` (prefix `/containers`), and `search` (no prefix — its paths are `/inbox`, `/search`,
  `/recent`). Combined with the app-level `/api/v1` prefix (main.py:33), effective search paths are
  `/api/v1/inbox`, `/api/v1/search`, `/api/v1/recent`.
- Notes routes: `backend/app/api/v1/notes.py:19-79`. `POST ""` (201), `GET ""` (filters
  `container_id`/`stage`/`q`), `GET/PUT /{id}`, `PATCH /{id}/move`, `PATCH /{id}/highlights`,
  `DELETE /{id}` (204). Handlers instantiate `NoteService(db)` inline and stay thin (≤ ~5 lines
  each), matching the project rule "route handlers under 15 lines" (CLAUDE.md).
- Containers routes: `backend/app/api/v1/containers.py:19-65`. CRUD + `PATCH /{id}/archive`.
- Search routes: `backend/app/api/v1/search.py:11-26`. `GET /inbox`, `GET /search?q=`,
  `GET /recent?limit=`.
- Note schemas (one-per-use-case pattern): `backend/app/schemas/note.py`. `NoteBase` (note.py:10-14),
  `NoteCreate` (17-18), `NoteUpdate` (21-27), `NoteMoveRequest` (30-31), `HighlightRange`
  (34-37, `layer: int  # 2 or 3`), `NoteHighlightsUpdate` (40-41), `NoteResponse`
  (`ConfigDict(from_attributes=True)`, 44-55).
- Container schemas: `backend/app/schemas/container.py`. `ContainerBase`, `ContainerCreate`,
  `ContainerUpdate`, `ContainerResponse` (from_attributes), `ContainerWithCount` (adds
  `note_count`), `ContainerWithNotes` (adds `notes: list[NoteResponse]`) (container.py:12-49).
- Route handlers return ORM objects and rely on `response_model` + `from_attributes` for
  serialization (e.g. notes.py:19-22 returns `Note`, declares `response_model=NoteResponse`).

## 4. Backend — services (business logic layer)

- Architecture is routes → services (no separate repository layer; services hold SQLAlchemy queries
  directly). Confirmed across all three services.
- `NoteService`: `backend/app/services/note_service.py:10-105`. Takes `AsyncSession` in `__init__`
  (note_service.py:11-12). `create_note` forces `code_stage=CAPTURE` (note_service.py:20).
  `list_notes` filters with `.ilike("%q%")` on title/content (note_service.py:44) — substring, not
  vector/full-text. `move_to_container` mutates `code_stage` on move (CAPTURE→ORGANIZE, or →CAPTURE
  when moved to inbox, note_service.py:71-77). `update_highlights` advances stage to DISTILL and
  writes `{"highlights": [...]}` (note_service.py:89-92). `delete_note` is a hard delete
  (note_service.py:98-105).
- `ContainerService`: `backend/app/services/container_service.py:12-107`. `list_containers_with_counts`
  uses `outerjoin` + `func.count(Note.id)` + `group_by` and hand-builds `ContainerWithCount`
  (container_service.py:42-70). `get_container_with_notes` uses `selectinload(Container.notes)`
  (container_service.py:34-40). `archive_container` sets type=ARCHIVE + `is_active=False`
  (container_service.py:87-97).
- `SearchService`: `backend/app/services/search_service.py:7-33`. `get_inbox` = notes where
  `code_stage==CAPTURE AND container_id IS NULL` (search_service.py:11-19). `search_notes` = `.ilike`
  substring match on title/content (search_service.py:21-28). `get_recent` = order by `updated_at`
  desc, limit (search_service.py:30-33). No semantic/vector search exists.

## 5. Backend — Alembic migrations

- Single migration on disk: `backend/alembic/versions/6a9f679dbc20_initial_models.py` (revision
  `6a9f679dbc20`, `down_revision = None`, dated 2026-01-12). Creates `containers`, `tags`, `notes`,
  `note_tags` (initial.py:24-68). `notes.highlights` uses `sqlite.JSON()` (initial.py:50).
- `backend/alembic/env.py` runs async migrations (`async_engine_from_config` + `run_async_migrations`,
  env.py:58-78), imports `Base` and models for autogenerate target metadata (env.py:10-24). Models
  must be imported in `env.py` for autogenerate to see them (currently `Container, Note, Tag`,
  env.py:11).
- `backend/alembic.ini` and standard `README`/`script.py.mako` present. No pgvector/extension
  migrations exist.

## 6. Backend — dependencies, tooling, tests

- `backend/pyproject.toml`. Runtime deps (pyproject.toml:6-16): fastapi, uvicorn[standard], pydantic,
  pydantic-settings, python-multipart, zipp, sqlalchemy[asyncio], aiosqlite, alembic. Dev deps
  (18-29): pytest, pytest-asyncio, pytest-cov, httpx, factory-boy, ruff, mypy, bandit[toml],
  pip-audit. No httpx-based Ollama client, no qdrant-client, no pgvector, no asyncpg, no fastmcp.
- Ruff: line-length 100, target py310, rule set includes `S` (flake8-bandit) and `T20` (no print),
  tests ignore `S101` (pyproject.toml:38-65). Mypy: `strict = true`, excludes tests/.venv
  (pyproject.toml:67-72). Pytest: `asyncio_mode = "auto"`, markers `integration`/`slow`
  (pyproject.toml:77-88). Coverage: branch=true, source=app (pyproject.toml:90-99).
- Test layout: `backend/tests/conftest.py` provides `db_session` (fresh in-memory
  `sqlite+aiosqlite:///:memory:` per test, creates all tables, conftest.py:8-28) and `client`
  (httpx `AsyncClient` + `ASGITransport`, overrides `get_db`, conftest.py:31-44).
- Tests present: `tests/unit/test_note_service.py`, `tests/unit/test_container_service.py`,
  `tests/integration/test_notes_api.py`, `tests/integration/test_containers_api.py`,
  `tests/integration/test_search_api.py`; factories under `tests/factories/`
  (`note_factory.py`, `container_factory.py`). Style: `@pytest.mark.asyncio`, AAA, status-code +
  field assertions (e.g. `test_notes_api.py:5-47`).

## 7. Frontend — structure, stores, api, types, router

- Entry: `frontend/src/main.ts:1-12` (createApp + Pinia + router). Router:
  `frontend/src/router/index.ts:3-34` — routes `dashboard (/)`, `inbox (/inbox)`, `note
  (/notes/:id)`, `container (/containers/:id)`, `search (/search)`, all lazy-imported. No `/chat`
  route exists.
- API client: `frontend/src/api/client.ts`. `const API_BASE = '/api/v1'` (client.ts:14); shared
  `handleResponse<T>` handles 204 and error `detail` (client.ts:16-25). Three grouped objects:
  `notesApi` (client.ts:28-92), `containersApi` (95-137), `searchApi` (140-155, calls `/inbox`,
  `/search?q=`, `/recent?limit=`). Uses native `fetch`; no axios; no streaming/SSE reader.
- Vite dev proxy forwards `/api` → `http://localhost:8000` (frontend/vite.config.ts:13-20). Vitest
  config: globals true, jsdom env (vite.config.ts:21-24). Path alias `@` → `src` (vite.config.ts:8-11).
- Types mirror backend schemas: `frontend/src/types/index.ts:1-95` — `ContainerType`, `CodeStage`,
  `HighlightRange` (`layer: 2 | 3`), `Note`, `NoteCreate/Update/MoveRequest/HighlightsUpdate`,
  `Container`, `ContainerCreate/Update`, `ContainerWithCount`, `ContainerWithNotes`. No chat/message/
  document/source-citation types exist.
- Pinia stores use setup-store style with `ref`/`computed` and `loading`/`error` state:
  `frontend/src/stores/notes.ts:6-221` (actions: fetchNotes/Inbox/Recent/Note, quickCapture,
  updateNote, moveToContainer, updateHighlights, deleteNote, searchNotes; getters inbox/byContainer/
  byStage). `frontend/src/stores/containers.ts:13-186` (getters projects/areas/resources/archives/
  byType/totalNoteCount — archives = `type==='archive' || !is_active`, containers.ts:33-35).
- Views: `Dashboard.vue`, `Inbox.vue`, `NoteView.vue`, `ContainerView.vue`, `SearchView.vue`
  (`frontend/src/views/`). Components include `ParaSidebar.vue`, `NoteCard.vue`, `RichEditor.vue`,
  `EditorToolbar.vue`, `ExecutiveSummary.vue`, `MoveNoteModal.vue`, `CreateContainerModal.vue`,
  `KeyboardShortcutsHelp.vue` (`frontend/src/components/`).

## 8. Frontend — editor & test conventions

- Tiptap editor stack: `frontend/package.json:15-20` (`@tiptap/vue-3`, `@tiptap/starter-kit`,
  `@tiptap/extension-highlight`, all ^3.15.3), plus `pinia ^3`, `vue ^3.5`, `vue-router ^4`.
  Custom highlight extensions: `frontend/src/editor/extensions/L2Highlight.ts`,
  `L3Highlight.ts`, `index.ts` (progressive-summarization L2/L3), tested in
  `frontend/src/editor/extensions/__tests__/highlights.spec.ts`.
- Frontend test tooling: Vitest 4, @vue/test-utils, @testing-library/vue, @pinia/testing, jsdom
  (package.json:22-37). Store tests mock `@/api/client` with `vi.mock` and assert store state
  (e.g. `frontend/src/stores/__tests__/notes.spec.ts:7-45`). Component tests under
  `frontend/src/components/__tests__/`.
- Scripts: `dev`, `build` (`vue-tsc -b && vite build`), `test`/`test:run` (vitest), `lint`
  (`vue-tsc --noEmit`) (package.json:6-13). TailwindCSS 4 present (package.json:32).

## 9. CI / repo governance (facts)

- CI workflows exist: `.github/workflows/ci.yml` and `.github/workflows/security.yml` (contents not
  read in this pass — noted as present).
- Root context files present and populated: `intent.md`, `constraints.md`, `evals.md`, `AGENTS.md`,
  `README.md`, project `CLAUDE.md` (contents not fully read this pass; `CLAUDE.md` documents the
  layered routes→services→repositories intent, `/api/v1` endpoints, `CodeStage`/`ContainerType`
  enums, and progressive-summarization L1–L4 shape).

## 10. Open questions / gaps (facts not found — NOT recommendations)

- CI pipeline gates (`ci.yml`, `security.yml`) were not read; the exact lint/type/test/coverage/
  bandit steps that new code must satisfy are unconfirmed.
- `intent.md`, `constraints.md`, and `evals.md` were not read in full; any must/must-not
  constraints, acceptance-criteria format, or logged decisions they contain are unverified here.
- No `.env`/`.env.example` was located in this pass; the concrete runtime env-var set beyond the
  three `Settings` fields is unconfirmed.
- `highlights` column uses the SQLite-specific `JSON` type (note.py:9,34; migration initial.py:50).
  Its behavior/portability under a non-SQLite backend was not exercised or verified.
- No document raw-file storage directory, no `data/` folder, and no upload-handling code were found
  in the repo (only `python-multipart` is declared as a dep, pyproject.toml:11); current upload
  surface is unconfirmed.
- The referenced external `grounded-code-mcp` engine (its `IngestionPipeline`, `EmbeddingClient`,
  search impl, `pdf2md`/`web2md` tools) lives outside this repo and was not inspected; only
  second-brain was in scope for this mapping.
- Whether the frontend `fetch`/`handleResponse` helper supports a streaming/readable-stream response
  path (needed for streamed chat) was not found — current client reads full JSON bodies
  (client.ts:16-25).
