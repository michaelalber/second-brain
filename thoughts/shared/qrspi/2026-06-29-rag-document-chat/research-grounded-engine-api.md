---
feature: rag-document-chat
artifact: research-addendum
subject: grounded-code-mcp importable engine API
status: complete
created: 2026-07-03
---

# grounded-code-mcp — Importable Engine API (Library Reuse Analysis)

Scope: confirm the *importable Python API* of the grounded-code-mcp engine so
`second-brain` can reuse it as a **library** (direct imports), not over MCP.
All engine logic lives in flat modules under `src/grounded_code_mcp/`. The MCP
server (`server.py`) is a thin layer over these modules and is NOT required for
library reuse.

Package name: `grounded-code-mcp` v2.1.0, MIT license, hatchling build
(`pyproject.toml:5-11`, `:52-53`, `:59-60`). Import package: `grounded_code_mcp`.

---

## Area 1 — Document ingestion (parse → markdown, + hash dedup)

Module: `src/grounded_code_mcp/parser.py`

- `ParsedDocument` dataclass — `parser.py:42-56`
  - `path: Path`, `content: str`, `title: str | None = None`,
    `page_count: int | None = None`, `file_type: str = ""`,
    `metadata: dict[...] | None = None`; `is_empty` property.
- `class DocumentParser` — `parser.py:122`
  - `__init__(self, *, enable_ocr: bool = True, enable_table_extraction: bool = True,
    pdf_page_batch_size: int = 0, docling_settings: DoclingSettings | None = None) -> None`
    — `parser.py:125-150`
  - `parse(self, path: Path) -> ParsedDocument` — `parser.py:183`. Plaintext
    (`.md/.rst/.txt/.asciidoc`) read directly; binary formats via Docling; prefers a
    pre-converted `<name>.md` sidecar when present (`parser.py:209-218`).
  - `parse_many(self, paths: list[Path], *, skip_errors: bool = True) -> list[ParsedDocument]`
    — `parser.py:407`
- Module helpers:
  - `is_supported_format(path: Path) -> bool` — `parser.py:75`
  - `get_file_type(path: Path) -> str` — `parser.py:87`
  - `sidecar_path(source: Path) -> Path` — `parser.py:110`
  - `scan_directory(directory, *, recursive=True, exclude_filenames=frozenset(),
    exclude_patterns=None) -> list[Path]` — `parser.py:447`
- Exceptions: `DocumentParseError` (`parser.py:59`), `UnsupportedFormatError`
  (`parser.py:67`).

**Content-hash dedup** lives in the manifest layer, NOT the parser:
Module: `src/grounded_code_mcp/manifest.py`
- `compute_sha256(path)`, `SourceEntry.has_changed(hash)`, `Manifest.load_or_create/
  get_entry/add_entry/save` — used by `ingest.py:13, 219-222, 276-287`.
Dedup is orchestrated only inside `IngestionPipeline._process_file`
(`ingest.py:218-224`). A caller composing primitives directly gets **no dedup**
unless it also reuses `Manifest`.

Import-friendliness: **clean.** `DocumentParser` is an injectable class; Docling is
imported lazily inside methods (`parser.py:152-160, 337, 357`), so importing this
module does not pull Docling at import time.

Async: **all sync.** `parse()` is a blocking call (Docling CPU/GPU work).

---

## Area 2 — Chunking

Module: `src/grounded_code_mcp/chunking.py`

- `Chunk` dataclass — `chunking.py:23-41`
  - `chunk_id: str`, `content: str`, `chunk_index: int`, `start_char: int = 0`,
    `end_char: int = 0`, `heading_context: list[str] = []`, `is_code: bool = False`,
    `code_language: str | None = None`, `is_table: bool = False`,
    `source_path: str = ""`; `char_count` property.
- `class DocumentChunker` — `chunking.py:133`
  - `__init__(self, text_chunk_size: int = 1000, text_chunk_max_size: int = 1500,
    text_chunk_overlap: int = 200, max_code_chunk_size: int = 3000) -> None`
    — `chunking.py:136-154`
  - `@classmethod from_settings(cls, settings: ChunkingSettings) -> DocumentChunker`
    — `chunking.py:156`
  - `chunk(self, content: str, source_path: str = "") -> list[Chunk]` — `chunking.py:173`
