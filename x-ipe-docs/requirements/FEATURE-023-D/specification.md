# Feature Specification: Tracing Skill Integration

> Feature ID: FEATURE-023-D | Version: v1.1 | Last Updated: 2026-02-02

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.1 | 02-02-2026 | Updated AC status - skill implemented |
| v1.0 | 02-01-2026 | Initial specification |

---

## Overview

### Purpose

FEATURE-023-D provides an AI skill that automatically instruments Python code with `@x_ipe_tracing` decorators. The skill analyzes code structure, identifies traceable functions, suggests appropriate tracing levels, auto-detects sensitive parameters for redaction, and applies decorators in batch.

### Technical Scope

- [x] Skill Definition (`.github/skills/`)
- [x] Backend Python (utility functions)
- [ ] Frontend (N/A - skill only)
- [ ] API (N/A - skill instructions)

### Dependencies

| Dependency | Feature/Component | Description |
|------------|-------------------|-------------|
| `@x_ipe_tracing` decorator | FEATURE-023-A | Core tracing decorator to apply |
| `Redactor` patterns | FEATURE-023-A | Built-in sensitive field patterns |
| Skill execution framework | X-IPE Core | Skill loading and execution |

---

## User Stories

### US-1: Auto-Instrument Module
**As a** developer  
**I want to** ask the agent to add tracing to a Python module  
**So that** all functions in the module are traced without manual decorator placement

### US-2: Smart Level Assignment
**As a** developer  
**I want to** have the skill automatically assign INFO vs DEBUG levels  
**So that** public/service functions are INFO and internal helpers are DEBUG

### US-3: Sensitive Field Detection
**As a** developer  
**I want to** have the skill detect parameters like `password`, `token`, `secret`  
**So that** sensitive data is automatically redacted in traces

### US-4: Respect Existing Patterns
**As a** developer  
**I want to** have the skill respect existing decorators and skip already-traced functions  
**So that** I don't get duplicate decorators

### US-5: Batch Apply with Review
**As a** developer  
**I want to** review proposed tracing additions before they're applied  
**So that** I can exclude specific functions if needed

---

## Acceptance Criteria

### AC-1: Skill Definition

| # | Criterion | Required |
|---|-----------|----------|
| 1.1 | Skill file exists at `.github/skills/x-ipe-tool-tracing-instrumentation/SKILL.md` | Yes |
| 1.2 | Skill has clear trigger patterns (e.g., "add tracing to", "instrument for tracing") | Yes |
| 1.3 | Skill defines step-by-step execution procedure | Yes |
| 1.4 | Skill includes usage examples | Yes |

### AC-2: Code Analysis

| # | Criterion | Required |
|---|-----------|----------|
| 2.1 | Skill can analyze a single Python file for traceable functions | Yes |
| 2.2 | Skill can analyze a module/package (multiple files) | Yes |
| 2.3 | Skill identifies function signature (name, parameters, return type) | Yes |
| 2.4 | Skill detects async functions for proper decorator handling | Yes |
| 2.5 | Skill skips functions already decorated with `@x_ipe_tracing` | Yes |
| 2.6 | Skill skips private functions (`_name`) by default (configurable) | Yes |
| 2.7 | Skill skips dunder methods (`__init__`, `__str__`, etc.) | Yes |

### AC-3: Level Assignment

| # | Criterion | Required |
|---|-----------|----------|
| 3.1 | Public functions (no underscore prefix) default to `level="INFO"` | Yes |
| 3.2 | Protected functions (`_prefix`) default to `level="DEBUG"` | Yes |
| 3.3 | Functions in `routes/` or `api/` directories default to `level="INFO"` | Yes |
| 3.4 | Functions in `utils/` or `helpers/` directories default to `level="DEBUG"` | Yes |
| 3.5 | Override level can be specified in skill invocation | Yes |

### AC-4: Sensitive Parameter Detection

