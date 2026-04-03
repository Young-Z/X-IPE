# Change Request - Examples

> **Legacy Note:** Examples below use the Epic-aware folder structure (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`). Projects created before the Epic migration may still use the legacy format (`FEATURE-{nnn}/`). Both formats are supported during the transition period.

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Bulk Import Feature Change Request

**Request:** "Add bulk import functionality to the existing product management module"

### CR Classification

```
Step 3.1: Read Change Request
  change_request: "Add bulk import to product management"

Step 3.2: Identify Affected Features
  - Search features.json (via x-ipe-tool-task-board-manager) for "product management"
  - Found: FEATURE-012 (Product Management Module)
  - Check if bulk import exists → Not found

Step 3.3: Classify Scope
  Questions:
  1. Does this require entirely new components? → Yes, import service
  2. Does this significantly expand feature scope? → Yes, new capability
  3. Are there new user stories? → Yes, "As admin, I can import CSV"
  4. Estimated complexity? → High (parsing, validation, error handling)
  
  Classification: NEW_FEATURE
```

### Conflict Analysis (Step 4)

```
Step 4.1: Spawn Conflict Detector
  - Read FEATURE-012 specification (product management)
  - No other features depend on FEATURE-012's data model
  - No pending CRs for FEATURE-012
  
  Conflicts found: 0

Step 4.2: No conflicts → proceed to Human Approval
```

### Output

```yaml
category: Standalone
next_task_based_skill: Feature Breakdown
require_human_review: Yes

cr_classification: NEW_FEATURE
conflicts_found: []
conflicts_resolution: none
reasoning: |
  Bulk import requires:
  - New ImportService component
  - CSV parsing logic
  - Validation pipeline
  - Error handling and reporting
  - New API endpoints
  - New UI components
  This significantly expands the scope beyond the existing feature.
  
affected_artifacts:
  - x-ipe-docs/planning/features/features.json (new feature to add)
  - x-ipe-docs/requirements/EPIC-013/FEATURE-013-A/ (new folder to create)

task_output_links:
  - x-ipe-docs/requirements/EPIC-013/FEATURE-013-A/ (pending creation in Feature Breakdown)
```

---

## Example 2: UI Refinement - ENHANCEMENT Classification

**Request:** "Make the settings page auto-save instead of requiring a save button"

### CR Classification

```
Step 3.1: Read Change Request
  change_request: "Auto-save settings page"

Step 3.2: Identify Affected Features
  - Search features.json (via x-ipe-tool-task-board-manager) for "settings"
  - Found: FEATURE-005 (User Settings)
  
Step 3.3: Classify Scope
  Questions:
  1. Entirely new components? → No, modifying existing SettingsService
  2. Expand feature scope? → No, same functionality with UX improvement
  3. New user stories? → No, same goal "user saves preferences"
  4. Estimated complexity? → Medium (debouncing, state management)
  
  Classification: ENHANCEMENT
```

### Conflict Analysis (Step 4)

```
Step 4.1: Spawn Conflict Detector
  - Read FEATURE-005 specification
  - Read FEATURE-005 technical design
  - Check features depending on FEATURE-005: FEATURE-010 (Dashboard) uses saved settings
  - Spec conflict: none (settings data model unchanged)
  - Design conflict: none (SettingsService API contract preserved)
  - Dependency conflict: none (FEATURE-010 reads settings, not writes)
  
  Conflicts found: 0

Step 4.2: No conflicts → proceed to Human Approval
```

### Output

```yaml
category: Standalone
next_task_based_skill: Feature Refinement
require_human_review: Yes

cr_classification: ENHANCEMENT
conflicts_found: []
conflicts_resolution: none
reasoning: |
  Auto-save modifies existing behavior without adding new capabilities.
  Same user goal, improved UX implementation.
  
affected_artifacts:
  - x-ipe-docs/requirements/EPIC-005/FEATURE-005-A/specification.md
  - x-ipe-docs/requirements/EPIC-005/FEATURE-005-A/technical-design.md

task_output_links:
  - x-ipe-docs/requirements/EPIC-005/FEATURE-005-A/specification.md (to update)
```

---

## Example 3: CR with Dependency Conflict

**Request:** "Change the user profile data model to use a flat structure instead of nested objects"

### CR Classification

```
Step 3.1: Read Change Request
  change_request: "Flatten user profile data model"

Step 3.2: Identify Affected Features
  - Found: FEATURE-003 (User Profile Management)
  - FEATURE-003 is used by: FEATURE-007 (User Search), FEATURE-010 (Dashboard), FEATURE-015 (Admin Panel)
  
Step 3.3: Classify Scope
  - Modifies existing data model within same feature → MODIFICATION
```

### Conflict Analysis (Step 4)

```
Step 4.1: Spawn Conflict Detector
  - Read FEATURE-003 specification and technical design
  - Read FEATURE-007 specification: uses profile.address.city for location search
  - Read FEATURE-010 specification: renders profile.preferences.theme
  - Read FEATURE-015 specification: bulk-edits profile.permissions.roles[]

  Conflicts found: 3
    1. SPEC CONFLICT: FEATURE-007 acceptance criteria references "profile.address.city"
       → Flattening would change to "profile_address_city", breaking AC-007-03
       Severity: High
    2. DESIGN CONFLICT: FEATURE-010 technical design uses nested destructuring
       → Code assumes nested structure: const { preferences: { theme } } = profile
       Severity: Medium
    3. DEPENDENCY CONFLICT: FEATURE-015 bulk edit logic iterates profile.permissions.roles[]
       → Flattening arrays requires different iteration pattern
       Severity: High

Step 4.2: Classify conflicts
  - Conflict 1: "expected" — flattening necessarily changes field paths
  - Conflict 2: "expected" — code changes are implied by data model change
  - Conflict 3: "unexpected" — CR did not mention changing array handling, this is a side effect

Step 4.3: Unexpected conflict found
  - Present to human: "Flattening the profile model would also require changing
    how FEATURE-015 (Admin Panel) handles role arrays. The current nested
    profile.permissions.roles[] would become profile_permissions_roles (a single
    field), losing array semantics."
  - Suggest mitigation: "Consider a hybrid approach — flatten scalar fields but
    preserve nested arrays. Or create a separate CR for FEATURE-015 admin panel."
```

### Human Decision

```
Human: "Keep arrays nested, only flatten scalar fields. Update the CR scope."
→ Return to Step 3 with narrowed scope
→ Re-run conflict analysis: all remaining conflicts now "expected"
```

### Output

```yaml
category: Standalone
next_task_based_skill: Feature Refinement
require_human_review: Yes

cr_classification: MODIFICATION
conflicts_found:
  - feature: FEATURE-007
    type: specification
    severity: high
    classification: expected
    description: "Field path references change from nested to flat"
  - feature: FEATURE-010
    type: design
    severity: medium
    classification: expected
    description: "Technical design code patterns change"
conflicts_resolution: mitigated
reasoning: |
  Data model flattening for scalar fields only (arrays preserved).
  Scope narrowed after conflict analysis revealed array handling issues.
  
affected_artifacts:
  - x-ipe-docs/requirements/EPIC-003/FEATURE-003-A/specification.md
  - x-ipe-docs/requirements/EPIC-007/FEATURE-007-A/specification.md (AC updates)
  - x-ipe-docs/requirements/EPIC-010/FEATURE-010-A/technical-design.md (code pattern updates)
```

---

## Example 4: Ambiguous Request - Human Decision Required

**Request:** "We need better error handling"

### CR Classification

```
Step 3.1: Read Change Request
  change_request: "better error handling"
  → Too vague to classify

Step 3.2: Identify Affected Features
  - "error handling" could apply to multiple features
  - Cannot determine specific feature

Step 3.3: Request Clarification
  Questions for human:
  1. Which module needs better error handling?
  2. What specific errors are not being handled?
  3. Is this about user-facing messages or logging?
  
Human Response: "The file upload feature doesn't show error details"

Step 3.2 (retry): 
  - Found: FEATURE-008 (File Upload)

Step 3.3: Classify Scope
  - Just improving error messages → ENHANCEMENT
  
Step 3.4: Route CR
  - Classification: ENHANCEMENT
  - Next Task: Feature Refinement
```

---

## Example 5: Bug Report - NOT a Change Request

**Request:** "The login page crashes on Safari"

### CR Classification

```
Step 3.1: Read Change Request
  change_request: "login page crashes on Safari"

Step 3.2: Analyze Request Type
  - This describes broken existing functionality
  - Not a new feature or enhancement
  - This is a BUG, not a Change Request

Step 3.3: Redirect to Bug Fix
  Response: "This appears to be a bug report, not a change request.
             Switching to Bug Fix task type."

Step 3.4: Route to Bug Fix
  → Hand off to x-ipe-task-based-bug-fix skill
```

### Output

```yaml
cr_classification: NOT_A_CR
redirect_to: Bug Fix
reasoning: "Describes broken functionality, not a change request"
```
