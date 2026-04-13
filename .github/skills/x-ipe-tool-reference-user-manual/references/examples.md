# Reference User Manual — Examples

## Example 1: Retrieve Step-by-Step for Creating a New Workflow

**Scenario:** The `x-ipe-task-based-general-purpose-executor` is executing a task that requires creating a new workflow in the application. It calls `x-ipe-tool-reference-user-manual` to get instructions.

### Step 1 — Lookup

```yaml
input:
  operation: "lookup_instruction"
  kb_path: "x-ipe-docs/knowledge-base/my-app"
  query: "How do I create a new workflow?"
  section_filter: null
  feature_id: ""
```

**What the skill does:**
1. Reads `x-ipe-docs/knowledge-base/my-app/04-core-features/_index.md` — scans feature listing table
2. Reads `x-ipe-docs/knowledge-base/my-app/05-common-workflows/_index.md` — finds entry: "Create New Workflow"
3. Reads `.kb-index.json` in both folders for metadata tag matches
4. Matches query "create a new workflow" against titles → top match: `workflow01-create-new-workflow.md` (relevance: 0.95)
5. Reads the matched file, checks instruction quality → all steps have action, element, expected outcome → clarity_score: 1.0

**Output:**

```json
{
  "success": true,
  "operation": "lookup_instruction",
  "result": {
    "matches": [
      {
        "file_path": "x-ipe-docs/knowledge-base/my-app/05-common-workflows/workflow01-create-new-workflow.md",
        "title": "Create New Workflow",
        "relevance_score": 0.95,
        "interaction_pattern": "FORM",
        "clarity_score": 1.0
      },
      {
        "file_path": "x-ipe-docs/knowledge-base/my-app/04-core-features/feature03-workflow-editor.md",
        "title": "Workflow Editor",
        "relevance_score": 0.6,
        "interaction_pattern": "NAVIGATION",
        "clarity_score": 0.85
      }
    ],
    "best_match": {
      "file_path": "x-ipe-docs/knowledge-base/my-app/05-common-workflows/workflow01-create-new-workflow.md",
      "title": "Create New Workflow"
    },
    "needs_human_feedback": false,
    "feedback_reason": null
  },
  "errors": []
}
```

### Step 2 — Get Step-by-Step

The executor then requests detailed steps for the best match:

```yaml
input:
  operation: "get_step_by_step"
  kb_path: "x-ipe-docs/knowledge-base/my-app"
  query: ""
  section_filter: null
  feature_id: "workflow01-create-new-workflow"
```

**What the skill does:**
1. Locates `x-ipe-docs/knowledge-base/my-app/05-common-workflows/workflow01-create-new-workflow.md`
2. Parses the Instructions section — finds 4 ordered steps
3. Each step has action verb, element name, and expected outcome → clarity_score: 1.0
4. Collects 2 screenshot references and 1 tip

**Output:**

```json
{
  "success": true,
  "operation": "get_step_by_step",
  "result": {
    "steps": [
      {
        "step_number": 1,
        "action": "Click",
        "element": "\"+ New Workflow\" button in the top toolbar",
        "expected_outcome": "A modal dialog titled \"Create Workflow\" appears",
        "screenshot_ref": "x-ipe-docs/knowledge-base/my-app/05-common-workflows/screenshots/create-workflow-modal.png"
      },
      {
        "step_number": 2,
        "action": "Type",
        "element": "\"Workflow Name\" text field",
        "expected_outcome": "The name appears in the text field and the \"Create\" button becomes enabled",
        "screenshot_ref": null
      },
      {
        "step_number": 3,
        "action": "Select",
        "element": "\"Template\" dropdown",
        "expected_outcome": "A list of available templates is shown",
        "screenshot_ref": null
      },
      {
        "step_number": 4,
        "action": "Click",
        "element": "\"Create\" button",
        "expected_outcome": "The modal closes and the new workflow appears in the workflow list",
        "screenshot_ref": "x-ipe-docs/knowledge-base/my-app/05-common-workflows/screenshots/workflow-created.png"
      }
    ],
    "clarity_score": 1.0,
    "needs_human_feedback": false,
    "unclear_steps": [],
    "tips": [
      "Workflow names must be unique within the project. If a duplicate name is entered, an error message appears below the text field."
    ]
  },
  "errors": []
}
```

---

## Example 2: Vague Configuration Instructions Trigger Human Feedback

**Scenario:** The executor needs to configure application settings. The manual section exists but instructions are too vague to follow literally.

```yaml
input:
  operation: "get_step_by_step"
  kb_path: "x-ipe-docs/knowledge-base/my-app"
  query: "configure settings"
  section_filter: "configuration"
  feature_id: ""
```

**What the skill does:**
1. Section filter maps to `06-configuration.md` → reads the file directly
2. Parses the Instructions section — finds 3 steps
3. Assesses each step for clarity:
   - Step 1: "Open the settings page" — missing element name (which link/button?), no expected outcome → deduct 0.15
   - Step 2: "Adjust the settings as needed" — missing action verb (adjust what?), missing element, missing expected outcome → deduct 0.15
   - Step 3: "Save your changes" — missing element name (which button?), no expected outcome → deduct 0.15
4. clarity_score = 1.0 - (3 × 0.15) = 0.55 → below 0.6 threshold
5. Sets `needs_human_feedback: true`

**Output:**

```json
{
  "success": true,
  "operation": "get_step_by_step",
  "result": {
    "steps": [
      {
        "step_number": 1,
        "action": "Open",
        "element": "the settings page",
        "expected_outcome": null,
        "screenshot_ref": null
      },
      {
        "step_number": 2,
        "action": "Adjust",
        "element": "the settings as needed",
        "expected_outcome": null,
        "screenshot_ref": null
      },
      {
        "step_number": 3,
        "action": "Save",
        "element": "your changes",
        "expected_outcome": null,
        "screenshot_ref": null
      }
    ],
    "clarity_score": 0.55,
    "needs_human_feedback": true,
    "unclear_steps": [
      {"step_number": 1, "missing_component": "specific element name, expected outcome"},
      {"step_number": 2, "missing_component": "specific action verb, element name, expected outcome"},
      {"step_number": 3, "missing_component": "specific element name, expected outcome"}
    ],
    "tips": []
  },
  "errors": []
}
```

**What happens next:** The executor receives `needs_human_feedback: true` and escalates to the human (or DAO representative) asking: "The manual instructions for configuring settings are too vague. Specifically, steps 1–3 are missing element names and expected outcomes. Can you provide more details on how to navigate to settings and which fields to configure?"
