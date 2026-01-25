# Feature Board

> Last Updated: 01-24-2026 14:07:00

## Overview

This board tracks all features across the project lifecycle.

**Status Definitions:**
- **Planned** - Feature identified, awaiting refinement
- **Refined** - Specification complete, ready for design
- **Designed** - Technical design complete, ready for implementation
- **Implemented** - Code complete, ready for testing
- **Tested** - Tests complete, ready for deployment
- **Completed** - Feature fully deployed and verified

---

## Feature Tracking

| Feature ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |
|------------|---------------|---------|--------|-------------------|---------|--------------|
| FEATURE-001 | Project Navigation | v1.0 | Implemented | [specification.md](../requirements/FEATURE-001/specification.md) | 01-18-2026 | 01-18-2026 00:35:00 |
| FEATURE-002 | Content Viewer | v1.0 | Implemented | [specification.md](../requirements/FEATURE-002/specification.md) | 01-18-2026 | 01-18-2026 00:55:00 |
| FEATURE-003 | Content Editor | v1.0 | Implemented | [specification.md](../requirements/FEATURE-003/specification.md) | 01-18-2026 | 01-20-2026 09:30:00 |
| FEATURE-004 | Live Refresh | v1.0 | Implemented | [specification.md](../requirements/FEATURE-004/specification.md) | 01-18-2026 | 01-19-2026 00:45:00 |
| FEATURE-005 | Interactive Console | v2.0 | Designed | [specification.md](../requirements/FEATURE-005/specification.md) | 01-18-2026 | 01-22-2026 10:30:00 |
| FEATURE-006 | Settings & Configuration | v1.0 | Implemented | [specification.md](../requirements/FEATURE-006/specification.md) | 01-18-2026 | 01-19-2026 14:30:00 |
| FEATURE-007 | Git Integration | v1.0 | Planned | - | 01-18-2026 | 01-18-2026 00:10:00 |
| FEATURE-008 | Workplace (Idea Management) | v1.3 | Implemented | [specification.md](../requirements/FEATURE-008/specification.md) | 01-22-2026 | 01-23-2026 14:35:00 |
| FEATURE-009 | File Change Indicator | v1.0 | Completed | [specification.md](../requirements/FEATURE-009/specification.md) | 01-22-2026 | 01-22-2026 11:21:00 |
| FEATURE-010 | Project Root Configuration | v1.0 | Completed | [specification.md](../requirements/FEATURE-010/specification.md) | 01-23-2026 | 01-23-2026 05:58:00 |
| FEATURE-011 | Stage Toolbox | v1.0 | Completed | [specification.md](../requirements/FEATURE-011/specification.md) | 01-24-2026 | 01-24-2026 06:48:00 |
| FEATURE-012 | Design Themes | v1.0 | Completed | [specification.md](../requirements/FEATURE-012/specification.md) | 01-24-2026 | 01-24-2026 09:25:00 |
| FEATURE-013 | Default Theme Content | v1.0 | Completed | [design-system.md](../themes/theme-default/design-system.md) | 01-24-2026 | 01-24-2026 09:35:00 |
| FEATURE-014 | Theme-Aware Frontend Design Skill | v1.0 | Planned | - | 01-24-2026 | 01-24-2026 07:50:00 |
| FEATURE-015 | Architecture DSL Skill | v1.0 | Completed | [specification.md](../requirements/FEATURE-015/specification.md) | 01-24-2026 | 01-24-2026 13:27:00 |
| FEATURE-016 | Architecture Diagram Renderer | v1.0 | Completed | [specification.md](../requirements/FEATURE-016/specification.md) | 01-24-2026 | 01-24-2026 14:00:00 |
| FEATURE-017 | Architecture DSL JavaScript Library | v1.0 | Planned | - | 01-24-2026 | 01-24-2026 14:07:00 |

---

## Status Details

### Planned (3)
- FEATURE-007: Git Integration
- FEATURE-014: Theme-Aware Frontend Design Skill
- FEATURE-017: Architecture DSL JavaScript Library

### Refined (0)
- None

### Designed (1)
- FEATURE-005: Interactive Console v2.0

### Implemented (5)
- FEATURE-001: Project Navigation
- FEATURE-002: Content Viewer
- FEATURE-003: Content Editor
- FEATURE-004: Live Refresh
- FEATURE-006: Settings & Configuration

### Tested (0)
- None

