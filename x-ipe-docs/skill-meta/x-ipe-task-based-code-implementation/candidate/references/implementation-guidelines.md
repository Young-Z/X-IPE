# Implementation Guidelines Reference

This document contains detailed implementation guidelines, coding standards, AAA scenario format specification, tool skill contract, and error handling patterns for the Code Implementation task type.

Load the common lifecycle/goal contracts from the entry. All procedures here are
domain-only under the same supplied owner/readiness, not another task or Git route.
Concrete example credentials/API behaviors are illustrative approved-contract
fixtures, not authority to add authentication, status codes or targets to a feature.

---

## AAA Scenario Format Specification

### Format

Each scenario follows this YAML-like structure:

```yaml
@{layer_tag}
Test Scenario: {descriptive_name}
  Arrange:
    - {precondition_1}
    - {precondition_2}
  Act:
    - {action_performed}
  Assert:
    - {expected_outcome_1}
    - {expected_outcome_2}
```

### Layer Tags

| Tag | Scope | Granularity |
|-----|-------|-------------|
| `@backend` | Individual functions, methods, endpoints in isolation | Unit-level |
| `@frontend` | Individual components, event handlers, DOM behavior | Unit-level |
| `@integration` | Cross-layer workflows with mocking | Functional-level |

### Generation Algorithm

```
PROCEDURE: Generate AAA Scenarios

INPUT: specification.md, technical-design.md
OUTPUT: List of tagged AAA scenarios

1. PARSE specification.md:
   a. Extract every scoped AC and ALL original assertions with stable source/story/AC links and specification test type; use appropriate layer scenarios, not forced mocked integration for every acceptance type
      - Arrange = preconditions from AC context
      - Act = user action described in AC
      - Assert = all approved observable expected behaviors from AC, not a stakeholder-outcome achievement claim

2. PARSE technical-design.md Part 2:
   a. Extract API endpoints / service methods:
      - For each endpoint → create @backend happy-path scenario
      - For each endpoint → create @backend error-path scenario
   b. Extract UI components / event handlers:
      - For each component → create @frontend happy-path scenario
      - For each component → create @frontend error-path scenario
   c. Extract validation rules:
      - For each rule → create @backend validation scenario
   d. Extract error conditions / edge cases:
      - For each → create scenario in matching layer

3. TAG each scenario with @backend, @frontend, or @integration

4. VALIDATE coverage:
   - Every scoped AC has suitable checks and every original Assert clause retained
   - Selected contracts have concrete happy/error/edge/regression checks where applicable
   - Log source/AC/assertion coverage; activity counts are not success criteria

5. IF context is large (>20 components):
   - Generate per-layer: all @backend first, then @frontend
   - Retain complete cross-layer AC/assertion map before any invocation; never lose uncovered criteria between batches
```

### Context Budget Strategy (Large Features)

For large context (the >20 components heuristic is not a feature goal):
1. Preserve a complete scoped AC/assertion/test-type map, including cross-layer cases.
2. Generate per-layer batches; order dependent work/shared writes sequentially, backend before dependent frontend. Independent read/test calls may be batched only with isolated data/environment/cleanup; skills remain in the same context.
3. Run integration with suitable mocking plus original UI/API/CLI/structured acceptance checks; mocking does not prove actual UI or stakeholder outcome.

This prevents context overflow by processing one layer at a time.

---

## Tool Skill Input/Output Contract

### Input (Orchestrator → Tool Skill)

```yaml
tool_skill_input:
  operation: "implement"  # Supported: "implement" | "fix" | "refactor"
  aaa_scenarios:
    - scenario_text: |
        @backend
        Test Scenario: Create project via API
          Arrange:
            - User is authenticated with valid credentials
          Act:
            - Send POST /api/projects with body { name: "Test Project" }
          Assert:
            - Response status is 201
  source_code_path: "src/my_app/"
  test_code_path: "tests/"
  feature_context:  # REQUIRED for implement; OPTIONAL for fix/refactor
    feature_id: "FEATURE-XXX-X"
    feature_title: "..."
    mockup_link: "{current scoped frontend mockup or N/A}"
    technical_design_link: "x-ipe-docs/requirements/EPIC-XXX/FEATURE-XXX-X/technical-design.md"
    specification_link: "x-ipe-docs/requirements/EPIC-XXX/FEATURE-XXX-X/specification.md"
```

Use actual approved source_code_path/test_code_path. Preserve original scenario
texts, AC/test types and feature links when filtering layers. Supplemental
feature_context may carry existing artifact anchors/revision evidence, not a new
board/output schema. Agree same-task lifecycle ownership before tool invocation.

### Operation Semantics

| Operation | Purpose | AAA Scenarios | feature_context | TDD Gate |
|-----------|---------|--------------|-----------------|----------|
| `implement` | Build approved feature capability | Full scoped original assertion set | Required | New/changed behavior RED before implementation then GREEN; baseline/regression for already satisfied criteria |
| `fix` | Fix a bug via TDD | 1-2 narrow scenarios from bug context | Optional (synthetic fallback) | Test MUST fail before fix |
| `refactor` | Restructure preserving behavior | Per-phase target state scenarios | Optional (synthetic fallback) | Baseline tests must pass first |

