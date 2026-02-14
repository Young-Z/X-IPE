# Feature Specification: Copy Design as Mockup Mode

> Feature ID: FEATURE-030-B-MOCKUP
> Version: v2.0
> Status: Refined
> Last Updated: 02-14-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v2.0 | 02-14-2026 | Initial specification — 4-step wizard for component capture and mockup generation | [CR-002](../FEATURE-030-B/CR-002.md) |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Toolbar v2.0 Mockup Mode | HTML | [mockups/toolbar-v2-v1.html](mockups/toolbar-v2-v1.html) | Mockup mode view: smart-snap overlay on semantic containers, component list, 4-step wizard progress | current |

## Overview

FEATURE-030-B-MOCKUP provides the "Copy Design as Mockup" mode within the v2.0 toolbar. It is a 4-step wizard that guides users through capturing page components and generating pixel-perfect mockup replications:

1. **Select Components** — Click to smart-snap to semantic HTML containers with drag-handle resize
2. **Add Instructions** — Attach free-text notes per component for agent context
3. **Analyze** — Agent evaluates captured data via a 5-dimension rubric, requesting deeper capture if needed
4. **Generate** — Persist metadata via MCP, generate mockup, validate via screenshot comparison (max 3 iterations)

This feature renders its UI into the mode content area provided by FEATURE-030-B (toolbar shell).

## User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-M1 | As a user, I want to click a page element and have the toolbar automatically select the nearest semantic container, so that I capture meaningful UI components. | P0 |
| US-M2 | As a user, I want drag handles on the selected area so that I can adjust the capture boundary after smart-snap. | P0 |
| US-M3 | As a user, I want to add text instructions per component (e.g., "sticky header" or "parallax scroll"), so that the agent has context for replication. | P0 |
| US-M4 | As a user, I want the agent to analyze my captured data and tell me if more information is needed, so that the mockup will be accurate. | P0 |
| US-M5 | As a user, I want the agent to generate a mockup that closely matches the original, with automatic re-tries if the match is below threshold. | P1 |
| US-M6 | As a user, I want my captured data saved before mockup generation starts, so that I do not lose work if generation fails. | P0 |

## Acceptance Criteria

### Step 1 — Select Components (Smart-Snap)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M1 | Mockup mode active, Step 1 shown | User clicks a page element | Toolbar traverses up from clicked element to find nearest semantic container (section, nav, article, aside, header, footer, main, or element with role attribute). Dashed teal border overlay appears around selected container. |
| AC-M2 | Click on element with no semantic ancestor within 5 levels | Smart-snap fallback | Snaps to nearest ancestor div with width > 50px AND height > 50px. |
| AC-M3 | Container selected | Overlay visible | Overlay shows: tag badge (e.g., "section"), CSS selector label, dimensions. Drag handles at 4 corners + 4 midpoints. |
| AC-M4 | Container selected with drag handles | User drags a handle | Selection boundary resizes in real-time. Updated bounding box stored. |
| AC-M5 | Container selected | Data captured | Lightweight capture: bounding_box (x, y, width, height), screenshot_dataurl (cropped), computed styles (box model, colors, fonts, borders only). |
| AC-M6 | Multiple components selected | Component list in panel | Each component shown as a row: tag badge + selector + dimensions. Remove (x) button. |
| AC-M7 | Component in list | User hovers entry | Component highlighted on page with dashed overlay. Scrolled into view if needed. |

### Step 2 — Add Instructions

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M8 | Step 2 shown | User views component list | Each component has a text input field for instructions. Placeholder: "Add notes (e.g., sticky header, animated)". |
| AC-M9 | User types instruction | Data stored | Instruction saved to __xipeRefData.components[n].instruction. |
| AC-M10 | User leaves instruction empty | Proceed to Step 3 | Allowed. Empty instruction is valid (not all components need notes). |

