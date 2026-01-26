# Test Generation - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Standard TDD Test Generation

**Context:**
- Feature: FEATURE-001 (User Authentication)
- Technical Design: `x-ipe-docs/requirements/FEATURE-001/technical-design.md`
- Project Type: Python Flask API

### Execution Flow

```
1. Execute Task Flow from task-execution-guideline skill

2. Read Technical Design:
   x-ipe-docs/requirements/FEATURE-001/technical-design.md
   
   Components Found:
   - AuthService: authenticate(), create_token(), verify_token()
   - UserRepository: create(), get_by_email(), update_password()
   - AuthMiddleware: require_auth() decorator

3. Identify Test Framework:
   - Check pyproject.toml → pytest configured
   - Check existing tests → pytest fixtures pattern

4. Generate Test File Structure:
   tests/test_auth.py
   
   ```python
   # Components under test from technical design:
   # - AuthService (authenticate, create_token, verify_token)
   # - UserRepository (create, get_by_email, update_password)  
   # - AuthMiddleware (require_auth decorator)
   
   import pytest
   from src.services.auth_service import AuthService
   from src.repositories.user_repository import UserRepository
   from src.middleware.auth_middleware import require_auth
   ```

5. Generate RED Tests (31 tests total):

   AuthService Tests (12):
   - test_authenticate_valid_credentials
   - test_authenticate_invalid_password
   - test_authenticate_nonexistent_user
   - test_authenticate_locked_account
   - test_create_token_generates_jwt
   - test_create_token_includes_user_id
   - test_create_token_has_expiry
   - test_verify_token_valid
   - test_verify_token_expired
   - test_verify_token_invalid_signature
   - test_verify_token_malformed
   - test_verify_token_missing_claims

   UserRepository Tests (11):
   - test_create_user_success
   - test_create_user_duplicate_email
   - test_create_user_invalid_email
   - test_create_user_hashes_password
   - test_get_by_email_exists
   - test_get_by_email_not_found
   - test_get_by_email_case_insensitive
   - test_update_password_success
   - test_update_password_wrong_current
   - test_update_password_same_password
   - test_update_password_weak_password

   AuthMiddleware Tests (8):
   - test_require_auth_valid_token
   - test_require_auth_missing_header
   - test_require_auth_invalid_format
   - test_require_auth_expired_token
   - test_require_auth_sets_current_user
   - test_require_auth_returns_401_on_failure
   - test_require_auth_skips_public_routes
   - test_require_auth_refreshes_near_expiry

6. Verify All Tests RED:
   $ pytest tests/test_auth.py --collect-only
   31 tests collected
   
   $ pytest tests/test_auth.py
   31 failed (expected - implementations don't exist yet)

7. Resume Task Flow from task-execution-guideline skill
```

### Output

```yaml
category: feature-stage
next_task_type: Code Implementation
require_human_review: No

test_summary:
  file: tests/test_auth.py
  total_tests: 31
  status: all_red
  framework: pytest
  
components_covered:
  - AuthService: 12 tests
  - UserRepository: 11 tests
  - AuthMiddleware: 8 tests

task_output_links:
  - tests/test_auth.py
```

---

## Example 2: Existing Test File - Incremental Addition

**Scenario:** Technical design updated with new component

```
1. Read Technical Design:
   - Existing: AuthService, UserRepository
   - NEW: PasswordResetService (added in CR)

2. Check Existing Tests:
   - tests/test_auth.py exists with 23 tests
   - No PasswordResetService tests

3. Add New Tests (without modifying existing):
   
   PasswordResetService Tests (7):
   - test_initiate_reset_sends_email
   - test_initiate_reset_unknown_email
   - test_initiate_reset_rate_limited
   - test_verify_reset_token_valid
   - test_verify_reset_token_expired
   - test_complete_reset_success
   - test_complete_reset_invalid_token

4. Verify:
   - Original 23 tests: unchanged
   - New 7 tests: all RED
   - Total: 30 tests

5. Output:
   tests_added: 7
   tests_modified: 0
   total_tests: 30
```

---

## Example 3: Missing Technical Design (Blocked)

**Scenario:** Feature assigned but no technical design

```
1. Check for Technical Design:
   - Expected: x-ipe-docs/requirements/FEATURE-003/technical-design.md
   - Result: FILE NOT FOUND

2. BLOCKED - Cannot proceed:
   "No technical design found for FEATURE-003.
    
    Cannot generate tests without component specifications.
    Required: x-ipe-docs/requirements/FEATURE-003/technical-design.md"

3. Status: blocked
   Reason: Missing technical design
   Required: Complete Technical Design task first
```

---

## Example 4: JavaScript/TypeScript Project

**Context:**
- Feature: FEATURE-010 (Dashboard)
- Technical Design exists
- Framework: React + Jest

```
1. Identify Test Framework:
   - Check package.json → jest, @testing-library/react
   - Pattern: __tests__/*.test.tsx

2. Generate Tests:
   __tests__/Dashboard.test.tsx
   
   Components Covered:
   - DashboardContainer: 5 tests
   - MetricsPanel: 8 tests  
   - ActivityFeed: 6 tests
   - useMetricsHook: 4 tests

3. Verify RED:
   $ npm test -- --collect-only
   23 tests found
   
   $ npm test
   23 failed (expected)

4. Output:
   test_file: __tests__/Dashboard.test.tsx
   total_tests: 23
   status: all_red
```
