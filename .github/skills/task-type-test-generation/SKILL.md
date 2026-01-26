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
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Test Generation |
| Category | feature-stage |
| Next Task Type | Code Implementation |
| Require Human Review | No |
| Feature Phase | Test Generation |

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
  next_task_type: Code Implementation
  require_human_review: No
  auto_proceed: {from input Auto Proceed}
  task_output_links: [tests/]
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Test Generation
  
  # Test generation specific
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

Execute Test Generation by following these steps in order:

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

### Step 2: Read Technical Design Document

**Action:** THOROUGHLY understand what to test

```
1. READ {technical_design_link} from Feature Data Model
   Location: x-ipe-docs/requirements/FEATURE-XXX/technical-design.md

2. EXTRACT testable components from Part 1 (Agent-Facing Summary):
   - Components and their scope
   - Key interfaces and method signatures
   - Usage examples (basis for test cases)
   - Tags for context

3. EXTRACT test details from Part 2 (Implementation Guide):
   - Data models (fields to validate)
   - API endpoints (request/response to test)
   - Workflows (sequences to verify)
   - Edge cases and error handling (negative test cases)

4. CHECK Design Change Log for any updates

5. NOTE any references to architecture designs

6. **🎨 CHECK Technical Scope for mockup-based tests:**
   ```
   IF Technical Scope includes [Frontend] OR [Full Stack]:
     a. Review "Linked Mockups" in specification.md
     b. Open mockup files to understand UI expectations
     c. Generate frontend-specific tests:
        - Component rendering tests
        - User interaction tests (click, input, submit)
        - Visual state tests (loading, error, success)
        - Form validation tests
        - Accessibility tests (if applicable)
     d. Reference mockup elements in test descriptions
   
   ELSE (Backend/API Only/Database):
     - Skip frontend/UI tests
     - Focus on unit tests, integration tests, API tests
   ```
```

**⚠️ STRICT REQUIREMENT:**
- Tests MUST be based on the technical design document
- All components in Part 1 must have corresponding tests
- All edge cases in Part 2 must have test coverage
- If design is unclear or incomplete - STOP and request design update first

---

### Step 3: Read Architecture Designs (If Referenced)

**Action:** If technical design mentions common architecture rules, understand them for testing

```
IF technical design references architecture components:
  1. READ x-ipe-docs/architecture/technical-designs/{component}.md
  2. UNDERSTAND:
     - Common patterns that need testing
     - Shared utilities to mock/stub
     - Integration requirements to verify

COMMON REFERENCES:
  - Database patterns → Test data access
  - API standards → Test request/response formats
  - Error handling → Test error cases
  - Authentication → Test auth flows
```

---

### Step 4: Read Feature Specification

**Action:** Get acceptance criteria for test cases

```
1. READ {specification_link} from Feature Data Model
   Location: x-ipe-docs/requirements/FEATURE-XXX/specification.md

2. EXTRACT acceptance criteria:
   - Each criterion becomes at least one test
   - Note edge cases documented
   - Note business rules to verify
```

---

### Step 5: Design Test Strategy

**Action:** Plan the complete test suite

**🌐 Web Search (Recommended):**
Use web search capability to research:
- Testing best practices for the technology stack
- Framework-specific testing patterns (pytest, jest, etc.)
- Mocking strategies for external services
- Test coverage strategies and industry standards
- Integration testing patterns
- API testing best practices

```
1. CATEGORIZE tests needed:

   UNIT TESTS (isolated components):
   - Each public method
   - Each data model validation
   - Each utility function
   
   INTEGRATION TESTS (component interactions):
   - Service → Repository
   - Controller → Service
   - Component A → Component B
   
   API TESTS (endpoint validation):
   - Each endpoint from technical design
   - Success responses
   - Error responses

2. PRIORITIZE:
   - Core functionality first
   - Happy path before edge cases
   - Critical paths before optional

3. DEFINE test data:
   - Mock data for unit tests
   - Fixtures for integration tests
   - Request/response samples for API tests
```

---

### Step 6: Generate Unit Tests

**Action:** Create unit tests for all components

**For each component/function from technical design:**

```
1. TEST happy path:
   - Valid inputs → Expected outputs
   - Normal conditions → Success

2. TEST edge cases:
   - Boundary values (min, max, zero)
   - Empty inputs
   - Maximum values

3. TEST error conditions:
   - Invalid inputs → Appropriate errors
   - Missing dependencies → Handled gracefully
   - Exception scenarios → Caught and reported
```

**Test Naming Convention:**
```
test_<function>_<scenario>_<expected_result>

Examples:
- test_authenticate_valid_credentials_returns_token
- test_authenticate_invalid_email_raises_error
- test_authenticate_expired_token_returns_401
```

