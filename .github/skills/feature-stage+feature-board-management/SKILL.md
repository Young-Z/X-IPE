---
name: feature-stage+feature-board-management
description: Manage feature lifecycle in x-ipe-docs/planning/features.md. Category-level skill called during Step 4 (Category Closing) for feature-stage tasks. Accepts Task Data Model with feature_id and feature_phase, updates feature board, returns category_level_change_summary. Also provides query interface for Feature Data Model.
---

# Feature Board Management

## Purpose

AI Agents follow this skill to manage the feature board (`x-ipe-docs/planning/features.md`) - the central tracking system for all feature-level work.

**Two Usage Modes:**

1. **Category-Level Skill** (Step 4 of task execution)
   - Called automatically for feature-stage tasks
   - Updates feature status based on task completion
   - Returns category_level_change_summary

2. **Query Interface** (Called by other skills)
   - Provides Feature Data Model for feature-stage tasks
   - Allows feature creation/updates during breakdown
   - Enables data retrieval for implementation

---

## Important Notes

### Skill Prerequisite
- This skill is called automatically by task-execution-guideline for feature-stage tasks
- Other skills can call this skill directly for queries and updates

**Important:** If Agent DO NOT have skill capability, can directly go to `skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Feature Board Structure

**Location:** `x-ipe-docs/planning/features.md`

**Content Sections:**
1. Overview and status definitions
2. Feature Tracking Table (primary view)
3. Status Details (grouped by status)
4. Feature Details (expanded information)

---

## Feature Data Model

**Core structure used throughout the system:**

```yaml
Feature:
  # Core identification
  feature_id: FEATURE-XXX
  title: <Feature Title>
  version: v1.0
  
  # Status tracking  
  status: Planned | Refined | Designed | Implemented | Tested | Completed
  description: <Brief description, ≤100 words>
  
  # Dependencies
  dependencies: [FEATURE-XXX, ...]  # List of feature IDs
  
  # Artifact links
  specification_link: x-ipe-docs/requirements/FEATURE-XXX/specification.md | null
  technical_design_link: x-ipe-docs/requirements/FEATURE-XXX/technical-design.md | null
  
  # Metadata
  created: MM-DD-YYYY
  last_updated: MM-DD-YYYY HH:MM:SS
  
  # Task tracking
  tasks:
    - task_id: TASK-XXX
      task_type: <Task Type>
      status: <Status>
      completed_at: <Timestamp> | null
```

---

## Feature Status Lifecycle

```
Planned → Refined → Designed → Implemented → Tested → Completed
   ↓         ↓          ↓           ↓           ↓          ↓
Created   Feature   Technical    Code       Human     Feature
 (Auto)   Refine     Design     Implement  Playground  Closing
          + Test Gen
```

**Status Definitions:**

| Status | Description | Triggered By |
|--------|-------------|--------------|
| **Planned** | Feature identified, awaiting refinement | Feature Breakdown (auto) |
| **Refined** | Specification complete, ready for design | Feature Refinement task completion |
| **Designed** | Technical design complete, ready for implementation | Technical Design task completion (Test Generation keeps Designed) |
| **Implemented** | Code complete, ready for closing | Code Implementation task completion |
| **Completed** | Feature fully deployed and verified | Feature Closing task completion |

---

## Operations

### Operation 1: Create or Update Features

**When to use:** During feature breakdown or initial feature setup

**Input:**
```yaml
operation: create_or_update_features
features:
  - feature_id: FEATURE-001
    title: User Authentication
    version: v1.0
    description: JWT-based user authentication with login, logout, and token refresh
    dependencies: []
  - feature_id: FEATURE-002
    title: User Profile
    version: v1.0
    description: User profile management and settings
    dependencies: [FEATURE-001]
```

**Execution:**
```
1. Create x-ipe-docs/planning/features.md if not exists (use template)
2. FOR EACH feature in features:
   IF feature_id exists on board:
     → Update feature information (title, version, description, dependencies)
     → Keep existing status and links
   ELSE:
     → Add new feature to tracking table
     → Set status = "Planned"
     → Set created = today's date
   → Set last_updated = current timestamp
