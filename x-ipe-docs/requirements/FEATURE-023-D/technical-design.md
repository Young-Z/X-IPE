# Technical Design: Tracing Skill Integration

> Feature ID: FEATURE-023-D | Version: v1.0 | Last Updated: 2026-02-01

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `x-ipe-tool-tracing-instrumentation` | Skill for adding tracing decorators | `.github/skills/` | #skill #tracing #instrumentation |
| `TracingAnalyzer` | Analyze Python files for traceable functions | Backend utility | #analyzer #python #ast |
| `SensitiveParamDetector` | Detect parameters that need redaction | Backend utility | #security #redaction |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `@x_ipe_tracing` | FEATURE-023-A | [technical-design.md](../FEATURE-023-A/technical-design.md) | Decorator to apply to functions |
| `Redactor.SENSITIVE_KEY_PATTERNS` | FEATURE-023-A | [redactor.py](../../../src/x_ipe/tracing/redactor.py) | Reference patterns for detection |

### Major Flow

1. User invokes skill: "Add tracing to {target}"
2. Skill analyzes Python files → identifies traceable functions
3. Skill proposes changes (function, level, redact params)
4. Human approves/modifies
5. Skill applies decorators to code

### Usage Example

```markdown
User: "Add tracing to src/x_ipe/services/ideas_service.py"

Skill Output:
## Proposed Tracing Additions

| Function | Level | Redact | Action |
|----------|-------|--------|--------|
| `get_all_ideas()` | INFO | - | Add |
| `create_idea()` | INFO | - | Add |
| `_validate_idea()` | DEBUG | - | Add |

Proceed? [Yes/No]

User: "Yes"

Agent applies decorators...
```

---

## Part 2: Implementation Guide

> **Purpose:** Human-readable details for developers.

### Skill Structure

```
.github/skills/x-ipe-tool-tracing-instrumentation/
├── SKILL.md           # Main skill definition
└── references/
    └── examples.md    # Usage examples
```

### Skill Definition (SKILL.md)

```markdown
---
name: x-ipe-tool-tracing-instrumentation
description: Add @x_ipe_tracing decorators to Python functions. Analyzes code, 
  suggests levels (INFO/DEBUG), detects sensitive params for redaction, and 
  applies decorators in batch. Triggers on "add tracing to", "instrument for tracing".
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

- "add tracing to {file/module}"
- "instrument {file/module} for tracing"
- "add @x_ipe_tracing to {file}"
- "trace all functions in {path}"

---

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| target | string | Required | File path or directory to instrument |
| level | string | "auto" | Force level: "INFO", "DEBUG", or "auto" |
| include_private | bool | false | Include `_prefixed` functions |
| dry_run | bool | false | Only show proposed changes, don't apply |

---

## Execution Procedure

### Step 1: Validate Target

1. Verify target path exists
2. If directory, find all `.py` files recursively
3. Exclude `__pycache__`, `.venv`, `test_*.py`

### Step 2: Analyze Each File

For each Python file:
1. Parse with Python AST
2. Find all function definitions (def, async def)
3. For each function:
   - Check if already has `@x_ipe_tracing` → skip
   - Check if dunder method (`__init__`) → skip
   - Determine level based on rules (see Level Assignment)
   - Detect sensitive params (see Sensitive Detection)
   - Add to proposal list

### Step 3: Determine Level

Apply these rules in order:

| Rule | Level | Description |
|------|-------|-------------|
| Explicit override | {level} | If level parameter != "auto" |
| Route function | INFO | Function in `routes/` or `api/` directory |
| Service method | INFO | Method in class ending with `Service` |
| Public function | INFO | No underscore prefix |
| Protected function | DEBUG | Single underscore prefix `_func` |
| Utils/helpers | DEBUG | Function in `utils/` or `helpers/` dir |

### Step 4: Detect Sensitive Parameters

Check each parameter name against:

```python
SENSITIVE_PATTERNS = {
    "password", "pwd", "passwd",
    "secret", "secret_key",
    "token", "auth_token", "api_token",
    "key", "api_key", "apikey", "private_key",
    "auth", "authorization",
    "credential", "cred", "credentials",
    "ssn", "social_security",
}

