# Feature Specification: Design Themes

> Feature ID: FEATURE-012  
> Version: v1.0  
> Status: Completed  
> Last Updated: 01-24-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 01-24-2026 | Initial specification |

---

## Overview

Design Themes is a theming system for X-IPE that enables brands to define unified design systems (colors, typography, spacing) and apply them consistently when designing mockups for new features. Themes are stored as structured files in the `x-ipe-docs/themes/` folder, discoverable via a sidebar menu, and selectable via visual theme cards in the Stage Toolbox modal.

This feature addresses the need for brand consistency across AI-generated mockups by providing:
1. A standardized folder structure for theme definitions
2. A sidebar navigation menu to browse and edit theme files
3. An integrated theme selector in the Stage Toolbox with visual preview cards
4. Persistence of theme selection in the global tools configuration

Users include designers defining brand tokens, developers selecting themes for projects, and AI agents consuming structured theme data to generate branded mockups.

---

## Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| themes-toolbox-modal | [themes-toolbox-modal.html](mockups/themes-toolbox-modal.html) |

---

## User Stories

1. As a **designer**, I want to **define a theme with my brand's design tokens**, so that **all mockups follow our brand guidelines**.

2. As a **developer**, I want to **select a theme in the toolbox**, so that **AI uses consistent styling for my project**.

3. As a **user**, I want to **see a visual preview of theme colors and fonts**, so that **I can quickly identify and select the right theme**.

4. As an **AI agent**, I want to **read structured design data from theme files**, so that **I can generate accurate, branded mockups**.

5. As a **user**, I want to **browse theme files in the sidebar**, so that **I can view and edit design-system.md and component-visualization.html directly**.

---

## Acceptance Criteria

### Theme Folder Structure
- [ ] AC-1.1: Themes stored in `x-ipe-docs/themes/` folder
- [ ] AC-1.2: Each theme in subfolder named `theme-{name}/` (e.g., `theme-default/`, `theme-ocean/`)
- [ ] AC-1.3: Each theme folder contains `design-system.md` (required)
- [ ] AC-1.4: Each theme folder contains `component-visualization.html` (required)
- [ ] AC-1.5: Theme discovery scans `x-ipe-docs/themes/theme-*/` pattern

### design-system.md Structure
- [ ] AC-2.1: Core Tokens section (mandatory): colors, typography, spacing
- [ ] AC-2.2: Component Specs section (optional): buttons, forms, cards
- [ ] AC-2.3: Usage Guidelines section (optional): accessibility, best practices
- [ ] AC-2.4: Structured format parseable by AI agents (markdown with code blocks)

### component-visualization.html Structure
- [ ] AC-3.1: Visual HTML preview of all design tokens for humans
- [ ] AC-3.2: Structured data (JSON-LD or data attributes) for AI parsing
- [ ] AC-3.3: Self-contained HTML file (no external dependencies beyond CDN fonts)

### Sidebar Themes Menu
- [ ] AC-4.1: "Themes" menu item in sidebar navigation
- [ ] AC-4.2: Themes menu shows folder tree of `x-ipe-docs/themes/`
- [ ] AC-4.3: Clicking theme subfolder shows its files (design-system.md, component-visualization.html)
- [ ] AC-4.4: Clicking a file opens it in the content viewer (existing functionality)
- [ ] AC-4.5: Themes menu uses same tree component as Project navigation

### Toolbox Modal - Themes Section
- [ ] AC-5.1: Themes section appears at TOP of Stage Toolbox modal (before stage accordions)
- [ ] AC-5.2: Section header shows "Design Themes" with palette icon and badge showing count
- [ ] AC-5.3: Visual theme cards in 4-column grid layout
- [ ] AC-5.4: Each card shows: color swatches, typography preview, theme name, description
- [ ] AC-5.5: Click card to select theme (checkmark indicator, pink accent border)
- [ ] AC-5.6: Maximum 8 themes visible, then scrollable grid
- [ ] AC-5.7: Thumbnails auto-generated from design-system.md color tokens

