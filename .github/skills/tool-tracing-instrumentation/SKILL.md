---
name: tool-tracing-instrumentation
description: Add @x_ipe_tracing decorators to Python functions. Analyzes code, suggests levels (INFO/DEBUG), detects sensitive params for redaction, and applies decorators in batch. Triggers on "add tracing to", "instrument for tracing", "trace functions in".
---

# Tool: Tracing Instrumentation

## Purpose

Automatically instrument Python code with `@x_ipe_tracing` decorators by:
1. Analyzing target file(s) for traceable functions
2. Assigning appropriate tracing levels (INFO/DEBUG)
3. Detecting sensitive parameters for redaction
4. Proposing changes for human review
5. Applying decorators to approved functions

---

## Trigger Patterns

Use this skill when human asks to:
- "add tracing to {file/module}"
- "instrument {file/module} for tracing"
- "add @x_ipe_tracing to {file}"
- "trace all functions in {path}"
- "add tracing decorators to {path}"

---

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| target | string | Required | File path or directory to instrument |
| level | string | "auto" | Force level: "INFO", "DEBUG", or "auto" (recommended) |
| include_private | bool | false | Include `_prefixed` functions |
| dry_run | bool | false | Only show proposed changes, don't apply |

---

## Execution Procedure

### Step 1: Validate Target

1. **Verify target path exists**
   - If file: validate `.py` extension
   - If directory: find all `.py` files recursively

2. **Exclude patterns:**
   - `__pycache__/`
   - `.venv/`, `venv/`, `env/`
   - `test_*.py`, `*_test.py` (test files)
   - `conftest.py`

3. **Report scope:**
   ```
   Found X Python files in {target}
   ```

---

### Step 2: Analyze Each File

For each Python file, use Python AST to extract functions:

```python
import ast

with open(filepath) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # Process function
```

**For each function, check:**

1. **Already traced?**
   - Look for `@x_ipe_tracing` in decorators
   - If found → mark as "already traced", skip

