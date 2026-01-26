---
name: tool-draw-system-landscape
description: Render system landscape diagrams (Landscape View) from Architecture DSL definitions. Creates self-contained HTML visualizations showing application integration maps with zones, apps, databases, and action flows. Integrates with X-IPE theme system for brand consistency.
---

# System Landscape Diagram Renderer

Transforms Architecture DSL `landscape-view` code into production-grade, self-contained HTML diagrams for application integration maps.

## Quick Reference

| Input | Output | View Type |
|-------|--------|-----------|
| `architecture-dsl` code block | Self-contained HTML file | `landscape-view` |

## Skill Resources

| Folder | Purpose |
|--------|---------|
| [templates/](templates/) | HTML base template for landscape view |
| [examples/](examples/) | Complete DSL → HTML rendering examples |
| [references/](references/) | DSL-to-CSS mapping for landscape elements |

---

## Execution Workflow

### Step 1: Extract Theme from DSL

Parse the `theme` property from the DSL document:

```architecture-dsl
@startuml landscape-view
title "Enterprise Landscape"
theme "theme-default"    ← Extract this value
...
```

**Theme Resolution:**
1. If `theme "{name}"` is specified → Use `x-ipe-docs/themes/{name}/design-system.md`
2. If no theme specified → Default to `x-ipe-docs/themes/theme-default/design-system.md`

### Step 2: Load Theme Tokens

Read theme tokens from the theme's design-system.md:

```bash
# theme_name extracted from DSL (e.g., "theme-default")
cat "x-ipe-docs/themes/${theme_name}/design-system.md"
```

**Required tokens:**
- `--color-primary`: Zone titles, app names
- `--color-secondary`: Subtitles, meta text
- `--color-accent`: Highlights, flow arrows
- `--color-neutral`: Backgrounds, borders
- `--font-heading`: Zone/app titles
- `--font-body`: Meta text

### Step 3: Identify View Type

Parse `@startuml` header:
- `@startuml landscape-view` → Use `templates/landscape-view.html`

> **Note:** For module-view diagrams, use the `tool-draw-layered-architecture` skill instead.

### Step 4: Parse DSL Structure

Extract hierarchical structure:
- **Landscape View**: Document → Zones → Apps/Databases → Flows

### Step 5: Extract Elements

#### Zones
- Zone name and title
- Contained apps and databases

#### Apps
- Alias (id attribute)
- Display name
- Tech stack
- Platform
- Status (healthy/warning/critical)

#### Databases
- Alias (id attribute)
- Display name

#### Flows
- Source alias
- Target alias
- Action label

### Step 6: Generate HTML

Apply parsed values to the landscape template. See [references/landscape-mapping.md](references/landscape-mapping.md) for mapping rules.

### Step 7: Save Output

```
x-ipe-docs/requirements/FEATURE-XXX/architecture/   ← Feature architecture
playground/architecture/                       ← Standalone diagrams
x-ipe-docs/ideas/idea-XXX/architecture/              ← Idea exploration
```

---

## Element Styling

### Zone Styles

Zones are container sections that group related applications and databases.

```css
.zone {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
}
```

### App Styles

Apps represent applications with tech stack, platform, and health status.

```css
.app {
    background: #f8fafc;
    border-radius: 8px;
    padding: 16px;
    min-width: 160px;
    border: 1px solid #e2e8f0;
}
```

### Status Indicators

| Status | Color | Effect |
|--------|-------|--------|
| `healthy` | `#22c55e` | Green glow |
| `warning` | `#f97316` | Orange glow |
| `critical` | `#ef4444` | Red glow + pulse animation |

### Database Styles

Databases have a distinct visual treatment to differentiate from apps.

```css
.database {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border-radius: 8px;
    border: 2px solid #0ea5e9;
    text-align: center;
}
```

### Flow Styles

Flows show action relationships between applications.

```css
.flow {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f8fafc;
    border-radius: 6px;
}
```

---

## Validation Checklist

Before rendering, verify:

1. **Zone Structure**: All apps/databases belong to a zone
2. **Unique Aliases**: All app and database aliases are unique
3. **Valid Flows**: Flow sources and targets reference existing aliases
4. **Theme Loaded**: Design system tokens extracted

---

## See Also

- [tool-architecture-dsl](../tool-architecture-dsl/SKILL.md) - DSL syntax reference
- [tool-draw-layered-architecture](../tool-draw-layered-architecture/SKILL.md) - Module view diagrams
- [tool-frontend-design](../tool-frontend-design/SKILL.md) - Creative frontend design
- [theme-factory](../theme-factory/SKILL.md) - Theme management
