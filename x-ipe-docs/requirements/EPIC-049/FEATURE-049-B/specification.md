# Feature Specification: KB Sidebar & Navigation

> Feature ID: FEATURE-049-B  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-11-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-11-2026 | Initial specification — template conformance with GWT criteria, test type legend, linked mockups |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| KB Browse Articles | HTML | [../../mockups/kb-interface-v1.html](../../mockups/kb-interface-v1.html) | Scene 1 — Browse Articles grid view with sidebar tree | current | 03-11-2026 |
| KB Article Detail | HTML | [../../mockups/kb-interface-v1.html](../../mockups/kb-interface-v1.html) | Scene 2 — Article Detail view with sidebar navigation | current | 03-11-2026 |
| Reference Picker Modal | HTML | [../../mockups/kb-interface-v1.html](../../mockups/kb-interface-v1.html) | Scene 3 — Reference Picker Modal | current | 03-11-2026 |
| AI Librarian Intake | HTML | [../../mockups/kb-interface-v1.html](../../mockups/kb-interface-v1.html) | Scene 4 — AI Librarian Intake | current | 03-11-2026 |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

FEATURE-049-B delivers the Knowledge Base sidebar section and interactive folder tree navigation within the X-IPE interface. It provides developers with a dedicated sidebar area to browse, navigate, and manage KB articles without leaving their current workflow.

The sidebar renders a hierarchical folder tree that mirrors the KB file system structure, supporting expand/collapse navigation, file click to open content, and drag-and-drop to move files between folders. Visual feedback via emerald dashed borders and background highlights guides the drag-drop experience.

This feature depends on FEATURE-049-A (KB Backend & Storage Foundation) for the tree API and file move endpoints. It uses vanilla JavaScript with Bootstrap 5 components, following existing X-IPE sidebar patterns. The sidebar auto-refreshes after write operations via a custom `kb:changed` event.

## User Stories

As a developer using X-IPE, I want a Knowledge Base section in the sidebar with an interactive folder tree so that I can browse, navigate, and manage KB articles without leaving my current workflow.

## Acceptance Criteria

### AC-049-B-01: Sidebar Section Presence

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-01a | GIVEN user opens X-IPE sidebar WHEN KB section renders THEN "Knowledge Base" section appears with `bi-book` icon | UI |
| AC-049-B-01b | GIVEN X-IPE sidebar is rendered WHEN section order is inspected THEN KB section is positioned after "Project Plan" AND before "Requirements" | UI |

### AC-049-B-02: Folder Tree Rendering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-02a | GIVEN KB root contains folders and files WHEN sidebar tree loads via GET /api/kb/tree THEN folder tree mirrors `x-ipe-docs/knowledge-base/` file system structure | Integration |
| AC-049-B-02b | GIVEN folder tree is rendered WHEN a folder node is inspected THEN it displays with `bi-folder` icon | UI |
| AC-049-B-02c | GIVEN folder tree is rendered WHEN a file node is inspected THEN it displays with `bi-file-earmark-text` icon | UI |

### AC-049-B-03: Expand/Collapse Folders

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-03a | GIVEN a collapsed folder exists in the tree WHEN user clicks the folder node THEN it expands to show children (sub-folders and files) | UI |
| AC-049-B-03b | GIVEN a folder is currently expanded WHEN user clicks the folder node THEN it collapses to hide children | UI |
| AC-049-B-03c | GIVEN a folder node is clicked WHEN expand or collapse occurs THEN chevron rotation animation plays | UI |

### AC-049-B-04: File Click Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-04a | GIVEN a file exists in the sidebar tree WHEN user clicks the file THEN its content opens in the main content area via existing rendering pipeline | UI |
| AC-049-B-04b | GIVEN user clicks a file in the tree WHEN the file opens THEN the file item shows active (highlighted) state in the tree | UI |

### AC-049-B-05: Tree Auto-Refresh

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-05a | GIVEN a KB write operation (create/move/delete/upload) completes WHEN kb:changed event is dispatched THEN sidebar KB tree refreshes automatically | Integration |
| AC-049-B-05b | GIVEN a KB write operation completes WHEN tree refresh is triggered THEN refresh completes within 2 seconds of operation completion | UI |

### AC-049-B-06: Drag-Over Visual Feedback

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-06a | GIVEN user is dragging a KB item WHEN the item is dragged over a folder THEN emerald dashed border appears around the folder | UI |
| AC-049-B-06b | GIVEN user is dragging a KB item WHEN the item is dragged over a folder THEN subtle background highlight is shown | UI |
| AC-049-B-06c | GIVEN a folder has drag-over visual feedback WHEN the dragged item leaves the folder THEN visual feedback clears | UI |

### AC-049-B-07: Drop to Move

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-07a | GIVEN user is dragging a KB item over a valid folder WHEN the item is dropped THEN KB move API is called (`PUT /api/kb/files/move` or `/api/kb/folders/move`) | Integration |
| AC-049-B-07b | GIVEN a drop-to-move operation succeeds WHEN move API returns 200 THEN tree refreshes to show item in new location | UI |

### AC-049-B-08: Intake Placeholder

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-08a | GIVEN KB sidebar section is rendered WHEN the section content is inspected THEN "📥 Intake" entry appears at the bottom | UI |
| AC-049-B-08b | GIVEN "📥 Intake" entry is displayed WHEN user clicks the entry THEN no action occurs (placeholder for FEATURE-049-F) | UI |

