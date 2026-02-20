# Requirement Summary — Part 11

> Last Updated: 02-20-2026
> Covers: EPIC-038

---

## EPIC-038: CR-Refine Idea Action

### Project Overview

A Change Request to implement the **"Refine Idea" workflow action** end-to-end — establishing a reusable **modal-before-CLI execution pattern** that future workflow actions can follow. When a user clicks a CLI Agent action button in the workflow stage ribbon, a modal opens showing instructions and an optional extra input field, then launches the agent in a console session. The agent executes the skill, reports results via MCP, and the workflow UI reflects the updated status and deliverables.

> Source: IDEA-025 (CR-Refine Idea Action)
> Status: Proposed
> Priority: High
> Idea Summary: [idea-summary-v1.md](../ideas/025.%20CR-Refine%20Idea%20Action/idea-summary-v1.md)

### User Request

The user wants:
1. A modal dialog when clicking CLI Agent actions (starting with Refine Idea) showing readonly instructions + optional extra instructions
2. Agent execution via console session with automatic session idle detection and reuse
3. Automatic workflow status update via MCP when the agent skill completes
4. Enhanced deliverable viewer with file-tree browsing and inline markdown preview
5. This pattern to serve as a reusable template for all future CLI Agent workflow actions

### Clarifications

| # | Question | Answer |
|---|----------|--------|
| 1 | Session management: always create new or detect idle? | **Option B: Idle detection.** A session is "idle/available" when it's not running any command and not in a CLI tool (vi, ping, etc.) — just at a shell prompt waiting for input. Add `is_idle()` to PersistentSession. |
| 2 | Which agent CLI tools supported? | Leverage existing detection method. Check `.x-ipe.yaml` and default settings for agent tool configuration. |
| 3 | Real-time WebSocket status push? | No — reuse the implementation adopted for the Compose Idea action: agent → MCP → workflow-manager → UI. Same refresh pattern. |
| 4 | Scope: Refine Idea only or reusable template? | **Reusable template.** This CR is a prototype/template for other CLI Agent actions. The modal-before-CLI pattern should be generic. |
| 5 | Deliverable folder preview format? | File tree listing with clickable files, then inline markdown/text preview of each selected file. |
| 6 | Extra instructions persistence and limits? | **Ephemeral** (not saved in workflow JSON), max **500 characters**. |
| 7 | Retry behavior after agent crash? | **Overwrite** — each execution starts fresh in the output folder (e.g., `refined-idea/`). Partial output from a crashed run is cleared. |

### High-Level Requirements

**HR-038.1: Action Execution Modal (CR on FEATURE-036-C)**
A reusable modal dialog for CLI Agent workflow actions:
- Displays readonly instructions loaded from `copilot-prompt.json` (keyed by action ID)
- Provides an editable extra-instructions textarea (ephemeral, max 500 characters)
- "Copilot" button triggers console session + agent CLI command
- Modal follows the lifecycle pattern of `compose-idea-modal.js` (open → populate → submit → close)
- Agent tool is auto-detected from `.x-ipe.yaml` and default configuration
- The agent CLI command is constructed from: instructions + extra instructions + idea folder path context

**HR-038.2: Session Idle Detection (CR on FEATURE-029-A)**
Add `is_idle()` capability to `PersistentSession`:
- A session is "idle" if: not currently executing a command, not inside a CLI tool (vi, ping, less, etc.), at a normal shell prompt waiting for input
- Detection method: check if the last output buffer ends with a known shell prompt pattern (`$`, `%`, `>`) after no output for a configurable timeout
- When the modal needs a console session: first check existing sessions for idle ones → reuse if found → create new if none available
- Session is renamed to `wf-{workflow_name}-{action_name}` for identification and cleanup

**HR-038.3: Refinement Skill MCP Integration**
The existing ideation/refinement skill must:
- Accept `extra_instructions` as an input parameter
- Output refined idea to `{idea_folder}/refined-idea/` subfolder (overwrite on each run)
- Call `update_workflow_action` MCP tool in its DoD with: action=`refine_idea`, status=`done`, deliverables=[`{idea_folder}/refined-idea/`]
- Output the workflow manager response status

**HR-038.4: Enhanced Deliverable Viewer (CR on FEATURE-036-E)**
Extend the deliverables section:
- When a deliverable is a folder path: show a file-tree listing of its contents
- Clicking a file in the tree: opens inline markdown/text preview
- Scoped to files within the current workflow's idea/requirement folders only
- Reuse the existing linked idea file viewer component pattern

