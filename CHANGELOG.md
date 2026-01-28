# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **FEATURE-008 v1.4 (CR-004): Workplace Submenu Navigation**
  - Sidebar submenu structure: Workplace parent with nested Ideation and UIUX Feedbacks children
  - `/workplace` route serving dedicated Ideation page with existing functionality
  - `/uiux-feedbacks` route serving WIP placeholder page
  - Submenu CSS styles for parent/child indentation in sidebar
  - JavaScript handling for parent no-action click behavior
  - 11 new tests validating CR-004 implementation
  - Note: Copilot hover menu (AC-36 to AC-40) deferred to future CR

- **FEATURE-016: Architecture Diagram Renderer** - Tool skill for rendering Architecture DSL as visual diagrams
  - `.github/skills/tool-architecture-draw/` folder with complete skill structure
  - `SKILL.md`: Main skill definition with rendering workflow and capabilities
  - `templates/base-styles.css`: Complete CSS with design tokens and flexbox utilities
  - `templates/module-view.html`: HTML template for Module View diagrams
  - `templates/landscape-view.html`: HTML template for Landscape View diagrams
  - `references/rendering-rules.md`: Detailed DSL-to-HTML mapping and error handling
  - `examples/module-view-rendered.html`: Rendered AI Platform Architecture
  - `examples/landscape-view-rendered.html`: Rendered Enterprise Application Landscape
  - Module View rendering: layers with vertical labels, dashed-border modules, pill-shaped component badges
  - Landscape View rendering: zone containers, app boxes with status indicators, database cylinders, SVG flow arrows
  - Flexbox utility classes: jc-*, ai-*, fd-*, gap-* for layout control
  - Status colors: healthy (#22c55e), warning (#f97316), critical (#ef4444)
  - Export capabilities: PNG (html2canvas), SVG (DOM serialization), standalone HTML
  - Registered in `x-ipe-docs/config/tools.json` under `stages.ideation.ideation.tool-architecture-draw`
  - 71 comprehensive tests validating structure, templates, CSS, rules, examples, and config

- **FEATURE-015: Architecture DSL Skill** - Tool skill for architecture diagram DSL translation
  - `.github/skills/tool-architecture-dsl/` folder with complete skill structure
  - `SKILL.md`: Main skill definition with workflow, capabilities, and quick reference
  - `references/grammar.md`: Complete DSL grammar in BNF format with validation rules
  - `examples/module-view.dsl`: AI Platform Architecture example (3-layer structure)
  - `examples/landscape-view.dsl`: Enterprise Application Landscape example
  - PlantUML-inspired syntax: `@startuml module-view` / `@enduml` blocks
  - Module View elements: `layer`, `module`, `component`, `component <<stereotype>>`
  - Landscape View elements: `zone`, `app` (with tech/platform/status), `database`
  - Action flows: `source --> target : "action label"` (action-focused)
  - CSS Flexbox-inspired layout: `style "justify-content: space-evenly; column-gap: 16px"`
  - Supported style properties: justify-content, align-items, flex-direction, row-gap, column-gap
  - `text-align left|center|right` with inheritance (top → layer → module)
  - `virtual-box { }` for grouping with vertical stacking
  - Registered in `x-ipe-docs/config/tools.json` under `stages.ideation.ideation.tool-architecture-dsl`
  - 52 comprehensive tests validating structure, grammar, examples, and config

- **FEATURE-013: Default Theme Content** - Pre-built default theme for X-IPE
  - `x-ipe-docs/themes/theme-default/` folder with complete design system
  - `design-system.md`: Core tokens (colors, typography, spacing, radius, shadows)
  - Color palette: Primary (#0f172a), Secondary (#475569), Accent (#10b981), Neutral (#e2e8f0)
  - Semantic colors: Success, Warning, Error, Info
  - Full slate neutral scale (50-900)
  - Typography: Inter headings, System UI body, JetBrains Mono code
  - 8-step spacing scale (4-64px)
  - Component specs: buttons, cards, form inputs
  - `component-visualization.html`: Visual preview of all design tokens
  - JSON-LD structured data for AI agent parsing
  - Serves as template for creating custom themes

- **FEATURE-012: Design Themes** - Theming system for consistent brand design in mockups
  - ThemesService backend for theme discovery and parsing
  - Scans `x-ipe-docs/themes/theme-*/` folders for valid themes
  - Extracts color tokens (primary, secondary, accent, neutral) from design-system.md
  - Extracts description from first paragraph of design-system.md
  - API: `GET /api/themes` returns list with metadata (name, description, colors, files, path)
  - API: `GET /api/themes/{name}` returns theme details with design-system content
  - Stage Toolbox integration: Themes section at top of modal
  - 4-column visual theme card grid with auto-generated color swatches
  - Click card to select theme (pink accent border, checkmark indicator)
  - Theme selection persisted in `x-ipe-docs/config/tools.json` under `themes.selected`
  - Scrollable grid when >8 themes (max-height: 280px)
  - 36 comprehensive tests covering service, API, and edge cases

- **FEATURE-011: Stage Toolbox** - Comprehensive tool management modal
  - Modal UI with 680px width, light theme, accordion structure
  - 5 development stages: Ideation (functional), Requirement, Feature, Quality, Refactoring (placeholders)
  - Ideation stage with 3 phases: Ideation (`antv-infographic`, `mermaid`), Mockup (`frontend-design`), Sharing
  - Toggle switches for enabling/disabling tools with immediate persistence
  - Active tool count badges per stage
  - ToolsConfigService backend with `x-ipe-docs/config/tools.json` storage
  - Auto-migration from legacy `.ideation-tools.json` (deletes old file after migration)
  - GET/POST `/api/config/tools` API endpoints
  - StageToolboxModal JavaScript class with full modal lifecycle
  - Top bar "Toolbox" button with green accent (replaces old Workplace dropdown)
  - ESC key and overlay click to close modal
  - 29 comprehensive tests covering service, API, and integration

- **FEATURE-010: Project Root Configuration** - Support for X-IPE as subfolder in larger projects
  - `.x-ipe.yaml` config file at project root defines path mappings
  - Config discovery: searches cwd then parent directories (up to 20 levels)
  - ConfigService with load(), discover, parse, validate methods
  - ConfigData with get_file_tree_path(), get_terminal_cwd() helpers
  - /api/config endpoint returns detected configuration
  - Settings page shows "Project Configuration" section (read-only)
  - Automatic PROJECT_ROOT configuration at app startup
  - Backward compatible: works without config file (existing behavior unchanged)
  - PyYAML dependency added for YAML parsing
  - 42 comprehensive tests covering all config scenarios

- **FEATURE-009: File Change Indicator** - Visual notification for changed files
  - Yellow dot indicator (6px, Bootstrap warning color) appears before file/folder names
  - Dot shows when file content or structure changes (detected via 5s polling)
  - Bubble-up: parent folders also show dots when children change
  - Click-to-clear: clicking a file removes its dot
  - Parent cleanup: parent dots clear when no changed children remain
  - Session-only: dots reset on page refresh (no persistence)
  - Implemented in ProjectSidebar class with changedPaths Set tracking

- **FEATURE-008: Workplace (Idea Management)** - Dedicated space for idea management
  - Two-column layout with tree navigation and content editor
  - IdeasService backend with get_tree(), upload(), rename_folder() methods
  - API endpoints: GET /api/ideas/tree, POST /api/ideas/upload, POST /api/ideas/rename
  - File upload via drag-and-drop or click-to-browse
  - Auto-save editor with 5-second debounce and status indicator (Saving.../Saved)
  - Inline folder rename on double-click
  - Uploads stored in `x-ipe-docs/ideas/{Draft Idea - MMDDYYYY HHMMSS}/` (files directly in folder)
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
