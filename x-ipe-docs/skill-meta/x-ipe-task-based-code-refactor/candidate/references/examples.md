# Code Refactor V2 Examples

## Example 1: Splitting a Large API Module

**Inputs:**
```yaml
refactoring_scope:
  files: [src/api/users.py]  # 800 lines
  modules: [api.users]
  
refactoring_requirement:
  goals: 
    - Split large file into smaller modules
    - Improve cohesion
    - Apply Single Responsibility Principle
  constraints:
    - Maintain backward compatibility
    - No behavior changes
  principles: [SOLID, DRY]
  target_structure: "Separate modules for CRUD, auth, and bulk operations"
```

### Step 1: Reflect on Context

```yaml
context_map:
  files:
    - path: src/api/users.py
      requirements:
        - x-ipe-docs/requirements/user-management.md
      features:
        - FEATURE-012 (User Management)
        - FEATURE-015 (Bulk Operations)
      tech_specs:
        - x-ipe-docs/requirements/FEATURE-012/technical-design.md
      
      code_sections:
        - lines 1-150: User CRUD operations
        - lines 151-300: Authentication helpers
        - lines 301-500: Password management
        - lines 501-650: Bulk operations
        - lines 651-800: Utility functions
```

### Step 2: Generate Refactoring Plan

```yaml
refactoring_plan:
  phases:
    - phase: 1
      name: "Extract User CRUD"
      changes:
        - type: create
          to: src/api/users/crud.py
          reason: "Single responsibility - CRUD operations"
        - type: move
          from: src/api/users.py:1-150
          to: src/api/users/crud.py
          reason: "Extract user CRUD functions"
      risk: low
      tests_affected: [tests/test_users.py]
      
    - phase: 2
      name: "Extract Authentication"
      changes:
        - type: create
          to: src/api/users/auth.py
          reason: "Single responsibility - auth operations"
        - type: move
          from: src/api/users.py:151-300
          to: src/api/users/auth.py
          reason: "Extract auth helpers"
      risk: low
      tests_affected: [tests/test_users.py, tests/test_auth.py]
      
    - phase: 3
      name: "Extract Password Management"
      changes:
        - type: create
          to: src/api/users/password.py
          reason: "Single responsibility - password ops"
        - type: move
          from: src/api/users.py:301-500
          to: src/api/users/password.py
          reason: "Extract password functions"
      risk: medium
      tests_affected: [tests/test_users.py]
      
    - phase: 4
      name: "Extract Bulk Operations"
      changes:
        - type: create
          to: src/api/users/bulk.py
          reason: "Single responsibility - bulk ops"
        - type: move
          from: src/api/users.py:501-650
          to: src/api/users/bulk.py
          reason: "Extract bulk functions"
      risk: low
      tests_affected: [tests/test_bulk.py]
      
    - phase: 5
      name: "Create Re-export Hub"
      changes:
        - type: create
          to: src/api/users/__init__.py
          reason: "Backward compatibility - re-export all"
      risk: low
      
  estimated_changes:
    files_modified: 1
    files_created: 5
    files_deleted: 0
```

**Human approves plan.**

### Step 3: Execute Refactoring

**Phase 1: Extract User CRUD**
```
checkpoint: git commit -m "checkpoint: before refactor phase 1 - Extract User CRUD"

Creating src/api/users/crud.py...
Moving user CRUD functions...
Updating imports...

Running tests... ✅ All pass

git commit -m "refactor(users): extract CRUD operations to crud.py"
```

**Phase 2: Extract Authentication**
```
checkpoint: git commit -m "checkpoint: before refactor phase 2 - Extract Authentication"

Creating src/api/users/auth.py...
Moving auth functions...
Updating imports...

Running tests... ✅ All pass

git commit -m "refactor(users): extract auth helpers to auth.py"
```

**Phase 3: Extract Password Management**
```
checkpoint: git commit -m "checkpoint: before refactor phase 3 - Extract Password Management"

Creating src/api/users/password.py...
Moving password functions...
Updating imports...

Running tests... ❌ 1 failure

Analyzing failure:
- test_reset_password ImportError: cannot import 'reset_password' from 'api.users'

Fixing: Update import in test file
- from api.users import reset_password
+ from api.users.password import reset_password

Running tests... ✅ All pass

git commit -m "refactor(users): extract password management to password.py"
```

**Phase 4 & 5 continue similarly...**

### Step 4: Update References

```
Updating technical design...

x-ipe-docs/requirements/FEATURE-012/technical-design.md:
---
## User API Structure

```
src/api/users/
├── __init__.py      # Re-exports for backward compatibility
├── crud.py          # User CRUD operations
├── auth.py          # Authentication helpers
├── password.py      # Password management
├── bulk.py          # Bulk operations
└── utils.py         # Shared utilities
```

### Design Change Log
| Date | Phase | Change Summary |
| 2024-01-15 | Code Refactor V2 | Split users.py (800 lines) into 5 modules. Applied SRP. No behavior changes. |
---

references_updated:
  requirements: []
  features: [x-ipe-docs/requirements/FEATURE-012/specification.md]
  technical_designs: [x-ipe-docs/requirements/FEATURE-012/technical-design.md]
```

### Step 5: Validate and Complete

```
Final test suite... ✅ All 47 tests pass

Quality Assessment:

| Dimension | Before | After | Change |
|-----------|--------|-------|--------|
| Readability | 5 | 8 | +3 |
| Maintainability | 4 | 9 | +5 |
| Testability | 6 | 9 | +3 |
| Cohesion | 3 | 10 | +7 |
| Coupling | 5 | 7 | +2 |

Overall Quality:
- Before: 4.6/10
- After: 8.6/10
- Improvement: +4.0

Test Coverage:
- Before: 84%
- After: 86%
- Status: improved

Refactoring Summary:
- Files modified: 1 (tests)
- Files created: 5
- Files deleted: 0
- Tests updated: 3
- Principles applied: [SRP, DRY]

Human approves completion.

git commit -m "refactor: Complete users module split - quality 4.6 → 8.6"
```

**Final Output:**
```yaml
refactoring_summary:
  files_modified: 1
  files_created: 5
  files_deleted: 0
  tests_updated: 3
  principles_applied: [SRP, DRY]
  
code_quality_evaluated:
  quality_score_before: 4.6
  quality_score_after: 8.6
  improvements:
    - category: readability
      before: 5
      after: 8
    - category: maintainability
      before: 4
      after: 9
    - category: testability
      before: 6
      after: 9
    - category: cohesion
      before: 3
      after: 10
    - category: coupling
      before: 5
      after: 7
  test_coverage:
    before: 84
    after: 86
    status: improved
  references_updated:
    requirements: []
    features: [x-ipe-docs/requirements/FEATURE-012/specification.md]
    technical_designs: [x-ipe-docs/requirements/FEATURE-012/technical-design.md]
```

---

## Example 2: Rollback Scenario

**During Phase 3 of refactoring:**

```
Moving function to new module...

Running tests... ❌ 5 failures

Analyzing failures:
- All assertion errors, not import errors
- Functions returning different results

Diagnosis: Behavior changed during refactoring (bug introduced)

Action: ROLLBACK
git checkout HEAD~1

Revising plan:
- Original plan moved helper function without its dependency
- Updated plan: Move both function AND helper together

Retry Phase 3 with corrected plan...
Running tests... ✅ All pass

Continue with remaining phases.
```
