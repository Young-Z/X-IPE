# Feature Specification: Workflow Manager & State Persistence

> Feature ID: FEATURE-036-A  
> Epic: EPIC-036 (Engineering Workflow View)  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-17-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Engineering Workflow View | HTML | [../mockups/workflow-view-v1.html](x-ipe-docs/requirements/EPIC-036/mockups/workflow-view-v1.html) | Full workflow view with panels, stages, lanes | outdated — use as directional reference only |

> **Note:** The shared mockup covers the full EPIC-036 UI. FEATURE-036-A is a backend service with no direct UI. The mockup is directional reference for understanding data structures and state transitions.

## Overview

The Engineering Workflow Manager is the backend foundation for EPIC-036. It provides a service that manages the full lifecycle of engineering workflows — from creation through stage progression, feature lane management, and eventual archiving. The service encapsulates all business logic for workflow CRUD, stage gating, dependency evaluation, next-action suggestion, and JSON state persistence.

This feature is needed because the Engineering Workflow View requires a single authoritative backend service that owns all state mutations. Without it, the frontend would need to manage complex gating logic, dependency graphs, and concurrent state updates — leading to inconsistency and data corruption.

The primary consumers are: (1) the Engineering Workflow View frontend (FEATURE-036-B through E) via Flask REST endpoints, and (2) CLI agent skills via two new MCP tools (`update_workflow_status` and `get_workflow_state`) registered on the existing `x-ipe-app-and-agent-interaction` MCP server.

## User Stories

- As a **developer using the Workflow View**, I want to **create a new engineering workflow**, so that **I can track my project through the full delivery lifecycle**.
- As a **developer using the Workflow View**, I want to **see which stage and action to work on next**, so that **I don't have to manually figure out what's ready**.
- As a **CLI agent skill**, I want to **report my completion status and deliverables via MCP**, so that **the workflow state stays up-to-date without manual intervention**.
- As a **CLI agent skill**, I want to **query the current workflow state**, so that **I can understand the context before executing my task**.
- As a **developer using the Workflow View**, I want the **stage gating to prevent premature progression**, so that **mandatory steps aren't accidentally skipped**.
- As a **developer using the Workflow View**, I want **dependency evaluation before starting feature actions**, so that **I'm warned when dependencies aren't met**.

## Acceptance Criteria

### Workflow CRUD

- [ ] `create_workflow(name)` creates `x-ipe-docs/engineering-workflow/workflow-{name}.json` with schema v1.0; Ideation stage active, all other stages locked
- [ ] `create_workflow(name)` returns error if a workflow with that name already exists
- [ ] `get_workflow(name)` returns the full parsed workflow state including stages, features, and actions
- [ ] `get_workflow(name)` returns error with descriptive message if workflow file not found
- [ ] `list_workflows()` returns metadata (name, created, last_activity, current_stage, feature_count) for all active workflows
- [ ] `delete_workflow(name)` removes the workflow JSON file from disk
- [ ] `delete_workflow(name)` returns error if workflow file not found
- [ ] Workflow directory `x-ipe-docs/engineering-workflow/` is auto-created if it does not exist

### Stage Gating

- [ ] Stage gating evaluates mandatory action completion: all mandatory actions in a stage must be "done" before the next stage unlocks
- [ ] Optional actions (status "skipped" or "pending") do not block stage progression
- [ ] Shared stages (Ideation, Requirement) gate at workflow level — all actions must be globally done
- [ ] Per-feature stages (Implement, Validation, Feedback) gate independently per feature lane
- [ ] When a stage unlocks, its status transitions from "locked" to "in_progress"
- [ ] `get_next_action(workflow_name)` returns the recommended next action (globally or per-feature) based on gating rules

### Dependency Evaluation

- [ ] `check_dependencies(workflow_name, feature_id)` returns list of blocking dependencies with their completion statuses
- [ ] If all dependencies are satisfied (done), returns `{blocked: false, blockers: []}`
- [ ] If any dependency is unfinished, returns `{blocked: true, blockers: [{feature_id, current_stage, required_stage}]}`
- [ ] Dependency data is read from the `depends_on` array in each feature's workflow JSON entry

### State Persistence

- [ ] All state writes are atomic: write to temp file first, then rename to target path
- [ ] `last_activity` timestamp updated on every write operation
- [ ] Workflow JSON includes `schema_version: "1.0"` field
- [ ] On read, if JSON is corrupted (parse error), log error and return descriptive error (no silent failure)
- [ ] Workflow directory and file paths use safe naming (alphanumeric + hyphens only; reject special characters in workflow name)

### MCP Tools

- [ ] `update_workflow_status(workflow_name, action, status, deliverables[])` registered on `x-ipe-app-and-agent-interaction` MCP server
- [ ] `update_workflow_status` updates the specified action's status and deliverables list in the workflow JSON
- [ ] `update_workflow_status` triggers stage gating re-evaluation after update
- [ ] `update_workflow_status` returns updated workflow state summary (current_stage, next_action)
- [ ] `get_workflow_state(workflow_name)` registered on `x-ipe-app-and-agent-interaction` MCP server
- [ ] `get_workflow_state` returns the full workflow state as JSON (same as `get_workflow`)
- [ ] Both MCP tools validate input parameters and return structured error responses on failure

