# Idea Summary

> Idea ID: IDEA-001
> Folder: Draft Idea - 01222026 195931
> Version: v2
> Created: 2026-01-22
> Status: Refined

## Overview

Extends the lightweight project viewer with file/folder management capabilities within the Workplace (Idea Management) area, enabling users to create and delete files and folders directly from the UI via context menus.

## Problem Statement

v1 of the project viewer allows users to view, edit, and navigate files, but lacks the ability to create new files/folders or delete existing ones from the UI. Users must switch to their OS file manager or terminal to perform these basic file operations, breaking their workflow.

## Target Users

**Primary:** Solo developers/users working with AI coding agents on their local machine.

**Use Case:** While brainstorming in the Workplace area, human user wants to:
1. Create a new idea folder to organize thoughts
2. Create new files within idea folders (notes, drafts, etc.)
3. Delete obsolete or draft files/folders
4. All without leaving the web application

## Proposed Solution

Add context menu (right-click) actions to the Workplace file tree with:
- **New File** - Create a new file in the selected folder
- **New Folder** - Create a new folder in the selected location
- **Delete** - Remove file or folder with confirmation dialog

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Workplace File Tree                                        │
├─────────────────────────────────────────────────────────────┤
│  ▼ Draft Idea - 01222026                                    │
│    │ idea-summary-v1.md                                     │
│    │ idea-summary-v2.md ← [Right-click]                     │
│    │                      ┌──────────────┐                  │
│    └ Project Proposal     │ ✏️ Rename     │                  │
│                           │ 📄 New File   │                  │
│                           │ 📁 New Folder │                  │
│                           │ ─────────────│                  │
│                           │ 🗑️ Delete     │                  │
│                           └──────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Context Menu | Vanilla JS | Right-click menu UI |
| File API | Flask REST | Create/delete endpoints |
| Confirmation Dialog | Bootstrap Modal | Delete confirmation |
| Path Validation | Backend | Restrict to docs/ideas/ |

## Key Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Context Menu | Right-click menu on file tree items | High |
| New File | Create empty file with name prompt | High |
| New Folder | Create folder with name prompt | High |
| Delete with Confirm | Delete file/folder after confirmation | High |
| Scope Restriction | Operations limited to docs/ideas/ only | High |
| Inline Rename | Rename files/folders (existing in v1) | Medium |

## Success Criteria

- [ ] Right-click on file/folder shows context menu
- [ ] "New File" creates file with user-provided name
- [ ] "New Folder" creates folder with user-provided name
- [ ] "Delete" shows confirmation dialog before deleting
- [ ] Delete confirmation shows item name clearly
- [ ] Operations restricted to docs/ideas/ directory only
- [ ] Error messages for invalid names or paths
- [ ] File tree refreshes after create/delete operations

## Constraints & Considerations

| Constraint | Impact |
|------------|--------|
| Scope limited to docs/ideas/ | Prevents accidental deletion of code/docs |
| Confirmation required | Prevents accidental deletions |
| No recursive folder delete without listing | User sees what will be deleted |
| Single user only | No conflict resolution needed |

### Out of Scope for v2
- File/folder operations in src/, tests/, docs/planning/, etc.
- Drag-and-drop file moving
- File copying/duplicating
- Undo delete (no trash/recycle bin)
- Bulk operations (multi-select delete)

## Brainstorming Notes

**Decisions Made:**
1. **Scope:** Limited to docs/ideas/ only - safe boundary for experimentation
2. **UI Pattern:** Context menu (right-click) - familiar desktop metaphor
3. **Delete Safety:** Confirmation dialog required - prevents accidents
4. **Create Actions:** Both New File and New Folder in context menu

**Technical Insights:**
- Delete endpoint already exists from TASK-068 (delete_item in services.py)
- Can extend existing WorkplaceManager JavaScript class
- Bootstrap modal for confirmation keeps styling consistent
- Path validation critical to prevent escaping docs/ideas/ boundary

**Security Consideration:**
- Backend must validate all paths stay within docs/ideas/
- Reject any path traversal attempts (../)
- Whitelist allowed file extensions for creation

## Source Files

- idea-summary-v1.md (base version)
- Project Proposal (original requirements)

## Next Steps

- [ ] Proceed to Requirement Gathering for FEATURE: Workplace File Operations
- [ ] Define formal requirements with acceptance criteria
- [ ] Break down into implementable features