### AC-049-B-09: Empty State

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-09a | GIVEN KB root directory exists but contains no files WHEN sidebar tree loads THEN "No articles yet" message is shown | UI |
| AC-049-B-09b | GIVEN KB root directory does not exist WHEN sidebar tree loads THEN "No articles yet" message is shown | UI |

### AC-049-B-10: Tree Performance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-B-10a | GIVEN KB contains up to 500 files WHEN sidebar tree renders THEN rendering completes within 500ms | UI |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB)

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-049-B-01 | KB sidebar section added to `DEFAULT_SECTIONS` in `file_service.py` with `id: 'knowledge-base'`, `label: 'Knowledge Base'`, `path: 'x-ipe-docs/knowledge-base'`, `icon: 'bi-book'` |
| FR-049-B-02 | Custom rendering logic in `sidebar.js` for KB section: fetches tree from `GET /api/kb/tree` instead of using the generic file scanner |
| FR-049-B-03 | Folder expand/collapse uses Bootstrap Collapse with chevron rotation matching existing sidebar pattern |
| FR-049-B-04 | File click dispatches to content renderer via `window.contentRenderer` or navigation event |
| FR-049-B-05 | Tree auto-refresh on custom event `kb:changed` dispatched after any KB write operation |
| FR-049-B-06 | Drag-drop on KB sidebar folders uses `dragover`/`dragleave`/`drop` HTML5 events with visual feedback CSS classes |
| FR-049-B-07 | Drop handler calls `PUT /api/kb/files/move` or `PUT /api/kb/folders/move` depending on dragged item type |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-049-B-01 | Tree load ≤ 500ms for 500 files |
| NFR-049-B-02 | Follow existing sidebar CSS patterns (`.nav-section-header`, `.nav-item`, `.nav-folder`, etc.) |
| NFR-049-B-03 | Drag-drop feedback must be accessible (not color-only — use border + background) |
| NFR-049-B-04 | No new external dependencies — vanilla JS + Bootstrap 5 only |
| NFR-049-B-05 | KB section must coexist with existing sidebar sections without layout issues |

## UI/UX Requirements

- **UX-049-B-01:** KB sidebar section follows existing `.nav-section-header`, `.nav-item`, `.nav-folder` CSS patterns
- **UX-049-B-02:** Folder tree uses Bootstrap 5 Collapse component with chevron rotation animation matching existing sidebar behavior
- **UX-049-B-03:** Drag-over feedback uses emerald dashed border (`2px dashed var(--bs-success)`) plus subtle background highlight (`rgba(25, 135, 84, 0.08)`)
- **UX-049-B-04:** Active file item uses standard `.active` class with sidebar highlight color
- **UX-049-B-05:** Invalid drop target (folder into itself) shows CSS shake animation for 300ms
- **UX-049-B-06:** Tree indentation uses 16px per level for nested folders
- **UX-049-B-07:** Empty state message ("No articles yet") centered in KB section area with muted text

## Dependencies

### Internal
- FEATURE-049-A (KB Backend & Storage Foundation) — provides `GET /api/kb/tree`, `PUT /api/kb/files/move`, `PUT /api/kb/folders/move`

### External
- Bootstrap 5 (already in project) — Collapse component, icon classes
- Bootstrap Icons (already in project) — `bi-book`, `bi-folder`, `bi-file-earmark-text`

## Business Rules

1. KB section uses `/api/kb/tree` (from FEATURE-049-A) — NOT the generic file scanner
2. File click opens file in the standard content area (same as other sidebar files)
3. Drag-drop is KB-internal only in V1 (no cross-section drag)
4. Intake placeholder is non-functional until FEATURE-049-F
5. Section position: after Project Plan, before Requirements

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| KB root doesn't exist yet | Show "No articles yet" message; section still renders |
| Deeply nested folders (>5 levels) | Tree renders all levels with increasing indent; may need scroll |
| Dragging non-KB item onto KB folder | Ignore (KB drag-drop only activates for items with KB paths) |
| Dropping folder into itself or child | Show shake animation + error feedback; no API call |
| API error on tree fetch | Show error state in section; retry on next polling cycle |
| Concurrent sidebar refresh | Debounce tree refresh to max once per second |

## Out of Scope

- Cross-section drag-and-drop (dragging files from other sidebar sections into KB)
- Non-KB file management (sidebar only manages knowledge-base files)
- Inline file renaming in the sidebar tree (V2)
- Multi-select drag-and-drop (single item only in V1)
- Custom folder icons or color-coding
- Sidebar search/filter within the tree (search is in FEATURE-049-D)

## Technical Considerations

- Vanilla JavaScript only — no external frameworks or libraries beyond Bootstrap 5
- Event-driven refresh via custom `kb:changed` DOM event dispatched after write operations
- Folder tree built from `GET /api/kb/tree` JSON response — recursive DOM rendering
- Drag-and-drop uses HTML5 `dragover`/`dragleave`/`drop` events with CSS class toggling
- Debounce tree refresh to max once per second to avoid rapid re-renders
- Follow existing X-IPE sidebar patterns in `src/x_ipe/static/js/sidebar.js`

## Open Questions

- None — all questions resolved during refinement
