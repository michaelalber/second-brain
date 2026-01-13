# Security Checklist

## Automated Tools

```bash
# Static analysis
bandit -r src/ -ll -ii

# Dependency audit
pip-audit --strict

# Secret scanning
detect-secrets scan --all-files
```

## pyproject.toml

```toml
[tool.bandit]
exclude_dirs = ["tests", "venv"]
skips = ["B101"]  # assert in tests only
targets = ["src"]

[tool.bandit.assert_used]
skips = ["*_test.py", "test_*.py"]
```

## OWASP Top 10 Python Checks

### A01: Broken Access Control
- [ ] Authorization checked at function entry
- [ ] No direct object references without validation
- [ ] RBAC/ABAC patterns used consistently

### A02: Cryptographic Failures
- [ ] No hardcoded secrets (use `python-dotenv` or secrets manager)
- [ ] `secrets` module for random generation (not `random`)
- [ ] TLS 1.2+ enforced for network calls

### A03: Injection
- [ ] Parameterized queries (SQLAlchemy, psycopg2 params)
- [ ] No `eval()`, `exec()`, or `__import__()` with user input
- [ ] subprocess with `shell=False`

```python
# Bad
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Good
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### A04: Insecure Design
- [ ] Input validation at boundaries
- [ ] Defense in depth (multiple validation layers)
- [ ] Fail-secure defaults

### A05: Security Misconfiguration
- [ ] `DEBUG = False` in production
- [ ] Secure headers configured
- [ ] Dependencies pinned with hashes

### A07: Authentication Failures
- [ ] Password hashing with `argon2-cffi` or `bcrypt`
- [ ] Session tokens with sufficient entropy
- [ ] Rate limiting on auth endpoints

### A08: Data Integrity Failures
- [ ] Signed/verified data from untrusted sources
- [ ] Integrity checks on deserialization

```python
# Bad - unsafe deserialization
import pickle
data = pickle.loads(untrusted_data)

# Good - use JSON or validated schema
import json
data = json.loads(untrusted_data)
schema.validate(data)
```

### A09: Logging Failures
- [ ] No PII/secrets in logs
- [ ] Structured logging with correlation IDs
- [ ] Audit trail for security events

### A10: SSRF
- [ ] URL validation before requests
- [ ] Allowlist for external domains
- [ ] No user-controlled redirects

## Coverage Requirements

Security-critical code requires **95% coverage**:
- Authentication/authorization modules
- Cryptographic operations
- Input validation
- Data access layers
