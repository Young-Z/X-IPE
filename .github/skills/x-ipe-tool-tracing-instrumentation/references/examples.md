# Tracing Instrumentation Examples

## Example 1: Single File Instrumentation

### User Request
```
Add tracing to src/x_ipe/services/ideas_service.py
```

### Agent Analysis
```markdown
## Proposed Tracing Additions

### File: src/x_ipe/services/ideas_service.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `get_all_ideas()` | 25 | INFO | - | Add |
| `get_idea_by_id(id)` | 35 | INFO | - | Add |
| `create_idea(name, content)` | 48 | INFO | - | Add |
| `update_idea(id, data)` | 65 | INFO | - | Add |
| `delete_idea(id)` | 82 | INFO | - | Add |
| `_validate_idea_data(data)` | 95 | DEBUG | - | Add |
| `_sanitize_content(content)` | 108 | DEBUG | - | Add |

### Summary

| Metric | Count |
|--------|-------|
| Files analyzed | 1 |
| Total functions | 7 |
| To instrument | 7 |
| Already traced | 0 |

Proceed? [Yes/No]
```

### User Response
```
Yes
```

### Agent Action
1. Add import: `from x_ipe.tracing import x_ipe_tracing`
2. Add decorators to all 7 functions

### Result
```markdown
## Instrumentation Complete ✅

- Files modified: 1
- Functions instrumented: 7
- Import statements added: 1
```

---

## Example 2: Auth Service with Sensitive Params

### User Request
```
Add tracing to src/x_ipe/services/auth_service.py
```

### Agent Analysis
```markdown
## Proposed Tracing Additions

### File: src/x_ipe/services/auth_service.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `login(email, password)` | 20 | INFO | password | Add |
| `logout(session_id)` | 45 | INFO | - | Add |
| `validate_token(token)` | 60 | INFO | token | Add |
| `refresh_token(refresh_token)` | 78 | INFO | refresh_token | Add |
| `reset_password(user_id, new_password)` | 95 | INFO | new_password | Add |
| `_hash_password(password)` | 115 | DEBUG | password | Add |
| `_generate_token(user_id, secret_key)` | 125 | DEBUG | secret_key | Add |

### Summary

| Metric | Count |
|--------|-------|
| Functions with redaction | 6 |
| Total functions | 7 |

Proceed? [Yes/No]
```

### User Response
```
Yes
```

### Resulting Code
```python
from x_ipe.tracing import x_ipe_tracing

class AuthService:
    @x_ipe_tracing(level="INFO", redact=["password"])
    def login(self, email: str, password: str) -> dict:
        ...
    
    @x_ipe_tracing(level="INFO")
    def logout(self, session_id: str) -> bool:
        ...
    
    @x_ipe_tracing(level="INFO", redact=["token"])
    def validate_token(self, token: str) -> dict:
        ...
    
    @x_ipe_tracing(level="DEBUG", redact=["password"])
    def _hash_password(self, password: str) -> str:
        ...
```

---

## Example 3: Module Batch Processing

### User Request
```
Add tracing to src/x_ipe/routes/
```

### Agent Analysis
```markdown
## Proposed Tracing Additions

### File: src/x_ipe/routes/ideas_routes.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `list_ideas()` | 15 | INFO | - | Add |
| `get_idea(id)` | 28 | INFO | - | Add |
| `create_idea()` | 42 | INFO | - | Add |
| `update_idea(id)` | 58 | INFO | - | Add |
| `delete_idea(id)` | 72 | INFO | - | Add |

### File: src/x_ipe/routes/tracing_routes.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `get_status()` | 28 | INFO | - | Add |
| `start_tracing()` | 51 | INFO | - | Add |
| `stop_tracing()` | 83 | INFO | - | Add |
| `list_logs()` | 100 | INFO | - | Add |
| `delete_logs()` | 122 | INFO | - | Add |
| `get_trace(trace_id)` | 137 | INFO | - | Add |

### File: src/x_ipe/routes/health_routes.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `health_check()` | 10 | INFO | - | Add |
| `readiness()` | 18 | INFO | - | Add |

### Summary

| Metric | Count |
|--------|-------|
| Files analyzed | 3 |
| Total functions | 13 |
| To instrument | 13 |

Proceed? [Yes/No/Exclude specific]
```

### User Response
```
Exclude: health_check, readiness
```

### Agent Action
Skip health_routes.py functions, instrument remaining 11

### Result
```markdown
## Instrumentation Complete ✅

| Metric | Count |
|--------|-------|
| Files modified | 2 |
| Functions instrumented | 11 |
| Functions excluded | 2 |
```

---

## Example 4: Function Already Traced

### User Request
```
Add tracing to src/x_ipe/services/tracing_service.py
```

### Agent Analysis
```markdown
## Proposed Tracing Additions

### File: src/x_ipe/services/tracing_service.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `get_config()` | 50 | INFO | - | Add |
| `is_active()` | 71 | INFO | - | Add |
| `start(duration_minutes)` | 100 | - | - | Skip (already traced) |
| `stop()` | 125 | - | - | Skip (already traced) |
| `list_logs()` | 141 | INFO | - | Add |
| `cleanup_on_startup()` | 178 | INFO | - | Add |
| `get_trace(trace_id)` | 221 | INFO | - | Add |

### Summary

| Metric | Count |
|--------|-------|
| To instrument | 5 |
| Already traced | 2 |

Proceed? [Yes/No]
```

---

## Example 5: Dry Run Mode

### User Request
```
Add tracing to src/x_ipe/services/ --dry-run
```

### Agent Analysis
Shows proposal as normal, but ends with:

```markdown
### Dry Run Mode

No changes were made. This was a preview of proposed instrumentation.

To apply changes, run without `--dry-run` flag.
```

---

## Common Patterns

### Pattern: Route Files
- All functions get `level="INFO"` (public API endpoints)
- Check for auth-related params

### Pattern: Service Files  
- Public methods: `level="INFO"`
- Protected methods (`_prefix`): `level="DEBUG"`
- Always check for sensitive params

### Pattern: Utils/Helpers
- Default to `level="DEBUG"` (internal details)
- Lower priority for tracing

### Pattern: Class Methods
- Trace instance methods normally
- Skip `__init__`, `__str__`, `__repr__` etc.
- Include `@staticmethod` and `@classmethod`
