# Feature Specification: Architecture Diagram Renderer

> Feature ID: FEATURE-016  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-24-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.1 | 01-24-2026 | CR-001: JS Library for Canvas rendering → spawned FEATURE-017 | [CR-001](./CR-001.md) |
| v1.0 | 01-24-2026 | Initial specification | - |

---

## Overview

The Architecture Diagram Renderer is a tool skill that takes Architecture DSL definitions (produced by FEATURE-015) and renders them as visual HTML diagrams. It produces pixel-perfect, publication-quality architecture diagrams with support for both Module View and Application Landscape View.

The renderer uses HTML/CSS with Flexbox for layout control, producing diagrams that can be:
1. Previewed live in the X-IPE content viewer
2. Exported as PNG images
3. Exported as SVG vectors
4. Embedded in markdown documents
5. Saved as standalone HTML files

This skill completes the architecture design workflow: natural language → DSL → visual diagram.

---

## User Stories

### US-1: DSL to Visual Diagram
As an **AI agent**, I want to **render Architecture DSL as visual diagrams**, so that **I can produce professional architecture documentation**.

### US-2: Live Preview in X-IPE
As an **architect**, I want to **see my DSL render in real-time as I edit**, so that **I can iterate quickly on diagram layout**.

### US-3: Export Diagrams
As a **user**, I want to **export diagrams in multiple formats (PNG, SVG, HTML)**, so that **I can include them in presentations and documentation**.

### US-4: Layout Control Rendering
As an **architect**, I want to **see my flexbox-style layout properties reflected visually**, so that **I can fine-tune component arrangement**.

### US-5: Markdown Embedding
As a **documentation author**, I want to **embed architecture diagrams in markdown files using code blocks**, so that **I can keep diagrams alongside my documentation**.

---

## Acceptance Criteria

### 1. Skill Structure
- [x] AC-1.1: Skill folder exists at `.github/skills/tool-architecture-draw/`
- [x] AC-1.2: SKILL.md contains complete skill definition with purpose, workflow, and examples
- [x] AC-1.3: HTML/CSS template files included at `templates/` folder
- [x] AC-1.4: Example rendered outputs at `examples/` folder
- [x] AC-1.5: References grammar from FEATURE-015 skill

### 2. DSL Parsing
- [x] AC-2.1: Parse `@startuml <view-type>` to determine Module View vs Landscape View
- [x] AC-2.2: Parse `title` property and render as diagram header
- [x] AC-2.3: Parse `direction` property (top-to-bottom, left-to-right)
- [x] AC-2.4: Ignore comments (`'` and `/' ... '/`)
- [x] AC-2.5: Report clear error messages for invalid DSL syntax
- [x] AC-2.6: Parse `text-align` property with inheritance (top → layer → module)

### 3. Module View Rendering
- [x] AC-3.1: Render `layer` as horizontal bar with vertical label on left side
- [x] AC-3.2: Layer label uses black background, white text, rotated 180°
- [x] AC-3.3: Render layer content area with padding
- [x] AC-3.4: Layer title centered (or per `text-align` property)
- [x] AC-3.5: Render `module` as dashed-border box within layer
- [x] AC-3.6: Module title rendered at top of box
- [x] AC-3.7: Render `component` as black pill-shaped badge
- [x] AC-3.8: Render `component <<stereotype>>` with icon/badge indicator
- [x] AC-3.9: Render `virtual-box` as light purple container with visual boundary
- [x] AC-3.10: Multiple `virtual-box` elements stack vertically
- [x] AC-3.11: Support nested structure: Layer → Module → Component (3 levels max)

### 4. Landscape View Rendering
- [x] AC-4.1: Render `zone` as labeled container section
- [x] AC-4.2: Render `app` as rectangular box with metadata
- [x] AC-4.3: App box shows: name, tech, platform (when provided)
- [x] AC-4.4: Render status indicator dot on app box (green=healthy, orange=warning, red=critical)
- [x] AC-4.5: Render `database` as cylinder icon
- [x] AC-4.6: Render action flow arrows (`-->`) between elements
- [x] AC-4.7: Flow arrow labels displayed on or near the line
- [x] AC-4.8: Arrow routing avoids overlapping where possible

### 5. Layout Control (Flexbox-inspired)
- [x] AC-5.1: Apply `justify-content` to container (flex-start, flex-end, center, space-between, space-around, space-evenly)
- [x] AC-5.2: Apply `align-items` to container (flex-start, flex-end, center, stretch, baseline)
- [x] AC-5.3: Apply `flex-direction` to container (row, row-reverse, column, column-reverse)
- [x] AC-5.4: Apply `row-gap` spacing between rows
- [x] AC-5.5: Apply `column-gap` spacing between columns
- [x] AC-5.6: Apply `text-align` with inheritance (top-level → layer → module)
- [x] AC-5.7: Default values when style not specified (flex-start, stretch, row, 8px gaps)

