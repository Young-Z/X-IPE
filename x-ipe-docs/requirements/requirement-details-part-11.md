# Requirement Summary — Part 11

> Last Updated: 02-22-2026
> Covers: EPIC-038, EPIC-039

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

### Feature List

| Feature ID | Epic ID | Feature Name | Version | Brief Description | Dependencies |
|-----------|---------|--------------|---------|-------------------|-------------|
| FEATURE-038-A | EPIC-038 | Action Execution Modal | v1.0 | Reusable modal for CLI Agent actions: readonly instructions from copilot-prompt.json, extra instructions textarea (500 char), Copilot button triggers console session, agent tool auto-detect from .x-ipe.yaml. CR on FEATURE-036-C. | FEATURE-036-C |
| FEATURE-038-B | EPIC-038 | Session Idle Detection | v1.0 | Add `is_idle()` to PersistentSession (shell-prompt detection, not in CLI tool) and `find_idle_session()` to SessionManager. Session rename to wf-{name}-{action}. CR on FEATURE-029-A. | FEATURE-029-A |
| FEATURE-038-C | EPIC-038 | Enhanced Deliverable Viewer | v1.0 | Folder-type deliverables render as file-tree with clickable files and inline markdown/text preview. Path-scoped, reuses existing file API. CR on FEATURE-036-E. | FEATURE-036-E |
| FEATURE-038-D | EPIC-038 | Refinement Skill Integration | v1.0 | Update ideation skill: accept extra_instructions param, output to refined-idea/ (overwrite mode), call update_workflow_action MCP in DoD. | FEATURE-038-A, FEATURE-038-B |
| FEATURE-038-E | EPIC-038 | Execution Skill DoD Update | v1.0 | Add workflow status verification checkpoint to x-ipe-workflow-task-execution Step 5: verify update_workflow_action was called if skill declares workflow interaction. | None |

### Feature Details

#### FEATURE-038-A: Action Execution Modal

**Version:** v1.0
**Brief Description:** A reusable modal dialog that opens when any CLI Agent workflow action is clicked. Shows readonly instructions loaded from `copilot-prompt.json` (keyed by action ID), an editable extra-instructions textarea (ephemeral, max 500 chars with counter), and a "Copilot" button that triggers the console session + agent execution flow. Agent tool auto-detected from `.x-ipe.yaml`. Includes spinner/pulse on action button during execution and status refresh via agent → MCP → workflow-manager → UI chain. Follows `compose-idea-modal.js` lifecycle pattern. This is a CR on FEATURE-036-C.

**Acceptance Criteria:**
- [ ] AC-038.1: Clicking a CLI Agent action button opens the Action Execution Modal
- [ ] AC-038.2: Modal title shows the action name (e.g., "Refine Idea")
- [ ] AC-038.3: Readonly instructions textarea populated from `copilot-prompt.json` by action ID
- [ ] AC-038.4: If action ID missing from config, error toast shown and Copilot button disabled
- [ ] AC-038.5: Extra instructions textarea is editable, max 500 characters with live counter
- [ ] AC-038.6: "Copilot" button triggers: find idle session → rename → construct CLI command → type into session
- [ ] AC-038.7: Agent CLI tool auto-detected from `.x-ipe.yaml` configuration
- [ ] AC-038.8: Action button shows spinner/pulse CSS animation when status is `in_progress`
- [ ] AC-038.9: Spinner is non-blocking — user can interact with rest of UI
- [ ] AC-038.10: Status refresh follows agent → MCP → workflow-manager → UI chain (same as Compose Idea)
- [ ] AC-038.11: After status transitions to `done`, deliverables section shows output artifacts
- [ ] AC-038.12: Modal can be re-opened while agent is running (shows "in progress" state)

**Dependencies:**
- FEATURE-036-C (Stage Ribbon & Action Execution — base action button mechanics)

**Technical Considerations:**
- Reuse `compose-idea-modal.js` lifecycle pattern (open → populate → submit → close)
- `copilot-prompt.json` served from `src/x_ipe/resources/config/copilot-prompt.json` at runtime
- Agent CLI command does NOT auto-press Enter — user confirms (existing pattern)

