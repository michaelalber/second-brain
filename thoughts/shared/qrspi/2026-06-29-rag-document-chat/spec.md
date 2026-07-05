---
date: 2026-07-03T00:00:00
repository: second-brain
topic: "RAG document chat — federated notes+documents retrieval, /chat surface, second-brain MCP"
tags: [qrspi, spec, rag, mcp, pgvector, qdrant, ollama]
git_commit: 8443bfe
phase: Spec (S)
qrspi_feature: rag-document-chat
research_artifact: thoughts/shared/qrspi/2026-06-29-rag-document-chat/research.md
design_approved: true         # approved 2026-07-04 (rev4); Movement 2 written
status: approved              # approved 2026-07-05 (rev6, post-review); ready for /qrspi-plan
brain_dump_revision: 5        # rev1: Testing & Evaluation Strategy; rev2: adopt VSA via strangler fig (slice zero = this feature); rev3: reconcile with confirmed grounded engine API (research-grounded-engine-api.md); rev4: product positioning (engine/app/MCP layers), Qdrant server-mode substrate, decision 9 resolved to Option C (grounded extras); rev5: review-driven accuracy fixes — Option C merged+pinned (91021cae), [parse] extra name, chunk-count correction, shared-notes/highlights/deps gaps added to Risks; rev6: decision 10 — resolve gaps #1/#2 by standardizing the whole test base on Postgres+pgvector (retire in-memory SQLite)
research_addendum: thoughts/shared/qrspi/2026-06-29-rag-document-chat/research-grounded-engine-api.md
---

# Spec: rag-document-chat

## Movement 1 — Design Brain-Dump  (source stage 3)

<!-- ~200 lines. Written first; revised in the brain-surgery loop until the human approves.
     Present this and STOP before writing Movement 2. -->

### Current state

second-brain today is a complete-but-purely-CRUD BASB app. The backend is layered
routes → services, with services holding SQLAlchemy queries directly (there is no repository
layer, confirmed across all three services — `research.md` §4). Data lives in three models:
`Note` (`backend/app/models/note.py:27-51`), `Container` (self-referential PARA hierarchy,
`backend/app/models/container.py:24-45`), and `Tag` + a `note_tags` M2M table
(`backend/app/models/tag.py:16-32`). Notes carry `code_stage`, `highlights` (SQLite-dialect JSON,
`note.py:9,34`), `executive_summary`, `source_url`, and `container_id`. Critically, there is **no
embedding column, no provenance columns (`derived_from`/`derivation_layer`/`supersedes`), and no
document/chunk/conversation tables anywhere** (`research.md` §1, §0).

Persistence is async SQLAlchemy 2.0: an `AsyncEngine` + sessionmaker + `get_db()` commit-on-success
dependency (`backend/app/database.py:8-31`), aliased as `DbSession` (`backend/app/api/deps.py:8`).
Config is a Pydantic-settings `Settings` with only three fields — `DATABASE_URL` (defaulting to
`sqlite+aiosqlite:///./basb.db`), `DEBUG`, `CORS_ORIGINS` (`backend/app/config.py:4-16`). There are
**no Ollama/Qdrant/embedding/feature-flag settings** (`research.md` §2). The app factory mounts one
router at `/api/v1` and applies CORS with `allow_methods=["*"]`, `allow_headers=["*"]`
(`backend/app/main.py:18-33`); `lifespan` is a no-op stub (`main.py:11-16`).

Routes are thin (≤5 lines) and delegate to inline-constructed services
(`backend/app/api/v1/notes.py:19-79`). "Search" today is **substring `.ilike` matching**, not
semantic — both `NoteService.list_notes` (`note_service.py:44`) and `SearchService.search_notes`
(`search_service.py:21-28`). Schemas follow one-per-use-case (`backend/app/schemas/note.py`), return
ORM objects via `response_model` + `from_attributes`. A single Alembic migration exists
(`6a9f679dbc20_initial_models.py`), and `env.py` runs async autogenerate but only sees models
imported into it (`env.py:11`). Dependencies are lean: **no qdrant-client, no pgvector, no asyncpg,
no fastmcp, no httpx-Ollama client** (`research.md` §6).

The frontend is Vue 3 setup-store style. Router has `dashboard/inbox/note/container/search` routes
and **no `/chat` route** (`frontend/src/router/index.ts:3-34`). The API client uses native `fetch`
with a shared `handleResponse<T>` that reads **full JSON bodies** — there is no streaming/readable-
stream path today (`frontend/src/api/client.ts:16-25`). Types mirror backend schemas with **no
chat/message/document/citation types** (`frontend/src/types/index.ts:1-95`). Vite proxies `/api` →
`localhost:8000` (`vite.config.ts:13-20`). The external `grounded-code-mcp` engine lives outside
this repo and has now been **read and confirmed** (`research-grounded-engine-api.md`): its reusable
surface is four flat, cleanly-importable modules — `DocumentParser` (`parser.py`), `DocumentChunker`
(`chunking.py`), `EmbeddingClient` (`embeddings.py`), `QdrantStore` (`vectorstore.py`) — with **no
import-time global state** and **no MCP-server coupling** (the FastMCP singletons live only in
`server.py`). It is a dependency we drive as a library, not code we own.

### Desired end state

"Done" for the MVP skeleton is: a user can ingest documents into a shared Qdrant library, chat
against a **PARA-container-scoped** bundle of their own notes + documents, see **source citations**,
and optionally **save a chat answer back as a note that remembers its evidence** — all strictly
local via Ollama, and all gracefully degrading to plain BASB when Ollama is off.

Concretely (tied to the answered questions):