### Action Status Updates

- [ ] `update_action_status(workflow_name, action, status, feature_id?, deliverables[])` updates the action status for the specified stage action
- [ ] Valid action statuses: `pending`, `in_progress`, `done`, `skipped`, `failed`
- [ ] When `feature_id` is provided, updates the feature-level action (Implement/Validation/Feedback stages)
- [ ] When `feature_id` is omitted, updates the workflow-level action (Ideation/Requirement stages)
- [ ] After status update, automatically re-evaluates stage gating for affected stage(s)

### Feature Lane Management

- [ ] `add_features(workflow_name, features[])` populates per-feature structures in Implement, Validation, and Feedback stages
- [ ] Each feature entry includes: `name`, `depends_on[]`, and per-stage action statuses (all initially `pending`)
- [ ] Feature data follows the per-feature JSON schema defined in EPIC-036 requirements

### Idea Folder Linking

- [ ] `link_idea_folder(workflow_name, idea_folder_path)` sets the `idea_folder` field in workflow JSON
- [ ] `idea_folder` defaults to `null` at creation (no folder required upfront)
- [ ] `link_idea_folder` validates that the provided path exists on disk

## Functional Requirements

### FR-036-A.1: Workflow CRUD Service

**Description:** Provide create, read, list, and delete operations for engineering workflows.

**Details:**
- Input: Workflow name (string, alphanumeric + hyphens, max 100 chars)
- Process: Create/read/delete workflow JSON in `x-ipe-docs/engineering-workflow/` directory
- Output: Workflow state object or operation result

### FR-036-A.2: Stage Gating Engine

**Description:** Evaluate stage completion rules to determine which stages are unlocked.

**Details:**
- Input: Workflow state with action statuses
- Process: For each stage, check all mandatory actions are "done"; for per-feature stages, evaluate per feature lane
- Output: Updated stage statuses (locked/in_progress/completed) and next action suggestion

### FR-036-A.3: Dependency Evaluation

**Description:** Check feature dependencies before allowing action execution.

**Details:**
- Input: Workflow name, target feature ID
- Process: Read feature's `depends_on` array, check each dependency's completion status in workflow JSON
- Output: Blocked/unblocked result with blocker details

### FR-036-A.4: MCP Tool — update_workflow_status

**Description:** MCP tool for agent skills to report action completion and deliverables.

**Details:**
- Input: `{workflow_name, action, status, deliverables[]}`; optional `feature_id` for per-feature actions
- Process: Validate input → update action status → save deliverables → re-evaluate gating → persist state
- Output: Updated workflow state summary

### FR-036-A.5: MCP Tool — get_workflow_state

**Description:** MCP tool for agent skills to query current workflow state.

**Details:**
- Input: `{workflow_name}`
- Process: Read and parse workflow JSON, resolve current stage and next action
- Output: Full workflow state as JSON

### FR-036-A.6: State Persistence

**Description:** Persist all workflow state as JSON files with atomic writes.

**Details:**
- Input: Workflow state object
- Process: Serialize to JSON → write to temp file → atomic rename to target
- Output: Persisted JSON file at `x-ipe-docs/engineering-workflow/workflow-{name}.json`

### FR-036-A.7: Feature Lane Population

**Description:** After Feature Breakdown, populate per-feature structures in per-feature stages.

**Details:**
- Input: List of features with IDs, names, and dependency arrays
- Process: Create feature entries in Implement, Validation, and Feedback stage sections of workflow JSON
- Output: Updated workflow JSON with feature lane data

### FR-036-A.8: Idea Folder Linking

**Description:** Associate an idea folder with a workflow.

**Details:**
- Input: Workflow name, idea folder path
- Process: Validate path exists → update `idea_folder` field in workflow JSON
- Output: Updated workflow state

## Non-Functional Requirements

### NFR-036-A.1: Atomicity

All state file writes must be atomic (write temp → rename) to prevent corruption from crashes or concurrent access.

### NFR-036-A.2: Data Integrity

Only the Workflow Manager writes to workflow JSON files. No other component may directly modify state files.

### NFR-036-A.3: Schema Versioning

Workflow JSON must include `schema_version` field. The manager must validate schema version on read and reject unknown versions with a descriptive error.

### NFR-036-A.4: Performance

- `get_workflow()` must complete within 100ms for a single workflow
- `list_workflows()` must complete within 500ms for up to 50 workflows
- `update_action_status()` must complete within 200ms including file write

### NFR-036-A.5: Error Resilience

- Corrupted JSON detected on read must produce a descriptive error (not a silent fallback)
- All API responses include structured error codes and messages
- Invalid workflow names rejected before any file I/O

### NFR-036-A.6: Naming Safety

