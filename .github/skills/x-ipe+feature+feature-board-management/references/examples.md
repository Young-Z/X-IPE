# Feature Board Management — Reference Examples

## Feature Data Model

Core structure used throughout the system:

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
      task_based_skill: <Task-Based Skill>
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
specification_link: null
technical_design_link: null
created: 01-15-2026
last_updated: 01-15-2026 10:00:00
tasks: []
```

### Example 3: Category Closing Updates Status

```yaml
# After Feature Refinement task completes:
# Task Data Model has:
feature_id: FEATURE-001
feature_phase: Feature Refinement
task_output_links: [x-ipe-docs/requirements/FEATURE-001/specification.md]

# Category skill (Step 4) calls update_feature_status:
# - Status changes: Planned → Refined
# - Specification link added
# - Returns: "Updated FEATURE-001 (User Authentication) status to Refined"
```

### Example 4: Full Category-Level Execution (Step 4)

```yaml
# Input Task Data Model
task_id: TASK-023
task_based_skill: Technical Design
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

## Best Practices

### For Feature Breakdown
- Create all features at once with create_or_update_features
- Include dependencies to track order
- Keep descriptions concise (≤100 words)

### For Feature-Stage Tasks
- Always query feature board first to get full context
- Output feature_phase correctly (Feature Refinement, Technical Design, Test Generation, Code Implementation, Feature Closing)
- Include feature_id in task output

### For Board Maintenance
- Let category skill handle status updates automatically
- Do not manually edit feature status
- Use query operation to check feature state