- **Two federated stores, one query.** Documents/ebooks live as chunks+vectors in the shared Qdrant
  collection `brain_documents` (grounded's engine, reused as a library — Q3.1, Q13.1). Notes get an
  **embedding column on the note row** in Postgres+pgvector (Q3.1, Q12). second-brain's own logic
  federates one query across both stores and **merges by score**, which only works because both use
  the **same embedding model + distance metric**: `snowflake-arctic-embed2`, 1024-dim, cosine (Q4.2).
- **PARA-native retrieval (P1).** Container-scoped chat is the *primary* mode; whole-corpus search is
  the fallback. Archives excluded by default; rank Projects > Areas > Resources (Q6.2).
- **Documents as first-class PARA resources** filed in a *single* most-actionable container; moving
  containers is a reference update, **never a re-embed** (Q2.4, Q6.1, P2).
- **Provenance is first-class (P3):** notes gain `derived_from` / `derivation_layer` / `supersedes`
  as denormalized columns. Saving a chat answer as a note sets `derivation_layer='derived'` and
  `derived_from=[cited ids]` (Q6.3).
- **A `/chat` route** in the Vue app, container-selectable, **streaming** the answer over HTTP chunked
  `StreamingResponse` (no `EventSource`/SSE — Q8.2), with **persisted** conversation history (Q7.2)
  and rendered citations (Q7.3).
- **New endpoints under `/api/v1`:** `/api/v1/documents` and `/api/v1/chat` (Q8.1).
- **A separate second-brain MCP server** (own entry point, shared code+DB — Q11.3) exposing a
  read/search tool surface — `search_my_notes`, `search_my_library`, `chat_my_brain`,
  `get_document_info`, `list_containers` (Q11.1) — over **Streamable HTTP + stdio**, bound to
  `127.0.0.1`/LAN only (Q11.2), reachable by Goose/Claude Code and Open WebUI via `mcpo`.
- **Feature-flagged and degrade-safe:** the whole AI surface is opt-in via an env var; with Ollama
  down, notes/documents still list and chat shows a clear disabled banner (Q4.3, Q10.1, Q10.2).
- **Dev commits to Postgres+pgvector** via a Docker Compose service (Q3.4, Q10.3); Ollama and Qdrant
  stay remote on the Mac Mini (`192.168.42.165:11434`).
- **"Done" is eval-gated, not just green-suite.** Each slice ships test-first (Red-Green-Refactor);
  the *feature* is complete only when the `evals.md` RAG eval set — retrieval relevance,
  groundedness/citation correctness, prompt-injection resistance, PARA-scope isolation — passes.
  Acceptance criteria are written **before** Movement 2 (design decision 8).
- **The feature lands as a self-contained vertical slice.** All new code lives under
  `backend/app/features/rag_document_chat/` (router, schemas, service, feature models, migration,
  co-located tests), wired into `main.py` by one explicit `include_router`. The shared kernel
  (`main.py`, `database.py`, `config.py`, `Note`/`Container`/`Tag`) is unchanged except for that
  include line and the additive `Settings` fields; the legacy notes/containers/tags layers are
  **untouched** (design decision 3). This is the first slice of a strangler-fig migration to VSA.
- **The project `CLAUDE.md` architecture rule is amended** from "layered … not vertical slice" to a
  VSA-for-new-features rule with a shared kernel and opportunistic legacy migration — a deliverable of
  this feature, done by the main agent so the logged project decision and this spec agree.

### Product positioning & project boundaries

second-brain is **not** a superset that swallows grounded-code-mcp. The two are *sibling
applications* standing on a *shared RAG engine*, in three layers:

- **Layer 0 — the RAG engine (shared library).** The four confirmed primitives
  (`DocumentParser` / `DocumentChunker` / `EmbeddingClient` / `QdrantStore`). Lives in grounded's
  repo today; reused by second-brain via direct import (decision 1). Infrastructure, not product.
- **Layer 1 — two sibling products on that engine.** *grounded-code-mcp* stays a **standalone,
  narrow coding-agent MCP** (code indexing, code-aware chunking, its `graph`/networkx code-graph,
  serving a coding agent) — a legitimate product for users who want exactly that and no more.
  *second-brain* is the **broad personal-knowledge product** (PARA + notes in pgvector + documents
  in Qdrant + chat + provenance). Forcing PARA/chat/provenance into grounded would be the
  wrong-abstraction trap (`patterns/metz-the-wrong-abstraction.md`); the two share a foundation,
  they do not merge. second-brain is a superset of *capabilities* (it absorbs the retired local-rag's
  role and adds chat/PARA/provenance) but is built by **sharing grounded's engine, not containing
  grounded's app.**
- **Layer 2 — second-brain's own MCP surface.** By exposing `search_my_notes` / `search_my_library`
  / `chat_my_brain` / `list_containers`, second-brain becomes a **knowledge/memory backend that
  other agents are clients of** — the "knowledge core of an AI coding agent / chatbot / AI memory"
  role. A coding agent can wire up *both* MCPs: grounded's for code, second-brain's for durable
  cross-project knowledge. They compose, they do not compete.

**North star vs MVP (YAGNI guard):** "knowledge core for any AI agent" is the project's north star,
but this feature builds only the **read/search** MCP surface. The write path (`remember`), per-agent
identity, multi-tenant RLS, and memory governance stay **deferred** (§14, P8) — the grand framing
must not pull deferred work forward.

### Design decisions & tradeoffs

1. **Reuse grounded-code-mcp as a library for documents; own the notes store directly (DRY).**
   We reuse grounded's **Layer-0 engine** (the four primitives), **not** its Layer-1 coding-agent
   product — importing the engine modules directly, never driving grounded over MCP (see product
   positioning above). We compose grounded's confirmed primitives — `DocumentParser().parse(path) -> ParsedDocument`,
   `DocumentChunker().chunk(content) -> list[Chunk]`, `EmbeddingClient(...).embed_many(...)`, and
   `QdrantStore(url=...).create_collection/add_chunks/search` (`research-grounded-engine-api.md`,
   Areas 1-4) — rather than re-implement chunking, Docling, or Qdrant wiring (Q13.1). Research
   corrected an assumption: there are **no `pdf2md`/`web2md` importable symbols** — parsing is
   `DocumentParser.parse()` (Docling for binary formats, direct read for plaintext), so we drive that
   class, not a converter function. We take the **primitive-composition path** (not the high-level
   `IngestionPipeline`/`ingest_documents`), which deliberately avoids grounded's `Manifest` file and
   its `graph` package coupling (`ingest.py` force-path). We do **not** extract a neutral `rag-core`
   yet — rule of three; revisit only if the coupling bites (Q1.2, Q13.1).

   **Engine integration constraints (correctness, not optional — from `research-grounded-engine-api.md`):**
   - **The engine is fully synchronous** (no `async def` anywhere in the four modules). second-brain is
     async FastAPI/SQLAlchemy, so **every** engine call (parse / embed / search) MUST be offloaded via
     `asyncio.to_thread` (or a thread-pool executor). Calling them directly on the request path would
     block the event loop — this is a defect, not a style choice.
   - **Query/document embedding asymmetry:** `EmbeddingClient.embed(text, is_query=True)` prepends a
     literal `"query: "` prefix; **documents are embedded WITHOUT it, queries WITH it** (`embeddings.py:204,257`).
     Omitting this silently degrades retrieval. This convention is load-bearing and applies to **both
     stores** — the pgvector note-embedding path must replicate the same prefix rule so note and
     document scores federate on the same footing (reinforces decision 2).
   - **Non-deterministic point IDs:** `generate_chunk_id` returns a random `uuid4` and ignores
     source_path/index (`chunking.py:44-61`), so re-ingesting a document yields new IDs. Idempotent
     re-ingest therefore requires **delete-then-insert keyed on our own stable identifier** — we store
     `document_id`/`source_path` in the Qdrant payload and delete a document's prior points before
     re-adding, rather than relying on stable chunk IDs (see ingestion decision 7).

2. **Split stores by data shape, not one-store-for-all.** A document *is* its vector; a note's vector
   is just one facet of a relational row that also carries provenance, lineage, and metadata (P3).
   Provenance/synthesis queries (`trace_provenance`, `find_derivatives`) are native in Postgres and
   impossible in Qdrant. Tradeoff: two stores to keep consistent — mitigated by pinning the **same
   embedding model + metric** so scores federate (Q3.2, Q4.2).

   **Qdrant runs in server mode (`url=`), not embedded — and this settles Qdrant-vs-Chroma.** Three
   processes — grounded's MCP, second-brain's API, and Open WebUI (via `mcpo`) — must hit the same
   `brain_documents` collection **concurrently**. Embedded Qdrant (`path=`) holds a single-process
   storage lock (`research-grounded-engine-api.md`, Area 4), and Chroma's embedded mode has the same
   single-writer limit; a **shared running Qdrant server** is the only option among the three that
   supports genuine multi-process access. Its payload filtering is also what PARA-scope isolation
   (decision 8 eval) relies on. So Chroma loses here on the **sharing requirement**, not on quality —
   at this corpus size (~9.4K documents ≈ hundreds-of-thousands to low-millions of chunks) both are
   more than adequate — Qdrant handles millions; re-verify vector-storage sizing against the real
   chunk count.

3. **Adopt Vertical Slice Architecture via strangler fig; rag-document-chat is slice zero.** We are
   changing direction from the project's current layered convention (`research.md` §4) to VSA
   (Bogard, `patterns/bogard-vertical-slice-architecture.md`) — but incrementally, not big-bang, per
   the Strangler Fig pattern (`patterns/msft-cloud-strangler-fig.md`). The rules:
   - **This feature is the first slice.** rag-document-chat lands as `backend/app/features/rag_document_chat/`
     — the first `app/features/<feature>/` module. **Nothing existing moves now:** notes, containers,
     and tags keep their current layered layout. We prove VSA end-to-end on new code before touching
     anything that already works (YAGNI + risk control; no speculative reorg).
   - **Shared kernel stays central (DRY).** `main.py` app factory, `database.py` engine/`DbSession`,
     `config.py` `Settings`, and the cross-cutting models `Note`, `Container`, `Tag` remain shared.
     The feature **references** these (provenance FK `note_id`, PARA scoping via `Container`) but does
     **not** own them — the FK crosses the boundary; ownership does not. Avoids the "wrong abstraction"
     trap of forcing shared entities into one feature (`patterns/metz-the-wrong-abstraction.md`).
     Note the two *distinct* shared foundations: this **internal** shared kernel (second-brain's own
     cross-cutting code) versus the **external** Layer-0 RAG engine imported from grounded (product
     positioning above). The feature slice consumes both without owning either.
   - **Feature-owned lives in the slice.** `router.py`, `schemas.py`, `service.py`, feature-specific
     tables/models (document / chunk-ref / conversation / message rows and the note-embedding wiring),
     the feature's Alembic migration, and **co-located tests** (`features/rag_document_chat/tests/`).
     Domain logic (ingestion dispatch, federated merge/ranking, PARA scoping) evolves per-slice.
   - **One integration point: the app factory.** The feature exposes a router that `main.py` explicitly
     `include_router`s. **No plugin/auto-discovery mechanism** (YAGNI) — a single explicit include line.
   - **Legacy migrates opportunistically, never now.** Boy-scout / rule-of-three: when a legacy module
     (notes/containers) is next *substantially* touched, lift it into its own slice as an atomic,
     tested commit. Not in this feature's scope. The two architectures coexist by design until then.

   **This decision amends the project convention**, so the project `CLAUDE.md` architecture rule must
   change too (see the "CLAUDE.md amendment" deliverable below) — otherwise the logged decision
   ("layered … not vertical slice") contradicts this spec.

4. **Postgres+pgvector for dev, not just prod.** SQLite has no vector search, so the note embedding
   column forces Postgres locally (Q3.4). Provenance columns are DB-agnostic and would work in SQLite,
   but the embedding column does not. Tradeoff: dev now needs a Compose Postgres service; the test
   suite also moves to Postgres (**decision 10** — retire in-memory SQLite, session-scoped
   Testcontainers), which resolves both the fixture reconciliation and the `highlights` `sqlite.JSON`
   portability problem (`note.py:9,34`) in one move.

5. **Stream chat over HTTP chunked `StreamingResponse`, not SSE.** Consistent with the Streamable-HTTP
   MCP transport choice (Q8.2, Q11.2). The current `fetch`/`handleResponse` client reads full JSON
   bodies (`client.ts:16-25`), so the frontend needs a **new readable-stream reader path** — additive,
   not a rewrite of the existing helper.

6. **MCP server as a separate entry point sharing code+DB (like grounded's `serve`).** Independently
   launchable so the FastAPI app and the MCP surface fail independently (Q11.3). Tradeoff: two process
   entry points to run; justified because Open WebUI/agents consume MCP while humans use the web app.

7. **Ingestion is an out-of-band batch job, sequential, dedup-on.** Hundreds of books → drive
   `DocumentParser.parse(path)` (Docling handles binary formats internally; it prefers a pre-converted
   `<name>.md` sidecar when present) then `DocumentChunker.chunk()` — **one chunking strategy, no
   pre-chunking** (Q5.3, Q5.4). Sequential to avoid OOM; runs off the request path in a worker thread
   (per the sync-offload constraint in decision 1). Two research-driven corrections:
   - **We own dedup (not grounded's `Manifest`).** Content-hash dedup lives only in grounded's
     `Manifest`/`IngestionPipeline` layer, which couples to a manifest file and the `graph` package
     (`research-grounded-engine-api.md`, Area 1). Since our YAGNI cut is **level-1 content-hash dedup
     only**, second-brain computes its **own SHA-256 on upload** and skips re-embedding a matching
     hash — trivial, and it keeps us on the clean primitive-composition path (Q2.1, P6).
   - **Idempotent re-ingest via delete-then-insert.** Because grounded's point IDs are random uuid4
     (non-deterministic), re-ingesting a document must first delete its prior Qdrant points (matched on
     our `document_id`/`source_path` payload field) before adding the new ones — we never rely on
     stable chunk IDs (decision 1).
   Tradeoff: an overnight run; acceptable, and not on the request path.

8. **Two-tier Testing & Evaluation Strategy — both first-class; neither optional.** A RAG feature
   fails in two distinct ways: the *code* can be wrong (a parser mis-dispatches, a scope filter
   leaks, a query concatenates SQL) and the *output* can be bad even when every test is green (the
   retriever returns irrelevant chunks, the model hallucinates past its evidence, an injected
   document hijacks the prompt). Unit tests catch the first; evals catch the second. We build both,
   and — per global rule — **a passing test suite is not "done"; evals verify the output is actually
   good relative to intent.**

   **Tier 1 — Unit/integration tests, strict Red-Green-Refactor (mandatory).** Every vertical slice
   in Movement 2 is failing-test-first; green is the minimum code to pass; refactor only on green.
   We target the *deterministic* surfaces so tests stay fast and repeatable:
   - **Ingestion:** parser dispatch by type, magic-byte validation (accept/reject), content-hash
     dedup (identical ebook ingested twice → one embed).
   - **Chunking boundaries** at the seams we own (grounded does the chunking; we test our dispatch
     into it, not grounded's internals — DRY).
   - **Embedding adapter:** the Ollama call is **mocked and deterministic — no network in unit
     tests** (a fixed fake vector), so tests never depend on the Mac Mini being up.
   - **Store adapters:** notes pgvector column + Qdrant `brain_documents`, asserting **parameterized
     queries only** (a security-regression test, not just correctness).
   - **Federated merge/ranking:** given two scored result sets, the merge order is correct and
     stable.
   - **PARA scoping:** Archives excluded by default; Projects > Areas > Resources ordering; a
     container-scoped query **must not return** another container's rows.
   - **Streaming route contract:** chunked `StreamingResponse` shape and terminal framing.
   - **Chat-answer→note sanitation** and **upload-allowlist rejection** (both security-critical →
     ≥95% coverage per global gates).

     Fixture consequence (RESOLVED — see decision 10): the shared `Note` table now carries
     `Vector(1024)` + JSONB, which SQLite cannot build, so the **entire suite standardizes on an
     ephemeral Postgres+pgvector** backing — a **session-scoped Testcontainers Postgres** (pgvector
     image) with **per-test transaction rollback** for isolation and speed. The in-memory SQLite
     fixture (`conftest.py:8-28`) is **retired**: dev, test, and prod are all Postgres (full parity),
     which also dissolves the `highlights` dialect problem and the whole class of SQLite-vs-Postgres
     drift. Cost (logged): every run needs Docker+Postgres and a slightly slower cold start — bounded
     by one container per session + txn-per-test.

     **Test location follows the slice (decision 3):** these tests are **co-located** under
     `backend/app/features/rag_document_chat/tests/`, not scattered into the top-level `tests/unit`
     and `tests/integration` trees — integration-tests-per-slice is exactly VSA's test approach
     (`patterns/bogard-vertical-slice-architecture.md`). The shared `conftest.py` fixtures are still
     reused (DRY); the slice adds its own Postgres/pgvector fixtures locally.

     **Alignment:** QRSPI vertical *delivery* slices now map **1:1 onto VSA *folders***. Each
     Movement-2 checkpoint is one end-to-end slice (mock-API → front-end → DB) landing inside
     `features/rag_document_chat/` — the delivery discipline and the code layout finally agree,
     instead of a vertical delivery cutting across horizontal layer folders.

   **Tier 2 — Data/RAG evals as safety infrastructure, seeded in `evals.md` BEFORE Movement 2.**
   These are the feature's **acceptance criteria written before implementation** — if we can't write
   them, we don't understand the feature well enough to build it. A small, curated, **labeled**
   dataset (a handful of Q → expected-chunk / expected-answer rows over a fixed sample corpus),
   runnable in CI, scoring four axes:
   - **Retrieval relevance** — recall@k / precision@k against the labeled Q→expected-chunk set.
   - **Answer groundedness / faithfulness** — the answer asserts nothing beyond the retrieved
     evidence (no hallucination), and **citations point at chunks that actually support the claim.**
   - **Prompt-injection resistance (security eval, not a unit test)** — documents containing
     "ignore previous instructions…" must be treated as **evidence, not instructions** (the P5
     evidence-not-instructions guardrail). This is behavioral, so it lives in evals.
   - **PARA-scope correctness (security eval)** — a container-scoped chat **must not leak** content
     from another container; scope isolation is an authorization property, verified as an eval.

   Evals double as the definition of done: the feature cannot be declared complete until the eval
   set passes, and evals re-run after any prompt/model change.

9. **Grounded engine packaging — Option C DONE (grounded PR #1 merged; pin `91021cae`).**
   grounded-code-mcp is **not on PyPI** (git/pipx only), is **MIT** (no legal blocker), and pins
   **heavy transitive deps** in core — docling, chromadb, fastmcp, networkx — though only `ollama` +
   `qdrant-client` import eagerly; Docling/Chroma load lazily (`research-grounded-engine-api.md`,
   Blockers). Because the author **owns** grounded and the engine is now the **shared Layer-0
   foundation for a family of apps** (product positioning above), the packaging choice changes:
   - **Vendoring the modules (the old fallback) is rejected** — it forks the engine and destroys the
     one-shared-core story; with two+ consumers the DRY cost is now unacceptable.
   - **A plain git dep on the current package works but drags in** docling/chromadb/fastmcp/networkx
     even when unused (import-time stays light, but the venv is heavy).
   - **(Chosen) Option C — restructure grounded's `pyproject.toml`:** move `docling` / `chromadb` /
     `fastmcp` / `networkx` into **optional-dependency extras**, leaving the engine core
     (`parser`/`chunking`/`embeddings`/`vectorstore`/`config`) needing only `ollama` + `qdrant-client`.
     second-brain then takes a **git dependency on the light core**; `grounded-code-mcp[parse]` is
     pulled only on the ingest box that actually parses binaries. Preserves DRY (single authoritative source)
     **and** a light install — the win neither vendoring nor a heavy git dep could give.
   - **Retire `ChromaStore` from grounded's core** (→ optional `[chroma]` extra, or drop it): once the
     ecosystem standardizes on a **shared Qdrant server** (decision 2), Chroma is dead weight in core.
   **DONE 2026-07-04:** grounded PR #1 merged into `main`
   (`91021cae2e300378032471bfc63059a45cb3fb65`); extras are `parse`/`serve`/`graph`/`chroma`/`all`,
   `ChromaStore` kept behind `[chroma]`, 518 tests green. second-brain pins that commit (see the
   Plan-phase prerequisite section). **Rule-of-three watch:** when a *third* engine consumer appears,
   extract the four primitives into a standalone `rag-core` package and have all apps depend on it.

10. **Test base standardizes on Postgres+pgvector; retire in-memory SQLite (resolves review gaps #1/#2).**
    Adding `Vector(1024)` + JSONB to the shared `Note` makes the in-memory SQLite fixture
    (`conftest.py:8-28`) unbuildable, and `highlights` (`sqlite.JSON`) is already Postgres-incompatible.
    Rather than maintain dialect-variant column types and two fixtures forever, the **whole test suite
    moves to an ephemeral Postgres+pgvector backing** — a **session-scoped Testcontainers Postgres
    (pgvector image)** with **per-test transaction rollback** for isolation/speed. Consequences:
    - **Schema is native, no variants:** `highlights → JSONB` (a type change to an existing column —
      NOT purely additive), `embedding → Vector(1024)`, provenance `derived_from → JSONB`.
    - **Dev = test = prod = Postgres** (full parity) — exactly the DIP guidance that Testcontainers /
      real-DB testing obsoletes faking; eliminates the SQLite-vs-Postgres drift class the `highlights`
      bug is a symptom of.
    - **Migration is mechanical:** rewrite `conftest.py`'s `db_session`/`client` fixtures onto the
      container; legacy notes/containers/tags test *assertions* are unchanged — only their DB backing.
    - **Tradeoff (logged):** every test run needs Docker + a Postgres container; cold start is slower
      than in-memory SQLite, bounded by one container per session + transaction-per-test rollback so the
      inner loop stays fast. This **reverses the project's current SQLite-test convention** — a
      deliberate, logged change; the parity/boy-scout win outweighs the SQLite speed.

**YAGNI — deliberately NOT building now:**
- **No GraphRAG / knowledge-graph layer** (P9) — layer on post-MVP once there's interlinked content.
- **No write/capture MCP tool (`remember`)** (P8) — read/search surface only until agent-memory
  governance ships.
- **No agent-memory governance sidecars, per-agent identity, evidence-merge reconciliation, or
  multi-user RLS** (§14 "Deferred").
- **No URL/web-page ingestion, XLSX, or image-OCR** at launch — phase 2 (Q5.1, Q5.2).
- **No manual document-set chat scope, no embedded-in-note chat** — phase 2 (Q6.2, Q7.1).
- **No smart-ingest reconciliation machinery** (`append_evidence`/`create_revision`) — level-1
  content-hash dedup only (P6).
- **No per-topic Qdrant collections** — one `brain_documents` collection, payload-filtered (Q3.3).
- **No background embedding pipeline beyond the large-note fallback** — embed on-save for typical
  notes (Q12.1).
- **No heavyweight eval infrastructure.** The eval harness is a lean, labeled dataset + assertions
  runnable in CI — **not** a full LangSmith production deployment, eval dashboards, tracing backend,
  or A/B experiment infra (LangSmith is a reference for eval *design*, not a build target unless it
  is already the substrate). Grow it only when the small set stops catching regressions.

**DRY — what we reuse rather than rebuild:**
- grounded-code-mcp's document RAG engine — the confirmed `DocumentParser` / `DocumentChunker` /
  `EmbeddingClient` / `QdrantStore` primitives (ingestion, chunking, Docling, Qdrant search) — as a
  dependency (Q13.1, `research-grounded-engine-api.md`).
- grounded's Docling-backed `DocumentParser` for binary→text conversion instead of a new converter
  (corrects the earlier `pdf2md`/`web2md` assumption — those symbols do not exist) (Q5.4).
- The existing thin-route → service delegation style, the shared-kernel `DbSession` dependency,
  one-schema-per-use-case, and `response_model`/`from_attributes` serialization (`research.md` §2-4).
  VSA changes *where* this code lives (inside the slice), not *how* a request flows — routes stay thin
  and delegate to the feature's service; the shared kernel is reused, not duplicated per slice.
- One embedding model + metric across both stores (Q4.2) rather than per-store choices.
- The shared Mac Mini Ollama + central Qdrant substrate — grounded and second-brain point at the
  same instances (Q13.2).

**Security-by-Design (OWASP):**
- **Input validation at boundaries:** Pydantic v2 schemas for every new `/documents` and `/chat`
  request; file-upload validation is an **allowlist + magic-byte check per accepted type** — grounded's
  current allowlist is `.pdf/.epub/.md/.txt/.rst/.html`, so DOCX/PPTX/(XLSX) must expand the validated
  allowlist and add magic-byte checks before those parsers are enabled (Q5.1). Each new parser is new
  attack surface.
- **Raw files outside the web root:** documents stored under `second-brain/data/documents/`, never
  served statically (Q2.2).
- **Prompt-injection guardrail (P5):** retrieved note/document content is **evidence, not
  instructions** — ingested text must not be able to inject system prompts on a RAG surface exposed
  over MCP to multiple clients.
- **No secrets in code:** Ollama/Qdrant/Postgres hosts and the feature flag come from env/`Settings`,
  never hardcoded (extends `config.py`).
- **Parameterized queries only:** continue SQLAlchemy expression/ORM queries (no string-concatenated
  SQL); pgvector similarity via bound parameters.
- **Sanitize rich-text/user content** before storage (project rule) — chat answers saved as notes go
  through the same sanitation as editor output.
- **Two security properties are verified as evals, not unit tests** (decision 8): prompt-injection
  resistance (retrieved content is evidence, never instructions) and PARA-scope isolation (no
  cross-container leakage). Both are behavioral/authorization guarantees that a green unit suite
  would not prove — they belong in `evals.md` and gate "done."
- **Bind network surfaces locally:** MCP HTTP to `127.0.0.1`/LAN only (Q11.2); tighten the current
  wildcard CORS (`main.py:29-30`) toward explicit methods/headers as new origins are added.

### Deployment topology & corpus  (hardware — verified 2026-07-04)

**Serve/ingest split by accelerator.** Verified on the PC: grounded already runs Qdrant in *server*
mode (`~/.config/grounded-code-mcp/config.toml` → `qdrant_url=http://localhost:6333`, a Docker
container from grounded's `docker-compose.yml`), Ollama is already remote on the Mac Mini
(`192.168.42.165:11434`), and Docling ingestion is pinned to **CUDA + flash-attn** (`config.toml
[docling]`) — i.e. the PC's NVIDIA GPU. So the target is a split, not a wholesale move:
- **Serve on the Mac Mini** (always-on, VPN-reachable): Ollama, the shared **Qdrant server**, grounded's
  MCP serve, and second-brain's app + MCP + Postgres. Migrate Qdrant by **snapshot/restore of the
  `qdrant_data` volume — NOT re-ingest** (re-ingest needs the PC's CUDA Docling anyway).
- **Ingest on the PC** (CUDA Docling): reads the corpus in place, pushes vectors → Mac Mini Qdrant over
  LAN, then can sleep. Same grounded repo, two machine-specific config overrides.
- Moving grounded's *process* cannot interrupt second-brain — second-brain depends only on the
  Qdrant/Ollama **URLs**, not grounded's process (siblings, not a chain). The real migration risk is
  grounded's **own vetted `grounded_*` KB** living in the `qdrant_data` volume; that volume must be
  migrated, not lost.
- Security: Qdrant has **no auth** by default and is currently on `0.0.0.0:6333` — keep it LAN/VPN-only
  (never WAN-forward 6333) or set a Qdrant API key.

**Drive map (PC, verified).** Apps/code + Postgres → `AppDev` (sdb1, 2.6 T free). Raw corpus → `Media`
(sdc1). Backups (Qdrant snapshots, PG dumps) → external `Elements` (sdd1, NTFS — backup only, not live
DB). Qdrant Docker volume currently defaults to NVMe `/`.

**Corpus → PARA (ingest in place from `/home/malber/Media/eBooks/`; verified scan).**

| Folder | Size / files | Ingestable (pdf+epub) | Skip (noise) | PARA |
|---|---|---|---|---|
| Technology | 107 G / 62,205 | **~8,000** (5,264 pdf + 2,772 epub) | ~24K images, ~15K saved-HTML+assets, .class/.py/.php artifacts | Resources; stale → Archive |
| Business | 3.6 G / 501 | ~376 | 66 chm, 4 mobi (convert first) | Resources |
| Politics | 6.4 G / 1,042 | ~908 | jpg/mp4/mp3 | Resources |
| TheAtlantic | 977 M / 43 | 43 | — | Resources (periodical; old→Archive) |
| TheEconomist | 1.4 G / 414 | 115 | 295 mp3 audio editions (phase-2) | Resources (periodical; old→Archive) |

**Ingest in place; `data/documents/` is only for app-uploaded docs.** The bulk library is ingested
in place from `Media/eBooks` — only vectors (Qdrant) + metadata/provenance (Postgres) get created;
raw files never move (refines Q2.2). `second-brain/data/documents/` is reserved for documents
uploaded through the app UI, which still get the allowlist + magic-byte check.

**Two-tier knowledge separation.** `Media/eBooks/grounded-code-sources` = grounded's **vetted**
`grounded_*` collections (authoritative engineering standards). The topical folders above =
second-brain's **personal library** `brain_documents` (broad, some stale). Keep them **separate
collections** — a stale personal ebook must never pollute the vetted standards. second-brain queries
its own `brain_documents` + notes; it does not fold grounded's vetted KB into that surface (YAGNI;
avoids mixing authority levels).

**Selective ingest = mandatory, and mostly automatic.** Restricting the bulk-library ingest to
**`{pdf, epub}`** (the decision-8 security allowlist doing double duty) collapses Technology's 62 K
files → ~8 K with no hand-curation — images/saved-pages/code artifacts are simply not ingestable
types. **Staleness** (old-but-valid books) is handled by **PARA Archive** (excluded from default chat
scope per Q6.2/P1, still searchable on demand), not deletion or up-front curation. Formats outside the
allowlist (`chm`, `mobi`, `azw`, the `Kindle/` folder) need Calibre conversion or are skipped;
`mp3`/`mp4` are out of scope until phase-2 transcription.

**Ingest-cost reality (corrects decision 7's "overnight").** ~9.4 K PDFs through CUDA Docling is a
**multi-day** GPU batch — reinforcing PC/CUDA-only, sequential + batched, content-hash dedup so re-runs
are incremental, and a curated **first tranche** (e.g. Technology-recent) before the full sweep.
`# VERIFY:` staleness-curation strategy + whether to convert chm/mobi.

### Risks & dependencies

- **~~External grounded-code-mcp engine is unread~~ — RESOLVED.** Read and confirmed in
  `research-grounded-engine-api.md`: the four importable primitives, their exact signatures, the
  `snowflake-arctic-embed2`/1024-dim/COSINE substrate, and the minimum viable import path are all
  documented. The five reality-corrections it surfaced (no `pdf2md`/`web2md`; dedup not in parser;
  sync-only engine; query `is_query` prefix; non-deterministic IDs) are now folded into decisions 1
  and 7 as **design constraints**, not open risks. The packaging strategy (decision 9) is now
  **resolved to Option C** (restructure grounded's extras) — a small cross-repo task, not an open
  unknown.
- **Test-fixture migration:** the suite uses in-memory SQLite (`conftest.py:8-28`); pgvector needs a
  Postgres-backed test path (Testcontainers or a Compose test DB). **Resolution direction set by
  decision 8** — vector-touching tests run on ephemeral Postgres+pgvector, pure-logic tests stay
  in-memory; the exact fixture wiring is fixed in Movement 2's first slice.
- **~~Shared `notes` table gains Postgres-only column types → breaks the SQLite test base~~ — RESOLVED
  (decision 10).** The whole suite standardizes on ephemeral Postgres+pgvector (session-scoped
  Testcontainers + per-test txn rollback); in-memory SQLite is retired. `Vector(1024)` + JSONB build
  natively in tests, no dialect variants.
- **~~`highlights` is `sqlite.JSON` → non-additive change~~ — RESOLVED (decision 10).** With Postgres
  everywhere, `highlights` becomes native `JSONB`. This IS a type change to an existing column (not
  purely additive) — carried explicitly in Slice 1's migration, applied before the additive
  embedding/provenance columns.
- **New backend dependencies to add (Plan must enumerate):** an async Postgres driver (asyncpg or
  psycopg3 — neither present, `research.md` §6), the `pgvector` Python binding (for the `Vector` type),
  the grounded git dep pinned at `91021cae`
  (`grounded-code-mcp @ git+ssh://git@codeberg.org/michaelkalber/grounded-code-mcp.git@91021cae2e300378032471bfc63059a45cb3fb65`;
  `[parse]` only on the ingest box), and a magic-byte library (python-magic/libmagic or pure-Python
  `filetype`).
- **Streaming client path** does not exist yet in `client.ts` — new reader code, new frontend tests.
- **Alembic + pgvector:** the `vector` column type and the pgvector extension need a migration; the
  extension must exist in the dev/prod Postgres (Compose init).
- **Substrate availability:** federated search and chat depend on Mac Mini Ollama + central Qdrant
  being reachable; the feature flag + graceful-degrade path is the safety valve.
- **Project convention change (deliverable, not just risk):** the project `CLAUDE.md` is amended on
  **two** points so the logged conventions and this spec agree — (1) the architecture rule
  ("layered … not vertical slice") → VSA-with-shared-kernel (decision 3); (2) the Database **test**
  convention ("Test: In-memory SQLite `:memory:`") → **Postgres+pgvector via session-scoped
  Testcontainers** (decision 10). **DONE 2026-07-05 (uncommitted):** `CLAUDE.md` VSA rule was already
  present; its Database/Test section updated to Postgres+pgvector+Testcontainers. `AGENTS.md` gained
  an Architecture section (VSA + shared kernel) and the Postgres test-base convention. Both carry a
  transitional note (legacy stays on SQLite until this feature's Slice 1 lands).
- **First-slice scaffolding cost:** introducing `backend/app/features/` (package `__init__`, the
  first slice folder, the `main.py` include wiring, slice-local `conftest`) is one-time setup carried
  by Movement 2's first slice. Small, but it is genuinely new structure, not just new files in old
  folders — call it out so it is not mistaken for zero-cost.

## Movement 2 — Structure Outline  (source stage 4)

> Type/function signatures + **vertical** delivery slices. Each slice cuts mock-API → front-end → DB
> for ONE capability and lands inside `features/rag_document_chat/` (never a horizontal layer). `/qrspi-plan`
> turns each slice into a mechanically executable, Red-Green-Refactor plan. Signatures are the *shape*
> to build to, not final code.

### Module layout (the slice owns its full stack)

```
backend/app/features/rag_document_chat/
├── __init__.py
├── router.py          # thin routes (<15 lines each): /documents, /rag/search, /chat, save-as-note, /rag/health
├── schemas.py         # Pydantic v2, one-per-use-case
├── models.py          # Document, Conversation, Message (feature-owned); note-embedding/provenance wiring
├── engine.py          # async adapter over grounded's SYNC primitives (asyncio.to_thread)
├── ingest_service.py  # out-of-band ingest: parse→chunk→embed→upsert, sha256 dedup, delete-then-insert
├── retrieval_service.py  # federated merge/rank across pgvector notes + Qdrant docs, PARA scope
├── chat_service.py    # retrieve→prompt(evidence-not-instructions)→Ollama stream→persist
├── mcp_server.py      # separate entry point: read/search MCP tools (Streamable HTTP + stdio)
├── alembic/           # feature migrations (incl. the one additive shared-notes migration)
└── tests/             # co-located; slice-local Postgres+pgvector (Testcontainers) + reused conftest
```

**Shared-kernel touches:** `main.py` gains one `include_router(rag_router)`; `config.py` `Settings`
gains additive fields (below); the shared `notes` table gets a migration — mostly additive (embedding
`Vector(1024)` + provenance columns) **plus one type change** (`highlights` `sqlite.JSON → JSONB`,
decision 10); and `conftest.py` moves to Postgres+pgvector (decision 10). Legacy notes/containers/tags
*application* code is untouched (decision 3) — only their test backing changes.

### Config additions (`config.py Settings`, all additive, env-sourced)

```python
RAG_ENABLED: bool = False                      # master feature flag; off ⇒ router not mounted, banner shown
OLLAMA_HOST: str = "http://192.168.42.165:11434"
QDRANT_URL: str = "http://192.168.42.165:6333" # server mode (decision 2)
EMBEDDING_MODEL: str = "snowflake-arctic-embed2"  # config constant, never a bare literal (AI/ML rule)
EMBEDDING_DIM: int = 1024
DOCUMENTS_COLLECTION: str = "brain_documents"  # personal library; SEPARATE from grounded_* (two-tier)
DOCUMENT_UPLOAD_DIR: Path = Path("data/documents")  # app-UI uploads only; bulk library ingested in place
INGEST_ALLOWLIST: frozenset[str] = frozenset({"pdf", "epub"})  # bulk-library selective ingest
MCP_BIND_HOST: str = "127.0.0.1"               # LAN/VPN only, never WAN
```

### Key types & signatures

```python
# schemas.py  (Pydantic v2, ConfigDict(from_attributes=True) on *Response)
class RagHealthResponse(BaseModel):     enabled: bool; ollama: bool; qdrant: bool; postgres: bool; degraded: bool; message: str
class DocumentResponse(BaseModel):      id: UUID; title: str; source_path: str; file_type: str; container_id: UUID | None; sha256: str; chunk_count: int; status: Literal["pending","ingested","failed"]; created_at: datetime
class Citation(BaseModel):              source_type: Literal["note","document"]; source_id: UUID; chunk_id: str | None; title: str; snippet: str; score: float
class SearchResultItem(BaseModel):      source_type: Literal["note","document"]; source_id: UUID; title: str; snippet: str; score: float; container_id: UUID | None
class ChatRequest(BaseModel):           query: str; container_id: UUID | None = None; n_results: int = 8
class ChatChunk(BaseModel):             type: Literal["token","citation","done","error"]; text: str | None = None; citation: Citation | None = None
class SaveAsNoteRequest(BaseModel):     conversation_id: UUID; message_id: UUID; container_id: UUID | None = None

# models.py  (SQLAlchemy 2.0 Mapped[]; feature-owned tables)
class Document(Base):      id, title, source_path, file_type, sha256 (indexed), container_id FK→containers, chunk_count, status, created_at
class Conversation(Base):  id, container_id FK→containers (nullable), created_at
class Message(Base):       id, conversation_id FK, role: Literal["user","assistant"], content, citations: Mapped[list[dict]] (JSONB), created_at
# additive on SHARED notes (one migration): embedding: Vector(1024) | None; derived_from: JSONB | None; derivation_layer: str="primary"; supersedes: UUID | None

# engine.py  (async wrapper — every grounded call offloaded; decision 1)
class RagEngine:
    async def parse(self, path: Path) -> ParsedDocument          # to_thread(DocumentParser().parse)
    async def chunk(self, content: str, source_path: str) -> list[Chunk]
    async def embed_documents(self, texts: list[str]) -> list[list[float]]   # is_query=False
    async def embed_query(self, text: str) -> list[float]                    # is_query=True ("query: " prefix)
    async def upsert_document(self, collection: str, document_id: UUID, chunks: list[Chunk], vectors: list[list[float]]) -> None  # delete-then-insert on document_id payload
    async def search_documents(self, collection: str, qvec: list[float], *, n: int, min_score: float, filter_metadata: dict | None) -> list[SearchResult]

# retrieval_service.py
async def federated_search(db, engine, *, query: str, container_id: UUID | None, n: int) -> list[SearchResultItem]
    # embed_query → (Qdrant search w/ PARA payload filter) + (pgvector cosine over notes) → merge by score → PARA rank (Proj>Area>Res, Archives excluded)

# chat_service.py
async def stream_chat(db, engine, req: ChatRequest) -> AsyncIterator[ChatChunk]
    # federated_search → build EVIDENCE-not-instructions prompt → Ollama chat stream → yield token/citation frames → persist Conversation+Message

# mcp_server.py  (thin wrappers over the services above — DRY)
search_my_notes(query, container_id=None) · search_my_library(query, container_id=None) · chat_my_brain(query, container_id=None) · get_document_info(document_id) · list_containers()
```

### Vertical slices (dependency order; one checkpoint each)

**Slice 1 — Walking skeleton: flag + substrate health + `/chat` shell (degrade-safe).**
Carries one-time setup: `features/` package, `main.py` include, Settings additions, dev Compose
(Postgres+pgvector + Qdrant), and the **test-base migration (decision 10): retire in-memory SQLite,
move `conftest.py` to a session-scoped Testcontainers Postgres+pgvector with per-test txn rollback**,
plus the `highlights` `sqlite.JSON → JSONB` type change (before the additive notes columns).
- **mock-API → real:** `GET /api/v1/rag/health` → `RagHealthResponse`; `RAG_ENABLED` gates the router include.
- **front-end:** `/chat` route + `ragStore` (Pinia) health probe → chat shell OR "AI features disabled" banner.
- **DB:** pgvector extension migration; empty feature tables created.
- **✔ checkpoint:** flag off → banner; flag on + substrate up → healthy shell; substrate down → degrade banner.
  Tests: health contract, degrade path (substrate mocked-down), flag-gated mount.

**Slice 2 — Document ingest + list (Qdrant `brain_documents` + Postgres metadata).**
- **mock-API → real:** `POST /api/v1/documents` (multipart, **allowlist + magic-byte**), `GET /api/v1/documents?container_id=`
  return canned → then real via `ingest_service` (parse→chunk→embed→`upsert_document`), **sha256 dedup**, delete-then-insert.
- **front-end:** document-list view + upload + container filter.
- **DB:** `Document` model + migration; app-UI uploads → `DOCUMENT_UPLOAD_DIR`; bulk library ingested in place from `Media/eBooks`.
- **✔ checkpoint:** upload a PDF → ingested → listed with `chunk_count`; re-upload → one embed (dedup).
  Tests: **allowlist reject (security ≥95%)**, dedup, delete-then-insert idempotency, parser dispatch (engine mocked, no network).

**Slice 3 — Federated retrieval, PARA-scoped (folds in note-embedding + provenance).**
- **DB (shared-kernel touch):** additive `notes` migration (embedding `Vector(1024)` + provenance cols); embed-on-save
  (documents-style, **no** `query:` prefix); backfill existing notes; pgvector index.
- **mock-API → real:** `GET /api/v1/rag/search?q=&container_id=` canned merged results → then `federated_search`
  (Qdrant payload-filtered by container / Archives-excluded + pgvector cosine over notes, merge by score, PARA rank).
- **front-end:** search view, container scope selector, **note/document source badges** + scores.
- **✔ checkpoint:** query returns merged notes+docs; container-scoped (no cross-container leak); Archives excluded.
  Tests: merge order stable; **PARA-scope isolation (security)**; embed-on-save `is_query=False`; **parameterized pgvector**.

**Slice 4 — Streaming chat with citations + persisted conversation.**
- **mock-API → real:** `POST /api/v1/chat` → chunked `StreamingResponse` of `ChatChunk` frames; canned tokens/citations first,
  then `stream_chat` (retrieve → evidence-not-instructions prompt → Ollama stream → persist).
- **front-end:** chat UI + **new readable-stream reader** (additive to `client.ts`), live tokens, citation chips, history.
- **DB:** `Conversation` + `Message` (citations JSONB) models + migration.
- **✔ checkpoint:** ask → streamed grounded answer with clickable citations; conversation persisted.
  Tests: streaming frame contract + terminal framing; citations reference retrieved chunks; **prompt-injection resistance (eval seed)**.

**Slice 5 — Save chat answer as note (provenance loop).**
- **mock-API → real:** `POST /api/v1/chat/{conversation_id}/messages/{message_id}/save-as-note` → `NoteResponse`;
  real path **sanitizes** answer, creates Note with `derivation_layer="derived"`, `derived_from=[cited ids]`, embeds it.
- **front-end:** "save as note" action on an assistant message → navigate to the new note.
- **DB:** reuses slice-3 provenance columns.
- **✔ checkpoint:** save → new note carries citations as provenance, is embedded, and is retrievable in slice-3 search.
  Tests: provenance set correctly; **sanitation (security)**; new note embedded.

**Slice 6 — second-brain MCP server (read/search surface).**
- **API (MCP):** separate `mcp_server.py` entry point sharing code+DB; **Streamable HTTP + stdio**; bound `MCP_BIND_HOST`.
  Tools `search_my_notes` / `search_my_library` / `chat_my_brain` / `get_document_info` / `list_containers` — thin wrappers (DRY).
- **"front-end" = MCP client smoke test** (Claude Code / Goose / Open WebUI via `mcpo`) — agents are the clients.
- **DB:** none new (reuses services).
- **✔ checkpoint:** an MCP client lists the tools and gets grounded results; **scope isolation holds over MCP**.
  Tests: tool contract; bind address (127.0.0.1/LAN); evidence-not-instructions over MCP.

### Acceptance gate (before coding Slice 4 / per decision 8)

Seed `evals.md` with the labeled RAG eval set — retrieval relevance (recall@k/precision@k),
groundedness/citation-correctness, **prompt-injection resistance**, **PARA-scope isolation** — over a
fixed sample corpus. "Done" for the feature = every slice green **and** the eval set passes.

### Plan-phase prerequisite (cross-repo) — ✅ CLEARED

**Option C (decision 9) is DONE.** grounded PR #1 merged into `main` 2026-07-04; the engine core
installs light and heavy deps are opt-in extras (`parse`/`serve`/`graph`/`chroma`/`all`). second-brain
pins:
`grounded-code-mcp @ git+ssh://git@codeberg.org/michaelkalber/grounded-code-mcp.git@91021cae2e300378032471bfc63059a45cb3fb65`
(add `[parse]` on the PC/CUDA ingest box; the serve box needs no extras). Task log:
`grounded-option-c-task.md`. `/qrspi-plan` is unblocked.
