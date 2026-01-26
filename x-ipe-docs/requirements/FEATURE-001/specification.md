# Feature Specification: Project Navigation

> Feature ID: FEATURE-001  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-18-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 01-18-2026 | Initial specification | - |

## Overview

The Project Navigation feature provides a dynamic sidebar that displays the folder structure of an AI agent-created project. Users can browse through the project hierarchy using an expandable/collapsible tree view, with three predefined top-level sections mapping to standard project folders: Project Plan, Requirements/Technical Design, and Code Repository.

This is the MVP (Minimum Viable Product) feature that establishes the core application structure and enables users to discover and select files for viewing. Without navigation, users cannot access any project content, making this the foundational feature for the entire application.

The sidebar will automatically detect changes to the project structure (new files, renamed folders, deletions) and update the tree view without requiring a page refresh, providing a seamless experience as AI agents modify project files.

## User Stories

- As a **human reviewer**, I want to **see the project folder structure in a sidebar**, so that **I can quickly understand what documentation and code exists**.

- As a **human reviewer**, I want to **expand and collapse folders**, so that **I can focus on specific sections without visual clutter**.

- As a **human reviewer**, I want to **click on a file to view its contents**, so that **I can read documentation and code**.

- As a **human reviewer**, I want to **see new files appear automatically**, so that **I don't miss updates made by AI agents**.

- As a **project manager**, I want to **configure which project folder to view**, so that **I can switch between different AI projects**.

## Acceptance Criteria

- [ ] AC-1: Left sidebar displays project folder structure as a tree view
- [ ] AC-2: Three top-level menu sections exist: "Project Plan", "Requirements", "Code"
- [ ] AC-3: "Project Plan" section maps to `x-ipe-docs/planning/` folder
- [ ] AC-4: "Requirements" section maps to `x-ipe-docs/requirements/` folder
- [ ] AC-5: "Code" section maps to `src/` folder
- [ ] AC-6: Folders can be expanded/collapsed by clicking
- [ ] AC-7: Clicking a file triggers content loading (emits event/callback)
- [ ] AC-8: File system changes are detected within 2 seconds
- [ ] AC-9: Tree view updates automatically when files are added/removed
- [ ] AC-10: UI placeholder exists for project root path switching
- [ ] AC-11: Sidebar is responsive and works on tablet+ screen sizes

## Functional Requirements

### FR-1: Project Structure Scanning

**Description:** Backend API to scan and return project folder structure

**Details:**
- Input: Project root path (from configuration)
- Process: Recursively scan configured directories (x-ipe-docs/planning, x-ipe-docs/requirements, src)
- Output: JSON tree structure with files and folders

**API Endpoint:** `GET /api/project/structure`

**Response Format:**
```json
{
  "sections": [
    {
      "id": "planning",
      "label": "Project Plan",
      "path": "x-ipe-docs/planning",
      "children": [
        {"name": "task-board.md", "type": "file", "path": "x-ipe-docs/planning/task-board.md"},
        {"name": "features.md", "type": "file", "path": "x-ipe-docs/planning/features.md"}
      ]
    }
  ]
}
```

### FR-2: Folder Tree Rendering

**Description:** Frontend component to render folder tree in sidebar

**Details:**
- Input: JSON tree structure from API
- Process: Render Bootstrap accordion/tree with expand/collapse
- Output: Interactive sidebar navigation

**UI Behavior:**
- Folders show expand/collapse icons
- Files show appropriate file type icons
- Current selection is highlighted
- Smooth expand/collapse animations

### FR-3: File Selection Handler

**Description:** Handle user clicks on files to trigger content loading

**Details:**
- Input: User click on file item
- Process: Emit file selection event with file path
- Output: Event dispatched to content viewer component

### FR-4: File System Change Detection

**Description:** Detect when project files are modified on disk

**Details:**
- Input: File system events (create, modify, delete)
- Process: Backend monitors file system, pushes updates via WebSocket
- Output: Frontend receives update, refreshes tree

**WebSocket Event:**
```json
{
  "type": "structure_changed",
  "action": "created|modified|deleted",
  "path": "x-ipe-docs/planning/new-file.md"
}
```

### FR-5: Project Root Configuration

**Description:** Allow configuration of which project folder to monitor

**Details:**
- Input: Project root path (string)
- Process: Validate path exists, update configuration
- Output: Sidebar refreshes with new project structure

## Non-Functional Requirements

### NFR-1: Performance

