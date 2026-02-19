# Requirement Details — Part 10

> Epics covered: EPIC-037

---

## EPIC-037: Compose Idea Modal

### Project Overview

Replace the brief "prompt to create/select idea folder → opens existing modal UI" behavior (FR-036.12, FR-036.15) with a fully-featured Compose Idea Modal dialog that supports creating new ideas or linking existing ideas — all within the workflow view without navigation.

### User Request

From IDEA-023 (CR-Compose Idea in Workflow): The current Compose Idea workflow action uses a basic prompt and navigates away to Workplace, causing context loss. Users need a rich modal that stays in the workflow view with compose, upload, and link-existing capabilities.

### Clarifications

| Question | Answer |
|----------|--------|
| Re-edit support? | Yes — modal can re-open with existing content for editing (both new and linked ideas) |
| Link sources? | Only from the ideas folder tree (no external URLs) |
| Draft persistence on close? | No — content is lost on close, user must re-enter |
| Reusable outside workflow? | Scoped to workflow only for now (may expand later) |
| Link granularity? | Any file in the idea folder (.md, .pdf, .png, .txt, etc.) |
| UIUX Reference tab? | Not included — UIUX reference is a separate workflow action |

### High-Level Requirements

1. **Modal Dialog** — Full-featured modal opens when clicking "Compose Idea" in workflow stage view; overlays the workflow without navigating away
2. **Toggle Mode Selection** — Top bar with [Create New] / [Link Existing] toggle; default is "Create New"
3. **Create New Mode** — Name input (max 10 words) + tabbed Compose (Markdown editor) / Upload (drag-and-drop) interface reusing Workplace JS components
4. **Link Existing Mode** — Mini file tree (from `/api/ideas/tree`) with client-side search + read-only preview panel (markdown rendered via marked.js / EasyMDE preview)
5. **Auto Folder Naming** — New ideas auto-generate `wf-{NNN}-{sanitized-name}` folders; NNN auto-increments from highest existing `wf-XXX` in ideas directory
6. **Dual Deliverables** — Submit produces both: idea file path + idea folder name; stored in workflow JSON
7. **Auto-Complete Action** — After submit/link, `compose_idea` action auto-marks as "done" with deliverables
8. **Re-Edit Support** — Modal can re-open with previously composed/linked content for editing
9. **Error Handling** — Folder collision → error toast (modal stays open); API failure → warning with retry; modal close mid-upload → cancel requests; empty/invalid name → inline validation

### Functional Requirements

| FR ID | Description | Priority |
|-------|-------------|----------|
| FR-037.1 | **Modal Container** — Centered overlay modal (max-width ~720px) with header, content area, and action footer. Close via × button, Escape key, or Cancel button. Overlay click does NOT close (prevent accidental loss) | P0 |
| FR-037.2 | **Toggle Mode** — Pill-style toggle buttons [Create New] / [Link Existing] in modal header area. Switches entire content area. Preserves name input across toggles | P0 |
| FR-037.3 | **Idea Name Input** — Required text input with max 10-word validation. Live word counter. Sanitization rules: lowercase, replace spaces with hyphens, remove special chars, max 50 chars | P0 |
| FR-037.4 | **Compose Tab** — Markdown editor (EasyMDE) with toolbar (Bold, Italic, Heading, Lists, Link, Code, Preview). Reuses `setupComposer()` from workplace.js (refactored to accept container parameter) | P0 |
| FR-037.5 | **Upload Tab** — Drag-and-drop file upload zone. Accepted formats: md, txt, pdf, png, jpg, py, js, docx. Reuses `setupUploader()` from workplace.js (refactored to accept container parameter) | P0 |
| FR-037.6 | **File Tree Browser** — Left panel in Link Existing mode. Fetches from `/api/ideas/tree`. Expandable folder/file hierarchy. Click to select a file | P0 |
| FR-037.7 | **Tree Search/Filter** — Text input above file tree. Client-side filtering on folder and file names. Instant filter as user types | P1 |
| FR-037.8 | **Preview Panel** — Right panel in Link Existing mode. Renders selected file content (markdown via marked.js, images inline, other formats show metadata). Read-only | P0 |
| FR-037.9 | **Auto Folder Naming** — On submit (Create New): generate folder name `wf-{NNN}-{sanitized-name}`. NNN = highest existing `wf-XXX` folder + 1, zero-padded to 3 digits. Call `POST /api/ideas/upload` with generated folder name | P0 |
| FR-037.10 | **Link Submit** — On confirm (Link Existing): record selected file path and its root idea folder name. Call existing link-idea API. No new folder creation | P0 |
| FR-037.11 | **Auto-Complete** — After successful submit/link, update `compose_idea` action status to "done" via Workflow Manager with deliverables (file path + folder name) | P0 |
| FR-037.12 | **Re-Edit** — If `compose_idea` is already "done", re-opening modal loads existing content. For new ideas: load from saved file. For linked ideas: show current linked file in preview mode with option to re-link | P1 |
| FR-037.13 | **Error Handling** — Folder name collision: show inline error, suggest alternative. API failure: toast with retry. Upload cancellation: clean up temp files. Empty name: prevent submit with inline validation | P0 |
| FR-037.14 | **EasyMDE Cleanup** — Properly destroy EasyMDE instances on modal close to prevent memory leaks | P0 |
| FR-037.15 | **Workplace JS Refactoring** — Refactor `setupComposer()` and `setupUploader()` in workplace.js to accept a container element parameter (currently hardcoded to `#workplace-*` DOM IDs) | P0 |

