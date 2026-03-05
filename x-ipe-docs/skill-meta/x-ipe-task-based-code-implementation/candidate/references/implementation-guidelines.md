# Implementation Guidelines Reference

This document contains detailed implementation guidelines, coding standards, AAA scenario format specification, tool skill contract, and error handling patterns for the Code Implementation task type.

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
   a. Extract each acceptance criterion → create one @integration scenario per AC
      - Arrange = preconditions from AC context
      - Act = user action described in AC
      - Assert = expected outcome from AC

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
   - Every AC has ≥1 scenario
   - Every endpoint/component has both happy + sad path
   - Log coverage summary

5. IF context is large (>20 components):
   - Generate per-layer: all @backend first, then @frontend
   - Pass each batch to tool skills before generating next batch
```

### Context Budget Strategy (Large Features)

For features with >20 components:
1. Generate all @backend scenarios → invoke backend tool skill
2. Generate all @frontend scenarios → invoke frontend tool skill
3. Generate @integration scenarios → orchestrator validates with mocking

This prevents context overflow by processing one layer at a time.

---

## Tool Skill Input/Output Contract

### Input (Orchestrator → Tool Skill)

```yaml
tool_skill_input:
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
  feature_context:
    feature_id: "FEATURE-XXX-X"
    feature_title: "..."
    technical_design_link: "x-ipe-docs/requirements/EPIC-XXX/FEATURE-XXX-X/technical-design.md"
    specification_link: "x-ipe-docs/requirements/EPIC-XXX/FEATURE-XXX-X/specification.md"
```

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

---

## Implementation Principles (Detailed)

### KISS (Keep It Simple, Stupid)

**Core Principles:**
- Write simple, readable code
- No complex abstractions unless specified in design
- Use standard patterns from technical design
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
- If it's not in the design doc, don't implement it
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
   c. IF retry fails → preserve all other passing results, escalate to human

2. Multiple tool skills fail:
   a. Preserve results from passing tool skills
   b. Re-invoke ONLY failed tool skills
   c. IF still failing → escalate with details of all attempts

3. AAA generation failure:
   a. FALLBACK to x-ipe-tool-test-generation (Phase 1 coexistence)
   b. Use test-generation output as implementation guidance
   c. Log warning: "AAA generation fell back to test-generation"

4. No tool skill match + general insufficient:
   a. Signal human: "New tool skill needed for tech_stack entry: {entry}"
   b. Do NOT attempt ad-hoc implementation
```

### Integration Failure

```
1. @integration scenario fails after all unit-level tool skills pass:
   a. Both tool skill outputs are correct individually
   b. Cross-layer contract mismatch exists
   c. Report: describe the mismatch, provide both outputs
   d. Human decides: fix backend interface, frontend expectations, or both
```

---

## Tracing Instrumentation

### Step 7: Apply Tracing (Detailed)

```
1. INVOKE x-ipe-tool-tracing-instrumentation skill:
   - Target: All files modified/created in this implementation
   
2. REVIEW proposed decorators:
   - Verify level assignments (INFO for public, DEBUG for helpers)
   - Verify sensitive params detected (password, token, secret, key)

3. APPLY decorators and RE-RUN tests

Skip Conditions:
- Skip if project has no tracing infrastructure (no x_ipe.tracing module)
- Skip for test files, configuration files, skill files (.md)
```

---

## Design Update Procedure

```
IF during implementation you discover design issues:

THEN:
  1. STOP implementation
  2. UPDATE technical-design.md:
     - Modify affected sections in Part 1 and/or Part 2
     - Add entry to Design Change Log
  3. RESUME implementation with updated design

DO NOT:
  - Implement something different from the design without updating it
  - Skip the change log entry
```
