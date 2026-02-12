---
name: x-ipe-task-based-code-implementation
description: Implement code based on technical design for a single feature. First queries feature board, then learns technical design (and architecture if referenced). Follows TDD workflow and KISS/YAGNI principles. Triggers on requests like "implement feature", "write code", "develop feature".
---

# Task-Based Skill: Code Implementation

## Purpose

Implement code for a single feature by:
1. Querying feature board for full Feature Data Model
2. Learning technical design document thoroughly
3. Reading architecture designs (if referenced in technical design)
4. Following TDD - write tests first, then implementation
5. NO board status update (handled by category skill)

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

### Implementation Principles

| Principle | Rule |
|-----------|------|
| KISS | Keep code simple and readable; prefer clarity over cleverness |
| YAGNI | Implement ONLY what is in technical design; no extras |
| TDD | RED (test fails) -> GREEN (pass) -> REFACTOR -> REPEAT |
| Coverage | Target 80%+; NEVER add complexity just for coverage |
| Standards | Use linters, formatters, meaningful names |
| Mockups | For frontend work, reference mockups from specification.md and match layout, components, and visual states |

See [references/implementation-guidelines.md](references/implementation-guidelines.md) for detailed principles, coding standards, and error handling patterns.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Code Implementation"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "Feature Acceptance Test"
  require_human_review: no
  feature_phase: "Code Implementation"

  # Required inputs
  auto_proceed: false
  feature_id: "{FEATURE-XXX}"

  # Git strategy (from .x-ipe.yaml, passed by workflow)
  git_strategy: "main-branch-only | dev-session-based"
  git_main_branch: "{auto-detected}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Feature exists on feature board</name>
    <verification>Query feature board for feature_id; status must exist</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is "Designed"</name>
    <verification>Feature board status == "Designed"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design document exists</name>
    <verification>File exists at x-ipe-docs/requirements/FEATURE-XXX/technical-design.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tests exist from Test Generation task</name>
    <verification>Run test suite; test files found and execute</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests currently FAIL (TDD ready)</name>
    <verification>Run pytest/npm test; all feature tests must FAIL (no implementation yet)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tracing utility exists in project</name>
    <verification>Check for tracing/ directory or x_ipe.tracing import; if missing, use x-ipe-tool-tracing-creator skill first</verification>
  </checkpoint>