### Non-Functional Requirements

| NFR ID | Description |
|--------|-------------|
| NFR-037.1 | Modal must open within 300ms of click |
| NFR-037.2 | File tree must load within 1s for up to 500 idea folders |
| NFR-037.3 | Preview must render within 500ms for files up to 100KB |
| NFR-037.4 | No navigation away from workflow view during entire flow |

### Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-037.1 | Workflow at Ideation stage, compose_idea pending | User clicks "Compose Idea" | Modal opens with "Create New" toggle active, name input focused |
| AC-037.2 | Modal open in Create New mode | User enters name + content in Compose tab + clicks Submit | Folder `wf-NNN-{name}` created, file saved, compose_idea marked done, modal closes |
| AC-037.3 | Modal open in Link Existing mode | User browses file tree, selects a file | Preview panel shows file content; Confirm Link button enables |
| AC-037.4 | File selected in Link Existing mode | User clicks Confirm Link | compose_idea marked done with file path + folder deliverables, modal closes |
| AC-037.5 | compose_idea already done | User clicks "Compose Idea" again | Modal re-opens with existing content (editable for new, preview for linked) |
| AC-037.6 | Modal open with content entered | User clicks × or Cancel | Modal closes, content is lost (no draft persistence) |
| AC-037.7 | Modal open, name field empty | User clicks Submit | Inline validation error, submit prevented |
| AC-037.8 | Folder name collision on submit | API returns error | Error toast in modal, modal stays open, user can rename |

### Constraints

- Must reuse existing APIs: `/api/ideas/tree`, `/api/ideas/download`, `/api/ideas/upload`, link-idea endpoint
- Must reuse Workplace compose/upload JS (requires refactoring for container parameterization)
- Scoped to workflow context only (not available from Workplace tab)
- No draft persistence — content lost on modal close
- `wf-NNN` folders coexist with existing numbered folders in ideas directory

### Dependencies

- **FEATURE-036-A** (Workflow Manager) — for action status updates and gating
- **FEATURE-036-B** (Workflow View Shell) — modal rendered within workflow view
- **FEATURE-036-C** (Stage Ribbon & Action Execution) — CR impact on FR-036.12, FR-036.15
- **FEATURE-008** (Workplace) — reuse compose/upload JS, `/api/ideas/*` endpoints

### Related Features (Conflict Review)

| Existing Feature | Overlap Type | Decision |
|-----------------|--------------|----------|
| FEATURE-036-C (FR-036.12, FR-036.15, AC-036.3) | Functional — "opens existing modal UI" is now fully specified by EPIC-037 | CR on FEATURE-036-C — impact markers added |
| FEATURE-008 (Workplace) | Dependency — reuses API endpoints and JS components | Dependency (no CR needed) |

### Open Questions

- None — all clarifications resolved during ideation (IDEA-023) and requirement gathering

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| Compose Idea Modal (Create New + Link Existing) | [compose-idea-modal-v1.html](EPIC-037/mockups/compose-idea-modal-v1.html) |

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-037-A | EPIC-037 | Compose Idea Modal — Create New | v1.0 | MVP modal with Create New mode: name input, Compose/Upload tabs (refactored from Workplace JS), auto folder naming (wf-NNN), submit with auto-complete workflow action, error handling, EasyMDE cleanup | FEATURE-036-C |
| FEATURE-037-B | EPIC-037 | Compose Idea Modal — Link Existing & Re-Edit | v1.0 | Link Existing mode: file tree browser from /api/ideas/tree, client-side search/filter, preview panel (markdown + images), link submit. Re-edit support for both modes (re-open modal with existing content) | FEATURE-037-A |

