# second-brain — Intent

---

## Agent Architecture

**This project uses:** Coding harness

**Reason:** Solo developer with human review at every step; task-level features and bug fixes do not require autonomous multi-session loops.

---

## Primary Goal

A fully functional AI-augmented personal KMS: the user captures raw notes, organizes them into the PARA taxonomy, and progressively distills them from L1 raw text to L4 executive summary — with AI assistance accelerating the distill and express stages of the CODE workflow.

---

## Values (What We Optimize For)

1. **Correctness** — code accurately implements BASB semantics; no data loss or corruption
2. **Security** — user content is sanitized, stored safely, and never leaked
3. **Maintainability** — readable, tested code a solo developer can return to after weeks away
4. **Performance** — async throughout; UI responses feel immediate
5. **Speed of delivery** — last priority; correctness is never sacrificed for pace

---

## Tradeoff Rules

| Conflict | Resolution |
|---|---|
| Speed vs. correctness | Default to correctness. Flag explicitly if timeline requires compromise. |
| Completeness vs. brevity | Prefer brevity unless depth is explicitly requested. |
| New abstraction vs. duplication | Tolerate duplication until the third occurrence; then extract. |
| AI feature richness vs. scope creep | Confirm AI integration points before implementing; see Open Loops in AGENTS.md. |

---

## Decision Boundaries

### Decide Autonomously

- Formatting, structure, naming within established project conventions
- Tool selection for read-only exploration
- Refactoring within an approved, scoped task
- Choosing between two equivalent async SQLAlchemy patterns
- Adding a test for an untested code path discovered during a task

### Escalate to Human

- Any AI feature that touches external APIs — confirm provider, model name, and cost before implementing
- Any DB schema migration that drops or renames a column
- Any CORS policy change that broadens allowed origins beyond `localhost`
- Any change that moves business logic out of `services/` and into routes or models
- Any output intended for external distribution
- Any irreversible action (delete, force-push, send)
- Scope changes beyond the stated task
- When acceptance criteria cannot be met within stated constraints

---

## What "Good" Looks Like

A good output for this project:

- Implements the BASB concept correctly (not just the literal endpoint spec) — e.g., a "move" operation correctly advances the `code_stage`
- Produces working, tested code on the first attempt within the defined scope
- Stays thin at the route layer and puts logic in services — verifiable by line count
- Uses the domain vocabulary (`CodeStage`, `ContainerType`, `highlights`) consistently
- Flags risks (schema changes, async pitfalls, highlight offset drift) proactively

---

## Anti-Patterns (What Bad Looks Like)

- Implementing the literal request while missing the BASB intent (e.g., moving a note to a container without updating `code_stage`)
- Adding a repository layer or other abstraction "for future flexibility" — YAGNI
- Synchronous SQLAlchemy calls that block the event loop
- Reusing a Pydantic schema across semantically different operations to save lines
- Recommending an AI feature without surfacing the provider/cost/integration question first

---

## Persistent Decisions

| Date | Decision | Rationale |
|---|---|---|
| [VERIFY: date] | L4 executive summary is always user-authored | AI may suggest, but the user's own words are the point of the express stage |
| [VERIFY: date] | Inbox = notes with no `container_id` | Simple; avoids a separate inbox table |
