# Feature Specification: Compose Idea Modal — Create New

> Feature ID: FEATURE-037-A
> Epic: EPIC-037 (Compose Idea Modal)
> Version: v1.0
> Status: Refined
> Last Updated: 02-19-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-19-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Compose Idea Modal | HTML | [../mockups/compose-idea-modal-v1.html](../mockups/compose-idea-modal-v1.html) | Interactive modal with Create New and Link Existing modes | current |

> **Note:** Shared mockup at Epic level covers both FEATURE-037-A (Create New mode) and FEATURE-037-B (Link Existing mode). This specification focuses on the Create New mode elements.

## Overview

FEATURE-037-A replaces the current basic prompt-based "Compose Idea" workflow action (FR-036-C.4) with a rich modal dialog featuring a Create New mode. When a user clicks "Compose Idea" in the workflow Ideation stage, a full-featured modal opens — without navigating away — providing a name input, tabbed Compose (Markdown) / Upload interface, automatic folder naming (`wf-NNN-{sanitized-name}`), and automatic workflow action completion.

This is the MVP feature for EPIC-037. It delivers the core value: composing a new idea entirely within the workflow view. The existing Workplace `setupComposer()` and `setupUploader()` functions must be refactored to accept a container parameter (currently hardcoded to `#workplace-*` DOM IDs) to enable reuse in this modal.

The primary user is a developer running an X-IPE engineering workflow who wants to compose or upload an idea as the first step of the Ideation stage.

## User Stories

### US-001: Compose Idea Without Leaving Workflow
**As** a developer using X-IPE engineering workflow,
**I want** to click "Compose Idea" and have a modal open right in the workflow view,
**So that** I can compose my idea without losing workflow context.

### US-002: Write Idea in Markdown
**As** a developer,
**I want** a Markdown editor with toolbar (bold, italic, headings, lists, code, preview) in the modal,
**So that** I can write a well-formatted idea document.

### US-003: Upload Idea Files
**As** a developer,
**I want** a drag-and-drop upload zone in the modal,
**So that** I can attach existing documents, images, or code files to my idea.

### US-004: Auto-Named Idea Folder
**As** a developer,
**I want** the idea folder to be automatically named based on my idea name,
**So that** I don't have to manually create folders or worry about naming conventions.

### US-005: Automatic Workflow Progression
**As** a developer,
**I want** the compose_idea action to automatically mark as "done" after I submit,
**So that** the workflow progresses without manual status updates.

## Acceptance Criteria

### AC Group: Modal Lifecycle

- **AC-001**: Clicking "Compose Idea" action in the workflow Ideation stage opens the modal dialog.
- **AC-002**: Modal appears as centered overlay (max-width ~720px) with semi-transparent backdrop.
- **AC-003**: Modal has header ("Compose Idea"), close button (×), and action footer (Cancel / Submit Idea).
- **AC-004**: Close via × button, Escape key, or Cancel button dismisses the modal.
- **AC-005**: Clicking the overlay backdrop does NOT close the modal (prevents accidental content loss).
- **AC-006**: Content is lost on close — no draft persistence.

### AC Group: Toggle Mode

- **AC-007**: Top area shows [Create New] / [Link Existing] toggle buttons.
- **AC-008**: "Create New" is the default active toggle on open.
- **AC-009**: "Link Existing" toggle shows a placeholder message ("Available in next update") until FEATURE-037-B is implemented.
- **AC-010**: Name input value is preserved when toggling between modes.

### AC Group: Idea Name Input

- **AC-011**: Required text input labeled "Idea Name" appears below the toggle.
- **AC-012**: Live word counter displays current/max words (e.g., "3 / 10 words").
- **AC-013**: Validation prevents submit when name exceeds 10 words or is empty.
- **AC-014**: Inline validation error message shown when rules are violated.

### AC Group: Compose Tab

- **AC-015**: "Compose" tab is the default active tab.
- **AC-016**: Tab content shows EasyMDE Markdown editor with toolbar buttons: Bold, Italic, Heading, Bulleted List, Numbered List, Link, Code, Preview.
- **AC-017**: Editor placeholder text guides the user (e.g., "Write your idea in Markdown...").
- **AC-018**: EasyMDE instance is properly destroyed on modal close (no memory leaks verified by absence of orphaned DOM elements).

### AC Group: Upload Tab

- **AC-019**: Clicking "Upload" tab switches to drag-and-drop upload zone.
- **AC-020**: Upload zone accepts: md, txt, pdf, png, jpg, py, js, docx files.
- **AC-021**: Visual feedback shown on file drag-over (highlight zone).
- **AC-022**: Uploaded files listed with name and size; removable before submit.

### AC Group: Submit & Auto-Complete

- **AC-023**: "Submit Idea" button is disabled until name input is valid AND (compose content exists OR files uploaded).
- **AC-024**: On submit, folder name generated as `wf-{NNN}-{sanitized-name}` where NNN = highest existing `wf-XXX` + 1, zero-padded 3 digits.
- **AC-025**: Name sanitization: lowercase, spaces → hyphens, remove special chars, max 50 chars.
- **AC-026**: Submit calls `POST /api/ideas/upload` with generated folder name and content/files.
- **AC-027**: On success, `compose_idea` action auto-completes via Workflow Manager API with deliverables: `{ file: "<file-path>", folder: "<folder-name>" }`.
- **AC-028**: Modal closes on successful submit; workflow stage view refreshes to show updated action state.