| # | Criterion | Required |
|---|-----------|----------|
| 4.1 | Skill detects common sensitive names: `password`, `token`, `secret`, `key`, `auth` | Yes |
| 4.2 | Skill detects sensitive names with suffixes: `api_key`, `auth_token`, `secret_key` | Yes |
| 4.3 | Skill detects credential patterns: `credential`, `cred`, `pwd` | Yes |
| 4.4 | Detected sensitive params are added to `redact=["param_name"]` list | Yes |
| 4.5 | Skill respects built-in Redactor patterns (doesn't duplicate) | Yes |

### AC-5: Decorator Application

| # | Criterion | Required |
|---|-----------|----------|
| 5.1 | Skill generates correct decorator syntax: `@x_ipe_tracing(level="INFO")` | Yes |
| 5.2 | Skill adds `from x_ipe.tracing import x_ipe_tracing` import if missing | Yes |
| 5.3 | Skill preserves existing decorators (adds tracing decorator first/last) | Yes |
| 5.4 | Skill handles multi-line decorator stacks correctly | Yes |
| 5.5 | Skill handles functions with docstrings correctly | Yes |

### AC-6: Batch Operations

| # | Criterion | Required |
|---|-----------|----------|
| 6.1 | Skill can process multiple files in a single invocation | Yes |
| 6.2 | Skill provides summary of proposed changes before applying | Yes |
| 6.3 | Human can exclude specific functions from batch | Yes |
| 6.4 | Skill reports success/failure count after application | Yes |

### AC-7: Configuration Respect

| # | Criterion | Required |
|---|-----------|----------|
| 7.1 | Skill reads tracing config from `tools.json` if present | Yes |
| 7.2 | Skill respects `tracing_ignored_apis` patterns | Yes |
| 7.3 | Skill can read custom config from `.x-ipe.yaml` tracing section | Optional |

---

## Edge Cases

### EC-1: Already Traced Functions
**Scenario:** Function already has `@x_ipe_tracing` decorator  
**Expected:** Skip function, report as "already traced"

### EC-2: Conflicting Decorators
**Scenario:** Function has decorators that may conflict (e.g., `@staticmethod`)  
**Expected:** Add `@x_ipe_tracing` before `@staticmethod` (decorator order matters)

### EC-3: No Functions in File
**Scenario:** Python file has only class definitions or no functions  
**Expected:** Report "no traceable functions found"

### EC-4: Import Already Exists
**Scenario:** File already imports `x_ipe_tracing`  
**Expected:** Don't add duplicate import

### EC-5: Relative vs Absolute Import
**Scenario:** Project uses relative imports  
**Expected:** Use project-appropriate import style

---

## AC-8: Skill Integration Updates (FEATURE-023-D Extension)

This section specifies updates to existing X-IPE skills to integrate tracing enforcement.

### AC-8.1: Code Implementation Skill Updates

| # | Criterion | Required |
|---|-----------|----------|
| 8.1.1 | DoR includes tracing utility check (tracing infrastructure exists) | Yes |
| 8.1.2 | DoR references `x-ipe-tool-tracing-creator` skill if tracing missing | Yes |
| 8.1.3 | DoD includes decorator requirement for all public functions | Yes |
| 8.1.4 | DoD includes sensitive parameter redaction check | Yes |
| 8.1.5 | DoD references `x-ipe-tool-tracing-instrumentation` skill for adding decorators | Yes |

### AC-8.2: Test Generation Skill Updates

| # | Criterion | Required |
|---|-----------|----------|
| 8.2.1 | DoD includes tracing assertions requirement | Yes |
| 8.2.2 | Skill provides tracing test templates (decorator check, context, redaction) | Yes |
| 8.2.3 | Examples include tests for `@x_ipe_tracing` decorator presence | Yes |
| 8.2.4 | Examples include tests for trace context propagation | Yes |
| 8.2.5 | Examples include tests for sensitive data redaction | Yes |

### AC-8.3: Code Refactor V2 Skill Updates

| # | Criterion | Required |
|---|-----------|----------|
| 8.3.1 | DoD includes "existing tracing preserved" check | Yes |
| 8.3.2 | DoD includes "new/moved code has decorators" check | Yes |
| 8.3.3 | Skill provides tracing preservation rules for move/split/rename | Yes |
| 8.3.4 | Skill references `x-ipe-tool-tracing-instrumentation` for adding to new code | Yes |

### AC-8.4: Refactoring Analysis Skill Updates

| # | Criterion | Required |
|---|-----------|----------|
| 8.4.1 | Adds tracing coverage as 5th quality perspective | Yes |
| 8.4.2 | Step 6b evaluates tracing decorator coverage percentage | Yes |
| 8.4.3 | Step 6b identifies untraced public functions | Yes |
| 8.4.4 | Step 6b checks sensitive parameter redaction | Yes |
| 8.4.5 | Gap types include: untraced, unredacted, wrong_level | Yes |

### AC-8.5: Project Quality Board Management Skill Updates

| # | Criterion | Required |
|---|-----------|----------|
| 8.5.1 | Violation Details includes Tracing Coverage Violations section | Yes |
| 8.5.2 | Report structure has 5 subsections per feature (not 4) | Yes |
| 8.5.3 | Tracing coverage threshold defined (≥90% public functions) | Yes |
| 8.5.4 | Report shows untraced functions list | Yes |
| 8.5.5 | Report shows unredacted sensitive params list | Yes |

---

## Skill Invocation Examples

### Example 1: Instrument Single File
```
User: "Add tracing to src/x_ipe/services/ideas_service.py"

Agent:
1. Analyzes file, finds 8 functions
2. Proposes:
   - `get_all_ideas()` → @x_ipe_tracing(level="INFO")
   - `create_idea()` → @x_ipe_tracing(level="INFO")
   - `_validate_idea()` → @x_ipe_tracing(level="DEBUG")
   ...
3. Human approves
4. Agent applies decorators
```

### Example 2: Instrument Module with Exclusions
```
User: "Add tracing to src/x_ipe/routes/ excluding health routes"

Agent:
1. Finds 5 route files, 24 functions
2. Proposes changes (excludes health_routes.py)
3. Human approves
4. Agent applies decorators
```

### Example 3: Detect Sensitive Params
```
User: "Add tracing to auth_service.py"

Agent:
1. Analyzes file, finds:
   - `login(email, password)` → redact=["password"]
   - `validate_token(token)` → redact=["token"]
   - `reset_password(user_id, new_password)` → redact=["new_password"]
2. Proposes decorators with redaction
3. Human approves
4. Agent applies decorators
```

---

## Skill Output Format

### Proposed Changes Format
```
## Proposed Tracing Additions

### File: src/x_ipe/services/ideas_service.py

| Function | Level | Redact | Status |
|----------|-------|--------|--------|
| `get_all_ideas()` | INFO | - | Add |
| `create_idea()` | INFO | - | Add |
| `_validate_idea()` | DEBUG | - | Add |
| `update_idea()` | INFO | - | Add |
| `delete_idea()` | INFO | - | Skip (already traced) |

### Summary
- **Total functions:** 5
- **To instrument:** 4
- **Already traced:** 1
- **Excluded:** 0

Proceed with applying decorators? [Yes/No]
```

---

## Non-Functional Requirements

### NFR-1: Performance
- Skill should analyze files quickly (< 1s per file)
- Batch operations should stream progress

### NFR-2: Safety
- Skill should never modify code without human approval
- Skill should create backup or use git for rollback

### NFR-3: Idempotency
- Running skill twice on same code should produce same result
- Already-traced functions should not be modified

---

## Out of Scope

- JavaScript/TypeScript tracing (Python only)
- Automatic test generation for traced functions
- Runtime tracing configuration changes
- Integration with external APM tools

---

## Related Documents

| Document | Link |
|----------|------|
| FEATURE-023-A Specification | [specification.md](../FEATURE-023-A/specification.md) |
| FEATURE-023-A Technical Design | [technical-design.md](../FEATURE-023-A/technical-design.md) |
| Tracing Decorator Source | [decorator.py](../../../src/x_ipe/tracing/decorator.py) |
| Redactor Patterns | [redactor.py](../../../src/x_ipe/tracing/redactor.py) |
