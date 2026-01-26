# Feature Specification: Content Editor

> Feature ID: FEATURE-003  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-20-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 01-20-2026 | Initial specification | - |

## Overview

The Content Editor feature enables users to modify file contents directly in the browser and save changes back to the filesystem. It extends the Content Viewer (FEATURE-002) by adding an "Edit" mode that transforms the rendered view into an editable text area.

This feature provides a simple, straightforward editing experience with direct file system saves. When a user clicks "Edit", the rendered content switches to a text editor (textarea or code editor). After making changes, the user can save to persist modifications or cancel to discard them. Visual feedback confirms save success or failure.

The editor is designed for quick fixes and small modifications to AI-generated documentation. It's not intended to replace full-featured IDEs, but to enable immediate corrections without leaving the browser.

## User Stories

- As a **human reviewer**, I want to **edit markdown files in the browser**, so that **I can fix typos or clarify AI-generated content immediately**.

- As a **human reviewer**, I want to **see my changes saved to the actual file**, so that **my corrections persist when the file is next viewed**.

- As a **human reviewer**, I want to **cancel my edits without saving**, so that **I can abandon changes if I make mistakes**.

- As a **human reviewer**, I want to **see confirmation when my save succeeds**, so that **I know my changes were persisted**.

- As a **developer**, I want to **edit code files with proper formatting**, so that **I can make quick fixes to source code**.

## Acceptance Criteria

- [ ] AC-1: Edit button visible in content header when viewing a file
- [ ] AC-2: Clicking Edit switches from view mode to edit mode
- [ ] AC-3: Edit mode shows file content in editable textarea/editor
- [ ] AC-4: Save button writes content to file system
- [ ] AC-5: Cancel button discards changes and returns to view mode
- [ ] AC-6: Success toast notification shown after successful save
- [ ] AC-7: Error message shown if save fails (permission denied, etc.)
- [ ] AC-8: File content is re-rendered after save (shows updated content)
- [ ] AC-9: Unsaved changes warning if user navigates away while editing
- [ ] AC-10: Edit mode preserves original content until save
- [ ] AC-11: Keyboard shortcut Ctrl/Cmd+S saves file while editing

## Functional Requirements

### FR-1: Edit Mode Toggle

**Description:** Toggle between view mode and edit mode

**Details:**
- Input: User clicks Edit button
- Process: Switch content area from rendered view to editor
- Output: Editable content area with Save/Cancel buttons

**UI State Transitions:**
```
View Mode                    Edit Mode
┌──────────────────────┐     ┌──────────────────────┐
│ [Edit]               │ --> │ [Save] [Cancel]      │
│                      │     │                      │
│ Rendered Content     │     │ ┌──────────────────┐ │
│ (Markdown/Code)      │     │ │ Raw text content │ │
│                      │     │ │                  │ │
│                      │     │ │                  │ │
└──────────────────────┘     └──────────────────────┘
```

### FR-2: File Save API

**Description:** Backend API to write file content

**Details:**
- Input: Relative file path + new content
- Process: Validate path, write to filesystem
- Output: Success/failure status

**API Endpoint:** `POST /api/file/save`

**Request Body:**
```json
{
  "path": "x-ipe-docs/planning/task-board.md",
  "content": "# Updated Task Board\n..."
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "File saved successfully",
  "path": "x-ipe-docs/planning/task-board.md"
}
```

**Response (Error - 400/403/404):**
```json
{
  "success": false,
  "error": "Permission denied: Cannot write to this file"
}
```

### FR-3: Path Validation

**Description:** Validate file path before save

**Details:**
- Input: Relative file path
- Process: Security checks (path traversal, allowed extensions)
- Output: Validation pass/fail

**Security Rules:**
- Path must be within project root (no `../` traversal outside)
- Path must not contain null bytes
- File must exist (no creating new files in v1.0)
- File must be writable

### FR-4: Content Editor UI

**Description:** Text editing interface

**Details:**
- Input: File content string
- Process: Display in editable form
- Output: User-modified content

**UI Elements:**
- Textarea or code editor (monospace font)
- Full width/height of content area
- Line numbers (optional enhancement)
- Tab key inserts spaces (2 or 4)

### FR-5: Save Confirmation

**Description:** Visual feedback on save result

**Details:**
- Input: Save operation result
- Process: Show toast/notification
- Output: User sees confirmation

