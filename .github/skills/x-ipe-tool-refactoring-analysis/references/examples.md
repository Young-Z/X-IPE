# Refactoring Analysis Examples

## Example 1: API Module Refactoring Analysis

**Initial Request:** "Analyze src/api/users.py for refactoring"

### Step 1: Parse Initial Scope

```yaml
initial_refactoring_scope:
  files: [src/api/users.py]
  modules: [api.users]
  description: "Refactor user API module - too large"
  reason: "File is 800 lines, multiple responsibilities"
```

### Step 2: Scope Reflection Loop

**Iteration 1:**
```
Analyzing src/api/users.py...
- Imports: models/user.py, services/auth.py, utils/validation.py
- Imported by: routes/v1.py, tests/test_users.py

Added to scope:
- src/models/user.py (shared data model)
- src/services/auth.py (tight coupling - user auth)
- src/utils/validation.py (shared utilities)
```

**Iteration 2:**
```
Analyzing newly added files...
- src/services/auth.py imports: models/session.py
- src/models/user.py imported by: services/profile.py

Added to scope:
- src/models/session.py (related to auth flow)
```

**Iteration 3:**
```
No new dependencies found.
Scope expansion complete.
```

**Final refactoring_scope:**
```yaml
refactoring_scope:
  files:
    - src/api/users.py
    - src/models/user.py
    - src/models/session.py
    - src/services/auth.py
    - src/utils/validation.py
  modules: [api.users, models, services.auth, utils.validation]
  dependencies:
    - src/api/users.py → src/models/user.py
    - src/api/users.py → src/services/auth.py
    - src/services/auth.py → src/models/session.py
  scope_expansion_log:
    - iteration: 1
      files_added: [models/user.py, services/auth.py, utils/validation.py]
      reason: "Direct imports from target file"
    - iteration: 2
      files_added: [models/session.py]
      reason: "Auth service dependency"
    - iteration: 3
      files_added: []
      reason: "Stable - no new dependencies"
```

### Steps 3-6: Quality Evaluation

```yaml
code_quality_evaluated:
  requirements_alignment:
    status: aligned
    gaps: []
    related_docs: [x-ipe-docs/requirements/user-management.md]
    
  feature_alignment:
    status: needs_update
    gaps:
      - feature_id: FEATURE-012
        type: extra
        description: "Password reset logic not in feature spec"
    feature_ids: [FEATURE-012, FEATURE-015]
    
  technical_spec_alignment:
    status: needs_update
    gaps:
      - type: structure
        description: "Tech design shows UserService class, code uses functions"
        spec_location: "technical-design.md:45"
        code_location: "src/api/users.py:120"
    spec_docs: [x-ipe-docs/requirements/FEATURE-012/technical-design.md]
    
  test_coverage:
    status: insufficient
    current_percentage: 62
    target_percentage: 80
    file_coverage:
      - file: src/api/users.py
        line_coverage: 58
        untested_functions: [reset_password, bulk_update]
      - file: src/services/auth.py
        line_coverage: 75
        untested_functions: [refresh_token]
    critical_gaps:
      - file: src/api/users.py
        gap_type: business_logic
        description: "Password reset flow untested"
        
  overall_quality_score: 6
```

### Final Output

```
Refactoring Analysis Complete

Scope: 5 files, 4 modules
Expansions: 3 iterations

Quality Assessment:
- Requirements: ✅ Aligned
- Features: ⚠️ Needs Update (1 gap)
- Tech Spec: ⚠️ Needs Update (1 gap)
- Test Coverage: 62% (target: 80%)

Overall Score: 6/10

Approve to proceed to Validate Quality Before Refactoring?
```

---

## Example 2: No Documentation Scenario

**Initial Request:** "Analyze legacy/payment.js for refactoring"

```yaml
code_quality_evaluated:
  requirements_alignment:
    status: not_found
    gaps:
      - type: missing
        description: "No requirement documentation exists for payment module"
    related_docs: []
    
  feature_alignment:
    status: not_found
    gaps:
      - type: missing
        description: "Payment module has no associated feature documentation"
    feature_ids: []
    
  technical_spec_alignment:
    status: not_found
    gaps:
      - type: missing
        description: "No technical design document for payment processing"
    spec_docs: []
    
  test_coverage:
    status: no_tests
    current_percentage: 0
    target_percentage: 80
    critical_gaps:
      - file: legacy/payment.js
        gap_type: business_logic
        description: "Entire module untested"
        
  overall_quality_score: 3
```

**Recommendation:** Create documentation and tests before proceeding with refactoring.
