# Ruff Configuration

## pyproject.toml

```toml
[tool.ruff]
target-version = "py312"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate (commented code)
    "PL",     # Pylint
    "RUF",    # Ruff-specific
    "S",      # flake8-bandit (security)
    "A",      # flake8-builtins
    "COM",    # flake8-commas
    "C90",    # mccabe complexity
]
ignore = [
    "E501",   # line length (handled by formatter)
    "PLR0913", # too many arguments (use judgment)
]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pylint]
max-args = 5
max-branches = 10
max-statements = 50

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ARG001", "PLR2004"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true
```

## Key Rules

- **C90**: Cyclomatic complexity >10 fails
- **PL**: Pylint rules for code quality
- **S**: Security checks (bandit subset)
- **B**: Bug-prone patterns
- **SIM**: Simplification suggestions

## CI Integration

```yaml
- name: Lint
  run: |
    ruff check --output-format=github .
    ruff format --check .
```
