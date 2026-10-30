# Task Category Skill Metadata Template

Category completion orchestration uses the workflow SKILL scaffold: Execution
Flow → Execution Procedure → Output Result → DoD → Skill Registry. It does not
expose tool Operations or implement board CRUD. Preserve existing domain-specific
completion gates and child output contracts when updating an existing category.

Copy the YAML, replace placeholders, and bind each registry mapping to the actual
child skill schema. `all` means cross-category orchestration.

```yaml
skill_name: "x-ipe+{category}+{name}"
skill_type: x-ipe-task-category
version: "1.0.0"
status: candidate
last_updated: YYYY-MM-DD
implementation_path: ".github/skills/{skill_name}/"
managed_category: "{category}"
trigger: "All required related tasks in {category} have verified completion outputs"

completion_inputs:
  shared_context:
    category: "{category}"
    child_outputs: []  # Full child task_completion_output mappings, not IDs alone
    process_preference:
      interaction_mode: "interact-with-human"
  options:
    stop_on_first_failure: true
    max_retries: 0

completion_gate:
  required_children: ["{child_skill}"]
  assertion: "Every required child has passed its domain DoD; blocked children prevent completion"

skill_registry:
  - skill: "{child_skill}"
    input_mapping: "shared_context.{field} -> child_input.{field}"
    output_capture: "child_output.{field} -> workflow_state.{field}"

outputs:
  workflow_output:
    status: "completed | partial | failed"
    phases_completed: 0
    total_phases: 0
    results: {}
    failed_skills: []
    rollback_executed: false

dependencies:
  board_service: x-ipe-tool-task-board-manager  # Only if domain requires persistence
  board_policy: "Load the board tool and use its JSON/API contract; no direct Markdown board writes"

acceptance_criteria:
  must:
    - {id: AC-001, desc: "Incomplete or blocked children stop category completion"}
    - {id: AC-002, desc: "Registry input/output mappings preserve actual child schemas"}
    - {id: AC-003, desc: "Aggregation returns workflow_output and explicit failure handling"}
  should:
    - {id: AC-004, desc: "Repeated completion does not duplicate side effects"}
  wont:
    - {id: AC-005, desc: "Board storage migration or tool CRUD", reason: "Separate tool responsibility"}
```

## Field Reference

| Field | Contract |
|-------|----------|
| skill_name | `x-ipe+{category}+{name}`, including `all` for cross-category |
| completion_inputs | Full child outputs and shared context, preserving nested process preference |
| completion_gate | Domain-specific verified completion, not merely board status |
| skill_registry | Explicit child schema mapping; load before readiness verification |
| outputs.workflow_output | Same aggregate result schema as workflow SKILL scaffold |
| dependencies | Board tool only where necessary; no fabricated legacy board path |

## Example: Feature Category Release

```yaml
skill_name: "x-ipe+feature-stage+release"
managed_category: "feature-stage"
completion_gate:
  required_children: [x-ipe-task-based-feature-acceptance-test, x-ipe-task-based-feature-closing]
  assertion: "Acceptance evidence and closing outputs verified; release permission checked separately"
```