### AC Group: Error Handling

- **AC-029**: Folder name collision (API returns 409): inline error toast in modal, modal stays open, user can edit name and retry.
- **AC-030**: API failure (5xx): error toast with "Retry" option, modal stays open.
- **AC-031**: Upload cancellation (modal closed mid-upload): in-flight requests cancelled, no partial files saved.

### AC Group: Mockup Alignment

- **AC-032**: UI layout of Create New mode MUST match the approved mockup (`compose-idea-modal-v1.html`) — modal container, toggle buttons, name input, tab bar, editor area, action footer.
- **AC-033**: Visual styling (colors, spacing, typography) MUST be consistent with mockup — Slate/Emerald palette, DM Sans font, 8px spacing unit.
- **AC-034**: Interactive elements shown in mockup MUST be present and functional — toggle buttons, tab switching, toolbar buttons, word counter.

### AC Group: Workplace JS Refactoring

- **AC-035**: `setupComposer(containerEl)` accepts an optional container element parameter; defaults to existing `#workplace-*` selectors when not provided (backward compatible).
- **AC-036**: `setupUploader(containerEl)` accepts an optional container element parameter; defaults to existing `#workplace-*` selectors when not provided (backward compatible).
- **AC-037**: Existing Workplace compose/upload functionality continues to work without changes after refactoring.

## Functional Requirements

### FR-037-A.1: Modal Container

**Description:** Render a centered overlay modal when "Compose Idea" is triggered.

**Details:**
- Input: "Compose Idea" action button click from FEATURE-036-C stage ribbon
- Process: Create modal DOM elements (overlay, dialog, header, content, footer), attach event listeners for close actions
- Output: Visible modal dialog over the workflow view
- Constraints: z-index above workflow view (1000+), overlay rgba(0,0,0,0.4), border-radius 10-12px

### FR-037-A.2: Toggle Mode Controller

**Description:** Manage switching between Create New and Link Existing modes.

**Details:**
- Input: Toggle button clicks
- Process: Show/hide content areas based on active toggle, persist name input across toggles
- Output: Active mode's content visible, inactive hidden
- Note: Link Existing mode shows placeholder until FEATURE-037-B

### FR-037-A.3: Idea Name Input & Validation

**Description:** Validate idea name with word count and sanitization rules.

**Details:**
- Input: User text input
- Process: Count words (split by whitespace), validate ≤ 10 words and non-empty, sanitize for folder name (lowercase, hyphens, no special chars, max 50 chars)
- Output: Validated name + sanitized folder suffix; inline error if invalid

### FR-037-A.4: Compose Tab (EasyMDE)

**Description:** Provide Markdown editor using EasyMDE within modal.

**Details:**
- Input: Refactored `setupComposer(containerEl)` call with modal's compose container
- Process: Initialize EasyMDE with toolbar config, bind to textarea in modal
- Output: Functional Markdown editor with toolbar
- Cleanup: Destroy EasyMDE instance on modal close via `editor.toTextArea()` + remove

### FR-037-A.5: Upload Tab

**Description:** Provide drag-and-drop file upload zone within modal.

**Details:**
- Input: Refactored `setupUploader(containerEl)` call with modal's upload container
- Process: Initialize drag-and-drop zone, handle file selection, validate file types, display file list
- Output: List of selected files ready for upload on submit
- Accepted types: md, txt, pdf, png, jpg, py, js, docx

### FR-037-A.6: Auto Folder Naming

**Description:** Generate unique `wf-NNN-{name}` folder names.

**Details:**
- Input: Sanitized idea name + ideas tree data
- Process: Fetch `/api/ideas/tree`, find highest `wf-XXX` prefix, increment NNN, combine with sanitized name
- Output: Unique folder name string (e.g., `wf-001-my-great-idea`)
- Edge case: If no `wf-XXX` folders exist, start at `wf-001`

### FR-037-A.7: Submit Handler

**Description:** Package content and submit to backend API.

**Details:**
- Input: Folder name + (markdown content OR uploaded files)
- Process: Call `POST /api/ideas/upload` with folder name and content; on success call Workflow Manager to auto-complete `compose_idea` action with deliverables
- Output: Idea saved, workflow updated, modal closed
- Error: On failure, display error toast, keep modal open

### FR-037-A.8: Workplace JS Refactoring

**Description:** Refactor `setupComposer()` and `setupUploader()` to accept container parameter.

**Details:**
- Input: workplace.js functions with hardcoded `#workplace-*` DOM IDs
- Process: Add optional `containerEl` parameter; if provided, scope all DOM queries to `containerEl.querySelector()` instead of `document.querySelector()`; if not provided, fall back to existing global selectors
- Output: Backward-compatible functions usable in both Workplace page and modal
- Testing: Verify Workplace page still works after refactoring

