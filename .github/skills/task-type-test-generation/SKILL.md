---
name: task-type-test-generation
description: Generate comprehensive test cases from technical design before implementation. Follows TDD approach - write tests first, then implement. Queries feature board, reads technical design, creates all test files. Use after Technical Design, before Code Implementation.
---

# Task Type: Test Generation

## Purpose

Generate comprehensive test cases for a single feature by:
1. Querying feature board for full Feature Data Model
2. Reading technical design document thoroughly
3. Reading architecture designs (if referenced)
4. Creating complete test suite (unit, integration, API tests)
5. Verifying all tests fail (TDD ready state)
6. NO board status update (handled by category skill)

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first.
- If Agent DO NOT have skill capability, go to `skills/` folder to learn skills (SKILL.md is entry point).

---

## Task Type Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Test Generation |
| Category | feature-stage |
| Next Task Type | Code Implementation |
| Require Human Review | No |
| Feature Phase | Test Generation |
| Auto Proceed (Input) | False (default) |

---

## Skill/Task Completion Output

```yaml
Output:
  category: feature-stage
  status: completed | blocked
  next_task_type: Code Implementation
  require_human_review: No
  auto_proceed: {from input}
  task_output_links: [tests/]
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Test Generation
  tests_created: [list of test files]
  test_count: {number}
  baseline_status: "X tests failing, 0 passing (TDD ready)"
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Feature exists on feature board | Yes |
| 2 | Feature status is "Designed" | Yes |
| 3 | Technical design document exists | Yes |
| 4 | Test framework available in project | Yes |

---

## Execution Flow

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Read Design | Extract testable components from technical design | Components identified |
| 3 | Read Architecture | Check referenced architecture for test patterns | Patterns understood |
| 4 | Read Spec | Get acceptance criteria from specification | Criteria extracted |
| 5 | Design Strategy | Plan unit, integration, and API tests | Strategy defined |
| 6 | Generate Tests | Create all test files | Tests written |
| 7 | Verify TDD Ready | Run tests, confirm ALL fail | All tests fail |

**⛔ BLOCKING RULES:**
- Step 7: ALL tests MUST fail (no implementation exists)
- Step 7: If any test passes → test is wrong or implementation exists

---

## Execution Procedure

### Step 1: Query Feature Board

```
CALL feature-stage+feature-board-management skill:
  operation: query_feature
  feature_id: {feature_id from task_data}

RECEIVE: feature_id, title, version, status, specification_link, technical_design_link
```

### Step 2: Read Technical Design Document

1. READ `{technical_design_link}` from Feature Data Model
2. EXTRACT from Part 1 (Agent-Facing Summary): Components, interfaces, method signatures, usage examples
3. EXTRACT from Part 2 (Implementation Guide): Data models, API endpoints, workflows, edge cases
4. CHECK Design Change Log for updates
5. NOTE references to architecture designs
6. **If Technical Scope includes [Frontend] or [Full Stack]:** Review mockups for UI tests

**⚠️ Tests MUST be based on technical design. If design is unclear - STOP and request update.**

### Step 3: Read Architecture Designs (If Referenced)

```
IF technical design references architecture components:
  READ x-ipe-docs/architecture/technical-designs/{component}.md
  UNDERSTAND: patterns to test, utilities to mock, integration requirements
```

### Step 4: Read Feature Specification

1. READ `{specification_link}` from Feature Data Model
2. EXTRACT acceptance criteria (each becomes at least one test)

### Step 5: Design Test Strategy

**🌐 Web Search (Recommended):** Research testing best practices for tech stack.

1. CATEGORIZE: Unit (isolated), Integration (interactions), API (endpoints)
2. PRIORITIZE: Core functionality → Happy path → Edge cases
3. DEFINE test data: Mocks, fixtures, request/response samples

### Step 6: Generate Tests

For each component from technical design:
1. **Happy path:** Valid inputs → Expected outputs
2. **Edge cases:** Boundary values, empty inputs, max values
3. **Error conditions:** Invalid inputs, missing dependencies, exceptions

> 📖 See [references/test-patterns.md](references/test-patterns.md) for templates, naming conventions, mock examples

### Step 7: Verify TDD Ready

```
1. RUN all tests: pytest tests/ -v
2. VERIFY all tests FAIL (missing implementation, not test errors)
3. FIX any test syntax/setup issues
4. RECORD baseline: "X tests failing, 0 passing (TDD ready)"
```

### Step 8: Generate Tracing Tests

> 📖 See [references/test-patterns.md](references/test-patterns.md) for tracing test templates

**Skip if:** No tracing infrastructure OR pure utility modules

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Feature board queried for context | Yes |
| 2 | Technical design read and understood | Yes |
| 3 | Unit tests cover all public interfaces | Yes |
| 4 | Integration tests cover main flows | Yes |
| 5 | API tests cover all endpoints | Yes |
| 6 | Tests follow project conventions | Yes |
| 7 | All tests fail for right reason (TDD ready) | Yes |
| 8 | Test coverage documented | Yes |
| 9 | Tracing assertions included in tests | Yes |

**Important:** After completing, return to `task-execution-guideline` skill to continue the flow.

---

## Patterns

### Pattern: API Feature
**When:** Feature includes REST endpoints
**Then:** Unit tests (service) + Integration tests (flow) + API tests (endpoints) + Auth/error tests

### Pattern: Background Service
**When:** Feature runs as async/background process
**Then:** Unit tests (core) + Mock dependencies + Timeout/retry tests + Cleanup verification

### Pattern: Data Processing
**When:** Feature processes/transforms data
**Then:** Valid input tests + Edge cases + Invalid input tests + Parameterized tests

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip reading design | Tests miss requirements | Read technical design first |
| Test implementation details | Brittle tests | Test behavior only |
| One giant test | Hard to debug | One assertion per test |
| Test private methods | Couples to internals | Test via public interface |
| Skip edge cases | Bugs hide in edges | Prioritize edge cases |
| Hardcoded test data | Hard to maintain | Use test fixtures |
| Tests pass initially | Not TDD | Ensure tests fail first |

---

## References

- [Test Patterns & Templates](references/test-patterns.md) - Naming conventions, mock examples, coverage requirements
- [Execution Examples](references/examples.md) - Standard TDD, incremental tests, blocked scenarios

---

## Notes

- Work on ONE feature at a time
- Query feature board FIRST for context
- Read technical design THOROUGHLY before writing tests
- Create ALL tests before Code Implementation starts
- Verify tests FAIL (TDD ready state)
- Output feature_phase = "Test Generation" for correct board update
