# Feature Specification: Workplace (Idea Management)

> Feature ID: FEATURE-008  
> Version: v1.5  
> Status: Refined  
> Last Updated: 01-28-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.5 | 2026-01-28 | CR-005: Copy URL button for file access | [CR-005](./CR-005.md) |
| v1.4 | 2026-01-28 | CR-004: Rename to Ideation, sidebar submenu, Copilot hover menu | [CR-004](./CR-004.md) |
| v1.3 | 2026-01-23 | CR-003: Add Ideation Toolbox for skill configuration | [CR-003](./CR-003.md) |
| v1.2 | 2026-01-23 | CR-002: Add drag-drop file upload to existing folders | [CR-002](./CR-002.md) |
| v1.1 | 2026-01-22 | CR-001: Added Copilot button for idea refinement | [CR-001](./CR-001.md) |
| v1.0 | 2026-01-22 | Initial specification | - |

## Overview

The Ideation feature (formerly Workplace) introduces a dedicated space for users to manage their ideas before they become formal requirements. Users can upload idea files (documents, notes, code snippets, images), organize them in folders, edit content with auto-save functionality, and rename folders as ideas evolve. 

**Navigation Structure (CR-004):** Ideation appears as a nested submenu item under "Workplace" in the sidebar. The Workplace parent menu item has no action (does not redirect). Submenu items are always visible as indented nested children.

This feature integrates with a new agent skill (`task-type-ideation`) that analyzes uploaded ideas, brainstorms with users to refine concepts, and produces structured summaries ready for requirement gathering.

## User Stories

- As a **user**, I want to **upload my idea files to a central workspace**, so that **I can keep all related materials organized in one place**.
- As a **user**, I want to **browse my ideas in a tree view**, so that **I can quickly navigate between different idea folders and files**.
- As a **user**, I want to **edit idea files with auto-save**, so that **I don't lose my work and don't have to manually save**.
- As a **user**, I want to **rename idea folders**, so that **I can give meaningful names as my ideas evolve**.
- As a **user**, I want to **see Workplace as the first sidebar item**, so that **I can easily access my idea workspace**.
- As a **user**, I want to **quickly refine my idea with Copilot CLI**, so that **I can get AI assistance without manually typing commands** (CR-001).
- As a **user**, I want to **drag and drop files into existing idea folders**, so that **I can easily add new materials to ideas I'm already working on** (CR-002).
- As a **user**, I want to **configure which AI skills are available for ideation**, so that **I can customize my workflow and enable/disable tools as needed** (CR-003).
- As a **user**, I want to **see Ideation as a nested submenu item under Workplace**, so that **related pages are organized together** (CR-004).
- As a **user**, I want to **access Copilot actions via a hover menu**, so that **I can choose specific actions like "Refine idea"** (CR-004).
- As a **user**, I want to **copy a file's access URL**, so that **I can share direct links to idea files** (CR-005).

## Acceptance Criteria

