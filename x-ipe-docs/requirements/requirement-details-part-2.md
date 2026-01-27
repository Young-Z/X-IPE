# Requirement Details - Part 2

> Continued from: [requirement-details-part-1.md](requirement-details-part-1.md)  
> Created: 01-24-2026

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-012 | Design Themes | v1.0 | Theme folder structure, sidebar menu, toolbox integration with visual theme cards | FEATURE-011 |
| FEATURE-013 | Default Theme Content | v1.0 | Pre-built default theme with design-system.md and component-visualization.html | FEATURE-012 |
| FEATURE-014 | Theme-Aware Frontend Design Skill | v1.0 | New tool-frontend-design skill that reads selected theme and applies design tokens | FEATURE-012 |
| FEATURE-015 | Architecture DSL Skill | v1.0 | Tool skill for NL ↔ DSL translation of architecture descriptions | FEATURE-011 |
| FEATURE-016 | Architecture Diagram Renderer | v1.0 | Tool skill that renders Architecture DSL into visual HTML canvas diagrams | FEATURE-015 |
| FEATURE-017 | Architecture DSL JavaScript Library | v1.0 | Standalone JS library that parses Architecture DSL and renders to Canvas | FEATURE-015, FEATURE-016 |
| FEATURE-018 | X-IPE CLI Tool | v1.0 | PyPI package with CLI commands: init, serve, upgrade, status, info | None |
| FEATURE-019 | Simplified Project Setup | v1.0 | `x-ipe init` creates x-ipe-docs/, .github/skills/, .x-ipe/ structure | FEATURE-018 |
| FEATURE-020 | Skills Discovery & Override | v1.0 | Skills loaded from package, local overrides in .github/skills/ | FEATURE-018, FEATURE-019 |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| themes-toolbox-modal | FEATURE-012 | [themes-toolbox-modal.html](FEATURE-012/mockups/themes-toolbox-modal.html) |
| architecture-dsl-demo | FEATURE-015 | [architecture-dsl-demo.html](FEATURE-015/mockups/architecture-dsl-demo.html) |
| architecture-diagram-renderer | FEATURE-016 | [architecture-diagram-renderer.html](FEATURE-016/mockups/architecture-diagram-renderer.html) |

---

## Feature Details (Continued)

### FEATURE-012: Design Themes

**Version:** v1.0  
**Brief Description:** Theming system for X-IPE that enables brands to define unified design systems and apply them consistently when designing mockups. Includes theme folder structure, sidebar menu for theme files, and toolbox modal integration with visual theme cards.

**Source:** [Idea Summary - Feature Themes](../ideas/Feature-Themes/idea-summary-v1.md)  
**Mockup:** [Themes in Toolbox Modal](../ideas/Feature-Themes/mockups/themes-toolbox-v1.html)

**Acceptance Criteria:**

1. **Theme Folder Structure**
   - [ ] AC-1.1: Themes stored in `x-ipe-docs/themes/` folder
   - [ ] AC-1.2: Each theme in subfolder named `theme-{name}/` (e.g., `theme-default/`, `theme-ocean/`)
   - [ ] AC-1.3: Each theme folder contains `design-system.md` (required)
   - [ ] AC-1.4: Each theme folder contains `component-visualization.html` (required)
   - [ ] AC-1.5: Theme discovery scans `x-ipe-docs/themes/theme-*/` pattern

2. **design-system.md Structure**
   - [ ] AC-2.1: Core Tokens section (mandatory): colors, typography, spacing
   - [ ] AC-2.2: Component Specs section (optional): buttons, forms, cards
   - [ ] AC-2.3: Usage Guidelines section (optional): accessibility, best practices
   - [ ] AC-2.4: Structured format parseable by AI agents (markdown with code blocks)

3. **component-visualization.html Structure**
   - [ ] AC-3.1: Visual HTML preview of all design tokens for humans
   - [ ] AC-3.2: Structured data (JSON-LD or data attributes) for AI parsing
   - [ ] AC-3.3: Self-contained HTML file (no external dependencies beyond CDN fonts)

