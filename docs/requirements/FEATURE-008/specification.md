# Feature Specification: Workplace (Idea Management)

> Feature ID: FEATURE-008  
> Version: v1.1  
> Status: Complete  
> Last Updated: 01-22-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.1 | 01-22-2026 | CR-001: Added Copilot button for idea refinement |
| v1.0 | 01-22-2026 | Initial specification |
| v1.0 | 01-22-2026 | Implementation complete |

## Overview

The Workplace feature introduces a dedicated space for users to manage their ideas before they become formal requirements. Users can upload idea files (documents, notes, code snippets, images), organize them in folders, edit content with auto-save functionality, and rename folders as ideas evolve. The Workplace appears as the first item in the sidebar navigation, emphasizing its role as the starting point for the ideation workflow.

This feature integrates with a new agent skill (`task-type-ideation`) that analyzes uploaded ideas, brainstorms with users to refine concepts, and produces structured summaries ready for requirement gathering.

## User Stories

- As a **user**, I want to **upload my idea files to a central workspace**, so that **I can keep all related materials organized in one place**.
- As a **user**, I want to **browse my ideas in a tree view**, so that **I can quickly navigate between different idea folders and files**.
- As a **user**, I want to **edit idea files with auto-save**, so that **I don't lose my work and don't have to manually save**.
- As a **user**, I want to **rename idea folders**, so that **I can give meaningful names as my ideas evolve**.
- As a **user**, I want to **see Workplace as the first sidebar item**, so that **I can easily access my idea workspace**.
- As a **user**, I want to **quickly refine my idea with Copilot CLI**, so that **I can get AI assistance without manually typing commands** (CR-001).

## Acceptance Criteria

- [x] AC-1: Workplace appears as the first item in the sidebar navigation (above existing items)
- [x] AC-2: Clicking Workplace shows a two-column layout (left: tree + controls, right: content area)
- [x] AC-3: "Upload Idea" button is visible at the top of the left sidebar
- [x] AC-4: Idea tree displays all folders and files from `docs/ideas/` directory
- [x] AC-5: Clicking a file in the tree opens it in the right content view
- [x] AC-6: File content can be edited in the content view
- [x] AC-7: Changes auto-save after 5 seconds of no input (debounced)
- [x] AC-8: Visual indicator shows "Saving..." during save and "Saved" on completion
- [x] AC-9: Clicking "Upload Idea" shows upload view with drag-and-drop zone
- [x] AC-10: Upload view also supports click-to-select file picker
- [x] AC-11: Uploaded files are stored in `docs/ideas/{Draft Idea - MMDDYYYY HHMMSS}/` (directly in folder)
- [x] AC-12: Folders in the tree can be renamed via inline editing (double-click)
- [x] AC-13: Folder rename updates the physical folder name on disk
- [x] AC-14: Tree view updates automatically when files/folders are added, renamed, or deleted
- [x] AC-15: "Copilot" button appears to the left of the Edit button in content view header (CR-001)
- [x] AC-16: Clicking Copilot button expands the terminal panel (CR-001)
- [x] AC-17: If terminal is in Copilot CLI mode, a new terminal session is created (CR-001)
- [x] AC-18: Copilot button sends `copilot` command with typing simulation (CR-001)
- [x] AC-19: After copilot CLI init, sends `refine the idea {file path}` command (CR-001)

## Functional Requirements

### FR-1: Sidebar Navigation Reorganization

**Description:** Move Workplace to the first position in the sidebar

**Details:**
- Input: Existing sidebar menu items
- Process: Insert "Workplace" as first item, shift others down
- Output: Sidebar with Workplace at top, existing items below

### FR-2: Two-Column Workplace Layout

**Description:** Display Workplace content in a split-pane layout

**Details:**
- Input: User clicks Workplace in sidebar
- Process: Render left panel (tree + controls) and right panel (content area)
- Output: Two-column view with resizable divider (optional)
- Left panel width: ~250-300px (fixed or adjustable)
- Right panel: remaining space

### FR-3: Idea Tree View

**Description:** Display folder/file structure from docs/ideas/

**Details:**
- Input: Directory structure at `docs/ideas/`
- Process: Recursively scan and build tree structure
- Output: Expandable/collapsible tree showing folders and files
- Folder icons distinguish from file icons
- Clicking folder expands/collapses it
- Clicking file loads it in content view

### FR-4: File Editor with Auto-Save

**Description:** Edit idea files with automatic save after inactivity

**Details:**
- Input: File content loaded in content view
- Process: 
  1. User edits content
  2. Start 5-second debounce timer on each keystroke
  3. After 5 seconds of no input, trigger save
  4. Show "Saving..." indicator
  5. Call save API endpoint
  6. Show "Saved" indicator on success
- Output: File saved to disk, visual confirmation

### FR-5: File Upload System

**Description:** Upload files via drag-and-drop or file picker

**Details:**
- Input: User clicks "Upload Idea" button
- Process:
  1. Show upload view in right panel
  2. Accept files via drag-and-drop on drop zone
  3. Accept files via click-to-browse file picker
  4. Create folder: `docs/ideas/temp idea - {YYYY-MM-DD}/files/`
  5. Copy uploaded files to the folder
  6. Refresh tree view
- Output: Files stored in new idea folder, tree updated
- Supported files: Any file type GitHub Copilot can understand (text, md, code, images)

### FR-6: Folder Rename

**Description:** Rename folders via inline editing

**Details:**
- Input: User double-clicks folder name in tree
- Process:
  1. Replace folder name with editable input field
  2. User types new name
  3. On blur or Enter key, rename folder on disk
  4. Update tree view
  5. Handle name conflicts (append number if exists)