**Linked Mockups:**
- [refine-idea-modal-v1.html](EPIC-038/mockups/refine-idea-modal-v1.html) — Scene 1 (action button states), Scene 2 (modal dialog)

> **⚠️ CR Impact Note** (added 2026-02-22, ref: EPIC-040)
> - **Change:** Generalize ActionExecutionModal to support ALL CLI workflow actions, not just Refine Idea. Replace `_resolveIdeaFiles()` with generic `_resolveInputFiles(actionKey)`. Add `input_source` / `deliverable_folder` fields to copilot-prompt.json.
> - **Affected FRs:** FR-038.1 (modal instruction display), FR-038.4 (idea file selector → generic file selector), FR-038.6 (command construction → generalized command template)
> - **Action Required:** Feature specification refactoring needed — modal must become action-agnostic
> - **New Feature Ref:** EPIC-040 — see requirement-details-part-12.md

---

#### FEATURE-038-B: Session Idle Detection

**Version:** v1.0
**Brief Description:** Add session idle detection to the console session management. `PersistentSession` gains `is_idle()` method that checks if the session is at a shell prompt (not running a command, not in vi/ping/less/etc). `SessionManager` gains `find_idle_session()` that iterates and returns first idle session. Found sessions are renamed to `wf-{workflow_name}-{action_name}`. Handles edge cases: no idle session found, session limit reached. This is a CR on FEATURE-029-A.

**Acceptance Criteria:**
- [ ] AC-038.13: `PersistentSession.is_idle()` returns true when session is at shell prompt
- [ ] AC-038.14: `is_idle()` returns false when session is executing a command or in a CLI tool
- [ ] AC-038.15: Shell prompt detection: last output line matches known patterns (`$ `, `% `, `> `) + configurable idle timeout
- [ ] AC-038.16: `SessionManager.find_idle_session()` returns first idle session or null
- [ ] AC-038.17: Found idle session is renamed to `wf-{workflow_name}-{action_name}`
- [ ] AC-038.18: If no idle session and limit not reached, new session created with action name
- [ ] AC-038.19: If no idle session and limit reached (10/10), error toast: "No available sessions"
- [ ] AC-038.20: Idle detection responds within 100ms (no blocking I/O)

**Dependencies:**
- FEATURE-029-A (Session Explorer Core — session management infrastructure)

**Technical Considerations:**
- Detection based on output buffer analysis — no backend API changes needed
- Configurable prompt patterns via `.x-ipe.yaml` or hardcoded defaults
- Must not interfere with existing session switching/management

---

#### FEATURE-038-C: Enhanced Deliverable Viewer

**Version:** v1.0
**Brief Description:** Extend the deliverables section to support folder-type deliverables. When a deliverable path ends with `/`, render an expandable file-tree listing. Clicking a file opens inline preview: markdown rendered via marked.js, text shown as-is. Tree and preview scoped to current idea/requirement folder (no path traversal). Reuses existing `GET /api/ideas/file` endpoint pattern. This is a CR on FEATURE-036-E.

**Acceptance Criteria:**
- [ ] AC-038.21: Deliverables section detects folder-type deliverables (path ending with `/`)
- [ ] AC-038.22: Folder deliverables render as expandable file-tree
- [ ] AC-038.23: Clicking a file in tree opens inline preview (markdown rendered, text as-is)
- [ ] AC-038.24: File-tree and preview scoped to current folder only (no path traversal)
- [ ] AC-038.25: File-tree handles up to 50 files per folder without performance degradation
- [ ] AC-038.26: File content fetched via existing `GET /api/ideas/file` endpoint pattern

**Dependencies:**
- FEATURE-036-E (Deliverables, Polling & Lifecycle — base deliverables section)

**Technical Considerations:**
- File-tree component can be built with simple nested `<ul>` and CSS toggle
- Markdown rendering reuses marked.js (already in project for FEATURE-037-B)
- Backend needs a folder listing endpoint (or extend existing file endpoint)