### Completed (8)
- FEATURE-008: Workplace (Idea Management) ✅
- FEATURE-009: File Change Indicator ✅
- FEATURE-010: Project Root Configuration ✅
- FEATURE-011: Stage Toolbox ✅
- FEATURE-012: Design Themes ✅
- FEATURE-013: Default Theme Content ✅
- FEATURE-015: Architecture DSL Skill ✅
- FEATURE-016: Architecture Diagram Renderer ✅

---

## Feature Details

### FEATURE-001: Project Navigation

**Version:** v1.0  
**Status:** Planned  
**Description:** Dynamic sidebar with folder tree navigation for project structure  
**Dependencies:** None  
**Specification:** -  
**Technical Design:** -  

---

### FEATURE-002: Content Viewer

**Version:** v1.0  
**Status:** Planned  
**Description:** Markdown and code file rendering with syntax highlighting  
**Dependencies:** FEATURE-001  
**Specification:** -  
**Technical Design:** -  

---

### FEATURE-003: Content Editor

**Version:** v1.0  
**Status:** Planned  
**Description:** Edit mode for modifying files with direct save to filesystem  
**Dependencies:** FEATURE-002  
**Specification:** -  
**Technical Design:** -  

---

### FEATURE-004: Live Refresh

**Version:** v1.0  
**Status:** Designed  
**Description:** Auto-detect file changes and refresh content in browser  
**Dependencies:** FEATURE-002  
**Specification:** [specification.md](../requirements/FEATURE-004/specification.md)  
**Technical Design:** [technical-design.md](../requirements/FEATURE-004/technical-design.md)  

---

### FEATURE-005: Interactive Console

**Version:** v2.0  
**Status:** Designed  
**Description:** Full terminal emulator with xterm.js, session persistence, auto-reconnection, and optional split-pane support  
**Dependencies:** FEATURE-001  
**Specification:** [specification.md](../requirements/FEATURE-005/specification.md)  
**Technical Design:** [technical-design.md](../requirements/FEATURE-005/technical-design.md)  

**v2.0 New Features:**
- xterm.js integration (replace VanillaTerminal)
- Session persistence (1hr with 10KB buffer)
- Auto-reconnection with session reattach
- Connection status indicator
- Multiple terminals (up to 2 split panes)
- Debounced resize with PTY SIGWINCH  

---

### FEATURE-006: Settings & Configuration

**Version:** v1.0  
**Status:** Implemented  
**Description:** Settings page for project root path and app configuration  
**Dependencies:** FEATURE-001  
**Specification:** [specification.md](../requirements/FEATURE-006/specification.md)  
**Technical Design:** [technical-design.md](../requirements/FEATURE-006/technical-design.md)  

---

### FEATURE-007: Git Integration

**Version:** v1.0  
**Status:** Planned  
**Description:** Version history and side-by-side diff comparison  
**Dependencies:** FEATURE-002  
**Specification:** -  
**Technical Design:** -  

---

### FEATURE-008: Workplace (Idea Management)

**Version:** v1.0  
**Status:** Designed  
**Description:** Idea upload, tree view navigation, inline editing with auto-save, and folder rename functionality  
**Dependencies:** None (reuses existing ContentService infrastructure)  
**Specification:** [specification.md](../requirements/FEATURE-008/specification.md)  
**Technical Design:** [technical-design.md](../requirements/FEATURE-008/technical-design.md)  

**Key Components:**
- `IdeasService` - Backend service for idea CRUD operations
- `WorkplaceView` - Two-column frontend layout
- `IdeaTree` - Tree navigation with inline rename
- `IdeaEditor` - Auto-save with 5s debounce
- `IdeaUploader` - Drag-drop + file picker

---

### FEATURE-010: Project Root Configuration

**Version:** v1.0  
**Status:** Designed  
**Description:** Support `.x-ipe.yaml` configuration file for nested project structures where X-IPE runs as a subfolder within a larger project  
**Dependencies:** FEATURE-006 (Settings & Configuration)  
**Specification:** [docs/requirements/FEATURE-010/specification.md](../requirements/FEATURE-010/specification.md)  
**Technical Design:** [docs/requirements/FEATURE-010/technical-design.md](../requirements/FEATURE-010/technical-design.md)  

**Key Capabilities:**
- Config file (`.x-ipe.yaml`) at project root
- Config discovery: cwd → parent directories → fallback
- Dual path awareness: `project_root` and `x_ipe_app`
- File tree defaults to project root when configured
- Terminal cwd configurable
- Settings page shows read-only config display
- Backward compatible (works without config file)

