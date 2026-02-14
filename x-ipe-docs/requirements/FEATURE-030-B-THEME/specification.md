# Feature Specification: Catch Design Theme Mode

> Feature ID: FEATURE-030-B-THEME
> Version: v2.0
> Status: Refined
> Last Updated: 02-14-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v2.0 | 02-14-2026 | Initial specification — 3-step wizard for extracting design themes | [CR-002](../FEATURE-030-B/CR-002.md) |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Toolbar v2.0 Theme Mode | HTML | [mockups/toolbar-v2-v1.html](mockups/toolbar-v2-v1.html) | Theme mode view: magnifier overlay, color swatch list with role chips, Create Theme button | current |

## Overview

FEATURE-030-B-THEME provides the "Catch Design Theme" mode within the v2.0 toolbar. It is a 3-step wizard that guides users through extracting a reusable design theme from any web page:

1. **Pick Colors** — Click pixels on the page using an offscreen canvas renderer with a circular magnifier for precision
2. **Annotate Roles** — Assign semantic roles (primary, secondary, accent, or custom text) to each collected color
3. **Create Theme** — Send annotated colors to the agent, which invokes the `brand-theme-creator` skill to generate a `design-system.md` and `component-visualization.html`

This feature renders its UI into the mode content area provided by FEATURE-030-B (toolbar shell).

## User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-T1 | As a user, I want to click any pixel on the page and see its exact color value via a magnified view, so that I can pick precise colors from images, gradients, and text. | P0 |
| US-T2 | As a user, I want a circular magnifier following my cursor showing a zoomed grid of pixels, so that I can target the exact pixel I want. | P0 |
| US-T3 | As a user, I want to assign a role (primary, secondary, accent, or custom label) to each picked color, so that the generated theme has semantic meaning. | P0 |
| US-T4 | As a user, I want to review all my collected colors with their roles before creating the theme, so that I can verify completeness. | P0 |
| US-T5 | As a user, I want to click "Create Theme" to generate a design system from my annotated colors, so that I get a reusable theme file. | P0 |
| US-T6 | As a user, I want toast notifications showing the progress of theme creation, so that I know when it is complete. | P1 |

## Acceptance Criteria

### Step 1 — Pick Colors (Offscreen Canvas + Magnifier)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-T1 | Theme mode active, Step 1 shown | User moves mouse over page | Circular magnifier (120px diameter) follows cursor. Shows 10x zoomed grid of surrounding pixels rendered from offscreen canvas. Crosshair overlay marks center pixel. |
| AC-T2 | Magnifier visible | User clicks a pixel | Color sampled from offscreen canvas at click coordinates. Stored as hex, RGB, HSL + source CSS selector. Color swatch pill appears near click point (fades after 3s). |
| AC-T3 | User clicks on an image element | Color sampled | Offscreen canvas correctly renders the image and samples the actual pixel color (not transparent or background). |
| AC-T4 | User clicks on a CSS gradient | Color sampled | Offscreen canvas renders the gradient and samples the exact pixel at click coordinates. |
| AC-T5 | User clicks on text | Color sampled | Text color (foreground) captured from the rendered pixel, not the background. |
| AC-T6 | Cross-origin image on page | User tries to pick color | Toast warning: "Cross-origin content cannot be color-sampled." Magnifier shows checkerboard pattern for tainted regions. |
| AC-T7 | Magnifier active | Performance check | Magnifier updates throttled via requestAnimationFrame. No visible lag or jank during mouse movement. |
| AC-T8 | Multiple colors picked | User views color list | Each color shown as a row: swatch circle + hex value + source selector (truncated). Remove (x) button per entry. |

### Step 2 — Annotate Roles

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-T9 | Colors collected, Step 2 shown | User views color list | Each color has a role selector: chip buttons for primary, secondary, accent + text input for custom. Default: no role assigned. |
| AC-T10 | User clicks "primary" chip on a color | Role assigned | Chip highlighted. Role stored in __xipeRefData.colors[n].role = "primary". Only one role per color. |
| AC-T11 | User types "brand-blue" in custom input | Custom role | Role stored as "brand-blue". Custom chip shown. |
| AC-T12 | User changes role on already-assigned color | Role updated | Previous role deselected. New role applied. |

