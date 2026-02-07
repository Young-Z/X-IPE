# Task Category Skill Template

Task Category skills are orchestration skills called when all related task-based skills in a category finish their work.

> Copy YAML, replace `{placeholders}`, delete comments. `?` = optional field.

```yaml
---
# IDENTIFICATION
skill_name: "x-ipe-{category}-{operation-name}"  # string, required
skill_type: x-ipe-task-category                   # literal, required
version: "1.0.0"                                  # semver, required
last_updated: YYYY-MM-DD                          # date, required
implementation_path: .github/skills/{skill_name}/
related_skills: []                                # string[], optional

# CATEGORY INTERFACE
managed_category: "{category}"                    # string: feature-stage|requirement-stage|ideation-stage
board_path: "x-ipe-docs/planning/{category}-board.md"

entity_schema:                                    # Define entity fields
  id:        { type: string, pattern: "{ENTITY}-NNN" }
  status:    { type: enum, values: [pending, in_progress, completed, blocked, cancelled] }
  title:     { type: string }
  assignee?: { type: string }                     # ? = optional

# STATE MACHINE
states:
  pending:     { terminal: false, transitions_to: [in_progress, cancelled] }
  in_progress: { terminal: false, transitions_to: [completed, blocked, pending] }
  blocked:     { terminal: false, transitions_to: [in_progress, cancelled] }
  completed:   { terminal: true, transitions_to: [] }
  cancelled:   { terminal: true, transitions_to: [] }

# OPERATIONS (? = optional input)
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
  must:   [{ id: AC-001, desc: "Operations preserve data integrity" },
           { id: AC-002, desc: "Markdown format stays valid" },
           { id: AC-003, desc: "Stats match actual counts" }]
  should: [{ id: AC-004, desc: "IDs follow {ENTITY}-NNN pattern" }]
  could:  [{ id: AC-005, desc: "Auto-archive after 30 days" }]
  wont:   [{ id: AC-006, desc: "{out_of_scope}", reason: "{why}" }]

# QUALITY METRICS
quality_metrics: { max_active_items: 50, archive_after_days: 30, complexity: medium }
---
```

---

## Field Reference

| Section | Field | Required | Description |
|---------|-------|----------|-------------|
| Identity | skill_name | Yes | `x-ipe-{category}+{operation-name}` format |
| Identity | skill_type | Yes | `x-ipe-task-category` |
| Identity | version | Yes | Semver format |
| Category | managed_category | Yes | feature-stage, requirement-stage, ideation-stage |
| Category | board_path | Yes | Path to the board markdown file |
| Schema | entity_schema | Yes | Define entity fields and types |
| States | states | Yes | State machine with transitions |
| Operations | operations | Yes | CRUD operations definition |
| Sections | sections | Yes | Board markdown sections |
| Acceptance | must | Yes | All must pass for merge |

---

## Minimal Example: Task Board Management

```yaml
# Only showing fields that differ from template defaults
skill_name: "x-ipe-task-board-management"
managed_category: "task"
board_path: "x-ipe-docs/planning/task-board.md"

entity_schema:  # Extended fields
  type:        { type: enum, values: [feature, bug, chore, spike] }
  feature_ref?: { type: reference, target: "feature-board" }

sections:
  - { name: "Active Tasks", columns: [ID, Type, Title, Status, Assignee, Updated, Links] }
```

## Example: Feature Board Management

```yaml
skill_name: "x-ipe-feature-board-management"
managed_category: "feature-stage"
board_path: "x-ipe-docs/planning/feature-board.md"

entity_schema:
  feature_id: { type: string, pattern: "FEATURE-NNN" }
  status:     { type: enum, values: [planning, in_progress, review, completed] }
  title:      { type: string }
  tasks:      { type: array, items: { type: reference, target: "task-board" } }
```
