# Code Review Checklist

## TDD Verification

- [ ] Tests written before implementation (check commit history)
- [ ] Test names follow `test_should_<expected>_when_<condition>`
- [ ] AAA pattern: clear Arrange/Act/Assert sections
- [ ] One assertion per test (except related validations)
- [ ] Edge cases covered

## YAGNI Check

- [ ] No speculative abstractions
- [ ] Interfaces justified by 3+ implementations (Rule of Three)
- [ ] No unused parameters or "future" placeholders
- [ ] Simplest solution that works

## Quality Gates

| Gate | Threshold | Pass? |
|------|-----------|-------|
| Cyclomatic Complexity | <10 per method | [ ] |
| Test Coverage | 80%+ (95% security) | [ ] |
| Maintainability Index | 70+ | [ ] |
| Code Duplication | <3% | [ ] |
| Ruff | Zero errors | [ ] |
| mypy --strict | Zero errors | [ ] |
| bandit | Zero high/medium | [ ] |

## Architecture (Pragmatic)

- [ ] Layer count justified by complexity (not convention)
- [ ] No interfaces with single implementation
- [ ] No factories for single types
- [ ] Abstractions earned by Rule of Three
- [ ] Composition used over inheritance (unless true "is-a")
- [ ] Module boundaries reflect real domain boundaries

## SOLID (Strategic)

- [ ] SRP: Class changes for genuinely different reasons (not just "different methods")
- [ ] OCP: Strategy/polymorphism only when 3+ variants exist
- [ ] LSP: Subtypes fully substitutable (always enforced)
- [ ] ISP: Interfaces split only when clients implement unused methods
- [ ] DIP: Abstractions only where swappable implementations exist

## Code Organization

- [ ] Dependencies flow inward (no infrastructure in domain)
- [ ] No circular imports
- [ ] Public API minimal and documented

## Type Safety

- [ ] All public functions typed
- [ ] `Optional` explicit, not implicit `None`
- [ ] Generics used where appropriate
- [ ] No `# type: ignore` without comment

## Error Handling

- [ ] Specific exceptions, not bare `except:`
- [ ] Errors logged with context
- [ ] Fail-fast in invalid states
- [ ] Resources cleaned up (context managers)

## Performance

- [ ] No N+1 queries
- [ ] Expensive operations lazy/cached
- [ ] Async where I/O bound
- [ ] Profiled if performance-critical
