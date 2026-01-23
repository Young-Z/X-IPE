# Feature Specification: Settings & Configuration

> Feature ID: FEATURE-006  
> Version: v2.0  
> Status: Refined  
> Last Updated: 01-20-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v2.0 | 01-20-2026 | Multiple project folders, project switcher, auto-refresh | - |
| v1.0 | 01-18-2026 | Initial specification | - |

## Overview

The Settings & Configuration feature provides a dedicated settings page where users can manage project folders and configure application preferences. **In v2.0**, users can manage a list of named project folders and switch between them from the main document viewer page using a dropdown selector.

Settings are persisted across browser sessions using SQLite storage. The UI follows Bootstrap 5 design language. Switching projects triggers automatic refresh of the sidebar navigation and content area.

## What's New in v2.0

- **Multiple Project Folders:** Manage a list of project folders (name + path) instead of single project root
- **Project Switcher:** Dropdown in doc viewer header to switch active project
- **Auto-Refresh:** Sidebar and content auto-refresh when switching projects
- **Default Project:** "Default Project Folder" → "." (application root) created on first run

## User Stories

- As a **human reviewer**, I want to **manage multiple project folders with names**, so that **I can quickly switch between different AI agent projects**.

- As a **user**, I want to **switch projects from the main page via dropdown**, so that **I don't have to navigate to settings every time**.

- As a **user**, I want to **add, edit, and remove project folders**, so that **I can organize my frequently accessed projects**.

- As a **user**, I want the **sidebar to auto-refresh when I switch projects**, so that **I immediately see the new project's structure**.

- As a **user**, I want to **my project list to persist across sessions**, so that **I don't have to re-add projects each time**.

## Acceptance Criteria

### Settings Page - Project Folder Management
- [ ] AC-1: Settings page displays a list of project folders with name and path
- [ ] AC-2: Default project "Default Project Folder" with path "." exists on first run
- [ ] AC-3: User can add a new project folder (name + path)
- [ ] AC-4: User can edit an existing project folder's name and path
- [ ] AC-5: User can remove a project folder (with confirmation)
- [ ] AC-6: Cannot remove the last remaining project folder
- [ ] AC-7: Path validation occurs when adding/editing (exists, is directory, readable)
- [ ] AC-8: Project names must be non-empty and unique
- [ ] AC-9: Project folders list persists to SQLite database

### Doc Viewer Page - Project Switcher
- [ ] AC-10: Dropdown selector in doc viewer header shows all project folders by name
- [ ] AC-11: Currently active project is highlighted in dropdown
- [ ] AC-12: Selecting a different project switches the active project
- [ ] AC-13: Switching project auto-refreshes the sidebar navigation tree
- [ ] AC-14: Switching project clears current content view (or shows placeholder)
- [ ] AC-15: Active project persists across page refreshes

### General
- [ ] AC-16: Settings page accessible via Settings icon in UI header
- [ ] AC-17: Bootstrap 5 styling consistent with rest of application

## Functional Requirements

### FR-1: Project Folders List Management

**Description:** Manage a list of named project folders in settings

**Details:**
- Input: List of project folders from database
- Process: Display in table/list with actions (Edit, Remove)
- Output: User can manage the project folder list

**UI Elements:**
```
┌─────────────────────────────────────────────────────────────┐
│ Project Folders                                    [+ Add]   │
├─────────────────────────────────────────────────────────────┤
│ Name                    │ Path                    │ Actions  │
├─────────────────────────┼─────────────────────────┼──────────┤
│ Default Project Folder  │ .                       │ ✏️ 🗑️    │
│ AI Agent Project        │ /Users/dev/ai-agent     │ ✏️ 🗑️    │
│ Web App                 │ /Users/dev/webapp       │ ✏️ 🗑️    │
└─────────────────────────────────────────────────────────────┘
```

### FR-2: Add Project Folder

**Description:** Allow users to add new project folders

**Details:**
- Input: User clicks "+ Add" button
- Process: Show modal/form for name + path input
- Output: New project folder added to list (after validation)

**Validation:**
- Name: Required, non-empty, unique
- Path: Required, must exist, must be directory, must be readable

**UI (Modal/Inline Form):**
```
┌─────────────────────────────────────────┐
│ Add Project Folder                       │
├─────────────────────────────────────────┤
│ Name: [________________________]         │
│ Path: [________________________]         │
│                                          │
│              [Cancel] [Add Project]      │
└─────────────────────────────────────────┘
```

### FR-3: Edit Project Folder

**Description:** Allow users to edit existing project folders

**Details:**
- Input: User clicks Edit (✏️) button on a project row
- Process: Show edit modal/form with current values
- Output: Project folder updated (after validation)

### FR-4: Remove Project Folder

**Description:** Allow users to remove project folders

**Details:**
- Input: User clicks Remove (🗑️) button on a project row
- Process: Show confirmation dialog
- Output: Project folder removed from list

**Constraints:**
- Cannot remove if only 1 project remains
- Cannot remove the currently active project (switch first)

