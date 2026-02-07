# Skill Meta Template: Workflow Orchestration

<!-- ~50 lines YAML | Copy, fill {placeholders}, delete comments | Validate: skill-meta-validator.md -->

```yaml
---
skill_name: x-ipe-workflow-{name}  # Required: string
skill_type: x-ipe-workflow-orchestration  # Required: literal
version: 1.0.0  # Required: string (semver)
last_updated: {YYYY-MM-DD}  # Required: string (ISO date)
implementation_path: .github/skills/{skill-name}/  # Required: string (path)

lifecycle:  # Required
  steps:  # array<Step>
    - name: {step_name}  # Required: string
      action: "{what happens}"  # Required: string
      gate: "{condition to proceed}"  # Optional: string
      skills_loaded: [{skill-1}]  # Optional: array<string> - skill names to load
      next_step: {next_step_name} | END  # Required: string|literal

data_model:  # Required
  core: [{field}: {type}]  # Required: array - set during planning
  execution: [{field}: {type}]  # Optional: array - set by task-based skills
  closing: [{field}: {type}]  # Optional: array - set by category skills
  control: [auto_proceed: boolean]  # Required: array - routing flags

states:  # Required
  values: [pending, in_progress, blocked, completed, cancelled]  # Required: array<enum>
  terminal: [completed, cancelled]  # Required: array<enum>
  transitions: "pending→in_progress→completed|blocked"  # Required: string

routing:  # Required
  task_based_skills:  # array<TaskRoute>
    - pattern: "{request pattern}"  # Required: string (regex)
      task_based_skill: {x-ipe-task-based-skill}  # Required: string
      category: {category-name} | Standalone  # Required: string|literal
  category_skills:  # array<CategoryRoute>
    - category: {category-name}  # Required: string
      skill: {category-skill-name}  # Required: string
      required: true | false  # Required: boolean - if true, category skill MUST run at closing

decision_points:  # Required
  - name: {gate_name}  # Required: string
    condition: "{when to trigger}"  # Required: string
    on_true: "{action}"  # Required: string
    on_false: "{action}"  # Required: string

error_handling:  # Required
  - error_type: {error_name}  # Required: string
    recovery: "{strategy}"  # Required: string

acceptance_criteria:  # Required (MoSCoW)
  must: [{id: AC-001, description: "{critical requirement}"}]  # Required: array
  should: [{id: AC-002, description: "{important requirement}"}]  # Optional: array
  could: [{id: AC-003, description: "{nice-to-have}"}]  # Optional: array
  wont: [{id: AC-004, description: "{explicitly excluded}"}]  # Optional: array
---
```

## Example: Task Execution Workflow

```yaml
---
skill_name: x-ipe-workflow-task-execution
skill_type: workflow-orchestration
version: 1.0.0
last_updated: 2026-02-03
implementation_path: .github/skills/x-ipe-workflow-task-execution/

lifecycle:
  steps:
    - {name: planning, action: "Match request → Create task", gate: "Task on board", skills_loaded: [x-ipe+all+task-board-management], next_step: execute}
    - {name: execute, action: "Load task-based skill → Do work", skills_loaded: [x-ipe-task-based-{matched}], next_step: closing}
    - {name: closing, action: "Update boards → Validate DoD", skills_loaded: [x-ipe+all+task-board-management], next_step: END}

data_model:
  core: [task_id: string, task_based_skill: string, category: string, status: enum]
  execution: [next_task_based_skill: string|null, require_human_review: boolean]
  control: [auto_proceed: boolean]

states: {values: [pending, in_progress, completed], terminal: [completed], transitions: "pending→in_progress→completed"}

routing:
  task_based_skills: [{pattern: "implement|code", task_based_skill: x-ipe-task-based-code-implementation, category: feature-stage}]
  category_skills: [{category: feature-stage, skill: x-ipe+feature+feature-board-management, required: true}]

decision_points: [{name: human_review_gate, condition: "require_human_review=true AND auto_proceed=false", on_true: "STOP", on_false: "Continue"}]
error_handling: [{error_type: skill_not_found, recovery: "Log warning, continue manually"}]
acceptance_criteria: {must: [{id: AC-001, description: "Task on board before work"}], could: [{id: AC-002, description: "Auto-advance"}]}
---
```

**Flow:** Planning → Execute → Closing → END (auto_proceed=true chains to next task)
