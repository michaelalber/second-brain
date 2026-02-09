# AGENTS.md

## Build/Lint/Test Commands

### Backend
```bash
# Run all tests
pytest

# Run single test
pytest -k <test_name>

# Test coverage
pytest --cov=app --cov-report=term-missing

# Lint
ruff check app/ tests/

# Type check
mypy app/

# Security scan
bandit -r app/ -c pyproject.toml
```

### Frontend
```bash
# Run all tests
npm run test

# Run single test
npm run test -- --grep <test_name>

# Lint
npm run lint

# Build
npm run build
```

## Code Style Guidelines

### Python (Backend)

**Imports:**
- Follow standard Python import ordering (stdlib, third-party, local)
- Separate groups with blank lines
- Prefer absolute imports

**Formatting:**
- Follow PEP 8 style guidelines
- Use Ruff for linting, formatting, and import sorting
- 4-space indentation

**Types:**
- Type hints on all function parameters and return types
- Use Pydantic models for all request/response schemas
- Use `Mapped[]` for SQLAlchemy 2.0 column definitions
- Use dataclasses for simple data containers

**Naming:**
- `snake_case` for variables/functions
- `PascalCase` for classes
- `UPPER_CASE` for constants

**Error Handling:**
- Use specific exception types, never bare `except:`
- Use `raise RuntimeError(...)` instead of bare `assert` for runtime checks (bandit S101)
- Provide helpful error messages
- Log errors using `logging`

**Documentation:**
- Google-style docstrings for all public functions and classes
- Include parameter descriptions with types
- Include return value descriptions

**Async:**
- Use `async/await` throughout - no sync database calls
- Services layer for business logic, routes stay thin

**Testing:**
- Arrange-Act-Assert pattern
- Use fixtures for test data setup
- Test business logic and edge cases
- Use `@pytest.mark.asyncio` for async tests

### TypeScript (Frontend)

**Imports:**
- Use relative paths
- Group imports by type (components, utilities, styles)

**Formatting:**
- Follow Prettier style (2 spaces, semi-colons)

**Types:**
- Define prop/emit types explicitly
- Use TypeScript interfaces for component props

**Naming:**
- `camelCase` for variables
- `PascalCase` for components
- `UPPER_SNAKE_CASE` for constants

**Composition API:**
- Use `<script setup lang="ts">` only
- Pinia stores: actions async, getters for derived state
- Define reusable logic in composables

## Development Principles

### TDD
1. **Never write production code without a failing test first**
2. Cycle: RED (write failing test) → GREEN (minimal code to pass) → REFACTOR
3. Run tests before committing: `pytest` (backend), `npm run test` (frontend)
4. Coverage targets: Backend 80%+, Frontend 70%+

### Security by Design (OWASP)
- Validate all inputs at system boundaries
- Use parameterized queries for all database operations
- Never trust client-side validation alone
- Sanitize filenames (remove path traversal, special chars)
- Follow OWASP guidelines for file handling, auth, and data protection
- Never commit secrets - use environment variables

### YAGNI (You Aren't Gonna Need It)
- No abstract interfaces until needed
- No dependency injection containers
- No plugin architecture
- Only apply abstractions after Rule of Three (3+ consumers)
- Add complexity only when justified by current requirements

### Quality Gates
- **Cyclomatic Complexity**: Methods <10, classes <20
- **Code Coverage**: 80% minimum for business logic (backend), 70% (frontend)
- **Maintainability Index**: Target 70+
- **Code Duplication**: Maximum 3%

## Git Workflow

- Commit after each GREEN phase
- Commit message format: `feat|fix|test|refactor: brief description`
- Don't commit failing tests (RED phase is local only)
- Use feature branches for new functionality
- Pull requests: include 1-3 bullet points summarizing changes

## Tools

- **Bash**: Use for running tests, linters, and formatters
- **Read/Write/Edit**: For file operations
- **Grep/Glob**: For code search
- **Task**: For complex, multi-step operations
- **Skill**: For TDD cycles and architecture reviews

## Example Workflow

1. Write a failing test for the new feature
2. Run `pytest -k <test_name>` to confirm it fails (RED)
3. Write minimal code to make the test pass (GREEN)
4. Run full test suite: `pytest`
5. Run linters: `ruff check app/ tests/ && mypy app/`
6. Refactor if needed while keeping tests green (REFACTOR)
7. Commit: `git commit -m "feat: <description>"`
