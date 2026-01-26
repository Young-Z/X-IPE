# FEATURE-009: File Change Indicator

> Version: v1.0  
> Status: Refined  
> Created: 01-22-2026  
> Last Updated: 01-22-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 01-22-2026 | Initial specification | - |

## Overview

Visual indicator (yellow dot) in the sidebar to notify users when files or folders have changed, allowing users to quickly identify updates without manual checking.

## User Story

As a user browsing the project sidebar, I want to see a visual indicator when files have changed so that I can quickly notice which files have been updated since I last viewed them.

---

## Acceptance Criteria

### AC-1: Content Change Detection
**Given** a file's content changes on disk (detected by polling)  
**When** the sidebar refreshes  
**Then** a yellow dot appears before the file name

### AC-2: Structure Change Detection
**Given** a new file or folder is created/deleted  
**When** the sidebar refreshes  
**Then** a yellow dot appears before the new item (or parent folder for deletions)

### AC-3: Bubble Up to Parents
**Given** a file `x-ipe-docs/planning/features.md` changes  
**When** the sidebar renders  
**Then** yellow dots appear on:
- `features.md` (the file)
- `planning/` (parent folder)
- `x-ipe-docs/` (grandparent folder)

### AC-4: Clear on File Click
**Given** a file with a yellow dot indicator  
**When** the user clicks on that file  
**Then** the yellow dot disappears from that file

### AC-5: Clear Parent When Empty
**Given** a folder has a yellow dot because of changed children  
**And** the user clicks all changed children  
**When** no changed children remain  
**Then** the parent folder's yellow dot also disappears

### AC-6: Bootstrap Warning Color
**Given** the indicator dot is displayed  
**Then** it uses Bootstrap's warning color (`--bs-warning`) for UI consistency

### AC-7: No Persistence
**Given** the user refreshes the page  
**Then** all change indicators are cleared (session-only tracking)

### AC-8: Integration with Existing Polling
**Given** the existing 5-second structure polling  
**When** changes are detected  
**Then** the indicator system uses the same detection mechanism

---

## Functional Requirements

### FR-1: Change Tracking
- Track changed file/folder paths in memory (JavaScript Set)
- Identify changes by comparing old vs new structure hash
- Extract specific paths that changed between polls

### FR-2: Visual Indicator
- Small circular dot (6-8px diameter)
- Positioned before (left of) file/folder name
- Uses Bootstrap warning color (#ffc107)
- Subtle animation on appearance (optional: fade-in)

### FR-3: Parent Propagation
- When adding a changed path, also add all parent paths
- When clearing a path, check if parent has other changed children
- If no changed children remain, clear parent recursively

### FR-4: Click Handler Integration
- Extend existing file click handler
- On click: remove path from changed set
- Trigger parent cleanup check
- Re-render affected items (or use CSS class toggle)

---

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| File and folder with same name | Both show dot independently |
| Rapid consecutive changes | Single dot (debounced by poll interval) |
| Delete then recreate file | Shows as changed (new file) |
| Parent folder collapsed | Dot still visible on collapsed folder |
| Section header (e.g., "Project Plan") | No dot on section headers, only on items |

---

## UI/UX Notes

### Dot Placement
```
📁 x-ipe-docs/                    ← no dot (no changes)
  🔴 📁 planning/           ← dot (has changed child)
    🔴 📄 features.md       ← dot (content changed)
    📄 task-board.md        ← no dot (unchanged)
```

### Dot Style
- Position: `::before` pseudo-element or inline element
- Size: 6px width × 6px height
- Border-radius: 50% (circle)
- Margin-right: 6px
- Background: Bootstrap warning color

---

## Out of Scope

- Persisting change state across page refresh
- Notification sound or browser notification
- Change timestamp display
- Diff preview on hover
- ~~File content comparison (only structure/existence check)~~ **Now supported via mtime tracking (v1.1)**

---

## Dependencies

- FEATURE-001: Project Navigation (base sidebar implementation)
- Existing polling mechanism in `ProjectSidebar._checkForChanges()`

---

## Testing Considerations

1. **Unit Tests:**
   - Change set management (add, remove, check)
   - Parent path extraction
   - Parent cleanup logic

2. **Integration Tests:**
   - Dot appears after structure change
   - Dot clears on click
   - Parent propagation works correctly

3. **Manual Testing:**
   - Create/delete files via terminal
   - Verify dot appears within 5 seconds
   - Click through and verify clearing behavior