### Step 3 — Analyze (Agent Rubric)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M11 | Step 3, user clicks "Analyze" | Data sent to agent | __xipeRefReady set true with mode = "mockup". Agent reads component data. Toast: "Analyzing components..." (progress). |
| AC-M12 | Agent evaluates components | Rubric assessment | Agent scores 5 dimensions per component: layout structure, typography, color palette, spacing/sizing, visual effects. Each scored confident/uncertain/missing. |
| AC-M13 | Any dimension scored "missing" | Agent needs more data | Agent writes __xipeRefCommand: { action: "deep_capture", target: "comp-001" }. Toolbar captures full computed styles + outer HTML for that component. Sets __xipeRefReady when done. |
| AC-M14 | Deep capture requested | Toolbar executes | html_css.level changes from "minimal" to "deep". Full computed_styles and outer_html captured. Toast: "Capturing detailed styles for {selector}..." |
| AC-M15 | All dimensions confident | Analysis complete | Toast: "Analysis complete. Ready to generate." Step 4 enabled. |
| AC-M16 | Agent requests deep capture but element no longer exists (removed from DOM) | Error case | Toast: "Element not found — may have been removed." Component marked with warning. Agent proceeds with available data. |

### Step 4 — Generate Mockup

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M17 | Step 4, user clicks "Generate" | Step 4a: Persist | All metadata (screenshots, HTML/CSS, dimensions, instructions, analysis) saved via FEATURE-033 MCP save_uiux_reference BEFORE generation. Toast: "Saving reference data..." |
| AC-M18 | Data persisted | Step 4b: Generate | Agent invokes mockup creator skill. Toast: "Generating mockup..." (progress). |
| AC-M19 | Mockup generated | Validation | Agent takes screenshot of generated mockup, compares to original component screenshots. Comparison method and threshold defined by agent (targeting ~90% match). |
| AC-M20 | Match below threshold | Iteration loop | Agent re-analyzes, adjusts, regenerates. Max 3 auto-iterations. Toast: "Refining mockup (attempt 2/3)..." |
| AC-M21 | 3 iterations exhausted, still below threshold | Human approval | Agent asks user: "Mockup quality is below target after 3 attempts. Approve current result or stop?" |
| AC-M22 | Mockup approved or passes threshold | Completion | Toast: "Mockup generated successfully." (success). |
| AC-M23 | No components selected | User clicks "Generate" | Button disabled. Tooltip: "Select at least one component first." |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-M1 | Smart-snap: on click, traverse parentElement up to 5 levels looking for semantic tags (section, nav, article, aside, header, footer, main) or elements with role attribute. | P0 |
| FR-M2 | Fallback: if no semantic element found, select nearest ancestor div with offsetWidth > 50 AND offsetHeight > 50. | P0 |
| FR-M3 | Overlay: dashed teal border (2px) around selected container. Tag badge top-left. CSS selector label. 8 drag handles (corners + midpoints). | P0 |
| FR-M4 | Drag handles resize selection boundary. Store updated bounding_box. Re-crop screenshot on resize. | P0 |
| FR-M5 | Lightweight capture per component: bounding_box via getBoundingClientRect(), screenshot via canvas crop or CDP, computed styles (limited: display, position, flexbox/grid props, width, height, margin, padding, border, background, color, font-family, font-size, font-weight, line-height, box-shadow, border-radius, opacity). | P0 |
| FR-M6 | Store in __xipeRefData.components[] with auto-increment ID (comp-001, comp-002...). | P0 |
| FR-M7 | Per-component instruction: free-text input stored in components[n].instruction. | P0 |
| FR-M8 | "Analyze" button sends data to agent. Agent evaluates 5-dimension rubric. | P0 |
| FR-M9 | Deep capture command: agent sends __xipeRefCommand { action: "deep_capture", target: "comp-001" }. Toolbar captures all getComputedStyle() properties + element.outerHTML. Updates html_css.level to "deep". | P0 |
| FR-M10 | Step 4a: save all data via MCP save_uiux_reference before generation. | P0 |
| FR-M11 | Step 4b: agent generates mockup. Screenshot comparison determines quality. Max 3 auto-iterations on failure. | P1 |
| FR-M12 | Component list in panel: tag badge + selector (truncated) + dimensions. Remove (x) button. Hover highlights on page. | P0 |
| FR-M13 | Wizard step navigation: Next/Back. Current step in progress bar (1-4). | P1 |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-M1 | Smart-snap detection within 50ms of click (DOM traversal). | P0 |
| NFR-M2 | Lightweight capture (styles + screenshot crop) within 200ms per component. | P0 |
| NFR-M3 | Deep capture (full computed styles + outerHTML) within 500ms per component. | P0 |
| NFR-M4 | Overlay rendering at 60fps during drag-resize. | P1 |
| NFR-M5 | Maximum 20 components per session to keep payload manageable. | P1 |