### FR-5: Project Switcher Dropdown

**Description:** Dropdown in doc viewer header to switch active project

**Details:**
- Input: Current active project + list of all projects
- Process: Display dropdown with project names
- Output: User can select different project

**UI Location:** Header bar, near breadcrumb or after logo

**UI Elements:**
```
┌──────────────────────────────────────────────────────────┐
│ 📁 DocViewer   [▼ AI Agent Project    ]   [⚙️]          │
│                 ├─ Default Project Folder               │
│                 ├─ AI Agent Project    ✓                │
│                 └─ Web App                              │
├──────────────────────────────────────────────────────────┤
│ Sidebar        │ Content Area                           │
```

### FR-6: Project Switch Action

**Description:** Switch active project and refresh UI

**Details:**
- Input: User selects different project from dropdown
- Process: 
  1. Update active_project in settings
  2. Reload sidebar with new project structure
  3. Clear content area
- Output: Sidebar shows new project, content placeholder displayed

### FR-7: Active Project Persistence

**Description:** Remember which project is active across sessions

**Details:**
- Input: User switches project
- Process: Store active_project_id in settings
- Output: Same project is active on next page load

## Data Model

### Project Folders Table

```sql
CREATE TABLE IF NOT EXISTS project_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Settings Table (existing)

```sql
-- Add active_project_id to track which project is selected
INSERT INTO settings (key, value) VALUES ('active_project_id', '1');
```

### Initial Data

| id | name | path |
|----|------|------|
| 1 | Default Project Folder | . |

## API Endpoints

### GET /api/projects

Retrieve all project folders.

```json
Response (200):
{
  "projects": [
    {"id": 1, "name": "Default Project Folder", "path": "."},
    {"id": 2, "name": "AI Agent Project", "path": "/Users/dev/ai-agent"}
  ],
  "active_project_id": 1
}
```

### POST /api/projects

Add a new project folder.

```json
Request:
{
  "name": "My Project",
  "path": "/path/to/project"
}

Response (201):
{
  "success": true,
  "project": {"id": 3, "name": "My Project", "path": "/path/to/project"}
}

Response (400 - validation error):
{
  "success": false,
  "errors": {"path": "The specified path does not exist"}
}
```

### PUT /api/projects/<id>

Update an existing project folder.

```json
Request:
{
  "name": "Updated Name",
  "path": "/new/path"
}

Response (200):
{
  "success": true,
  "project": {"id": 2, "name": "Updated Name", "path": "/new/path"}
}
```

### DELETE /api/projects/<id>

Remove a project folder.

```json
Response (200):
{
  "success": true
}

Response (400 - cannot delete last):
{
  "success": false,
  "error": "Cannot remove the last project folder"
}
```

### POST /api/projects/switch

Switch active project.

```json
Request:
{
  "project_id": 2
}

Response (200):
{
  "success": true,
  "active_project_id": 2,
  "project": {"id": 2, "name": "AI Agent", "path": "/path"}
}
```

## UI/UX Requirements

### Settings Page - Project Folders Section

```
┌──────────────────────────────────────────────────────────────┐
│ ⚙️ Settings                                                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Project Folders                                    [+ Add]   │
│  ───────────────────────────────────────────────────────────  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Name                  │ Path              │ Actions     │  │
│  ├───────────────────────┼───────────────────┼─────────────┤  │
│  │ Default Project       │ .                 │ [✏️] [🗑️]  │  │
│  │ AI Agent              │ /Users/dev/agent  │ [✏️] [🗑️]  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│                                           [ Back to Viewer ]  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Doc Viewer Header with Project Dropdown

```
┌──────────────────────────────────────────────────────────────┐
│ 📁 DocViewer    [▼ Select Project... ]    [🔄] [⚙️]          │
├──────────────────────────────────────────────────────────────┤
│ Sidebar  │ Breadcrumb: docs / planning / features.md        │
```

## Edge Cases

### EC-1: Only One Project Folder

**Scenario:** User tries to delete the last remaining project  
**Expected:** Error message, deletion prevented

### EC-2: Active Project Deleted

**Scenario:** User tries to delete the currently active project  
**Expected:** Error message "Switch to another project before deleting this one"

### EC-3: Path Becomes Invalid

**Scenario:** Project path no longer exists  
**Expected:** Show warning icon, allow editing but block switching until fixed

### EC-4: Duplicate Project Name

**Scenario:** User tries to add project with existing name  
**Expected:** Validation error "A project with this name already exists"

## Out of Scope (v2.0)

- Drag-and-drop reordering of project folders
- Project folder grouping/categories
- Project folder icons/colors
- Import/export project list
- Recently accessed projects quick list

## Migration from v1.0

For existing installations:
1. Create `project_folders` table
2. Migrate existing `project_root` setting to first project folder entry
3. Set that as the active project

```sql
-- Migration script
INSERT INTO project_folders (name, path) 
SELECT 'Default Project Folder', COALESCE(
  (SELECT value FROM settings WHERE key = 'project_root'),
  '.'
);
```