**HR-038.5: Execution Skill DoD Update**
Add a new workflow status verification checkpoint to `x-ipe-workflow-task-execution`:
- After existing "Changes committed to git" check: if the skill's `task_completion_output` interacts with workflow actions, verify that `update_workflow_action` was called
- On failure: flag the task as incomplete — "Skill completed but workflow status not updated"

**HR-038.6: UI Status Refresh**
Follow the same pattern as Compose Idea (EPIC-037):
- Action button shows spinner/pulse animation during execution (non-blocking)
- Agent → MCP → workflow-manager → UI refresh chain
- Status transitions: pending → in_progress (when agent starts) → done (when MCP callback received)
- Deliverables section shows the output folder after completion

### Functional Requirements

**Action Execution Modal (CR: FEATURE-036-C)**

- **FR-038.1:** When a CLI Agent action button is clicked, a modal dialog opens with the action's title and instructions
- **FR-038.2:** Instructions are loaded from `copilot-prompt.json` (served at runtime from `src/x_ipe/resources/config/copilot-prompt.json`), keyed by the action ID (e.g., `refine-idea`)
- **FR-038.3:** Modal contains an editable "Extra Instructions" textarea, max 500 characters, with character counter
- **FR-038.4:** Modal contains a "Copilot" button that triggers the agent execution flow
- **FR-038.5:** On "Copilot" click: find idle session → rename → construct CLI command → type into session → start progress indicator
- **FR-038.6:** Agent CLI tool is auto-detected from `.x-ipe.yaml` configuration (or default setting)
- **FR-038.7:** If `copilot-prompt.json` is missing the action's instructions, show error toast and disable Copilot button
- **FR-038.8:** Modal can be re-opened while agent is running (shows "in progress" state)

**Session Idle Detection (CR: FEATURE-029-A)**

- **FR-038.9:** `PersistentSession` class gains an `is_idle()` method returning boolean
- **FR-038.10:** `is_idle()` checks: (a) session is connected, (b) last output matches a known shell prompt pattern, (c) no output received for configurable idle timeout
- **FR-038.11:** Known shell prompt patterns: line ending with `$ `, `% `, `> `, or custom patterns from config
- **FR-038.12:** `SessionManager` gains a `find_idle_session()` method that iterates sessions and returns first idle one, or null
- **FR-038.13:** Found idle session is renamed to `wf-{workflow_name}-{action_name}` before use
- **FR-038.14:** If no idle session found and session limit not reached, create new session with the action name
- **FR-038.15:** If no idle session and limit reached (10/10), show error toast: "No available sessions. Close an existing session and retry."

**Refinement Skill Updates**

- **FR-038.16:** Ideation/refinement skill accepts `extra_instructions` as an optional input parameter
- **FR-038.17:** Skill outputs refined idea to `{idea_folder}/refined-idea/` subfolder
- **FR-038.18:** On each execution, `refined-idea/` folder is cleared before writing new output (overwrite mode)
- **FR-038.19:** Skill calls `update_workflow_action(workflow_name, "refine_idea", "done", deliverables=[...])` in its completion step
- **FR-038.20:** Skill outputs the MCP response status for verification

**Enhanced Deliverable Viewer (CR: FEATURE-036-E)**

- **FR-038.21:** Deliverables section detects folder-type deliverables (path ending with `/`)
- **FR-038.22:** Folder deliverables render as expandable file-tree (list files recursively)
- **FR-038.23:** Clicking a file in the tree opens inline preview: markdown rendered, text shown as-is
- **FR-038.24:** File-tree and preview are scoped to the current idea/requirement folder (no path traversal)
- **FR-038.25:** File-tree uses the existing `GET /api/ideas/file` endpoint pattern for file content

**Execution Skill DoD**

- **FR-038.26:** `x-ipe-workflow-task-execution` Step 5 (Global DoD) adds: if skill output declares workflow action interaction, verify `update_workflow_action` was called
- **FR-038.27:** Verification check: action status in workflow JSON is NOT `pending` after skill completion

**UI Status**

- **FR-038.28:** Action button shows spinner/pulse CSS animation when action status is `in_progress`
- **FR-038.29:** Spinner is non-blocking — user can interact with rest of UI during execution
- **FR-038.30:** Status refresh follows agent → MCP → workflow-manager → UI chain (same as Compose Idea)
- **FR-038.31:** After status transitions to `done`, deliverables section shows output artifacts

