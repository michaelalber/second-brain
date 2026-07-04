---
feature: rag-document-chat
status: answers-complete-ready-for-research
created: 2026-06-29
revised: 2026-07-03 (rev4 — all open items resolved; ready for /qrspi-research)
source-project: ../grounded-code-mcp (RAG engine — reused for documents)
retired-project: ../local-rag (KnowledgeHub — archived; role absorbed by second-brain)
target-project: second-brain
informed-by:
  - OB1 / Open Brain (NateBJones-Projects/OB1) — thoughts primitive, provenance-chains, smart-ingest, agent-memory schemas
  - Forte Labs — PARA method + "Why PARA Is the Key to the AI Era"
---

# QRSPI Questions — rag-document-chat

> Revised 2026-07-03 against the agreed architecture (§0) and the adopted design principles
> (§14). Most questions are **DECIDED**; **CONFIRM** items carry a recommended answer to
> accept/change; **OPEN** items still need input. Open shortlist at the bottom.

---

## 0. Design Baseline (decided this session)

- **Two stores, one interface — the right tool per data type, federated at the MCP layer:**
  - **Documents / ebooks → `grounded-code-mcp`'s Qdrant engine** (reused as a library). Heavy Docling
    ingestion, code-aware chunking, permanent vectors. Collection `brain_documents`.
  - **Notes → second-brain's own Postgres + `pgvector`.** The note, its metadata, its provenance,
    and its embedding all live in one row. Lineage/synthesis is a Postgres-shaped problem (see §14 P3),
    and this dissolves the separate notes→vector sync path (§12).
- **local-rag:** retired/archived. Role absorbed; code not ported (salvage Vue chat bits only if handy).
- **Shared substrate:** one Ollama + one Qdrant on the Mac Mini (LAN, Ollama `192.168.42.165:11434`);
  second-brain's Postgres holds notes. **Same embedding model + distance metric on both stores** so
  federated results are score-comparable (see §4, §14 P1).
- **second-brain exposes its own MCP server** over notes + documents, reachable by Goose, Claude Code,
  **and Open WebUI via `mcpo`** (same wiring as grounded). Open WebUI does no retrieval of its own.
- **Retrieval is PARA-native (see §14 P1):** the container is a pre-assembled context bundle;
  container-scoped chat is the *primary* mode, whole-corpus search the fallback; rank
  Projects > Areas > Resources; exclude Archives by default.
- **Documents are first-class PARA resources**, filed in a *single* most-actionable container (§14 P2).
- **Provenance is first-class** (§14 P3): `derived_from` / `derivation_layer` / `supersedes`.
- **Strictly local** (Ollama); AI is optional and feature-flagged; app runs without it.

---

## 1. Integration Architecture

**Q1.1** — merge / sidecar / standalone?
> **DECIDED.** second-brain depends on `grounded-code-mcp` as a library for the *document* engine, and
> owns its *notes* store (Postgres+pgvector) directly. Not a sidecar, not local-rag.

**Q1.2** — wholesale import vs extract core?
> **DECIDED (reframed).** Reuse grounded's engine via dependency for documents. Coupling → §13.

**Q1.3** — local-rag's Vue frontend?
> **DECIDED.** Discard; second-brain's Vue app is the only UI. Salvage individual chat components only.

---

## 2. Document Storage & Lifecycle

**Q2.1** — what does "permanent vector data" mean?
> **DECIDED.** Both: vectors persist across restarts, and identical content is not re-embedded (manifest
> for documents in Qdrant; content-hash guard for notes — §14 P6).

**Q2.2** — where are raw document files stored?
> **CONFIRM.** Default `second-brain/data/documents/` (outside web root per security rule), configurable.

**Q2.3** — delete document → vectors?
> **DECIDED.** Hard delete — remove vectors immediately.

**Q2.4** — one PARA container or many?
> **DECIDED — one.** PARA doctrine: file in the single most-actionable location; duplication violates
> simplicity (Forte). Moving between containers updates the container reference only — **never a re-embed**.