---

## Feature Details

### FEATURE-037-A: Compose Idea Modal — Create New

**Version:** v1.0
**Brief Description:** Core modal dialog with Create New mode — the minimum runnable feature that replaces the current basic prompt with a full compose experience inside the workflow view.

**Functional Requirements Covered:**
- FR-037.1 (Modal Container)
- FR-037.2 (Toggle Mode — UI shell only, Link Existing content delivered in FEATURE-037-B)
- FR-037.3 (Idea Name Input)
- FR-037.4 (Compose Tab)
- FR-037.5 (Upload Tab)
- FR-037.9 (Auto Folder Naming)
- FR-037.11 (Auto-Complete Action)
- FR-037.13 (Error Handling)
- FR-037.14 (EasyMDE Cleanup)
- FR-037.15 (Workplace JS Refactoring)

**Acceptance Criteria:**
- [ ] Modal opens when clicking "Compose Idea" in workflow Ideation stage
- [ ] Toggle UI shows [Create New] / [Link Existing] buttons (Link Existing shows placeholder until FEATURE-037-B)
- [ ] Name input validates max 10 words with live word counter
- [ ] Compose tab provides Markdown editor (EasyMDE) with toolbar
- [ ] Upload tab provides drag-and-drop file upload zone
- [ ] Submit creates `wf-NNN-{sanitized-name}` folder via `/api/ideas/upload`
- [ ] After submit, `compose_idea` action auto-completes with deliverables
- [ ] Modal closes on successful submit
- [ ] Folder name collision shows inline error, modal stays open
- [ ] Empty/invalid name prevents submit with inline validation
- [ ] EasyMDE destroyed on modal close (no memory leaks)
- [ ] Cancel / × / Escape closes modal without saving
- [ ] `setupComposer()` and `setupUploader()` refactored to accept container parameter

**Dependencies:**
- FEATURE-036-C (Stage Ribbon provides action button that opens this modal)

**Technical Considerations:**
- Workplace JS refactoring (FR-037.15) is prerequisite work within this feature — refactor `setupComposer()` / `setupUploader()` to accept container element before building modal
- Modal overlay click does NOT close (prevent accidental content loss)
- `wf-NNN` auto-increment: scan `/api/ideas/tree` response for highest `wf-XXX` folder

**Linked Mockup:** [compose-idea-modal-v1.html](EPIC-037/mockups/compose-idea-modal-v1.html) — "Create New" mode

---

### FEATURE-037-B: Compose Idea Modal — Link Existing & Re-Edit

**Version:** v1.0
**Brief Description:** Extends the modal with Link Existing mode (file tree browser + preview) and re-edit support for both modes.

**Functional Requirements Covered:**
- FR-037.6 (File Tree Browser)
- FR-037.7 (Tree Search/Filter)
- FR-037.8 (Preview Panel)
- FR-037.10 (Link Submit)
- FR-037.12 (Re-Edit)

**Acceptance Criteria:**
- [ ] Toggle to "Link Existing" shows file tree sidebar + preview panel
- [ ] File tree fetches from `/api/ideas/tree` with expandable folder/file hierarchy
- [ ] Search input filters tree items client-side as user types
- [ ] Clicking a file shows content in preview panel (markdown rendered, images inline)
- [ ] "Confirm Link" button enabled only when a file is selected
- [ ] Link submit records file path + root folder as deliverables, auto-completes action
- [ ] Re-opening modal after compose_idea is "done" loads existing content for editing
- [ ] Re-edit for linked ideas shows current linked file in preview with option to re-link

**Dependencies:**
- FEATURE-037-A (modal container, toggle UI, auto-complete mechanism)

**Technical Considerations:**
- File tree reuses same data source as Workplace sidebar (`/api/ideas/tree`)
- Preview uses `marked.js` for markdown rendering (already in app dependencies)
- Re-edit loads content from the file path stored in workflow JSON deliverables
- Any file type selectable (.md, .pdf, .png, .txt, etc.) — non-markdown shows file metadata

**Linked Mockup:** [compose-idea-modal-v1.html](EPIC-037/mockups/compose-idea-modal-v1.html) — "Link Existing" mode
