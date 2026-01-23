# Requirement Summary

> Requirement ID: REQ-001  
> Created: 01-18-2026  
> Last Updated: 01-23-2026

## Project Overview

A lightweight project management web application that provides a user-friendly interface for humans to view and manage text-based project documentation created by AI agents.

## User Request

Create a web viewer for AI-created project documentation with:
- Left/right layout (sidebar navigation + content display)
- Markdown rendering with Mermaid diagram support
- Code syntax highlighting
- Edit capability
- Auto-refresh on file changes
- Interactive terminal console

## Clarifications

| Question | Answer |
|----------|--------|
| Multi-project support? | Single project at a time, but include UI placeholder for switching project root |
| Feature priority order? | 1. Navigation, 2. Content Display, 3. Console |
| Edit save workflow? | Direct save to file system (simple approach) |
| Version history? | Low priority - Git integration for change history and diff comparison |
| Terminal scope? | Full shell commands (not just Python), low priority |
| Settings page? | Yes, simple but visually clean |

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-001 | Project Navigation | v1.0 | Dynamic sidebar with folder tree navigation for project structure | None |
| FEATURE-002 | Content Viewer | v1.0 | Markdown and code file rendering with syntax highlighting | FEATURE-001 |
| FEATURE-003 | Content Editor | v1.0 | Edit mode for modifying files with direct save to filesystem | FEATURE-002 |
| FEATURE-004 | Live Refresh | v1.0 | Auto-detect file changes and refresh content in browser | FEATURE-002 |
| FEATURE-005 | Interactive Console | v1.0 | Collapsible terminal panel for shell command execution | FEATURE-001 |
| FEATURE-006 | Settings & Configuration | v1.0 | Settings page for project root path and app configuration | FEATURE-001 |
| FEATURE-007 | Git Integration | v1.0 | Version history and side-by-side diff comparison | FEATURE-002 |
| FEATURE-008 | Workplace (Idea Management) | v1.0 | Idea upload, tree view, inline editing with auto-save, folder rename | None |
| FEATURE-009 | File Change Indicator | v1.0 | Yellow dot indicator for changed files/folders in sidebar | FEATURE-001 |
| FEATURE-010 | Project Root Configuration | v1.0 | .x-ipe.yaml config file for nested project structure support | FEATURE-006 |

---

## Feature Details

### FEATURE-008: Workplace (Idea Management)

**Version:** v1.0  
**Brief Description:** Workplace for managing ideas with upload capability, tree view navigation, inline editing with auto-save, and folder rename functionality.

**Acceptance Criteria:**
- [ ] Workplace is the first item in the sidebar navigation
- [ ] Two-column layout: left sidebar with idea tree, right content area
- [ ] "Upload Idea" button at top of left sidebar
- [ ] Idea tree shows folders and files from `docs/ideas/`
- [ ] Clicking a file opens it in the right content view
- [ ] File editor with auto-save after 5 seconds of no changes
- [ ] Visual indicators for "Saving..." and "Saved" states
- [ ] Upload view supports drag-and-drop and file picker
- [ ] Uploaded files stored in `docs/ideas/{temp idea - YYYY-MM-DD}/files/`
- [ ] Folders can be renamed inline (double-click to edit)
- [ ] Folder rename updates physical folder name on disk

**Dependencies:**
- None (can be developed independently, reuses existing infrastructure)

**Technical Considerations:**
- Reuse ContentService for file operations
- Debounce auto-save with 5-second timer
- File upload endpoint with multipart form data
- Folder rename API endpoint
- Inline rename with contenteditable or input field

---

### FEATURE-009: File Change Indicator

**Version:** v1.0  
**Brief Description:** Yellow dot visual indicator for changed files and folders in the sidebar to notify users of updates.