- Output: Folder renamed physically and in UI
- Validation: No special characters that are invalid for filesystem

### FR-7: Copilot Refinement Button (CR-001)

**Description:** One-click Copilot CLI integration for idea refinement

**Details:**
- Input: User clicks "Copilot" button in content view header
- Process:
  1. Expand terminal panel via `window.terminalPanel.expand()`
  2. Check if current terminal is in Copilot CLI mode (detect prompt indicators)
  3. If in Copilot mode and space available, create new terminal session
  4. Focus on target terminal
  5. Send `copilot` command with typing simulation (30-80ms per character)
  6. Wait 1.5 seconds for CLI initialization
  7. Send `refine the idea {current file path}` command with typing simulation
- Output: Terminal expanded with Copilot CLI running refine command
- Button: Located left of Edit button, uses Bootstrap `btn-outline-info` styling with robot icon

**Copilot Mode Detection:**
- Check terminal buffer for indicators: `copilot>`, `Copilot`, `⏺`
- If detected, create new terminal to avoid command conflicts

**Typing Simulation:**
- Random delay 30-80ms between characters for realistic typing effect
- Send Enter key after command completes

## Non-Functional Requirements

### NFR-1: Performance

- Tree loading: < 500ms for up to 100 folders/files
- Auto-save response: < 200ms acknowledgment
- File upload: Support files up to 10MB each

### NFR-2: Security

- Path validation: Prevent directory traversal attacks
- Sanitize folder names: Remove dangerous characters
- Validate uploaded file types (optional restriction)

### NFR-3: Usability

- Clear visual feedback for all operations
- Keyboard navigation support in tree view
- Responsive layout for different screen sizes

## UI/UX Requirements

**Layout:**
```
+--------------------------------------------------+
| [Sidebar]                                        |
| [Workplace] <-- First item, highlighted          |
| [Project Plan]                                   |
| [Requirements]                                   |
| [Code Repository]                                |
+--------------------------------------------------+

When Workplace selected:
+------------------+-------------------------------+
| Upload Idea [btn]|                               |
|------------------|     Content/Upload View       |
| 📁 idea-2026-01  |                               |
|   📄 notes.md    |     (Selected file editor     |
|   📄 sketch.png  |      or Upload dropzone)      |
| 📁 idea-2026-02  |                               |
|   📁 files/      |                               |
|     📄 doc.txt   |                               |
+------------------+-------------------------------+
```

**Visual States:**
- Saving indicator: Spinner or "Saving..." text
- Saved indicator: Checkmark or "Saved" text (auto-hide after 2s)
- Upload dropzone: Dashed border, "Drop files here" text
- Inline rename: Input field replaces folder name

## Dependencies

### Internal Dependencies

- **Existing ContentService:** Reuse file read/write operations
- **Existing Tree Component:** Extend Project Navigation tree for ideas

### External Dependencies

- None (uses existing Flask backend)

## Business Rules

### BR-1: Folder Naming Convention

**Rule:** Uploaded ideas create folders with format `temp idea - YYYY-MM-DD`

**Example:** 
- Upload on 2026-01-22 creates `temp idea - 2026-01-22`
- If exists, append counter: `temp idea - 2026-01-22 (2)`

### BR-2: Auto-Save Debounce

**Rule:** Changes trigger save only after 5 seconds of no editing

**Example:**
- User types "Hello" → Timer starts
- User types " World" at second 3 → Timer resets
- No input for 5 seconds → Save triggered

### BR-3: Folder Rename Validation

**Rule:** Folder names must be valid filesystem names

**Validation:**
- No `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` characters
- Max 255 characters
- No leading/trailing spaces

## Edge Cases & Constraints

### Edge Case 1: Empty Ideas Directory

**Scenario:** `docs/ideas/` doesn't exist or is empty  
**Expected Behavior:** Show empty state message, "Upload Idea" button still visible

### Edge Case 2: File Locked During Auto-Save

**Scenario:** File is being accessed by another process  
**Expected Behavior:** Show error toast, retry after 2 seconds, max 3 retries

### Edge Case 3: Large File Upload

**Scenario:** User uploads file > 10MB  
**Expected Behavior:** Show validation error, reject upload

### Edge Case 4: Rename to Existing Folder Name

**Scenario:** User renames folder to a name that already exists  
**Expected Behavior:** Append counter: `new-name (2)`, `new-name (3)`, etc.

### Edge Case 5: Unsaved Changes Before Navigation

**Scenario:** User has pending changes and clicks another file  
**Expected Behavior:** Trigger immediate save before loading new file

## Out of Scope

- Multiple file upload progress tracking (show only success/failure)
- File deletion from UI (use filesystem directly for now)
- Drag-and-drop reordering of files/folders
- Search within ideas
- Version history for idea files
- Sharing ideas between users

## Technical Considerations

- Reuse existing `ContentService.save_content()` for auto-save
- Consider `watchdog` or polling for tree refresh after external changes
- Upload endpoint: `POST /api/ideas/upload` with multipart form data
- Rename endpoint: `POST /api/ideas/rename` with old_path, new_name
- Ideas tree endpoint: `GET /api/ideas/tree`

## Open Questions

- [x] Upload file types: Any file type GitHub Copilot can understand ✅
- [x] Auto-save delay: 5 seconds ✅
- [x] Date format in folder names: ISO format (YYYY-MM-DD) ✅

---

## Change Request References

| CR ID | Date | Description | Impact |
|-------|------|-------------|--------|
| CR-001 | 01-22-2026 | Add Copilot button for idea refinement | Added US-6, AC-15 to AC-19, FR-7 |

---
