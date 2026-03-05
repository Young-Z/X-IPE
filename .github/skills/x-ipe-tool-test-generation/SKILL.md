---
name: x-ipe-tool-test-generation
description: Generate comprehensive test cases from technical design following TDD approach. Called by x-ipe-task-based-code-implementation to create tests before writing implementation code. Reads technical design, specification, and architecture to produce complete test suites. All tests must FAIL (TDD ready state).
---

# Tool Skill: Test Generation

## Purpose

Generate comprehensive test cases for a single feature. This is a **tool skill** invoked by `x-ipe-task-based-code-implementation` as part of TDD workflow. It does NOT manage task board entries or workflow status — the calling skill handles those.

**Called by:** `x-ipe-task-based-code-implementation` (Step 4)

---

## Input Parameters

```yaml
input:
  operation: "generate_tests"

  # Feature context (passed by calling skill)
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  technical_design_link: "{path to technical-design.md}"
  specification_link: "{path to specification.md}"

  # Tech context (from Technical Design output)
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."
  tech_stack: []  # e.g. ["Python/Flask", "JavaScript/Vanilla", "HTML/CSS"]
```

---

## Execution Procedure

```xml
<procedure name="test-generation-tool">

  <step_1>
    <name>Read Technical Design Document</name>
    <action>
      1. READ {technical_design_link}
      2. EXTRACT from Part 1 (Agent-Facing Summary): Components, interfaces, method signatures, usage examples
      3. EXTRACT from Part 2 (Implementation Guide): Data models, API endpoints, workflows, edge cases
      4. CHECK Design Change Log for updates
      5. NOTE references to architecture designs
      6. IF Technical Scope includes [Frontend] or [Full Stack]: review mockups for UI test cases
    </action>
    <constraints>
      - BLOCKING: Tests MUST be based on technical design. If design is unclear — STOP and report to calling skill.
    </constraints>
    <output>List of testable components, interfaces, and edge cases</output>
  </step_1>

  <step_2>
    <name>Read Architecture Designs (If Referenced)</name>
    <action>
      1. IF technical design references architecture components:
         READ x-ipe-docs/architecture/technical-designs/{component}.md
      2. UNDERSTAND: patterns to test, utilities to mock, integration requirements
    </action>
    <output>Architecture patterns and integration test requirements</output>
  </step_2>

  <step_3>
    <name>Read Feature Specification</name>
    <action>
      1. READ {specification_link}
      2. EXTRACT acceptance criteria (each becomes at least one test)
    </action>
    <output>Acceptance criteria mapped to test cases</output>
  </step_3>

  <step_4>
    <name>Design Test Strategy</name>
    <action>
      1. CATEGORIZE: Unit (isolated), Integration (interactions), API (endpoints)
      2. PRIORITIZE: Core functionality, then happy path, then edge cases
      3. DEFINE test data: Mocks, fixtures, request/response samples
      4. DETERMINE test types based on program_type and tech_stack:
         - IF program_type = "backend" or "cli" or "library":
           → Backend tests only (pytest for Python, go test for Go, etc.)
         - IF program_type = "frontend":
           → Frontend tests using a proper JS test framework (Vitest/Jest + jsdom)
           → Test actual class/function behavior, NOT source code string matching
           → Mock browser APIs (fetch, DOM, bootstrap) via jsdom environment
         - IF program_type = "fullstack":
           → Backend tests for API/service layer (pytest, etc.)
           → Frontend tests for JS modules using JS test framework (Vitest/Jest + jsdom)
           → Test actual logic: instantiate classes, call methods, assert behavior
           → Integration tests covering API↔UI contracts
         - IF program_type = "skills" or "mcp" or other:
           → Determine appropriate test approach from tech_stack
         - IDENTIFY test frameworks from tech_stack (e.g. pytest for Python, Vitest/Jest for JS)
         - CRITICAL: For frontend/fullstack JS code, ALWAYS use a JS test runner (Vitest preferred).
           String-matching source code in pytest is NOT acceptable as frontend testing.
           If Vitest/Jest is not yet configured, set it up (npm install, vitest.config.js).
         - For browser-global JS (no ES modules), use a test helper that loads scripts
           via `vm.runInThisContext()` and exposes classes to globalThis.
      5. DETERMINE test file organization:
         - IF only ONE tech stack needs tests → place test files directly in tests/
         - IF MULTIPLE tech stacks need separate tests → create subfolders:
           → tests/backend-python/   (Python backend tests)
           → tests/frontend-js/      (JavaScript frontend tests)
           → tests/mcp-python/       (MCP server tests)
           → Pattern: tests/{layer}-{language}/
           → Each subfolder gets its own __init__.py (if Python) or vitest.config.js (if JS)
         - ALWAYS check existing test structure first — follow project conventions
    </action>
    <constraints>
      - CRITICAL: Research testing best practices for the project tech stack before designing strategy.
      - CRITICAL: Do NOT skip frontend test coverage when program_type includes frontend code.
    </constraints>
    <output>Test strategy with categorized test plan covering all program layers</output>
  </step_4>

  <step_5>
    <name>Generate Tests</name>
    <action>
      For each component from technical design:
      1. Happy path: Valid inputs producing expected outputs
      2. Edge cases: Boundary values, empty inputs, max values
      3. Error conditions: Invalid inputs, missing dependencies, exceptions
    </action>
    <constraints>
      - MANDATORY: See references/test-patterns.md for templates, naming conventions, mock examples.
    </constraints>
    <output>All test files created in tests/ directory</output>
  </step_5>

  <step_6>
    <name>Verify TDD Ready</name>
    <action>
      1. RUN all tests: pytest tests/ -v (or npm test for frontend)
      2. VERIFY all tests FAIL (missing implementation, not test errors)
      3. FIX any test syntax/setup issues
      4. RECORD baseline: "X tests failing, 0 passing (TDD ready)"
    </action>
    <constraints>
      - BLOCKING: ALL tests MUST fail. Passing tests indicate wrong test or existing implementation.
    </constraints>
    <success_criteria>
      - All tests fail for the right reason (missing implementation)
      - No test syntax or setup errors
      - Baseline recorded
    </success_criteria>
    <output>TDD baseline status string</output>
  </step_6>

  <step_7>
    <name>Generate Tracing Tests</name>
    <action>
      1. See references/test-patterns.md for tracing test templates
      2. Skip if: No tracing infrastructure OR pure utility modules
    </action>
    <output>Tracing test files (if applicable)</output>
  </step_7>

</procedure>
```

---

## Output Result

```yaml
tool_output:
  status: completed | blocked
  tests_created: [list of test files]
  test_count: "{number}"
  baseline_status: "X tests failing, 0 passing (TDD ready)"
  test_folder: "{path to test directory}"
```

---

## Patterns & Anti-Patterns

### Pattern: API Feature

**When:** Feature includes REST endpoints
**Then:**
```
1. Unit tests for service layer
2. Integration tests for request flow
3. API tests for endpoints
4. Auth and error handling tests
```

### Pattern: Background Service

**When:** Feature runs as async/background process
**Then:**
```
1. Unit tests for core logic
2. Mock external dependencies
3. Timeout and retry tests
4. Cleanup verification tests
```

### Pattern: Data Processing

**When:** Feature processes/transforms data
**Then:**
```
1. Valid input tests
2. Edge case tests (boundaries, empty, max)
3. Invalid input tests
4. Parameterized tests for variations
```

### Anti-Patterns

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

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-test-generation/references/examples.md) for concrete execution examples including standard TDD, incremental tests, and blocked scenarios.

See [references/test-patterns.md](.github/skills/x-ipe-tool-test-generation/references/test-patterns.md) for templates, naming conventions, and mock examples.
