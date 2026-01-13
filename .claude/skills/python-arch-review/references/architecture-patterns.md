# Architecture Patterns

## Core Philosophy

**Pragmatic over perfect.** Architecture serves the code, not the other way around.

## Selective Clean Architecture

Apply layers only where complexity justifies abstraction.

### Layer Decision Matrix

| Scenario | Recommended Structure |
|----------|----------------------|
| Simple CRUD, no business logic | Direct: Route → DB |
| Validation + simple transforms | 2-layer: Service → Repository |
| Complex domain rules, workflows | 3-layer: Use Case → Domain → Repository |
| External integrations + domain | Full: Ports/Adapters pattern |

### When to Add Layers

**Add a layer when:**
- You have 3+ places doing the same thing (Rule of Three)
- Testing requires mocking infrastructure
- Business rules exist independent of persistence
- Multiple entry points need same logic (API + CLI + queue)

**Don't add layers for:**
- "Future flexibility" 
- Single-use code paths
- Simple data passthrough
- Consistency with other modules (each module earns its complexity)

### Practical Example

```python
# ❌ Over-engineered for simple CRUD
class UserRepositoryInterface(Protocol): ...
class UserRepository(UserRepositoryInterface): ...
class UserService:
    def __init__(self, repo: UserRepositoryInterface): ...
class CreateUserUseCase:
    def __init__(self, service: UserService): ...

# ✓ Right-sized for simple CRUD
class UserRepository:
    def create(self, data: UserCreate) -> User:
        return db.users.insert(data.model_dump())

# ✓ Graduated to layers when complexity emerged
class UserService:
    """Added when: email verification, role assignment, audit logging needed"""
    def __init__(self, db: Database, email: EmailClient):
        self._db = db
        self._email = email
    
    def create(self, data: UserCreate) -> User:
        user = self._db.users.insert(data.model_dump())
        self._email.send_verification(user.email)
        audit.log("user_created", user.id)
        return user
```

## Strategic SOLID Principles

Apply SOLID where it prevents real problems, not hypothetical ones.

### Single Responsibility (SRP)

**Apply when:** A class changes for genuinely different reasons  
**Skip when:** "Responsibilities" are just different methods on coherent data

```python
# ❌ Over-applied SRP
class UserDataValidator: ...
class UserDataTransformer: ...
class UserDataPersister: ...
class UserDataNotifier: ...

# ✓ Pragmatic SRP - cohesive operations on User
class UserService:
    def create(self, data): ...  # validate + save + notify
    def update(self, id, data): ...
    def deactivate(self, id): ...
```

### Open/Closed (OCP)

**Apply when:** You have 3+ variants of behavior (Rule of Three)  
**Skip when:** Only 1-2 cases exist; `if/elif` is clearer

```python
# ✓ 2 cases: if/elif is fine
def calculate_discount(customer_type: str, amount: Decimal) -> Decimal:
    if customer_type == "premium":
        return amount * Decimal("0.2")
    elif customer_type == "standard":
        return amount * Decimal("0.1")
    return Decimal("0")

# ✓ 5+ discount types emerged: now Strategy pattern earns its place
class DiscountStrategy(Protocol):
    def calculate(self, amount: Decimal) -> Decimal: ...

STRATEGIES: dict[str, DiscountStrategy] = {
    "premium": PremiumDiscount(),
    "loyalty": LoyaltyDiscount(),
    # ... pattern justified by real variants
}
```

### Liskov Substitution (LSP)

**Always apply.** No exceptions — broken LSP causes runtime bugs.

```python
# ❌ LSP violation
class Bird:
    def fly(self) -> None: ...

class Penguin(Bird):
    def fly(self) -> None:
        raise NotImplementedError  # Breaks substitutability

# ✓ Correct modeling
class Bird: ...
class FlyingBird(Bird):
    def fly(self) -> None: ...
class Penguin(Bird): ...  # No fly method
```

### Interface Segregation (ISP)

**Apply when:** Clients implement methods they don't use  
**Skip when:** Interface is small (<5 methods) and cohesive

```python
# ✓ Small cohesive interface - no segregation needed
class Repository(Protocol):
    def get(self, id: str) -> Entity | None: ...
    def save(self, entity: Entity) -> None: ...
    def delete(self, id: str) -> None: ...

# ✓ Large interface split when clients diverge
class Readable(Protocol):
    def get(self, id: str) -> Entity | None: ...

class Writable(Protocol):
    def save(self, entity: Entity) -> None: ...
    def delete(self, id: str) -> None: ...
```

### Dependency Inversion (DIP)

**Apply when:** You need to swap implementations (test doubles, multiple providers)  
**Skip when:** Only one implementation will ever exist

```python
# ❌ Over-applied DIP
class ConfigLoaderInterface(Protocol): ...
class JsonConfigLoader(ConfigLoaderInterface): ...  # Only implementation ever

# ✓ DIP justified - multiple payment providers
class PaymentGateway(Protocol):
    def charge(self, amount: Decimal) -> PaymentResult: ...

class StripeGateway(PaymentGateway): ...
class PayPalGateway(PaymentGateway): ...
```

## Composition Over Inheritance

**Default to composition.** Use inheritance only for true "is-a" with shared behavior.

```python
# ❌ Inheritance for code reuse
class BaseService:
    def log(self, msg): ...
    def validate(self, data): ...

class UserService(BaseService): ...

# ✓ Composition
class UserService:
    def __init__(self, logger: Logger, validator: Validator):
        self._logger = logger
        self._validator = validator
```

## Module Boundaries

### When to Extract a Module

- 3+ files with tight coupling to each other, loose coupling to rest
- Clear domain boundary (payments, notifications, auth)
- Different deployment/scaling needs
- Separate team ownership

### Module Structure (when justified)

```
module_name/
├── __init__.py      # Public API only
├── service.py       # Entry point
├── models.py        # Domain types
├── repository.py    # Data access (if needed)
└── _internal/       # Implementation details
```

## Anti-Pattern Recognition

| Smell | Likely Over-Engineering | Right-Size Solution |
|-------|------------------------|---------------------|
| Interface with 1 implementation | Premature abstraction | Delete interface, use concrete class |
| Factory for single type | Unnecessary indirection | Direct instantiation |
| 5+ layers for CRUD | Architecture astronaut | Route → Service → DB |
| Dependency injection framework | Often overkill | Manual DI or simple container |
| Event bus for 2 subscribers | Premature decoupling | Direct function calls |
