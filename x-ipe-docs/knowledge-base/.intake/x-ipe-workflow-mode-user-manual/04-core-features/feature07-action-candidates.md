---
title: "Action Candidates"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/features/action-execution-modal.js
---

# Action Candidates

## Overview

Action Candidates are pre-resolved file/folder paths from previous action deliverables that serve as input for the current action. They appear as a dropdown in the Action Execution Modal.

## What Are Candidates?

When an action requires input from a previous action's output, the system resolves "candidates" — a list of matching files and folders. For example:
- **Refine Idea** action candidates: `.md` files from the "Compose Idea" output
- **Feature Refinement** candidates: specification files from requirement gathering

## When Candidates Appear

Candidates appear in the ActionExecutionModal when the action definition includes an `action_context` field with a `candidates` specification. The modal renders a **dropdown select** populated from the API response.

## API

```
GET /api/workflow/{name}/candidates/{actionKey}/{candidatesName}?feature_id={featureId}
```

**Response:**
```json
[
  { "type": "file", "path": "x-ipe-docs/ideas/wf-008/refined-idea.md" },
  { "type": "folder", "path": "x-ipe-docs/ideas/wf-008/" }
]
```

## User Flow

1. Click workflow action → ActionExecutionModal opens
2. If action has candidates → `_loadCandidates(candidatesName)` fetches options
3. Dropdown populated with file paths
4. User selects a candidate file/folder
5. Selection included in the action context sent to the AI CLI tool
6. Action executes with the selected input

## Resolution Logic

The backend `resolve_candidates` function:
1. Searches all completed previous actions for matching deliverable tags
2. Matches by tag name or folder pattern
3. Returns file/folder paths as candidate options