## Non-Functional Requirements

| NFR ID | Description |
|--------|-------------|
| NFR-037-A.1 | Modal opens within 300ms of action button click |
| NFR-037-A.2 | EasyMDE initializes within 500ms after modal open |
| NFR-037-A.3 | No memory leaks: EasyMDE and event listeners cleaned up on every modal close |
| NFR-037-A.4 | Backward compatibility: Workplace compose/upload must pass existing tests after refactoring |

## UI/UX Requirements

### Component Inventory (from mockup)

| Component | Mockup Element | Notes |
|-----------|---------------|-------|
| Modal overlay | Semi-transparent backdrop | rgba(0,0,0,0.4), no close on click |
| Modal dialog | Centered container, max-width ~720px | Border-radius 10-12px, shadow-lg |
| Header bar | "Compose Idea" title + × close button | Sticky at top |
| Toggle buttons | [Create New] / [Link Existing] pill toggle | Below header, emerald accent for active |
| Name input | Text field with word counter badge | "3 / 10 words" right-aligned |
| Tab bar | ✏️ Compose / 📁 Upload buttons | Active tab has accent underline |
| Compose editor | EasyMDE textarea with toolbar | Toolbar: B, I, H, •, #, 🔗, {}, 👁 |
| Upload zone | Drag-and-drop area with icon + text | File type tags shown below |
| Action footer | [Cancel] secondary + [Submit Idea] primary | Submit disabled until valid |

### User Interaction Flow

1. User clicks "Compose Idea" in workflow → modal opens
2. Default: Create New active, name input focused
3. User types idea name → word counter updates live
4. User writes in Compose tab OR uploads in Upload tab
5. User clicks "Submit Idea" → loading state → success → modal closes → action marked done

### States

| State | Behavior |
|-------|----------|
| Empty | Submit disabled, no validation errors |
| Name entered, no content | Submit disabled |
| Name + content valid | Submit enabled (primary green) |
| Submitting | Submit shows spinner, disabled; Cancel hidden |
| Success | Modal closes, toast "Idea created successfully" |
| Error (name) | Inline red text below name input |
| Error (API) | Toast in modal, retry available |

## Dependencies

### Internal Dependencies

| Feature | Type | Description |
|---------|------|-------------|
| FEATURE-036-C | Required | Stage ribbon provides "Compose Idea" action button that triggers this modal |
| FEATURE-036-A | Required | Workflow Manager API for action auto-complete (`update_workflow_action`) |
| FEATURE-008 | Required | Workplace JS (`setupComposer`, `setupUploader`) and `/api/ideas/upload` endpoint |

### External Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| EasyMDE | Library | Markdown editor (already in app dependencies) |
| marked.js | Library | Markdown rendering for preview (already in app) |

## Business Rules

- **BR-001**: Idea names must be ≤ 10 words. Empty names are not allowed.
- **BR-002**: Folder names follow pattern `wf-{NNN}-{sanitized-name}` where NNN auto-increments.
- **BR-003**: Sanitization: lowercase, spaces → hyphens, strip non-alphanumeric (except hyphens), max 50 chars.
- **BR-004**: A workflow can only have one idea folder linked at a time.
- **BR-005**: Content is not persisted as draft — closing modal without submit loses all content.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| Name with 11+ words | Inline error, submit disabled |
| Name with special characters (e.g., `idea @#$%`) | Sanitized to `idea` |
| No existing `wf-XXX` folders | First folder starts at `wf-001-{name}` |
| Folder name collision (`wf-001-my-idea` already exists) | API returns 409, modal shows error, user renames |
| User closes modal mid-upload | In-flight fetch requests aborted, no partial files |
| Very long idea name (50+ chars after sanitization) | Truncated to 50 chars at word boundary |
| Empty compose content + no uploads | Submit disabled |
| Network failure during submit | Error toast with "Retry" button, modal stays open |
| compose_idea already "done" | Modal opens for re-edit (handled by FEATURE-037-B) |
| Workflow has no idea_folder linked yet | Folder created and linked during submit |

## Out of Scope

- **Link Existing mode** — delivered in FEATURE-037-B
- **Re-edit support** — delivered in FEATURE-037-B
- **Draft persistence / auto-save** — explicitly excluded per requirements
- **UIUX Reference tab** — remains a separate workflow action
- **Usage outside workflow context** — scoped to workflow only for now
- **Keyboard shortcuts in editor** — standard EasyMDE shortcuts apply, no custom additions

## Technical Considerations

- The Workplace JS refactoring (FR-037-A.8) should be done first as it's a prerequisite for both Compose and Upload tabs
- The `wf-NNN` auto-increment needs to parse the `/api/ideas/tree` response to find highest existing prefix
- Modal should use the existing app modal/dialog CSS patterns (z-index 1000+, overlay conventions) for consistency
- The `compose_idea` action auto-complete should call the same Workflow Manager endpoint used by FEATURE-036-C for other actions

## Open Questions

- None — all clarifications resolved during IDEA-023 ideation and EPIC-037 requirement gathering.
