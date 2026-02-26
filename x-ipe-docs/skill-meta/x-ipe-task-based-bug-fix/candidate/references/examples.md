# Bug Fix Skill — Examples

## Example 1: Simple Bug Fix (No Conflicts)

**Bug Report:** "Login fails with 'invalid token' error"

**Execution:**
```
1. Step 1 - Understand:
   - Expected: User logs in successfully
   - Actual: Error "invalid token" on login
   - Severity: High (feature broken)

2. Step 2 - Reproduce:
   - Go to login page, enter valid credentials, click login
   - Error appears — Reproduced

3. Step 3 - Diagnose:
   - Error in: authService.validateToken()
   - Root cause: Token expiry check uses > instead of >=
   - Tokens expiring at exact boundary fail

4. Step 4 - Design Fix:
   - Option A: Change > to >= (1 line, low risk) — Selected
   - Option B: Add grace period (more changes)

5. Step 5 - Conflict Analysis:
   - Conflict Detector: Analyzed validateToken() callers (loginHandler, refreshHandler, apiMiddleware)
   - No conflicts found — the >= change only makes boundary tokens valid (strictly additive)
   - Proceed directly to Step 6

6. Step 6 - Write Test:
   - Add test: test_token_at_exact_expiry_boundary()
   - Run test: FAILS (confirms bug)

7. Step 7 - Implement:
   - Fix: token.expiry > now → token.expiry >= now
   - Run new test: PASSES
   - Run all tests: 156/156 pass

8. Step 8 - Verify:
   - Reproduction steps: Now works
   - Full test suite: 156/156 pass

Output Result:
  category: standalone
  next_task_based_skill: null
  require_human_review: yes
  bug_severity: High
  root_cause: "Token expiry boundary check used > instead of >="
  conflicts_found: []
  task_output_links:
    - src/auth/tokenValidator.js
    - tests/auth/tokenValidator.test.js
```

---

## Example 2: Bug Fix with Unexpected Conflict

**Bug Report:** "Password validation allows empty passwords"

**Execution:**
```
1. Step 1 - Understand:
   - Expected: Login rejects empty password
   - Actual: Empty password is accepted, login succeeds
   - Severity: High (security issue)

2. Step 2 - Reproduce:
   - Go to login, enter username, leave password empty, click login
   - Login succeeds — Reproduced

3. Step 3 - Diagnose:
   - Root cause: validateCredentials() has no minimum length check
   - Password is passed directly to bcrypt.compare() which returns true for empty hash

4. Step 4 - Design Fix:
   - Option A: Add password.length > 0 check in validateCredentials() — Selected
   - Option B: Add check at form level

5. Step 5 - Conflict Analysis:
   - Conflict Detector: Analyzed validateCredentials() callers
     - Found: guestLoginHandler() deliberately passes empty password for guest access
     - CONFLICT: Fix would break guest login feature
   - Conflict Validator: Checked against user's original request
     - User said "password validation allows empty passwords" — refers to regular login
     - Guest login using empty password is a separate, intentional feature
     - Classification: UNEXPECTED — user didn't intend to break guest login
   - Presented to user: "The fix would also block guest login, which uses empty
     passwords intentionally. Should we: (a) only apply the check to regular login,
     or (b) also require guests to have passwords?"
   - User clarified: "Only regular login, guest should still work"
   - Returned to Step 4 with updated understanding

   Revised Step 4 - Design Fix:
   - Option A (revised): Add password.length > 0 check ONLY in regularLoginHandler(),
     not in shared validateCredentials() — Selected

   Revised Step 5 - Conflict Analysis:
   - No conflicts — fix is scoped to regularLoginHandler() only
   - Proceed to Step 6

6. Step 6 - Write Test:
   - Add test: test_regular_login_rejects_empty_password()
   - Add test: test_guest_login_still_works_with_empty_password()
   - Run tests: Both structured correctly, first FAILS (confirms bug)

7. Step 7 - Implement:
   - Fix: Add if (!password || password.length === 0) in regularLoginHandler()
   - Run new tests: Both PASS
   - Run all tests: 158/158 pass

8. Step 8 - Verify:
   - Empty password on regular login: Now rejected ✓
   - Guest login: Still works ✓
   - Full test suite: 158/158 pass

Output Result:
  category: standalone
  bug_severity: High
  root_cause: "No minimum length check on password in regular login flow"
  conflicts_found:
    - "guestLoginHandler() uses empty password intentionally — scoped fix to regularLoginHandler() only"
  task_output_links:
    - src/auth/regularLoginHandler.js
    - tests/auth/loginValidation.test.js
```