4. **Sidebar Themes Menu**
   - [ ] AC-4.1: "Themes" menu item in sidebar navigation
   - [ ] AC-4.2: Themes menu shows folder tree of `x-ipe-docs/themes/`
   - [ ] AC-4.3: Clicking theme subfolder shows its files (design-system.md, component-visualization.html)
   - [ ] AC-4.4: Clicking a file opens it in the content viewer (existing functionality)
   - [ ] AC-4.5: Themes menu uses same tree component as Project navigation

5. **Toolbox Modal - Themes Section**
   - [ ] AC-5.1: Themes section appears at TOP of Stage Toolbox modal (before stage accordions)
   - [ ] AC-5.2: Section header shows "Design Themes" with palette icon and badge showing count
   - [ ] AC-5.3: Visual theme cards in 4-column grid layout
   - [ ] AC-5.4: Each card shows: color swatches, typography preview, theme name, description
   - [ ] AC-5.5: Click card to select theme (checkmark indicator, pink accent border)
   - [ ] AC-5.6: Maximum 8 themes visible, then scrollable grid
   - [ ] AC-5.7: Thumbnails auto-generated from design-system.md color tokens

6. **Theme Selection Persistence**
   - [ ] AC-6.1: Selected theme saved to `x-ipe-docs/config/tools.json` under `themes.selected` key
   - [ ] AC-6.2: Theme selection is global (applies to all ideas)
   - [ ] AC-6.3: If no theme selected, default to `theme-default`
   - [ ] AC-6.4: Theme selection persists across browser refresh

7. **Backend API**
   - [ ] AC-7.1: `GET /api/themes` returns list of available themes with metadata
   - [ ] AC-7.2: `GET /api/themes/{name}` returns theme details (design-system.md content, file paths)
   - [ ] AC-7.3: Theme metadata includes: name, description, color tokens (for thumbnail generation)

**Dependencies:**
- FEATURE-011: Stage Toolbox (required for toolbox modal integration)

**Technical Considerations:**
- Reuse FileService patterns for theme folder scanning
- Extend ToolsConfigService to handle theme selection
- Parse design-system.md to extract color tokens for thumbnail generation
- Theme cards should be clickable components with visual feedback

**Clarifications:**
| Question | Answer |
|----------|--------|
| Thumbnail generation? | Auto-generated from design-system.md color tokens |
| Grid limit before scroll? | 8 themes max, then scrollable |
| Persistence scope? | Global only (x-ipe-docs/config/tools.json) |
| Sidebar themes menu purpose? | Display raw theme files for viewing/editing |

---

### FEATURE-013: Default Theme Content

**Version:** v1.0  
**Brief Description:** Pre-built default theme that ships with X-IPE, providing a neutral design system baseline and serving as a template for custom themes.

**Acceptance Criteria:**

1. **Theme Files**
   - [ ] AC-1.1: `x-ipe-docs/themes/theme-default/` folder exists
   - [ ] AC-1.2: `design-system.md` with complete core tokens
   - [ ] AC-1.3: `component-visualization.html` with visual preview

