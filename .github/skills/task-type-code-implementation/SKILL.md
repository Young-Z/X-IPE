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

**⚠️ PRE-CODING VERIFICATION:**
Before writing ANY implementation code, agent MUST:
1. Run the test suite to confirm tests exist
2. Verify tests FAIL (proving no implementation yet)
3. If tests pass or don't exist → STOP and complete Test Generation first

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

### KISS (Keep It Simple, Stupid)

- Write simple, readable code
- No complex abstractions unless specified in design
- Use standard patterns from technical design
- Prefer clarity over cleverness
- If implementation seems complex, question the design

---

### YAGNI (You Aren't Gonna Need It)

- Implement ONLY what's in technical design
- No extra features "just in case"
- No "nice to have" additions
- If it's not in the design doc, don't implement it
- Defer future features to future tasks

---

### Test Driven Development (TDD)

**Workflow:**
```
1. Write test (RED - test fails)
2. Write minimum code to pass (GREEN - test passes)
3. Refactor if needed (REFACTOR - clean up)
4. Repeat
```

---

### 🎨 Mockup Reference (Conditional)

**When implementing frontend code:**
```
IF Technical Scope in specification.md includes [Frontend] OR [Full Stack]:
  1. MUST open and reference "Linked Mockups" from specification.md
  2. Keep mockup visible during frontend implementation
  3. Match implementation to mockup:
     - Component structure and hierarchy
     - Layout and positioning
     - Interactive elements and behaviors
     - Form fields and their validations
     - Visual states (hover, active, disabled, error)
  4. Verify implementation visually matches mockup
  5. Note any deviations and document reasons

ELSE (Backend/API Only/Database/Infrastructure):
  - Skip mockup reference
  - Implement based on technical design only
```

**Implementation Tip:**
For frontend work, implement in this order:
1. Component structure (HTML/JSX)
2. Styling (CSS) to match mockup
3. Interactivity (event handlers)
4. State management
5. API integration

---

### ⚠️ Coverage ≠ Complexity

**CRITICAL RULE: DO NOT make code complex just for test coverage!**

- Keep code simple and testable
- Target reasonable coverage (80%+), not 100% at all costs
- If code is hard to test, simplify the code
- Avoid testing implementation details
- Do NOT add parameters, abstractions, or indirection just to hit coverage metrics

**Good:**
```python
# Simple, testable function
def calculate_discount(price: float, percent: int) -> float:
    return price * (1 - percent / 100)
```

