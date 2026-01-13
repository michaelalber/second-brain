# mypy Configuration

## pyproject.toml

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true
show_error_codes = true
show_column_numbers = true
pretty = true

# Per-module overrides
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_untyped_decorators = false

[[tool.mypy.overrides]]
module = [
    "third_party_lib.*",
]
ignore_missing_imports = true
```

## Strict Mode Checklist

When `strict = true`, these are enforced:
- All functions have type annotations
- No `Any` without explicit annotation
- No implicit `Optional`
- No untyped decorators
- Return types required

## Common Patterns

### Protocols (Structural Typing)

```python
from typing import Protocol

class Repository(Protocol):
    def get(self, id: str) -> Entity | None: ...
    def save(self, entity: Entity) -> None: ...
```

### TypeVar for Generics

```python
from typing import TypeVar

T = TypeVar("T", bound="BaseModel")

def get_by_id(cls: type[T], id: str) -> T | None: ...
```

### Callable Types

```python
from collections.abc import Callable

Handler = Callable[[Request], Response]
```

## CI Integration

```yaml
- name: Type Check
  run: mypy --strict src/
```