### Theme Selection Persistence
- [ ] AC-6.1: Selected theme saved to `x-ipe-docs/config/tools.json` under `themes.selected` key
- [ ] AC-6.2: Theme selection is global (applies to all ideas)
- [ ] AC-6.3: If no theme selected, default to `theme-default`
- [ ] AC-6.4: Theme selection persists across browser refresh

### Backend API
- [ ] AC-7.1: `GET /api/themes` returns list of available themes with metadata
- [ ] AC-7.2: `GET /api/themes/{name}` returns theme details (design-system.md content, file paths)
- [ ] AC-7.3: Theme metadata includes: name, description, color tokens (for thumbnail generation)

---

## Functional Requirements

### FR-1: Theme Discovery Service

**Description:** Backend service to discover and parse themes from the filesystem.

**Details:**
- Input: None (scans `x-ipe-docs/themes/` folder)
- Process: 
  - Scan `x-ipe-docs/themes/theme-*/` pattern
  - Validate each theme has required files (design-system.md, component-visualization.html)
  - Parse design-system.md to extract color tokens
  - Extract theme description from first paragraph
- Output: List of ThemeMetadata objects

### FR-2: Theme API Endpoints

**Description:** REST API endpoints for theme operations.

**Details:**
- `GET /api/themes` - List all themes with metadata
- `GET /api/themes/{name}` - Get single theme details including file contents
- Response includes: name, description, colorTokens, files, selected status

### FR-3: Sidebar Themes Navigation

**Description:** Add Themes menu item to sidebar with folder tree navigation.

**Details:**
- Input: User clicks "Themes" menu item
- Process: Load folder tree for `x-ipe-docs/themes/`
- Output: Expandable tree showing theme folders and their files
- Uses existing ProjectSidebar tree component

### FR-4: Toolbox Theme Selector

**Description:** Visual theme cards section in Stage Toolbox modal.

**Details:**
- Input: User opens Stage Toolbox modal
- Process: 
  - Fetch themes from API
  - Generate visual cards with color swatches
  - Highlight selected theme
- Output: Grid of clickable theme cards

### FR-5: Theme Selection Persistence

**Description:** Save and load selected theme from configuration.

**Details:**
- Input: User clicks theme card
- Process: 
  - Update `x-ipe-docs/config/tools.json` with `themes.selected: "theme-name"`
  - Update UI to show selected state
- Output: Theme selection persists across sessions

### FR-6: Color Token Parser

**Description:** Parse design-system.md to extract color tokens for thumbnail generation.

**Details:**
- Input: design-system.md content
- Process: 
  - Find color palette section
  - Extract hex color values using regex
  - Return primary, secondary, accent, neutral colors
- Output: ColorTokens object { primary, secondary, accent, neutral }

---

## Non-Functional Requirements

### NFR-1: Performance

- Theme discovery should complete in < 500ms for up to 20 themes
- Theme cards should render within 100ms
- Lazy load theme details (only on expansion/selection)

### NFR-2: Scalability

- Support up to 20 themes without pagination
- Grid scrolls for > 8 themes
- Theme files can be up to 50KB each

### NFR-3: Accessibility

- Theme cards keyboard navigable (Tab, Enter to select)
- Color swatches have tooltips with hex values
- Selected state announced to screen readers

---

## UI/UX Requirements

### Mockup Reference
See [themes-toolbox-modal.html](mockups/themes-toolbox-modal.html) for visual design.

### Sidebar Themes Menu
- Position: Below "Workplace" in sidebar
- Icon: Palette icon (🎨)
- Behavior: Click to expand folder tree of `x-ipe-docs/themes/`

