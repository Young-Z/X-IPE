# Idea Summary

> Idea ID: IDEA-010
> Folder: Draw Architecture Diagram for itself
> Version: v2
> Created: 2026-01-24
> Status: Architecture Complete

## Overview

Use X-IPE's newly created architecture diagram skills (`tool-architecture-dsl` + `tool-architecture-draw`) to create self-documenting architecture diagrams for the X-IPE application itself. This is a practical demonstration of the skills while producing valuable documentation.

## Problem Statement

X-IPE lacks visual architecture documentation. As the application grows with 16+ features and 8+ services, developers and AI agents need clear visual references to understand:
1. How internal components are organized (layered architecture)
2. How X-IPE integrates with external systems (AI agents, GitHub, MCP)

## Target Users

1. **AI Agents** - Need architecture context when modifying X-IPE codebase
2. **Developers** - Understanding system structure before contributing
3. **Project Maintainers** - Documentation for onboarding and planning

## Proposed Solution

Create two architecture diagrams using the `tool-architecture-dsl` and `tool-architecture-draw` skills:

### 1. Module View (Internal Architecture)
Shows X-IPE's layered architecture with services as components:
- **Presentation Layer:** Jinja2 Templates, Frontend JS modules (Workplace Manager, Terminal, Stage Toolbox, Content Renderer)
- **Business Logic Layer:** Core Services (FileService, IdeasService, TerminalService), Configuration Services (ConfigService, SettingsService, ToolsConfigService), Extension Services (ThemesService, SkillsService)
- **Data Layer:** Project Files (x-ipe-docs/, src/, static/), Configuration (x-ipe-docs/config/tools.json, .x-ipe.yaml), Session Data (instance/)

### 2. Landscape View (External Integrations)
Shows X-IPE's connections to external systems:
- **External Systems:** Copilot CLI, GitHub, MCP Servers
- **X-IPE Application:** Flask Backend, Web Frontend, WebSocket Terminal
- **Skills & Configuration:** GitHub Skills, Tools Config, Themes
- **Storage:** Project Files, Ideas Folder, Session Data

## Key Features

1. **Module View Diagram**
   - 3-layer architecture (Presentation → Business → Data)
   - 8 services shown as components
   - Layout follows P1-P5 principles:
     - P1: All layers have consistent width
     - P2: Horizontal layout for peer services (low dependency)
     - P3: `justify-content: space-evenly` fills space with alignment
     - P4: Component sizes adjusted to fill modules when needed
     - P5: Default consistent sizes, adjusted only when necessary

2. **Landscape View Diagram**
   - X-IPE as central application
   - 3 external integrations (Copilot, GitHub, MCP)
   - Data flow arrows with labels
   - All systems show healthy status
   - Horizontal layout for peer systems per P2

3. **Output Format**
   - DSL source files (`.dsl`)
   - HTML rendered diagrams (`.html`)
   - Stored in idea folder

## Architecture Diagrams

### CSS-Based Rendering (Original)

| Diagram | Type | DSL File | HTML File | Tool Used |
|---------|------|----------|-----------|-----------|
| X-IPE Application Architecture | Module View | [module-view.dsl](architecture/module-view.dsl) | [module-view.html](architecture/module-view.html) | tool-architecture-dsl + tool-architecture-draw |
| X-IPE Integration Landscape | Landscape View | [landscape-view.dsl](architecture/landscape-view.dsl) | [landscape-view.html](architecture/landscape-view.html) | tool-architecture-dsl + tool-architecture-draw |

### Canvas Rendering (PNG Export)

| Diagram | Type | DSL File | HTML File | Tool Used |
|---------|------|----------|-----------|-----------|
| X-IPE Application Architecture | Module View | [module-view-canvas.dsl](architecture/module-view-canvas.dsl) | [module-view-canvas.html](architecture/module-view-canvas.html) | tool-architecture-dsl + tool-architecture-draw (Canvas) |
| X-IPE Integration Landscape | Landscape View | [landscape-view-canvas.dsl](architecture/landscape-view-canvas.dsl) | [landscape-view-canvas.html](architecture/landscape-view-canvas.html) | tool-architecture-dsl + tool-architecture-draw (Canvas) |

### Viewing Instructions

- **HTML files:** Open in any web browser to view rendered diagrams
- **Canvas HTML files:** Include "Export PNG" and "Export 2x PNG" buttons for image download
- **DSL files:** View in text editor; can be re-rendered by AI agent using `tool-architecture-draw` skill

## Success Criteria

- [x] Module View diagram created with all 8 services
- [x] Landscape View diagram shows Copilot, GitHub, MCP integrations
- [x] Diagrams stored in current idea folder (`x-ipe-docs/ideas/Draw Architecture Diagram for itself/architecture/`)
- [x] HTML outputs render correctly
- [x] Diagrams follow Architecture DSL grammar

## Constraints & Considerations

1. **DSL Grammar** - Must follow `tool-architecture-dsl` syntax exactly ✅
2. **Skill Integration** - Use `tool-architecture-draw` for HTML rendering ✅
3. **Accuracy** - Diagrams reflect actual codebase structure ✅
4. **Maintainability** - DSL source files are easy to update ✅

## Brainstorming Notes

**Scope Decisions:**
- Medium detail level for Module View (services as components, not methods)
- Recommended integrations for Landscape View (Copilot, GitHub, MCP)
- Both DSL and HTML outputs
- Store in current idea folder first (`x-ipe-docs/ideas/Draw Architecture Diagram for itself/`)

**Architecture Analysis:**
- 8 backend services identified in `src/services/`
- Clear 3-layer architecture pattern (Flask + Services + Filesystem)
- External integrations via MCP, GitHub API, and direct filesystem access

## Ideation Artifacts

- Original idea: `new idea.md` (raw input)
- Architecture skills reference:
  - `.github/skills/tool-architecture-dsl/SKILL.md`
  - `.github/skills/tool-architecture-draw/SKILL.md`

## Source Files

- new idea.md

## Next Steps

- [x] ~~Proceed to **Idea to Architecture** task~~ (COMPLETE)
- [ ] Proceed to **Requirement Gathering** (if this becomes a feature)
- [ ] Or consider this idea complete as documentation artifact

## References & Common Principles

### Applied Principles

- **Layered Architecture Pattern:** Separating presentation, business logic, and data access concerns - [Microsoft Docs](https://docs.microsoft.com/en-us/azure/architecture/guide/architecture-styles/n-tier)
- **C4 Model Concepts:** Context and Container diagrams for architecture documentation - [C4Model.com](https://c4model.com/)

### Further Reading

- [Architecture DSL Skill](.github/skills/tool-architecture-dsl/SKILL.md) - DSL grammar reference
- [Architecture Draw Skill](.github/skills/tool-architecture-draw/SKILL.md) - HTML rendering rules
