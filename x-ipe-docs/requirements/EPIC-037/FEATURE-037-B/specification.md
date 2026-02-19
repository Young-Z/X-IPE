# Feature Specification: Compose Idea Modal — Link Existing & Re-Edit

> Feature ID: FEATURE-037-B
> Epic: EPIC-037 (Compose Idea Modal)
> Version: v1.1
> Status: Refined
> Last Updated: 02-19-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-19-2026 | Initial specification (Link Existing + Re-Edit) |
| v1.1 | 02-19-2026 | CR-001: Enriched Re-Edit with stage gate, confirmation dialog, edit mode, file auto-detection |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Compose Idea Modal | HTML | [../mockups/compose-idea-modal-v1.html](../mockups/compose-idea-modal-v1.html) | Shared mockup — Create New and Link Existing modes | current |

> **Note:** Shared mockup at Epic level covers FEATURE-037-A (Create New) and this feature (Link Existing + Re-Edit). The Link Existing tab in the mockup is the primary reference. Re-Edit mode reuses the same modal layout with pre-populated content — no separate mockup needed.

## Overview

FEATURE-037-B extends the Compose Idea Modal (EPIC-037) with two capabilities that FEATURE-037-A explicitly deferred:

1. **Link Existing mode** — Instead of composing a new idea, the user can browse the project's existing idea folder tree, preview files, and link an existing idea to the workflow. This replaces the placeholder "Available in next update" shown in 037-A's Link Existing toggle.

2. **Re-Edit mode** (enriched by CR-001) — After `compose_idea` is marked "done", clicking it again allows the user to re-open the modal with pre-loaded content for editing. A stage gate check prevents re-opening if downstream actions have already started. A confirmation dialog ensures intentional re-opening.

The primary user is a developer running an X-IPE engineering workflow who needs to either link an existing idea document or fix/refine a previously composed idea.

## User Stories

### US-001: Link Existing Idea to Workflow
**As** a developer using an X-IPE engineering workflow,
**I want** to browse my existing ideas folder and select an idea to link,
**So that** I can reuse a previously written idea document instead of composing a new one.

### US-002: Preview Before Linking
**As** a developer,
**I want** to preview an idea file's content before linking it,
**So that** I can confirm I'm selecting the correct document.

### US-003: Search Ideas Quickly
**As** a developer with many idea folders,
**I want** to filter the file tree by typing a search term,
**So that** I can quickly find the idea I'm looking for.

### US-004: Re-Edit a Composed Idea
**As** a developer who has already completed compose_idea,
**I want** to click the action again and re-open the modal with my existing content,
**So that** I can fix typos, refine content, or replace the idea file.

### US-005: Safe Re-Opening with Stage Gate
**As** a developer,
**I want** the system to prevent re-opening compose_idea if downstream stages have started,
**So that** I don't invalidate work that already depends on the current idea.

## Acceptance Criteria

### AC Group: Link Existing Mode

- **AC-001**: Clicking "Link Existing" toggle replaces the Create New content area with a file tree sidebar and preview panel.
- **AC-002**: File tree fetches data from `GET /api/ideas/tree` and renders expandable folder/file hierarchy.
- **AC-003**: A text input above the file tree filters items client-side as the user types (instant filter on folder and file names).
- **AC-004**: Clicking a `.md` file in the tree renders its content in the preview panel using `marked.js`.
- **AC-005**: Clicking a non-markdown file (`.pdf`, `.png`, `.txt`, etc.) shows file metadata (name, size, type) in the preview panel.
- **AC-006**: "Confirm Link" button in the footer is disabled until a file is selected.
- **AC-007**: On confirm, the selected file path and its root idea folder name are stored as deliverables via Workflow Manager API, and `compose_idea` auto-completes.
- **AC-008**: Modal closes on success; workflow stage view refreshes.
- **AC-009**: If the tree is empty (no ideas exist), a message "No existing ideas found. Use Create New instead." is shown.

### AC Group: Re-Edit Mode — Stage Gate (CR-001)

- **AC-010**: Clicking a `compose_idea` action that is already "done" triggers a stage gate check.
- **AC-011**: Stage gate: the system checks if any action in the **next stage** (requirement) has status `in_progress` or `done`.
- **AC-012**: If the gate check fails (downstream actions started), an error toast is shown: "Cannot re-open — requirement stage has already started."
- **AC-013**: If the gate check passes, a confirmation dialog is shown: "Re-open for editing? This will set the action back to pending." with Confirm/Cancel buttons.
- **AC-014**: The gate check function `_canReopenAction(actionKey, stages)` is reusable — not hardcoded to `compose_idea` — so other actions can use the same pattern in the future.