</definition_of_ready>
```

BLOCKING: Before writing ANY implementation code, agent MUST:
1. Run the test suite to confirm tests exist
2. Verify tests FAIL (proving no implementation yet)
3. If tests pass or do not exist -> STOP and complete Test Generation first

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Learn Design | Read technical design document thoroughly | Design understood |
| 3 | Read Architecture | Read referenced architecture designs (if any) | Architecture understood |
| 4 | Load Tests | Locate and run tests, verify they FAIL | Tests fail (TDD ready) |
| 5 | Implement | Write minimum code to pass tests | Tests pass |
| 6 | Verify | Run all tests, linter, check coverage | All checks pass |
| 7 | Tracing | Add tracing decorators to implemented code | Tests still pass |

BLOCKING: Step 4 -> 5 is BLOCKED until tests exist AND fail. If tests pass or do not exist -> STOP, complete Test Generation first.
BLOCKING: Step 5: If design needs changes -> UPDATE technical design BEFORE implementing.

---

## Execution Procedure

```xml
<procedure name="code-implementation">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Query Feature Board</name>
    <action>
      1. CALL x-ipe+feature+feature-board-management skill with operation=query_feature
      2. RECEIVE Feature Data Model (feature_id, title, version, status, specification_link, technical_design_link)
    </action>
    <constraints>
      - BLOCKING: Feature must exist on board with status "Designed"
    </constraints>
    <output>Feature Data Model with all links and context</output>
  </step_1>

  <step_2>
    <name>Learn Technical Design</name>
    <action>
      1. READ technical_design_link from Feature Data Model
      2. UNDERSTAND Part 1 (Agent-Facing Summary) and Part 2 (Implementation Guide)
      3. NOTE references to architecture designs
      4. CHECK Design Change Log for updates
      5. CHECK specification.md for Linked Mockups section:
         a. IF mockups exist with status "current":
            - READ each current mockup file from x-ipe-docs/requirements/FEATURE-XXX/mockups/
            - Extract: layout structure, component placement, visual states, interactions, styling details
            - These mockup details MUST guide frontend implementation in Step 5
         b. IF mockups are marked "outdated" or absent: note and proceed
    </action>
    <constraints>
      - BLOCKING: Do NOT code until design is understood
      - If design is unclear -> STOP and clarify before proceeding
      - CRITICAL: If implementation reveals design issues during later steps, STOP, UPDATE technical-design.md, add to Design Change Log, then RESUME
    </constraints>
    <output>Complete understanding of implementation requirements, mockup references loaded (if applicable)</output>
  </step_2>

  <step_3>
    <name>Read Architecture Designs</name>
    <action>
      1. CHECK if technical design references architecture patterns
      2. IF no architecture references: skip this step
         ELSE: READ x-ipe-docs/architecture/technical-designs/{component}.md and UNDERSTAND common patterns, interfaces, integration requirements
    </action>
    <output>Architecture patterns understood (or skipped)</output>
  </step_3>

  <step_4>
    <name>Load and Verify Tests</name>
    <action>
      1. LOCATE test files: tests/unit/{feature}/, tests/integration/{feature}/, tests/test_{feature}.py
      2. RUN all tests: pytest tests/ -v or npm test
      3. VERIFY tests FAIL (proves TDD ready)
    </action>
    <constraints>
      - MANDATORY: Do NOT write implementation code until tests exist AND fail
      - BLOCKING: If tests pass -> STOP, implementation may already exist
      - BLOCKING: If tests do not exist -> STOP, complete Test Generation first
    </constraints>
    <output>Confirmed: N tests exist and all FAIL</output>
  </step_4>

  <step_5>
    <name>Implement Code</name>
    <action>
      1. IMPLEMENT in order: Data models -> Business logic -> API endpoints -> Integration
      2. FOR EACH component: Write code -> Run tests -> Verify pass -> Refactor if needed
      3. Follow technical design exactly; no extra features
      4. IF current mockups were loaded in Step 2 AND feature has frontend/UI components:
         a. Use mockup as the visual source of truth for layout, component placement, and styling
         b. Match HTML structure, CSS classes, and element hierarchy to the mockup
         c. Implement all visual states shown in mockup (hover, active, disabled, empty, error)
         d. Ensure spacing, colors, and typography follow mockup (and brand theme if specified in specification)
    </action>
    <constraints>
      - CRITICAL: Implement ONLY what is in technical design (YAGNI)
      - CRITICAL: Keep code simple (KISS)
      - CRITICAL: Do NOT modify existing tests; if test fails due to design gap, report to human
      - CRITICAL: For UI/frontend code with current mockups, the mockup is the visual spec -- implementation MUST match it
      - Use web search for library APIs, error messages, best practices
    </constraints>
    <output>All feature tests passing</output>
  </step_5>

  <step_6>
    <name>Verify and Ensure Quality</name>
    <action>
      1. RUN tests: pytest tests/ -v or npm test
      2. CHECK coverage: pytest --cov=src tests/ (aim 80%+)
      3. RUN linter: ruff check / eslint
      4. RUN formatter: ruff format / prettier
      5. VERIFY: All tests pass, no linter errors, code matches design
    </action>
    <success_criteria>
      - All tests pass
      - No linter errors
      - Code matches technical design
      - No extra features added
      - Frontend output matches current mockups (if applicable)
    </success_criteria>
    <output>All quality checks pass</output>
  </step_6>

  <step_7>
    <name>Apply Tracing Instrumentation</name>
    <action>
      1. IF no tracing infrastructure (no x_ipe.tracing module) or only test/config files modified: skip this step
      2. ELSE:
         a. INVOKE x-ipe-tool-tracing-instrumentation skill for all modified files
         b. REVIEW proposed decorators (INFO for public, DEBUG for helpers)
         c. APPLY decorators with sensitive param redaction
         d. RE-RUN tests to verify functionality
    </action>
    <output>Tracing decorators applied; tests still pass</output>
  </step_7>

</procedure>
```

See [references/implementation-guidelines.md](references/implementation-guidelines.md) for detailed sub-procedures per step.

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "Feature Acceptance Test"
  require_human_review: no
  auto_proceed: "{from input auto_proceed}"
  task_output_links:
    - "src/"
    - "tests/"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Code Implementation"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Feature board queried for context</name>
    <verification>Feature Data Model received with all links</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design learned and understood</name>
    <verification>Agent can describe implementation plan from design</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests pass</name>
    <verification>Run pytest/npm test; zero failures</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Implementation matches technical design</name>
    <verification>Compare implemented components against design document</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Frontend matches current mockups</name>
    <verification>If feature has current mockups in specification, UI layout/components/styling match the mockup</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No extra features added (YAGNI)</name>
    <verification>Review code for functionality not specified in design</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code is simple (KISS)</name>
    <verification>No unnecessary abstractions or over-engineering</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Linter passes</name>
    <verification>Run ruff check / eslint with zero errors</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Test coverage at least 80% for new code</name>
    <verification>Run pytest --cov=src tests/; check coverage report</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All public functions have @x_ipe_tracing decorators</name>
    <verification>Grep for public functions without decorators in modified files</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Sensitive parameters have redact=[] specified</name>
    <verification>Grep for password/token/secret/key params; verify redact is set</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

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

**When:** Tests do not exist or pass unexpectedly
**Then:**
```
1. STOP implementation
2. Return to Test Generation task
3. Create/fix failing tests
4. Resume implementation
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip reading design | Wrong implementation | Learn technical design first |
| Ignore architecture docs | Inconsistent patterns | Read referenced architecture |
| Code first, test later | Not TDD, miss edge cases | Tests must exist and fail first |
| Add "nice to have" features | YAGNI violation | Only implement what is in design |
| Complex code for coverage | Maintenance nightmare | Keep simple, accept 80% coverage |
| Over-engineering | KISS violation | Simplest solution that works |
| Ignore mockups for frontend | UI drifts from approved design | Use current mockups as visual spec |
| Copy-paste code | DRY violation | Extract reusable functions |

---

## Examples

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Authentication service implementation (TDD)
- Test failure during implementation (design gap)
- Missing tests (blocked scenario)
- Multiple features batch implementation