- [x] AC-1: Workplace appears as the first item in the sidebar navigation (above existing items)
- [x] AC-2: Clicking Workplace shows a two-column layout (left: tree + controls, right: content area)
- [x] AC-3: "Upload Idea" button is visible at the top of the left sidebar
- [x] AC-4: Idea tree displays all folders and files from `x-ipe-docs/ideas/` directory
- [x] AC-5: Clicking a file in the tree opens it in the right content view
- [x] AC-6: File content can be edited in the content view
- [x] AC-7: Changes auto-save after 5 seconds of no input (debounced)
- [x] AC-8: Visual indicator shows "Saving..." during save and "Saved" on completion
- [x] AC-9: Clicking "Upload Idea" shows upload view with drag-and-drop zone
- [x] AC-10: Upload view also supports click-to-select file picker
- [x] AC-11: Uploaded files are stored in `x-ipe-docs/ideas/{Draft Idea - MMDDYYYY HHMMSS}/` (directly in folder)
- [x] AC-12: Folders in the tree can be renamed via inline editing (double-click)
- [x] AC-13: Folder rename updates the physical folder name on disk
- [x] AC-14: Tree view updates automatically when files/folders are added, renamed, or deleted
- [x] AC-20: Users can drag files onto folder nodes in the idea tree (CR-002)
- [x] AC-21: Folder highlights visually when files are dragged over it (CR-002)
- [x] AC-22: Dropping files onto a folder uploads them directly to that folder (CR-002)
- [x] AC-23: Toast notification confirms successful upload to existing folder (CR-002)
- [x] AC-15: "Copilot" button appears to the left of the Edit button in content view header (CR-001)
- [x] AC-16: Clicking Copilot button expands the terminal panel (CR-001)
- [x] AC-17: If terminal is in Copilot CLI mode, a new terminal session is created (CR-001)
- [x] AC-18: Copilot button sends `copilot` command with typing simulation (CR-001)
- [x] AC-19: After copilot CLI init, sends `refine the idea {file path}` command (CR-001)
- [ ] AC-24: "Ideation Toolbox" button visible next to "Create Idea" button (CR-003)
- [ ] AC-25: Clicking Toolbox button opens dropdown panel with 3 sections (CR-003)
- [ ] AC-26: Ideation section contains checkboxes: antv-infographic, mermaid (CR-003)
- [ ] AC-27: Mockup section contains checkbox: frontend-design (CR-003)
- [ ] AC-28: Sharing section shows placeholder text (CR-003)
- [ ] AC-29: Default selections: mermaid checked, frontend-design checked (CR-003)
- [ ] AC-30: `.ideation-tools.json` created in x-ipe-docs/ideas/ on first use (CR-003)
- [ ] AC-31: Checkbox changes save immediately to JSON file (CR-003)
- [ ] AC-32: UI state reflects JSON file state on page load (CR-003)
- [ ] AC-33: Ideation appears as nested submenu item under Workplace parent (CR-004)
- [ ] AC-34: Clicking Workplace parent does nothing (no redirect) (CR-004)
- [ ] AC-35: Ideation submenu item has icon with label (CR-004)
- [ ] AC-36: Copilot button is not directly clickable (CR-004)
- [ ] AC-37: Hovering Copilot button reveals dropdown menu (CR-004)
- [ ] AC-38: Copilot hover menu shows "Refine idea" as first option (CR-004)
- [ ] AC-39: Copilot hover menu shows 3 existing options below "Refine idea" (CR-004)
- [ ] AC-40: Clicking "Refine idea" triggers original Copilot button behavior (CR-004)
- [ ] AC-41: All existing Workplace functions work after rename to Ideation (CR-004)
- [x] AC-42: Copy URL icon appears next to Edit button in editor header (CR-005)
- [x] AC-43: Clicking copy URL copies file access URL to clipboard (CR-005)
- [x] AC-44: Toast notification confirms URL copied (CR-005)
- [x] AC-45: File rename button works in tree view for files (CR-005)

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

**Description:** Display folder/file structure from x-ipe-docs/ideas/

**Details:**
- Input: Directory structure at `x-ipe-docs/ideas/`
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
  4. Create folder: `x-ipe-docs/ideas/temp idea - {YYYY-MM-DD}/files/`
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

### FR-8: Drag-Drop Upload to Existing Folders (CR-002)

**Description:** Enable file upload via drag-and-drop onto existing idea folders in the tree

**Details:**
- Input: User drags files from system onto a folder node in the idea tree
- Process:
  1. Detect dragover on folder nodes
  2. Highlight folder as valid drop target
  3. On drop, extract files from drag event
  4. Call `/api/ideas/upload` with `target_folder` parameter
  5. Show toast notification on success/failure
  6. Refresh tree view
- Output: Files uploaded directly to target folder, tree refreshed

**Backend Changes:**
- Add optional `target_folder` form field to `/api/ideas/upload`
- If provided, upload files directly to that folder
- If not provided, create new timestamped folder (existing behavior)

**Frontend Changes:**
- Add `draggable-folder` class to folder nodes
- Bind `dragover`, `dragleave`, `drop` events to folder nodes
- Visual feedback: Add `drop-target` class on dragover

### FR-9: Ideation Toolbox Configuration (CR-003)

**Description:** Provide UI for configuring ideation tools with persistent state

**Details:**
- Input: User clicks "Ideation Toolbox" button next to "Create Idea"
- Process:
  1. Show dropdown panel with 3 sections
  2. Load existing settings from `.ideation-tools.json` (or use defaults)
  3. Display checkboxes for each tool option
  4. On checkbox change, save immediately to JSON file
  5. Close panel on outside click or button re-click
- Output: Tool configuration saved to JSON file

**Sections and Options:**
1. **Ideation** (for idea analysis and visualization)
   - `antv-infographic`: AntV Infographic DSL generation (default: unchecked)
   - `mermaid`: Mermaid diagram support (default: checked)