# Also check suffixes
SENSITIVE_SUFFIXES = ["_key", "_token", "_secret", "_password", "_auth"]
```

If match → add to `redact=["param_name"]`

### Step 5: Present Proposal

Output in table format:

```markdown
## Proposed Tracing Additions

### File: {filepath}

| Function | Level | Redact | Action |
|----------|-------|--------|--------|
| `function_name(param1, param2)` | INFO | param2 | Add |
| `other_function()` | DEBUG | - | Add |
| `already_traced()` | - | - | Skip (already traced) |

### Summary
- Total functions: X
- To instrument: Y
- Already traced: Z
- Excluded (private/dunder): W

**Proceed with applying decorators?** [Yes/No/Exclude specific]
```

### Step 6: Apply Decorators

For each approved function:

1. Check if import exists: `from x_ipe.tracing import x_ipe_tracing`
   - If not, add after other imports
2. Add decorator before function:
   ```python
   @x_ipe_tracing(level="INFO")  # or with redact
   @x_ipe_tracing(level="INFO", redact=["password"])
   ```
3. Preserve existing decorators (add tracing first in stack)

### Step 7: Report Results

```markdown
## Instrumentation Complete

- Files modified: X
- Functions instrumented: Y
- Import statements added: Z

### Changes Applied
- `ideas_service.py`: 4 functions
- `auth_service.py`: 3 functions (with redaction)
```

---

## Edge Cases

### Already Traced
```python
# Before
@x_ipe_tracing(level="INFO")
def my_function():
    pass

# Result: SKIP (report as "already traced")
```

### Multiple Decorators
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

### Class Methods
```python
# Before
class MyService:
    def process(self, data):
        pass

# After
class MyService:
    @x_ipe_tracing(level="INFO")
    def process(self, data):
        pass
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Trace `__init__` | Noisy, rarely useful | Skip dunder methods |
| Trace test functions | Test code shouldn't be traced | Exclude `test_*.py` |
| Force all to INFO | DEBUG floods logs | Use level auto-assignment |
| Skip redaction | Security risk | Always check for sensitive params |

---

## Examples

### Example 1: Simple File
```
User: "Add tracing to src/x_ipe/services/ideas_service.py"

1. Analyze → 5 functions found
2. Propose:
   - get_all_ideas() → INFO
   - create_idea() → INFO  
   - update_idea() → INFO
   - delete_idea() → INFO
   - _validate_idea() → DEBUG
3. Human: "Yes"
4. Apply decorators + add import
```

### Example 2: Auth Service with Redaction
```
User: "Add tracing to auth_service.py"

1. Analyze → 3 functions
2. Propose:
   - login(email, password) → INFO, redact=["password"]
   - validate_token(token) → INFO, redact=["token"]
   - logout(session_id) → INFO
3. Human: "Yes"
4. Apply with redaction
```

