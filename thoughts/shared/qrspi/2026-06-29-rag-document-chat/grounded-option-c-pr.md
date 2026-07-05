# build(deps): split engine into light core + optional extras

## Summary
Restructure packaging so the reusable RAG engine installs **without** the heavy,
role-specific dependencies. The base now carries only the engine core; Docling,
fastmcp, chromadb, and networkx move into opt-in extras.

## Motivation
The engine modules (`parser`, `chunking`, `embeddings`, `vectorstore`, `config`) only
import `ollama`, `qdrant-client`, and `pydantic` at import time — everything else is
lazy or role-specific. Keeping those heavy libs in the base forced every consumer to
install the full stack. Making the base light lets other projects depend on the engine
as a library (single source of truth, no vendoring) while grounded's own tool install
opts into everything via `[all]`.

## What changed
- **`pyproject.toml`** — base slimmed to `ollama`, `qdrant-client`, `pydantic`, `tomli`
  (py<3.11). New extras:
  | extra | pulls | role |
  |---|---|---|
  | `parse` | docling, pypdf | binary-format ingestion |
  | `serve` | fastmcp, click, rich | MCP server + CLI |
  | `graph` | networkx | concept-graph force path |
  | `chroma` | chromadb | ChromaStore fallback (Qdrant is default) |
  | `all` | parse+serve+graph+chroma | full tool install |
  Also drops a duplicate `pypdf` line.
- **`ChromaStore` code retained** — only its dependency became opt-in.
- **CI (`ci.yml`, ×3)** and all install docs (`README`, `CONTRIBUTING`, `ARCHITECTURE`,
  `constraints`, `evals`, `CLAUDE`, `AGENTS`) updated to `.[all,dev]` / `[all]`.

## ⚠️ Breaking change / migration
Installing grounded-code-mcp **as the tool** now requires the `[all]` extra:
- `pipx install git+…` → `pipx install "grounded-code-mcp[all] @ git+…"`
- `pip install -e ".[dev]"` → `pip install -e ".[all,dev]"`
- `pipx install . --force` → `pipx install ".[all]" --force`

A bare install now yields only the importable engine core (intended for library reuse).
Suggest a **major version bump (2.1.0 → 3.0.0)**.

## Verification
- **Light-core proof:** fresh venv, base-only install pulls just `ollama + pydantic +
  qdrant-client`; all four primitives import **and construct** with
  docling/fastmcp/chromadb/networkx absent.
- **Full suite:** `pytest` → **518 passed in 10.25s** (no behavior change).
- `pyproject.toml` valid; `all` extra resolves to `[parse,serve,graph,chroma]`.

## Review notes
- The `all` extra uses a self-reference (`grounded-code-mcp[parse,serve,graph,chroma]`) —
  supported by pip ≥ 21.2.
- No runtime/source code changed — packaging + docs only.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