Workflow names must be sanitized: alphanumeric characters and hyphens only, max 100 characters. Names with special characters must be rejected with a clear error message.

## UI/UX Requirements

FEATURE-036-A is a backend service with no direct UI. All user interaction happens through:
- FEATURE-036-B (Workflow View Shell) — calls REST endpoints
- MCP tools — called by CLI agent skills

## Dependencies

### Internal Dependencies

- **FEATURE-033** (App-Agent Interaction MCP): Provides the FastMCP server infrastructure where new MCP tools (`update_workflow_status`, `get_workflow_state`) will be registered. FEATURE-036-A adds tool functions to the existing MCP server.

### External Dependencies

- **Flask**: Web framework for REST API endpoints
- **FastMCP**: MCP tool registration framework (already in use)
- **Python stdlib (json, os, tempfile)**: JSON serialization, file operations, atomic writes

## Business Rules

### BR-036-A.1: Stage Ordering

Stages must follow strict order: Ideation → Requirement → Implement → Validation → Feedback. No stage can be skipped.

### BR-036-A.2: Mandatory vs Optional Actions

Each stage has mandatory and optional actions (defined in the Action-to-Stage Mapping). Only mandatory actions block stage progression.

### BR-036-A.3: Shared vs Per-Feature Stages

Ideation and Requirement are workflow-level (shared). Implement, Validation, and Feedback are per-feature. Per-feature stages only appear after Feature Breakdown populates feature data.

### BR-036-A.4: Dependency Rules

Feature dependencies form a DAG (no cycles). An action on feature B that depends on feature A is allowed if A has completed the same stage or beyond.

### BR-036-A.5: Action Status Transitions

Valid transitions: `pending` → `in_progress` → `done` | `failed`; `pending` → `skipped`; `failed` → `in_progress` (retry). No other transitions allowed.

### BR-036-A.6: Single Writer

Only the Workflow Manager service writes to workflow JSON files. All mutations go through the manager's API methods.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Create workflow with existing name | Return error: "Workflow '{name}' already exists" |
| Get workflow that doesn't exist | Return error: "Workflow '{name}' not found" |
| Workflow JSON is corrupted (invalid JSON) | Return error: "Workflow '{name}' has corrupted state — manual repair required" |
| Workflow name has special characters | Reject with error: "Workflow name must be alphanumeric with hyphens only" |
| Workflow name exceeds 100 chars | Reject with error: "Workflow name must not exceed 100 characters" |
| Update action on locked stage | Reject with error: "Stage '{stage}' is locked — complete previous stage first" |
| Update feature action before features exist | Reject with error: "No features in workflow — run Feature Breakdown first" |
| Dependency check on feature with no dependencies | Return `{blocked: false, blockers: []}` |
| Circular dependency detected in feature data | Return error: "Circular dependency detected involving feature(s): [...]" |
| Concurrent writes (race condition) | Atomic write (temp+rename) prevents partial state; last writer wins |
| Workflow directory doesn't exist | Auto-create `x-ipe-docs/engineering-workflow/` directory |
| Empty workflow list | Return empty array `[]`, not error |
| MCP tool called with missing required fields | Return structured validation error listing missing fields |
| `link_idea_folder` with non-existent path | Return error: "Idea folder path does not exist: {path}" |

## Out of Scope

- **Multi-user concurrent locking** — Single-user scope for v1; no file locking or conflict resolution
- **Schema migration** — `schema_version` field is set but automated migration from v1 to v2 is deferred
- **Undo/redo** — No state history or rollback capability
- **Workflow templates** — No pre-defined workflow templates for v1
- **Archive management** — Auto-archive logic (FEATURE-036-E responsibility)
- **Frontend rendering** — All UI is handled by FEATURE-036-B through E
- **Action execution** — The Workflow Manager does NOT invoke skills; it only tracks their status
- **Deliverables file verification** — File existence checking is FEATURE-036-E's Deliverables Resolver responsibility

## Technical Considerations

- **State file location**: `x-ipe-docs/engineering-workflow/workflow-{name}.json` — one file per workflow
- **Stage gating configuration**: The Action-to-Stage Mapping (mandatory/optional flags) should be data-driven, not hardcoded — enabling future extensibility
- **MCP tool registration**: Follow the existing pattern in `x_ipe/mcp/app_agent_interaction.py` — decorator-based `@mcp.tool` registration with JSON input/output
- **Flask endpoint pattern**: Register a new blueprint (e.g., `workflow_routes.py` → `workflow_bp`) following existing blueprint patterns
- **Service pattern**: Follow `KBManagerService` pattern — a manager class composing domain logic with `@x_ipe_tracing()` for observability
- **Atomic writes**: Use `tempfile.NamedTemporaryFile` in the same directory as target, then `os.replace()` for atomic rename
- **Timestamp format**: ISO 8601 (e.g., `2026-02-17T12:00:00Z`) consistent with JSON schema in EPIC-036 requirements

## Open Questions

None — all design decisions resolved during requirement gathering (see EPIC-036 Clarifications section in requirement-details-part-9.md).
