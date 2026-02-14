# Feature Specification: UIUX Reference Agent Skill & Toolbar

> Feature ID: FEATURE-030-B
> Version: v1.1
> Status: Refined
> Last Updated: 02-13-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.1 | 02-13-2026 | Eyedropper cursor, expandable color/element lists with hover-highlight, screenshot accuracy, post-send reset | [CR-001](./CR-001.md) |
| v1.0 | 02-13-2026 | Initial specification | - |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Injected Reference Toolbar v3 (CR-001) | HTML | [mockups/injected-toolbar-v3.html](mockups/injected-toolbar-v3.html) | v2 + CR-001 enhancements: eyedropper cursor on color picker, expandable color/element lists with hover-to-highlight source elements, remove buttons, post-send reset of all collected data | current |
| Injected Reference Toolbar (light) | HTML | [mockups/injected-toolbar-v2.html](mockups/injected-toolbar-v2.html) | Frosted-glass toolbar panel on simulated website — hamburger toggle, Phase 1/2 tool list, collected data summary, element highlighting with CSS selector label, color picker swatch, "Send References" button | outdated — superseded by v3 |
| Injected Reference Toolbar (dark alt) | HTML | [mockups/injected-toolbar-v1.html](mockups/injected-toolbar-v1.html) | Dark glassmorphism alternative | outdated — use as directional reference only |

> **Note:** UI/UX requirements and acceptance criteria below are derived from the mockup marked as "current" (v3 CR-001).
> The v1/v2 mockups are outdated; use as directional reference only.

## Overview

FEATURE-030-B is the **agent-side execution engine** for the UIUX Reference workflow. After the user submits the `uiux-reference` prompt via FEATURE-030-A's console-first flow, this feature takes over: the agent skill uses Chrome DevTools MCP to open the target URL in Chrome, optionally handles an authentication prerequisite page, and injects an interactive toolbar into the target page.

The injected toolbar provides two Phase 1 tools — **Color Picker** (extract hex/RGB/HSL values from any element) and **Element Highlighter** (inspect elements with bounding box overlays, CSS selector paths, and screenshots). Users interact with these tools directly in the browser, and all collected reference data is accumulated in an in-page JavaScript object. When the user clicks "Send References," the data is transmitted back to the agent via a CDP callback mechanism (`Runtime.addBinding` primary, `evaluate_script` polling fallback), and the agent saves it to the idea folder through the FEATURE-033 MCP server.

**Target users:** CLI agents (Copilot, Claude Code, OpenCode) executing the `uiux-reference` skill on behalf of X-IPE users who want to extract design reference data from external web pages.

## User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-1 | As an agent, I want to open a target URL in Chrome via Chrome DevTools MCP, so that the user can interact with the reference page. | P0 |
| US-2 | As an agent, I want to handle an authentication prerequisite URL flow, so that users can reference pages that require login. | P1 |
| US-3 | As an agent, I want to inject an interactive toolbar into the target page, so that users can pick colors and highlight elements. | P0 |
| US-4 | As a user, I want to use the Color Picker tool to click any element and capture its color values (hex, RGB, HSL) plus the CSS selector, so that I can reference exact colors from the page. | P0 |
| US-5 | As a user, I want to use the Element Highlighter tool to hover over elements and see bounding box overlays with CSS selector labels, and click to capture screenshots, so that I can reference specific UI components. | P0 |
| US-6 | As a user, I want to click "Send References" to transmit all collected data back to the agent, so that the data is persisted to my idea folder. | P0 |
| US-7 | As an agent, I want to receive collected reference data via a CDP callback and save it through the App-Agent Interaction MCP, so that the data is organized in the correct folder structure. | P0 |
| US-8 | As a user, I want to drag the toolbar to any position on the page, so that it doesn't obstruct the content I'm inspecting. | P1 |
| US-9 | As a user, I want the cursor to change to an eyedropper icon when Color Picker is active, so that I can aim precisely at the element I want to pick color from. | P0 |
| US-10 | As a user, I want to see an expandable list of all picked colors in the toolbar panel, so that I can review what I've collected before sending. | P0 |
| US-11 | As a user, I want the source element to be highlighted on the page when I hover over a color entry in the list, so that I can verify where each color came from. | P0 |
| US-12 | As a user, I want to see an expandable list of all selected elements in the toolbar panel, so that I can review what I've captured. | P0 |
| US-13 | As a user, I want the element to be highlighted on the page when I hover over an element entry in the list, so that I can verify which element each entry represents. | P0 |
| US-14 | As a user, I want all collected colors and elements to be reset after clicking "Send References," so that I can start a fresh collection session. | P0 |

## Acceptance Criteria

