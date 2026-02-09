# AGENTS.md

## Build/Lint/Test Commands

### Backend
- **Run all tests**: `pytest` (colorized output)
- **Run single test**: `pytest -k <test_name>`
- **Test coverage**: `pytest --cov=app --cov-report=term-missing`
- **Type check**: `mypy app` (ensure Pydantic models are type-checked)
- **Format code**: `black app` (for Python files)
- **Lint**: `flake8 app` (check for style violations)

### Frontend
- **Run all tests**: `npm run test`
- **Run single test**: `npm run test -- --grep <test_name>`
- **Format code**: `prettier --write "src/**/*.ts" "src/**/*.vue"`
- **Lint**: `eslint --ext .ts,.vue src` (check for style violations)
- **Build**: `npm run build` (production build)

## Code Style Guidelines

### Python (Backend)
- **Imports**: Group standard library, third-party, and local imports. Use absolute imports.
- **Formatting**: Follow [Black](https://black.readthedocs.io/) style (4 spaces, no trailing spaces)
- **Types**: Use Pydantic models for request/response schemas. Annotate all function signatures.
- **Naming**: Use `snake_case` for variables, `PascalCase` for classes. Constants in `UPPER_SNAKE_CASE`.
- **Error Handling**: Use specific exceptions. Prefer `try/except` blocks with clear error messages. Log errors using `logging`.
- **Async**: Use `async/await` for I/O operations. Never mix sync and async code.

### TypeScript (Frontend)
- **Imports**: Use relative paths. Group imports by type (e.g., components, utilities, styles).
- **Formatting**: Follow [Prettier](https://prettier.io/) style (2 spaces, semi-colons)
- **Types**: Define prop/emit types explicitly. Use TypeScript interfaces for component props.
- **Naming**: Use `camelCase` for variables, `PascalCase` for components. Constants in `UPPER_SNAKE_CASE`.
- **Error Handling**: Use `try/catch` blocks. Use `console.error()` for debugging.
- **Composition API**: Use `<script setup>` only. Define reusable logic in composables.

## Additional Rules

### Cursor Rules
- If `.cursor/rules/` exists, follow its formatting and style guidelines.
- Ensure all code changes pass `cursor lint` and `cursor format`.

### Copilot Rules
- If `.github/copilot-instructions.md` exists, follow its instructions for AI-assisted coding.
- Disable Copilot for sensitive files (e.g., `.env`, `secrets.ts`)

## TDD Requirements
- **RED**: Write failing tests first (use `@pytest.mark.asyncio` for async tests)
- **GREEN**: Minimal code to make tests pass
- **REFACTOR**: Improve code structure while keeping tests green
- **Coverage**: Aim for 80%+ backend, 70%+ frontend

## Security
- **Never commit secrets**: Use environment variables or vaults for sensitive data
- **Input validation**: Sanitize all user inputs to prevent injection attacks
- **Permissions**: Use least privilege principles for file system and database access

## Git
- **Commit messages**: Use `feat|fix|test|refactor: brief description`
- **Branching**: Use feature branches for new functionality. Merge with `--no-ff` to preserve history
- **Pull requests**: Include 1-3 bullet points summarizing changes. Reference related issues

## Tools
- **Bash**: Use for running tests, linters, and formatters
- **Read/Write/Edit**: For file operations
- **Grep/Glob**: For code search
- **Task**: For complex, multi-step operations
- **Skill**: For TDD cycles and architecture reviews

## Example Workflow
1. Run `pytest -k <test_name>` to identify failing tests
2. Write minimal code to make tests pass
3. Run linters and formatters
4. Refactor code while keeping tests green
5. Commit with `git commit -m "fix: <description>"`
6. Push to remote and create PR with `gh pr create`