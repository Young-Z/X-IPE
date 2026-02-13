# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **FEATURE-030-A: UIUX Reference Tab & Console Integration**
  - New "UIUX Reference" tab in the Ideation upload view (third tab alongside Compose and Upload)
  - Pulsing "NEW" badge on tab to draw attention
  - Target Page URL input with validation (empty/invalid URL detection, accent border on focus)
  - Collapsible "Authentication Prerequisite" section with auth URL input and info hint
  - "Extra Instructions" textarea with character counter (0/1000)
  - "Go to Reference" button with 3-state transitions: idle → loading (spinner) → success (checkmark) → auto-reset
  - Console integration: auto-finds or creates terminal session, types copilot command with realistic keystroke simulation
  - Command format: `copilot execute uiux-reference --url {url} [--auth-url {auth}] [--extra "{instructions}"]`
  - Flow preview section showing 4 steps: Enter URL → Console Opens → Agent Navigates → Pick Elements
  - Editorial light theme: Outfit sans-serif body, warm cream background (#f8f6f1), deep indigo accent (#3730a3)
  - Staggered entrance animations (fadeSlideIn with progressive delays)
  - Added `uiux-reference` prompt entry to copilot-prompt.json (EN/ZH bilingual)
  - 22 unit tests, 23/23 acceptance criteria verified
- **FEATURE-025-D: KB Topics & Summaries**
  - Topics sidebar listing all knowledge base topics with icon, name, metadata, and item count badge
  - Active topic visual highlighting (green left border, darker background)
  - Topic detail view: header with name, "Processed" badge, Reprocess and Add Knowledge buttons
  - Stats row: Raw Files count, Summaries count, Last Updated (relative time), Related Topics count
  - AI-Generated Summary card with markdown rendering (headings, lists, code, blockquotes, highlights)
  - Summary version badge showing version number and generation date
  - Source references section linking to files used for summary generation
  - Version History panel listing up to 5 summary versions (newest-first)
  - Version switching: click any version to load its summary content
  - Knowledge Graph preview with connected topic nodes and Expand button (Phase 2 placeholder)
  - Source Files section with type-specific icons (PDF red, MD purple), file sizes, hover-reveal View/Download buttons
  - Reprocess button triggering POST /api/kb/process with auto-refresh
  - Add Knowledge button opening file upload dialog scoped to current topic
  - Empty state messages for no-topics and no-summaries scenarios
  - `GET /api/kb/topics/<name>/detail`: Topic detail API with metadata, raw files, summary versions
  - `GET /api/kb/topics/<name>/summary?version=N|latest`: Summary content retrieval API
  - Dark theme CSS fix: explicit text colors with fallbacks for visibility on dark backgrounds
  - 34 unit tests, 22/25 acceptance tests executed (100% pass rate)

- **FEATURE-029-D: Explorer UI Controls**
  - Drag-to-resize handle (5px) between terminal content and explorer panel
  - Explorer width resizable via drag within 160–360px range
  - col-resize cursor and accent highlight on handle hover
  - Centered dot indicator on handle hover (2px × 24px)
  - Explorer width persisted to localStorage (`console_explorer_width`)
  - Explorer collapsed/expanded state persisted (`console_explorer_collapsed`)
  - State restored on page reload (width, collapsed)
  - Handle auto-hidden when explorer collapsed
  - Preview panel offset synced with explorer width during resize
  - Edge case handling: invalid localStorage values clamped, graceful degradation
  - 18 acceptance test cases (18/18 pass, 100%)

- **FEATURE-025-C: KB Manager Skill**
  - LLMService: DashScope Generation API wrapper for AI-powered text completion
  - KBManagerService: Classification, summary generation, search, and reorganization
  - `POST /api/kb/process`: Trigger classification of landing files with AI-suggested topics
  - `POST /api/kb/process/confirm`: Execute confirmed classifications (move files, generate summaries)
  - `POST /api/kb/process/cancel`: Cancel active processing session
  - `GET /api/kb/search?q={query}`: Search knowledge base files by query
  - `POST /api/kb/reorganize`: Trigger topic reorganization
  - Session-based processing flow with pending/confirmed/cancelled states
  - Fallback to "uncategorized" topic when AI classification unavailable
  - Per-file atomic processing (failure on one file doesn't affect others)
  - 57 unit tests, 10 acceptance tests (100% pass rate)

- **FEATURE-029-A: Session Explorer Core**
  - Console Session Explorer panel replacing the 2-pane split-terminal layout
  - Right-side explorer panel (220px) with vertically scrollable session list
  - Support for up to 10 concurrent terminal sessions (Map-based architecture)
  - Session creation via "+" button with sequential naming ("Session 1", "Session 2", ...)
  - Single-session view: only active session visible, others hidden but running
  - Click-to-switch between sessions with output preservation
  - Background sessions continue running with buffered output
  - Default "Session 1" auto-created on console load
  - Active session indicator (green dot) and inactive indicator (dim dot)
  - "+" button disabled at 10/10 session limit
  - Zen mode hides explorer panel, restores on exit
  - Backward compatible: reconnection, buffer replay, FitAddon, voice controls
  - SessionExplorer class for panel UI management
  - 17 backend regression tests (test_session_explorer.py)
  - 16 acceptance test cases (16/16 pass, 100%)

### Changed
- **FEATURE-025-B: KB Landing Zone**
  - File upload to Knowledge Base landing folder via Upload button or drag-and-drop
  - Supported file types: PDF, MD, TXT, DOCX, XLSX, code files (.py, .js, .ts, .java, .go, .rs, .c, .cpp, .h, .html, .css, .json, .yaml), images (.png, .jpg, .jpeg, .gif, .svg, .webp)
  - Maximum file size: 50MB per file with validation
  - Duplicate file detection (skips with warning, preserves original)
  - File grid view with responsive card layout showing type icon, filename, and size
  - List view alternative with same data and selection support
  - File card selection with visual highlight (click to toggle, Select All, Clear)
  - Batch delete with confirmation dialog and disk cleanup
  - Sort by name, size, date, or type with ascending/descending toggle
  - Empty state with centered upload zone and drop area
  - Automatic index refresh after upload/delete operations
  - Path traversal protection on delete operations
  - Backend: KBService extensions (`upload_files()`, `delete_files()`, `get_landing_files()`, `_validate_upload()`)
  - API endpoints: `POST /api/kb/upload`, `POST /api/kb/landing/delete`, `GET /api/kb/landing`
  - Frontend: `kb-landing.js` (~550 lines) + `kb-landing.css` (~370 lines)
  - 57 unit tests across 9 test classes, 13 acceptance tests (all passing)
- **FEATURE-028-D: Settings Language Switch (Web UI)**
  - Language switching from Settings page — no CLI needed
  - Language card with globe icon, current language badge, dropdown (English / 中文)
  - Confirmation modal before switching (warns about copilot instruction regeneration)
  - Same-language guard: info toast "Already using [language]" — no API call
  - `POST /api/config/language` endpoint with atomicity: extract instructions BEFORE updating `.x-ipe.yaml`
  - Success/error/info toast notifications — no page reload
  - Dropdown disabled during switch to prevent concurrent operations
  - Badge updates in real-time after successful switch
  - Error recovery: dropdown reverts to previous language on failure
  - 17 unit/integration tests, 19 acceptance tests (Playwright)

- **FEATURE-026: Homepage Infinity Loop**
  - Interactive homepage visualization displaying 8 development lifecycle stages on an infinity loop (∞)
  - Entry point: Click "X IPE" logo in header to display homepage
  - Stage buttons: Ideation, Requirement, Implementation, Deployment, Validation, Monitoring, Feedback, Planning
  - Control loop (left): Blue theme (#3b82f6) for "What we decide" stages
  - Transparency loop (right): Purple theme (#8b5cf6) for "What we see" stages
  - Click behavior: Stage buttons highlight corresponding sidebar section
  - TBD handling: Deployment stage shows "Coming Soon" tooltip
  - Backend: HomepageService class (`homepage_service.py`) with stage mapping configuration
  - Frontend: `homepage-infinity.js` (260 lines) + `homepage-infinity.css` (180 lines)
  - Integration with sidebar.js (expandSection, highlightItem methods)
  - Responsive: Hidden on mobile screens < 768px
  - 26 unit tests validating stage mapping and template generation
  - 13 acceptance test cases (10 pass, 3 partial)

- **FEATURE-025-A: Knowledge Base Core Infrastructure**
  - New Knowledge Base page accessible at `/knowledge-base` route
  - KBService class (`kb_service.py`) for folder structure and index management
  - REST API endpoints: `/api/kb/index`, `/api/kb/index/refresh`, `/api/kb/topics`, `/api/kb/topics/<name>`
  - Automatic folder structure initialization: `landing/`, `topics/`, `processed/`, `index/`
  - File index management with `file-index.json` containing path, name, type, size, topic, created_date, keywords
  - Topic metadata management with `metadata.json` per topic
  - File type detection for 20+ extensions (pdf, markdown, python, javascript, etc.)
  - Keyword extraction from filenames (splits on `-`, `_`, spaces)
  - Frontend JS module (`kb-core.js`) with sidebar file tree and search filtering
  - CSS styles in `kb-core.css` (~120 lines)
  - Tracing decorators on all service methods and API routes
  - 54 tests validating KB core functionality

- **FEATURE-024: Project Quality Evaluation UI**
  - Quality evaluation view integrated into Workplace sidebar with clipboard-check icon
  - Action bar with Evaluate button and Refactoring dropdown (hover-triggered)
  - Version timeline showing up to 5 historical evaluation versions (newest on left)
  - Markdown preview with styled rendering (tables, lists, code blocks)
  - Empty state UI with CTA when no evaluation exists
  - 2 new REST API endpoints: `/api/quality-evaluation/status`, `/api/quality-evaluation/content`
  - Config v2.0 structure: `copilot-prompt.json` with `ideation` and `evaluation` sections
  - 6 refactoring options configurable via JSON
  - Console integration for command execution
  - Tracing decorators on all API routes
  - CSS styles in quality-evaluation.css (~250 lines)
  - JavaScript module in quality-evaluation.js (~370 lines)
  - 28 tests validating quality evaluation functionality

- **FEATURE-023-B: Tracing Dashboard UI**
  - Dashboard view integrated into Workplace sidebar with graph icon
  - Duration toggle buttons (3/15/30 minutes) to start tracing sessions
  - Live countdown timer with color states (green active, yellow warning, gray inactive)
  - Trace list sidebar with status indicators (green=success, red=error)
  - Config modal for retention hours and log path settings
  - Ignored APIs modal for pattern-based API exclusions
  - Auto-polling trace list every 5 seconds during active tracing
  - Session persistence across page refresh via tools.json
  - Toast notifications for operation feedback
  - CSS styles in tracing-dashboard.css (~300 lines)
  - JavaScript module in tracing-dashboard.js (~600 lines)
  - 27 tests validating dashboard API integration

- **FEATURE-023-A: Application Action Tracing - Core**
  - Decorator-based trace capture: `@trace_scope('name')` for actions, tools, agents
  - LLM observability: input/output capture with automatic context linking
  - Trace file storage in JSON format (instance/traces/{trace_id}.json)
  - 4 REST API endpoints: status, start, stop, logs
  - Tracing service with configurable retention and ignored API patterns
  - Integration with tools.json for config persistence
  - Context variable-based span linking for nested traces
  - 61 tests validating core tracing functionality

- **FEATURE-008 v1.5 (CR-006): Ideas Folder Tree UX Enhancement**
  - Drag-and-drop reorganization: move files/folders between locations with visual feedback
  - Folder view panel: dedicated panel with breadcrumb navigation, action bar, and file grid
  - Search/filter: real-time tree filtering with parent context preservation
  - Confirmation dialogs: reusable modal for delete/move operations with item counts
  - 7 new backend API endpoints: move, duplicate, download, folder-contents, search, delete-info, validate-drop
  - 4 new JavaScript modules: confirm-dialog.js, tree-search.js, tree-drag.js, folder-view.js
  - ~400 lines of new CSS for drag states, folder view, search bar, and confirmation dialogs
  - Design system: DM Sans font, Slate/Emerald color scheme, consistent 8px spacing
  - 49 new tests validating CR-006 implementation

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
  - `.github/skills/x-ipe-tool-architecture-dsl/` folder with complete skill structure
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
  - Registered in `x-ipe-docs/config/tools.json` under `stages.ideation.ideation.x-ipe-tool-architecture-dsl`
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