- `generate_chunk_id(source_path: str, index: int) -> str` — `chunking.py:44`.
  **Returns a random `uuid.uuid4()`** — source_path/index are ignored
  (`chunking.py:60-61`). IDs are NOT deterministic; re-ingest produces new IDs.

Import-friendliness: **clean.** Pure-Python, no external clients, no import-time
side effects. Async: **sync.**

---

## Area 3 — Embedding generation (Ollama)

Module: `src/grounded_code_mcp/embeddings.py`

- `EmbeddingResult` dataclass — `embeddings.py:38-49`
  - `text: str`, `embedding: list[float]`, `model: str`; `dimensions` property.
- `class EmbeddingClient` — `embeddings.py:52`
  - `__init__(self, model: str = "snowflake-arctic-embed2",
    host: str = "http://localhost:11434", context_length: int = 8192) -> None`
    — `embeddings.py:55-71`
  - `@classmethod from_settings(cls, settings: OllamaSettings) -> EmbeddingClient`
    — `embeddings.py:73`
  - `embed(self, text: str, *, is_query: bool = False) -> EmbeddingResult`
    — `embeddings.py:188`
  - `embed_many(self, texts: list[str], *, batch_size: int = 32,
    show_progress: bool = False, is_query: bool = False) -> list[EmbeddingResult]`
    — `embeddings.py:224`
  - `health_check() -> dict[...]` — `embeddings.py:122`;
    `ensure_ready() -> None` — `embeddings.py:170` (raises `OllamaConnectionError`/
    `ModelNotFoundError`); `get_embedding_dimensions() -> int` — `embeddings.py:310`.
- Ollama client is created lazily (`embeddings.py:89-94`, `ollama.Client(host=...)`).

**Query/document asymmetry (important):** `is_query=True` prepends the literal
`"query: "` prefix to the text before embedding (`embeddings.py:204, 257`).
Documents are embedded WITHOUT the prefix; queries WITH it. The server passes
`is_query=True` on the search path (`server.py:291, 391`). Second-brain must
replicate this asymmetry to match retrieval behavior.

**Model + dimension (CONFIRMED):** default model `snowflake-arctic-embed2`,
`embedding_dim = 1024`, `context_length = 8192` (`embeddings.py:57-59`,
`config.py:52-55`).

Import-friendliness: **clean class**, but `import ollama` happens at module top
(`embeddings.py:9`) — the `ollama` package must be installed to import this module.
Async: **sync** (blocking HTTP to Ollama).

---

## Area 4 — Vector storage / search (Qdrant)

Module: `src/grounded_code_mcp/vectorstore.py`

- `SearchResult` dataclass — `vectorstore.py:22-42`
  - `chunk_id: str`, `content: str`, `score: float`,
    `metadata: dict[str, Any] = {}`; `source_path`, `heading_context` properties.
- `class VectorStore(ABC)` — `vectorstore.py:45` (abstract contract):
  - `create_collection(self, name: str, *, embedding_dim: int = 1024) -> None`
  - `delete_collection(self, name: str) -> None`
  - `collection_exists(self, name: str) -> bool`
  - `add_chunks(self, collection: str, chunks: list[Chunk],
    embeddings: list[list[float]]) -> None`
  - `delete_chunks(self, collection: str, chunk_ids: list[str]) -> None`
  - `search(self, collection: str, query_embedding: list[float], *,
    n_results: int = 5, min_score: float = 0.0,
    filter_metadata: dict[str, Any] | None = None) -> list[SearchResult]`
  - `list_collections(self) -> list[str]`
  - `collection_count(self, name: str) -> int`
- `class QdrantStore(VectorStore)` — `vectorstore.py:148`
  - `__init__(self, path: Path | str | None = None, *, url: str | None = None) -> None`
    — `vectorstore.py:151`. `url=` (running server) takes precedence over `path=`
    (embedded/local); with neither, uses `":memory:"` (`vectorstore.py:164-169`).
  - `create_collection(name, *, embedding_dim=1024)` — **distance hardcoded to
    `Distance.COSINE`** (`vectorstore.py:181-187`). Idempotent (returns if exists).
  - `add_chunks(...)` — builds `PointStruct(id=chunk.chunk_id, vector=embedding,
    payload={content, source_path, chunk_index, heading_context, is_code,
    code_language, is_table})`, upserts in batches of `_UPSERT_BATCH_SIZE = 100`
    (`vectorstore.py:198-232`, `:13`).
  - `search(...)` — uses `query_points(..., score_threshold=min_score)`;
    higher score = better (cosine) (`vectorstore.py:263-301`).
  - `close(self) -> None` — `vectorstore.py:315` (releases local storage lock).
