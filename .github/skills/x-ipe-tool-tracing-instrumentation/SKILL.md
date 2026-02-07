---
name: x-ipe-tool-tracing-instrumentation
description: Add @x_ipe_tracing decorators to Python functions. Analyzes code, suggests levels (INFO/DEBUG), detects sensitive params for redaction, and applies decorators in batch. Triggers on "add tracing to", "instrument for tracing", "trace functions in".
---

# Tool: Tracing Instrumentation

## Purpose

AI Agents follow this skill to instrument Python code with `@x_ipe_tracing` decorators to:
1. Analyze target file(s) for traceable functions using AST
2. Assign appropriate tracing levels (INFO/DEBUG) based on context
3. Detect sensitive parameters and configure redaction
4. Present proposals for human review before applying changes
5. Apply decorators and imports in batch after approval

---

## Important Notes

BLOCKING: Never apply decorators without presenting a proposal and receiving human approval first.
CRITICAL: Always check parameters against the sensitive-param patterns list. Sensitive data leaking into traces is a security risk.
CRITICAL: Add `@x_ipe_tracing` as the outermost decorator when other decorators exist.

---

## About

This tool automates adding `@x_ipe_tracing` decorators to Python functions. It uses Python AST parsing to discover functions, classify them by tracing level, detect parameters that need redaction, and apply changes surgically.

**Key Concepts:**
- **Tracing Level** - INFO for public/API functions, DEBUG for internal/utility functions
- **Redaction** - Automatic detection of sensitive parameter names (passwords, tokens, keys) to add `redact=[...]` to the decorator
- **Proposal-first** - All changes are shown as a markdown table for human review before any file modification

---

## When to Use

```yaml
triggers:
  - "add tracing to {file/module}"
  - "instrument {file/module} for tracing"
  - "add @x_ipe_tracing to {file}"
  - "trace all functions in {path}"
  - "add tracing decorators to {path}"

not_for:
  - "Configuring tracing runtime settings (use tracing dashboard)"
  - "Viewing or querying existing traces (use tracing API)"
```

---

## Input Parameters

```yaml
input:
  target: "string (required) - File path or directory to instrument"
  options:
    level: "string (default: 'auto') - Force level: INFO, DEBUG, or auto"
    include_private: "bool (default: false) - Include _prefixed functions"
    dry_run: "bool (default: false) - Only show proposed changes, do not apply"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Target path exists</name>
    <verification>Verify file (.py) or directory exists at specified path</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tracing module available</name>
    <verification>Confirm x_ipe.tracing module exists in the project</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Analyze and Propose

**When:** Human requests tracing instrumentation for a target path.

```xml
<operation name="analyze_and_propose">
  <action>
    1. Validate target path exists (file must be .py; directory: find .py files recursively)
    2. Exclude: __pycache__/, .venv/, venv/, env/, test_*.py, *_test.py, conftest.py
    3. Report scope: "Found X Python files in {target}"
    4. For each file, parse with Python AST to extract FunctionDef and AsyncFunctionDef nodes
    5. For each function:
       a. Skip if already has @x_ipe_tracing decorator
       b. Skip dunder methods (__init__, __str__, etc.)
       c. Skip _private functions unless include_private=true
       d. Extract: name, parameters (with type hints), line number, is_async, existing decorators
    6. Assign tracing level per priority rules:
       P1: Explicit level param != "auto" -> use that level
       P2: File in routes/ or api/ directory -> INFO
       P3: Class ends with Service, Handler, Controller -> INFO
       P4: Public function (no _ prefix) -> INFO
       P5: File in utils/, helpers/, internal/ -> DEBUG
       P6: Protected function (_prefix) -> DEBUG
       P7: Default fallback -> INFO
    7. Check each parameter name against sensitive patterns (see references/edge-cases.md)
       If match: add to redact=["param_name"] list
    8. Present proposal as markdown table with Function, Line, Level, Redact, Action columns
    9. Show summary (files analyzed, to instrument, already traced, excluded)
    10. Ask: "Proceed?" with options: Yes / Exclude: func1,func2 / No
  </action>
  <constraints>
    - BLOCKING: Do not modify any files during this operation
    - Always show proposal even in dry_run mode
  </constraints>
  <output>Markdown proposal table with per-function instrumentation plan</output>
</operation>
```

### Operation: Apply Decorators

**When:** Human approves the proposal (replies "Yes" or excludes specific functions).

```xml
<operation name="apply_decorators">
  <action>
    1. Remove any functions the human excluded from the approved list
    2. For each file with approved functions:
       a. Check for existing import: from x_ipe.tracing import x_ipe_tracing
       b. If missing, add import after other imports (before first function/class)
    3. For each approved function, add decorator:
       - No redaction: @x_ipe_tracing(level="{LEVEL}")
       - With redaction: @x_ipe_tracing(level="{LEVEL}", redact=["{param1}", "{param2}"])
    4. Place @x_ipe_tracing as outermost decorator (before any existing decorators)
    5. Async functions use the same decorator syntax
    6. Report results: files modified, functions instrumented, imports added, redactions applied
    7. Suggest next steps: run tests, start tracing, check trace logs
  </action>
  <constraints>
    - BLOCKING: Requires human approval from analyze_and_propose
    - Preserve existing decorator order (add tracing above them)
    - Skip if dry_run=true (report "No changes made, dry run only")
  </constraints>
  <output>Summary of applied changes with file-level breakdown</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    files_modified: 0
    functions_instrumented: 0
    imports_added: 0
    functions_with_redaction: 0
    functions_skipped_already_traced: 0
    functions_excluded: 0
  errors: []
  next_steps:
    - "Run tests: pytest tests/"
    - "Start tracing: Use Tracing Dashboard or API"
    - "View traces: Check instance/traces/ for logs"
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Target validated</name>
    <verification>Target path confirmed to exist with .py files</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>AST analysis complete</name>
    <verification>All files parsed, functions classified by level</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Sensitive params detected</name>
    <verification>All parameters checked against sensitive patterns</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Proposal shown and approved</name>
    <verification>Human reviewed and approved the proposal</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Decorators applied correctly</name>
    <verification>All approved functions have @x_ipe_tracing with correct level and redact params</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Imports added</name>
    <verification>Files with new decorators have the tracing import</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Results reported</name>
    <verification>Summary of changes provided to human</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Target path not found | Invalid file/directory path | Report error, ask human for correct path |
| Not a Python file | Target file lacks .py extension | Report error, skip file |
| AST parse failure | Syntax error in Python file | Report "Error parsing {filepath}: {error}", skip file, continue with others |
| No traceable functions | File has no eligible functions | Report "No traceable functions found in {filepath}" |
| Human declines proposal | Replied "No" | Cancel operation, no files modified |

---

## Templates

| File | Purpose |
|------|---------|
| `references/examples.md` | Detailed usage examples (single file, batch, auth, exclusions) |
| `references/edge-cases.md` | Edge cases, anti-patterns, and sensitive parameter patterns |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples including:
- Single file instrumentation
- Auth service with sensitive parameter redaction
- Module/directory batch processing
- Excluding specific functions from instrumentation
- Dry run mode