3. Update status details sections
4. Update feature details sections
```

**Output:**
```yaml
success: true
features_added: [FEATURE-001, FEATURE-002]
features_updated: [FEATURE-003]
board_path: x-ipe-docs/planning/features.md
message: "Created 2 features, updated 1 feature on feature board"
```

---

### Operation 2: Query Feature

**When to use:** Feature-stage tasks need full Feature Data Model

**Input:**
```yaml
operation: query_feature
feature_id: FEATURE-001
```

**Execution:**
```
1. Read x-ipe-docs/planning/features.md
2. Find feature with matching feature_id
3. Extract all feature information
4. Build Feature Data Model
```

**Output (Feature Data Model):**
```yaml
feature_id: FEATURE-001
title: User Authentication
version: v1.0
status: Designed
description: JWT-based user authentication with login, logout, and token refresh
dependencies: []
specification_link: x-ipe-docs/requirements/FEATURE-001/specification.md
technical_design_link: x-ipe-docs/requirements/FEATURE-001/technical-design.md
created: 01-15-2026
last_updated: 01-17-2026 14:30:00
tasks:
  - task_id: TASK-015
    task_type: Feature Refinement
    status: completed
    completed_at: 01-16-2026 10:15:00
  - task_id: TASK-023
    task_type: Technical Design
    status: completed
    completed_at: 01-17-2026 14:30:00
```

**Error Handling:**
```yaml
# If feature not found
success: false
error: "Feature not found"
feature_id: FEATURE-001
message: "FEATURE-001 does not exist on the feature board"
```

---

### Operation 3: Update Feature Status (Category-Level)

**When to use:** Automatically during Step 4 (Category Closing) for feature-stage tasks

**Input (from Task Data Model):**
```yaml
task_id: TASK-023
task_type: Technical Design
category: feature-stage
status: completed
feature_id: FEATURE-001
feature_phase: Technical Design
```

**Status Update Logic Based on feature_phase:**

| feature_phase | New Status | Specification Link Update | Technical Design Link Update |
|---------------|------------|---------------------------|------------------------------|
| `Feature Refinement` | Refined | Set from task_output_links | - |
| `Technical Design` | Designed | - | Set from task_output_links |
| `Test Generation` | Designed | - | - |
| `Code Implementation` | Implemented | - | - |
| `Feature Closing` | Completed | - | - |

**Execution:**
```
1. Read x-ipe-docs/planning/features.md
2. Find feature with feature_id
3. Update status based on feature_phase (see table above)
4. Update artifact links from task_output_links if applicable
5. Add task to feature's task list
6. Update last_updated timestamp
7. Move feature in status details sections
8. Update feature details section
```

**Output:**
```yaml
success: true
feature_id: FEATURE-001
old_status: Refined
new_status: Designed
category_level_change_summary: "Updated FEATURE-001 (User Authentication) status from Refined to Designed, added technical design link"
```

---

## Category-Level Execution (Step 4)

**Called By:** task-execution-guideline during Step 4 (Category Closing)

**Input:** Full Task Data Model

**Required Attributes in Task Data Model:**
- `feature_id` - Which feature to update
- `feature_phase` - What phase was just completed
- `task_output_links` - Artifacts to link
- `status` - Task status (must be completed)

**Process:**
```
1. Validate Task Data Model has feature_id and feature_phase
2. Call Operation 3: Update Feature Status
3. Return category_level_change_summary
```

**Example:**
```yaml
# Input Task Data Model
task_id: TASK-023
task_type: Technical Design
category: feature-stage
status: completed
feature_id: FEATURE-001
feature_title: User Authentication
feature_version: v1.0
feature_phase: Technical Design
task_output_links: [x-ipe-docs/requirements/FEATURE-001/technical-design.md]

