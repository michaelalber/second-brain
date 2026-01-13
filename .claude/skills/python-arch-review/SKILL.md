---
name: python-arch-review
description: Architecture review for Python 3 projects enforcing TDD (Red→Green→Refactor→Quality Check), YAGNI principles, and code quality gates. Use when (1) writing new Python code, (2) reviewing existing Python code, (3) refactoring Python modules, (4) adding tests to Python projects, or (5) checking code quality metrics. Integrates Ruff, mypy, and security scanning.
---

# Python Architecture Review

## TDD Workflow

Every code change follows: **Red → Green → Refactor → Quality Check**

1. **Red**: Write failing test first
2. **Green**: Minimal code to pass
3. **Refactor**: Clean up, no new functionality
4. **Quality Check**: Run full quality gate

```bash
# Run quality gate
scripts/quality_check.py <path>
```

## Test Standards

**Naming**: `test_should_<expected>_when_<condition>` or `test_<method>_<scenario>_<result>`

**Pattern**: Arrange-Act-Assert (one assertion per test, except related validations)

```python
def test_should_return_sum_when_two_positive_numbers():
    # Arrange
    calc = Calculator()
    
    # Act
    result = calc.add(2, 3)
    
    # Assert
    assert result == 5
```

## Quality Gates

| Metric | Target | Tool |
|--------|--------|------|
| Cyclomatic Complexity | Methods <10, Classes <20 | radon |
| Coverage | 80% business logic, 95% security-critical | pytest-cov |
| Maintainability Index | 70+ | radon |
| Code Duplication | <3% | pylint |

## Core Philosophy: Pragmatic Over Perfect

**Start simple, add complexity only when needed.**

### YAGNI Principles

- Start simple with direct implementations
- Add abstractions only when complexity demands (Rule of Three)
- Prefer composition over inheritance
- No abstractions for future "what-ifs"
- Refactor to add abstractions when patterns emerge

### Architecture Decision Flow

```
Is this a simple CRUD operation?
  → YES: Direct implementation, no layers
  → NO: Does it have complex business rules?
      → NO: Service + Repository (2 layers max)
      → YES: Consider Clean Architecture layers
```

See [references/architecture-patterns.md](references/architecture-patterns.md) for selective Clean Architecture and strategic SOLID guidance.

## Tool Integration

### Ruff (Lint + Format)

```bash
ruff check --fix .
ruff format .
```

See [references/ruff-config.md](references/ruff-config.md) for pyproject.toml config.

### mypy (Type Checking)

```bash
mypy --strict .
```

See [references/mypy-config.md](references/mypy-config.md) for strict config.

### Security

```bash
bandit -r src/
pip-audit
```

See [references/security-checklist.md](references/security-checklist.md) for OWASP checks.

## Review Workflow

1. **Pre-commit**: `scripts/quality_check.py` (blocks on failures)
2. **Code Review**: Check against [references/review-checklist.md](references/review-checklist.md)
3. **Merge**: All gates green, coverage met

## When to Skip Quality Checks

Never skip for production code. Acceptable for:
- Spike/prototype branches (labeled `spike/*`)
- Documentation-only changes
- CI/CD config changes
