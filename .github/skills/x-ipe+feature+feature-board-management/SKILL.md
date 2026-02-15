---
name: x-ipe+feature+feature-board-management
description: Manage feature lifecycle in x-ipe-docs/planning/features.md. Category-level skill called during Step 4 (Category Closing) for feature-stage tasks. Accepts Task Data Model with feature_id and feature_phase, updates feature board, returns category_level_change_summary. Also provides query interface for Feature Data Model. Triggers on "create feature", "query feature", "update feature status", "init feature board".
---

# Feature Board Management

## Purpose

AI Agents follow this skill to manage the feature board (`x-ipe-docs/planning/features.md`) — the central tracking system for all feature-level work:
1. **Create** or update features on the board
2. **Query** feature data for feature-stage tasks
3. **Update** feature status during category closing (Step 4)
4. **Track** feature lifecycle from Planned through Completed

---

## Important Notes

MANDATORY: This skill is called automatically by x-ipe-workflow-task-execution for feature-stage tasks during Step 4 (Category Closing). Other skills can call it directly for queries and updates.

BLOCKING: If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point for each skill.

CRITICAL: Board is the single source of truth for feature status. All feature-stage tasks must output feature_id and feature_phase.

---

## About

The feature board at `x-ipe-docs/planning/features.md` tracks all features across the project lifecycle.

**Key Concepts:**

- **Feature Data Model** — Structured record containing feature_id, title, version, status, description, dependencies, artifact links, and task history. See [references/examples.md](references/examples.md) for full schema.
- **Feature Statuses** — `Planned`, `Refined`, `Designed`, `Implemented`, `Tested`, `Completed`
- **Status Lifecycle** — `Planned -> Refined -> Designed -> Implemented -> Tested -> Completed`. Each transition is triggered by completing a specific feature-stage task phase.
- **Board Sections** — Overview, Feature Tracking Table
- **Category-Level Skill** — Called automatically during Step 4 (Category Closing) for feature-stage tasks to update feature status and return category_level_change_summary
- **Query Interface** — Provides Feature Data Model to any skill needing feature context

**Status Definitions:**

| Status | Description | Triggered By |
|--------|-------------|--------------|
| Planned | Feature identified, awaiting refinement | Feature Breakdown (auto) |
| Refined | Specification complete, ready for design | Feature Refinement completion |
| Designed | Technical design complete, ready for implementation | Technical Design completion (Test Generation keeps Designed) |
| Implemented | Code complete, ready for closing | Code Implementation completion |
| Completed | Feature fully deployed and verified | Feature Closing completion |

---

## When to Use

```yaml
triggers:
  - "create feature"
  - "query feature"
  - "update feature status"
  - "init feature board"
  - "feature breakdown creates features"
  - "category closing for feature-stage"

not_for:
  - "Task board management (use x-ipe+all+task-board-management)"
  - "Requirement board management (use requirement-board-management)"
```

---

## Input Parameters

```yaml
input:
  operation: "create_or_update_features | query_feature | update_feature_status"
  features:  # For create_or_update_features
    - feature_id: "FEATURE-XXX"
      title: "{Feature Title}"
      version: "v1.0"
      description: "{Brief description, max 100 words}"
      dependencies: "[FEATURE-XXX, ...]"
  feature_id: "FEATURE-XXX"  # For query_feature and update_feature_status
  task_data_model:  # For update_feature_status (from Step 4)
    task_id: "TASK-XXX"
    task_based_skill: "{task_based_skill}"
    category: "feature-stage"
    status: "completed"
    feature_id: "FEATURE-XXX"
    feature_phase: "{Feature Refinement | Technical Design | Test Generation | Code Implementation | Feature Closing}"
    task_output_links: "[{artifact paths}]"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation identified</name>
    <verification>Caller specifies which operation to perform</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Required parameters provided</name>
    <verification>create_or_update_features requires features list; query_feature requires feature_id; update_feature_status requires Task Data Model with feature_id and feature_phase</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Board location known or discoverable</name>
    <verification>x-ipe-docs/planning/features.md exists or can be created from template</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Create or Update Features

**When:** During feature breakdown or initial feature setup

```xml
<operation name="create_or_update_features">
  <action>
    1. Create x-ipe-docs/planning/features.md if not exists (use template)
    2. FOR EACH feature in features:
       IF feature_id exists on board:
         Update feature information (title, version, description, dependencies)
         Keep existing status and links
       ELSE:
         Add new feature to tracking table
         Set status = "Planned"
         Set created = today's date
       Set last_updated = current timestamp
  </action>
  <constraints>
    - BLOCKING: feature_id must be unique per feature
    - CRITICAL: New features always start with status Planned
  </constraints>
  <output>List of features_added, features_updated, board_path</output>
