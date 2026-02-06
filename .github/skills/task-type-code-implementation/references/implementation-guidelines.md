# Implementation Guidelines Reference

This document contains detailed implementation guidelines, coding standards, TDD workflow examples, and error handling patterns for the Code Implementation task type.

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

**Examples:**
```python
# ✅ GOOD: Only what's needed
class UserService:
    def create_user(self, data):
        # Only the create operation needed now
        pass

# ❌ BAD: Features for "later"
class UserService:
    def create_user(self, data): pass
    def bulk_create_users(self, data_list): pass  # Not in design!
    def import_users_from_csv(self, file): pass   # Not in design!
```

---

### Test Driven Development (TDD) Workflow

**The Red-Green-Refactor Cycle:**

```
┌─────────────────────────────────────────────────────────────┐
│  1. RED: Write a failing test                               │
│     ↓                                                        │
│  2. GREEN: Write minimum code to pass the test              │
│     ↓                                                        │
│  3. REFACTOR: Improve code quality while keeping tests green│
│     ↓                                                        │
│  4. REPEAT: Next test case                                  │
└─────────────────────────────────────────────────────────────┘
```

**Detailed TDD Example:**

```python
# Step 1: RED - Write failing test
def test_calculate_discount_applies_percentage():
    result = calculate_discount(100, 20)
    assert result == 80.0

# Run: pytest -v → FAILS (no implementation yet)

# Step 2: GREEN - Minimum code to pass
def calculate_discount(price: float, percent: int) -> float:
    return price * (1 - percent / 100)

# Run: pytest -v → PASSES

# Step 3: REFACTOR - Clean up if needed (in this case, already clean)
# Step 4: REPEAT - Next test case
def test_calculate_discount_zero_percent():
    result = calculate_discount(100, 0)
    assert result == 100.0
```

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
     - Form fields and their validations
     - Visual states (hover, active, disabled, error)
  4. Verify implementation visually matches mockup
  5. Note any deviations and document reasons

ELSE (Backend/API Only/Database/Infrastructure):
  - Skip mockup reference
  - Implement based on technical design only
```

**Implementation Order for Frontend:**
1. Component structure (HTML/JSX)
2. Styling (CSS) to match mockup
3. Interactivity (event handlers)
4. State management
5. API integration

---

### Coverage vs. Complexity

**CRITICAL RULE: DO NOT make code complex just for test coverage!**

- Keep code simple and testable
- Target reasonable coverage (80%+), not 100% at all costs
- If code is hard to test, simplify the code
- Avoid testing implementation details
- Do NOT add parameters, abstractions, or indirection just to hit coverage metrics

**Good Example:**
```python
# Simple, testable function
def calculate_discount(price: float, percent: int) -> float:
    return price * (1 - percent / 100)
```

**Bad Example (DON'T DO THIS):**
```python
# Over-complicated just for "testability"
def calculate_discount(price, percent, 
                       logger=None, cache=None, 
                       event_bus=None, metrics=None):
    # Unnecessary complexity added for coverage
```

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

### Error Response Format (APIs)

```python
# Standard error response structure
{
    "error": {
        "code": "USER_NOT_FOUND",
        "message": "User with ID 123 not found",
        "details": {}
    }
}
```

---

## Implementation Structure

### Standard Project Layout

```
src/
├── models/         # Data models from design
├── services/       # Business logic from design
├── routes/         # API endpoints from design (if applicable)
├── middleware/     # Cross-cutting concerns
└── utils/          # Helper functions
```

### Implementation Order

1. **Data Models** - Define entities and their relationships
2. **Business Logic/Services** - Core functionality
3. **API Endpoints** - Route handlers (if applicable)
4. **Integration Points** - External service connections

---

## Step-by-Step Procedure Details

### Step 4: Load Tests (Detailed)

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

### Step 5: Implement Code (Detailed)

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

### Step 6: Verify & Ensure Quality (Detailed)

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

## Tracing Instrumentation

### Step 7: Apply Tracing (Detailed)

```
1. INVOKE tool-tracing-instrumentation skill:
   - Target: All files modified/created in this implementation
   - Example: "Add tracing to src/x_ipe/services/new_service.py"

2. REVIEW proposed decorators:
   - Verify level assignments (INFO for public, DEBUG for helpers)
   - Verify sensitive params detected (password, token, secret, key)
   - Approve or modify as needed

3. APPLY decorators:
   - Let skill add @x_ipe_tracing decorators
   - Let skill add imports if missing

4. RE-RUN tests to ensure decorators don't break functionality:
   - pytest tests/ -v
```

**Skip Conditions:**
- Skip if project has no tracing infrastructure (no `x_ipe.tracing` module)
- Skip for test files (test_*.py)
- Skip for configuration files

### Tracing Levels

| Level | Use For |
|-------|---------|
| INFO | Public APIs, endpoints, key business functions |
| DEBUG | Helper functions, internal utilities |

### Sensitive Parameter Handling

```python
# Parameters to redact: password, token, secret, key, credential, auth
@x_ipe_tracing(level="INFO", redact=["password", "token"])
def login(username: str, password: str, token: str) -> User:
    pass
```

---

## Web Search Guidelines

**Use web search capability when you encounter:**
- Library/framework API questions → Search official documentation
- Error messages → Search Stack Overflow, GitHub Issues
- Implementation patterns → Search for best practices
- Performance issues → Search for optimization techniques
- Security concerns → Search for secure coding practices

---

## Design Update Procedure

**If implementation reveals design issues, UPDATE the design BEFORE proceeding:**

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
