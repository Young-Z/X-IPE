# Change Request - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Bulk Import Feature Change Request

**Request:** "Add bulk import functionality to the existing product management module"

### CR Classification

```
Step 3.1: Read Change Request
  change_request: "Add bulk import to product management"

Step 3.2: Identify Affected Features
  - Search features.md for "product management"
  - Found: FEATURE-012 (Product Management Module)
  - Check if bulk import exists → Not found

Step 3.3: Classify Scope
  Questions:
  1. Does this require entirely new components? → Yes, import service
  2. Does this significantly expand feature scope? → Yes, new capability
  3. Are there new user stories? → Yes, "As admin, I can import CSV"
  4. Estimated complexity? → High (parsing, validation, error handling)
  
  Classification: NEW_FEATURE

Step 3.4: Route CR
  - Classification: NEW_FEATURE
  - Action: Create FEATURE-013
  - Next Task: Feature Breakdown
```

### Output

```yaml
category: Standalone
next_task_type: Feature Breakdown
require_human_review: Yes

cr_classification: NEW_FEATURE
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
  - x-ipe-docs/planning/features.md (new feature to add)
  - x-ipe-docs/requirements/FEATURE-013/ (new folder to create)

task_output_links:
  - x-ipe-docs/requirements/FEATURE-013/ (pending creation in Feature Breakdown)
```

---

## Example 2: UI Refinement - ENHANCEMENT Classification

**Request:** "Make the settings page auto-save instead of requiring a save button"

### CR Classification

```
Step 3.1: Read Change Request
  change_request: "Auto-save settings page"

Step 3.2: Identify Affected Features
  - Search features.md for "settings"
  - Found: FEATURE-005 (User Settings)
  
Step 3.3: Classify Scope
  Questions:
  1. Entirely new components? → No, modifying existing SettingsService
  2. Expand feature scope? → No, same functionality with UX improvement
  3. New user stories? → No, same goal "user saves preferences"
  4. Estimated complexity? → Medium (debouncing, state management)
  
  Classification: ENHANCEMENT

Step 3.4: Route CR
  - Classification: ENHANCEMENT
  - Action: Update FEATURE-005/specification.md
  - Next Task: Feature Refinement
```

### Output

```yaml
category: Standalone
next_task_type: Feature Refinement
require_human_review: Yes

cr_classification: ENHANCEMENT
reasoning: |
  Auto-save modifies existing behavior without adding new capabilities.
  Same user goal, improved UX implementation.
  
affected_artifacts:
  - x-ipe-docs/requirements/FEATURE-005/specification.md
  - x-ipe-docs/requirements/FEATURE-005/technical-design.md

task_output_links:
  - x-ipe-docs/requirements/FEATURE-005/specification.md (to update)
```

---

## Example 3: Ambiguous Request - Human Decision Required

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

## Example 4: Bug Report - NOT a Change Request

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
  → Hand off to task-type-bug-fix skill
```

### Output

```yaml
cr_classification: NOT_A_CR
redirect_to: Bug Fix
reasoning: "Describes broken functionality, not a change request"
```