2. **design-system.md Content**
   - [ ] AC-2.1: Color palette: primary (#0f172a), secondary (#475569), accent (#10b981), neutrals (slate scale), semantic (success, warning, error, info)
   - [ ] AC-2.2: Typography: Inter for headings, System UI for body, JetBrains Mono for code
   - [ ] AC-2.3: Spacing scale: 4px base unit, 8-step scale (4, 8, 12, 16, 24, 32, 48, 64)
   - [ ] AC-2.4: Border radius tokens: sm (4px), md (8px), lg (12px), full (9999px)
   - [ ] AC-2.5: Shadow tokens: sm, md, lg definitions

3. **component-visualization.html Content**
   - [ ] AC-3.1: Color swatches grid showing all palette colors
   - [ ] AC-3.2: Typography samples for all font sizes/weights
   - [ ] AC-3.3: Spacing visualization
   - [ ] AC-3.4: JSON-LD script block with structured token data

4. **Template Purpose**
   - [ ] AC-4.1: Serves as fallback when no theme selected
   - [ ] AC-4.2: Can be copied to create new themes
   - [ ] AC-4.3: Well-documented with comments explaining each section

**Dependencies:**
- FEATURE-012: Design Themes (provides folder structure)

**Technical Considerations:**
- Use clean, neutral colors that work for any project type
- Ensure component-visualization.html is standalone (no external CSS except CDN fonts)
- JSON-LD format for AI-readable structured data

---

### FEATURE-014: Theme-Aware Frontend Design Skill

**Version:** v1.0  
**Brief Description:** New `tool-frontend-design` skill that reads the selected theme from config, loads design tokens, and applies them when generating frontend mockups.

**Acceptance Criteria:**

1. **Skill Structure**
   - [ ] AC-1.1: Skill folder at `.github/skills/tool-frontend-design/`
   - [ ] AC-1.2: SKILL.md with complete skill definition
   - [ ] AC-1.3: Registered in toolbox as a Mockup phase tool

2. **Theme Loading**
   - [ ] AC-2.1: Read selected theme from `x-ipe-docs/config/tools.json` → `themes.selected`
   - [ ] AC-2.2: Load `design-system.md` from selected theme folder
   - [ ] AC-2.3: Load `component-visualization.html` for reference
   - [ ] AC-2.4: Fall back to `theme-default` if selected theme missing

3. **Design Token Application**
   - [ ] AC-3.1: Apply color tokens when generating CSS
   - [ ] AC-3.2: Apply typography tokens (fonts, sizes, weights)
   - [ ] AC-3.3: Apply spacing tokens for margins/padding
   - [ ] AC-3.4: Apply border-radius and shadow tokens

4. **Skill Behavior**
   - [ ] AC-4.1: Invocable from ideation toolbox modal (toggleable)
   - [ ] AC-4.2: Generates mockup HTML files in idea folder
   - [ ] AC-4.3: Includes CSS that uses theme tokens
   - [ ] AC-4.4: Output files reference theme name in comments

5. **Relationship to frontend-design**
   - [ ] AC-5.1: Separate skill from existing `frontend-design`
   - [ ] AC-5.2: Can coexist - user can enable either or both
   - [ ] AC-5.3: `tool-frontend-design` is theme-aware, `frontend-design` uses its own defaults

**Dependencies:**
- FEATURE-012: Design Themes (provides theme infrastructure)
- FEATURE-013: Default Theme Content (provides fallback theme)

**Technical Considerations:**
- Skill should read config at start of execution, not cache theme selection
- Parse design-system.md to extract usable CSS variables
- Consider generating a CSS custom properties file from theme tokens

---

### FEATURE-015: Architecture DSL Skill

**Version:** v1.0  
**Brief Description:** Tool skill that translates between natural language architecture descriptions and a structured DSL (Domain-Specific Language). Enables AI agents to precisely define, refine, and communicate architecture designs.

**Source:** [Idea Summary v2](../ideas/architecture%20dsl%20skills/idea-summary-v2.md)  
**Mockup:** [Architecture DSL Demo v4](../ideas/architecture%20dsl%20skills/mockups/architecture-dsl-demo-v4.html)

**Acceptance Criteria:**

1. **Skill Structure**
   - [ ] AC-1.1: Skill folder at `.github/skills/tool-architecture-dsl/`
   - [ ] AC-1.2: SKILL.md with complete skill definition
   - [ ] AC-1.3: DSL grammar reference document included
   - [ ] AC-1.4: Example DSL files for Module View and Landscape View

2. **DSL Syntax - Core Elements**
   - [ ] AC-2.1: `@startuml` / `@enduml` block delimiters
   - [ ] AC-2.2: `title` property for diagram title
   - [ ] AC-2.3: `direction` property (top-to-bottom, left-to-right)
   - [ ] AC-2.4: Comments with `'` prefix

3. **DSL Syntax - Module View Elements**
   - [ ] AC-3.1: `layer "name" as alias { }` for architectural layers
   - [ ] AC-3.2: `module "name" { }` for modules within layers
   - [ ] AC-3.3: `component "name"` for components within modules
   - [ ] AC-3.4: `component "name" <<stereotype>>` for decorated components (e.g., `<<model>>`, `<<icon>>`)

4. **DSL Syntax - Landscape View Elements**
   - [ ] AC-4.1: `zone "name" { }` for application zones
   - [ ] AC-4.2: `app "name" as alias { tech: X, platform: Y, status: Z }` for applications
   - [ ] AC-4.3: `database "name" as alias` for database nodes
   - [ ] AC-4.4: `source --> target : "action label"` for action flows

5. **DSL Syntax - Layout Control (Flexbox-inspired)**
   - [ ] AC-5.1: `style "property: value"` for flexbox layout (justify-content, align-items, flex-direction, row-gap, column-gap)
   - [ ] AC-5.2: `text-align left|center|right` at top, layer, or module level with inheritance
   - [ ] AC-5.3: `virtual-box { }` container for grouping (multiple boxes stack vertically)

6. **Skill Capabilities**
   - [ ] AC-6.1: Natural language → DSL translation
   - [ ] AC-6.2: DSL → Natural language explanation
   - [ ] AC-6.3: DSL validation (syntax checking)
   - [ ] AC-6.4: DSL refinement (update existing DSL based on feedback)

7. **Integration**
   - [ ] AC-7.1: Configurable via `x-ipe-docs/config/tools.json` under `stages.ideation.ideation.tool-architecture-dsl`
   - [ ] AC-7.2: Can be enabled/disabled in Stage Toolbox modal
   - [ ] AC-7.3: Works alongside other ideation tools (mermaid, antv-infographic)

**Dependencies:**
- FEATURE-011: Stage Toolbox (for toolbox modal integration)

**Technical Considerations:**
- DSL syntax inspired by PlantUML for familiarity
- Flexbox-inspired layout properties for precise control
- text-align inherits from parent (top → layer → module)
- virtual-box enables nested grouping with vertical stacking

**Clarifications:**
| Question | Answer |
|----------|--------|
| Deployment context? | Integrated into X-IPE app as a feature |
| Integration point? | Configurable via tools.json |
| Scope? | Module View and Application Landscape View |

---

### FEATURE-016: Architecture Diagram Renderer

**Version:** v1.0  
**Brief Description:** Tool skill that renders Architecture DSL into visual HTML canvas diagrams. Produces pixel-perfect diagrams matching reference samples with export capabilities.

**Source:** [Idea Summary v2](../ideas/architecture%20dsl%20skills/idea-summary-v2.md)  
**Mockup:** [Architecture DSL Demo v4](../ideas/architecture%20dsl%20skills/mockups/architecture-dsl-demo-v4.html)

**Acceptance Criteria:**

1. **Skill Structure**
   - [ ] AC-1.1: Skill folder at `.github/skills/tool-architecture-draw/`
   - [ ] AC-1.2: SKILL.md with complete skill definition
   - [ ] AC-1.3: HTML/CSS template files for diagram rendering
   - [ ] AC-1.4: Examples showing rendered output

2. **Module View Rendering**
   - [ ] AC-2.1: Horizontal layers with vertical label on left side
   - [ ] AC-2.2: Layer content with title centered (or as per text-align)
   - [ ] AC-2.3: Dashed-border module boxes within layers
   - [ ] AC-2.4: Black pill-shaped component badges
   - [ ] AC-2.5: Icon support for infrastructure components
   - [ ] AC-2.6: virtual-box containers with visual boundaries

3. **Landscape View Rendering**
   - [ ] AC-3.1: Zone containers with labels
   - [ ] AC-3.2: Application boxes with colored backgrounds (green/red/tan by status)
   - [ ] AC-3.3: Status indicator dots (green=healthy, red=critical, orange=warning)
   - [ ] AC-3.4: Database cylinder icons
   - [ ] AC-3.5: Action flow connections with arrow lines
   - [ ] AC-3.6: Action labels on connection lines

4. **Layout Control**
   - [ ] AC-4.1: Apply justify-content styles (flex-start, center, space-between, space-around, space-evenly)
   - [ ] AC-4.2: Apply align-items styles
   - [ ] AC-4.3: Apply flex-direction (row, column)
   - [ ] AC-4.4: Apply gap properties (row-gap, column-gap)
   - [ ] AC-4.5: Apply text-align with inheritance

5. **Export Capabilities**
   - [ ] AC-5.1: Export as PNG image
   - [ ] AC-5.2: Export as SVG vector
   - [ ] AC-5.3: Export as embeddable markdown (```architecture-dsl code block)
   - [ ] AC-5.4: Export as standalone HTML file

6. **Live Preview in X-IPE**
   - [ ] AC-6.1: Render DSL in content viewer (similar to markdown preview)
   - [ ] AC-6.2: Support ```architecture-dsl code blocks in markdown files
   - [ ] AC-6.3: Auto-refresh preview on DSL changes
   - [ ] AC-6.4: White canvas background (matching reference samples)

7. **Integration**
   - [ ] AC-7.1: Configurable via `x-ipe-docs/config/tools.json` under `stages.ideation.ideation.architecture-draw`
   - [ ] AC-7.2: Can be enabled/disabled in Stage Toolbox modal
   - [ ] AC-7.3: Invoked automatically after DSL skill generates output
   - [ ] AC-7.4: Output files saved to idea folder

**Dependencies:**
- FEATURE-015: Architecture DSL Skill (provides DSL input)
- FEATURE-011: Stage Toolbox (for toolbox modal integration)

**Technical Considerations:**
- Use HTML/CSS for rendering (flexbox for layout control)
- Canvas or HTML-to-image for PNG/SVG export
- Match reference diagram styles (Sample 1 & 2 images)
- Support syntax highlighting in code editor view

**Clarifications:**
| Question | Answer |
|----------|--------|
| Export formats? | PNG, SVG, and embed in markdown |
| Live preview? | Yes, render in viewer AND export as files |
| Canvas background? | White (matching reference samples) |

---

### FEATURE-017: Architecture DSL JavaScript Library

**Version:** v1.0  
**Brief Description:** Standalone JavaScript library that parses Architecture DSL and renders diagrams to HTML Canvas. Reusable outside X-IPE as an NPM package. Complements FEATURE-016 (HTML/CSS renderer) with canvas-based rendering.

**Source:** Change Request CR-001 for FEATURE-016  
**Related Features:** [FEATURE-015](FEATURE-015/specification.md) (DSL grammar), [FEATURE-016](FEATURE-016/specification.md) (HTML/CSS renderer)

**Acceptance Criteria:**

1. **Library Structure**
   - [ ] AC-1.1: NPM-compatible package structure with `package.json`
   - [ ] AC-1.2: TypeScript source with type definitions (`.d.ts`)
   - [ ] AC-1.3: ESM and CommonJS build outputs
   - [ ] AC-1.4: Zero runtime dependencies (standalone)
   - [ ] AC-1.5: Minified bundle under 50KB

2. **DSL Parser**
   - [ ] AC-2.1: Parse Architecture DSL following grammar from FEATURE-015
   - [ ] AC-2.2: Support Module View elements (layer, module, component, virtual-box)
   - [ ] AC-2.3: Support Landscape View elements (zone, app, database, flow)
   - [ ] AC-2.4: Support all style properties (justify-content, align-items, text-align, gaps)
   - [ ] AC-2.5: Return structured AST (Abstract Syntax Tree)
   - [ ] AC-2.6: Detailed error messages with line numbers

3. **Canvas Renderer**
   - [ ] AC-3.1: Render Module View diagrams to HTML Canvas
   - [ ] AC-3.2: Render Landscape View diagrams to HTML Canvas
   - [ ] AC-3.3: Apply flexbox-style layout calculations
   - [ ] AC-3.4: Draw layers as horizontal bars with rotated labels
   - [ ] AC-3.5: Draw modules as dashed-border boxes
   - [ ] AC-3.6: Draw components as pill-shaped badges
   - [ ] AC-3.7: Draw zones, apps, databases with appropriate styling
   - [ ] AC-3.8: Draw flow arrows with bezier curves
   - [ ] AC-3.9: Support status colors (healthy, warning, critical)

4. **JavaScript API**
   - [ ] AC-4.1: `parse(dsl: string): AST` - Parse DSL to AST
   - [ ] AC-4.2: `render(ast: AST, canvas: HTMLCanvasElement, options?: RenderOptions): void` - Render to canvas
   - [ ] AC-4.3: `renderToCanvas(dsl: string, canvas: HTMLCanvasElement): void` - Convenience method
   - [ ] AC-4.4: `exportPNG(canvas: HTMLCanvasElement): Blob` - Export as PNG
   - [ ] AC-4.5: `exportSVG(ast: AST): string` - Export as SVG string
   - [ ] AC-4.6: `validate(dsl: string): ValidationResult` - Validate DSL syntax

5. **Rendering Options**
   - [ ] AC-5.1: `scale` - Render scale factor (1x, 2x for retina)
   - [ ] AC-5.2: `padding` - Canvas padding in pixels
   - [ ] AC-5.3: `theme` - Color theme override (optional)
   - [ ] AC-5.4: `fonts` - Font family overrides

6. **Visual Fidelity**
   - [ ] AC-6.1: Match rendering rules from FEATURE-016
   - [ ] AC-6.2: Same colors, spacing, and styling as HTML/CSS renderer
   - [ ] AC-6.3: Crisp text rendering on canvas
   - [ ] AC-6.4: Anti-aliased lines and curves

7. **Documentation**
   - [ ] AC-7.1: README with installation and usage examples
   - [ ] AC-7.2: API reference documentation
   - [ ] AC-7.3: Interactive demo page

**Dependencies:**
- FEATURE-015: Architecture DSL Skill (provides DSL grammar)
- FEATURE-016: Architecture Diagram Renderer (provides visual reference and rendering rules)

**Technical Considerations:**
- Use Canvas 2D API for rendering (not WebGL)
- Implement custom layout engine for flexbox-style calculations
- Text measurement via `ctx.measureText()` for proper sizing
- Arrow routing algorithm for flow connections
- Consider using OffscreenCanvas for better performance

**Clarifications:**
| Question | Answer |
|----------|--------|
| Deployment? | Standalone NPM package, not X-IPE specific |
| Canvas vs HTML/CSS? | Canvas for programmatic use, HTML/CSS in X-IPE skill |
| Browser support? | Modern browsers with Canvas 2D support |
| Node.js support? | Yes, via node-canvas or similar |

---

### FEATURE-018: X-IPE CLI Tool

**Version:** v1.0  
**Brief Description:** Transform X-IPE from a cloned repository into a pip-installable PyPI package with a CLI tool. Provides commands for initializing projects, running the web server, upgrading skills, and checking status.

**Source:** Human request (simplified setup discussion)  
**Mockup:** N/A (CLI tool)

**Acceptance Criteria:**

1. **Package Distribution**
   - [ ] AC-1.1: X-IPE published to PyPI as `x-ipe` package
   - [ ] AC-1.2: Installable via `pip install x-ipe`
   - [ ] AC-1.3: Package includes all skills as package data
   - [ ] AC-1.4: Package includes static files (CSS, JS, templates)
   - [ ] AC-1.5: Version follows semantic versioning

2. **CLI Entry Point**
   - [ ] AC-2.1: `x-ipe` command available after installation
   - [ ] AC-2.2: Help text shows all available commands
   - [ ] AC-2.3: Version flag `x-ipe --version` shows package version
   - [ ] AC-2.4: Uses `click` or `argparse` for CLI parsing

3. **Init Command**
   - [ ] AC-3.1: `x-ipe init` creates project structure in current directory
   - [ ] AC-3.2: Creates `x-ipe-docs/` folder with subfolders (ideas, planning, requirements)
   - [ ] AC-3.3: Creates `.x-ipe/` hidden folder for runtime data (db, cache)
   - [ ] AC-3.4: Creates/merges `.github/` folder with skills and copilot instructions
   - [ ] AC-3.5: Creates `.x-ipe.yaml` config file with sensible defaults
   - [ ] AC-3.6: Auto-detects git repo and updates `.gitignore`
   - [ ] AC-3.7: Adds `.x-ipe/` and `.x-ipe.yaml` to `.gitignore`
   - [ ] AC-3.8: Non-destructive: skips existing files/folders with warning
   - [ ] AC-3.9: Shows summary of created/skipped items

4. **Serve Command**
   - [ ] AC-4.1: `x-ipe serve` starts web server in current directory
   - [ ] AC-4.2: `--port` flag to specify port (default: 5000)
   - [ ] AC-4.3: `--open` flag to auto-open browser
   - [ ] AC-4.4: Server finds and uses `.x-ipe.yaml` if present
   - [ ] AC-4.5: Falls back to sensible defaults without config
   - [ ] AC-4.6: Hot reload for development (optional flag)

5. **Upgrade Command**
   - [ ] AC-5.1: `x-ipe upgrade` updates skills from package
   - [ ] AC-5.2: Detects local skill modifications before overwriting
   - [ ] AC-5.3: `--force` flag to overwrite local changes
   - [ ] AC-5.4: Creates backup of modified skills before upgrade
   - [ ] AC-5.5: Updates `.github/` copilot instructions

6. **Status Command**
   - [ ] AC-6.1: `x-ipe status` shows project X-IPE status
   - [ ] AC-6.2: Shows if project is initialized
   - [ ] AC-6.3: Shows skills count (package vs local)
   - [ ] AC-6.4: Shows server status if running

7. **Info Command**
   - [ ] AC-7.1: `x-ipe info` shows detailed diagnostics
   - [ ] AC-7.2: Shows package version
   - [ ] AC-7.3: Shows Python version and environment
   - [ ] AC-7.4: Shows config file location and contents
   - [ ] AC-7.5: Shows paths (skills, docs, .x-ipe folder)

**Dependencies:**
- None (this is the foundation)

**Technical Considerations:**
- Use `pyproject.toml` for package configuration
- Include `[project.scripts]` for CLI entry point
- Use `importlib.resources` for accessing package data
- Consider `click` library for CLI (cleaner than argparse)

**Clarifications:**
| Question | Answer |
|----------|--------|
| Installation method? | pip install x-ipe (PyPI) |
| CLI framework? | click or argparse |
| Package name? | x-ipe |
| Minimum Python? | 3.10+ |

---

### FEATURE-019: Simplified Project Setup

**Version:** v1.0  
**Brief Description:** The `x-ipe init` command creates a complete project structure with docs folders, hidden .x-ipe runtime folder, and merged .github configuration.

**Source:** Human request (simplified setup discussion)  
**Mockup:** N/A

**Acceptance Criteria:**

1. **Docs Folder Structure**
   - [ ] AC-1.1: Creates `x-ipe-docs/ideas/` folder
   - [ ] AC-1.2: Creates `x-ipe-docs/planning/` folder with empty `task-board.md`
   - [ ] AC-1.3: Creates `x-ipe-docs/requirements/` folder
   - [ ] AC-1.4: Creates `x-ipe-docs/themes/` folder with `theme-default/`
   - [ ] AC-1.5: All docs folders are version-controlled (not gitignored)

2. **Runtime Folder (.x-ipe/)**
   - [ ] AC-2.1: Creates `.x-ipe/` hidden folder
   - [ ] AC-2.2: Stores `settings.db` in `.x-ipe/`
   - [ ] AC-2.3: Stores session data in `.x-ipe/sessions/`
   - [ ] AC-2.4: Stores cache in `.x-ipe/cache/`
   - [ ] AC-2.5: Entire `.x-ipe/` folder gitignored

3. **GitHub Configuration**
   - [ ] AC-3.1: Creates `.github/skills/` with skills from package
   - [ ] AC-3.2: Merges with existing `.github/` if present (non-destructive)
   - [ ] AC-3.3: Copies copilot instructions to `.github/copilot-instructions.md`
   - [ ] AC-3.4: Skills are copied (not symlinked) for portability
   - [ ] AC-3.5: Local skills override package skills by name

4. **Configuration File**
   - [ ] AC-4.1: Creates `.x-ipe.yaml` with default configuration
   - [ ] AC-4.2: Default paths point to current directory structure
   - [ ] AC-4.3: Config file is gitignored (project-specific settings)

5. **Git Integration**
   - [ ] AC-5.1: Detects if current directory is a git repository
   - [ ] AC-5.2: Creates/updates `.gitignore` with X-IPE patterns
   - [ ] AC-5.3: Gitignore includes: `.x-ipe/`, `.x-ipe.yaml`
   - [ ] AC-5.4: Does NOT gitignore `x-ipe-docs/` or `.github/skills/`

**Dependencies:**
- FEATURE-018: X-IPE CLI Tool (provides the `x-ipe` command)

**Technical Considerations:**
- Use `shutil.copytree` for folder copying with ignore patterns
- Check for existing files before overwriting
- Provide `--dry-run` flag to preview changes

**Clarifications:**
| Question | Answer |
|----------|--------|
| Overwrite existing files? | No, skip with warning |
| x-ipe-docs/ location? | Project root (visible, version controlled) |
| .x-ipe/ location? | Project root (hidden, gitignored) |
| Skills copied or linked? | Copied for portability |

---

### FEATURE-020: Skills Discovery & Override

**Version:** v1.0  
**Brief Description:** Skills are loaded from the installed X-IPE package by default, but local skills in `.github/skills/` take precedence, allowing project-specific customization.

**Source:** Human request (simplified setup discussion)  
**Mockup:** N/A

**Acceptance Criteria:**

1. **Package Skills Discovery**
   - [ ] AC-1.1: Skills bundled in X-IPE package at install time
   - [ ] AC-1.2: Package skills accessible via `importlib.resources`
   - [ ] AC-1.3: SkillsService discovers package skills automatically
   - [ ] AC-1.4: Package skills read-only (not modified at runtime)

2. **Local Skills Override**
   - [ ] AC-2.1: Local skills in `.github/skills/` discovered
   - [ ] AC-2.2: Local skill with same name overrides package skill
   - [ ] AC-2.3: Override is by skill folder name (e.g., `task-type-bug-fix`)
   - [ ] AC-2.4: Partial override: local skill completely replaces package skill

3. **Skills Merge Logic**
   - [ ] AC-3.1: Final skills list = package skills + local-only skills - overridden
   - [ ] AC-3.2: API endpoint shows skill source (package vs local)
   - [ ] AC-3.3: `x-ipe status` shows skills breakdown

4. **Skills Upgrade**
   - [ ] AC-4.1: `x-ipe upgrade` syncs package skills to local
   - [ ] AC-4.2: Detects modified local skills (hash comparison)
   - [ ] AC-4.3: Prompts before overwriting modified skills
   - [ ] AC-4.4: `--force` flag overwrites without prompt
   - [ ] AC-4.5: Creates `.x-ipe/backups/skills-{timestamp}/` before upgrade

**Dependencies:**
- FEATURE-018: X-IPE CLI Tool
- FEATURE-019: Simplified Project Setup

**Technical Considerations:**
- Use file hashes (SHA-256) to detect local modifications
- Store original package skill hashes in `.x-ipe/skill-hashes.json`
- Consider lazy loading skills for performance

**Clarifications:**
| Question | Answer |
|----------|--------|
| Override granularity? | Entire skill folder, not individual files |
| New skills in package? | Auto-discovered, no init needed |
| Deleted package skills? | Local copy remains until manually deleted |