### Page Navigation

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-1 | Agent receives `uiux-reference` prompt with `--url` parameter | Agent executes the skill | Target URL is opened in Chrome via Chrome DevTools MCP `navigate_page` tool. Page loads completely (wait for `load` event or timeout after 30s). |
| AC-2 | Agent receives prompt with `--url` and `--auth-url` parameters | Agent executes the skill | Auth URL is opened first via `navigate_page`. Agent waits for user to complete authentication. |
| AC-3 | User is on the auth page | User completes login and page URL changes away from auth domain | Agent detects URL change (via `take_snapshot` or `evaluate_script` polling current URL), then navigates to the target URL. |
| AC-4 | User is on the auth page | 5 minutes elapse without URL change | Agent prompts user: "Authentication timeout — please complete login or type 'skip' to proceed to target URL without auth." |
| AC-5 | Target URL fails to load (network error, 4xx, 5xx) | Agent detects failure | Agent reports error to user: "Failed to load {url}. Please check the URL and try again." Skill terminates gracefully. |

### Toolbar Injection

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-6 | Target page is loaded in Chrome | Agent injects toolbar | Toolbar appears as a circular hamburger button (52×52px) at top-right (20px from top and right edges). Button shows "X-IPE" text and a badge count of collected items. |
| AC-7 | Toolbar hamburger is visible | User clicks the hamburger button | Panel expands (272px wide) showing: header with "X-IPE Reference" title and close button, Phase 1 tools (Color Picker, Element Highlighter), collected data summary, and "Send References" button. Panel animation: 0.35s slideIn. |
| AC-8 | Panel is expanded | User clicks close button (×) | Panel hides, hamburger button reappears. |
| AC-9 | Toolbar is injected | Visual comparison | UI layout MUST match the approved mockup (injected-toolbar-v3.html) for the toolbar panel, hamburger button, tool list, and expandable color/element lists. |
| AC-10 | Toolbar is injected on any page | Page has high z-index elements | Toolbar uses `z-index: 2147483647` (max) and remains on top of all page content. |
| AC-11 | Toolbar hamburger is visible (collapsed state) | User drags the hamburger button | Toolbar position updates in real-time following mouse movement. New position persists until page reload. Drag only works when panel is collapsed. |
| AC-12 | Toolbar is injected | Page is scrolled or resized | Toolbar remains fixed in its position (`position: fixed`). All tool functionality continues to work. |
| AC-13 | Toolbar is first injected | Drag hint appears | A "Drag to move toolbar" hint appears near the hamburger (fades out after 3 seconds). |
| AC-14 | Toolbar is injected | Page content check | Toolbar injection does NOT break the target page's layout, styling, or JavaScript functionality. All toolbar styles are scoped/namespaced to prevent conflicts. |

### Color Picker Tool

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-15 | Color Picker tool is active (selected in toolbar) | User clicks any element on the page | Color values extracted: hex (e.g., `#667eea`), RGB (e.g., `102, 126, 234`), HSL (e.g., `229, 75%, 66%`). CSS selector of the source element captured (e.g., `body > main > .cards > .card:nth-child(1) > .card-icon`). |
| AC-16 | Color is picked | Data is stored | Color entry added to `window.__xipeRefData.colors` array with fields: `id`, `hex`, `rgb`, `hsl`, `source_selector`, `context`. Badge count on Color Picker tool increments. |
| AC-17 | Color is picked | Visual feedback | A small swatch pill appears near the picked element showing the hex value (e.g., `#667eea`), matching mockup style (rounded pill, mono font, 10px). |
| AC-18 | Multiple colors picked | User views toolbar | "Collected References" section shows running count (e.g., "3 colors"). Total badge on hamburger button updates. |

### Element Highlighter Tool

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-19 | Element Highlighter tool is active | User hovers over any element | A bounding box overlay appears around the element (2px solid accent border, pulsing glow animation). CSS selector label shown above the element in a small accent-colored pill (mono font, 10px). |
| AC-20 | Element Highlighter is active, hover overlay visible | User moves mouse to a different element | Previous overlay disappears, new overlay appears on the new element. |
| AC-21 | Element Highlighter is active | User clicks an element | Element is captured: CSS selector path, tag name, bounding box (x, y, width, height). Full-page screenshot taken via Chrome DevTools MCP `take_screenshot` (fullPage: true). Element crop screenshot taken via `take_screenshot` (uid of element). |
| AC-22 | Element is captured | Data is stored | Element entry added to `window.__xipeRefData.elements` array with fields: `id`, `selector`, `tag`, `bounding_box`, `screenshots` (paths). Badge count on Element Highlighter tool increments. |
| AC-23 | Multiple elements captured | User views toolbar | "Collected References" section shows running count (e.g., "2 elements"). Total badge on hamburger button updates. |