**Tasks:**
- TASK-079 (Feature Refinement) - Completed on 01-23-2026
- TASK-080 (Technical Design) - Completed on 01-23-2026
- TASK-082 (Test Generation) - Completed on 01-23-2026

---

### FEATURE-011: Stage Toolbox

**Version:** v1.0  
**Status:** Refined  
**Description:** Comprehensive tool management modal with accordion UI for all development stages (Ideation, Requirement, Feature, Quality, Refactoring)  
**Dependencies:** None (replaces FEATURE-008 v1.3 toolbox functionality)  
**Specification:** [specification.md](../requirements/FEATURE-011/specification.md)  
**Technical Design:** [technical-design.md](../requirements/FEATURE-011/technical-design.md)  

**Source:**
- Idea Summary: `docs/ideas/Toolbox Design/idea-summary-v2.md`
- Mockup: `docs/requirements/FEATURE-011/mockups/stage-toolbox-modal.html`

**Key Capabilities:**
- Modal triggered from top bar icon
- 5-stage accordion (Ideation, Requirement, Feature, Quality, Refactoring)
- Nested phases within each stage
- Toggle switches for tool enable/disable
- Config stored in `config/tools.json`
- Auto-migration from old `.ideation-tools.json`
- Placeholder stages show "Coming soon"

---

### FEATURE-015: Architecture DSL Skill

**Version:** v1.0  
**Status:** Designed  
**Description:** Tool skill that translates between natural language architecture descriptions and a structured DSL (Domain-Specific Language). Enables AI agents to precisely define, refine, and communicate architecture designs.  
**Dependencies:** FEATURE-011 (Stage Toolbox)  
**Specification:** [specification.md](../requirements/FEATURE-015/specification.md)  
**Technical Design:** [technical-design.md](../requirements/FEATURE-015/technical-design.md)  

**Source:**
- Idea Summary: `docs/ideas/architecture dsl skills/idea-summary-v2.md`
- Mockup: `docs/ideas/architecture dsl skills/mockups/architecture-dsl-demo-v4.html`

**Key Capabilities:**
- PlantUML-inspired DSL syntax
- Module View elements (layer, module, component)
- Landscape View elements (zone, app, database, action flows)
- Flexbox-inspired layout control (style property)
- text-align with inheritance
- virtual-box grouping containers
- NL ↔ DSL translation

**Tasks:**
- TASK-129 (Feature Refinement) - Completed on 01-24-2026
- TASK-130 (Technical Design) - Completed on 01-24-2026
- TASK-132 (Test Generation) - Completed on 01-24-2026

---

### FEATURE-016: Architecture Diagram Renderer

**Version:** v1.0  
**Status:** Planned  
**Description:** Tool skill that renders Architecture DSL into visual HTML canvas diagrams. Produces pixel-perfect diagrams matching reference samples with export capabilities.  
**Dependencies:** FEATURE-015 (Architecture DSL Skill), FEATURE-011 (Stage Toolbox)  
**Specification:** -  
**Technical Design:** -  

**Source:**
- Idea Summary: `docs/ideas/architecture dsl skills/idea-summary-v2.md`
- Mockup: `docs/ideas/architecture dsl skills/mockups/architecture-dsl-demo-v4.html`

**Key Capabilities:**
- Module View rendering (layers, modules, components)
- Landscape View rendering (zones, apps, databases, action flows)
- Layout control via flexbox properties
- Export as PNG, SVG, standalone HTML
- Live preview in content viewer
- ```architecture-dsl code block support

---

### FEATURE-017: Architecture DSL JavaScript Library

**Version:** v1.0  
**Status:** Planned  
**Description:** Standalone JavaScript library that parses Architecture DSL and renders diagrams to HTML Canvas. Reusable outside X-IPE as an NPM package.  
**Dependencies:** FEATURE-015 (DSL grammar), FEATURE-016 (rendering rules)  
**Specification:** -  
**Technical Design:** -  

**Source:**
- Change Request: `docs/requirements/FEATURE-016/CR-001.md`
- Requirements: `docs/requirements/requirement-details-part-2.md`

**Key Capabilities:**
- DSL parser following FEATURE-015 grammar
- Canvas-based rendering (alternative to HTML/CSS)
- JavaScript API: parse(), render(), exportPNG(), exportSVG()
- TypeScript support with type definitions
- Zero runtime dependencies
- NPM-compatible package structure

---