</operation>
```

### Operation: Query Feature

**When:** Feature-stage tasks need full Feature Data Model

```xml
<operation name="query_feature">
  <action>
    1. Read x-ipe-docs/planning/features.md
    2. Find feature with matching feature_id
    3. Extract all feature information
    4. Build and return Feature Data Model
  </action>
  <output>Complete Feature Data Model (feature_id, title, version, status, description, dependencies, specification_link, technical_design_link, created, last_updated, tasks)</output>
</operation>
```

### Operation: Update Feature Status

**When:** Automatically during Step 4 (Category Closing) for feature-stage tasks

**Status update logic based on feature_phase:**

| feature_phase | New Status | Specification Link Update | Technical Design Link Update |
|---------------|------------|---------------------------|------------------------------|
| Feature Refinement | Refined | Set from task_output_links | — |
| Technical Design | Designed | — | Set from task_output_links |
| Test Generation | Designed | — | — |
| Code Implementation | Implemented | — | — |
| Feature Closing | Completed | — | — |

```xml
<operation name="update_feature_status">
  <action>
    1. Validate Task Data Model has feature_id and feature_phase
    2. Read x-ipe-docs/planning/features.md
    3. Find feature with feature_id
    4. Update status based on feature_phase (see table above)
    5. Update artifact links from task_output_links if applicable
    6. Add task to feature's task list
    7. Update last_updated timestamp
    8. Return category_level_change_summary
  </action>
  <constraints>
    - BLOCKING: Task Data Model must contain feature_id and feature_phase
    - BLOCKING: Task status must be completed
    - CRITICAL: Follow lifecycle order — do not skip phases
  </constraints>
  <output>feature_id, old_status, new_status, category_level_change_summary</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "{operation_name}"
  result:
    board_path: "x-ipe-docs/planning/features.md"
    feature_id: "FEATURE-XXX"
    features_added: []
    features_updated: []
    old_status: "{previous_status}"
    new_status: "{current_status}"
    category_level_change_summary: "{summary text}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>operation_output.success is true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Board file updated</name>
    <verification>x-ipe-docs/planning/features.md reflects the operation changes</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Status consistency verified</name>
    <verification>After every update, verify the feature status in the tracking table is correct. Cross-check that the status aligns with the feature_phase lifecycle (Planned → Refined → Designed → Implemented → Completed). If any mismatch is found, correct it before completing the operation.</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `FEATURE_NOT_FOUND` | Invalid feature_id | Check feature_id exists on board; use query_feature to verify |
| `BOARD_NOT_FOUND` | Board file missing on first operation | Auto-create from template at `templates/features.md` |
| `MISSING_FEATURE_ID` | Task Data Model incomplete | Ensure task-based skill outputs feature_id and feature_phase |
| `INVALID_STATUS_TRANSITION` | Skipped lifecycle phase | Follow lifecycle order: Planned -> Refined -> Designed -> Implemented -> Completed |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/features.md` | Feature board template with sections and default structure |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples including Feature Data Model schema, Status Lifecycle diagram, Board Template Structure, and integration examples.