**Test Structure (Arrange-Act-Assert):**
```python
def test_login_with_valid_credentials_returns_token(self):
    """AC: User receives JWT token on successful login"""
    # ARRANGE (Given)
    email = "user@test.com"
    password = "ValidPass123"
    
    # ACT (When)
    result = auth_service.authenticate(email, password)
    
    # ASSERT (Then)
    assert result.access_token is not None
    assert result.token_type == "Bearer"
```

---

### Step 7: Generate Integration Tests

**Action:** Create integration tests for component interactions

```
1. IDENTIFY integration points from technical design:
   - Service → Database/Repository
   - Controller → Service
   - Feature → External service

2. FOR EACH integration:
   - Test successful flow end-to-end
   - Test failure handling and recovery
   - Test timeout/retry behavior (if applicable)
```

---

### Step 8: Generate API Tests

**Action:** Create API tests for all endpoints from technical design

```
FOR EACH endpoint in technical design:

1. TEST success case:
   - Valid request → Expected response
   - Correct status code
   - Response body matches schema

2. TEST error cases:
   - Missing required fields → 400 Bad Request
   - Invalid data format → 400 Bad Request
   - Unauthorized → 401 Unauthorized
   - Not found → 404 Not Found

3. TEST edge cases:
   - Empty body
   - Extra fields (should be ignored or rejected)
   - Boundary values
```

---

### Step 9: Document Test Coverage

**Action:** Create test coverage summary

```
1. CREATE test coverage documentation:

   | Component | Unit Tests | Integration | API Tests |
   |-----------|------------|-------------|-----------|
   | AuthService | 8 | 2 | - |
   | TokenManager | 5 | - | - |
   | UserRepository | 4 | 3 | - |
   | /login endpoint | - | - | 4 |
   | /logout endpoint | - | - | 3 |
   | **TOTAL** | **17** | **5** | **7** |

2. DOCUMENT test data:
   - Mock data definitions
   - Test fixtures created
   - Setup/teardown requirements
```

---

### Step 10: Verify Tests Fail (TDD Ready)

**Action:** Run all tests to establish baseline

```
1. RUN all tests:
   pytest tests/ -v

2. VERIFY all tests FAIL:
   - Expected: X tests failing, 0 passing
   - Failure reason: Missing implementation (not test errors)

3. FIX any test syntax/setup issues:
   - Tests should fail because code doesn't exist
   - NOT because tests have bugs

4. RECORD baseline:
   baseline_status: "29 tests failing, 0 passing (TDD ready)"
```

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

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: API Feature

**When:** Feature includes REST endpoints
**Then:**
```
1. Unit tests for service layer
2. Integration tests for full flow
3. API tests for each endpoint
4. Test auth and error responses
```

### Pattern: Background Service

**When:** Feature runs as async/background process
**Then:**
```
1. Unit tests for core logic
2. Mock external dependencies
3. Test timeout and retry behavior
4. Verify cleanup on failure
```

### Pattern: Data Processing

**When:** Feature processes/transforms data
**Then:**
```
1. Test with valid input → expected output
2. Test with edge cases (empty, null, max)
3. Test with invalid input → proper errors
4. Use parameterized tests for variations
```

---

## Test File Structure

```
tests/
├── unit/                    # Unit tests (isolated)
│   ├── services/
│   │   └── auth_service_test.py
│   ├── models/
│   │   └── user_test.py
│   └── utils/
│       └── token_utils_test.py
├── integration/             # Integration tests
│   └── auth_flow_test.py
├── api/                     # API tests
│   └── auth_api_test.py
├── fixtures/                # Shared test data
│   └── users.py
└── conftest.py              # Test configuration
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip reading design | Tests miss requirements | Read technical design first |
| Test implementation details | Brittle, breaks on refactor | Test behavior only |
| One giant test | Hard to debug failures | One assertion per test |
| Test private methods | Couples to internals | Test via public interface |
| Skip edge cases | Bugs hide in edges | Prioritize edge cases |
| Hardcoded test data | Hard to maintain | Use test fixtures |
| Tests pass initially | Not TDD | Ensure tests fail first |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Standard TDD test generation (31 tests across 3 levels)
- Incremental addition to existing test file
- Missing technical design (blocked)
- JavaScript/TypeScript project with Jest

---

## Notes

- Work on ONE feature at a time (feature_id from task_data)
- Query feature board FIRST to get context
- Read technical design THOROUGHLY before writing tests
- Read architecture designs IF referenced
- Create ALL tests before Code Implementation starts
- Verify tests FAIL (TDD ready state)
- Output feature_phase = "Test Generation" for correct board update
- Code Implementation will use these tests to drive development
