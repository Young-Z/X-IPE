# Idea Summary: Themes for Design System

> **Version**: v1  
> **Date**: 2026-01-24  
> **Status**: Refined  
> **Refined by**: Bolt

---

## Executive Summary

A **theming system** for X-IPE that enables brands to define unified design systems (colors, typography, spacing) and apply them consistently when designing mockups for new features. Themes are stored as structured files, selectable via the toolbox UI, and consumed by a new `tool-frontend-design` skill.

---

## Problem Statement

When designing mockups for different brands or projects, there's no centralized way to:
1. Define and reuse brand design tokens (colors, fonts, spacing)
2. Ensure consistency across multiple feature mockups
3. Guide AI-assisted frontend design with brand-specific constraints

---

## Proposed Solution

### 1. Theme Folder Structure

```
x-ipe-docs/themes/
├── theme-default/           # Ships with X-IPE
│   ├── design-system.md     # Core tokens + optional component specs
│   └── component-visualization.html  # Visual + structured data
├── theme-{brand-name}/
│   ├── design-system.md
│   └── component-visualization.html
└── ...
```

### 2. Theme File Contents

#### `design-system.md` (Required Sections)
- **Core Tokens (mandatory)**:
  - Color palette (primary, secondary, accent, neutrals, semantic)
  - Typography scale (font families, sizes, weights, line heights)
  - Spacing tokens (base unit, scale)
- **Component Specs (optional)**:
  - Button variants, form elements, cards, etc.
- **Usage Guidelines (optional)**:
  - When to use which colors, accessibility notes

#### `component-visualization.html`
- **Dual-purpose file**:
  - Visual HTML for humans to preview design tokens
  - Structured data (JSON-LD or data attributes) for AI to parse programmatically

### 3. UI Integration

#### Sidebar
- **Themes menu** pointing to `x-ipe-docs/themes/` folder
- Shows available themes as navigable items

#### Toolbox Modal
- **Themes section** at the top of modal
- **Visual theme cards** with preview thumbnails
- Selection saved to `x-ipe-docs/config/tools.json` (reusing existing toolbox config pattern)
- Theme applies to current idea (per-idea persistence)

### 4. New Skill: `tool-frontend-design`

- **Purpose**: Theme-aware frontend design skill
- **Behavior**: Reads selected theme from `x-ipe-docs/config/tools.json`, loads `design-system.md` and `component-visualization.html`, applies tokens to generated designs
- **Relationship**: Separate from existing `frontend-design` skill (keeps original intact)

---

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US-1 | Designer | Define a theme with my brand's design tokens | All mockups follow our brand guidelines |
| US-2 | Developer | Select a theme in the toolbox | AI uses consistent styling for my project |
| US-3 | User | See a visual preview of theme colors/fonts | I can quickly identify and select the right theme |
| US-4 | AI Agent | Read structured design data from theme files | I can generate accurate, branded mockups |

---

## Scope

### In Scope (v1)
- Theme folder structure and naming convention
- `design-system.md` template with core tokens (mandatory) + optional sections
- `component-visualization.html` with visual + structured data
- Default "neutral/system" theme shipped with X-IPE
- Themes section in toolbox modal with visual cards
- Theme selection persisted in `x-ipe-docs/config/tools.json`
- Sidebar themes menu
- New `tool-frontend-design` skill

### Out of Scope (Future)
- Theme editor UI (create/edit themes in browser)
- Theme import/export (share themes across projects)
- Live theme preview on mockups
- Dark/light mode variants per theme
- Theme inheritance (extend a base theme)

---

## Technical Considerations

1. **Config Reuse**: Leverage existing `x-ipe-docs/config/tools.json` pattern for theme persistence
2. **Skill Design**: `tool-frontend-design` should be invocable from ideation toolbox
3. **Fallback**: If no theme selected, use `theme-default`
4. **Discovery**: Scan `x-ipe-docs/themes/theme-*/` folders to list available themes
5. **Thumbnail Generation**: Consider auto-generating theme card previews from design tokens

---

## Open Questions

1. Should theme thumbnails be auto-generated or manually created?
2. What's the maximum number of themes to display before needing pagination/search?
3. Should the default theme be customizable per project?

---

## Mockups & Prototypes

| Mockup | Type | Path | Tool Used |
|--------|------|------|-----------|
| Themes in Toolbox Modal | HTML | [mockups/themes-toolbox-v1.html](mockups/themes-toolbox-v1.html) | frontend-design |

### Preview Instructions
- Open the HTML file in a browser to view the interactive mockup
- Click the **green toolbox button** in the top bar to open the modal
- Click theme cards to select different themes (visual feedback)
- Expand/collapse stage accordions to see existing toolbox structure

---

## Next Steps

1. ~~**Mockup**: Create visual mockup of toolbox modal with themes section~~ ✅
2. **Requirement Gathering**: Break down into features for implementation
3. **Default Theme**: Create the `theme-default` content
