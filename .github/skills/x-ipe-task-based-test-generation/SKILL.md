---
name: x-ipe-task-based-test-generation
description: Generate comprehensive test cases from technical design before implementation. Follows TDD approach - write tests first, then implement. Queries feature board, reads technical design, creates all test files. Use after Technical Design, before Code Implementation.
---

# Task-Based Skill: Test Generation

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

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Test Generation"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "Code Implementation"
  require_human_review: "no"
  feature_phase: "Test Generation"

  # Required inputs
  auto_proceed: false
  feature_id: "{FEATURE-XXX}"

  # Context (from previous task or project)
  technical_design_link: "{path to technical design}"
  specification_link: "{path to feature specification}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Feature exists on feature board</name>
    <verification>Query feature board for feature_id</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is "Designed"</name>
    <verification>Check feature status from board query</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design document exists</name>
    <verification>Verify technical_design_link is accessible</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test framework available in project</name>
    <verification>Check project dependencies for test framework</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Read Design | Extract testable components from technical design | Components identified |
| 3 | Read Architecture | Check referenced architecture for test patterns | Patterns understood |
| 4 | Read Spec | Get acceptance criteria from specification | Criteria extracted |
| 5 | Design Strategy | Plan unit, integration, and API tests | Strategy defined |
| 6 | Generate Tests | Create all test files | Tests written |
| 7 | Verify TDD Ready | Run tests, confirm ALL fail | All tests fail |

BLOCKING: Step 7 - ALL tests MUST fail (no implementation exists). If any test passes, the test is wrong or implementation already exists.

---

## Execution Procedure

```xml
<procedure name="test-generation">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Query Feature Board</name>
    <action>
      1. CALL x-ipe+feature+feature-board-management skill:
         operation: query_feature
         feature_id: {feature_id from task_data}
      2. RECEIVE: feature_id, title, version, status, specification_link, technical_design_link
    </action>
    <output>Feature Data Model with all links and metadata</output>
  </step_1>

  <step_2>
    <name>Read Technical Design Document</name>
    <action>
      1. READ {technical_design_link} from Feature Data Model
      2. EXTRACT from Part 1 (Agent-Facing Summary): Components, interfaces, method signatures, usage examples
      3. EXTRACT from Part 2 (Implementation Guide): Data models, API endpoints, workflows, edge cases
      4. CHECK Design Change Log for updates
      5. NOTE references to architecture designs
      6. IF Technical Scope includes [Frontend] or [Full Stack]: review mockups for UI test cases
    </action>
    <constraints>
      - BLOCKING: Tests MUST be based on technical design. If design is unclear - STOP and request update.
    </constraints>
    <output>List of testable components, interfaces, and edge cases</output>
  </step_2>

  <step_3>
    <name>Read Architecture Designs (If Referenced)</name>
    <action>
      1. IF technical design references architecture components:
         READ x-ipe-docs/architecture/technical-designs/{component}.md
      2. UNDERSTAND: patterns to test, utilities to mock, integration requirements
    </action>
    <output>Architecture patterns and integration test requirements</output>
  </step_3>

  <step_4>
    <name>Read Feature Specification</name>
    <action>
      1. READ {specification_link} from Feature Data Model
      2. EXTRACT acceptance criteria (each becomes at least one test)
    </action>
    <output>Acceptance criteria mapped to test cases</output>
  </step_4>

  <step_5>
    <name>Design Test Strategy</name>
    <action>
      1. CATEGORIZE: Unit (isolated), Integration (interactions), API (endpoints)
      2. PRIORITIZE: Core functionality, then happy path, then edge cases
      3. DEFINE test data: Mocks, fixtures, request/response samples
    </action>
    <constraints>
      - CRITICAL: Research testing best practices for the project tech stack before designing strategy.
    </constraints>
    <output>Test strategy with categorized test plan</output>
  </step_5>

  <step_6>
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
  </step_6>

  <step_7>
    <name>Verify TDD Ready</name>
    <action>
      1. RUN all tests: pytest tests/ -v
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
  </step_7>

  <step_8>
    <name>Generate Tracing Tests</name>
    <action>
      1. See references/test-patterns.md for tracing test templates
      2. Skip if: No tracing infrastructure OR pure utility modules
    </action>
    <output>Tracing test files (if applicable)</output>
  </step_8>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "Code Implementation"
  require_human_review: "no"
  auto_proceed: {from input}
  task_output_links:
    - "tests/"
  feature_id: FEATURE-XXX
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Test Generation"
  tests_created: [list of test files]
  test_count: "{number}"
  baseline_status: "X tests failing, 0 passing (TDD ready)"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Feature board queried for context</name>
    <verification>Feature Data Model retrieved with all links</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design read and understood</name>
    <verification>All testable components identified from design</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Unit tests cover all public interfaces</name>
    <verification>Each public method/function has corresponding test</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Integration tests cover main flows</name>
    <verification>Primary workflows have integration tests</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>API tests cover all endpoints</name>
    <verification>Each endpoint has request/response tests</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tests follow project conventions</name>
    <verification>Naming, structure, and patterns match existing tests</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests fail for right reason (TDD ready)</name>
    <verification>Run test suite - all fail due to missing implementation</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test coverage documented</name>
    <verification>Test count and baseline status recorded in output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tracing assertions included in tests</name>
    <verification>Tracing tests exist or documented as skipped</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

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

See [references/examples.md](references/examples.md) for concrete execution examples including standard TDD, incremental tests, and blocked scenarios.

See [references/test-patterns.md](references/test-patterns.md) for templates, naming conventions, and mock examples.