### AC Group: Re-Edit Mode — Edit Modal (CR-001)

- **AC-015**: After confirmation, the `compose_idea` action status is rolled back to `pending` via the Workflow Manager API.
- **AC-016**: `ComposeIdeaModal` opens in edit mode with the existing idea file content pre-loaded in EasyMDE.
- **AC-017**: The idea folder name is pre-filled and read-only (not editable in re-edit mode).
- **AC-018**: File path is auto-detected from the `deliverables` array in the workflow JSON (no user input needed).
- **AC-019**: File content is fetched via `GET /api/ideas/file?path={relative-path}` with path security validation (path must be within project root).
- **AC-020**: The submit button label reads "Update Idea" instead of "Submit Idea" in edit mode.
- **AC-021**: On submit, the file is overwritten in-place (same path, same folder). No version increment.
- **AC-022**: After successful update, `compose_idea` is re-completed as "done" with the same deliverables.
- **AC-023**: Modal closes on success; workflow refreshes.

### AC Group: Error Handling

- **AC-024**: `GET /api/ideas/file` returns 404 if the deliverable file no longer exists → error toast: "Original idea file not found. Create a new idea instead."
- **AC-025**: `GET /api/ideas/file` returns 403 if the path is outside the project root → error toast: "Invalid file path."
- **AC-026**: Network failure during re-edit save → error toast with "Retry" button, modal stays open.
- **AC-027**: If `compose_idea` has no deliverables in workflow JSON → treat as if action is "pending" (open in create mode, not edit mode).

### AC Group: Mockup Alignment

- **AC-028**: Link Existing mode layout MUST match the approved mockup (`compose-idea-modal-v1.html`) — file tree sidebar on the left, preview panel on the right.
- **AC-029**: Visual styling (colors, spacing, typography) MUST be consistent with mockup — Slate/Emerald palette, DM Sans font, 8px spacing unit.
- **AC-030**: Interactive elements shown in the mockup MUST be present and functional — toggle buttons, tree expand/collapse, search input, file selection highlight.

## Functional Requirements

### FR-037-B.1: Link Existing — File Tree Browser

**Description:** Render a navigable file tree from the ideas directory when "Link Existing" mode is active.

**Details:**
- Input: `GET /api/ideas/tree` response (existing endpoint used by Workplace sidebar)
- Process: Parse tree JSON, render expandable folder/file hierarchy in the left panel
- Output: Interactive file tree with expand/collapse, click-to-select
- Constraints: Tree is read-only (no create/delete from this view)

### FR-037-B.2: Link Existing — Tree Search/Filter

**Description:** Client-side text filter above the file tree.

**Details:**
- Input: User types in search input
- Process: Filter tree items by matching folder/file names (case-insensitive substring match). Show matching items with their parent folders expanded.
- Output: Filtered tree; empty state message if no matches
- Constraints: Filter is client-side only (no API call per keystroke)

### FR-037-B.3: Link Existing — Preview Panel

**Description:** Show selected file content in a read-only preview panel.

**Details:**
- Input: Selected file path from tree
- Process: Fetch file content via `GET /api/ideas/file?path={relative-path}`. For `.md` files, render via `marked.js`. For images (`.png`, `.jpg`), render inline. For other types, show metadata (name, size, extension).
- Output: Rendered preview in right panel
- Constraints: Preview is read-only, no editing

### FR-037-B.4: Link Existing — Confirm & Link

**Description:** Submit the linked file as the workflow's idea.

**Details:**
- Input: Selected file path + root idea folder name
- Process: Call Workflow Manager API to update `compose_idea` action to "done" with deliverables `{ file: "{path}", folder: "{folder-name}" }`
- Output: Action completed, modal closed, workflow view refreshed
- Constraints: Same deliverable format as Create New mode (FEATURE-037-A)

### FR-037-B.5: Re-Edit — Stage Gate Check (CR-001)

**Description:** Determine if a completed action can be safely re-opened.