When `feature_context` is absent for fix/refactor, tool skills generate synthetic context:
- Fix: `feature_id: "BUG-{task_id}"`, `technical_design_link: "N/A"`
- Refactor: `feature_id: "REFACTOR-{task_id}"`, `technical_design_link: "N/A"`

### Output (Tool Skill → Orchestrator)

```yaml
tool_skill_output:
  implementation_files:
    - "src/my_app/projects/service.py"
  test_files:
    - "tests/test_projects_service.py"
  test_results:
    - scenario: "Create project via API"
      assert_clause: "Response status is 201"
      status: "pass"
  lint_status: "pass"
  lint_details: ""
```

Verify outputs against actual files and test execution, not a tool's self-reported
pass alone. Special skill-creator/MCP outputs retain their own contracts; adapt
their actual scoped artifacts/checks into existing evidence without fabricating
tool_skill_output, publication permission or an observed outcome.

## Implementation Coverage in Existing Artifacts

Append/update this section in the existing design/testing artifact, never a new
mandatory goal document. Replace placeholders with current sources and evidence.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {stable source/story ID} | {authoritative source/parent} | {actual stakeholder} | {approved outcome} | {enabling selected means; all-required cases versus alternatives} | {source-derived qualitative scenario or justified measure} | {approved constraints} | {all scoped ACs} | {not measured or cited actual observation} |

| Source / Parent Goal | Story / Subgoal | AC ID | Selected Means | Test / Assert | Delivery State | Outcome State |
| --- | --- | --- | --- | --- | --- | --- |
| {source/parent anchor} | {stable story/subgoal} | {stable scoped AC} | {justified means within approved design} | {original test type, every assertion, path/command/input/result/revision evidence} | {planned or current verified engineering delivery with actual evidence} | {not measured or cited observation} |

Record rejected alternatives as rationale, not backlog mandates. Necessary
support concerns must explain their contribution/constraints. Qualitative outcome
scenario identifies actual stakeholder/context/observable conditions/result and
evidence gaps; no invented KPI or scope. Planned checks, fixtures, approval or DAO
guidance are not observed stakeholder outcome. Legacy explicit so-that intent is
labeled inferred with exact source/story; ambiguity blocks its pertinent claim.

### TDD, Regression and Freshness

For new/changed behavior execute a relevant failing check before implementation,
confirm the failure is the expected behavior (not broken collection/import), then
rerun after changes for GREEN. Existing satisfied ACs retain passing baseline
and affected regression; never force all old tests red. Preserve ALL original
assertions/ACs/test types: no weakening/deletion/xfail/skips to manufacture success.
Delegated structured review has domain checks instead of fabricated executable RED.

Installed ordinary implement operations often create tests after code; do not
claim they already enforce this RED gate. The orchestrator supplies/runs relevant
RED tests before invoking them (or an explicitly agreed same-task TDD adapter),
then verifies those unchanged assertions against tool results. Live tool output
does not silently migrate every tool procedure. Keep mockup_link inside actual
feature_context as the HTML5 tool declares. When adding await verify async on the
containing function and propagate through callers needing completion; actual
browser/runtime syntax checks supplement mocks or jsdom where applicable.

Evidence binds relevant inputs: authoritative parent/spec/ACs, both design parts,
dependent interfaces, current mockups, actual tool/workflow/tracing config and
declarations, implementation/tests, commands/exits/results and review scope.
Rehash before completion; timestamps alone or prior pass counts cannot prove
freshness. Authorized intent/parent/means deltas invalidate affected checks/review/
outcome and dependent claims; preserve unrelated IDs/bytes/assertions/history and
evidence only after verifying dependency independence. An unmeasured outcome
does not block independently supported engineering delivery. No-op resume checks
fresh evidence read-only without rewriting logs or replaying owner persistence.

---

## Implementation Principles (Detailed)

### KISS (Keep It Simple, Stupid)

**Core Principles:**
- Write simple, readable code
- No complex abstractions unless specified in design
- Use compatible patterns within approved technical design/acceptance/constraints
- Prefer clarity over cleverness
- If implementation seems complex, question the design

**Examples:**
```python
# ✅ GOOD: Simple and clear
def get_user_display_name(user):
    return f"{user.first_name} {user.last_name}"

# ❌ BAD: Over-engineered
def get_user_display_name(user, formatter=None, cache=None, observer=None):
    if formatter is None:
        formatter = DefaultNameFormatter()
    # ... unnecessary complexity
```

---

### YAGNI (You Aren't Gonna Need It)

**Core Principles:**
- Implement ONLY what's in technical design
- No extra features "just in case"
- No "nice to have" additions
- Means may flex within approved design/interfaces/outcome/constraints; changed contracts require authorized affected design update first, not scope expansion
- Defer future features to future tasks

---

### Mockup Reference Guidelines (Frontend)

**When implementing frontend code:**

