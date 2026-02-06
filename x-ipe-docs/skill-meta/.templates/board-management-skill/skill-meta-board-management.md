# Board Management Skill Template

> Copy YAML, replace `{placeholders}`, delete comments. `?` = optional field.

```yaml
---
# IDENTIFICATION
skill_name: "{entity}-board-management"      # string, required
skill_type: board-management                 # literal, required
version: "1.0.0"                             # semver, required
last_updated: YYYY-MM-DD                     # date, required
implementation_path: .github/skills/{skill_name}/
related_skills: []                           # string[], optional

# BOARD INTERFACE
managed_entity: "{entity}"                   # string: task|feature|requirement
board_path: "x-ipe-docs/planning/{entity}-board.md"

entity_schema:                               # Define entity fields
  id:        { type: string, pattern: "{ENTITY}-NNN" }
  status:    { type: enum, values: [pending, in_progress, completed, blocked, cancelled] }
  title:     { type: string }
  assignee?: { type: string }                # ? = optional

# STATE MACHINE
states:
  pending:     { terminal: false, transitions_to: [in_progress, cancelled] }
  in_progress: { terminal: false, transitions_to: [completed, blocked, pending] }
  blocked:     { terminal: false, transitions_to: [in_progress, cancelled] }
  completed:   { terminal: true, transitions_to: [] }
  cancelled:   { terminal: true, transitions_to: [] }

# CRUD OPERATIONS (? = optional input)
operations:
  create: { inputs: [title, assignee?], outputs: { entity_id: string } }
  read:   { inputs: [filter?], outputs: { items: array } }
  update: { inputs: [entity_id, updates], outputs: { success: boolean } }
  delete: { inputs: [entity_id], outputs: { success: boolean } }

# BOARD SECTIONS
sections:
  - { name: "Active {entity_plural}", type: table, columns: [ID, Title, Status, Assignee, Updated] }
  - { name: "Completed {entity_plural}", type: table, columns: [ID, Title, Completed, Notes] }
  - { name: "Quick Stats", type: key-value, fields: [total, in_progress, completed, pending] }

# ACCEPTANCE CRITERIA (MoSCoW)
acceptance_criteria:
  must:   [{ id: AC-001, desc: "CRUD preserves data integrity" },
           { id: AC-002, desc: "Markdown format stays valid" },
           { id: AC-003, desc: "Stats match actual counts" }]
  should: [{ id: AC-004, desc: "IDs follow {ENTITY}-NNN pattern" }]
  could:  [{ id: AC-005, desc: "Auto-archive after 30 days" }]
  wont:   [{ id: AC-006, desc: "{out_of_scope}", reason: "{why}" }]

# QUALITY METRICS
quality_metrics: { max_active_items: 50, archive_after_days: 30, complexity: medium }
---
```

## Minimal Example: Task Board (delta from template)

```yaml
# Only showing fields that differ from template defaults
managed_entity: "task"
board_path: "x-ipe-docs/planning/task-board.md"

entity_schema:  # Extended fields
  type:        { type: enum, values: [feature, bug, chore, spike] }
  feature_ref?: { type: reference, target: "feature-board" }

sections:
  - { name: "Active Tasks", columns: [ID, Type, Title, Status, Assignee, Updated, Links] }
```
