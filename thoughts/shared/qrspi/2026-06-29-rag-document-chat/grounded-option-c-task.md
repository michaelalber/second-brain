---
task: grounded-code-mcp — Option C packaging restructure (light core + extras)
repo: grounded-code-mcp  (/home/malber/AppDev/michaelalber/codeberg/grounded-code-mcp)
blocks: second-brain rag-document-chat /qrspi-plan
status: done-merged             # PR #1 merged into main; pin = 91021cae; /qrspi-plan prerequisite CLEARED
created: 2026-07-04
rationale: decision 9 of ../spec.md — make grounded's engine a light, DRY-preserving git dependency
---

# Option C — grounded-code-mcp packaging restructure

## Goal
Make the four-primitive engine (`parser`/`chunking`/`embeddings`/`vectorstore`/`config`) installable
with **only** `ollama + qdrant-client + pydantic` so second-brain can git-dep the light core (DRY, no
vendoring). Push Docling/fastmcp/chromadb/networkx into optional extras.

## Verified scoping (2026-07-04)
- **Core top-level imports only:** `ollama` (embeddings.py:9), `qdrant-client` (vectorstore.py:11),
  `pydantic` (config.py:9), `tempfile` (parser.py). Everything else is lazy or non-core:
  - `chromadb` — lazy inside `ChromaStore.__init__` (vectorstore.py:329)
  - `docling`/`pypdf` — lazy inside `DocumentParser` methods (parser role, runtime-only)
  - `fastmcp` — only `server.py` (serve role); `click`/`rich` — only `__main__`/CLI
  - `networkx` — only the `graph` force path
- **Only test touching Chroma:** `tests/test_vectorstore.py`.
- **CI** installs `.[dev]` and runs the full pytest suite (`ci.yml:44,69,96`) → must install the full
  set or imports fail.
- **README** install: `pipx install git+…` (99), `pip install -e ".[dev]"` (107),
  `pipx install . --force` (411).

## Proposed pyproject.toml
Light base + role-based extras (keep `dev`; add `all` convenience):

```toml
dependencies = [
    "ollama",
    "qdrant-client",
    "pydantic>=2.0",
    "tomli; python_version < '3.11'",
]

[project.optional-dependencies]
parse  = ["docling>=2.70.0", "pypdf>=4.0"]   # binary-format parsing (ingest role)
serve  = ["fastmcp>=3.2.0", "click>=8.0", "rich>=13.0"]  # MCP server + CLI (grounded's own product)
graph  = ["networkx>=3.2"]                   # graph force path
chroma = ["chromadb>=1.0.0"]                 # ChromaStore fallback (Docker-free)
all    = ["grounded-code-mcp[parse,serve,graph,chroma]"]
dev    = ["pytest>=8.0", "pytest-asyncio", "pytest-cov", "ruff", "mypy", "bandit[toml]", "pip-audit"]
```
(Also drops the duplicate `pypdf` line in the current base.)

## ChromaStore disposition — DECISION
**Recommend: keep `ChromaStore` code, move `chromadb` to the `[chroma]` extra.** Least destructive,
preserves the public tool's Docker-free fallback, still removes it from the light core install (lazy
import already). "Drop entirely" is a later cleanup if it proves unused (rule of three).

## Blast radius (files to change)
1. `pyproject.toml` — base → light; add extras.
2. `.github/workflows/ci.yml` — `pip install -e ".[dev]"` → `".[all,dev]"` (×3: lint/test/mypy jobs).
3. `README.md` — install lines 99/107/411 → `[all]` form
   (`pipx install "grounded-code-mcp[all] @ git+https://github.com/michaelalber/grounded-code-mcp.git"`,
   `pip install -e ".[all,dev]"`, `pipx install ".[all]" --force`).
4. Skill/CONTRIBUTING install docs if they hardcode the bare install (grep before editing).
5. Pin the exact commit that second-brain will depend on.

## Verification (the Option C proof)
- **Light-core import proof (the key eval):** fresh venv → `pip install -e .` (base only) →
  `python -c "from grounded_code_mcp.parser import DocumentParser; from grounded_code_mcp.chunking import DocumentChunker; from grounded_code_mcp.embeddings import EmbeddingClient; from grounded_code_mcp.vectorstore import QdrantStore"`
  must succeed with docling/fastmcp/chromadb/networkx **absent**. Confirms the light dep set is correct.
- **Full-suite green:** `pip install -e ".[all,dev]"` → `pytest` green (unchanged behavior; Chroma test
  still runs because `[all]` includes `[chroma]`).
- Do **not** commit until human review (global git rule).

## Execution result (2026-07-04)
Approved: go + keep Chroma as opt-in `[chroma]` extra (code retained).
Changed (9 files, uncommitted): `pyproject.toml` (light base + extras), `.github/workflows/ci.yml`
(×3 → `.[all,dev]`), `README.md`, `CONTRIBUTING.md`, `constraints.md`, `evals.md`, `ARCHITECTURE.md`,
`CLAUDE.md`, `AGENTS.md` (all install commands → `[all]`/`[all,dev]`).
- **Light-core proof PASSED:** fresh venv, `pip install -e .` (base only) installs just
  `ollama + pydantic + qdrant-client`; all four primitives import + construct with
  docling/fastmcp/chromadb/networkx **absent**.
- **pyproject validated:** base carries no heavy dep; `all = [parse,serve,graph,chroma]` resolves.
- **Full suite GREEN:** `.venv/bin/pytest` → **518 passed in 10.25s** (existing dev venv already had
  the full stack; suite is fully mocked, no live services needed). Confirms the packaging change broke
  nothing.
- **Committed + pushed** on branch `build/engine-light-core-extras`, commit
  `789c100dff6fbb1da13d877df86f3038b8e6093e` (breaking: install now needs `[all]`).
  PR #1 (open): https://codeberg.org/michaelkalber/grounded-code-mcp/pulls/1
- **MERGED (merge-commit style) into `main` 2026-07-04.** main HEAD =
  `91021cae2e300378032471bfc63059a45cb3fb65`. Local main fast-forwarded to match origin.
- **PIN for second-brain:**
  `grounded-code-mcp @ git+ssh://git@codeberg.org/michaelkalber/grounded-code-mcp.git@91021cae2e300378032471bfc63059a45cb3fb65`
  (add `[parse]` on the PC ingest box for Docling; serve box needs no extras).
- **`/qrspi-plan` prerequisite CLEARED.**
- Housekeeping left: delete the merged `build/engine-light-core-extras` branch (local + remote) — optional.