```
IF Technical Scope in specification.md includes [Frontend] OR [Full Stack]:
  1. MUST open and reference "Linked Mockups" from specification.md
  2. Keep mockup visible during frontend implementation
  3. Match implementation to mockup:
     - Component structure and hierarchy
     - Layout and positioning
     - Interactive elements and behaviors
     - Visual states (hover, active, disabled, error)
  4. Verify implementation visually matches mockup

ELSE (Backend/API Only/Database/Infrastructure):
  - Skip mockup reference
  - Implement based on technical design only
```

---

### Coverage vs. Complexity

**CRITICAL RULE: DO NOT make code complex just for test coverage!**

- Keep code simple and testable
- Target reasonable coverage (80%+), not 100% at all costs
- If code is hard to test, simplify the code
- Avoid testing implementation details

---

## Coding Standards

### General Standards

- Follow project coding standards
- Use linters and formatters
- Consistent naming conventions
- Meaningful variable/function names
- Document public APIs
- Handle errors appropriately

### Naming Conventions

| Type | Python | JavaScript/TypeScript |
|------|--------|----------------------|
| Variables | `snake_case` | `camelCase` |
| Functions | `snake_case` | `camelCase` |
| Classes | `PascalCase` | `PascalCase` |
| Constants | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| Private | `_leading_underscore` | `#private` or `_underscore` |

### Documentation Standards

```python
def create_user(user_data: dict) -> User:
    """
    Create a new user in the system.
    
    Args:
        user_data: Dictionary containing user fields (name, email, role)
    
    Returns:
        User: The created user object
    
    Raises:
        ValidationError: If required fields are missing
        DuplicateError: If email already exists
    """
```

---

## Error Handling Patterns

### Python Error Handling

```python
# ✅ GOOD: Specific exception handling
def get_user(user_id: str) -> User:
    try:
        user = db.find_user(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
    except DatabaseConnectionError as e:
        logger.error(f"Database error: {e}")
        raise ServiceUnavailableError("Database unavailable")

# ❌ BAD: Catching everything
def get_user(user_id: str) -> User:
    try:
        return db.find_user(user_id)
    except Exception:  # Too broad!
        return None
```

---

## Failure Handling Procedures

### Tool Skill Failure

```
1. Single tool skill fails:
   a. Retry ONCE with original scenarios + error context from first attempt
   b. IF retry succeeds → continue to next tool skill
   c. IF retry fails → preserve passing results, block affected delivery and resolve through actual mode (human asks human; full DAO and hybrid bounded guidance)

2. Multiple tool skills fail:
   a. Preserve results from passing tool skills
   b. Re-invoke ONLY failed tool skills
   c. IF still failing → block and resolve through actual mode with all attempts; guidance cannot make failed tests pass

3. AAA generation failure:
   a. FALLBACK to x-ipe-tool-test-generation (Phase 1 coexistence)
   b. Validate generated checks against every approved AC/original assertion; unresolved expectations block, never become invented scope
   c. Log warning: "AAA generation fell back to test-generation"

4. No tool skill match + general insufficient:
   a. Signal the bounded gap through actual policy: human asks human; full DAO and hybrid use common representative contract
   b. BLOCK affected implementation; do NOT continue ad hoc or invent a new tool task
```

### Integration Failure

```
1. @integration scenario fails after all unit-level tool skills pass:
   a. Unit-level passing evidence supports only the checks actually executed, not complete individual correctness
   b. Investigate the cross-layer contract, wiring, mocks and actual runtime behavior; do not assume the cause from unit passes
   c. Report: describe the mismatch, provide both outputs
   d. Resolve the specific conflict through actual mode; original expectations stay intact. Approved contract changes require affected design/change-log/CR authority and reruns
```

---

## Tracing Instrumentation

### Applicable Existing Tracing Only

```
1. IF existing tracing infrastructure and supported modified runtime functions are applicable, invoke x-ipe-tool-tracing-instrumentation; otherwise record a skip rationale, no implicit setup
   - Target: Applicable modified runtime files only
   
2. REVIEW proposed decorators:
   - Verify level assignments (INFO for public, DEBUG for helpers)
   - Verify sensitive params detected (password, token, secret, key)

3. APPLY decorators with sensitive parameter/log redaction and opt-in behavior; RE-RUN affected tests and refresh revision evidence

Skip Conditions:
- Skip if project has no tracing infrastructure (no x_ipe.tracing module)
- Skip for test files, configuration files, skill files (.md)
```

---

## Design Update Procedure

```
IF during implementation you discover design issues:

THEN:
   1. Determine whether means remain within approved design/contracts; compatible bounded choices need rationale, not ceremonial redesign. STOP affected work for contract/scope changes
   2. With actual authorized affected design/CR scope, UPDATE the existing technical-design.md:
     - Modify affected sections in Part 1 and/or Part 2
     - Append actual Version History/Design Change Log entry, preserve unaffected bytes/IDs and invalidate affected design/test/outcome/dependent evidence
  3. Refresh affected scenarios/TDD/regression/review, then RESUME within updated approved design

DO NOT:
  - Implement something different from the design without updating it
  - Skip the change log entry
```
