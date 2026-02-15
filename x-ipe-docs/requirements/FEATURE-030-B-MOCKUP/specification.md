# Feature Specification: Copy Design as Mockup Mode

> Feature ID: FEATURE-030-B-MOCKUP
> Version: v2.3
> Status: Refined
> Last Updated: 02-15-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v2.0 | 02-14-2026 | Initial specification — 4-step wizard for component capture and mockup generation | [CR-002](../FEATURE-030-B/CR-002.md) |
| v2.1 | 02-14-2026 | Button lifecycle, screenshot validation, decoupled analyze/generate, agent auto-collection | [CR-001](./CR-001.md) |
| v2.2 | 02-15-2026 | Bounding box scope enforcement, 99% validation with property-level checks, analyze-phase data persistence, 6-dimension rubric (add Static Resources) | [CR-002](./CR-002.md) |
| v2.3 | 02-15-2026 | Area semantics (snap as anchor + discover all elements), exact area screenshots, structured folder output, resource auto-download | [CR-003](./CR-003.md) |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Toolbar v2.0 Mockup Mode | HTML | [mockups/toolbar-v2-v1.html](mockups/toolbar-v2-v1.html) | Mockup mode view: smart-snap overlay on semantic containers, component list, 4-step wizard progress | current |

## Overview

FEATURE-030-B-MOCKUP provides the "Copy Design as Mockup" mode within the v2.0 toolbar. It is a 4-step wizard that guides users through capturing page areas and generating pixel-perfect mockup replications:

1. **Select Areas** — Click to smart-snap to semantic HTML containers (as initial anchor), then resize via drag handles to define the capture region
2. **Add Instructions** — Attach free-text notes per area for agent context
3. **Analyze** — Agent discovers all DOM elements within the selected area's bounding box, evaluates via a 6-dimension rubric, captures exact area screenshots, downloads static resources, and produces structured folder output. If reflection shows insufficient data, agent auto-collects additional resources via Chrome DevTools.
4. **Generate** — Persist metadata via MCP, generate mockup with versioned filenames, validate via screenshot comparison (max 3 iterations)

Analysis and generation are decoupled — the user controls when to trigger each action via dedicated buttons. Both buttons have agent-controlled enable/disable states and processing animations to provide clear feedback on agent activity.

This feature renders its UI into the mode content area provided by FEATURE-030-B (toolbar shell).