---

## 3. Vector Storage (split)

**Q3.1** — which store(s)?
> **DECIDED (rev2 — the reopened decision).** **Documents → Qdrant** (grounded's engine).
> **Notes → Postgres + pgvector** (embedding is one column on the note row). Not one-store-for-all.
> Rationale in §14 P3 — provenance/lineage is relational; a vector is the *whole* point of a document
> but just *one facet* of a note.

**Q3.2** — same DB as notes, or separate?
> **DECIDED.** Notes (content + metadata + provenance + embedding) live together in second-brain's
> Postgres. Document chunks + vectors live in the shared Qdrant. The **second-brain MCP federates a
> query across both and merges by score** (requires the same embedding model + distance metric — §4).

**Q3.3** — expected library size?
> **DECIDED — hundreds of books** (tech, business, politics, education) **+ assorted magazines.** ~100s of
> sources → ~10⁴–10⁵ chunks. Qdrant/HNSW handles this comfortably; arctic-embed2's 8192-ctx suits book chunks.
> **Implications:**
> - **One `brain_documents` collection filtered by payload — not per-topic collections.** PARA organizes by
>   actionability, not subject (§14 P1/P7). Primary scope = PARA container (books/magazines are mostly
>   Resources); `domain` (tech/business/politics/education) + `source_type` (book|magazine) + `date` ride as
>   payload filters for optional narrowing. Keeps cross-domain search possible; avoids topic fragmentation.
> - **Magazines need issue/date metadata** and are lower-signal ("might have useful info"): capture
>   `source_type=magazine` + publication date so they can be recency/quality-weighted or down-ranked later
>   (OB1 `enhanced-thoughts` fields — store the metadata now, defer the ranking; YAGNI).
> - **Ingestion is a real batch job:** hundreds of books is slow — pre-process with **pdf2md** first (Q5.4;
>   `fast` engine for digital PDFs, Docling only for scanned), then ingest **sequentially** (parallel = OOM),
>   with content-hash **dedup on** (§14 P6; large libraries carry duplicate ebooks). Plan an overnight run.

**Q3.4 (new)** — pgvector requires **Postgres in dev**, not just prod (SQLite has no vector search).
Provenance columns are DB-agnostic and work in SQLite; only the note *embedding column* needs Postgres.
> **DECIDED — commit dev to Postgres.** Local Postgres + pgvector for dev via a Docker Compose service
> (§10.3). Provenance columns still work anywhere; the note embedding column needs Postgres.

---

## 4. LLM & Embedding

**Q4.1** — strictly local, or optional cloud?
> **DECIDED.** Strictly local (Ollama).

**Q4.2** — embedding model?
> **DECIDED — `snowflake-arctic-embed2` + cosine on both stores** (1024-dim, 8192 ctx), fixed default,
> configurable. Same model + metric on pgvector notes and Qdrant documents so federated search (§3.2) merges
> scores meaningfully. (grounded already uses it; local-rag's `mxbai-embed-large` dropped for consistency.)

**Q4.3** — Ollama not running?
> **DECIDED.** Graceful degradation: show notes/documents, disable chat with a clear banner + feature flag.

---

## 5. Document Types & Ingestion

**Q5.1** — required document types at launch?
> **DECIDED — lean into Docling's breadth.** Launch set: PDF, EPUB, DOCX, PPTX, HTML, Markdown/TXT/RST
> (all handled by grounded's Docling pipeline). XLSX + images(OCR) optional; web-page/URL ingestion stays
> phase 2 (fetch→convert).
> **Security follow-through (required):** grounded's current extension allowlist is
> `.pdf/.epub/.md/.txt/.rst/.html`. Adding DOCX/PPTX/(XLSX) means **expanding the validated allowlist +
> adding magic-byte checks per new type** (OWASP file-upload). Each new parser = new attack surface;
> validate before enabling.

**Q5.2** — URLs: fetch-and-store vs live?
> **DECIDED (when added).** Fetch-and-store at ingestion. URLs are phase 2.

**Q5.3** — Docling required?
> **DECIDED (refined by Q5.4).** Docling handles **non-PDF** formats (EPUB/DOCX/PPTX/HTML) and **scanned**
> PDFs; digital PDFs take pdf2md's lighter `fast` engine. On the Mac it uses MPS (no CUDA/flash-attn).
> Notes don't need Docling — they're already text.

**Q5.4 (new)** — PDF pre-processing toolchain.
> **DECIDED — reuse `ai-toolkit/tools/pdf2md`** (purpose-built for grounded; emits headings, code fences
> with language tags, tables, images, and YAML provenance front-matter). Pipeline:
> `pdf2md ./ebooks ./md-out --engine auto` → feed the `.md` output to grounded's **`.md` ingest path**
> (no Docling at ingest; **grounded's code-aware chunker does the chunking** — don't pre-chunk with
> `--chunk-by-heading`, keep one chunking strategy).
> - **Time-saver:** `auto`/`fast` uses PyMuPDF for *digital* ebooks and only invokes **Docling for scanned**
>   PDFs — much faster on a hundreds-of-books run than forcing Docling everywhere.
> - **Non-PDF** (EPUB/DOCX/PPTX) → grounded's Docling path directly (pdf2md is PDF-only). **URLs** →
>   `ai-toolkit/tools/web2md` (phase 2).
> - **Redundancy:** pdf2md supersedes grounded's built-in `convert` for PDFs; keep grounded `convert` only
>   for the non-PDF formats pdf2md doesn't handle.
> - pdf2md's YAML front-matter (`source`, `pages`, `extracted_at`, `tool`) feeds provenance (§14 P3) and can
>   carry `source_type`/`domain`/`date` for the payload filters (Q3.3).

---

## 6. PARA Integration

**Q6.1** — first-class PARA resources or separate library?
> **DECIDED.** First-class PARA resources — documents live in containers alongside notes.

**Q6.2** — is chat scopeable?
> **DECIDED (rev2 — elevated to core principle, §14 P1).** Container-scoping is the **primary** mode:
> you chat *within* a Project/Area and that container is the pre-assembled context bundle. Whole-corpus
> semantic search is the fallback. Default excludes **Archives**; cross-container ranking favors
> Projects > Areas > Resources. Manual document-set scope = phase 2.

**Q6.3** — can document content seed a note?
> **DECIDED + provenance.** Yes. Saving a chat answer as a note sets `derivation_layer='derived'` and
> `derived_from = [cited note/document/chunk ids]` (§14 P3) — the answer keeps its link to its evidence.

---

## 7. Chat UX

**Q7.1** — where does chat live?
> **DECIDED.** Dedicated `/chat` route in second-brain (container-selectable), **plus Open WebUI as an
> external chat surface** over the second-brain MCP (§11) — same "the app owns retrieval, clients are
> windows" model. Embedding chat in a container/note view is a phase-2 add.

**Q7.2** — persist chat history or ephemeral?
> **DECIDED — persist.** Conversations are capturable knowledge (feeds Q6.3) and part of compounding memory
> (§14 P8) — persisting + capturing good answers as notes is the compounding loop, not just convenience.

**Q7.3** — source citations?
> **DECIDED.** Yes — required (grounded returns source paths; notes carry provenance).

---

## 8. API Design

**Q8.1** — `/api/v1/...` or new namespace?
> **CONFIRM.** Under `/api/v1` (`/api/v1/documents`, `/api/v1/chat`), matching convention.

**Q8.2** — stream or single payload?
> **DECIDED — stream over HTTP, not legacy SSE.** App chat endpoint uses FastAPI `StreamingResponse`
> (HTTP chunked / fetch readable-stream on the Vue side); no `EventSource`/standalone-SSE. Consistent with
> the Streamable HTTP choice for the MCP transport (§11.2).

---

## 9. Testing & Migration

**Q9.1** — migrate local-rag tests or fresh?
> **DECIDED.** Fresh suite matching second-brain conventions.

**Q9.2** — migrate existing vector data?
> **DECIDED.** Start fresh; re-ingest.

---

## 10. Deployment & Dependencies

**Q10.1** — launchable without Ollama?
> **DECIDED.** Yes; BASB/notes features work without it, chat disabled gracefully.

**Q10.2** — feature flag or always-on?
> **DECIDED.** Feature flag (opt-in via env var).

**Q10.3** — Docker Compose?
> **DECIDED.** Not for Ollama (remote on Mac Mini). **Use Compose for the local dev Postgres+pgvector**
> (now a committed dev dependency, §3.4). second-brain runs natively, pointing at Mac Mini Ollama + central
> Qdrant and a local (dev) / prod Postgres.

---

## 11. second-brain MCP server

**Q11.1** — Tool surface (thin wrappers over the federated search): `search_my_notes(query, container?)`,
`search_my_library(query, container?)`, `chat_my_brain(query, container?)`, `get_document_info(path)`,
`list_containers()`. Clear, self-describing names so Open WebUI's model selects them reliably.
> **DECIDED — these tool names.** Read/search surface at launch; a write/capture tool (`remember`) is
> roadmap (§14 P8), gated by governance before it ships.

**Q11.2** — Transport.
> **DECIDED — Streamable HTTP** (current MCP standard; supersedes the deprecated HTTP+SSE two-endpoint
> transport — FastMCP ≥3 supports it, as grounded uses) **+ stdio** for local agents (Goose/Claude Code).
> Verify `mcpo`/Open WebUI speaks Streamable HTTP when wiring (same path as grounded). Bind HTTP to
> `127.0.0.1`/LAN only.

**Q11.3** — MCP in the FastAPI process or a separate entry point sharing engine + DB?
> **DECIDED — separate entry point, shared code/DB** — independently launchable, like grounded's `serve`.

---

## 12. Note embedding (was "notes→vector sync" — largely dissolved)

> Under pgvector (§3), a note's embedding is a column computed on write — **no separate sync service.**
> What remains:

**Q12.1** — Compute embedding synchronously on save, or as a lightweight background enrich for large notes?
> **DECIDED (lean accepted) — on-save for typical notes; background only if a note is large.**

**Q12.2** — Which text is embedded? L1 raw only, or raw + latest distilled layer?
> **DECIDED (lean accepted) — raw + latest distilled layer**, so search hits both captured and refined content.

**Q12.3** — Note deletion → remove its row/embedding (hard delete, mirrors Q2.3).
> **DECIDED.**

---

## 13. Shared-engine coupling

**Q13.1** — How second-brain consumes grounded's *document* engine:
> **DECIDED (a) — depend on `grounded-code-mcp` directly** (import `IngestionPipeline` + search impl +
> `EmbeddingClient`; init with own `Settings`, `collection_prefix="brain_"`, own manifest). Extract a
> neutral `rag-core` later if the naming/singleton-global-state coupling bites (rule of three).

**Q13.2** — Substrate host.
> **DECIDED — central Qdrant on the Mac Mini.** grounded is single-user and fully reproducible from its
> `sources/`, so "centralize" = stand up Qdrant on the Mac, **re-ingest grounded's collections there**
> (recreate — no fragile data migration), point second-brain + grounded at it, retire the PC-local Qdrant.
> Run ingest sequentially with Ollama up first (grounded's constraints).

---

## 14. Design principles adopted (OB1 + PARA)

- **P1 — Retrieve by actionability (PARA/AI-era).** The container is a pre-assembled context bundle.
  Default to container-scoped chat; whole-corpus search is the fallback. Exclude Archives by default;
  rank Projects > Areas > Resources. Don't do undifferentiated retrieval across everything.
- **P2 — Single placement (PARA).** One container per item; moving between containers is a reference
  change, never a re-embed.
- **P3 — Provenance is first-class (OB1 `provenance-chains`).** Add `derived_from` (JSONB array of source
  ids), `derivation_layer` (`primary` captured vs `derived` synthesized), `supersedes` (versioning) to the
  notes table. Denormalized columns, not an edge table. **Complements** BASB progressive summarization
  (intra-note highlights) with *inter-note* lineage. Provides `trace_provenance()` / `find_derivatives()`
  style queries — native in Postgres, impossible in Qdrant.
- **P4 — Additive schema (OB1 `enhanced-thoughts`).** Keep the base notes table lean; promote hot filter
  fields to columns; put optional/governance concerns in sidecars later.
- **P5 — Evidence, not instructions (OB1 `agent-memory`; OWASP).** Retrieved note/document content is
  *evidence*, never *instructions*. Ingested text must not be able to inject system prompts — a
  prompt-injection guardrail for a RAG surface exposed over MCP to multiple clients.
- **P6 — Dedup at ingest (OB1 `smart-ingest`).** Level-1 only for launch: content-hash / `input_hash`
  uniqueness so the same text isn't embedded twice. Skip the `append_evidence`/`create_revision`
  reconciliation machinery (YAGNI).
- **P7 — Simplicity (PARA/YAGNI).** Four categories, no more. "The system must give you time, not take it."
- **P8 — Memory compounds (Nate B Jones / OB1).** Persistent personal memory is the core AI value, and it
  *compounds* — the more you capture, distill, and link, the more personalized retrieval gets. The design
  already embodies this: permanent storage (no ephemeral); **provenance (P3) is *how* memory compounds
  without losing its evidence trail**; and the **chat → persist → capture-as-note loop** (Q7.2/Q6.3) is the
  compounding cycle. **Roadmap:** a write/capture MCP tool (`remember` / `capture_to_brain`) so *any* AI
  client contributes to the brain, not just reads it — gated by the deferred agent-memory governance
  (agent-written = pending-review; evidence-not-instruction P5) before it ships.
- **P9 — Knowledge graph / GraphRAG (phase 2, not MVP).** Reuse grounded's concept-graph *store +
  traversal + graph-expanded retrieval* (query → concepts → ~2-hop expansion; hits tagged
  `[graph-expanded: via <concept>]`; the `query_graph` traversal tool), but **replace its hand-authored
  `RELATIONSHIPS.md` population with automatic concept/entity extraction at ingest** (OB1
  `entity-extraction`-style) — authoring triples per source doesn't scale to hundreds of books. **Host the
  graph in Postgres** (edge table + recursive CTEs; a graph is relational — same reason notes use pgvector),
  unifying **provenance edges (P3)** and **concept-link edges** as *typed edges* over notes + documents.
  Value: "show me everything connected to this idea," multi-hop chat, retrieval that finds related material
  vector search misses. **Layer on after** the vector-RAG + provenance skeleton works and there's enough
  interlinked content to connect — building a graph over an empty brain is wasted effort.
- **Deferred (logged, not built):** agent-memory governance sidecars, per-agent identity, evidence-merge
  reconciliation, multi-user RLS, the P8 write/capture MCP tool, the P9 GraphRAG layer. Revisit post-MVP
  (P9 after the skeleton; the write/capture + governance items when autonomous agents *write* to the brain).

---

## All questions resolved — ready for `/qrspi-research`

_Final pass 2026-07-03 (rev4): Q3.3 library (hundreds, multi-domain + magazines) · Q4.2 arctic-embed2 +
cosine · Q7.1/7.2 `/chat` route + Open WebUI + persist history · Q11.1/11.3 tool names + separate process ·
Q12.1/12.2 embed on-save, raw+distilled. Remaining CONFIRM items (Q2.2 storage path, Q8.1 `/api/v1` prefix)
accepted at their recommended leans._

**Next step:** run `/qrspi-research` — objective, ticket-hidden codebase mapping of second-brain (models,
services, alembic, Vue) against this design, before `/qrspi-spec`.