**Details:**
- Input: Action key (e.g., `compose_idea`), full stages object from workflow JSON
- Process: Identify the current action's stage, find the next stage in sequence, check if any action in the next stage has status `in_progress` or `done`
- Output: Boolean — `true` if re-open is allowed, `false` if blocked
- Constraints: Implemented as reusable function `_canReopenAction(actionKey, stages)` in workflow-stage.js. Uses `ACTION_MAP` stage ordering to determine "next stage".

### FR-037-B.6: Re-Edit — Confirmation Dialog (CR-001)

**Description:** Show a confirmation dialog before re-opening a completed action.

**Details:**
- Input: Gate check passes
- Process: Show dialog: "Re-open for editing? This will set the action back to pending." with Confirm/Cancel buttons. Reuse existing `workflow-modal` dialog pattern.
- Output: User confirms → proceed to status rollback; user cancels → no-op

### FR-037-B.7: Re-Edit — Status Rollback & Edit Mode (CR-001)

**Description:** Roll back action status and open modal in edit mode with pre-loaded content.

**Details:**
- Input: User confirmed re-open
- Process:
  1. Call Workflow Manager API to set `compose_idea` status back to `pending`
  2. Extract file path from deliverables in workflow JSON
  3. Fetch file content via `GET /api/ideas/file?path={path}`
  4. Open `ComposeIdeaModal` with `{ mode: 'edit', filePath, folderPath, folderName }`
  5. Pre-populate EasyMDE with file content, set folder name (read-only), change button to "Update Idea"
- Output: Modal open in edit mode with existing content loaded
- Constraints: Folder name is read-only in edit mode (changing folders would break deliverable references)

### FR-037-B.8: Re-Edit — File Content API (CR-001)

**Description:** Backend endpoint to fetch raw idea file content.

**Details:**
- Input: `GET /api/ideas/file?path={relative-path}` where path is relative to project root
- Process: Validate path is within project root (prevent path traversal attacks — reject `..`, absolute paths, symlinks outside root). Read file content. Return as plain text.
- Output: 200 + file content (plain text), 404 if not found, 403 if path outside project root
- Constraints: New endpoint in `ideas_routes.py`. Only files within the project root directory are accessible.

## Non-Functional Requirements

| NFR ID | Description |
|--------|-------------|
| NFR-037-B.1 | File tree loads within 500ms for up to 200 idea folders |
| NFR-037-B.2 | Search filter responds within 100ms per keystroke (client-side) |
| NFR-037-B.3 | Preview panel renders markdown within 300ms |
| NFR-037-B.4 | Stage gate check completes within 100ms (uses in-memory workflow JSON) |
| NFR-037-B.5 | Path validation rejects traversal attempts without leaking file system information |
| NFR-037-B.6 | No memory leaks: EasyMDE and event listeners cleaned up on every modal close (same as 037-A) |

## UI/UX Requirements

### Component Inventory (from mockup)

| Component | Mockup Element | Notes |
|-----------|---------------|-------|
| File tree sidebar | Left panel in Link Existing mode | Expandable folders, file icons, selection highlight |
| Search input | Text field above file tree | Placeholder "Search ideas..." |
| Preview panel | Right panel in Link Existing mode | Rendered markdown or file metadata |
| Confirm Link button | Footer action button | Disabled until file selected, emerald accent |
| Confirmation dialog | Modal overlay | "Re-open for editing?" with Confirm/Cancel (CR-001) |
| Update Idea button | Footer action button in edit mode | Replaces "Submit Idea" label (CR-001) |

### User Interaction Flows

**Flow A — Link Existing:**
1. User clicks "Compose Idea" → modal opens in Create New mode (default)
2. User clicks "Link Existing" toggle → file tree + preview panel appear
3. User optionally types in search to filter tree
4. User clicks a folder to expand → clicks a file to select
5. Preview panel shows file content
6. User clicks "Confirm Link" → action completes → modal closes

**Flow B — Re-Edit (CR-001):**
1. User clicks a completed "Compose Idea" action (green checkmark)
2. System runs stage gate check → passes (no downstream actions started)
3. Confirmation dialog: "Re-open for editing?" → user clicks Confirm
4. Action status rolled back to pending
5. Modal opens in edit mode: folder name read-only, EasyMDE pre-loaded with content
6. User edits content → clicks "Update Idea"
7. File overwritten → action re-completed → modal closes

**Flow C — Blocked Re-Edit (CR-001):**
1. User clicks a completed "Compose Idea" action
2. System runs stage gate check → fails (requirement_gathering is "in_progress")
3. Error toast: "Cannot re-open — requirement stage has already started."
4. No modal opens

