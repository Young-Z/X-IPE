# FEATURE-049-B: KB Sidebar & Navigation — Specification

## Feature Overview

| Field | Value |
|-------|-------|
| Feature ID | FEATURE-049-B |
| Epic | EPIC-049 (Knowledge Base) |
| Version | v1.0 |
| Status | Refined |
| Dependencies | FEATURE-049-A (KB Backend & Storage Foundation) |

## User Story

As a developer using X-IPE, I want a Knowledge Base section in the sidebar with an interactive folder tree so that I can browse, navigate, and manage KB articles without leaving my current workflow.

## Acceptance Criteria

### AC-049-B-01: Sidebar Section Presence

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-01a | "Knowledge Base" section appears in sidebar with `bi-book` icon | UI |
| AC-049-B-01b | KB section positioned after "Project Plan" and before "Requirements" | UI |

### AC-049-B-02: Folder Tree Rendering

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-02a | Folder tree mirrors `x-ipe-docs/knowledge-base/` file system structure | Integration |
| AC-049-B-02b | Folders display with `bi-folder` icons | UI |
| AC-049-B-02c | Files display with `bi-file-earmark-text` icons | UI |

### AC-049-B-03: Expand/Collapse Folders

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-03a | Clicking a folder node expands it to show children (sub-folders and files) | UI |
| AC-049-B-03b | Clicking an expanded folder collapses it | UI |
| AC-049-B-03c | Chevron rotation animation plays on expand/collapse | UI |

### AC-049-B-04: File Click Navigation

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-04a | Clicking a file opens its content in the main content area via existing rendering pipeline | UI |
| AC-049-B-04b | Clicked file item shows active (highlighted) state in the tree | UI |

### AC-049-B-05: Tree Auto-Refresh

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-05a | Sidebar KB tree refreshes automatically after create/move/delete/upload operations | Integration |
| AC-049-B-05b | Tree refresh completes within 2 seconds of operation completion | UI |

### AC-049-B-06: Drag-Over Visual Feedback

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-06a | Emerald dashed border appears around folder on drag-over | UI |
| AC-049-B-06b | Subtle background highlight shown on drag-over | UI |
| AC-049-B-06c | Visual feedback clears on drag-leave | UI |

### AC-049-B-07: Drop to Move

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-07a | Dropping item onto a folder calls KB move API (`PUT /api/kb/files/move` or `/api/kb/folders/move`) | Integration |
| AC-049-B-07b | Tree refreshes to show new location after successful move | UI |

### AC-049-B-08: Intake Placeholder

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-08a | "📥 Intake" entry appears at the bottom of the KB section | UI |
| AC-049-B-08b | Intake entry is non-functional (placeholder for FEATURE-049-F) | UI |

### AC-049-B-09: Empty State

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-09a | "No articles yet" message shown when KB root is empty | UI |
| AC-049-B-09b | "No articles yet" message shown when KB root does not exist | UI |

### AC-049-B-10: Tree Performance

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-B-10a | Sidebar tree renders within 500ms for up to 500 files (NFR-049.2) | UI |

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

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| KB root doesn't exist yet | Show "No articles yet" message; section still renders |
| Deeply nested folders (>5 levels) | Tree renders all levels with increasing indent; may need scroll |
| Dragging non-KB item onto KB folder | Ignore (KB drag-drop only activates for items with KB paths) |
| Dropping folder into itself or child | Show shake animation + error feedback; no API call |
| API error on tree fetch | Show error state in section; retry on next polling cycle |
| Concurrent sidebar refresh | Debounce tree refresh to max once per second |

## Business Rules

1. KB section uses `/api/kb/tree` (from FEATURE-049-A) — NOT the generic file scanner
2. File click opens file in the standard content area (same as other sidebar files)
3. Drag-drop is KB-internal only in V1 (no cross-section drag)
4. Intake placeholder is non-functional until FEATURE-049-F
5. Section position: after Project Plan, before Requirements
