---
name: task-type-code-implementation
description: Implement code based on technical design for a single feature. First queries feature board, then learns technical design (and architecture if referenced). Follows TDD workflow and KISS/YAGNI principles. Triggers on requests like "implement feature", "write code", "develop feature".
---

# Task Type: Code Implementation

## Purpose

Implement code for a single feature by:
1. Querying feature board for full Feature Data Model
2. Learning technical design document thoroughly
3. Reading architecture designs (if referenced in technical design)
4. Following TDD - write tests first, then implementation
5. NO board status update (handled by category skill)

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Code Implementation |
| Category | feature-stage |
| Next Task Type | Feature Acceptance Test |
| Require Human Review | No |
| Feature Phase | Code Implementation |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: feature-stage
  status: completed | blocked
  next_task_type: Feature Acceptance Test
  require_human_review: No
  auto_proceed: {from input Auto Proceed}
  task_output_links: [src/, tests/]
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Code Implementation
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Feature exists on feature board | Yes |
| 2 | Feature status is "Designed" | Yes |
| 3 | Technical design document exists | Yes |
| 4 | **Tests exist from Test Generation task** | Yes |
| 5 | **All tests currently FAIL (TDD ready)** | Yes |
| 6 | **Tracing utility exists in project** | Yes (see Tracing Check) |

**⚠️ PRE-CODING VERIFICATION:**
Before writing ANY implementation code, agent MUST:
1. Run the test suite to confirm tests exist
2. Verify tests FAIL (proving no implementation yet)
3. If tests pass or don't exist → STOP and complete Test Generation first

**🔍 TRACING CHECK (FEATURE-023-D):**
Before implementing, verify tracing infrastructure exists:
1. Check for `tracing/` directory or `x_ipe.tracing` import availability
2. If NOT available → Use `tool-tracing-creator` skill to create tracing utility
3. If available → Proceed with implementation

---

## Execution Flow

Execute Code Implementation by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Learn Design | Read technical design document thoroughly | Design understood |
| 3 | Read Architecture | Read referenced architecture designs (if any) | Architecture understood |
| 4 | Load Tests | Locate and run tests, verify they FAIL | Tests fail (TDD ready) |
| 5 | Implement | Write minimum code to pass tests | Tests pass |
| 6 | Verify | Run all tests, linter, check coverage | All checks pass |

**⛔ BLOCKING RULES:**
- Step 4 → 5: BLOCKED until tests exist AND fail
- Step 4: If tests pass or don't exist → STOP, complete Test Generation first
- Step 5: If design needs changes → UPDATE technical design BEFORE implementing

---

## Implementation Principles

| Principle | Description |
|-----------|-------------|
| **KISS** | Keep code simple, readable, prefer clarity over cleverness |
| **YAGNI** | Implement ONLY what's in technical design, no extras |
| **TDD** | RED (test fails) → GREEN (pass) → REFACTOR → REPEAT |
| **Coverage ≠ Complexity** | Target 80%+, never add complexity for coverage |
| **Coding Standards** | Use linters, formatters, meaningful names |

**🎨 Mockup Reference:** For frontend work, reference mockups from specification.md and match layout, components, and visual states.

📖 **See:** [references/implementation-guidelines.md](references/implementation-guidelines.md) for detailed principles, examples, and coding standards.

---

## Execution Procedure

### Step 1: Query Feature Board

**Action:** Get full Feature Data Model for context

```
CALL feature-stage+feature-board-management skill:
  operation: query_feature
  feature_id: {feature_id from task_data}

RECEIVE Feature Data Model:
  feature_id: FEATURE-XXX
  title: {Feature Title}
  version: v1.0
  status: Designed
  specification_link: x-ipe-docs/requirements/FEATURE-XXX/specification.md
  technical_design_link: x-ipe-docs/requirements/FEATURE-XXX/technical-design.md
```

---

### Step 2: Learn Technical Design Document

**Action:** THOROUGHLY read and understand the technical design

1. READ `{technical_design_link}` from Feature Data Model
2. UNDERSTAND Part 1 (Agent-Facing Summary) and Part 2 (Implementation Guide)
3. NOTE references to architecture designs
4. CHECK Design Change Log for updates

**⚠️ STRICT:** Do NOT code until design is understood. If design is unclear → STOP and update first.

---

### Step 2.1: Update Technical Design If Needed

If implementation reveals design issues → STOP, UPDATE technical-design.md, add to Design Change Log, then RESUME.

