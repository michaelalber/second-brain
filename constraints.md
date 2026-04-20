# second-brain — Constraints

---

## Must Do

- Load and confirm context (`AGENTS.md`, `intent.md`, `constraints.md`) before every session.
- Write a failing test before any production code — no exceptions (RED → GREEN → REFACTOR).
- Run the full backend quality-check pass before any commit: pytest + ruff + mypy + bandit.
- Sanitize all Tiptap/rich-text editor output before storing to the database.
- Use `async/await` for every database operation — no synchronous SQLAlchemy calls.
- Write three verifiable acceptance criteria before delegating any significant subtask.
- Add a `# VERIFY:` comment rather than guess a function signature, API behavior, or SQLAlchemy idiom.
- Confirm understanding before any destructive migration (column drop, rename, table drop).

---

## Must NOT Do

- Do not write production code without a failing test. RED phase is local only — never committed.
- Do not use synchronous SQLAlchemy anywhere in the application code.
- Do not add a repository layer unless two or more services share identical query logic.
- Do not exceed 15 lines in a route handler — delegate to `services/`.
- Do not reuse a Pydantic schema across semantically different use cases.
- Do not hardcode secrets, tokens, or `DATABASE_URL` values — use environment variables.
- Do not commit `backend/basb.db`, `.env`, `.env.*`, or `__pycache__/`.
- Do not re-litigate decisions logged in the Persistent Decisions tables without surfacing the question first.
- Do not implement AI/LLM features without first resolving the Open Loop on AI augmentation strategy.

---

## Preferences

- Prefer brevity over completeness unless depth is explicitly requested.
- Prefer editing an existing file over creating a new one.
- Prefer `grounded-code-mcp` knowledge base over training data for FastAPI, Vue 3, SQLAlchemy, and Pydantic v2 idioms.
- Prefer a single focused service-layer unit test over a broad integration test when testing business logic.
- Prefer `Mapped[Optional[T]]` with an explicit `None` default over omitting the default for nullable columns.
- Prefer inline `# VERIFY:` annotations over guessing async patterns or SQLAlchemy 2.0 syntax.

---

## Escalate Rather Than Decide

- Any AI/LLM feature — confirm provider, model name, cost, and integration point before implementing.
- Any DB schema migration that drops or renames a column (hard to reverse).
- Any CORS policy change that broadens allowed origins beyond `localhost`.
- Any change that moves business logic out of `services/` (violates the layered architecture decision).
- Any security-relevant decision not explicitly covered by these constraints.

---

## Code Quality Gates

- **Test coverage (backend business logic):** ≥ 80% — `cd backend && .venv/bin/pytest --cov=app --cov-report=term-missing`
- **Test coverage (frontend):** ≥ 70% — `cd frontend && npm run test:run`
- **Test coverage (security-critical paths):** ≥ 95%
- **Cyclomatic complexity (per method):** < 10
- **Code duplication:** ≤ 3%
- **Commit format:** Conventional Commits — `feat:`, `fix:`, `refactor:`, `chore:`, `test:`, `docs:`
- **Commit scope:** Atomic — one logical change per commit; RED phase never committed