- `class ChromaStore(VectorStore)` — `vectorstore.py:320` (Docker-free fallback;
  converts distance→similarity as `1.0 - distance`, `vectorstore.py:446`).
- `create_vector_store(settings: Settings) -> VectorStore` — `vectorstore.py:484`.
  Reads `settings.vectorstore.provider`, `qdrant_url`, `knowledge_base.data_dir`.
  With `provider="qdrant"` + `qdrant_url` set → `QdrantStore(url=...)`; otherwise
  embedded `QdrantStore(path=data_dir/"qdrant")`.

**Collection naming:** `grounded_<suffix>`. Prefix is `VectorStoreSettings.
collection_prefix = "grounded_"` (`config.py:93`). Resolution via
`Settings.get_collection_name(source_path)` (`config.py:195-219`) — matches the
`[collections]` prefix map, else first path component under `sources_dir`, else
`grounded_default`. A library caller can bypass this and pass any collection name
string directly to `create_collection`/`add_chunks`/`search`.

Import-friendliness: **mostly clean**, but `from qdrant_client import QdrantClient`
runs at module top (`vectorstore.py:11`), so `qdrant-client` must be installed to
import this module. ChromaDB is imported lazily inside `ChromaStore.__init__`
(`vectorstore.py:329`) — not pulled unless Chroma is used. Async: **sync.**

---

## Configuration objects (Pydantic v2, TOML-only)

Module: `src/grounded_code_mcp/config.py` (all `pydantic.BaseModel`)
- `Settings` — `config.py:97` with sub-models: `KnowledgeBaseSettings` (`:17`),
  `OllamaSettings` (`:49`: `model`, `host`, `embedding_dim=1024`,
  `context_length=8192`), `ChunkingSettings` (`:58`: includes `ingest_batch_size=50`),
  `DoclingSettings` (`:71`), `VectorStoreSettings` (`:89`:
  `provider="qdrant"`, `collection_prefix="grounded_"`, `qdrant_url: str | None`),
  and `collections: dict[str, str]`.
- `Settings.load(config_path=None, user_config_path=None) -> Settings` — `config.py:148`.
  Merges `./config.toml` + `~/.config/grounded-code-mcp/config.toml`. **No env var
  support** (TOML only). Sub-models can also be instantiated directly in code with
  defaults (e.g. `OllamaSettings()`, `VectorStoreSettings(qdrant_url=...)`), so a
  caller can construct config programmatically without any TOML file.

---

## Minimum viable import path

**(a) Ingest + embed one document into Qdrant** (compose primitives — avoids the
MCP server, manifest, and graph entirely):

```python
from grounded_code_mcp.parser import DocumentParser
from grounded_code_mcp.chunking import DocumentChunker
from grounded_code_mcp.embeddings import EmbeddingClient
from grounded_code_mcp.vectorstore import QdrantStore

parser  = DocumentParser()
chunker = DocumentChunker()
embedder = EmbeddingClient(model="snowflake-arctic-embed2",
                           host="http://localhost:11434")
store    = QdrantStore(url="http://localhost:6333")

parsed = parser.parse(path)                                   # -> ParsedDocument
chunks = chunker.chunk(parsed.content, source_path=str(path)) # -> list[Chunk]
vectors = [r.embedding for r in
           embedder.embed_many([c.content for c in chunks])]  # documents: is_query=False
store.create_collection("grounded_notes", embedding_dim=1024) # COSINE fixed
store.add_chunks("grounded_notes", chunks, vectors)
```

**(b) Similarity search:**

```python
qvec = embedder.embed(query, is_query=True).embedding         # NOTE: is_query=True
hits = store.search("grounded_notes", qvec, n_results=5, min_score=0.3)
# hits: list[SearchResult]  (score = cosine similarity, higher is better)
```

Smallest symbol set: `DocumentParser`, `DocumentChunker`, `EmbeddingClient`,
`QdrantStore` (+ dataclasses `ParsedDocument`, `Chunk`, `SearchResult` for typing).
The high-level alternatives — `ingest_documents(settings, path, *, collection, force,
progress_callback)` (`ingest.py:426`) and `IngestionPipeline` (`ingest.py:47`) —
add manifest dedup and directory scanning but couple to `Settings`, the manifest
file, and (on `force=True`) the separate `graph` package (`ingest.py:293-294,
313-314`).

