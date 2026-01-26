---
name: requirement-stage+requirement-board-management
description: Manage requirement tracking during requirement-stage tasks. This is a category-level skill called during Step 4 (Category Closing) for requirement-stage tasks. Accepts Task Data Model. Outputs category_level_change_summary.
---

# Requirement Board Management

## Purpose

AI Agents follow this skill to manage requirement tracking - ensuring requirements are properly documented and tracked. This skill is called during **Step 4 (Category Closing)** for tasks with `category: requirement-stage`.

**Operations:**
1. **Locate** requirement documents
2. **Update** requirement summary after gathering
3. **Track** feature breakdown status
4. **Query** requirements by various criteria

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Input: Task Data Model

This skill receives the Task Data Model from task execution. For requirement-stage tasks, it expects these dynamic attributes:

```yaml
Task:
  # Core fields
  task_id: TASK-XXX
  task_type: <Task Type>
  task_description: <≤50 words>
  category: requirement-stage
  status: <status>
  
  # Dynamic attributes (from requirement-stage task type skills)
  requirement_id: REQ-XXX | null           # If tracking specific requirement
  features_created: [FEATURE-XXX, ...]     # Features created from breakdown
  requirement_summary_updated: true | false # Whether summary was updated
  # ... other dynamic attributes
```

---

## Output: category_level_change_summary

This skill MUST return a `category_level_change_summary` (≤100 words) describing what changed.

**Example outputs:**
```
"Updated requirement-details.md with new business requirements"
"Created 3 features from requirement breakdown: FEATURE-001, FEATURE-002, FEATURE-003"
"Feature Breakdown completed - 5 features identified and added to feature board"
```

---

## Integration with Task Lifecycle

This skill is called during Step 4 (Category Closing) when `category = requirement-stage`.

**Flow:**
```
Step 3: Task Work Execution
   ↓ (task type skill returns requirement-related attributes)
Step 4: Category Closing
   → task-board-management (MANDATORY)
   → requirement-stage+requirement-board-management (this skill)
      - Receives Task Data Model
      - Updates requirement documents
      - Returns category_level_change_summary
   ↓
Step 5: Check Global DoD
```

---

## Operations

### Operation 1: Update Requirement Summary

**When:** Requirement Gathering task completes
**Then:** Verify requirement-details.md is updated

```
Input: Task Data Model with:
  - task_type: Requirement Gathering
  - requirement_summary_updated: true | false
  - task_output_links: [paths to updated docs]

Process:
1. Verify x-ipe-docs/requirements/requirement-details.md exists
2. IF requirement_summary_updated = true:
   → Confirm changes are saved
3. Return summary of changes

Output:
  category_level_change_summary: "Updated requirement-details.md with new business requirements"
```

### Operation 2: Track Feature Breakdown

**When:** Feature Breakdown task completes
**Then:** Track features created

```
Input: Task Data Model with:
  - task_type: Feature Breakdown
  - features_created: [FEATURE-XXX, ...]
  - task_output_links: [paths to feature specs]

Process:
1. Count features created
2. Verify each feature exists on feature board
3. Verify specification.md created for each
4. Return summary

Output:
  category_level_change_summary: "Created {N} features from breakdown: {feature_ids}"
```

---

## Requirement Documents Structure

```
x-ipe-docs/
└── requirements/
    ├── requirement-details.md          # High-level requirements
    ├── features.md                     # Feature board (managed by feature-stage+feature-board-management)
    ├── FEATURE-001/
    │   └── specification.md
    ├── FEATURE-002/
    │   └── specification.md
    └── ...
```

---

## Task Type to Operation Mapping

| Task Type Skill | Operation |
|-----------------|-----------|
| task-type-requirement-gathering | Update Requirement Summary |
| task-type-feature-breakdown | Track Feature Breakdown |

---

## Examples

### Example 1: Requirement Gathering Complete

**Input Task Data Model:**
```yaml
task_id: TASK-001
task_type: Requirement Gathering
category: requirement-stage
status: completed
requirement_summary_updated: true
task_output_links:
  - x-ipe-docs/requirements/requirement-details.md
```

**Output:**
```yaml
category_level_change_summary: "Updated requirement-details.md with user authentication requirements"
```

### Example 2: Feature Breakdown Complete

**Input Task Data Model:**
```yaml
task_id: TASK-002
task_type: Feature Breakdown
category: requirement-stage
status: completed
features_created:
  - FEATURE-001
  - FEATURE-002
  - FEATURE-003
task_output_links:
  - x-ipe-docs/requirements/FEATURE-001/specification.md
  - x-ipe-docs/requirements/FEATURE-002/specification.md
  - x-ipe-docs/requirements/FEATURE-003/specification.md
```

**Output:**
```yaml
category_level_change_summary: "Created 3 features: FEATURE-001 (User Auth), FEATURE-002 (Dashboard), FEATURE-003 (Settings)"
```