## UI/UX Requirements

### Smart-Snap Overlay
- Dashed teal border (2px, #10b981) around selected container
- Tag badge: top-left, small pill (e.g., "section"), accent background, white text
- CSS selector label: top-right, mono font, truncated
- 8 drag handles: small squares (8x8px) at corners and midpoints, accent color, cursor: resize

### Component List
- Vertical list in panel content area
- Each row: tag badge + truncated selector + "WxH" dimensions
- Remove (x) on hover
- Text input for instructions below each entry (collapsible)

### Wizard Progress
- Step indicator bar at top: 4 steps with labels
- Active step highlighted. Completed steps show checkmark.
- Next/Back buttons at bottom of content area

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-030-B v2.0 | Internal | Toolbar shell: content area, toast API, data schema, __xipeRefReady, __xipeRefCommand |
| FEATURE-033 | Internal | MCP save_uiux_reference for Step 4a persistence |
| Mockup creator skill | External | Downstream skill for Step 4b generation (may need creation) |
| Chrome DevTools MCP | External | take_screenshot for component screenshots if canvas crop insufficient |

## Business Rules

| ID | Rule |
|----|------|
| BR-M1 | Components persist across mode switches (shared data store). |
| BR-M2 | Metadata must be saved (Step 4a) before generation starts (Step 4b). |
| BR-M3 | Max 3 auto-iterations for mockup validation. Then human approval required. |
| BR-M4 | Deep capture only triggered by agent request, not by user. |
| BR-M5 | Instructions are optional. Empty instruction is valid. |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| Click on body or html element | Skip — too broad. Toast: "Please click a more specific element." |
| Click on toolbar itself | Ignored. Toolbar elements excluded from snap detection. |
| Element removed from DOM after selection | Component marked with warning icon. Agent uses cached data. |
| Very large component (e.g., full-page section) | Allowed but toast warning if bounding_box > 80% of viewport. |
| Drag handle moved to invalid size (< 10px) | Minimum size enforced: 10x10px. |
| Deep capture on cross-origin iframe content | Not supported. Toast warning. Agent proceeds with available data. |
| 20+ components selected | Toast: "Maximum 20 components per session." Additional clicks ignored. |

## Out of Scope

- Color picking (FEATURE-030-B-THEME)
- Brand theme generation
- Mockup skill creation (downstream — identified as potentially needed)
- Screenshot comparison algorithm selection (TBD in technical design)
- Cross-origin iframe component capture
- Video frame capture as components

## Technical Considerations

- Smart-snap traversal should check element.tagName against a whitelist of semantic tags. Also check for ARIA role attributes.
- Lightweight capture uses getComputedStyle() with a limited property list to keep payload small. Deep capture sends all properties.
- Screenshot crop: use offscreen canvas to crop the full-page screenshot to the component bounding box, or use CDP take_screenshot with element uid.
- The __xipeRefCommand deep_capture flow: agent writes command -> toolbar polls (1s) -> toolbar captures -> sets __xipeRefReady -> agent reads enriched data.
- This feature registers itself with the toolbar shell via the extension point API (FR-16 of FEATURE-030-B).
- Mockup comparison method (pixel-diff, SSIM, perceptual hash) to be determined in technical design.

## Open Questions

None.