2. **Mockup** (for UI prototyping)
   - `frontend-design`: Frontend design skill (default: checked)
3. **Sharing** (for idea distribution - future expansion)
   - Placeholder text: "Coming soon..."

**JSON File Schema:**
```json
{
  "version": "1.0",
  "ideation": {
    "antv-infographic": false,
    "mermaid": true
  },
  "mockup": {
    "frontend-design": true
  },
  "sharing": {}
}
```

**File Location:** `x-ipe-docs/ideas/.ideation-tools.json`

**Backend Changes:**
- Add `GET /api/ideas/toolbox` - Read toolbox config
- Add `POST /api/ideas/toolbox` - Save toolbox config
- Create file with defaults if not exists on first read

**Frontend Changes:**
- Add "Ideation Toolbox" button with gear/toolbox icon
- Bootstrap dropdown panel with styled sections
- Checkbox inputs with labels
- Auto-save on checkbox change

### FR-10: Sidebar Submenu Navigation (CR-004)

**Description:** Restructure navigation to show Ideation as nested submenu under Workplace

**Details:**
- Input: Sidebar navigation structure
- Process:
  1. Add "Workplace" as parent menu item (no route/action)
  2. Add "Ideation" as first nested child (routes to current Workplace page)
  3. Add "UIUX Feedbacks" as second nested child (routes to FEATURE-022)
  4. Always show nested items (no expand/collapse needed)
  5. Indent nested items visually
- Output: Hierarchical sidebar with submenu structure

**Frontend Changes:**
- Update sidebar component to support nested menu items
- Add CSS for indented nested items
- Parent item click handler returns early (no navigation)
- Child items retain normal navigation behavior

### FR-11: Copilot Hover Menu (CR-004)

**Description:** Replace direct Copilot button click with hover dropdown menu

**Details:**
- Input: User hovers over Copilot button in content view header
- Process:
  1. Show dropdown menu on hover (or click to toggle)
  2. Display 4 menu options:
     - "Refine idea" (NEW - at top position)
     - [Existing option 2]
     - [Existing option 3]
     - [Existing option 4]
  3. On "Refine idea" click, execute original Copilot button behavior
  4. Hide menu on outside click or menu item selection
- Output: Dropdown menu with action options

**Frontend Changes:**
- Remove `onclick` from Copilot button
- Add Bootstrap dropdown or custom hover menu
- "Refine idea" option calls existing `handleCopilotClick()` function
- Menu styling consistent with existing UI

### FR-12: Page Rename to Ideation (CR-004)

**Description:** Rename all instances of "Workplace" to "Ideation"

**Details:**
- Input: Existing UI with "Workplace" labels
- Process:
  1. Update sidebar submenu item label to "Ideation"
  2. Update page title/header to "Ideation"
  3. Update any breadcrumbs or navigation indicators
  4. Maintain all existing functionality
- Output: Consistent "Ideation" branding throughout UI

**Verification:**
All existing functions must continue working:
- Idea upload/management
- File preview with Copilot integration
- Brainstorming history/sessions
- Mockup gallery

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

**Scenario:** `x-ipe-docs/ideas/` doesn't exist or is empty  
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

### Edge Case 6: Drop on File Node (CR-002)

**Scenario:** User drags files onto a file node instead of folder  
**Expected Behavior:** Ignore drop (only folders are valid drop targets)

### Edge Case 7: Drop on Root of Tree (CR-002)

**Scenario:** User drags files onto empty space in tree (not on any folder)  
**Expected Behavior:** Ignore drop (must target specific folder)

### Edge Case 8: Target Folder Deleted During Drag (CR-002)

**Scenario:** Folder is deleted by external process while user is dragging  
**Expected Behavior:** Show error toast "Folder no longer exists", refresh tree

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
| CR-005 | 01-28-2026 | Copy URL button for file access | Added US-10, AC-42 to AC-45 |
| CR-004 | 01-28-2026 | Sidebar submenu, rename to Ideation, Copilot hover menu | Added US-8/9, AC-33 to AC-41, FR-10 to FR-12 |
| CR-002 | 01-23-2026 | Drag-drop file upload to existing folders | Added US-7, AC-20 to AC-23, FR-8 |
| CR-001 | 01-22-2026 | Add Copilot button for idea refinement | Added US-6, AC-15 to AC-19, FR-7 |

---