### Non-Functional Requirements

- **NFR-038.1:** Session idle detection must respond within 100ms (no blocking I/O)
- **NFR-038.2:** Modal opening must complete within 200ms (instructions loaded from config already in memory)
- **NFR-038.3:** File-tree listing must handle up to 50 files per folder without performance degradation
- **NFR-038.4:** Extra instructions textarea must validate character limit client-side (no server round-trip)

### Constraints

- Scope: This CR implements the Refine Idea action AND establishes a reusable pattern for all CLI Agent actions
- The `copilot-prompt.json` is served from `src/x_ipe/resources/config/copilot-prompt.json` at runtime (the `x-ipe-docs/config/` copy is documentation only)
- The `update_workflow_action` MCP tool already exists — no new MCP endpoints needed
- Workflow JSON files follow existing naming: `workflow-{name}.json`
- Both file and folder paths are supported as deliverables (per existing workflow JSON patterns)
- The `refined-idea/` subfolder coexists with `idea-summary-vN.md` — they serve different purposes
- Agent CLI command does NOT auto-press Enter — user confirms (existing pattern from FEATURE-036-C)

### Related Features (Conflict Review)

| Existing Feature | Overlap Type | Decision | CR Description |
|-----------------|--------------|----------|----------------|
| FEATURE-036-C (Stage Ribbon & Action Execution) | Functional overlap — CLI agent execution pattern extended with modal-before-CLI | **CR on existing** | Adds modal with instructions + extra input before triggering console session |
| FEATURE-036-E (Deliverables, Polling & Lifecycle) | Scope overlap — deliverable viewer enhanced | **CR on existing** | Enriches deliverable viewer from basic links to file-tree + inline preview for folders |
| FEATURE-029-A (Session Explorer Core) | Dependency — needs session idle detection | **CR on existing** | Adds `is_idle()` method to PersistentSession and `find_idle_session()` to SessionManager |

### Failure Modes & Error Handling

| Failure Scenario | Detection | Expected Behavior |
|-----------------|-----------|-------------------|
| Agent crashes mid-refinement | Console session shows error/exit | Action status remains `in_progress` or `pending`. User can re-trigger from modal. Next run overwrites partial output. |
| MCP call fails | Skill DoD check finds status still `pending` | Skill reports incomplete. Agent logs error. User can manually update via context menu. |
| Session disconnects | `PersistentSession.is_connected` = false | PTY stays alive (existing behavior). User can reconnect. Agent continues in background. |
| copilot-prompt.json missing action | Modal fails to load instructions | Show error toast: "Action instructions not configured". Disable Copilot button. |
| No available session (idle or new) | All 10 sessions busy, none idle | Show error toast: "No available sessions. Close an existing session and retry." |
| Workflow JSON write fails | MCP returns error response | Agent retries once. On second failure: log error, mark action as `failed`. |

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| Refine Idea Modal (4 scenes: action button states, modal dialog, post-refinement workflow, deliverable viewer) | [refine-idea-modal-v1.html](EPIC-038/mockups/refine-idea-modal-v1.html) |

### Feature List (Proposed Breakdown — to be finalized in Feature Breakdown)

| Feature ID | Epic | Feature Name | Version | Brief Description | Dependencies |
|-----------|------|--------------|---------|-------------------|-------------|
| FEATURE-038-A | EPIC-038 | Action Execution Modal | v1.0 | Reusable modal for CLI Agent actions with instructions display, extra input, and Copilot execution button. CR on FEATURE-036-C. | FEATURE-036-C |
| FEATURE-038-B | EPIC-038 | Session Idle Detection | v1.0 | Add `is_idle()` to PersistentSession and `find_idle_session()` to SessionManager. CR on FEATURE-029-A. | FEATURE-029-A |
| FEATURE-038-C | EPIC-038 | Enhanced Deliverable Viewer | v1.0 | File-tree browsing and inline markdown preview for folder-type deliverables. CR on FEATURE-036-E. | FEATURE-036-E |
| FEATURE-038-D | EPIC-038 | Refinement Skill Integration | v1.0 | Update ideation skill for extra_instructions, refined-idea/ output, and MCP workflow update. | FEATURE-038-A, FEATURE-038-B |
| FEATURE-038-E | EPIC-038 | Execution Skill DoD Update | v1.0 | Add workflow status verification checkpoint to x-ipe-workflow-task-execution. | - |

### Open Questions

- None — all ambiguities resolved during clarification.
