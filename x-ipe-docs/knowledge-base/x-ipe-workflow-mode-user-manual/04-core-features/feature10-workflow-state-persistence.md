---
title: "Workflow State Persistence"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/services/workflow_manager_service.py
---

# Workflow State Persistence

## Overview

Each workflow's state is persisted as a JSON file on disk. This enables resume after restart, crash recovery, and version tracking.

## File Location

```
{PROJECT_ROOT}/.x-ipe/engineering-workflow/workflow-{name}.json
```

Example: `.x-ipe/engineering-workflow/workflow-knowledge-extraction.json`

## JSON Structure

```json
{
  "schema_version": "4.0",
  "name": "Knowledge-Extraction",
  "created": "2026-03-17T03:17:23.200297+00:00",
  "last_activity": "2026-03-17T14:17:58.219668+00:00",
  "idea_folder": "x-ipe-docs/ideas/wf-008-knowledge-extraction",
  "current_stage": "validation",
  "global": {
    "process_preference": {
      "interaction_mode": "interact-with-human"
    }
  },
  "shared": {
    "ideation": {
      "status": "completed",
      "actions": {
        "compose_idea": {
          "status": "done",
          "deliverables": {
            "raw-ideas": "path/to/file.md",
            "ideas-folder": "path/to/folder/"
          },
          "context": {},
          "next_actions_suggested": ["refine_idea"]
        }
      }
    },
    "requirement": { }
  },
  "features": [
    {
      "feature_id": "FEATURE-050-A",
      "name": "Extractor Skill Foundation",
      "depends_on": [],
      "implement": {
        "status": "done",
        "actions": { }
      }
    }
  ]
}
```

## Key Fields

| Field | Description |
|-------|-------------|
| `schema_version` | JSON schema version (current: "4.0") |
| `name` | Workflow name |
| `created` | ISO 8601 creation timestamp |
| `last_activity` | Last modification timestamp (used for polling) |
| `current_stage` | Active stage: ideation, requirement, implement, validation, feedback |
| `idea_folder` | Path to idea files directory |
| `global.process_preference` | Interaction mode setting |
| `shared` | Shared stage actions (ideation, requirement) |
| `features[]` | Per-feature state for implement/validation/feedback |
| `deliverables` | Tag → file path mapping per action |
| `next_actions_suggested` | AI-suggested next actions |

## Write Safety

- **Atomic writes:** Uses temp file + `os.replace()` — never leaves a corrupted state
- **Auto-migration:** Reads old versions (v1/v2/v3) and auto-migrates to v4
- **Concurrency:** Uses `fcntl.flock` file locking to prevent parallel write corruption