### Eyedropper Cursor (CR-001)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-36 | Color Picker tool is selected (active) | User moves mouse over page content (outside toolbar) | Mouse cursor changes to an eyedropper/straw icon (custom SVG cursor or `crosshair` fallback). Cursor provides clear visual feedback that the user is in color-picking mode. |
| AC-37 | Color Picker is active with eyedropper cursor | User moves mouse over the toolbar panel | Cursor reverts to default pointer within the toolbar area. Toolbar interactions are not affected by the custom cursor. |
| AC-38 | Element Highlighter tool is selected | User moves mouse over page content | Cursor changes to crosshair to indicate element selection mode. |
| AC-39 | User switches from Color Picker to Element Highlighter | Tool selection changes | Cursor changes from eyedropper to crosshair immediately. Previous cursor style is removed. |
| AC-40 | Panel is collapsed (hamburger visible) | Any tool is active | Cursor is NOT in eyedropper/crosshair mode (tools only apply custom cursor when panel is open and a tool is active). |

### Expandable Color List (CR-001)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-41 | User has picked 1+ colors | User views "Collected References" section in toolbar | An expandable list appears below the color summary tag showing all picked colors. Each entry shows: color swatch circle (16px), hex value (mono font), truncated source selector. |
| AC-42 | Color list is visible | User hovers over a color entry | The source element on the page is highlighted with a rose-colored border/glow (`box-shadow: 0 0 0 2px var(--rose)`). Highlight appears immediately on mouseenter. |
| AC-43 | Color entry is being hovered | User moves mouse away from the entry | Page highlight is removed immediately on mouseleave. No residual highlight remains. |
| AC-44 | Color list has entries | User clicks the remove button (×) on a color entry | The color entry is removed from the list, removed from `window.__xipeRefData.colors`, and all badge counts (tool badge, hamburger badge, summary tag) are decremented. |
| AC-45 | "Collected References" header is visible | User clicks the header toggle chevron | Color list and element list collapse/expand together. Chevron rotates 180° to indicate state. |

### Expandable Element List (CR-001)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-46 | User has captured 1+ elements | User views "Collected References" section | An expandable list appears below the element summary tag showing all captured elements. Each entry shows: tag name pill (mono font, accent background), truncated CSS selector, dimensions (width×height). |
| AC-47 | Element list is visible | User hovers over an element entry | The corresponding element on the page is highlighted with an accent-colored border/glow (`box-shadow: 0 0 0 2px var(--accent)`) and its CSS selector label appears above it. Highlight appears immediately on mouseenter. |
| AC-48 | Element entry is being hovered | User moves mouse away from the entry | Page highlight is removed immediately on mouseleave. No residual highlight remains. |
| AC-49 | Element list has entries | User clicks the remove button (×) on an element entry | The element entry is removed from the list, removed from `window.__xipeRefData.elements`, and all badge counts are decremented. |

### Element Screenshot Accuracy (CR-001)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-50 | Agent needs to take element-level screenshot | Agent processes captured element data | Agent calls `take_snapshot()` to get the accessibility tree, then finds the element by matching bounding box coordinates (x, y, width, height) against snapshot nodes. Uses the matched node's `uid` for `take_screenshot(uid)`. |
| AC-51 | Element bounding box matches multiple snapshot nodes | Agent resolves ambiguity | Agent selects the node whose bounding box has the closest match (smallest area difference). If no match within 20px tolerance, falls back to full-page screenshot crop. |
| AC-52 | Element's CSS selector contains dynamic classes | Agent takes screenshot | Screenshot accuracy is NOT dependent on CSS selector matching. The bounding-box-to-uid approach works regardless of dynamic class names. |

### Post-Send Reset (CR-001)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-53 | User has collected colors and/or elements | User clicks "Send References" and data is transmitted | After the success state animation completes (2.3s): `window.__xipeRefData.colors` is set to empty array `[]`, `window.__xipeRefData.elements` is set to empty array `[]`, `window.__xipeRefReady` is set to `false`. |
| AC-54 | Send completes and reset occurs | User views toolbar after reset | All badge counts show 0. Color list and element list are empty. Summary tags show "0 colors" and "0 elements". Send button returns to idle state. |
| AC-55 | Send completes and reset occurs | User picks new colors or elements | New items are collected fresh into the empty arrays. IDs restart from `color-001` / `elem-001`. A subsequent "Send References" creates a new session file (ref-session-{NNN+1}.json). |