### Example 3: Entire Module
```
User: "Add tracing to src/x_ipe/routes/"

1. Find: 6 Python files
2. Analyze: 28 functions total
3. Propose: 24 to instrument, 4 already traced
4. Human reviews, excludes health_routes.py
5. Apply to 22 functions
```
```

---

## Implementation Steps

### Step 1: Create Skill Folder

```bash
mkdir -p .github/skills/x-ipe-tool-tracing-instrumentation/references
```

### Step 2: Create SKILL.md

Create the skill definition file with:
- Trigger patterns
- Execution procedure
- Level assignment rules
- Sensitive param detection
- Output format

### Step 3: Create Examples

Add `references/examples.md` with:
- Simple file instrumentation
- Module batch instrumentation
- Auth service with redaction
- Excluding specific functions

### Step 4: Test Skill Manually

1. Ask agent: "Add tracing to src/x_ipe/services/ideas_service.py"
2. Verify proposal format
3. Approve and verify decorators applied correctly

---

## File Changes Summary

| File | Change Type | Lines |
|------|-------------|-------|
| `.github/skills/x-ipe-tool-tracing-instrumentation/SKILL.md` | Create | ~200 |
| `.github/skills/x-ipe-tool-tracing-instrumentation/references/examples.md` | Create | ~100 |

**Total new lines:** ~300

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 2026-02-01 | Initial Design | Initial technical design for tracing skill. Skill-only implementation (no Python utility needed - agent uses AST analysis directly). |
| 2026-02-01 | Extension | Added skill integration updates - 5 existing skills updated with tracing checks (code-implementation, test-generation, code-refactor-v2, refactoring-analysis, x-ipe+feature+quality-board-management). Added x-ipe-tool-tracing-creator skill for project setup. |

---

## Part 3: Skill Integration Updates

> **Purpose:** Document updates to existing X-IPE skills for tracing enforcement.

### Skills Created

| Skill | Location | Purpose |
|-------|----------|---------|
| `x-ipe-tool-tracing-instrumentation` | `.github/skills/x-ipe-tool-tracing-instrumentation/` | Adds decorators to existing code |
| `x-ipe-tool-tracing-creator` | `.github/skills/x-ipe-tool-tracing-creator/` | Creates tracing infrastructure for projects |

### Skills Updated

| Skill | Section Updated | Changes |
|-------|----------------|---------|
| `x-ipe-task-based-code-implementation` | DoR | Added tracing utility check (6th checkpoint) |
| `x-ipe-task-based-code-implementation` | DoD | Added decorator requirement (checkpoints 10-11), tracing verification section |
| `x-ipe-task-based-test-generation` | DoD | Added tracing assertions requirement (checkpoint 9), test templates |
| `x-ipe-task-based-code-refactor` | DoD | Added tracing preservation rules (checkpoints 10-11) |
| `x-ipe-task-based-refactoring-analysis` | Step 6 | Added Step 6b for tracing coverage evaluation |
| `x-ipe-task-based-refactoring-analysis` | Gap Types | Added tracing gap types: untraced, unredacted, wrong_level |
| `x-ipe+feature+quality-board-management` | Report Structure | Added Tracing Coverage Violations as 5th subsection |
| `x-ipe+feature+quality-board-management` | Rules | Added RULE 4 for tracing coverage evaluation |

### Execution Step Updates

Skills now include tracing instrumentation as explicit workflow steps:

| Skill | New Step | Description |
|-------|----------|-------------|
| `x-ipe-task-based-code-implementation` | Step 7 | Invoke `x-ipe-tool-tracing-instrumentation` on all implemented code |
| `x-ipe-task-based-test-generation` | Step 11 | Generate tracing-related tests (decorator presence, redaction) |
| `x-ipe-task-based-code-refactor` | Step 6 | Apply tracing to new/moved code, verify preservation |

### Updated File Locations

```
.github/skills/
├── x-ipe-tool-tracing-instrumentation/SKILL.md    # NEW
├── x-ipe-tool-tracing-creator/SKILL.md            # NEW
├── x-ipe-task-based-code-implementation/SKILL.md   # UPDATED (DoR, DoD, Step 7)
├── x-ipe-task-based-test-generation/SKILL.md       # UPDATED (DoD, Step 11)
├── x-ipe-task-based-code-refactor/SKILL.md      # UPDATED (DoD, Step 6)
├── x-ipe-task-based-refactoring-analysis/SKILL.md  # UPDATED (Step 6b, Gap Types)
└── x-ipe+feature+quality-board-management/SKILL.md # UPDATED (Report Structure, Rules)
```

### Tracing Quality Thresholds

| Metric | Threshold | Enforcement |
|--------|-----------|-------------|
| Public function coverage | ≥90% | Quality report, refactoring analysis |
| Sensitive param redaction | 100% | All sensitive params MUST have redact=[] |
| Level assignment | Consistent | API=INFO, Business=INFO, Utility=DEBUG |