2. **Dunder method?**
   - Name starts/ends with `__` (e.g., `__init__`, `__str__`)
   - → Skip (don't trace dunder methods)

3. **Private function?**
   - Name starts with `_` but not `__`
   - If `include_private=false` → Skip
   - If `include_private=true` → Include with DEBUG level

4. **Extract metadata:**
   - Function name
   - Parameters (names and type hints if available)
   - Line number
   - Is async (AsyncFunctionDef)
   - Existing decorators

---

### Step 3: Determine Level

Apply rules in priority order:

| Priority | Condition | Level |
|----------|-----------|-------|
| 1 | Explicit `level` parameter != "auto" | Use explicit level |
| 2 | File in `routes/` or `api/` directory | INFO |
| 3 | Class name ends with `Service`, `Handler`, `Controller` | INFO |
| 4 | Function is public (no underscore prefix) | INFO |
| 5 | Function in `utils/`, `helpers/`, `internal/` directory | DEBUG |
| 6 | Protected function (`_prefix`) | DEBUG |
| 7 | Default fallback | INFO |

---

### Step 4: Detect Sensitive Parameters

Check each parameter name against these patterns:

**Exact matches (case-insensitive):**
```
password, pwd, passwd, pass
secret, secret_key, secretkey
token, auth_token, api_token, access_token, refresh_token
key, api_key, apikey, private_key, privatekey
auth, authorization
credential, cred, credentials
ssn, social_security
pin, cvv, card_number
```

**Suffix patterns:**
```
*_password, *_pwd
*_secret, *_key
*_token, *_auth
*_credential
```

**If match found:**
- Add parameter to `redact=["param_name"]` list
- Note: Built-in Redactor already handles these, but explicit is clearer

---

### Step 5: Present Proposal

Format output as markdown table:

```markdown
## Proposed Tracing Additions

### File: src/x_ipe/services/ideas_service.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `get_all_ideas()` | 25 | INFO | - | Add |
| `create_idea(name, content)` | 42 | INFO | - | Add |
| `_validate_idea(data)` | 85 | DEBUG | - | Add |
| `update_idea(id, data)` | 58 | INFO | - | Add |
| `delete_idea(id)` | 72 | INFO | - | Add |

### File: src/x_ipe/services/auth_service.py

| Function | Line | Level | Redact | Action |
|----------|------|-------|--------|--------|
| `login(email, password)` | 15 | INFO | password | Add |
| `validate_token(token)` | 35 | INFO | token | Add |
| `already_traced()` | 50 | - | - | Skip (already traced) |

---

### Summary

| Metric | Count |
|--------|-------|
| Files analyzed | 2 |
| Total functions | 8 |
| To instrument | 7 |
| Already traced | 1 |
| Excluded (dunder/private) | 0 |

---

**Proceed with applying decorators?**
- Reply "Yes" to apply all
- Reply "Exclude: function1, function2" to skip specific functions
- Reply "No" to cancel
```

---

### Step 6: Apply Decorators

After human approval:

#### 6.1 Add Import (if missing)

Check file for existing import:
```python
from x_ipe.tracing import x_ipe_tracing
```

If not present, add after other imports (before first function/class).

#### 6.2 Add Decorator to Each Function

**Simple case (no redaction):**
```python
@x_ipe_tracing(level="INFO")
def my_function():
    pass
```

**With redaction:**
```python
@x_ipe_tracing(level="INFO", redact=["password", "token"])
def login(email, password, token):
    pass
```

#### 6.3 Preserve Decorator Order

When function has existing decorators, add `@x_ipe_tracing` first (outermost):

```python
# Before
@staticmethod
def my_function():
    pass

# After
@x_ipe_tracing(level="INFO")
@staticmethod
def my_function():
    pass
```

#### 6.4 Handle Async Functions

Same syntax works for async:
```python
@x_ipe_tracing(level="INFO")
async def async_function():
    pass
```

---

### Step 7: Report Results

After applying:

```markdown
## Instrumentation Complete ✅

### Summary

| Metric | Count |
|--------|-------|
| Files modified | 2 |
| Functions instrumented | 7 |
| Import statements added | 1 |
| With redaction | 2 |

### Changes Applied

| File | Functions | Notes |
|------|-----------|-------|
| `ideas_service.py` | 5 | - |
| `auth_service.py` | 2 | Added redaction for password, token |

### Next Steps

1. Run tests: `pytest tests/`
2. Start tracing: Use Tracing Dashboard or API
3. View traces: Check `instance/traces/` for logs
```

---

## Edge Cases

### EC-1: Already Traced Function
```python
# Input
@x_ipe_tracing(level="DEBUG")
def my_function():
    pass

# Action: SKIP
# Report: "already traced"
```

### EC-2: Multiple Decorators
```python
# Input
@validate_input
@authorize
def my_function():
    pass

# Output (add tracing first)
@x_ipe_tracing(level="INFO")
@validate_input
@authorize
def my_function():
    pass
```

### EC-3: Class with Methods
```python
# Input
class MyService:
    def process(self, data):
        pass

# Output
class MyService:
    @x_ipe_tracing(level="INFO")
    def process(self, data):
        pass
```

### EC-4: Empty File / No Functions
```
Report: "No traceable functions found in {filepath}"
```

### EC-5: Syntax Error in File
```
Report: "Error parsing {filepath}: {error}"
Skip file, continue with others
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Trace `__init__` | Noisy, rarely useful | Skip all dunder methods |
| Trace test files | Tests shouldn't be traced | Exclude `test_*.py` |
| Force all INFO | DEBUG floods production logs | Use auto level assignment |
| Skip redaction check | Security risk | Always detect sensitive params |
| Modify without approval | Unexpected changes | Always show proposal first |

---

## Definition of Done

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Target path validated | Yes |
| 2 | Files analyzed with AST | Yes |
| 3 | Levels assigned per rules | Yes |
| 4 | Sensitive params detected | Yes |
| 5 | Proposal shown to human | Yes |
| 6 | Human approved changes | Yes |
| 7 | Decorators applied correctly | Yes |
| 8 | Imports added if needed | Yes |
| 9 | Results reported | Yes |

---

## Examples

See [references/examples.md](references/examples.md) for detailed examples including:
- Single file instrumentation
- Module/directory batch processing
- Auth service with sensitive params
- Excluding specific functions