- Tree structure API response: < 200ms for projects with up to 500 files
- File system change detection latency: < 2 seconds
- Expand/collapse animation: 60fps smooth

### NFR-2: Usability

- Sidebar width: Resizable, default 250px, min 200px, max 400px
- Touch-friendly: Tap targets minimum 44px height
- Keyboard navigation: Arrow keys for tree traversal

### NFR-3: Scalability

- Support projects with up to 1000 files
- Lazy loading for deeply nested folders (> 3 levels)

## UI/UX Requirements

### Layout

```
+------------------+------------------------+
|                  |                        |
|     Sidebar      |     Content Area       |
|     (250px)      |     (flexible)         |
|                  |                        |
|  - Project Plan  |                        |
|    - task-board  |                        |
|    - features    |                        |
|                  |                        |
|  - Requirements  |                        |
|    > FEATURE-001 |                        |
|    > FEATURE-002 |                        |
|                  |                        |
|  - Code          |                        |
|    > src/        |                        |
|                  |                        |
+------------------+------------------------+
```

### UI Elements

| Element | Description |
|---------|-------------|
| Sidebar Container | Fixed left panel, scrollable, dark/light theme |
| Section Header | Clickable accordion header with icon and label |
| Folder Item | Expandable, shows folder icon, indented |
| File Item | Clickable, shows file type icon, indented |
| Selection State | Highlighted background for selected file |
| Project Switcher | Dropdown/input at top of sidebar (placeholder) |

### Icons

- 📁 Folder (collapsed)
- 📂 Folder (expanded)
- 📄 Generic file
- 📝 Markdown file (.md)
- 🐍 Python file (.py)
- 📜 JavaScript file (.js)

## Dependencies

### Internal Dependencies

- None (this is the MVP feature)

### External Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| Flask | Backend web framework | 3.x |
| watchdog | File system monitoring | Latest |
| Bootstrap 5 | Frontend UI framework | 5.3.x |
| Flask-SocketIO | WebSocket support | Latest |

## Business Rules

### BR-1: Section Mapping

**Rule:** Top-level sections always map to these paths:
- "Project Plan" → `x-ipe-docs/planning/`
- "Requirements" → `x-ipe-docs/requirements/`
- "Code" → `src/`

If a mapped folder doesn't exist, show section as empty (not hidden).

### BR-2: File Filtering

**Rule:** Only show supported file types:
- Documents: .md, .txt, .json, .yaml, .yml
- Code: .py, .js, .ts, .html, .css, .jsx, .tsx

Hidden files (starting with `.`) are excluded by default.

### BR-3: Path Security

**Rule:** Only allow access to files within the configured project root.
Path traversal attempts (../) must be rejected.

## Edge Cases & Constraints

### Edge Case 1: Empty Project

**Scenario:** Project folder exists but has no files in monitored directories
**Expected Behavior:** Show section headers with "No files" message under each

### Edge Case 2: Missing Folder

**Scenario:** One of the mapped folders (e.g., `src/`) doesn't exist
**Expected Behavior:** Show section with "Folder not found" indicator

### Edge Case 3: Large Project

**Scenario:** Project has hundreds of files
**Expected Behavior:** 
- Use lazy loading for subdirectories
- Show loading indicator during tree expansion
- Collapse all sections by default

### Edge Case 4: Rapid File Changes

**Scenario:** AI agent creates many files quickly
**Expected Behavior:** 
- Debounce file system events (100ms)
- Batch updates to prevent UI flickering

### Edge Case 5: Invalid Project Path

**Scenario:** Configured project root doesn't exist
**Expected Behavior:** Show error message with path validation

## Out of Scope

- Full-text search across project files (future feature)
- File drag-and-drop reorganization
- Multiple projects open simultaneously
- File creation/deletion from sidebar (edit mode only)
- Custom section configuration (fixed to 3 sections for v1.0)

## Technical Considerations

- Use Flask-SocketIO for real-time file system updates
- Consider `watchdog` library for cross-platform file monitoring
- Store project root path in configuration (environment variable or config file)
- Frontend tree component: Bootstrap 5 accordion with custom nested styling
- Consider virtual scrolling for very large projects

## Open Questions

- [x] ~~Should hidden files be shown?~~ → No, excluded by default
- [x] ~~Should section order be configurable?~~ → No, fixed order for v1.0
- [ ] Should we support custom sections beyond the 3 default ones? → Deferred to v2.0

---