### 6. Visual Styling
- [x] AC-6.1: White canvas background (#ffffff)
- [x] AC-6.2: Layer border: 2px solid black (#1a1a1a)
- [x] AC-6.3: Module border: 2px dashed gray (#999)
- [x] AC-6.4: Component badge: black background, white text, rounded pill shape
- [x] AC-6.5: Virtual-box: light purple border (#e0e7ff), subtle fill
- [x] AC-6.6: Consistent typography using system fonts (fallback to DM Sans, JetBrains Mono)
- [x] AC-6.7: Proper spacing and padding throughout

### 7. Export Capabilities
- [x] AC-7.1: Export as PNG image (html2canvas or similar)
- [x] AC-7.2: Export as SVG vector
- [x] AC-7.3: Export as standalone HTML file (self-contained, no external deps except CDN fonts)
- [x] AC-7.4: Export DSL as embeddable markdown (```architecture-dsl code block)
- [ ] AC-7.5: Export button visible in preview panel header (deferred - X-IPE integration)

### 8. Live Preview in X-IPE
- [ ] AC-8.1: Render `architecture-dsl` code blocks in markdown preview (deferred - X-IPE integration)
- [ ] AC-8.2: Auto-refresh preview when DSL changes (debounced) (deferred - X-IPE integration)
- [ ] AC-8.3: Show loading indicator during render (deferred - X-IPE integration)
- [ ] AC-8.4: Show error overlay for invalid DSL (with error message) (deferred - X-IPE integration)
- [ ] AC-8.5: Support `.dsl` file extension for standalone DSL files (deferred - X-IPE integration)

### 9. Integration
- [x] AC-9.1: Skill registered in `x-ipe-docs/config/tools.json` under `stages.ideation.ideation.tool-architecture-draw`
- [x] AC-9.2: Can be enabled/disabled via Stage Toolbox modal
- [x] AC-9.3: Works alongside `tool-architecture-dsl` skill
- [x] AC-9.4: Output files can be saved to idea folder

---

## Functional Requirements

### FR-1: DSL Parser

**Description:** Parse Architecture DSL text into a structured representation.

**Details:**
- Input: Raw DSL text string
- Process: Tokenize and parse according to grammar from FEATURE-015
- Output: Abstract Syntax Tree (AST) or error with line number

**Parser Output Structure:**
```javascript
{
  viewType: "module-view" | "landscape-view",
  title: "string",
  direction: "top-to-bottom" | "left-to-right",
  textAlign: "left" | "center" | "right",
  elements: [
    { type: "layer", name: "...", alias: "...", style: {...}, textAlign: "...", children: [...] },
    { type: "zone", name: "...", style: {...}, children: [...] },
    { type: "flow", source: "...", target: "...", label: "..." }
  ]
}
```

### FR-2: Module View Renderer

**Description:** Render Module View AST as HTML/CSS.

**Details:**
- Input: Parsed AST with viewType "module-view"
- Process: Generate HTML elements with CSS classes
- Output: HTML string or DOM fragment

**Visual Elements:**
| DSL Element | HTML Rendering |
|-------------|----------------|
| `layer` | `<div class="arch-layer">` with label + content |
| `module` | `<div class="module-box">` with dashed border |
| `component` | `<span class="component-badge">` pill shape |
| `virtual-box` | `<div class="virtual-box">` with light border |

### FR-3: Landscape View Renderer

**Description:** Render Landscape View AST as HTML/CSS/SVG.

**Details:**
- Input: Parsed AST with viewType "landscape-view"
- Process: Generate HTML for zones/apps, SVG for flow arrows
- Output: HTML + embedded SVG

**Visual Elements:**
| DSL Element | HTML Rendering |
|-------------|----------------|
| `zone` | `<div class="zone-container">` |
| `app` | `<div class="app-box">` with status dot |
| `database` | `<div class="db-cylinder">` or SVG cylinder |
| `flow` | `<svg><path>` with arrowhead marker |

### FR-4: Export Engine

**Description:** Export rendered diagram to various formats.

**Details:**
- Input: Rendered HTML element
- Process: Convert to target format using appropriate library
- Output: File blob (PNG/SVG) or text (HTML/Markdown)

**Export Methods:**
| Format | Method |
|--------|--------|
| PNG | html2canvas → canvas.toBlob() |
| SVG | DOM serialization or html-to-image |
| HTML | Full HTML document with embedded CSS |
| Markdown | Original DSL in code fence |

### FR-5: Preview Integration

**Description:** Integrate diagram rendering into X-IPE content viewer.

**Details:**
- Input: Markdown with ```architecture-dsl code blocks OR .dsl file
- Process: Detect code blocks, parse DSL, render inline
- Output: Live diagram in content viewer

---

## Non-Functional Requirements

### NFR-1: Performance

- Render diagrams under 500ms for typical complexity (< 50 elements)
- Debounce preview updates (300ms) during editing
- Lazy-load export libraries only when export requested

### NFR-2: Browser Compatibility

- Support modern browsers (Chrome, Firefox, Safari, Edge)
- Fallback gracefully if html2canvas not available
- No IE11 support required

### NFR-3: Accessibility

- Diagrams should have meaningful alt text
- Color should not be the only indicator (use shapes/text too)
- Export to SVG preserves text as text (not rasterized)

---

## Dependencies

### Internal Dependencies

| Feature | Why Needed | Status |
|---------|------------|--------|
| FEATURE-015 | Provides DSL grammar and skill for DSL generation | Completed |
| FEATURE-011 | Stage Toolbox for tool enable/disable | Completed |

### External Dependencies

| Library | Purpose | Note |
|---------|---------|------|
| html2canvas | PNG export | Load on-demand |
| (optional) html-to-image | Alternative export | Lighter weight |

---

## Business Rules

### BR-1: View Type Detection

**Rule:** Renderer must determine view type from `@startuml` declaration.

**Values:**
- `@startuml module-view` → Module View renderer
- `@startuml landscape-view` → Landscape View renderer

### BR-2: Style Inheritance

**Rule:** `text-align` inherits from parent to child if not explicitly set.

**Inheritance Chain:** Document → Layer → Module

### BR-3: Default Styles

**Rule:** When `style` property is not specified, use defaults.

| Property | Default |
|----------|---------|
| justify-content | flex-start |
| align-items | stretch |
| flex-direction | row |
| row-gap | 8px |
| column-gap | 8px |
| text-align | center |

### BR-4: Status Colors

**Rule:** Status indicator colors must use consistent semantic mapping.

| Status | Color | Hex |
|--------|-------|-----|
| healthy | Green | #22c55e |
| warning | Orange | #f97316 |
| critical | Red | #ef4444 |

---

## Edge Cases & Constraints

### Edge Case 1: Empty DSL

**Scenario:** User provides DSL with only `@startuml` / `@enduml` and no elements.  
**Expected Behavior:** Render empty white canvas with title (if provided) or placeholder text "No elements defined".

### Edge Case 2: Invalid DSL Syntax

**Scenario:** DSL contains syntax errors (missing closing brace, invalid keywords).  
**Expected Behavior:** Display error overlay with clear message and line number where possible.

### Edge Case 3: Very Large Diagrams

**Scenario:** DSL defines 100+ components across many layers.  
**Expected Behavior:** Render with scrolling enabled. Export may be slow but should complete. Warn user if export might fail.

### Edge Case 4: Missing Aliases in Flows

**Scenario:** Flow references an alias that doesn't exist in the DSL.  
**Expected Behavior:** Highlight invalid flow in red, show warning tooltip "Unknown target: {alias}".

### Edge Case 5: Circular Flows

**Scenario:** A → B → A (bidirectional flow).  
**Expected Behavior:** Render both arrows. Offset lines slightly to avoid overlap.

### Edge Case 6: Long Labels

**Scenario:** Component or app name is very long (50+ characters).  
**Expected Behavior:** Truncate with ellipsis, full name on hover tooltip.

---

## Out of Scope

- Interactive editing on canvas (click-to-add components)
- Real-time collaboration
- Animation or transitions
- Sequence diagrams, flow charts, or other diagram types
- Custom themes/color schemes (uses fixed styling v1)
- PDF export (v1 focuses on PNG/SVG/HTML)

---

## Technical Considerations

### Rendering Approach

Use HTML/CSS with Flexbox rather than Canvas API because:
1. Easier to implement and debug
2. Text remains selectable/searchable
3. CSS handles layout automatically
4. Better accessibility
5. Simpler export to HTML

### Arrow Drawing (Landscape View)

For flow arrows between apps, consider:
- SVG overlay positioned absolutely
- Calculate start/end points based on element positions
- Use cubic bezier curves for smooth routing
- Add arrowhead markers

### File Structure (Skill)

```
.github/skills/tool-architecture-draw/
├── SKILL.md                 # Main skill definition
├── templates/
│   ├── module-view.html     # HTML template for module diagrams
│   ├── landscape-view.html  # HTML template for landscape diagrams
│   └── base-styles.css      # Shared CSS styles
├── examples/
│   ├── module-view-rendered.html
│   └── landscape-view-rendered.html
└── references/
    └── rendering-rules.md   # Detailed rendering specifications
```

### X-IPE Integration Points

1. **Content Viewer**: Extend markdown renderer to detect `architecture-dsl` blocks
2. **File Service**: Register `.dsl` as renderable file type
3. **Export UI**: Add export dropdown to preview panel header

---

## Open Questions

- [x] Q1: Should arrows use straight lines or curved paths? → **Curved** (cubic bezier for cleaner look)
- [x] Q2: How to handle overlapping arrows? → **Offset parallel lines slightly**
- [ ] Q3: Maximum diagram size before warning? → Need to determine during implementation
- [ ] Q4: Should export include original DSL as HTML comment? → Useful for round-trip editing

---

## Mockup Reference

**Linked Mockup:** [architecture-diagram-renderer.html](mockups/architecture-diagram-renderer.html)

The mockup demonstrates:
- Module View with 3 layers (AI Application, AI Model, Infrastructure)
- Virtual-box grouping in AI Model layer
- Flexbox layout properties (justify-content, column-gap)
- Text-align inheritance
- Component badges with stereotypes
- Landscape View with zones, apps, databases, and action flows
- Status indicators (healthy, warning, critical)
- White canvas background
- Export buttons (PNG, SVG, Copy DSL)