## User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-M1 | As a user, I want to click a page element and have the toolbar automatically select the nearest semantic container as an initial anchor, so that I have a good starting point for my area selection. | P0 |
| US-M2 | As a user, I want drag handles on the selected area so that I can adjust the capture boundary beyond the snapped element. | P0 |
| US-M3 | As a user, I want to add text instructions per area (e.g., "sticky header" or "parallax scroll"), so that the agent has context for replication. | P0 |
| US-M4 | As a user, I want the agent to analyze my captured areas by discovering all DOM elements within the bounding box, so that the mockup includes everything visible in my selection. | P0 |
| US-M5 | As a user, I want the agent to generate a mockup that closely matches the original, with automatic re-tries if the match is below threshold. | P1 |
| US-M6 | As a user, I want my captured data saved before mockup generation starts, so that I do not lose work if generation fails. | P0 |
| US-M7 | As a user, I want the Analyze and Generate buttons to show processing state when the agent is working, so that I know the system is busy. | P0 | (v2.1) |
| US-M8 | As a user, I want to analyze my selections first and then decide separately when to generate a mockup, so that I can iterate on my selections before committing to generation. | P0 | (v2.1) |
| US-M9 | As a user, I want each generated mockup saved as a separate versioned file, so that I can compare iterations without losing previous results. | P1 | (v2.1) |
| US-M10 | As a user, I want the agent to automatically collect and download all static resources (images, SVGs, fonts, canvas, video) within my selected area, so that the mockup uses actual assets for pixel-perfect accuracy. | P0 | (v2.3) |
| US-M11 | As a user, I want the agent to validate that its screenshot captures exactly the rectangular area I selected (not a DOM element's bounds), so that mockup generation uses correct visual data. | P0 | (v2.3) |
| US-M12 | As a user, I want the analysis to produce a structured folder output (page-element-references/, mimic-strategy.md, full-page.png) so that all reference data is organized and reusable. | P0 | (v2.3) |
| US-M13 | As a user, I want the agent to discover all DOM elements within my selected area's bounding box (not just the snapped element), so that sibling, overlapping, and background elements are all captured. | P0 | (v2.3) |

## Acceptance Criteria

### Step 1 — Select Areas (Smart-Snap Anchor)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M1 | Mockup mode active, Step 1 shown | User clicks a page element | Toolbar traverses up from clicked element to find nearest semantic container (section, nav, article, aside, header, footer, main, or element with role attribute). Dashed teal border overlay appears around selected container. This is the initial snap anchor. |
| AC-M2 | Click on element with no semantic ancestor within 5 levels | Smart-snap fallback | Snaps to nearest ancestor div with width > 50px AND height > 50px. |
| AC-M3 | Container selected | Overlay visible | Overlay shows: tag badge (e.g., "section"), CSS selector label, dimensions. Drag handles at 4 corners + 4 midpoints. |
| AC-M4 | Container selected with drag handles | User drags a handle | Selection boundary resizes in real-time. Updated bounding box stored. The area may now extend beyond the original snapped element. |
| AC-M5 | Container selected | Data captured | Lightweight capture: bounding_box (x, y, width, height), screenshot_dataurl (cropped to bounding_box), computed styles (box model, colors, fonts, borders only). snap_element selector stored as reference. |
| AC-M6 | Multiple areas selected | Area list in panel | Each area shown as a row: tag badge + selector + dimensions. Remove (x) button. |
| AC-M7 | Area in list | User hovers entry | Area highlighted on page with dashed overlay. Scrolled into view if needed. |

### Step 2 — Add Instructions

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M8 | Step 2 shown | User views area list | Each area has a text input field for instructions. Placeholder: "Add notes (e.g., sticky header, animated)". |
| AC-M9 | User types instruction | Data stored | Instruction saved to __xipeRefData.areas[n].instruction. |
| AC-M10 | User leaves instruction empty | Proceed to Step 3 | Allowed. Empty instruction is valid (not all areas need notes). |

### Step 3 — Analyze (Agent Rubric)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M11 | Step 3, user clicks "Analyze" | Data sent to agent | __xipeRefReady set true with mode = "mockup" and action = "analyze". Analyze button disabled immediately. Processing spinner shown on button. __xipeAnalyzeEnabled set to false. Toast: "Analyzing areas..." (progress). |
| AC-M12 | Agent evaluates areas | Rubric assessment | Agent discovers all DOM elements within each area's bounding_box. Scores 6 dimensions per area: layout structure, typography, color palette, spacing/sizing, visual effects, static resources. Each dimension has detailed sub-checks. Scored confident/uncertain/missing per sub-check. |
| AC-M13 | Any dimension scored "missing" | Agent needs more data | Agent writes __xipeRefCommand: { action: "deep_capture", target: "area-1" }. Toolbar captures full computed styles + outer HTML for that area's snap element. Sets __xipeRefReady when done. |
| AC-M14 | Deep capture requested | Toolbar executes | html_css.level changes from "minimal" to "deep". Full computed_styles and outer_html captured for snap element. Toast: "Capturing detailed styles for {selector}..." |
| AC-M15 | All dimensions confident | Analysis complete | Toast: "Analysis complete. Ready to generate." Agent sets __xipeAnalyzeEnabled = true and __xipeGenerateMockupEnabled = true. Both buttons re-enabled. Processing spinner removed from Analyze. |
| AC-M16 | Agent requests deep capture but element no longer exists (removed from DOM) | Error case | Toast: "Element not found — may have been removed." Area marked with warning. Agent proceeds with available data. |

### Step 3a — Exact Area Screenshots (v2.3)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M24 | Agent captures screenshot during analysis | Screenshot captured | Agent uses the area's bounding_box coordinates (x, y, width, height) to capture an exact rectangular screenshot of the selected region. Does NOT use a DOM element UID — uses coordinate-based cropping. |
| AC-M25 | Screenshot dimensions differ from bounding_box by > 1px | Dimension mismatch detected | Agent scrolls to ensure area is in viewport, takes viewport screenshot, and crops to exact bounding_box coordinates. Validates cropped dimensions match within 1px. |
| AC-M26 | Screenshot matches bounding_box within tolerance (≤ 1px) | Validation passes | Agent proceeds with the screenshot for mockup generation. Screenshot saved as `screenshots/{area-id}.png`. |

### Step 3b — Area Element Discovery & Resource Download (v2.3)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M27 | Agent analyzes a selected area | Element discovery | Agent uses evaluate_script to enumerate ALL DOM elements whose getBoundingClientRect() intersects the area's bounding_box. This includes siblings, overlapping positioned elements, background layers — not just the snap element's subtree. |
| AC-M28 | DOM elements discovered within area | Resource classification | Agent classifies each element: `<img>` (src, srcset), `<svg>` (inline/external), `<canvas>`, `<video>` (poster, src), background-image URLs, @font-face URLs. |
| AC-M29 | Resources classified | Resource download | Agent downloads each static resource to `resources/` folder: `{area-id}-img-{N}.{ext}`, `{area-id}-svg-{N}.svg`, `{area-id}-font-{N}.woff2`, `{area-id}-canvas-{N}.png`. Uses evaluate_script with fetch() or get_network_request. |
| AC-M30 | Resources downloaded | CSS capture | Agent extracts computed styles for ALL discovered elements (not just snap element). Saves relevant CSS rules to `resources/{area-id}-styles.css`. |
| AC-M42 | All resources collected | Re-evaluation | Agent re-runs 6-dimension rubric with enriched data (all elements + downloaded resources). If still insufficient, proceeds with best available data and notes gaps. |

### Step 3c — Analyze-Generate Decoupling (v2.1)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M31 | Analysis complete, both buttons re-enabled | Agent continues polling | Agent resumes polling __xipeRefReady (3s interval) to detect next user action. Does NOT auto-trigger mockup generation. |
| AC-M32 | User clicks "Analyze" again after analysis | Re-analysis triggered | Agent receives new __xipeRefData with action = "analyze". Runs full analysis cycle again (may include new/modified areas). |
| AC-M33 | User clicks "Generate Mockup" after analysis | Generation triggered | Agent receives __xipeRefData with action = "generate". Proceeds to Step 4. |

### Step 4 — Generate Mockup

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M17 | Step 4, user clicks "Generate Mockup" | Button state change | Generate Mockup button disabled immediately. Processing spinner shown on button. __xipeGenerateMockupEnabled set to false. Toast: "Saving reference data..." |
| AC-M18 | Data persisted | Step 4b: Generate | Agent invokes mockup creator skill. Toast: "Generating mockup..." (progress). |
| AC-M19 | Mockup generated | Validation | Agent validates mockup against original using property-level checks: exact hex color match, font-family/size/weight match, spacing within 1px, layout dimensions within 1px, static resource URLs preserved. Target: 99% visual match. |
| AC-M20 | Match below 99% threshold | Iteration loop | Agent identifies specific property mismatches, fixes them, and regenerates. Max 3 auto-iterations. Toast: "Refining mockup (attempt 2/3)..." |
| AC-M21 | 3 iterations exhausted, still below threshold | Human approval | Agent asks user: "Mockup quality is below target after 3 attempts. Approve current result or stop?" |
| AC-M22 | Mockup approved or passes threshold | Completion | Toast: "Mockup generated successfully." (success). Agent sets __xipeGenerateMockupEnabled = true. Processing spinner removed from Generate Mockup button. |
| AC-M23 | No areas selected | User clicks "Generate" | Button disabled. Tooltip: "Select at least one area first." |

### Step 4a — Versioned Mockup Files (v2.1)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M34 | Agent generates a mockup file | File naming | Mockup saved with versioned filename (e.g., mockup-v1.html, mockup-v2.html). Agent scans existing files to determine next version number. |
| AC-M35 | Previous mockup versions exist | New generation | New file does NOT overwrite existing versions. All previous versions preserved for comparison. |
| AC-M36 | Generation complete | Post-generation state | Agent sets __xipeGenerateMockupEnabled = true. Agent resumes polling __xipeRefReady for further user actions (analyze again or generate again). |

### Bounding Box Scope Enforcement (v2.2)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M37 | User selected an area with a specific bounding box | Agent generates mockup | Mockup reproduces ONLY the content within the selected area's bounding box. Does NOT include page-level elements (navigation, footer, header) unless they are within the area's bounds. |
| AC-M38 | Area has outer_html captured for discovered elements | Agent generates mockup | Agent uses discovered elements' outer_html as the authoritative content source. Mockup viewport matches area dimensions (from bounding_box), not the full page. |

### Analyze-Phase Data Persistence (v2.2)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M39 | Analysis completes (all dimensions evaluated) | Before re-enabling buttons | Agent calls save_uiux_reference with current analysis data (screenshots, area data, rubric results). Data is persisted to idea folder immediately. |
| AC-M40 | Session crashes between analyze and generate phases | Recovery | All analysis artifacts are already saved in the idea folder's uiux-references/ structure. No data loss. |

### 6-Dimension Validation Rubric (v2.2)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M41 | Agent evaluates an area | Rubric assessment | Agent scores 6 dimensions with detailed sub-checks across ALL discovered elements: (1) Layout: display, position, flex/grid, dimensions; (2) Typography: font-family, size, weight, line-height, letter-spacing, color; (3) Color Palette: background, text, border, shadow — exact hex match; (4) Spacing: margin, padding, gap — within 1px; (5) Visual Effects: shadows, borders, gradients, opacity, border-radius; (6) Static Resources: fonts loaded, icons/SVGs, images with source URLs, background images. |

### Area Semantics — Snap as Anchor (v2.3)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M43 | User clicks a page element in Step 1 | Smart-snap occurs | The snapped DOM element is stored as `area.snap_element` (selector + tag). This is the initial anchor — NOT the sole content of the area. |
| AC-M44 | Area bounding_box differs from snap element's getBoundingClientRect() | User resized via drag handles | The area's bounding_box is authoritative. During analysis, agent discovers elements using bounding_box coordinates, not the snap element's subtree. |
| AC-M45 | Agent analyzes an area | Element discovery | Agent enumerates ALL DOM elements within the bounding_box: snap element, its siblings, overlapping positioned elements (position: absolute/fixed), background layers, and elements from parent containers that visually appear within the area. |

### Structured Folder Output (v2.3)

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-M46 | Analysis completes for an area | Structured output produced | Agent produces the following folder structure in `uiux-references/`: `screenshots/full-page.png`, `screenshots/{area-id}.png`, `page-element-references/summarized-uiux-reference.md`, `page-element-references/resources/{area-id}-structure.html`, `page-element-references/resources/{area-id}-styles.css`, `mimic-strategy.md`. |
| AC-M47 | Agent calls save_uiux_reference | Full data sent | Agent sends complete data including full outer_html and computed_styles for all discovered elements, enabling the MCP service to generate structured output automatically. |
| AC-M48 | Structured output generated | Verification | Agent verifies that `page-element-references/` folder, `mimic-strategy.md`, and `screenshots/full-page.png` exist after save. If missing, agent creates them manually from collected data. |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-M1 | Smart-snap: on click, traverse parentElement up to 5 levels looking for semantic tags (section, nav, article, aside, header, footer, main) or elements with role attribute. Snapped element stored as area.snap_element (anchor reference). | P0 |
| FR-M2 | Fallback: if no semantic element found, select nearest ancestor div with offsetWidth > 50 AND offsetHeight > 50. | P0 |
| FR-M3 | Overlay: dashed teal border (2px) around selected container. Tag badge top-left. CSS selector label. 8 drag handles (corners + midpoints). | P0 |
| FR-M4 | Drag handles resize selection boundary. Store updated bounding_box. Re-crop screenshot on resize. Area may extend beyond snap element. | P0 |
| FR-M5 | Lightweight capture per area: bounding_box via getBoundingClientRect() of snap element (initial), screenshot cropped to bounding_box, computed styles of snap element (limited: display, position, flexbox/grid props, width, height, margin, padding, border, background, color, font-family, font-size, font-weight, line-height, box-shadow, border-radius, opacity). | P0 |
| FR-M6 | Store in __xipeRefData.areas[] with auto-increment ID (area-1, area-2...). | P0 |
| FR-M7 | Per-area instruction: free-text input stored in areas[n].instruction. | P0 |
| FR-M8 | "Analyze" button sends data to agent. Agent evaluates 6-dimension rubric (layout, typography, color palette, spacing, visual effects, static resources) across ALL discovered elements in each area. | P0 |
| FR-M9 | Deep capture command: agent sends __xipeRefCommand { action: "deep_capture", target: "area-1" }. Toolbar captures all getComputedStyle() properties + element.outerHTML for the snap element. Updates html_css.level to "deep". | P0 |
| FR-M10 | Step 4a: save all data via MCP save_uiux_reference before generation. | P0 |
| FR-M11 | Step 4b: agent generates mockup. Screenshot comparison determines quality. Max 3 auto-iterations on failure. | P1 |
| FR-M12 | Area list in panel: tag badge + selector (truncated) + dimensions. Remove (x) button. Hover highlights on page. | P0 |
| FR-M13 | Wizard step navigation: Next/Back. Current step in progress bar (1-4). | P1 |
| FR-M14 | Global button control variables: window.__xipeAnalyzeEnabled (boolean, default false) and window.__xipeGenerateMockupEnabled (boolean, default false). Toolbar polls these variables (500ms interval) and updates button disabled state accordingly. Agent sets these to true/false to control button availability. | P0 | (v2.1) |
| FR-M15 | Button processing animation: When Analyze or Generate button is clicked, show a CSS spinner animation on the button and set disabled state. Remove spinner when agent re-enables the button variable. | P0 | (v2.1) |
| FR-M16 | Action field in __xipeRefData: When Analyze is clicked, set __xipeRefData.action = "analyze". When Generate Mockup is clicked, set __xipeRefData.action = "generate". Agent uses this field to distinguish user intent. | P0 | (v2.1) |
| FR-M17 | Exact area screenshot: Agent uses the area's bounding_box coordinates (x, y, width, height) to capture a coordinate-based screenshot. Does NOT use DOM element UID. Scrolls to ensure area is in viewport, captures viewport screenshot, crops to exact bounding_box. Validates dimensions match within 1px. | P0 | (v2.3) |
| FR-M18 | Area element discovery: Agent uses evaluate_script to enumerate ALL DOM elements whose getBoundingClientRect() intersects the area's bounding_box. Includes siblings, overlapping positioned elements, background layers — not just the snap element's subtree. | P0 | (v2.3) |
| FR-M19 | Versioned mockup files: Agent generates mockup files with auto-incrementing version suffix (mockup-v1.html, mockup-v2.html, ...). Scans existing files to determine next version. Never overwrites existing versions. | P1 | (v2.1) |
| FR-M20 | Decoupled analyze/generate polling: After analysis completes, agent resumes polling __xipeRefReady. Does NOT auto-trigger generation. Waits for user to click either Analyze (re-analyze) or Generate Mockup (proceed to generation). | P0 | (v2.1) |
| FR-M21 | Bounding box scope enforcement: Agent generates mockup containing ONLY elements discovered within the selected area's bounding_box. Uses collected outer_html as authoritative content. Mockup viewport matches area bounding_box dimensions. | P0 | (v2.2) |
| FR-M22 | Analyze-phase persistence: After analysis completes (before re-enabling buttons), agent calls save_uiux_reference with screenshots, area data, and rubric results. Data persisted immediately to prevent loss. | P0 | (v2.2) |
| FR-M23 | 6-dimension rubric: Agent evaluates layout, typography, color palette, spacing, visual effects, and static resources (6th dimension: fonts, icons, images, SVGs with source URLs) across all discovered elements. | P0 | (v2.2) |
| FR-M24 | Property-level validation: Mockup validation uses per-property checks — exact hex for colors, font match, 1px spacing tolerance, resource URL match. Target: 99% accuracy. Max 3 iterations fixing specific mismatches. | P0 | (v2.2) |
| FR-M25 | Resource auto-download: Agent downloads ALL static resources within each area's bounding_box to resources/ folder. Resources include: images ({area-id}-img-{N}.{ext}), SVGs ({area-id}-svg-{N}.svg), fonts ({area-id}-font-{N}.woff2), canvas ({area-id}-canvas-{N}.png). Uses evaluate_script with fetch() or get_network_request. | P0 | (v2.3) |
| FR-M26 | Structured folder output: Analysis produces complete uiux-references/ structure: screenshots/full-page.png, screenshots/{area-id}.png, page-element-references/summarized-uiux-reference.md, page-element-references/resources/{area-id}-structure.html, page-element-references/resources/{area-id}-styles.css, mimic-strategy.md. Agent takes full-page screenshot during analysis. | P0 | (v2.3) |
| FR-M27 | Full-page screenshot: Agent takes a full-page screenshot (take_screenshot with fullPage: true) and saves to screenshots/full-page.png as part of the analysis flow. | P0 | (v2.3) |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-M1 | Smart-snap detection within 50ms of click (DOM traversal). | P0 |
| NFR-M2 | Lightweight capture (styles + screenshot crop) within 200ms per area. | P0 |
| NFR-M3 | Deep capture (full computed styles + outerHTML) within 500ms per area. | P0 |
| NFR-M4 | Overlay rendering at 60fps during drag-resize. | P1 |
| NFR-M5 | Maximum 20 areas per session to keep payload manageable. | P1 |
| NFR-M6 | Resource download timeout: 10s per resource. Skip on timeout with warning. | P1 | (v2.3) |

## UI/UX Requirements

### Smart-Snap Overlay
- Dashed teal border (2px, #10b981) around selected container
- Tag badge: top-left, small pill (e.g., "section"), accent background, white text
- CSS selector label: top-right, mono font, truncated
- 8 drag handles: small squares (8x8px) at corners and midpoints, accent color, cursor: resize

### Area List
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
| Chrome DevTools MCP | External | take_screenshot, evaluate_script for area screenshots, element discovery, and resource download |

## Business Rules

| ID | Rule |
|----|------|
| BR-M1 | Areas persist across mode switches (shared data store). |
| BR-M2 | Metadata must be saved (Step 4a) before generation starts (Step 4b). |
| BR-M3 | Max 3 auto-iterations for mockup validation. Then human approval required. |
| BR-M4 | Deep capture only triggered by agent request, not by user. |
| BR-M5 | Instructions are optional. Empty instruction is valid. |
| BR-M6 | Analyze and Generate Mockup buttons are agent-controlled. Default state is disabled. Only the agent can enable them (by setting global variables). | (v2.1) |
| BR-M7 | Analysis does not auto-trigger generation. User must explicitly click Generate Mockup. | (v2.1) |
| BR-M8 | Mockup files are append-only (versioned). No file is ever overwritten. | (v2.1) |
| BR-M9 | Agent must validate screenshot accuracy against bounding_box coordinates (not DOM element dimensions) before using it for mockup generation. | (v2.3) |
| BR-M10 | The snap element is an anchor reference, not the sole content source. Area content = all elements within bounding_box. | (v2.3) |
| BR-M11 | All static resources within an area must be downloaded to resources/ folder during analysis. Mockup generation uses local resource files. | (v2.3) |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| Click on body or html element | Skip — too broad. Toast: "Please click a more specific element." |
| Click on toolbar itself | Ignored. Toolbar elements excluded from snap detection. |
| Snap element removed from DOM after selection | Area marked with warning icon. Agent uses cached bounding_box and any already-captured data. |
| Very large area (e.g., full-page section) | Allowed but toast warning if bounding_box > 80% of viewport. |
| Drag handle moved to invalid size (< 10px) | Minimum size enforced: 10x10px. |
| Deep capture on cross-origin iframe content | Not supported. Toast warning. Agent proceeds with available data. |
| 20+ areas selected | Toast: "Maximum 20 areas per session." Additional clicks ignored. |
| Area bounding_box extends beyond page bounds | Clamp coordinates to document dimensions. Screenshot captures only visible portion. | (v2.3) |
| Resource download blocked by CORS | Agent uses evaluate_script with fetch() which runs in page context (same-origin). For truly cross-origin resources, log warning and skip. | (v2.3) |
| Resource download timeout (>10s) | Skip resource with warning. Continue with remaining resources. | (v2.3) |
| Area contains no DOM elements (blank space) | Agent captures screenshot only. No elements to discover. Notes gap in analysis. | (v2.3) |
| User clicks Analyze repeatedly before agent finishes | Button is disabled during processing — additional clicks ignored. | (v2.1) |
| User clicks Generate before analysis completes | Button is disabled (agent-controlled). Cannot trigger until agent enables it. | (v2.1) |

## Out of Scope

- Color picking (FEATURE-030-B-THEME)
- Brand theme generation
- Mockup skill creation (downstream — identified as potentially needed)
- Screenshot comparison algorithm selection (TBD in technical design)
- Cross-origin iframe area capture
- Video playback capture (poster/thumbnail only)

## Technical Considerations

- Smart-snap traversal should check element.tagName against a whitelist of semantic tags. Also check for ARIA role attributes. Snapped element stored as `area.snap_element`.
- Lightweight capture uses getComputedStyle() with a limited property list to keep payload small. Deep capture sends all properties.
- (v2.3) Exact area screenshot: scroll area into viewport, take viewport screenshot via take_screenshot(), use evaluate_script to crop canvas to bounding_box coordinates. Do NOT rely on DOM element UID matching.
- (v2.3) Area element discovery: `document.querySelectorAll('*')` filtered by `getBoundingClientRect()` intersection with area bounding_box. Also check `position: absolute/fixed` elements that may overlap from outside the DOM tree.
- (v2.3) Resource download: Use evaluate_script with page-context `fetch()` to download same-origin resources as data URLs. Convert to files via the agent. For images, capture `naturalWidth`/`naturalHeight` metadata.
- (v2.3) Structured folder output: Agent sends full outer_html and computed_styles for all discovered elements to save_uiux_reference. The MCP service generates page-element-references/ and mimic-strategy.md automatically.
- The __xipeRefCommand deep_capture flow: agent writes command -> toolbar polls (1s) -> toolbar captures -> sets __xipeRefReady -> agent reads enriched data.
- This feature registers itself with the toolbar shell via the extension point API (FR-16 of FEATURE-030-B).
- Mockup comparison method (pixel-diff, SSIM, perceptual hash) to be determined in technical design.
- (v2.1) Button control via global variables: toolbar uses setInterval (500ms) to poll __xipeAnalyzeEnabled and __xipeGenerateMockupEnabled. Agent uses evaluate_script to set these. Avoids bi-directional event coupling.
- (v2.1) Auto-collection of CSS stylesheets: agent uses list_network_requests(resourceTypes: ["stylesheet"]) to discover loaded stylesheets, then get_network_request to retrieve content.
- (v2.1) The action field ("analyze" vs "generate") in __xipeRefData allows the agent to distinguish user intent without needing separate signaling channels.

## Open Questions

None.
