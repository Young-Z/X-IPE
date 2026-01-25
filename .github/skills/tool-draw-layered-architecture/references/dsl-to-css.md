# DSL to CSS Mapping

Complete mapping of Architecture DSL properties to CSS implementation.

---

## Module View Mappings

### Document Level

| DSL | CSS Target | CSS Property |
|-----|------------|--------------|
| `title "Name"` | `.diagram-title` | `textContent = "Name"` |
| `direction top-to-bottom` | `.diagram-content` | `grid-auto-flow: row` (default) |
| `direction left-to-right` | `.diagram-content` | `grid-auto-flow: column` |
| `grid 12 x N` | `.diagram-content` | `grid-template-rows: repeat(N, auto)` |

### Layer Level

| DSL | CSS Target | CSS Property |
|-----|------------|--------------|
| `layer "Name"` | `.layer` | `data-label="Name"` |
| `rows N` | `.layer` | `grid-row: span N` |
| `color "#hex"` | `.layer` | `background: #hex` |
| `border-color "#hex"` | `.layer` | `border: 2px solid #hex` |
| `text-align center` | `.layer` | `text-align: center` |

### Module Level

| DSL | CSS Target | CSS Property |
|-----|------------|--------------|
| `module "Name"` | `.module` | Element with `.module-title = "Name"` |
| `cols N` | `.module` | `grid-column: span N` |
| `rows N` | `.module` | `grid-row: span N` |
| `grid C x R` | `.module-content` | `grid-template-columns: repeat(C, 1fr); grid-template-rows: repeat(R, 1fr)` |
| `align H V` | `.module-content` | See alignment table below |
| `gap Npx` | `.module-content` | `gap: Npx` |

### Alignment Values

| DSL `align` | CSS `justify-items` | CSS `align-items` |
|-------------|--------------------|--------------------|
| `left top` | `start` | `start` |
| `left center` | `start` | `center` |
| `left bottom` | `start` | `end` |
| `center top` | `center` | `start` |
| `center center` | `center` | `center` |
| `center bottom` | `center` | `end` |
| `right top` | `end` | `start` |
| `right center` | `end` | `center` |
| `right bottom` | `end` | `end` |

### Component Level

| DSL | CSS Target | CSS Property |
|-----|------------|--------------|
| `component "Name"` | `.component` | `textContent = "Name"` |
| `cols N` | `.component` | `grid-column: span N` |
| `rows N` | `.component` | `grid-row: span N` |
| `<<stereotype>>` | `.component` | `data-stereotype="stereotype"` |

---

## Color Mappings

### Style-Specific Behavior

**Corporate Style (default):**
- ⛔ Do NOT use layer-specific colors
- ✅ All layers use `#ffffff` background with `#374151` border
- ✅ Use `layer-highlight` class for emphasis (gives subtle `#eff6ff` blue tint)
- ✅ DSL `color` and `border-color` properties are IGNORED in corporate style

**Default Style (non-corporate):**
The renderer may detect layer type from the name and apply colors:

| Layer Name Contains | Background | Border |
|--------------------|------------|--------|
| "presentation", "ui", "frontend", "view" | `#fce7f3` | `#ec4899` |
| "service", "api", "gateway" | `#fef3c7` | `#f97316` |
| "business", "domain", "logic", "core" | `#dbeafe` | `#3b82f6` |
| "data", "persistence", "storage", "db" | `#dcfce7` | `#22c55e` |
| "infrastructure", "infra", "platform" | `#f3e8ff` | `#a855f7` |

> **Note:** Color auto-detection only applies when using `style "default"` template.

---

## Theme Token Integration

When a theme is loaded, map these design-system.md tokens:

| Theme Token | CSS Variable | Usage |
|-------------|--------------|-------|
| Primary color | `--color-primary` | Layer titles, primary text |
| Secondary color | `--color-secondary` | Subtitles, labels |
| Accent color | `--color-accent` | Highlights |
| Neutral color | `--color-neutral` | Component backgrounds |
| Heading font | `--font-heading` | Titles, module names |
| Body font | `--font-body` | Component text |

---

## HTML Element Generation

### Layer HTML
```html
<div class="layer layer-{type}" data-label="{name}" style="grid-row: span {rows}; background: {color}; border: 2px solid {border-color};">
    <!-- modules -->
</div>
```

### Module HTML
```html
<div class="module" style="grid-column: span {cols};">
    <h3 class="module-title">{name}</h3>
    <div class="module-content" style="grid-template-columns: repeat({gridC}, 1fr); grid-template-rows: repeat({gridR}, 1fr); gap: {gap};">
        <!-- components -->
    </div>
</div>
```

### Component HTML
```html
<div class="component" style="grid-column: span {cols}; grid-row: span {rows};" data-stereotype="{stereotype}">
    {name}
</div>
```

> **Note:** For landscape view HTML generation (apps, databases, flows), see the `tool-draw-system-landscape` skill.