---

## ASSUMPTION vs REALITY

1. **`pdf2md` / `web2md`** — ASSUMPTION: named converters. REALITY: no such symbols
   exist. Parsing is `DocumentParser.parse()` via Docling for binary formats
   (`parser.py:277-325`) and direct file read for plaintext. A `convert` CLI command
   writes `.md` sidecars, but there is no importable `pdf2md`/`web2md` function.
2. **Content-hash dedup** — ASSUMPTION: available alongside parsing. REALITY: dedup
   (SHA-256) lives only in the `Manifest`/`IngestionPipeline` layer
   (`ingest.py:218-224`), not in the parser/chunker. Composing primitives directly
   yields NO dedup unless `Manifest` is also reused.
3. **`snowflake-arctic-embed2` + cosine** — ASSUMPTION CONFIRMED. Model default is
   `snowflake-arctic-embed2` (1024-dim, 8K ctx; `embeddings.py:57-59`,
   `config.py:52-55`); Qdrant distance is hardcoded `COSINE` (`vectorstore.py:186`).
4. **Embedding = text→vector call** — CONFIRMED via `embed()`/`embed_many()`, BUT the
   brain-dump omits the **`is_query="query: " prefix` asymmetry** (`embeddings.py:204,
   257`). Queries must be embedded with `is_query=True`, documents without, to match
   retrieval quality.
5. **Async reuse (second-brain is async)** — ASSUMPTION implicit. REALITY: the entire
   engine is **synchronous/blocking** (no `async def` anywhere in these modules).
   Calls must be wrapped (`asyncio.to_thread` / executor) to avoid blocking the
   FastAPI event loop.
6. **Vector store target** — REALITY: `QdrantStore(url=...)` talks to a running Qdrant
   server; `QdrantStore(path=...)` uses embedded single-process Qdrant with a storage
   lock (`vectorstore.py:164-169, 315-317`). A shared server requires `url=`.

---

## Blockers / risks for library reuse

- **Not published to PyPI.** Install is via git/pipx (`README.md:96-108`); homepage is
  a GitHub repo (`pyproject.toml:56-57`). Reuse options: git dependency, local path
  dependency, or vendor the four modules. **License is MIT (`pyproject.toml:10`) —
  no legal blocker.**
- **Heavy transitive dependencies if installed as a package.** `pyproject.toml:26-39`
  pins `docling`, `chromadb`, `fastmcp`, `networkx`, `pypdf`, `qdrant-client`,
  `ollama`. Installing the whole package pulls Docling (large) even if second-brain
  only needs embeddings + Qdrant. At *import* time only `ollama` and `qdrant-client`
  are eagerly imported (`embeddings.py:9`, `vectorstore.py:11`); Docling/Chroma are
  lazy. Vendoring only `parser.py`/`chunking.py`/`embeddings.py`/`vectorstore.py`
  (+`config.py`) avoids the Docling/Chroma/graph weight.
- **Sync-only engine** vs async second-brain — must offload to a thread pool.
- **`graph` package coupling** in the high-level ingest path: `IngestionPipeline.ingest`
  with `force=True` imports `graph.graph_builder`/`graph.graph_store`
  (`ingest.py:293-294, 313-314`), a *separate* top-level package (`src/graph`).
  Vendoring only `grounded_code_mcp` breaks the force path. The primitive-composition
  path avoids this entirely.
- **Non-deterministic point IDs.** `generate_chunk_id` returns random UUID4 and
  ignores source_path/index (`chunking.py:44-61`); re-ingest creates new IDs. Idempotent
  updates depend on the manifest deleting old `chunk_ids` first — not on stable IDs.
- **TOML-only config, no env vars** (`config.py`, ARCHITECTURE.md:111). Second-brain
  must construct `Settings`/sub-settings objects in code or ship a TOML file.
- **MCP server globals are irrelevant to library reuse but note the boundary:**
  `server.py` holds module-level `mcp = FastMCP(...)` and lazy globals `_settings`,
  `_embedder`, `_manifest` initialized via `initialize()` under a lock
  (`server.py:67-104`). None of the four engine modules have import-time global state
  or side effects — importing them directly does NOT trigger the server singletons.