**Acceptance Criteria:**
- [ ] Yellow dot appears before file/folder name when content changes on disk
- [ ] Yellow dot appears when structure changes (new/deleted files)
- [ ] Dot bubbles up to parent folders (if `docs/planning/features.md` changes, both file and `planning/` and `docs/` show dots)
- [ ] Clicking a file clears the dot for that file
- [ ] Parent folder dots clear automatically when no changed children remain
- [ ] Dot uses Bootstrap warning color for UI consistency
- [ ] Dots do not persist across page refresh (session-only)
- [ ] Works with existing polling-based structure detection

**Dependencies:**
- FEATURE-001: Project Navigation (enhancement to existing sidebar)

**Technical Considerations:**
- Track changed paths in memory (Set or Map)
- Extend existing `_checkForChanges()` method to identify changed paths
- Modify `renderFile()` and `renderFolder()` to show dot indicator
- Clear tracking on file click events
- Propagate changes up folder hierarchy
- CSS styling for dot indicator (small circle before item name)

---

### FEATURE-001: Project Navigation

**Version:** v1.0  
**Brief Description:** Dynamic sidebar with folder tree navigation for project structure

**Acceptance Criteria:**
- [ ] Left sidebar displays project folder structure
- [ ] Three top-level menu entries: Project Plan, Requirements, Code Repository
- [ ] Folders are expandable/collapsible
- [ ] Clicking a file loads it in content area
- [ ] Auto-detects new files/folders without page refresh
- [ ] UI placeholder for project root switching

**Dependencies:**
- None (MVP - first feature)

**Technical Considerations:**
- Backend API to scan project directory structure
- WebSocket or polling for file system change detection
- Bootstrap 5 accordion or tree component for navigation

---

### FEATURE-002: Content Viewer

**Version:** v1.0  
**Brief Description:** Markdown and code file rendering with syntax highlighting

**Acceptance Criteria:**
- [ ] Markdown files render as styled HTML
- [ ] Mermaid diagrams in markdown render correctly
- [ ] Code files display with syntax highlighting
- [ ] Supports common languages: Python, JS, HTML, CSS, JSON, YAML
- [ ] Clean, readable typography and styling

**Dependencies:**
- FEATURE-001: Need navigation to select files

**Technical Considerations:**
- Markdown library: marked.js or similar
- Mermaid.js for diagram rendering
- highlight.js or Prism.js for code syntax highlighting

---

### FEATURE-003: Content Editor

**Version:** v1.0  
**Brief Description:** Edit mode for modifying files with direct save to filesystem

**Acceptance Criteria:**
- [ ] Edit button toggles view mode to edit mode
- [ ] Text area or code editor for content modification
- [ ] Save button writes changes to file system
- [ ] Cancel button discards changes
- [ ] Visual feedback on save success/failure

**Dependencies:**
- FEATURE-002: Need content viewer as base

**Technical Considerations:**
- Simple textarea or CodeMirror/Monaco for editing
- Backend API endpoint for file write operations
- Error handling for permission/write failures

---

### FEATURE-004: Live Refresh

**Version:** v1.0  
**Brief Description:** Auto-detect file changes and refresh content in browser

**Acceptance Criteria:**
- [ ] Detect when currently viewed file changes on disk
- [ ] Auto-refresh content without full page reload
- [ ] Visual indicator when content is refreshed
- [ ] Handle file deletion gracefully

**Dependencies:**
- FEATURE-002: Need content viewer to refresh

**Technical Considerations:**
- WebSocket connection for real-time updates
- watchdog library for file system monitoring
- Debounce rapid file changes

---

### FEATURE-005: Interactive Console

**Version:** v1.0  
**Brief Description:** Collapsible terminal panel for shell command execution

**Acceptance Criteria:**
- [ ] Bottom panel collapsed by default (thin bar)
- [ ] Click to expand terminal interface
- [ ] Execute shell commands on server
- [ ] Display command output with proper formatting
- [ ] Command history support

**Dependencies:**
- FEATURE-001: Need basic app structure

**Technical Considerations:**
- WebSocket for bidirectional terminal communication
- xterm.js for terminal emulation in browser
- subprocess or pty for server-side execution
- Security: Consider command restrictions