### Step 3 — Create Theme

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-T13 | At least 1 color with a role assigned | User clicks "Create Theme" | __xipeRefReady set to true with mode = "theme". Agent reads annotated colors. |
| AC-T14 | Agent receives theme data | Agent processes | Agent invokes brand-theme-creator skill with annotated colors. Toast: "Creating theme..." (progress). |
| AC-T15 | Theme creation succeeds | Agent confirms | Toast: "Theme created" (success). design-system.md and component-visualization.html generated. |
| AC-T16 | No colors have roles assigned | User clicks "Create Theme" | Button disabled. Tooltip: "Assign at least one color role first." |
| AC-T17 | Theme creation fails | Agent reports error | Toast: "Theme creation failed" (error). User can retry. |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-T1 | Render visible viewport to offscreen canvas (document.body) for pixel sampling. Cache canvas; re-render on scroll/resize (debounced 200ms). | P0 |
| FR-T2 | Circular magnifier: 120px diameter, 10x zoom, 11x11 pixel grid. Crosshair overlay at center. Follows cursor via mousemove. Throttled with requestAnimationFrame. | P0 |
| FR-T3 | On click: sample pixel at (clientX, clientY) from offscreen canvas. Extract RGB, convert to hex and HSL. Store with auto-increment ID (color-001, color-002...). | P0 |
| FR-T4 | Generate CSS selector for the clicked element (same algorithm as FEATURE-030-B shell). | P0 |
| FR-T5 | Visual feedback: swatch pill near click point showing hex. Fades after 3s. | P0 |
| FR-T6 | Role annotation UI: per-color row with 3 preset chips (primary, secondary, accent) + custom text input. Selecting one deselects others. | P0 |
| FR-T7 | "Create Theme" button: enabled only when at least 1 color has a role. On click: set mode to "theme", trigger __xipeRefReady. | P0 |
| FR-T8 | Handle CORS: detect tainted canvas via try/catch on getImageData. Show warning toast for cross-origin content. | P0 |
| FR-T9 | Wizard step navigation: Next/Back buttons to move between Steps 1-3. Current step highlighted in progress bar. | P1 |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-T1 | Offscreen canvas render within 200ms for typical viewport (1920x1080). | P0 |
| NFR-T2 | Magnifier follows cursor at 60fps. No visible lag. | P0 |
| NFR-T3 | Color sampling within 5ms per click (canvas getImageData). | P0 |
| NFR-T4 | Canvas re-render debounced to avoid excessive CPU during scroll/resize. | P1 |

## UI/UX Requirements

### Magnifier
- Circular, 120px diameter, positioned offset from cursor (top-right, 20px gap)
- 10x zoom: shows 11x11 pixel grid
- Each pixel cell has subtle border for grid visibility
- Center pixel marked with crosshair (2px lines, contrasting color)
- Current color value shown below magnifier circle (hex, small mono font)

### Color List
- Vertical list in panel content area
- Each row: 16px color swatch circle + hex value + truncated selector
- Remove (x) button on hover
- Step indicator (1/3, 2/3, 3/3) at top of content area

### Role Chips
- Inline chip buttons: "Primary" | "Secondary" | "Accent" + text input for custom
- Active chip: accent background. Inactive: outline only.

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-030-B v2.0 | Internal | Toolbar shell provides content area, toast API, data schema, __xipeRefReady |
| brand-theme-creator skill | Internal | Downstream skill invoked by agent to generate design-system.md |
| FEATURE-033 | Internal | MCP for saving theme reference data |

## Business Rules

| ID | Rule |
|----|------|
| BR-T1 | Each color gets exactly one role (or no role). No multi-role assignment. |
| BR-T2 | At least 1 color must have a role to enable "Create Theme". |
| BR-T3 | Colors persist across mode switches (shared data store). |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| Page has only cross-origin images | Warning toast. User can still pick colors from CSS-rendered elements. |
| Canvas tainted after page navigation | Re-render offscreen canvas. If still tainted, show warning for affected regions. |
| User picks same pixel twice | Two separate color entries (same hex, different IDs). User can remove duplicates. |
| Very dark or very light magnifier content | Crosshair uses contrasting color (white on dark, dark on light) for visibility. |
| Page has overlay/modal covering content | Magnifier shows whatever is visually rendered (including overlays). |

## Out of Scope

- Component selection (FEATURE-030-B-MOCKUP)
- Typography extraction (future enhancement)
- Spacing/sizing token extraction
- Multi-page color collection
- Undo/redo for color picks

## Technical Considerations

- Offscreen canvas uses html2canvas or similar library, or native Canvas 2D rendering of DOM elements. Must handle CSS transforms, pseudo-elements, and z-index stacking.
- Magnifier data read via canvas.getContext('2d').getImageData(). CORS taints canvas for cross-origin images.
- Role annotation stored directly in __xipeRefData.colors[n].role field.
- This feature registers itself with the toolbar shell via the extension point API (FR-16 of FEATURE-030-B).

## Open Questions

None.