**Linked Mockups:**
- [refine-idea-modal-v1.html](EPIC-038/mockups/refine-idea-modal-v1.html) — Scene 4 (deliverable viewer)

> **⚠️ CR Impact Note** (added 2026-02-22, ref: EPIC-039)
> - **Change:** Replace inline folder tree+preview with a dedicated Folder Browser Modal (two-panel: tree on left, preview on right). Add folder card distinct background, search/filter, breadcrumb, image preview, download button.
> - **Affected FRs:** FR-038-C.2, FR-038-C.3, FR-038-C.4 (tree/preview rendering replaced with modal)
> - **Action Required:** Feature specification refactoring needed — inline tree/preview ACs become modal-based ACs
> - **New Feature Ref:** EPIC-039 — see requirement-details-part-11.md

---

#### FEATURE-038-D: Refinement Skill Integration

**Version:** v1.0
**Brief Description:** Update the ideation/refinement skill to work with the new action execution flow. Skill accepts `extra_instructions` input parameter, outputs refined idea to `{idea_folder}/refined-idea/` subfolder (overwrite mode — clears folder on each run), and calls `update_workflow_action` MCP tool in its completion step with action=refine_idea, status=done, deliverables list.

**Acceptance Criteria:**
- [ ] AC-038.27: Ideation skill accepts `extra_instructions` as optional input parameter
- [ ] AC-038.28: Skill outputs to `{idea_folder}/refined-idea/` subfolder
- [ ] AC-038.29: On each execution, `refined-idea/` folder is cleared before writing (overwrite mode)
- [ ] AC-038.30: Skill calls `update_workflow_action(workflow_name, "refine_idea", "done", deliverables=[...])` in completion step
- [ ] AC-038.31: Skill outputs MCP response status for verification

**Dependencies:**
- FEATURE-038-A (Action Execution Modal — provides the execution trigger)
- FEATURE-038-B (Session Idle Detection — provides session management)

**Technical Considerations:**
- This is a skill update, not a code implementation — modifies `.github/skills/` files
- The `refined-idea/` subfolder coexists with `idea-summary-vN.md`
- MCP `update_workflow_action` tool already exists — no new endpoints needed

---

#### FEATURE-038-E: Execution Skill DoD Update

**Version:** v1.0
**Brief Description:** Add a new workflow status verification checkpoint to `x-ipe-workflow-task-execution` skill's Step 5 (Check Global DoD). If the completed skill's `task_completion_output` declares workflow action interaction, verify that `update_workflow_action` was called (action status NOT still `pending` in workflow JSON). On failure, flag task as incomplete.

**Acceptance Criteria:**
- [ ] AC-038.32: x-ipe-workflow-task-execution Step 5 includes workflow status verification
- [ ] AC-038.33: Verification checks: action status in workflow JSON is NOT `pending` after skill completion
- [ ] AC-038.34: On verification failure, task flagged as incomplete with message

**Dependencies:**
- None (standalone skill update)

**Technical Considerations:**
- This is a skill update to `.github/skills/x-ipe-workflow-task-execution/SKILL.md`
- Only applies when skill output declares workflow action interaction
- Requires reading workflow JSON to verify status

### Open Questions

- None — all ambiguities resolved during clarification.

---

## EPIC-039: CR-Folder Browser Modal

### Project Overview

A Change Request on **FEATURE-038-C** (Enhanced Deliverable Viewer) to replace the inline folder tree with a **Folder Browser Modal** — a two-panel file explorer (tree + preview) that opens when clicking a folder deliverable card. Additionally: distinct folder card background, search/filter, breadcrumb navigation, typed file icons, image preview, and file download.

> Source: IDEA-026 (CR-Modal Window - Workflow-Deliverable Folder)
> Status: Proposed
> Priority: Medium
> Idea Summary: [idea-summary-v1.md](../ideas/026.%20CR-Modal%20Window%20-%20Workflow-Deliverable%20Folder/refined-idea/idea-summary-v1.md)
> Feedback: Feedback-20260222-110609

### User Request