**Messages:**
- Success: "File saved successfully" (green toast, 3s auto-dismiss)
- Error: "Save failed: [reason]" (red toast, manual dismiss)

### FR-6: Unsaved Changes Warning

**Description:** Warn user before losing edits

**Details:**
- Input: User attempts to navigate away with unsaved changes
- Process: Show confirmation dialog
- Output: User confirms or cancels navigation

**Trigger Conditions:**
- Clicking sidebar to navigate to another file
- Clicking Cancel button (optional: skip warning if no changes)
- Browser back/refresh (via `beforeunload` event)

## Non-Functional Requirements

### NFR-1: Performance

- Edit mode switch: < 100ms
- Save operation: < 2 seconds
- Large files (>1MB): Show warning, allow edit

### NFR-2: Security

- Path traversal prevention (validate path within project root)
- No arbitrary file creation (only edit existing files in v1.0)
- Input sanitization on backend

### NFR-3: Usability

- Clear visual distinction between view and edit modes
- Obvious Save/Cancel buttons
- Keyboard shortcuts for power users

## UI/UX Requirements

### Edit Button Location

```
┌───────────────────────────────────────────────────┐
│ 📄 x-ipe-docs/planning/task-board.md                    │
│ ───────────────────────────────────────────────── │
│ [Auto-refresh: ON]                    [✏️ Edit]   │
│                                                   │
│  Rendered content here...                         │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Edit Mode Layout

```
┌───────────────────────────────────────────────────┐
│ 📝 Editing: x-ipe-docs/planning/task-board.md           │
│ ───────────────────────────────────────────────── │
│ [💾 Save] [✖️ Cancel]                              │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ # Task Board                                  │ │
│ │                                               │ │
│ │ > Task tracking for project                   │ │
│ │                                               │ │
│ │ ## Active Tasks                               │ │
│ │ ...                                           │ │
│ └───────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

### User Flow

1. User views a file (View Mode)
2. User clicks "Edit" button
3. Content switches to editable textarea
4. User makes modifications
5. User clicks "Save"
   - Success: Toast shown, content re-renders in view mode
   - Failure: Error toast, stays in edit mode
6. OR User clicks "Cancel"
   - If changes made: Confirm dialog
   - Returns to view mode with original content

## Dependencies

### Internal Dependencies

- **FEATURE-002 (Content Viewer):** Uses content fetching, provides base UI structure

### External Dependencies

- **Flask:** Backend API for file save endpoint
- **Bootstrap 5:** UI styling (already in project)

## Business Rules

### BR-1: Files Only

**Rule:** Only existing files can be edited; no new file creation in v1.0

**Rationale:** Simplifies implementation, prevents accidental file creation

### BR-2: Project Scope

**Rule:** Only files within project root can be edited

**Rationale:** Security - prevents writing to system files

### BR-3: Single Editor

**Rule:** Only one file can be edited at a time

**Rationale:** Simplifies state management

## Edge Cases & Constraints

### Edge Case 1: File Modified Externally During Edit

**Scenario:** User is editing, file changes on disk (by AI agent or another process)  
**Expected Behavior:** 
- Option A (v1.0 simple): User's save overwrites external changes
- Option B (future): Show merge/conflict dialog

### Edge Case 2: File Deleted During Edit

**Scenario:** User is editing, file is deleted externally  
**Expected Behavior:** Save creates the file again (write operation)

### Edge Case 3: Permission Denied

**Scenario:** User tries to save to read-only file  
**Expected Behavior:** Error message explaining permission issue

### Edge Case 4: Very Large File

**Scenario:** File > 1MB  
**Expected Behavior:** Show warning, still allow edit (performance may degrade)

### Edge Case 5: Binary File

**Scenario:** User tries to edit binary file (image, etc.)  
**Expected Behavior:** Disable edit button for non-text files

## Out of Scope

The following are explicitly **NOT** included in v1.0:

- Creating new files
- Deleting files
- Renaming/moving files
- Syntax highlighting in editor (plain textarea is acceptable)
- Real-time collaboration
- Version history/undo across saves
- Conflict resolution with external changes
- Split view (edit + preview side by side)

## Future Enhancements (Post v1.0)

- **Monaco/CodeMirror Editor:** Rich code editing with syntax highlighting
- **Side-by-Side Preview:** Live markdown preview while editing
- **File Creation:** Create new files from UI
- **Conflict Detection:** Warn if file changed since last load
- **Auto-save:** Periodic auto-save drafts
