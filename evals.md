# second-brain — Evals

---

## Eval Philosophy

Evals are safety infrastructure, not a finishing step. Write them before the agent starts.
A passing test suite ≠ done; tests verify code correctness, evals verify output is actually
good relative to BASB intent.

A passing eval is measurable, repeatable, and would survive scrutiny from a developer who
understands Tiago Forte's BASB methodology and expects the domain semantics to be respected.

---

## Test Cases

### Test Case 1: Note Capture and PARA Move

- **Input / Prompt:** "Implement the endpoint to move a note to a PARA container and advance its CODE stage."
- **Known-Good Output:** `PATCH /api/v1/notes/{id}/move` sets `container_id` on the note AND advances `code_stage` from `capture` to `organize`. Route handler ≤15 lines. Business logic in `note_service.py`. Integration test covers happy path and 404 on missing note.
- **Pass Criteria:**
  - [ ] `code_stage` transitions from `capture` → `organize` on move (BASB semantic — not just a field update)
  - [ ] `container_id` is set to the target container
  - [ ] Route handler is ≤15 lines; logic is in `services/note_service.py`
  - [ ] Integration test in `tests/integration/test_notes_api.py` covers: success (200), missing note (404), missing container (404)
  - [ ] `pytest` passes with coverage ≥ 80%
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 2: Progressive Summarization Highlight Update

- **Input / Prompt:** "Implement `PATCH /api/v1/notes/{id}/highlights` to update L2/L3 highlight ranges."
- **Known-Good Output:** Endpoint accepts `{"highlights": [{"start": int, "end": int, "layer": 2|3}]}`. Validates layer is 2 or 3 only. Replaces the full highlight list (not appends). Service validates that ranges don't exceed content length. Unit test in `tests/unit/` covers validation; integration test covers the HTTP contract.
- **Pass Criteria:**
  - [ ] Layer values other than 2 or 3 return 422 (Pydantic validation, not a manual check)
  - [ ] L4 (executive summary) is NOT updated by this endpoint — separate field/endpoint
  - [ ] Highlight ranges are replaced atomically (not merged with existing)
  - [ ] Service-layer unit test covers: valid payload, invalid layer, empty list (clears all)
  - [ ] `pytest` passes; no ruff or mypy errors introduced
- **Last Run:** — | **Result:** —
- **Notes:** Highlight offset drift (content edited after highlights set) is a known open issue — not in scope here.

---

### Test Case 3: Full-Text Search

- **Input / Prompt:** "Implement `GET /api/v1/search?q=` for full-text search across note titles and content."
- **Known-Good Output:** Returns notes where title OR content contains the query string (case-insensitive). Empty `q` returns 422. Results include `code_stage` and `container_id`. Implemented in `search_service.py`. Integration test covers: match in title, match in content, no match, empty query.
- **Pass Criteria:**
  - [ ] Search is case-insensitive
  - [ ] Empty `q` returns 422 (not an empty list)
  - [ ] Response schema includes `code_stage` and `container_id` for each result
  - [ ] Logic is in `search_service.py`, not in the route handler
  - [ ] Integration tests cover all four cases above
- **Last Run:** — | **Result:** —
- **Notes:** SQLite `LIKE` is acceptable for now; defer FTS5 until the Open Loop on deployment target is resolved.

---

## Taste Rules (Encoded Rejections)

| # | Pattern to Reject | Why It Fails | Rule |
|---|---|---|---|
| 1 | Moving a note to a container without updating `code_stage` | Technically correct HTTP but wrong BASB semantics — capture stays capture forever | A move operation MUST advance `code_stage` to `organize` |
| 2 | Putting query logic directly in route handlers | Defeats the layered architecture; untestable in isolation | All DB access goes through `services/`; routes call services only |
| 3 | Reusing `NoteResponse` schema as the input schema for update | Semantically wrong; leaks read-only fields into writes | One schema per use case: `CreateNote`, `UpdateNote`, `NoteResponse` are all distinct |
| 4 | AI feature implemented without surfacing provider/cost question | Binds the project to an unconfirmed external dependency | Escalate AI integration to human before writing any model call code |

---

## CI Gate

The agent must not declare a task complete if any gate below fails.

- **Backend tests:** `cd backend && .venv/bin/pytest -v --cov=app --cov-report=term-missing` — all pass, coverage ≥ 80%
- **Backend lint:** `.venv/bin/ruff check app/ tests/` — zero errors
- **Backend format:** `.venv/bin/ruff format --check app/ tests/` — clean
- **Backend types:** `.venv/bin/mypy app/` — zero errors
- **Backend security:** `.venv/bin/bandit -r app/ -c pyproject.toml` — zero high/critical
- **Dependency audit:** `.venv/bin/pip-audit --skip-editable` — zero known vulnerabilities
- **Frontend tests:** `cd frontend && npm run test:run` — all pass
- **Frontend build:** `npm run build` — zero errors

---

## Rejection Log

*(Append entries here as outputs are rejected. Never delete entries.)*