### States

| State | Behavior |
|-------|----------|
| Link Existing — no selection | Confirm Link disabled, preview shows "Select a file to preview" |
| Link Existing — file selected | Confirm Link enabled, preview shows content |
| Link Existing — empty tree | Message: "No existing ideas found. Use Create New instead." |
| Re-Edit — gate passed | Confirmation dialog shown |
| Re-Edit — gate failed | Error toast, no modal |
| Re-Edit — loading content | Spinner in modal while fetching file |
| Re-Edit — file not found | Error toast: "Original idea file not found" |

## Dependencies

### Internal Dependencies

| Feature | Type | Description |
|---------|------|-------------|
| FEATURE-037-A | Required | Modal container, toggle UI, name input, compose/upload tabs, submit handler, auto-complete mechanism |
| FEATURE-036-C | Required | Stage ribbon action buttons — click handler for completed actions must change from toast to gate check |
| FEATURE-036-A | Required | Workflow Manager API — action status update (rollback to pending + re-complete) |
| FEATURE-008 | Required | Workplace JS (`setupComposer`, `setupUploader`) and `/api/ideas/tree` endpoint |

### External Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| EasyMDE | Library | Markdown editor (already in app) |
| marked.js | Library | Markdown rendering for preview (already in app) |

## Business Rules

- **BR-001**: A user can only re-open `compose_idea` if no action in the next stage (requirement) has moved to `in_progress` or `done`.
- **BR-002**: Re-edit overwrites the original file in-place. Git history serves as the rollback mechanism.
- **BR-003**: The folder name is immutable in edit mode — changing it would break deliverable references.
- **BR-004**: Linking an existing idea uses the same deliverable format as creating a new one (`file` + `folder`).
- **BR-005**: The stage gate is a general rule: it applies to any action, not just `compose_idea`.
- **BR-006**: If deliverables are missing from workflow JSON, clicking a completed `compose_idea` opens in create mode (not edit mode).

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| Idea file deleted after compose_idea completed | Re-edit API returns 404 → error toast, user must create new idea |
| Deliverables missing from workflow JSON | Open in create mode (no pre-load) |
| Next stage has a "done" action but user wants to re-open | Blocked — gate check prevents re-open |
| User cancels confirmation dialog | No action taken, status unchanged |
| File path contains `..` or absolute path | API returns 403, request rejected |
| Very large markdown file (>1MB) | Preview renders normally (marked.js handles large content) |
| Non-UTF8 file selected for preview | Show metadata only (name, size), no content rendering |
| Multiple users editing same workflow | Last write wins (no concurrency lock) |
| Ideas tree has 500+ folders | Client-side filter may be slow — NFR-037-B.1 sets 500ms target |
| Compose_idea status rolled back but modal close before save | Action stays as "pending" — user must re-compose or manual status reset |

## Out of Scope

- **Draft persistence / auto-save** — explicitly excluded per EPIC-037 requirements
- **File editing from Link Existing mode** — linked files are read-only; user must unlink and create new to edit
- **Concurrency locking** — no multi-user lock mechanism; last write wins
- **Version history for idea files** — git provides this; no in-app version UI
- **Re-edit for actions other than compose_idea** — gate check is reusable, but only compose_idea gets the edit modal in this feature
- **Recursive linking** — linking to a file that references another idea is treated as a simple file link

## Technical Considerations

- The `_canReopenAction()` function needs access to the `ACTION_MAP` stage ordering (ideation → requirement → implement → validation → feedback) to determine which stage is "next"
- The file content API endpoint should be added to `ideas_routes.py` alongside the existing `/api/ideas/tree` and `/api/ideas/upload` endpoints
- `ComposeIdeaModal` constructor currently accepts `{ workflowName, onComplete }` — needs to be extended with optional `{ mode, filePath, folderPath, folderName }` parameters
- In edit mode, the `AutoFolderNamer` is not used — folder name comes from deliverables
- The confirmation dialog should reuse the existing modal pattern from `workflow-stage.js` `_showPromptModal()`
- The toggle between Create New and Link Existing must be bidirectional — currently 037-A only supports Create New → placeholder; 037-B replaces the placeholder with real Link Existing UI
- Path security validation should use `os.path.realpath()` and verify the resolved path starts with the project root

## Open Questions

- None — all clarifications resolved during IDEA-024 brainstorming (scope, gate rule, editing semantics, file detection, history approach).