**Bad (DON'T DO THIS):**
```python
# Over-complicated just for "testability"
def calculate_discount(price, percent, 
                       logger=None, cache=None, 
                       event_bus=None, metrics=None):
    # Unnecessary complexity added for coverage
```

---

### Follow Coding Standards

- Follow project coding standards
- Use linters and formatters
- Consistent naming conventions
- Meaningful variable/function names
- Document public APIs
- Handle errors appropriately

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

**Action:** THOROUGHLY read and understand the technical design before writing any code

```
1. READ {technical_design_link} from Feature Data Model
   Location: x-ipe-docs/requirements/FEATURE-XXX/technical-design.md

2. UNDERSTAND Part 1 (Agent-Facing Summary):
   - Components to implement
   - Key interfaces and signatures
   - Scope and boundaries
   - Usage examples
   - Tags for context

3. UNDERSTAND Part 2 (Implementation Guide):
   - Data models (exact fields and types)
   - API endpoints (request/response formats)
   - Workflows (sequence and logic)
   - Implementation guidelines (specific notes)
   - Edge cases and error handling

4. NOTE any references to architecture designs

5. CHECK Design Change Log for any updates since initial design
```

**⚠️ STRICT REQUIREMENT:** 
- Do NOT start coding until you fully understand the technical design!
- Implementation MUST follow the technical design exactly
- If design is unclear, incomplete, or incorrect - STOP and update design first

---

### Step 2.1: Update Technical Design If Needed

**Action:** If implementation reveals design issues, UPDATE the design BEFORE proceeding

```
IF during implementation you discover:
  - Design is not working as expected
  - Better implementation approach exists
  - Design needs changes to support feature properly
  - Key component interfaces need modification

THEN:
  1. STOP implementation
  2. UPDATE technical-design.md:
     - Modify affected sections in Part 1 and/or Part 2
     - Add entry to Design Change Log:
       | Date | Phase | Change Summary |
       |------|-------|----------------|
       | {today} | Code Implementation | {What changed, why, impact ~100 words} |
  3. RESUME implementation with updated design

DO NOT:
  - Implement something different from the design without updating it
  - Make incompatible changes to key components without documenting
  - Skip the change log entry
```

---

### Step 3: Read Architecture Designs (If Referenced)

**Action:** If technical design mentions common architecture rules, READ them first

```
IF technical design references architecture components:
  1. READ x-ipe-docs/architecture/technical-designs/{component}.md
  2. UNDERSTAND:
     - Common patterns to follow
     - Required interfaces/protocols
     - Shared utilities to use
     - Integration requirements

COMMON REFERENCES:
  - Database patterns
  - API standards
  - Error handling conventions
  - Logging standards
  - Security patterns
  - Authentication/Authorization
```

**IMPORTANT:** Architecture designs define project-wide patterns. Follow them consistently!

---

### Step 4: Load Existing Tests from Test Generation (⚠️ MANDATORY)

**Action:** Verify tests from Test Generation are ready BEFORE any coding

```
1. LOCATE test files created by Test Generation task:
   - tests/unit/{feature}/
   - tests/integration/{feature}/
   - tests/api/{feature}/
   - tests/test_{feature}.py

2. RUN all tests to verify baseline:
   - pytest tests/ -v (Python)
   - npm test (Node.js)
   
3. VERIFY tests FAIL:
   - ⚠️ All feature-related tests should FAIL
   - This proves no implementation exists yet
   - Document: "X tests failing, 0 passing (TDD ready)"

4. IF tests pass:
   - STOP: Implementation may already exist
   - Review what code exists
   - Determine if this is a duplicate task

5. IF tests don't exist:
   - ⚠️ STOP immediately
   - Report: "Test Generation task not completed"
   - Go back to Test Generation task FIRST
   - Do NOT proceed without tests

6. UNDERSTAND what tests expect:
   - Review test assertions
   - Note expected inputs/outputs
   - Identify test structure
```

**⚠️ NO EXCEPTIONS:**
- Do NOT write any implementation code until Step 4 is complete
- Do NOT skip this step even if you "know" what to implement
- Tests MUST exist and MUST fail before proceeding

**TDD Workflow:**
```
RED → Tests fail (current state after Step 4)
GREEN → Write minimum code to pass (Step 5)
REFACTOR → Improve code quality
REPEAT → Until all tests pass
```

---

### Step 5: Implement Code

**Action:** Write minimum code to pass tests (following technical design)

**🌐 Web Search (As Needed):**
Use web search capability when you encounter:
- Library/framework API questions → Search official documentation
- Error messages → Search Stack Overflow, GitHub Issues
- Implementation patterns → Search for best practices
- Performance issues → Search for optimization techniques
- Security concerns → Search for secure coding practices

```
1. IMPLEMENT in order specified by technical design:
   - Data models
   - Business logic/services
   - API endpoints (if applicable)
   - Integration points

2. FOR EACH component:
   - Write code following technical design exactly
   - Run related tests
   - Verify tests pass (GREEN phase)
   - Refactor if needed (keep simple!)
   - Verify tests still pass

3. AVOID:
   - Adding features not in design
   - Over-engineering
   - Premature optimization
   - Complex abstractions
```

**Implementation Structure:**
```
src/
├── models/         # Data models from design
├── services/       # Business logic from design
├── routes/         # API endpoints from design (if applicable)
├── middleware/     # Cross-cutting concerns
└── utils/          # Helper functions
```

---

### Step 6: Verify & Ensure Quality

**Action:** Run all checks before completion

```
1. RUN all tests:
   - pytest tests/ -v (Python)
   - npm test (Node.js)

2. CHECK coverage (aim for 80%+, but don't add complexity for it):
   - pytest --cov=src tests/

3. RUN linter:
   - ruff check src/ tests/
   - flake8 src/ tests/
   - eslint src/ tests/

4. RUN formatter:
   - ruff format src/ tests/
   - black src/ tests/
   - prettier --write src/ tests/

5. VERIFY:
   - [ ] All tests pass
   - [ ] No linter errors
   - [ ] Code matches technical design
   - [ ] No extra features added
```

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