📖 **See:** [references/implementation-guidelines.md](references/implementation-guidelines.md#design-update-procedure) for detailed procedure.

---

### Step 3: Read Architecture Designs (If Referenced)

**Action:** If technical design references architecture patterns, READ them first

- Read `x-ipe-docs/architecture/technical-designs/{component}.md`
- Understand common patterns, interfaces, and integration requirements
- Follow project-wide patterns consistently

---

### Step 4: Load Existing Tests from Test Generation (⚠️ MANDATORY)

**Action:** Verify tests from Test Generation are ready BEFORE any coding

1. **LOCATE** test files: `tests/unit/{feature}/`, `tests/integration/{feature}/`, `tests/test_{feature}.py`
2. **RUN** all tests: `pytest tests/ -v` or `npm test`
3. **VERIFY** tests FAIL (proves TDD ready)
4. **IF tests pass** → STOP, implementation may exist
5. **IF tests don't exist** → STOP, complete Test Generation first

**⚠️ NO EXCEPTIONS:** Do NOT write implementation code until tests exist AND fail.

📖 **See:** [references/implementation-guidelines.md](references/implementation-guidelines.md#step-4-load-tests-detailed) for detailed procedure.

---

### Step 5: Implement Code

**Action:** Write minimum code to pass tests (following technical design)

1. **IMPLEMENT** in order: Data models → Business logic → API endpoints → Integration
2. **FOR EACH** component: Write code → Run tests → Verify pass → Refactor if needed
3. **AVOID:** Extra features, over-engineering, premature optimization

**🌐 Web Search:** Use for library APIs, error messages, best practices, security.

📖 **See:** [references/implementation-guidelines.md](references/implementation-guidelines.md#step-5-implement-code-detailed) for detailed procedure.

---

### Step 6: Verify & Ensure Quality

**Action:** Run all checks before completion

1. **RUN** tests: `pytest tests/ -v` or `npm test`
2. **CHECK** coverage: `pytest --cov=src tests/` (aim 80%+)
3. **RUN** linter: `ruff check` / `eslint`
4. **RUN** formatter: `ruff format` / `prettier`
5. **VERIFY:** All tests pass, no linter errors, code matches design

📖 **See:** [references/implementation-guidelines.md](references/implementation-guidelines.md#step-6-verify--ensure-quality-detailed) for detailed commands.

---

### Step 7: Apply Tracing Instrumentation (FEATURE-023-D)

**Action:** Add tracing decorators to all implemented code

1. **INVOKE** `tool-tracing-instrumentation` skill for all modified files
2. **REVIEW** proposed decorators (INFO for public, DEBUG for helpers)
3. **APPLY** decorators with sensitive param redaction
4. **RE-RUN** tests to verify functionality

**Skip if:** No tracing infrastructure, test files, or config files.

📖 **See:** [references/implementation-guidelines.md](references/implementation-guidelines.md#tracing-instrumentation) for detailed procedure.

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Feature board queried for context | Yes |
| 2 | Technical design learned and understood | Yes |
| 3 | Tests written (TDD) | Yes |
| 4 | All tests pass | Yes |
| 5 | Implementation matches technical design | Yes |
| 6 | No extra features added (YAGNI) | Yes |
| 7 | Code is simple (KISS) | Yes |
| 8 | Linter passes | Yes |
| 9 | Test coverage ≥ 80% for new code | Recommended |
| 10 | **All public functions have `@x_ipe_tracing` decorators** | Yes |
| 11 | **Sensitive parameters have `redact=[]` specified** | Yes |

**🔍 TRACING VERIFICATION (FEATURE-023-D):**
Before marking complete, verify tracing is applied:
1. All API endpoints have `@x_ipe_tracing(level="INFO")`
2. Key business functions have `@x_ipe_tracing(level="INFO")`
3. Helper/utility functions have `@x_ipe_tracing(level="DEBUG")` or are skipped
4. Sensitive parameters (password, token, secret, key) have `redact=["param"]`
5. Use `tool-tracing-instrumentation` skill to add decorators if missing

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: TDD Flow

**When:** Tests exist from Test Generation
**Then:**
```
1. Run tests - confirm all FAIL
2. Implement smallest unit first
3. Run tests - some pass
4. Continue until all pass
5. Refactor if needed
```

### Pattern: Design Reference

**When:** Technical design references architecture patterns
**Then:**
```
1. Read referenced architecture docs
2. Follow existing patterns exactly
3. Reuse shared utilities
4. Ask if patterns unclear
```

### Pattern: Blocked by Tests

**When:** Tests don't exist or pass unexpectedly
**Then:**
```
1. STOP implementation
2. Return to Test Generation task
3. Create/fix failing tests
4. Resume implementation
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip reading design | Wrong implementation | Learn technical design first |
| Ignore architecture docs | Inconsistent patterns | Read referenced architecture |
| Code first, test later | Not TDD, miss edge cases | Write tests first |
| Add "nice to have" features | YAGNI violation | Only implement what's in design |
| Complex code for coverage | Maintenance nightmare | Keep simple, accept 80% coverage |
| Over-engineering | KISS violation | Simplest solution that works |
| Copy-paste code | DRY violation | Extract reusable functions |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Authentication service implementation (TDD)
- Test failure during implementation (design gap)
- Missing tests (blocked scenario)
- Multiple features batch implementation

---

## Notes

- Work on ONE feature at a time (feature_id from task_data)
- Query feature board FIRST to get context
- Read technical design THOROUGHLY before coding
- Read architecture designs IF referenced
- Follow TDD: write tests FIRST, then implementation
- Keep code SIMPLE (KISS)
- Implement ONLY what's in design (YAGNI)
- Do NOT add complexity for test coverage
- Output feature_phase = "Code Implementation" for correct board update