The user wants:
1. Folder deliverable cards to have a **different background color** from file cards for visual distinction
2. **Remove all inline folder tree code** — no expandable tree within the card
3. Clicking a folder card opens a **modal window (80vw)** with:
   - Left panel (30%): folder tree navigation
   - Right panel (70%): file preview
   - Breadcrumb path above panels
   - Search/filter bar
   - Download button per file
4. Pattern follows the **LinkExistingPanel** UX from compose-idea-modal (tree+preview, no editing)

### Clarifications

| # | Question | Answer |
|---|----------|--------|
| 1 | Search bar in modal? | Yes — filter files/folders recursively, case-insensitive on name |
| 2 | File actions in preview? | Read-only preview + download button |
| 3 | Modal size? | 80vw — consistent with other content modals |
| 4 | Breadcrumb navigation? | Yes — shows full path context above panels |
| 5 | File type icons? | Yes — 📝 .md, 🖼️ images, 💻 code, 📄 other |
| 6 | Image preview support? | Yes — inline rendering of .png/.jpg/.svg |
| 7 | Folder download as ZIP? | No — out of scope, individual file download only |

### High-Level Requirements

1. **HLR-039.1: Folder Card Visual Distinction** — Folder-type deliverable cards MUST have a visually distinct background color from file-type cards (e.g., CSS variable `--deliverable-folder-bg`)
2. **HLR-039.2: Remove Inline Folder Tree** — All code for the expandable inline folder tree MUST be removed: `_expandFolderTree()`, expand/collapse toggle, `.deliverable-tree` container, inline preview backdrop. No dead code.
3. **HLR-039.3: Folder Browser Modal** — Clicking a folder card opens a modal (80vw) with:
   - Breadcrumb showing current folder path
   - Search/filter bar (filters file+folder names recursively, case-insensitive)
   - Tree panel (left 30%) with recursive folder tree, typed file icons
   - Preview panel (right 70%) with auto-detected rendering:
     - Markdown → HTML via marked.js
     - Images (.png, .jpg, .svg) → inline `<img>`
     - Code/text → preformatted `<pre>`
     - Binary/unsupported → file info + download prompt
   - Download button for currently previewed file
4. **HLR-039.4: Modal Lifecycle** — Modal closes via close button, Escape key, or backdrop click. Loading spinner while tree API is in-flight.
5. **HLR-039.5: Keyboard Accessibility** — Escape to close, Tab between panels, arrow keys for tree navigation. ARIA roles for modal and tree.
6. **HLR-039.6: Reuse Existing APIs** — No new backend endpoints needed. Uses existing `GET /api/workflow/{wf}/deliverables/tree` and `GET /api/ideas/file`.

### Functional Requirements

**FR-039.1: Folder Card Styling**
- Folder-type deliverable cards use a distinct background color via CSS variable
- Folder icon and name displayed; no expand/collapse toggle
- Click anywhere on card opens the Folder Browser Modal

**FR-039.2: Dead Code Removal**
- Remove `_expandFolderTree()` method from deliverable-viewer.js
- Remove expand/collapse toggle button (▸/▾) from folder card rendering
- Remove `.deliverable-tree` container and nested tree CSS
- Remove `.deliverable-preview-backdrop` (inline preview overlay)
- Remove all related event listeners and DOM manipulation code

**FR-039.3: Folder Browser Modal — Structure**
- Modal width: 80vw, centered, with backdrop overlay
- Header: breadcrumb path + close button
- Below header: search/filter input
- Body: two-panel flexbox (left 30% tree, right 70% preview)
- Footer: download button (enabled when file selected)

**FR-039.4: Folder Browser Modal — Tree Panel**
- Fetch folder tree from `GET /api/workflow/{wf}/deliverables/tree?path={folder}`
- Render recursive tree with expand/collapse per folder node
- File icons based on extension: 📝 `.md`, 🖼️ `.png/.jpg/.svg`, 💻 `.js/.py/.css/.html`, 📄 other
- Click file → load preview in right panel
- Click folder → expand/collapse