### Visual Consistency (Mockup Comparison)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-33 | Toolbar is rendered | Visual comparison | Visual styling (colors, spacing, typography) MUST be consistent with mockup (injected-toolbar-v3.html). Outfit font for UI text, Space Mono for selectors/values. Frosted-glass panel with `backdrop-filter: blur(24px)`. |
| AC-34 | Toolbar is rendered | Interactive elements check | All interactive elements shown in mockup (injected-toolbar-v3.html) MUST be present and functional: hamburger toggle, tool selection (active state with cursor change), close button, send button state transitions with post-send reset, drag-to-move, expandable color/element lists with hover-to-highlight. |
| AC-35 | Toolbar is rendered | Phase separator check | Phase 1 ("Phase 1 — Core") and Phase 2 ("Phase 2 — Advanced") sections visible with divider. Phase 2 tools (Element Commenter, Asset Extractor) shown as disabled/placeholder with "—" badge (not functional in this feature). |

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-24 | Before toolbar injection | Agent registers callback | Agent calls CDP `Runtime.addBinding(name: "__xipeCallback")` to create a `window.__xipeCallback(payload)` function in page context. |
| AC-25 | User has collected at least 1 color or element | User clicks "Send References" button | Button shows loading state: spinner icon + "Sending..." text. `window.__xipeCallback(JSON.stringify(window.__xipeRefData))` is called. |
| AC-26 | Callback fires | CDP receives event | Agent receives `Runtime.bindingCalled` event with `name: "__xipeCallback"` and `payload` containing the reference data JSON string. |
| AC-27 | Send completes successfully | Button updates | Button shows success state: checkmark icon + "Sent to X-IPE!" text, emerald background (#059669). After 2.3 seconds, all collected data resets (colors=[], elements=[], badges=0, lists cleared, `__xipeRefReady=false`). Button returns to idle state. |
| AC-28 | `Runtime.addBinding` is not available | Agent detects capability gap | Fallback activates: "Send References" button sets `window.__xipeRefReady = true`. Agent polls via `evaluate_script`: `() => window.__xipeRefReady ? window.__xipeRefData : null`. Polling interval: 2 seconds. |
| AC-29 | Agent receives reference data (primary or fallback) | Agent processes data | Agent constructs a valid Reference Data JSON (version 1.0 schema) and calls `save_uiux_reference` MCP tool (FEATURE-033) with the data. |

### Data Persistence

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-30 | Agent has reference data and idea folder context | Agent calls `save_uiux_reference` MCP tool | MCP tool POSTs data to Flask endpoint. Session JSON saved to `uiux-references/sessions/ref-session-{NNN}.json`. Merged `reference-data.json` updated. Agent confirms save to user. |
| AC-31 | Reference data includes element screenshots | Agent processes screenshots | Full-page screenshots saved to `uiux-references/screenshots/full-page-{NNN}.png`. Element crop screenshots saved to `uiux-references/screenshots/elem-{NNN}-crop.png`. Session JSON references file paths, not base64 data. |
| AC-32 | Save completes successfully | Agent reports to user | Agent outputs summary: "Reference data saved — {N} colors, {M} elements captured from {url}. Session: ref-session-{NNN}.json." |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Agent skill activated by `uiux-reference` prompt with parameters: `--url` (required), `--auth-url` (optional), `--extra` (optional) | P0 |
| FR-2 | Open target URL in Chrome via Chrome DevTools MCP `navigate_page` tool; wait for page load (30s timeout) | P0 |
| FR-3 | Authentication prerequisite flow: open auth URL → wait for URL change away from auth domain → navigate to target URL | P1 |
| FR-4 | Auth timeout: 5 minutes without URL change triggers user prompt | P1 |
| FR-5 | Inject toolbar HTML/CSS/JS into target page via `evaluate_script` tool | P0 |
| FR-6 | Toolbar appears as fixed-position circular hamburger (52×52px) at top-right, `z-index: 2147483647` | P0 |
| FR-7 | Hamburger click expands panel (288px wide) with tool list; close button collapses back to hamburger | P0 |
| FR-8 | Toolbar is draggable when collapsed (hamburger state only) via mousedown/mousemove/mouseup | P1 |
| FR-9 | "Drag to move toolbar" hint shown on injection, auto-fades after 3 seconds | P2 |
| FR-10 | Color Picker tool: click element → extract hex/RGB/HSL from `getComputedStyle().backgroundColor` (or `color` based on context), capture CSS selector via DOM traversal | P0 |
| FR-11 | Color Picker visual feedback: swatch pill shown near picked element with hex value | P0 |
| FR-12 | Element Highlighter tool: hover → bounding box overlay (2px accent border, pulsing glow) + CSS selector label above element | P0 |
| FR-13 | Element Highlighter tool: click → capture CSS selector path, tag name, bounding box from `getBoundingClientRect()` | P0 |
| FR-14 | Element Highlighter tool: on click, take full-page screenshot via Chrome DevTools MCP `take_screenshot(fullPage: true)` and element crop via `take_screenshot(uid)` | P0 |
| FR-15 | All collected data stored in `window.__xipeRefData` object (in-page JS) with `colors[]` and `elements[]` arrays | P0 |
| FR-16 | "Collected References" summary in toolbar panel shows running count of colors and elements with color-coded tags | P0 |
| FR-17 | Badge count on hamburger button shows total collected items (colors + elements) | P0 |
| FR-18 | Register CDP `Runtime.addBinding(name: "__xipeCallback")` before toolbar injection | P0 |
| FR-19 | "Send References" button calls `window.__xipeCallback(JSON.stringify(window.__xipeRefData))` | P0 |
| FR-20 | Send button 3-state transition: idle → sending (spinner, 1.2s) → success (checkmark, 2.3s) → reset to idle | P0 |
| FR-21 | Fallback callback: if `Runtime.addBinding` unavailable, use `window.__xipeRefReady` flag + `evaluate_script` polling (2s interval) | P1 |
| FR-22 | Agent constructs Reference Data JSON (v1.0 schema) from received data, including `idea_folder` from `--extra` or prompt context | P0 |
| FR-23 | Agent calls FEATURE-033 `save_uiux_reference` MCP tool with constructed JSON | P0 |
| FR-24 | Phase 2 tools (Element Commenter, Asset Extractor) shown in toolbar panel as disabled placeholders with "—" badge and "Phase 2 — Advanced" separator | P2 |
| FR-25 | Tool selection is mutually exclusive — only one tool active at a time; active tool has accent background highlight | P0 |
| FR-26 | CSS selector generation uses full path from `body` with tag names, class names, and `:nth-child()` for disambiguation (e.g., `body > main > .cards > .card:nth-child(2)`) | P0 |
| FR-27 | Eyedropper cursor: when Color Picker is active and mouse is outside toolbar panel, apply a custom SVG eyedropper cursor via CSS `cursor: url('data:image/svg+xml,...') 2 30, crosshair`. Cursor reverts to default inside toolbar panel. (CR-001-A) | P0 |
| FR-28 | Crosshair cursor: when Element Highlighter is active and mouse is outside toolbar panel, apply CSS `cursor: crosshair`. Cursor reverts to default inside toolbar panel. (CR-001-A) | P0 |
| FR-29 | Expandable color list: "Collected References" section shows a collapsible list of all picked colors. Each entry displays a 16px circular swatch, hex value (mono font), truncated source CSS selector, and a remove (×) button. (CR-001-B) | P0 |
| FR-30 | Color entry hover-to-highlight: on `mouseenter` of a color list entry, the source element on the page is highlighted with `box-shadow: 0 0 0 2px var(--rose)`. Highlight removed on `mouseleave`. (CR-001-B) | P0 |
| FR-31 | Expandable element list: "Collected References" section shows a collapsible list of all captured elements. Each entry displays a tag-name pill (mono font, accent background), truncated CSS selector, dimensions (w×h), and a remove (×) button. (CR-001-C) | P0 |
| FR-32 | Element entry hover-to-highlight: on `mouseenter` of an element list entry, the element on the page is highlighted with `box-shadow: 0 0 0 2px var(--accent)` and CSS selector label appears above it. Highlight removed on `mouseleave`. (CR-001-C) | P0 |
| FR-33 | Remove from list: clicking × on a color or element entry removes it from `window.__xipeRefData`, decrements all badge/summary counts, and removes the entry DOM node with a fade-out transition. (CR-001-B, CR-001-C) | P0 |
| FR-34 | Collapsible references section: the "Collected References" header has a toggle chevron that collapses/expands the color and element lists together. Chevron rotates 180° on toggle. (CR-001-B, CR-001-C) | P1 |
| FR-35 | Element screenshot accuracy: agent uses `take_snapshot()` to get the a11y tree, matches captured element bounding box (x, y, width, height) against snapshot nodes (20px tolerance), and uses the matched node's `uid` for `take_screenshot(uid)`. Falls back to full-page screenshot crop if no match. (CR-001-D) | P0 |
| FR-36 | Post-send reset: after "Send References" success animation completes (≈3.5s total), reset `window.__xipeRefData.colors = []`, `window.__xipeRefData.elements = []`, `window.__xipeRefReady = false`. Clear all badge counts, empty color/element lists in DOM, reset summary tags to "0 colors" / "0 elements", return send button to idle state. (CR-001-E) | P0 |
| FR-37 | Panel scrollability: panel content area has `max-height: calc(100vh - 120px)` with `overflow-y: auto` to accommodate large color/element lists. Panel header is sticky. (CR-001-B, CR-001-C) | P1 |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Toolbar injection must complete within 500ms (JS evaluation + DOM insertion) | P1 |
| NFR-2 | Toolbar styles must be fully scoped/namespaced (`.xipe-*` prefix) to avoid conflicts with target page CSS | P0 |
| NFR-3 | Toolbar must not interfere with target page event listeners or JavaScript execution | P0 |
| NFR-4 | Color picker extraction must complete within 50ms per click | P1 |
| NFR-5 | Element highlighter hover overlay must update within 16ms (60fps) for smooth tracking | P1 |
| NFR-6 | Screenshot capture (full-page + element crop) must complete within 5 seconds combined | P1 |
| NFR-7 | CDP connection resilience: 3 reconnection retries on connection drop; save partial data on final failure | P0 |
| NFR-8 | Injected toolbar total payload (HTML + CSS + JS) must be under 50KB minified | P1 |
| NFR-9 | Callback polling fallback interval: 2 seconds; max polling duration: 5 minutes | P1 |
| NFR-10 | Auth URL monitoring polling interval: 3 seconds; timeout: 5 minutes | P1 |

## UI/UX Requirements

### Component Inventory (from mockup)

| Component | Element | Details |
|-----------|---------|---------|
| Hamburger Button | Circular button (52×52px) | Gradient background (accent → #4f46e5), white "X-IPE" text, badge count circle (18×18px, emerald) |
| Panel | Expandable panel (288px wide) | Frosted glass (`backdrop-filter: blur(24px)`), 14px border-radius, slide-in animation, max-height with overflow-y scroll, sticky header |
| Panel Header | Title + close button | Accent dot (8×8px) + "X-IPE Reference" text (12.5px, 600 weight), × close button (26×26px) |
| Phase Separator | Section label | Uppercase, 9.5px, 600 weight, muted color, 0.1em letter-spacing |
| Tool Button | Interactive tool item | Icon (30×30px colored square) + name (12.5px) + description (10px muted) + badge (pill, 10px) |
| Tool Icon — Color Picker | Eyedropper icon | Rose background (`rgba(190,18,60,0.06)`), rose color (`#be123c`) |
| Tool Icon — Highlighter | Cursor-text icon | Accent light background, accent color |
| Tool Icon — Commenter | Chat-left-text icon | Amber background, amber color |
| Tool Icon — Extractor | Box-arrow-down icon | Emerald background, emerald color |
| Active Tool State | Selected tool | Accent light background + accent color text + subtle border |
| Tool Badge | Item count | Emerald background when items collected; muted when empty |
| Collected Summary | Color-coded tags | Rose tag for colors, accent tag for elements; dot + count text |
| Send Button | Primary action | Full width, emerald background, white text, 12px font, 6px radius |
| Highlight Overlay | Bounding box on element | 2px accent border, pulsing glow animation (1.5s), 14px border-radius |
| CSS Selector Label | Above highlighted element | Accent background, white text, mono font (Space Mono, 10px), 4px border-radius |
| Color Swatch Pill | Near picked element | White pill, 1px border, mono font hex value, 18×18px circular swatch |
| Drag Hint | Below hamburger | Rounded pill, arrows-move icon + text, fades after 3s |
| Eyedropper Cursor | Custom CSS cursor | SVG eyedropper icon (32×32), hotspot at tip (2, 30). Applied to `<body>` when Color Picker is active. Fallback: `crosshair`. |
| Crosshair Cursor | CSS cursor | Applied to `<body>` when Element Highlighter is active. |
| Color List Entry | Inside Collected References section | 16px circular swatch, hex value (mono font), truncated source selector (max-width 120px, ellipsis), × remove button (16px, rose on hover). Hover triggers page highlight. |
| Element List Entry | Inside Collected References section | Tag-name pill (mono font, accent background, 3px padding), truncated selector (max-width 120px, ellipsis), dimensions text (10px, muted), × remove button (16px, accent on hover). Hover triggers page highlight. |
| Collected References Header | Collapsible section header | "Collected References" title (10px, 600 weight, muted), chevron toggle icon (rotates 180° on collapse), controls visibility of color/element lists. |
| Hover Highlight (Color) | Page overlay on source element | `box-shadow: 0 0 0 2px var(--rose)` applied to source element when color entry is hovered. Removed on mouseleave. |
| Hover Highlight (Element) | Page overlay on captured element | `box-shadow: 0 0 0 2px var(--accent)` + CSS selector label above element. Applied when element entry is hovered. Removed on mouseleave. |

### Color System

| Token | Value | Usage |
|-------|-------|-------|
| `--toolbar-bg` | rgba(255,255,255,0.94) | Panel background |
| `--toolbar-border` | rgba(55,48,163,0.15) | Panel border |
| `--panel-bg` | rgba(255,255,255,0.97) | Inner panel areas |
| `--accent` | #3730a3 | Primary accent (deep indigo) |
| `--accent-hover` | #4f46e5 | Hover accent |
| `--accent-light` | rgba(55,48,163,0.08) | Active tool background |
| `--emerald` | #047857 | Send button, success, collected badges |
| `--rose` | #be123c | Color picker icon/badge |
| `--amber` | #b45309 | Commenter icon (Phase 2) |
| `--text-primary` | #1a1a2e | Primary text |
| `--text-secondary` | #4a4a5c | Secondary text |
| `--text-muted` | #8e8e9f | Descriptions, labels |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Panel title | Outfit | 12.5px | 600 |
| Tool name | Outfit | 12.5px | 500 |
| Tool description | Outfit | 10px | 400 |
| Phase separator | Outfit | 9.5px | 600 |
| Collected title | Outfit | 10px | 600 |
| Send button | Outfit | 12px | 600 |
| CSS selector label | Space Mono | 10px | 400 |
| Color hex value | Space Mono | 10px | 400 |
| Badge count | Outfit | 10px | 600 |

### Animations

| Animation | Duration | Easing | Details |
|-----------|----------|--------|---------|
| Panel slide-in | 0.35s | cubic-bezier(0.22,1,0.36,1) | translateY(-8px) + scale(0.96) → origin |
| Highlight pulse | 1.5s | ease-in-out | box-shadow glow 0 → 6px → 0, infinite |
| Drag hint fade | 3s | ease-in-out | Fade in at 15%, hold until 75%, fade out |
| Hamburger hover | 0.4s | cubic-bezier(0.22,1,0.36,1) | scale(1.1), gradient shift, enhanced shadow |
| Send button states | 1.2s sending, 2.3s success | — | spinner → checkmark → reset (post-reset clears all data) |
| Comment tooltip | 0.25s | cubic-bezier(0.22,1,0.36,1) | translateY(-4px) → 0, opacity 0 → 1 |
| Chevron toggle | 0.2s | ease | rotate(0deg) → rotate(180deg) on collapse |
| List entry remove | 0.2s | ease-out | opacity 1 → 0, height collapses |
| Hover highlight (page) | instant | — | box-shadow applied on mouseenter, removed on mouseleave |

## Dependencies

### Internal

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-030-A (UIUX Reference Tab) | Hard | Provides the entry point: tab UI auto-types the `uiux-reference` prompt into the console. Without 030-A, the skill has no trigger mechanism. |
| FEATURE-033 (App-Agent Interaction MCP) | Hard | Provides the `save_uiux_reference` MCP tool for persisting reference data to the idea folder. Without 033, data cannot be saved. |

### External

| Dependency | Type | Description |
|------------|------|-------------|
| Chrome DevTools MCP | Hard | CDP-based browser automation. Required for `navigate_page`, `evaluate_script`, `take_screenshot`, and `Runtime.addBinding`. Must be pre-configured in agent's MCP config. |
| Chrome Browser | Hard | Target page must be opened in a Chrome instance connected to Chrome DevTools MCP. |
| Bootstrap Icons CDN | Soft | Toolbar icons use Bootstrap Icons. Injected CSS links to CDN; if CDN unavailable, toolbar degrades gracefully (icons missing but functionality intact). |
| Google Fonts CDN (Outfit, Space Mono) | Soft | Toolbar typography. If CDN unavailable, falls back to system sans-serif/monospace fonts. |

## Business Rules

| ID | Rule |
|----|------|
| BR-1 | Only one tool can be active at a time — selecting a new tool deactivates the previous one. |
| BR-2 | Toolbar injection happens only after the target page is fully loaded (or 30s timeout). |
| BR-3 | The agent must register `Runtime.addBinding` BEFORE injecting the toolbar JS, to ensure the callback function exists when tools store data. |
| BR-4 | Color extraction uses `getComputedStyle()` to get the resolved color value, converting to hex/RGB/HSL formats. |
| BR-5 | CSS selectors must be unique within the page — if multiple elements match, append `:nth-child()` for disambiguation. |
| BR-6 | Screenshots are taken by the agent (server-side via Chrome DevTools MCP), not by the in-page JavaScript. The in-page JS signals which element to screenshot; the agent executes the capture. |
| BR-7 | The `idea_folder` parameter for the MCP save call is derived from the prompt context (either from `--extra` instructions or from the active idea in the X-IPE session). |
| BR-8 | Phase 2 tools (Element Commenter, Asset Extractor) are shown in the toolbar panel as visual placeholders only — clicking them has no effect beyond visual active state toggle. |
| BR-9 | The toolbar must not execute any network requests from the page context — all data transmission is handled via the CDP callback mechanism. |
| BR-10 | Reference data conforms to the JSON schema defined in IDEA-018 idea summary (version 1.0). |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Target page uses Content Security Policy (CSP) blocking inline scripts | Agent uses Chrome DevTools MCP `evaluate_script` which bypasses CSP (runs in isolated world). Toolbar injection works regardless of CSP. |
| Target page has iframes | Toolbar is injected into the top-level frame only. Elements inside iframes are not accessible. If user clicks inside an iframe, no color/element data is captured; no error shown. |
| Target page uses Shadow DOM | Elements inside shadow roots are not accessible by the CSS selector generator. If user clicks a shadow DOM element, the host element is captured instead. |
| Target page navigates away (SPA route change) | Toolbar remains injected (it's in the DOM). If a full page reload occurs, toolbar is lost. Agent detects this and re-injects. |
| Target page has `pointer-events: none` on elements | Color Picker and Highlighter may not detect clicks on those elements. User can switch to a different tool or inspect a parent element. |
| Very large page (>10MB DOM) | Highlight overlay may lag. CSS selector generation still works. Screenshot may take longer than 5s — extend timeout to 15s. |
| Multiple browser tabs open in Chrome | Toolbar is injected only into the page opened by the agent via Chrome DevTools MCP `navigate_page`. Other tabs are unaffected. |
| CDP connection drops mid-session | Agent attempts 3 reconnection retries (2s, 4s, 8s exponential backoff). If reconnection fails, agent saves any partial data already received and reports to user. |
| User clicks "Send References" with no data collected | Send button shows error state briefly: "No data collected — pick colors or elements first." Resets to idle after 2 seconds. |
| User sends references multiple times | Each send creates a new session (ref-session-{NNN}.json). Previous sessions are preserved. All collected data resets after successful send. |
| Color list entry source element removed from DOM | On hover, if `document.querySelector(selector)` returns null, show a tooltip "Element no longer in DOM" on the list entry. No highlight applied. |
| Element list entry element removed from DOM | On hover, if `document.querySelector(selector)` returns null, show a tooltip "Element no longer in DOM" on the list entry. No highlight applied. |
| User removes all colors/elements via × buttons | Badge counts show 0, summary tags show "0 colors" / "0 elements". Send button remains enabled (sends empty arrays). |
| Many collected items (>20 colors or >10 elements) | Panel scrolls within max-height. Lists remain performant. No pagination — all items shown. |
| Color picked from element behind toolbar | Toolbar pointer-events prevent picking through it. User must move toolbar (drag) to access obscured elements. |
| Auth URL and target URL are on the same domain | Agent monitors for any URL path change after auth URL loads. When path differs from auth URL path, auth is considered complete. |
| CORS-blocked resources on target page | Toolbar functionality is unaffected (runs via CDP, not page context). Screenshot capture works regardless of CORS. |
| Target page has z-index higher than 2147483646 | Toolbar uses `z-index: 2147483647` (max 32-bit int). If page also uses max z-index, toolbar may overlap with page elements — acceptable trade-off. |

## Out of Scope

- Element Commenter tool functionality (FEATURE-031 — Phase 2)
- Asset Extractor tool functionality (FEATURE-031 — Phase 2)
- Design system generation from extracted tokens (FEATURE-032 — Phase 3)
- Binary asset downloads (fonts, icons, images) — handled by FEATURE-031
- Multi-page reference sessions (each session targets a single URL)
- Shadow DOM element inspection
- Cross-origin iframe element inspection
- Real-time collaboration or multi-user sessions
- Toolbar theme switching (only light/frosted-glass theme in v1)
- Keyboard shortcuts for tool selection
- Undo/redo for collected data
- Editing collected data before sending
- Persistent toolbar position across sessions (position resets on re-injection)

## Technical Considerations

- The skill is an **agent-side orchestration script** — it does not run as a standalone server. The agent loads it as a skill and executes its procedures step-by-step.
- Toolbar injection should be a single large `evaluate_script` call containing the HTML template, CSS styles, and JavaScript logic as a self-contained IIFE (Immediately Invoked Function Expression).
- All toolbar CSS classes use the `.xipe-` prefix to avoid name collisions with target page styles. CSS specificity is kept high via the namespace.
- `Runtime.addBinding` is used because it's the standard CDP mechanism for page-to-DevTools communication. Puppeteer's `page.exposeFunction()` and Playwright's `page.exposeBinding()` both use it internally.
- Screenshot capture for elements requires the agent to call Chrome DevTools MCP `take_screenshot` with the element's uid (obtained from `take_snapshot`). The in-page JS cannot take screenshots — it only identifies the element.
- The agent needs to determine the `idea_folder` to pass to the MCP save tool. This comes from the user's prompt context or from the `--extra` parameter.
- CSS selector generation must handle edge cases: elements without classes, deeply nested elements, dynamically generated class names (should be excluded from selector).
- The injected toolbar must load fonts (Outfit, Space Mono) and icons (Bootstrap Icons) from CDN. These are injected as `<link>` elements in the page head. If CDN fails, the toolbar still functions with system fonts.

## Open Questions

None — all clarifications resolved during requirement gathering, idea summary (IDEA-018 v3), and change request CR-001.