---

### FEATURE-006: Settings & Configuration

**Version:** v1.0  
**Brief Description:** Settings page for project root path and app configuration

**Acceptance Criteria:**
- [ ] Settings page accessible from UI
- [ ] Configure project root directory path
- [ ] Settings persist across sessions
- [ ] Clean, simple UI design
- [ ] Validate project path exists

**Dependencies:**
- FEATURE-001: Need app navigation structure

**Technical Considerations:**
- SQLite for settings persistence
- Config validation on save
- Environment variable overrides

---

### FEATURE-007: Git Integration

**Version:** v1.0  
**Brief Description:** Version history and side-by-side diff comparison

**Acceptance Criteria:**
- [ ] View file commit history
- [ ] Show commit details (author, date, message)
- [ ] Side-by-side diff comparison between versions
- [ ] Navigate between versions

**Dependencies:**
- FEATURE-002: Need content viewer for diff display

**Technical Considerations:**
- GitPython or subprocess for git commands
- diff2html or similar for diff visualization
- Handle non-git repositories gracefully

---

### FEATURE-010: Project Root Configuration

**Version:** v1.0  
**Brief Description:** Support `.x-ipe.yaml` configuration file for nested project structures where X-IPE runs as a subfolder within a larger project.

**Acceptance Criteria:**
- [ ] X-IPE reads `.x-ipe.yaml` config file if present
- [ ] Config discovery: check cwd first, then traverse parent directories until found or root reached
- [ ] Config defines `project_root` and `x_ipe_app` paths (relative to config file location)
- [ ] Config defines `defaults.file_tree_scope` ("project_root" or "x_ipe_app")
- [ ] Config defines `defaults.terminal_cwd` for terminal working directory
- [ ] File tree defaults to configured `project_root` when config is present
- [ ] Works when launched from project root (`python x-ipe/main.py`) or x-ipe folder (`python main.py`)
- [ ] Invalid paths in config show warning toast, fall back to current working directory
- [ ] Existing multi-project folder behavior (FEATURE-006) remains unchanged
- [ ] Settings page shows read-only display of detected `.x-ipe.yaml` config
- [ ] Without `.x-ipe.yaml`, X-IPE behaves as before (backward compatible)

**Config File Structure:**
```yaml
# .x-ipe.yaml - placed at project root
version: 1
paths:
  project_root: "."              # Relative to this config file
  x_ipe_app: "./x-ipe"          # Path to X-IPE application
defaults:
  file_tree_scope: "project_root"  # or "x_ipe_app"
  terminal_cwd: "project_root"
```

**Expected Folder Structure:**
```
project-root/           ← project_root (shown in file tree by default)
├── .x-ipe.yaml         ← Configuration file
├── x-ipe/              ← x_ipe_app path
│   ├── main.py
│   ├── src/
│   └── ...
├── .github/skills/     ← Visible in file tree
├── docs/               ← Visible in file tree
└── ...
```

**Dependencies:**
- FEATURE-006: Settings & Configuration (for Settings page integration)

**Technical Considerations:**
- New ConfigService to parse `.x-ipe.yaml` (PyYAML)
- Config discovery traverses parent directories (max ~20 levels for safety)
- Path validation: ensure paths exist and are within project bounds
- Integrate with existing ProjectService for file tree scope
- Integrate with TerminalService for terminal cwd
- Settings page: read-only card showing detected config values
- Security: validate paths don't escape project root (no `../../../` attacks)

---

## Constraints

- Must work with existing AI agent project folder structure
- Must be responsive and visually modern (Bootstrap 5)
- Should be lightweight and easy to deploy
- Configuration for project root path (default: same directory as app)

## Target Users

- Human developers collaborating with AI agents
- Project managers reviewing AI-generated documentation

## Success Criteria

1. User can navigate project structure via sidebar
2. Markdown files render correctly with diagrams
3. Code files display with syntax highlighting
4. User can edit and save files
5. Changes on disk auto-refresh in browser
