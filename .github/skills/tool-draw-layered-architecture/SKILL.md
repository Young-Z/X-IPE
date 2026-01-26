---
name: tool-draw-layered-architecture
description: Render layered architecture diagrams (Module View) from Architecture DSL definitions. Default style is corporate. Integrates with X-IPE theme system.
---

# Layered Architecture Diagram Renderer

Transforms Architecture DSL `module-view` code into self-contained HTML diagrams.

## Quick Reference

| Input | Output | View Type | Default Style |
|-------|--------|-----------|---------------|
| `architecture-dsl` code block | Self-contained HTML file | `module-view` | `corporate` |

## Available Styles

| Style | Template | Default |
|-------|----------|---------|
| `corporate` | `module-view-corporate.html` | ✅ Yes |
| `default` | `module-view.html` | No |

---

## ⚠️ CRITICAL RULES

### 1. Always Use Corporate Style
**DEFAULT TEMPLATE: `templates/module-view-corporate.html`**

⛔ NEVER use `module-view.html` unless DSL explicitly contains `style "default"`

### 2. No Invention Rule
You MUST NOT add any content that doesn't exist in the DSL:
- ❌ Do NOT invent layer headers/titles
- ❌ Do NOT add extra components
- ❌ Do NOT add tooltips/descriptions
- ❌ Do NOT add classes/variants not specified by stereotypes

### 3. Required From DSL
You MUST include these elements when specified:
- ✅ `title "..."` → `<h1 class="diagram-title">...</h1>` at top
- ✅ `layer "..."` → Layer with side label
- ✅ `module "..."` → Module with title
- ✅ `component "..."` → Component with text

### 4. DSL-to-HTML Property Verification
After generating HTML, verify EACH property matches exactly:

| DSL Property | HTML Attribute |
|--------------|----------------|
| `cols N` | `class="cols-N"` |
| `rows N` | `class="rows-N"` |
| `grid C x R` | `class="grid-CxR"` |
| `component "Name"` | Text content |
| `<<stereotype>>` | `data-stereotype` or variant class |

### 5. Component Variant Rules
Default class is `component`. Only use variants when DSL specifies:

| DSL Stereotype | HTML Class |
|----------------|------------|
| `<<icon>>`, `<<folder>>`, `<<file>>`, `<<db>>` | `component-icon` |
| `<<full>>` | `component component-full` |
| `<<highlight>>` | `component component-highlight` |
| (none) | `component` |

---

## Execution Workflow

### Step 1: Parse DSL
Extract from DSL:
- `title` → Diagram title
- `style` → Template selection (default: corporate)
- `theme` → Design tokens (default: theme-default)
- Structure: Layers → Modules → Components

### Step 2: Load Theme
```bash
cat "x-ipe-docs/themes/${theme_name}/design-system.md"
```

### Step 3: Generate HTML
Apply DSL values to template. See [references/dsl-to-css.md](references/dsl-to-css.md).

### Step 4: Verify
Check every `cols`, `rows`, `grid` value matches DSL exactly.

### Step 5: Save Output
Save to specified path or same directory as DSL with `.html` extension.

---

## Grid System

| Level | Rule |
|-------|------|
| Document | `grid 12 x N` (12 columns fixed) |
| Layer | Full width, `rows N` for height |
| Module | `cols N` must sum to 12 per layer |
| Component | Positioned in module's `grid C x R` |

---

## Corporate Style Colors

**⚠️ CRITICAL: Corporate style ignores DSL color properties**

| Element | Color | Note |
|---------|-------|------|
| Layer BG | `#ffffff` | Always white |
| Layer BG Highlight | `#eff6ff` | Use `.layer-highlight` class |
| Border | `#374151` | Gray border |
| Badge BG | `#1f2937` | Dark gray |
| Badge Text | `#ffffff` | White text |

> DSL properties `color` and `border-color` are IGNORED when using corporate style. They only apply with `style "default"`.

---

## Resources

| Folder | Purpose |
|--------|---------|
| [templates/](templates/) | HTML templates |
| [examples/](examples/) | DSL → HTML examples |
| [references/](references/) | Grid system, DSL-to-CSS mapping |

## See Also

- [tool-architecture-dsl](../tool-architecture-dsl/SKILL.md) - DSL syntax
- [tool-draw-system-landscape](../tool-draw-system-landscape/SKILL.md) - Landscape diagrams