### Toolbox Themes Section
- Position: TOP of modal, before stage accordions
- Layout: 4-column grid
- Card Size: ~150px width, ~140px height
- Selection: Pink accent border (#ec4899), checkmark badge

### Theme Card Structure
```
┌─────────────────────┐
│  [Color Swatches]   │  <- 4 color bars
│  Aa Font Preview    │  <- Typography sample
├─────────────────────┤
│  theme-name         │  <- Monospace font
│  Short description  │  <- Muted text
└─────────────────────┘
```

---

## Dependencies

### Internal Dependencies

- **FEATURE-011: Stage Toolbox** - Required for modal integration. Themes section added to existing modal.

### External Dependencies

- None (uses existing infrastructure)

---

## Business Rules

### BR-1: Theme Naming Convention

**Rule:** Theme folders must be named `theme-{name}` where name is lowercase alphanumeric with hyphens.

**Examples:**
- ✅ `theme-default`, `theme-ocean-blue`, `theme-corporate2024`
- ❌ `my-theme`, `Theme_Corporate`, `ocean`

### BR-2: Required Theme Files

**Rule:** A valid theme must contain both `design-system.md` and `component-visualization.html`.

**Behavior:** Themes missing required files are excluded from the theme list with a warning logged.

### BR-3: Default Theme Fallback

**Rule:** If selected theme is deleted or missing, fall back to `theme-default`.

**Behavior:** If `theme-default` also missing, show "No themes available" message.

### BR-4: Global Theme Selection

**Rule:** Theme selection applies globally to all ideation sessions.

**Behavior:** Changing theme affects all future mockup generation, not existing mockups.

---

## Edge Cases & Constraints

### Edge Case 1: No Themes Exist

**Scenario:** `x-ipe-docs/themes/` folder is empty or doesn't exist.
**Expected Behavior:** Themes section shows "No themes available. Create a theme folder in x-ipe-docs/themes/" message.

### Edge Case 2: Theme Missing Required Files

**Scenario:** Theme folder exists but missing design-system.md or component-visualization.html.
**Expected Behavior:** Theme excluded from list. Console warning logged.

### Edge Case 3: Malformed design-system.md

**Scenario:** design-system.md exists but color tokens cannot be parsed.
**Expected Behavior:** Use fallback gray color swatches. Theme still selectable.

### Edge Case 4: Selected Theme Deleted

**Scenario:** User deletes theme folder while it's selected.
**Expected Behavior:** On next load, fall back to `theme-default`. Show toast notification.

### Edge Case 5: Many Themes (>8)

**Scenario:** User has more than 8 themes defined.
**Expected Behavior:** Themes section becomes scrollable. All themes accessible.

---

## Out of Scope

- Theme editor UI (create/edit themes in browser) - Future v2.0
- Theme import/export (share themes across projects) - Future
- Live theme preview on existing mockups - Future
- Dark/light mode variants per theme - Future
- Theme inheritance (extend a base theme) - Future
- Per-idea theme selection (currently global only)

---

## Technical Considerations

### Backend
- Create `ThemesService` class similar to existing services
- Reuse `FileService` patterns for folder scanning
- Store parsed color tokens in memory (cache on first load)

### Frontend
- Extend existing `StageToolboxModal` with themes section
- Create `ThemeCard` component for visual display
- Use CSS Grid for 4-column layout

### Configuration
- Add to existing `x-ipe-docs/config/tools.json` schema:
```json
{
  "themes": {
    "selected": "theme-default"
  },
  "ideation": { ... },
  "stages": { ... }
}
```

### Color Token Extraction
- Parse markdown code blocks for color definitions
- Regex pattern: `#[0-9A-Fa-f]{6}` or `#[0-9A-Fa-f]{3}`
- Extract first 4 colors found for thumbnail

---

## Open Questions

- [x] Q1: Should theme thumbnails be auto-generated? **Answer: Yes, from design-system.md tokens**
- [x] Q2: Max themes before scrolling? **Answer: 8 themes**
- [x] Q3: Theme persistence scope? **Answer: Global (x-ipe-docs/config/tools.json)**
- [x] Q4: Sidebar menu purpose? **Answer: Browse/edit raw theme files**

---