**FR-039.5: Folder Browser Modal — Preview Panel**
- Fetch file content from `GET /api/ideas/file?path={file}`
- Auto-detect rendering:
  - `.md` → `marked.parse()` into `<div class="markdown-body">`
  - `.png/.jpg/.jpeg/.gif/.svg` → `<img src="data:..." />` or direct URL
  - `.js/.py/.css/.html/.json/.yaml/.txt` → `<pre><code>` preformatted
  - Binary/unknown → file name + size + "Download" button (no preview)
- Show file name as preview header
- Large files (>1MB text) → truncate with "File too large to preview — download instead"

**FR-039.6: Search/Filter**
- Input field above tree panel
- Filters tree nodes (file and folder names) case-insensitive
- Recursive: matches in nested folders expand parent folders
- Real-time filtering on keyup (debounced 200ms)

**FR-039.7: Breadcrumb Navigation**
- Shows path segments separated by `/` (e.g., `ideas / 026 / refined-idea /`)
- Truncates with "..." for paths > 5 segments
- Display only; not clickable (modal is scoped to one folder)

**FR-039.8: File Download**
- Download button in preview panel footer
- Downloads currently selected file via browser download (Content-Disposition)
- Disabled when no file selected

### Non-Functional Requirements

- **NFR-039.1:** Modal tree render completes within 500ms for folders up to 50 files
- **NFR-039.2:** File preview fetch and render completes within 1s for files up to 100KB
- **NFR-039.3:** No additional JS libraries — uses native DOM + existing marked.js
- **NFR-039.4:** CSS variables for folder card background (themeable)

### Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty folder | Tree panel shows "This folder is empty" message |
| File fails to load | Preview panel shows error with "Retry" button |
| Large files (>1MB text) | Truncate preview, show "File too large — download instead" |
| Binary files (.pdf, .zip) | Show file icon, name, size + "Download" (no inline preview) |
| Deeply nested folders (>5 levels) | Tree supports unlimited nesting; breadcrumb truncates |
| Special characters in filenames | URL-encode paths in API calls |
| Folder path doesn't exist | Card shows existing "⚠️ not found" pattern |
| Path traversal attempt | Rejected by backend path scoping (existing protection) |

### Related Features (Conflict Review)

| Existing Feature | Overlap Type | Decision |
|-----------------|--------------|----------|
| FEATURE-038-C (Enhanced Deliverable Viewer) | Functional replacement — inline tree+preview replaced by modal | **CR on FEATURE-038-C** — same responsibility, same users, same domain |
| FEATURE-036-E (Deliverables, Polling & Lifecycle) | Indirect — base card grid, folder detection | No change needed — folder detection logic remains |
| FEATURE-037-B (Compose Idea Modal — Link Existing) | Pattern reference — tree+preview layout | No change — reuse pattern only |

### Constraints

- Reuses existing backend APIs (no new endpoints)
- Pattern follows LinkExistingPanel from compose-idea-modal
- Dead code removal must be clean (no unused CSS/JS)
- Folder card background uses CSS variable for themability
- ARIA roles required for accessibility compliance

### Open Questions

- None — all ambiguities resolved during ideation and clarification.

---

### Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-039-A | EPIC-039 | Folder Browser Modal (MVP) | v1.0 | Remove inline tree, add folder card distinct bg, click opens two-panel modal (tree left, preview right). Markdown+text preview, loading spinner, close via button/Escape/backdrop. | None |
| FEATURE-039-B | EPIC-039 | Enhanced Modal Features | v1.0 | Add search/filter bar, breadcrumb navigation, typed file icons, image preview, download button, keyboard accessibility (Tab/arrows), ARIA roles. Edge cases: empty folder, load errors, large/binary files. | FEATURE-039-A |

---

### Feature Details

#### FEATURE-039-A: Folder Browser Modal (MVP)

**Version:** v1.0
**Brief Description:** Core feature: remove inline folder tree code, give folder cards a distinct background color, and when a folder card is clicked, open a modal window (80vw) with tree panel (left 30%) and preview panel (right 70%). Preview supports markdown (via marked.js) and plain text. Modal has loading spinner, close button, Escape key, and backdrop click to close. Reuses existing API endpoints.

