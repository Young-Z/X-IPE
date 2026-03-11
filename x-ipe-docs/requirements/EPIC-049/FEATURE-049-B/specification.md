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
**Given** the application loads  
**When** the sidebar renders  
**Then** a "Knowledge Base" section appears with a `bi-book` icon in the sidebar, positioned after "Project Plan" and before "Requirements"

### AC-049-B-02: Folder Tree Rendering
**Given** the KB root has folders and files  
**When** the Knowledge Base section expands  
**Then** the folder tree mirrors the `x-ipe-docs/knowledge-base/` file system, showing folders with `bi-folder` icons and files with `bi-file-earmark-text` icons

### AC-049-B-03: Expand/Collapse Folders
**Given** a folder node in the KB tree  
**When** the user clicks the folder  
**Then** the folder expands to show children (sub-folders and files) with chevron rotation animation; clicking again collapses it

### AC-049-B-04: File Click Navigation
**Given** a file in the KB tree  
**When** the user clicks it  
**Then** the file content opens in the main content area using the existing content rendering pipeline; the file item shows active (highlighted) state

### AC-049-B-05: Tree Auto-Refresh
**Given** a file or folder operation occurs (create, move, delete, upload via other features)  
**When** the operation completes  
**Then** the sidebar KB tree refreshes automatically to reflect the new state within 2 seconds

### AC-049-B-06: Drag-Over Visual Feedback
**Given** a user drags a file or folder over a sidebar KB folder  
**When** the drag enters the folder element  
**Then** an emerald dashed border appears around the folder with a subtle background highlight; the visual clears on drag-leave

### AC-049-B-07: Drop to Move
**Given** a user drops a dragged item onto a KB sidebar folder  
**When** the drop event fires  
**Then** the file/folder is moved to the target folder via the KB move API; the tree refreshes to show the new location

### AC-049-B-08: Intake Placeholder
**Given** the sidebar KB section is expanded  
**When** the tree renders  
**Then** a "📥 Intake" entry appears at the bottom of the KB section (non-functional placeholder for FEATURE-049-F)

### AC-049-B-09: Empty State
**Given** the KB root folder is empty or doesn't exist  
**When** the sidebar KB section expands  
**Then** a subtle "No articles yet" message is shown instead of an empty tree

### AC-049-B-10: Tree Performance
**Given** the KB contains up to 500 files across nested folders  
**When** the tree is loaded  
**Then** the sidebar renders within 500ms (NFR-049.2)

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