# Output
category_level_change_summary: "Updated FEATURE-001 (User Authentication) status from Refined to Designed, added technical design link"
```

---

## Feature Board Template Structure

**File:** `x-ipe-docs/planning/features.md`

```markdown
# Feature Board

> Last Updated: MM-DD-YYYY HH:MM:SS

## Overview

This board tracks all features across the project lifecycle.

**Status Definitions:**
- **Planned** - Feature identified, awaiting refinement
- **Refined** - Specification complete, ready for design
- **Designed** - Technical design complete, ready for implementation
- **Implemented** - Code complete, ready for testing
- **Tested** - Tests complete, ready for deployment
- **Completed** - Feature fully deployed and verified

---

## Feature Tracking

| Feature ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |
|------------|---------------|---------|--------|-------------------|---------|--------------|
| FEATURE-001 | User Authentication | v1.0 | Designed | [spec](FEATURE-001/specification.md) | 01-15-2026 | 01-17-2026 |

---

## Status Details

### Planned (0)
- None

### Refined (0)
- None

### Designed (1)
- FEATURE-001: User Authentication

### Implemented (0)
- None

### Tested (0)
- None

### Completed (0)
- None

---

## Feature Details

### FEATURE-001: User Authentication
- **Version:** v1.0
- **Status:** Designed
- **Description:** JWT-based user authentication with login, logout, and token refresh
- **Dependencies:** None
- **Specification:** [x-ipe-docs/requirements/FEATURE-001/specification.md](FEATURE-001/specification.md)
- **Technical Design:** [x-ipe-docs/requirements/FEATURE-001/technical-design.md](FEATURE-001/technical-design.md)
- **Tasks:**
  - TASK-015 (Feature Refinement) - Completed on 01-16-2026
  - TASK-023 (Technical Design) - Completed on 01-17-2026

---
```

---

## Integration Examples

### Example 1: Feature Breakdown Creates Features

```yaml
# Feature Breakdown skill calls:
operation: create_or_update_features
features:
  - feature_id: FEATURE-001
    title: User Authentication
    version: v1.0
    description: JWT-based authentication
    dependencies: []
  - feature_id: FEATURE-002
    title: User Profile
    version: v1.0
    description: Profile management
    dependencies: [FEATURE-001]

# Result:
# - Board created if not exists
# - Two features added with status "Planned"
```

---

### Example 2: Feature Refinement Task Queries Feature

```yaml
# Feature Refinement skill calls:
operation: query_feature
feature_id: FEATURE-001

# Receives full Feature Data Model:
feature_id: FEATURE-001
title: User Authentication
version: v1.0
status: Planned
description: JWT-based authentication
dependencies: []
# ... etc
```

---

### Example 3: Category Closing Updates Status

```yaml
# After Feature Refinement task completes:
# Task Data Model has:
feature_id: FEATURE-001
feature_phase: refinement
task_output_links: [x-ipe-docs/requirements/FEATURE-001/specification.md]

# Category skill (Step 4) calls Update Feature Status:
# - Status changes: Planned → Refined
# - Specification link added
# - Returns: "Updated FEATURE-001 (User Authentication) status to Refined"
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Feature not found | Invalid feature_id | Check feature_id exists on board |
| Board file missing | First feature operation | Auto-creates from template |
| Missing feature_id | Task Data Model incomplete | Ensure task type outputs feature_id |
| Invalid status transition | Skipped phase | Follow lifecycle order |

---

## Best Practices

### For Feature Breakdown
- Create all features at once with create_or_update_features
- Include dependencies to track order
- Keep descriptions concise (≤100 words)

### For Feature-Stage Tasks
- Always query feature board first to get full context
- Output feature_phase correctly (refinement, design, implementation, testing, closing)
- Include feature_id in task output

### For Board Maintenance
- Let category skill handle status updates automatically
- Don't manually edit feature status
- Use query operation to check feature state

---

## Notes

- Board is single source of truth for feature status
- All feature-stage tasks must output feature_id and feature_phase
- Status updates happen automatically via category closing
- Query interface available for any skill needing feature context
- Board file created automatically on first use
