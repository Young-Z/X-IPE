# Validate Quality Before Refactoring Examples

## Example 1: Syncing Documentation for API Module

**Input from Refactoring Analysis:**
```yaml
refactoring_scope:
  files: [src/api/users.py, src/models/user.py, src/services/auth.py]
  modules: [api.users, models, services.auth]
  
code_quality_evaluated:
  requirements_alignment:
    status: needs_update
    gaps:
      - type: undocumented
        description: "Password reset with email verification"
        file: src/api/users.py
  feature_alignment:
    status: needs_update
    gaps:
      - feature_id: FEATURE-012
        type: extra
        description: "Bulk user import not in spec"
  technical_spec_alignment:
    status: needs_update
    gaps:
      - type: structure
        description: "Design shows class, code uses functions"
  test_coverage:
    status: insufficient
    current_percentage: 62
```

### Step 2: Sync Requirements

```
Processing requirement gaps...

Gap 1: undocumented - Password reset with email verification
→ Analyzing src/api/users.py:reset_password()
→ Found: Sends email, validates token, resets password
→ Creating requirement entry in x-ipe-docs/requirements/user-management.md

Added to requirements:
---
### Password Reset (Discovered Behavior)
*Documented from code during refactoring prep*

**Flow:**
1. User requests password reset with email
2. System sends reset token via email
3. User submits new password with token
4. System validates token and updates password

**Acceptance Criteria:**
- [x] Email sent within 5 seconds
- [x] Token expires after 24 hours
- [x] Password meets complexity requirements
---

requirements_alignment updated:
  status: aligned
  gaps: []
  updates_made:
    - doc: x-ipe-docs/requirements/user-management.md
      change: "Added Password Reset section"
```

### Step 3: Sync Features

```
Processing feature gaps...

Gap 1: extra - Bulk user import not in spec (FEATURE-012)
→ Asking human...

"Code has feature not in spec:
Bulk user import with CSV support
Options:
1. Add to specification
2. Mark for removal during refactoring"

Human chose: 1. Add to specification

→ Reading x-ipe-docs/requirements/FEATURE-012/specification.md
→ Adding acceptance criteria:

Added to specification:
---
### Bulk User Import

**User Story:** As an admin, I can import multiple users via CSV.

**Acceptance Criteria:**
- [ ] Accept CSV file upload
- [ ] Validate email format for all rows
- [ ] Report errors per row
- [ ] Create valid users
---

feature_alignment updated:
  status: aligned
  gaps: []
  updates_made:
    - doc: x-ipe-docs/requirements/FEATURE-012/specification.md
      change: "Added Bulk User Import section"
```

### Step 4: Sync Technical Design

```
Processing technical spec gaps...

Gap 1: structure - Design shows class, code uses functions
→ Reading x-ipe-docs/requirements/FEATURE-012/technical-design.md

Original design (Part 1):
```python
class UserService:
    def create_user(self, data): ...
    def get_user(self, id): ...
```

Actual code:
```python
def create_user(data): ...
def get_user(id): ...
```

→ Updating technical design to match code:

Updated design:
---
## User API Functions

The user module uses functional approach:

```python
# src/api/users.py
def create_user(data: UserCreate) -> User
def get_user(id: int) -> User
def update_user(id: int, data: UserUpdate) -> User
def delete_user(id: int) -> None
def reset_password(email: str) -> None
def bulk_import(file: UploadFile) -> ImportResult
```
---

Added to Design Change Log:
| Date | Phase | Change Summary |
| 2024-01-15 | Pre-Refactor Sync | Updated to functional pattern matching actual implementation |

technical_spec_alignment updated:
  status: aligned
  gaps: []
  updates_made:
    - doc: x-ipe-docs/requirements/FEATURE-012/technical-design.md
      change: "Updated to functional pattern"
```

### Step 5: Update Tests

```
Current coverage: 62%
Target: 80%

Analyzing critical gaps:
- src/api/users.py:reset_password - 0% covered
- src/api/users.py:bulk_import - 0% covered
- src/services/auth.py:refresh_token - 0% covered

Generating tests...

Created: tests/test_users_password.py
---
def test_reset_password_sends_email():
    # Test email is sent when valid user requests reset
    ...

def test_reset_password_invalid_email():
    # Test error when email not found
    ...

def test_reset_password_token_validation():
    # Test token validation flow
    ...
---

Created: tests/test_users_bulk.py
---
def test_bulk_import_valid_csv():
    # Test successful import
    ...

def test_bulk_import_invalid_rows():
    # Test partial failure handling
    ...
---

Running all tests... ✅ All pass

Running coverage...
- Before: 62%
- After: 84%

test_coverage updated:
  status: sufficient
  current_percentage: 84
  tests_added: 8
  tests_updated: 0
```

### Step 6: Final Output

```
Quality Validation Complete

Documentation Sync:
- Requirements: ✅ Aligned (1 update)
- Features: ✅ Aligned (1 update)
- Tech Design: ✅ Aligned (1 update)

Test Coverage: 62% → 84%
- Tests Added: 8
- All tests passing: ✅

Ready for Refactoring: ✅

Approve to proceed to Code Refactor V2?
```

**Updated code_quality_evaluated:**
```yaml
code_quality_evaluated:
  requirements_alignment:
    status: aligned
    gaps: []
    updates_made:
      - doc: x-ipe-docs/requirements/user-management.md
        change: "Added Password Reset section"
  feature_alignment:
    status: aligned
    gaps: []
    updates_made:
      - doc: x-ipe-docs/requirements/FEATURE-012/specification.md
        change: "Added Bulk User Import section"
  technical_spec_alignment:
    status: aligned
    gaps: []
    updates_made:
      - doc: x-ipe-docs/requirements/FEATURE-012/technical-design.md
        change: "Updated to functional pattern"
  test_coverage:
    status: sufficient
    current_percentage: 84
    tests_added: 8
    tests_updated: 0
  overall_quality_score: 10
  validation_summary:
    docs_created: 0
    docs_updated: 3
    tests_added: 8
    ready_for_refactoring: true
```

---

## Example 2: Creating Missing Documentation

**Input:**
```yaml
code_quality_evaluated:
  requirements_alignment:
    status: not_found
    gaps:
      - type: missing
        description: "No requirement documentation exists"
  feature_alignment:
    status: not_found
    gaps:
      - type: missing
        description: "No feature documentation exists"
  technical_spec_alignment:
    status: not_found
```

**Action:**
```
All documentation missing. Creating from code...

1. Analyzing code behavior...
   - Found: User CRUD operations
   - Found: Authentication flow
   - Found: Email notifications

2. Generating requirement doc:
   x-ipe-docs/requirements/user-module-requirements.md
   [Generated from code - requires review]

3. Generating feature spec:
   x-ipe-docs/requirements/FEATURE-NEW-001/specification.md
   [Generated from code - requires review]

4. Generating technical design:
   x-ipe-docs/requirements/FEATURE-NEW-001/technical-design.md
   [Generated from code - requires review]

⚠️ Note: All documentation was reverse-engineered from code.
Human review recommended before refactoring proceeds.
```
