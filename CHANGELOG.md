# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **FEATURE-008: Workplace (Idea Management)** - Dedicated space for idea management
  - Two-column layout with tree navigation and content editor
  - IdeasService backend with get_tree(), upload(), rename_folder() methods
  - API endpoints: GET /api/ideas/tree, POST /api/ideas/upload, POST /api/ideas/rename
  - File upload via drag-and-drop or click-to-browse
  - Auto-save editor with 5-second debounce and status indicator (Saving.../Saved)
  - Inline folder rename on double-click
  - Uploads stored in `docs/ideas/{Draft Idea - MMDDYYYY HHMMSS}/` (files directly in folder)
  - Workplace appears as first item in sidebar navigation

- **FEATURE-005 v4.0: Interactive Console** - Full-featured terminal with xterm.js
  - xterm.js 5.3.0 integration with 256-color support
  - Session persistence (1 hour timeout, 10KB output buffer)
  - Auto-reconnection with session reattach
  - Split-pane support (up to 2 terminals)
  - Connection status indicator (connected/disconnected)
  - Debounced resize with proper PTY SIGWINCH handling
  - Backend: OutputBuffer, PersistentSession, SessionManager, PTYSession classes
  - WebSocket handlers: connect, attach, disconnect, input, resize

- **FEATURE-006 v2.0: Multi-Project Support**
  - ProjectFoldersService for managing multiple project folders
  - API endpoints: GET/POST/DELETE /api/projects, POST /api/projects/switch
  - Project switcher dropdown in sidebar
  - Settings persistence in SQLite

- **FEATURE-004: Live Refresh**
  - ContentRefreshManager with 5-second HTTP polling
  - Toggle button for auto-refresh
  - Scroll position preservation
  - Toast notification for updates

- **FEATURE-003: Content Editor**
  - ContentEditor class with edit/save/cancel flow
  - POST /api/file/save endpoint
  - Path validation and security checks

- **FEATURE-002: Content Viewer**
  - Markdown rendering with marked.js
  - Syntax highlighting with highlight.js
  - Mermaid.js diagram support
  - Code copy button

- **FEATURE-001: Project Navigation**
  - ProjectService for file tree navigation
  - FileWatcher for structure updates
  - Collapsible sidebar with icons

### Changed
- Updated base.html with xterm.js CDN links and terminal panel styles

### Fixed
- Various WebSocket CORS and connection issues
- Terminal visibility and cursor display
- PTY directory validation to prevent hangs