**Acceptance Criteria:**
- [ ] AC-039.1: Folder cards have visually distinct background from file cards (CSS variable `--deliverable-folder-bg`)
- [ ] AC-039.2: Inline folder tree code fully removed (`_expandFolderTree()`, expand toggle, `.deliverable-tree`, inline preview backdrop)
- [ ] AC-039.3: No dead CSS/JS remains from inline tree implementation
- [ ] AC-039.4: Clicking folder card opens modal (80vw) with backdrop overlay
- [ ] AC-039.5: Modal fetches folder tree from `GET /api/workflow/{wf}/deliverables/tree?path={folder}`
- [ ] AC-039.6: Tree panel (left 30%) renders recursive folder structure with expand/collapse per folder
- [ ] AC-039.7: Clicking a file in tree loads preview in right panel via `GET /api/ideas/file?path={file}`
- [ ] AC-039.8: Markdown files rendered as HTML via `marked.parse()`; text/code files shown in `<pre>`
- [ ] AC-039.9: Loading spinner shown while tree API call is in-flight
- [ ] AC-039.10: Modal closes via close button, Escape key, or backdrop click

**Dependencies:**
- FEATURE-038-C (CR target — being replaced)
- FEATURE-036-E (Deliverables base — folder detection remains)

**Technical Considerations:**
- Remove `_expandFolderTree()`, expand/collapse toggle, `.deliverable-tree` CSS, `.deliverable-preview-backdrop` from deliverable-viewer.js and workflow.css
- New `FolderBrowserModal` class following same pattern as `ComposeIdeaModal` / `LinkExistingPanel`
- Reuse existing API endpoints — no backend changes

**Linked Mockups:**
- N/A (text-based idea summary — no visual mockup)

---

#### FEATURE-039-B: Enhanced Modal Features

**Version:** v1.0
**Brief Description:** Extend the Folder Browser Modal with search/filter bar (case-insensitive, recursive), breadcrumb navigation, typed file icons (📝 .md, 🖼️ images, 💻 code, 📄 other), image preview (inline `<img>` for .png/.jpg/.svg), download button per file, keyboard accessibility (Tab between panels, arrow keys in tree), ARIA roles (`role="dialog"`, `role="tree"`). Handles edge cases: empty folder, file load errors, large files (>1MB truncate), binary files (download only).

**Acceptance Criteria:**
- [ ] AC-039.11: Search/filter bar filters file+folder names recursively (case-insensitive, debounced 200ms)
- [ ] AC-039.12: Breadcrumb shows current folder path; truncates with "..." for >5 segments
- [ ] AC-039.13: Files show type-specific icons (📝 .md, 🖼️ images, 💻 code, 📄 other)
- [ ] AC-039.14: Image files (.png/.jpg/.svg) render inline in preview panel
- [ ] AC-039.15: Download button downloads currently selected file; disabled when no file selected
- [ ] AC-039.16: Binary/unsupported files show file info + "Download" button (no inline preview)
- [ ] AC-039.17: Large files (>1MB text) truncated with "File too large — download instead"
- [ ] AC-039.18: Empty folder shows "This folder is empty" message in tree panel
- [ ] AC-039.19: File load failure shows error message with "Retry" button
- [ ] AC-039.20: Keyboard: Escape closes, Tab moves between panels, arrow keys navigate tree
- [ ] AC-039.21: ARIA roles: modal (`role="dialog"`), tree (`role="tree"`, `role="treeitem"`)

**Dependencies:**
- FEATURE-039-A (Folder Browser Modal MVP)

**Technical Considerations:**
- Search filter can reuse pattern from LinkExistingPanel's `_filterTree()`
- Image preview: detect extension, render as `<img>` with file API URL or base64
- Download: use `Content-Disposition: attachment` header or create blob URL
- ARIA attributes added to modal container and tree elements

**Linked Mockups:**
- N/A (text-based idea summary — no visual mockup)
