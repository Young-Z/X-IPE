# Lesson Learned — x-ipe-tool-uiux-reference

---

## LL-001

**Date:** 2026-02-14
**Severity:** major
**Source:** human_feedback
**Status:** raw
**Task ID:** N/A (ad-hoc uiux-reference execution)

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  Executing UIUX reference capture on https://www.baidu.com.
  User selected element elem-001 (div.s_form_wrapper.soutu-env-mac) via the toolbar.
  Agent needed to take an element-level screenshot in step 8 of execute_reference.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "207. Baidu-Reference-v3"
```

### Observed Behavior

```
Step 8 of execute_reference: Agent took a11y snapshot to find a matching UID for
the selected element (div.s_form_wrapper.soutu-env-mac, bounding_box 800×384).

The element was a generic <div> with no ARIA role, so it was NOT exposed as an
independent node in the a11y tree — it had no UID.

Agent fell back to using uid=1_23 (a child textbox element inside the div) as a
proxy. This produced a screenshot of only the search input field (~11KB), not the
full form wrapper container (search box + Baidu logo + hot search list).

Result: elem-001.png was a tiny crop of the textbox, not the intended element.
```

### Expected Behavior

```
The agent should capture a screenshot of the exact element the user selected
(div.s_form_wrapper.soutu-env-mac), which includes the Baidu logo, search bar,
"百度一下" button, "文心助手" link, and the hot search content area (~140KB).
```

### Ground Truth

```
When a selected element has no UID in the a11y snapshot (common for generic
<div>, <section>, <span> without ARIA roles), the agent should:

1. Use evaluate_script to temporarily add role="region" and
   aria-label="xipe-target-element" to the target element via its CSS selector
2. Take a fresh a11y snapshot — the element now appears with a UID
3. Use take_screenshot(uid: found_uid) for the accurate element crop
4. Use evaluate_script to remove the temporary ARIA attributes (cleanup)

This approach was manually discovered and produced a correct 140KB screenshot
matching the full element bounding box.
```

### Proposed Improvement

```yaml
type: update_instruction
target: "SKILL.md → Operations → execute_reference → Step 8"
description: |
  Update step 8 to handle elements without UIDs in the a11y snapshot.
  Current step 8 only says "Use bounding_box to find matching node in snapshot"
  with a fallback of "IF matching UID found" → take screenshot, else skip.

  Add sub-steps for the "no matching UID" case:
  
  8c. IF no matching UID found by bounding_box comparison:
      i.   CALL evaluate_script to add role="region" and
           aria-label="xipe-target-element" to the element via its CSS selector
      ii.  CALL take_snapshot() to refresh the a11y tree
      iii. Find the node with aria-label="xipe-target-element" in the new snapshot
      iv.  CALL take_screenshot(uid: found_uid, filePath: ...)
      v.   CALL evaluate_script to remove the temporary ARIA attributes
  
  This ensures element-level screenshots work for generic DOM elements
  that lack semantic ARIA roles.

proposed_ac:
  should:
    - id: AC-C13
      category: content
      criterion: "Step 8 handles elements without a11y tree UIDs"
      test: content_check
      expected: "Describes fallback using temporary ARIA role injection"
```

---

## LL-002

**Date:** 2026-02-14
**Severity:** major
**Source:** human_feedback
**Status:** raw
**Task ID:** N/A (ad-hoc uiux-reference execution)

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  Color Picker on https://www.baidu.com fails to pick the correct color for:
  1. Baidu logo (red animated GIF) — picker returns black/blue instead of red
  2. "百度一下" button (blue background) — picker returns white instead of blue
inputs:
  url: "https://www.baidu.com"
  idea_folder: "207. Baidu-Reference-v3"
```

### Observed Behavior

```
The handleColorClick function uses this logic to determine color:

  const bgColor = computed.backgroundColor;
  const textColor = computed.color;
  const colorStr = (bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent')
    ? bgColor : textColor;

Two failure cases identified:

Case 1 — Baidu logo (animated GIF <img>):
  - e.target = <img> element
  - computed.backgroundColor = "rgba(0, 0, 0, 0)" (transparent — images have no CSS bg)
  - computed.color = "rgb(0, 0, 238)" (inherited default link blue)
  - Picker returns #0000ee (blue) — but the visible color is RED from the image content
  - Root cause: getComputedStyle cannot read pixel colors from <img>, <canvas>,
    <video>, SVG, or CSS gradients. The visible color exists in the rendered
    pixel data, not in CSS properties.

Case 2 — "百度一下" button (<input type="submit">):
  - e.target resolves to a DIFFERENT element due to z-index overlap!
  - The nav bar (#s-top-left, z-index: 100, position: absolute) overlaps the
    button area, so the click lands on the nav div instead of the button.
  - Nav div has backgroundColor = "rgba(0, 0, 0, 0)" and color = "rgb(0, 0, 0)"
  - Picker returns black — but the visible element is the blue button underneath.
  - Root cause: e.target is the topmost element in the stacking context, which
    may be a transparent overlay, not the visually dominant element.
```

### Expected Behavior

```
Case 1: Clicking on the Baidu logo should pick the dominant red color visible
in the GIF image (#de1021 or similar).

Case 2: Clicking on the "百度一下" button should pick the blue background
(#4e6ef2) that the user visually sees, not a transparent overlay's fallback.
```

### Ground Truth

```
The current color picker has two fundamental limitations:

LIMITATION 1 — Cannot extract colors from rendered pixel content:
  getComputedStyle only reads CSS property values. It cannot read:
  - Pixel colors inside <img>, <canvas>, <video> elements
  - Colors from CSS gradients (background-image: linear-gradient)
  - SVG fill/stroke colors rendered visually
  - Animated/dynamic colors

  Proper fix: Use a <canvas>-based pixel sampling approach:
  1. Render the target element (or a region around the click point) onto an
     offscreen <canvas> using html2canvas or drawImage
  2. Read the pixel color at the click coordinates via getImageData()
  3. This captures the actual rendered color regardless of source

  Alternative: Use the EyeDropper API (navigator.eyeDropper) where supported
  (Chromium 95+). This provides native pixel-level color picking.

LIMITATION 2 — e.target may not be the visually dominant element:
  When transparent overlays or high-z-index elements cover the target,
  e.target resolves to the overlay, not the visible element underneath.

  Proper fix: Walk up the e.target ancestor chain AND check
  document.elementsFromPoint(x, y) to find the first element with a
  non-transparent background color:
  1. Get all elements at click point: document.elementsFromPoint(e.clientX, e.clientY)
  2. Iterate through them (top to bottom in stacking order)
  3. For each element, check computed backgroundColor
  4. Return the first one with a non-transparent, non-default background
  5. Fall back to text color only if no visible background found

  This handles transparent navbars, modal overlays, and similar stacking issues.
```

### Proposed Improvement

```yaml
type: update_code
target: "references/toolbar-template.md → handleColorClick function"
description: |
  The color picker needs two enhancements to handle real-world pages:

  Enhancement 1 — Use elementsFromPoint for z-index awareness:
    Replace `const el = e.target` with:
    ```
    const elements = document.elementsFromPoint(e.clientX, e.clientY)
      .filter(el => !el.closest('.xipe-toolbar'));
    let el = elements[0];
    let colorStr = null;
    for (const candidate of elements) {
      const bg = getComputedStyle(candidate).backgroundColor;
      if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
        colorStr = bg;
        el = candidate;
        break;
      }
    }
    if (!colorStr) colorStr = getComputedStyle(el).color;
    ```

  Enhancement 2 — Canvas-based pixel sampling for images/canvas/gradients:
    When the target is <img>, <canvas>, <video>, or has background-image gradient:
    ```
    if (['IMG', 'CANVAS', 'VIDEO'].includes(el.tagName) ||
        getComputedStyle(el).backgroundImage !== 'none') {
      // Use canvas pixel sampling
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = 1; canvas.height = 1;
      // For images: ctx.drawImage(el, ...)
      // For gradients: render element region
      // Read pixel: ctx.getImageData(0, 0, 1, 1).data
    }
    ```

  Note: Full canvas-based approach has cross-origin limitations for external
  images. For MVP, Enhancement 1 alone fixes the majority of real-world cases.
  Enhancement 2 can be a Phase 2 improvement.

proposed_ac:
  should:
    - id: AC-C14
      category: content
      criterion: "Color picker uses elementsFromPoint for z-index-aware picking"
      test: content_check
      expected: "handleColorClick uses elementsFromPoint instead of e.target alone"
    - id: AC-C15
      category: content
      criterion: "Color picker documents image/canvas/gradient limitation"
      test: content_check
      expected: "Known limitation documented for pixel-rendered colors"
```

---

## LL-003

**Date:** 2026-02-14
**Severity:** critical
**Source:** human_feedback
**Status:** applied
**Task ID:** N/A (ad-hoc uiux-reference execution)

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  Color picker uses offscreen canvas + viewport screenshot for pixel sampling.
  Agent must inject a large base64 screenshot data URL (~40-350KB) into the page
  via evaluate_script. This is slow, unreliable, and causes CORS/mixed-content
  issues on HTTPS pages. The offscreen canvas approach also fails to track
  scroll/resize in real-time.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "208. Baidu-Reference-v4"
```

### Observed Behavior

```
1. Offscreen canvas color picker requires viewport screenshot injection
2. Screenshot data URL is 40-350KB — too large for single evaluate_script call
3. Agent tried multiple approaches: direct injection, local HTTP server (mixed
   content blocked), chunked injection (4+ calls)
4. Even when screenshot loads, it's a static snapshot — doesn't update on
   scroll/resize without re-injection
5. The entire process is slow, fragile, and wastes significant agent turns
```

### Expected Behavior

```
Color picking should work natively without requiring screenshot injection.
Should be fast, reliable, and work on any page regardless of CORS/CSP.
```

### Ground Truth

```
Replace offscreen canvas with EyeDropper API:
- Native Chromium API (window.EyeDropper) — available in Chrome/Edge
- Pixel-accurate color picking from anywhere on screen
- No screenshot needed, no canvas, no CORS issues
- Falls back to elementsFromPoint + getComputedStyle for non-Chromium

This eliminates:
- Step 5 (PROVIDE VIEWPORT SCREENSHOT) from SKILL.md
- __xipeViewportScreenshot global variable
- offscreenCanvas, loadScreenshot, screenshotPoll code in toolbar-theme
- All chunked screenshot injection logic

Applied fix: toolbar-theme.min.js rewritten to use EyeDropper API with
elementsFromPoint fallback. SKILL.md updated to remove step 5.
```

### Proposed Improvement

```yaml
type: update_instruction
target: "SKILL.md + references/toolbar-theme.min.js"
description: |
  APPLIED: Removed offscreen canvas color picker. Replaced with:
  1. EyeDropper API (primary) — native browser pixel color picking
  2. elementsFromPoint + getComputedStyle (fallback) — z-index aware CSS sampling
  
  SKILL.md changes:
  - Removed step 5 (PROVIDE VIEWPORT SCREENSHOT)
  - Removed __xipeViewportScreenshot constraint
  - Removed DoD checkpoint for viewport screenshot
  - Updated "Offscreen Canvas" key concept to "EyeDropper API"
status: applied
```

---

## LL-004

**Date:** 2026-02-14
**Severity:** major
**Source:** human_feedback
**Status:** applied
**Task ID:** N/A (ad-hoc uiux-reference execution)

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  When user switches to "Copy Mockup" mode and clicks on page elements,
  the color picker from theme mode still fires, intercepting clicks.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "208. Baidu-Reference-v4"
```

### Observed Behavior

```
handleColorClick in toolbar-theme.min.js listens globally on document click.
It only checks magnifierActive flag, but this flag is set per-step within
theme mode. When user switches to mockup mode, the click handler still fires
because magnifierActive may still be true from theme mode's step 1.

Even if magnifierActive is false, the handler doesn't check which mode is
active — it processes clicks regardless of the current toolbar mode.
```

### Expected Behavior

```
Color picking click handler should ONLY fire when:
1. Theme mode is the active mode (window.__xipeRefData.mode === 'theme')
2. AND magnifierActive is true (step 1 of theme wizard)

When mockup mode is active, clicking should only trigger component selection,
not color picking.
```

### Ground Truth

```
Added mode guard to handleColorClick:
  if (window.__xipeRefData.mode !== 'theme') return;

This ensures the color picker click handler exits immediately when
mockup mode is active, allowing mockup's handleSnapClick to process
the click instead.

Applied in toolbar-theme.min.js.
```

### Proposed Improvement

```yaml
type: update_ac
target: "toolbar-theme.min.js → handleColorClick"
description: |
  APPLIED: Added `if (window.__xipeRefData.mode !== 'theme') return;`
  as early guard in handleColorClick. Color picking now only activates
  in theme mode.
status: applied
```

---

## LL-005

**Date:** 2026-02-14
**Severity:** minor
**Source:** human_feedback
**Status:** applied
**Task ID:** N/A (ad-hoc uiux-reference execution)

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  When color picking is active, the cursor should change to an eyedropper/straw
  icon to indicate the picking mode. The magnifier preview should be centered
  on the cursor tip so the center crosshair of the magnifier aligns with
  where the color will be picked.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "208. Baidu-Reference-v4"
```

### Observed Behavior

```
1. Cursor remains default pointer during color picking — no visual feedback
   that picking mode is active
2. Magnifier is positioned at (clientX + 20, clientY - 140), offset to
   the right of cursor. The magnifier center crosshair does NOT align
   with the cursor position, making it unclear exactly which pixel
   the user is picking.
```

### Expected Behavior

```
1. Cursor should change to a straw/eyedropper icon when color picking is active
2. Magnifier should be positioned so its center (the crosshair) aligns with
   the cursor tip — the straw's pointing tip should be at the center of
   the magnifier
```

### Ground Truth

```
Applied fixes:
1. Added SVG eyedropper cursor via CSS data URI:
   - Green (#10b981) straw icon with black outline
   - Hotspot at (0, 24) — bottom-left tip of the straw
   - Applied via .xipe-eyedropper-active class on <html> element
   - Applied to all child elements (* selector) to override element cursors

2. Repositioned magnifier to center on cursor:
   - Changed from (clientX + 20, clientY - 140) → (clientX - 60, clientY - 150)
   - 60 = half of magnifier width (120px), so center aligns horizontally
   - 150 = magnifier height, positioned above cursor

3. Added updateMagnifierCss() function that toggles the cursor class
   when magnifierActive changes (on step transitions).
```

### Proposed Improvement

```yaml
type: update_ac
target: "toolbar-theme.min.js → cursor and magnifier positioning"
description: |
  APPLIED:
  - Straw cursor SVG added as CSS custom cursor
  - Magnifier centered horizontally on cursor position
  - updateMagnifierCss() manages cursor class on <html> element
status: applied
```

---

## LL-006

**Date:** 2026-02-14
**Severity:** major
**Source:** human_feedback
**Status:** applied
**Task ID:** N/A (ad-hoc uiux-reference execution)

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  In Copy Mockup mode, clicking an element immediately creates a permanent
  dashed overlay with drag handles. There is no hover preview showing which
  element will be selected before clicking. Additionally, the drag handles
  on the overlay have resize cursors but no actual drag/resize functionality.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "208. Baidu-Reference-v4"
```

### Observed Behavior

```
1. No hover preview — clicking immediately creates a permanent overlay
   without any visual feedback about which element will be selected
2. Drag handles display resize cursors (nw-resize, n-resize, etc.) but
   have no mousedown/mousemove/mouseup event listeners — dragging them
   has no effect on the overlay size
3. No visual distinction between "preview" and "confirmed" selection states
```

### Expected Behavior

```
1. Inspector-style hover preview: a semi-transparent blue overlay follows
   the cursor on mousemove, highlighting the semantic container that would
   be selected on click (like Chrome DevTools inspect mode)
2. Click confirms selection: converts blue preview into permanent green
   dashed overlay with drag handles
3. Drag handles should actually resize the overlay and update the
   component's bounding_box data
```

### Ground Truth

```
Applied fixes in toolbar-mockup.min.js:

1. Hover preview overlay:
   - Added .xipe-snap-hover CSS class (blue border, light blue bg, 0.08s transition)
   - Added showHoverPreview() on document mousemove (capture phase)
   - Uses findSemanticContainer() to identify target element
   - Shows tag badge on hover overlay
   - hideHoverPreview() called on click confirmation and step changes

2. Click-to-confirm flow:
   - handleSnapClick calls hideHoverPreview() before captureComponent()
   - Blue preview disappears, green dashed overlay appears

3. Working drag handles:
   - Each handle has dx/dy direction vectors (-1, 0, 1)
   - mousedown captures startX/Y and startRect
   - mousemove calculates delta and applies directional resize
   - mouseup updates component.bounding_box with final dimensions
   - Minimum size enforced (20x20px)
```

### Proposed Improvement

```yaml
type: update_ac
target: "toolbar-mockup.min.js → hover preview and drag resize"
description: |
  APPLIED:
  - Inspector-style hover preview with blue overlay on mousemove
  - Click-to-confirm flow with visual state transition
  - Working drag handles with directional resize logic
  - bounding_box data updated on drag completion
status: applied
```

---

## LL-007

**Date:** 2026-02-14
**Severity:** enhancement
**Source:** human_feedback
**Status:** raw
**Task ID:** N/A (ad-hoc uiux-reference execution)

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  After multiple iteration rounds on toolbar injection for https://www.baidu.com,
  user requested two optimizations: (1) remove straw cursor and call EyeDropper API
  directly on toggle click instead of a two-step click-then-pick flow, and (2) merge
  the 3-file injection (core, theme, mockup) into a single optimized file.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "208. Baidu-Reference-v4"
```

### Observed Behavior

```
1. Color picking used a two-step flow: toggle sets pickerActive=true + applies straw
   cursor, then user clicks on page to trigger EyeDropper.open(). This added unnecessary
   friction — user expected one click to open the native picker.
2. Toolbar was injected via 3 sequential evaluate_script calls (core ~10KB, theme ~12KB,
   mockup ~17KB = ~39KB total). Files had ~40% duplicated CSS (buttons, steps, nav styles)
   and dead code (viewport screenshot cropping, handleDeepCapture unused in interactive
   mode, getColorAtPoint fallback, straw cursor SVG/CSS).
```

### Expected Behavior

```
1. Click "Pick Color" toggle → directly calls new EyeDropper().open() with no intermediate
   state, cursor change, or click handler. On success: add color + no toggle state needed.
   On cancel/error: no-op.
2. Single evaluate_script call with one merged IIFE (~24KB). Deduplicated CSS in one
   <style> block. No dead code. No __xipeRegisterMode indirection needed (init functions
   defined inline). Estimated 40% size reduction.
```

### Ground Truth

```yaml
ground_truth:
  direct_eyedropper_pattern: |
    function pickColor() {
      if (!hasED) { toast('EyeDropper API not supported', 'error'); return; }
      new EyeDropper().open().then(r => addColor(r.sRGBHex)).catch(() => {});
    }
    // Toggle button onclick = pickColor (no intermediate state)
  single_file_injection: |
    - Single toolbar.min.js IIFE (~24KB vs ~39KB from 3 files)
    - One <style> block with all CSS (no duplication)
    - Core, theme, mockup defined inline in one closure
    - Dead code removed: straw cursor, magnifier, viewport screenshot,
      getColorAtPoint, handleDeepCapture standalone function
    - __xipeRegisterMode kept for lazy init but modes defined in same file
  file: ".github/skills/x-ipe-tool-uiux-reference/references/toolbar.min.js"
status: applied
```

### Improvement Proposal

```yaml
type: update_instruction
target: SKILL.md — Step 5 (Inject Toolbar)
description: |
  Update injection instructions to reference single toolbar.min.js instead of
  3 separate files. Add guidance:
  - "Inject toolbar via single evaluate_script call using toolbar.min.js"
  - "EyeDropper API should be called directly on button click (no toggle state)"
  - "All CSS consolidated in one <style> block to minimize DOM operations"
  - "Dead code should be removed before injection to stay under size limits"
```

---

## LL-008

**Date:** 2026-02-15
**Severity:** major
**Source:** human_feedback
**Status:** applied (CR-002/CR-001, TASK-456)
**Task ID:** TASK-452

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  Executing UIUX reference workflow on https://www.baidu.com.
  User selected a bounding box (comp-001: div.s_form_wrapper) covering the
  search form area (logo + search box + hot search). Agent treated the bounding
  box as if it covered the whole page and generated a full-page mockup including
  top nav bar and all page sections.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "209. Baidu-Reference-v5"
```

### Observed Behavior

```
1. User selected a specific bounding box (x:131.5, y:0, w:1575, h:383.5) via
   the toolbar's Copy Mockup mode — this covers ONLY the search form wrapper
   (Baidu logo, search input, hot search area).
2. Agent generated mockup-v1.html that included the entire page: top navigation
   bar, footer links, and other elements NOT within the selected bounding box.
3. The mockup scope was broader than what the user selected, violating the
   user's intent to capture only the selected area.
```

### Expected Behavior

```
The mockup should reproduce ONLY the content within the selected bounding box.
If the user selects a div covering the search form area (383.5px height), the
mockup should contain only: Baidu logo, search input with buttons, "问文心"
link, and hot search list — nothing else.

The agent must respect the component's bounding_box and selector as the scope
boundary for mockup generation.
```

### Ground Truth

```
When generating a mockup from selected components:
1. Only include elements that are children of or contained within the selected
   component's DOM subtree (identified by selector)
2. The bounding_box defines the visual area — do NOT add elements outside it
3. If the outer_html is available, use it as the authoritative content source
4. Do NOT infer or add page-level elements (nav bars, footers, headers) unless
   they are explicitly within the selected component's subtree
```

### Proposed Improvement

```yaml
type: update_instruction
target: "SKILL.md → Operations → process_mockup → GENERATE FLOW → Step 10"
description: |
  Add explicit scoping instruction to Step 10 (Generate versioned mockup):
  
  10a. SCOPE CONSTRAINT: The mockup MUST only contain elements within the
       selected component(s). Use the component's outer_html as the primary
       content source. Do NOT add page-level elements (navigation, footer,
       header) unless they appear within the component's DOM subtree.
  10b. The bounding_box defines the visual region — the mockup viewport
       should match the component dimensions, not the full page.

proposed_ac:
  should:
    - id: AC-C16
      category: content
      criterion: "Mockup generation respects selected component boundaries"
      test: content_check
      expected: "Step 10 instructs agent to scope mockup to component subtree only"
```

---

## LL-009

**Date:** 2026-02-15
**Severity:** major
**Source:** human_feedback
**Status:** applied (CR-002/CR-001, TASK-456)
**Task ID:** TASK-452

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  During mockup validation, agent used a ~90% visual similarity threshold.
  User requires 99% accuracy for mockup fidelity — "I want 100% the same".
inputs:
  url: "https://www.baidu.com"
  idea_folder: "209. Baidu-Reference-v5"
```

### Observed Behavior

```
1. Agent generated mockup with approximate styling (gradient button instead of
   flat blue #4e6ef2, wrong font-weight, "问文心" text duplicated with image).
2. Agent compared mockup screenshot to original and considered it "close enough"
   after 2 iterations.
3. The 5% tolerance threshold for screenshot dimension validation was the only
   quantitative check — no pixel-level or style-property-level validation.
```

### Expected Behavior

```
1. Validation target should be 99% visual similarity, not 90%.
2. Validation should include property-level checks:
   - Exact color values (hex match)
   - Exact font properties (family, size, weight)
   - Exact spacing values (margin, padding, gap)
   - Exact border/radius/shadow values
   - Correct image/icon sources (same CDN URLs)
3. When differences are found, agent should iterate (up to 3 times) fixing
   specific property mismatches before asking user for approval.
```

### Ground Truth

```
The validation rubric should be expanded to 6 dimensions (see LL-011) with
detailed sub-checks per dimension. Target accuracy: 99% visual match.

Key validation rules:
- Colors must be exact hex match (e.g., #4e6ef2 not a gradient approximation)
- Font properties must match computed values from deep capture
- Layout dimensions must match within 1px tolerance (not 5%)
- Background must match type (solid vs gradient vs image) exactly
- Static resources (images, icons, fonts) should use original source URLs
- Agent should iterate max 3 times, fixing specific mismatches each round
```

### Proposed Improvement

```yaml
type: update_instruction
target: "SKILL.md → Operations → process_mockup → GENERATE FLOW → Step 10"
description: |
  Update mockup validation threshold and add property-level checks:
  
  10d. VALIDATION (99% target):
       - Compare each CSS property from deep capture against mockup
       - Colors: exact hex match required
       - Fonts: family, size, weight must match
       - Spacing: margin/padding within 1px
       - Layout: width/height within 1px
       - Resources: original source URLs preserved
       - Screenshot dimension tolerance: 1% (was 5%)
  10e. IF match < 99%: identify specific property mismatches, fix, regenerate
       (max 3 iterations)

proposed_ac:
  should:
    - id: AC-C17
      category: content
      criterion: "Mockup validation targets 99% visual accuracy"
      test: content_check
      expected: "Validation uses property-level checks with 1px/exact-match thresholds"
```

---

## LL-010

**Date:** 2026-02-15
**Severity:** major
**Source:** human_feedback
**Status:** applied (CR-002/CR-001, TASK-456)
**Task ID:** TASK-452

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  During the analyze phase (process_mockup ANALYZE FLOW), agent performed
  deep capture, rubric evaluation, and auto-collection but did NOT save any
  data to the idea folder. Data was only saved at the generate phase (step 9).
  User expects analysis artifacts to be persisted immediately during analysis.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "209. Baidu-Reference-v5"
```

### Observed Behavior

```
1. Analyze flow (steps 2-7): Agent collected deep capture data, evaluated
   5-dimension rubric, took screenshots — but saved NOTHING to disk.
2. All collected data existed only in browser memory (window.__xipeRefData)
   and agent's context.
3. Only at Generate flow step 9 did agent call save_uiux_reference.
4. If agent session crashed between analyze and generate, all analysis data
   would be lost.
5. Screenshots were saved to screenshots/ folder but NOT to the idea folder's
   uiux-references structure.
```

### Expected Behavior

```
Analysis artifacts should be saved to the idea folder immediately during the
analyze phase, organized in the structured folder hierarchy (see LL-011).

At minimum, after analysis completes:
- Screenshots saved to uiux-references/screenshots/
- Component data saved to uiux-references/page-element-references/
- Rubric evaluation saved to strategy file
- save_uiux_reference called with analysis data
```

### Ground Truth

```
After completing ANALYZE FLOW step 6 (auto-collection), add a new step:

6b. PERSIST ANALYSIS DATA:
    a. Save screenshots to idea_folder/uiux-references/screenshots/
       - Full page: full-page.png
       - Selected area: {comp_id}.png
    b. Save component reference data to
       idea_folder/uiux-references/page-element-references/
       - summarized-uiux-reference.md (colors, fonts, elements summary)
       - resources/ folder with HTML/CSS/JS snippets
    c. Save mimic strategy to
       idea_folder/uiux-references/mimic-strategy.md
    d. CALL save_uiux_reference with analysis data

This ensures no data loss if session ends before generate phase.
```

### Proposed Improvement

```yaml
type: update_instruction
target: "SKILL.md → Operations → process_mockup → ANALYZE FLOW"
description: |
  Add step 6b after auto-collection to persist analysis artifacts:
  
  6b. PERSIST ANALYSIS DATA:
      - Save screenshots to idea_folder/uiux-references/screenshots/
      - Save summarized reference to page-element-references/
      - Save HTML/CSS/JS snippets to page-element-references/resources/
      - Save mimic strategy with rubric results
      - CALL save_uiux_reference with current analysis data
  
  This prevents data loss between analyze and generate phases.

proposed_ac:
  should:
    - id: AC-C18
      category: content
      criterion: "Analysis phase persists data to idea folder immediately"
      test: content_check
      expected: "ANALYZE FLOW includes data persistence step before re-enabling buttons"
```

---

## LL-011

**Date:** 2026-02-15
**Severity:** major
**Source:** human_feedback
**Status:** applied (CR-002/CR-001, TASK-456)
**Task ID:** TASK-452

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  User provided detailed feedback on the uiux-references folder structure
  and data organization. Current implementation saves minimal data (JSON
  session file only). User wants a comprehensive folder structure with
  organized artifacts and a 6-dimension validation strategy.
inputs:
  url: "https://www.baidu.com"
  idea_folder: "209. Baidu-Reference-v5"
```

### Observed Behavior

```
1. uiux-references/ folder only contains ref-session-001.json (flat JSON)
2. No structured subfolders for screenshots, element references, or resources
3. No mimic strategy document describing how to reproduce the design
4. Only 5-dimension rubric (layout, typography, color, spacing, visual_effects)
   with coarse confidence levels (confident/uncertain/missing)
5. No static resource validation (fonts, icons, images not tracked)
```

### Expected Behavior

```
User specified the following folder structure and content requirements:

uiux-references/                          (root)
├── screenshots/
│   ├── full-page.png                     (full page screenshot)
│   └── {comp-id}.png                     (selected area screenshot — the one to mimic)
├── page-element-references/
│   ├── summarized-uiux-reference.md      (page-level + selected-area-level summary)
│   │   Contains: colors, fonts, elements, source URLs
│   │   Organized by: page level vs selected area level
│   └── resources/
│       ├── {comp-id}-structure.html      (HTML snippet of component)
│       ├── {comp-id}-styles.css          (computed CSS for component)
│       └── {comp-id}-scripts.js          (relevant JS if any)
└── mimic-strategy.md                     (how to mimic + validation criteria)

The mimic-strategy.md should contain:
- 6-dimension validation rubric (expanded from 5):
  1. Layout (structure, flexbox/grid, positioning, dimensions)
  2. Typography (font-family, size, weight, line-height, letter-spacing, color)
  3. Color Palette (background, text, border, shadow colors — exact hex match)
  4. Spacing (margin, padding, gap — within 1px)
  5. Visual Effects (shadows, borders, gradients, opacity, border-radius)
  6. Static Resources (fonts loaded, icons/SVGs used, images with source URLs,
     background images — verify sources match original)
- Each dimension has detailed sub-checks (not just confident/uncertain/missing)
- Strategy for mimicking the selected area
- Key validation criteria for 99% accuracy target
```

### Ground Truth

```yaml
folder_structure:
  root: "uiux-references/"
  subfolders:
    screenshots:
      purpose: "Visual reference captures"
      contents:
        - "full-page.png: Full page screenshot for context"
        - "{comp-id}.png: Selected area screenshot (primary mimic target)"
    page-element-references:
      purpose: "Structured design data at page and component level"
      contents:
        - "summarized-uiux-reference.md: Comprehensive reference document"
      subfolders:
        resources:
          purpose: "Raw HTML/CSS/JS snippets extracted from page"
          contents:
            - "{comp-id}-structure.html: Component outer HTML"
            - "{comp-id}-styles.css: Computed CSS properties"
            - "{comp-id}-scripts.js: Relevant JavaScript (if any)"
    root_files:
      - "mimic-strategy.md: Strategy document with 6-dimension validation"

summarized_uiux_reference_template: |
  # UIUX Reference Summary
  
  ## Source
  - URL: {source_url}
  - Captured: {timestamp}
  
  ## Page-Level Reference
  ### Colors
  | Color | Hex | Usage | Source Element |
  |-------|-----|-------|----------------|
  
  ### Fonts
  | Font Family | Sizes Used | Weights | Source |
  |-------------|-----------|---------|--------|
  
  ### Key Elements
  | Element | Selector | Dimensions | Notes |
  |---------|----------|-----------|-------|
  
  ## Selected Area Reference: {comp-id}
  ### Colors (within selected area)
  | Color | Hex | RGB | Usage | Element |
  |-------|-----|-----|-------|---------|
  
  ### Typography (within selected area)
  | Element | Font Family | Size | Weight | Line-Height | Color |
  |---------|------------|------|--------|-------------|-------|
  
  ### Layout Structure
  - Display type: {flex/grid/block}
  - Dimensions: {width} × {height}
  - Children: {count} direct children
  
  ### Static Resources
  | Type | Source URL | Usage | Notes |
  |------|-----------|-------|-------|
  
  ### Source URLs
  - Images: {list of image URLs}
  - Stylesheets: {list of CSS URLs}
  - Fonts: {list of font URLs}

mimic_strategy_template: |
  # Mimic Strategy
  
  ## Target
  - Source: {source_url}
  - Component: {comp-id} ({tag})
  - Dimensions: {width} × {height}
  - Instruction: {user instruction}
  
  ## 6-Dimension Validation Rubric
  
  ### 1. Layout
  - [ ] Display type matches (flex/grid/block/inline)
  - [ ] Positioning matches (static/relative/absolute/fixed)
  - [ ] Dimensions within 1px (width, height)
  - [ ] Flex/grid properties match (direction, wrap, justify, align)
  - [ ] Child element count and order match
  - [ ] Overflow behavior matches
  
  ### 2. Typography
  - [ ] font-family exact match
  - [ ] font-size exact match
  - [ ] font-weight exact match
  - [ ] line-height exact match
  - [ ] letter-spacing match
  - [ ] text color exact hex match
  - [ ] text-align match
  - [ ] text-decoration match
  
  ### 3. Color Palette
  - [ ] Background color exact hex match
  - [ ] Text colors exact hex match
  - [ ] Border colors exact hex match
  - [ ] Shadow colors exact hex match
  - [ ] Gradient values match (if any)
  - [ ] Opacity values match
  
  ### 4. Spacing
  - [ ] Margin values within 1px
  - [ ] Padding values within 1px
  - [ ] Gap values within 1px (flex/grid)
  - [ ] Element spacing consistent with original
  
  ### 5. Visual Effects
  - [ ] box-shadow values match
  - [ ] border values match (width, style, color)
  - [ ] border-radius values match
  - [ ] background-image/gradient match
  - [ ] opacity match
  - [ ] transform match (if any)
  - [ ] transition/animation match (if any)
  
  ### 6. Static Resources
  - [ ] Font files loaded (same families available)
  - [ ] Icons/SVGs use original source or faithful reproduction
  - [ ] Images use original source URLs
  - [ ] Background images use original source URLs
  - [ ] CSS referenced resources available
  
  ## Mimic Approach
  {describe strategy: direct HTML/CSS recreation, component-by-component, etc.}
  
  ## Key Validation Criteria
  - Target accuracy: 99%
  - Screenshot comparison: dimensions within 1%
  - Property-level: exact match for colors, fonts; 1px tolerance for spacing
  - Static resources: original URLs preserved where possible
  - Max iterations: 3 refinement rounds before user approval
```

### Proposed Improvement

```yaml
type: new_ac
target: "SKILL.md → Operations → process_mockup"
description: |
  1. Add folder structure creation at the START of process_mockup:
     - Create uiux-references/screenshots/
     - Create uiux-references/page-element-references/resources/
  
  2. During ANALYZE FLOW, save artifacts to structured folders:
     - Screenshots to screenshots/
     - HTML/CSS/JS snippets to page-element-references/resources/
     - Create summarized-uiux-reference.md from collected data
     - Create mimic-strategy.md with 6-dimension rubric
  
  3. Add 6th dimension "Static Resources" to rubric evaluation:
     - Check for fonts, icons, images, SVGs used in component
     - Record source URLs for each static resource
     - Validate during mockup generation that resources are preserved
  
  4. Update GENERATE FLOW validation to use 6-dimension rubric from
     mimic-strategy.md with 99% accuracy target
  
  5. Add templates for summarized-uiux-reference.md and mimic-strategy.md
     to SKILL.md references/ folder

proposed_ac:
  should:
    - id: AC-C19
      category: structure
      criterion: "uiux-references folder has structured subfolders"
      test: structure_check
      expected: "screenshots/, page-element-references/resources/ created during analyze"
    - id: AC-C20
      category: content
      criterion: "summarized-uiux-reference.md created with page and area level data"
      test: content_check
      expected: "Contains colors, fonts, elements, source URLs at both levels"
    - id: AC-C21
      category: content
      criterion: "mimic-strategy.md created with 6-dimension validation rubric"
      test: content_check
      expected: "Contains layout, typography, color, spacing, visual effects, static resources"
    - id: AC-C22
      category: content
      criterion: "Static Resources is the 6th validation dimension"
      test: content_check
      expected: "Fonts, icons, images, SVGs tracked with source URLs"
    - id: AC-C23
      category: content
      criterion: "HTML/CSS/JS snippets saved to resources/ folder"
      test: content_check
      expected: "{comp-id}-structure.html, {comp-id}-styles.css saved"
```

---

## LL-012

**Date:** 2026-02-15
**Severity:** major
**Source:** human_feedback
**Status:** raw
**Task ID:** TASK-457

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  Executed UIUX reference on https://github.com/. Agent completed analyze + generate
  mockup flow. After completion, the uiux-references/ folder only contained:
  reference-data.json, screenshots/, sessions/ — missing the structured output
  required by LL-008..LL-011 and the save_uiux_reference service.
inputs:
  url: "https://github.com/"
  idea_folder: "210. Github-Reference-v6"
```

### Observed Behavior

```
uiux-references/ folder after completion:
├── reference-data.json
├── screenshots/
│   ├── comp-001.png
│   └── mockup-v1.png
└── sessions/
    ├── ref-session-001.json
    └── ref-session-002.json

Missing entirely:
- page-element-references/ folder
- page-element-references/summarized-uiux-reference.md
- page-element-references/resources/{comp-id}-structure.html
- page-element-references/resources/{comp-id}-styles.css
- mimic-strategy.md
- screenshots/full-page.png
```

### Expected Behavior

```
uiux-references/ folder should contain the full structured output:
├── screenshots/
│   ├── full-page.png                     (full page screenshot)
│   └── {comp-id}.png                     (selected area screenshot)
├── page-element-references/
│   ├── summarized-uiux-reference.md      (page-level + selected-area-level summary)
│   └── resources/
│       ├── {comp-id}-structure.html      (HTML snippet of component)
│       ├── {comp-id}-styles.css          (computed CSS for component)
│       └── {comp-id}-scripts.js          (relevant JS if any)
└── mimic-strategy.md                     (how to mimic + validation criteria)
```

### Ground Truth

```
The save_uiux_reference MCP service (TASK-454) was updated to generate structured output
when elements include html_css data. The SKILL.md must instruct the agent to:
1. Include outer_html and computed_styles in the elements data sent to save_uiux_reference
2. Take a full-page screenshot and save it as screenshots/full-page.png
3. Verify after save_uiux_reference call that the structured folders were created
4. If structured output is missing, manually create the files from collected data

The agent in TASK-457 sent incomplete outer_html (simplified instead of full deep capture)
and did not take a full-page screenshot, which prevented the service from generating
the full structured output.
```

### Improvement Proposal

```yaml
type: update_instruction
target: ".github/skills/x-ipe-tool-uiux-reference/SKILL.md"
section: "Operation: process_mockup — ANALYZE FLOW step 6b"
description: |
  1. Add explicit step: "Take full-page screenshot: take_screenshot(fullPage: true,
     filePath: '{screenshots_path}/full-page.png')"
  2. In step 6b, require that elements data sent to save_uiux_reference includes
     the FULL outer_html from deep capture (not a simplified version)
  3. Add verification step after save_uiux_reference: check that
     page-element-references/ and mimic-strategy.md were created
  4. If missing, agent should create them manually from collected data
```

---

## LL-013

**Date:** 2026-02-15
**Severity:** major
**Source:** human_feedback
**Status:** addressed (TASK-459 renamed comp→area; CR pending for area semantics)
**Task ID:** TASK-457

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  User feedback on the "Select Areas" step in mockup mode. The current toolbar
  snaps to a DOM element via findSem(), which is fine as a starting point.
  However, the snapped DOM element is only ONE of the related elements within
  the selected area. The area concept is broader — it represents a rectangular
  region that may contain multiple DOM elements, CSS, JS, and static resources.
inputs:
  url: "https://github.com/"
  idea_folder: "210. Github-Reference-v6"
```

### Observed Behavior

```
Current toolbar behavior:
1. User clicks "Select Area" button
2. Toolbar uses findSem() to snap to nearest semantic DOM element — this is OK
3. Selection overlay appears at that element's bounding box — user can resize
4. Area is named "area-1", "area-2", etc. (renamed from comp-XXX in TASK-459)
5. The snapped DOM element is treated as THE component, but it's really
   just the initial snap target — one of potentially many elements in the area
6. During analysis, the agent only captures the snapped element's styles/HTML

The issue: the snapped DOM element is treated as the sole content source,
but the selected area may contain sibling elements, child elements from
parent containers, overlapping positioned elements, background layers, etc.
```

### Expected Behavior

```
Updated "Select Area" semantics:
1. DOM snap via findSem() is still used as the initial selection anchor — KEEP
2. The snapped element gives the initial bounding box, user can resize via handles
3. The snapped element is stored as area.snap_element (one of many related elements)
4. During analysis, the agent discovers ALL elements within the area bounding_box:
   - DOM elements whose getBoundingClientRect() intersects the area
   - CSS styles applied to those elements
   - JS behaviors affecting those elements
   - Static resources (images, SVGs, fonts, etc.) used by those elements
5. The area's content = union of all elements within the bounding box, not just
   the snapped element
```

### Ground Truth

```
The distinction is:
- area.snap_element = the DOM element that was initially clicked (for reference)
- area.bounding_box = the user's selected rectangular region (may be resized)
- area.related_elements = ALL DOM elements within the bounding_box (discovered during analysis)

The toolbar still uses findSem() for smart-snap — that's a good UX. But the
analysis step must expand beyond the snapped element to capture everything
within the bounding_box coordinates.

The SKILL.md analysis step should:
1. Use bounding_box to enumerate all intersecting DOM elements
2. Capture computed styles for each discovered element
3. Collect static resources (img, svg, canvas, video, fonts) from all elements
4. Download resources to resources/ folder
5. The snapped element's selector is kept for deep_capture fallback
```

### Improvement Proposal

```yaml
type: new_ac
target: ".github/skills/x-ipe-tool-uiux-reference/SKILL.md"
section: "Operation: process_mockup — ANALYZE FLOW"
description: |
  1. Keep findSem() DOM-snap as initial selection anchor (good UX)
  2. Rename terminology: "component" → "area" throughout (DONE in TASK-459)
  3. Store snapped element as area.snap_element (reference only)
  4. During analysis: enumerate ALL DOM elements within area.bounding_box
  5. Capture styles, HTML, and resources from ALL discovered elements
  6. Download static resources to resources/ folder
  7. The area is the bounding_box region, not a single DOM element
```

---

## LL-014

**Date:** 2026-02-15
**Severity:** major
**Source:** human_feedback
**Status:** raw
**Task ID:** TASK-457

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  During analysis phase, agent takes a screenshot for the selected area.
  The screenshot should be pixel-exact to the user's selected area bounding box,
  but instead the agent tried to match the area to a DOM element UID in the
  a11y snapshot and screenshotted that element instead.
inputs:
  url: "https://github.com/"
  idea_folder: "210. Github-Reference-v6"
```

### Observed Behavior

```
Agent's screenshot approach during analysis:
1. Take a11y snapshot (take_snapshot)
2. Search for a DOM element UID that matches the selected component's selector
3. Call take_screenshot(uid: matched_uid) — which screenshots the DOM element
4. The DOM element's dimensions may differ from the user's selected area
   (especially if user resized via drag handles)

In TASK-457, the section element was 972x197px in the DOM but the user's
selected area was 972x312px (larger, including visual space below).
The screenshot captured the DOM element, not the user's intended area.
```

### Expected Behavior

```
Screenshot should match exactly the user's selected bounding_box:
1. Use the bounding_box coordinates (x, y, width, height) from the selected area
2. Take a viewport-level screenshot or use CDP clip parameters to capture
   exactly the selected rectangular area
3. Do NOT try to match to a DOM element UID — the area may span multiple
   elements or include whitespace
4. If the area extends beyond viewport, use fullPage screenshot and crop
```

### Ground Truth

```
The agent should use evaluate_script with CDP-level screenshot capabilities
or use take_screenshot with clip coordinates matching the bounding_box.
The Chrome DevTools MCP take_screenshot tool supports uid (element) or
fullPage, but for exact area capture, the agent could:
1. Scroll to ensure the area is in viewport
2. Use take_screenshot() for viewport capture
3. Use evaluate_script to create a canvas crop of the exact area
4. Or take fullPage screenshot and instruct post-processing to crop

The key point: screenshot dimensions MUST match the selected area's
bounding_box dimensions exactly, not a DOM element's dimensions.
```

### Improvement Proposal

```yaml
type: update_instruction
target: ".github/skills/x-ipe-tool-uiux-reference/SKILL.md"
section: "Operation: process_mockup — ANALYZE FLOW step 3"
description: |
  1. Replace "take_screenshot(uid: matching_element)" with area-based capture:
     "Use the selected area's bounding_box (x, y, width, height) to capture
     an exact screenshot of the selected rectangular region"
  2. Add procedure: scroll to area, take viewport screenshot, crop to bounding_box
  3. Remove dependency on finding a matching UID in the a11y snapshot
  4. Validate that screenshot dimensions match bounding_box within 1px
```

---

## LL-015

**Date:** 2026-02-15
**Severity:** critical
**Source:** human_feedback
**Status:** raw
**Task ID:** TASK-457

### Context

```yaml
skill_name: x-ipe-tool-uiux-reference
scenario: |
  During analysis, the agent should detect and download ALL resources within
  the selected area that would be needed to create an accurate mockup.
  Currently the agent only collects computed styles and outerHTML via deep capture,
  but does not download actual static resources (images, SVGs, canvas content,
  videos, CSS files, fonts) into the resources/ folder.
inputs:
  url: "https://github.com/"
  idea_folder: "210. Github-Reference-v6"
```

### Observed Behavior

```
During analysis (TASK-457), the agent:
1. Did deep capture → got computed_styles + outer_html
2. Checked font network requests → noted URLs but did NOT download them
3. Did NOT scan for images, SVGs, canvas, video within the selected area
4. Did NOT download any static resources to resources/ folder
5. The resources/ folder was never created

The auto-collection step 6 in SKILL.md mentions collecting images/SVGs and
stylesheets, but the agent either skipped it or only logged URLs without
downloading the actual files.
```

### Expected Behavior

```
During analysis, for each selected area, the agent MUST:
1. DETECT all DOM elements within the bounding_box:
   - Enumerate all elements whose getBoundingClientRect() intersects the area
   - Classify each: img, svg, canvas, video, iframe, etc.
2. DETECT all CSS/JS resources:
   - Collect relevant stylesheets (link[rel=stylesheet], inline <style>)
   - Collect relevant scripts if they affect visual rendering
3. DETECT static resources:
   - Images: <img> src, srcset, background-image URLs
   - SVGs: inline SVG outerHTML, external SVG src
   - Canvas: capture canvas content as data URL
   - Videos: poster image, src URL
   - Fonts: @font-face URLs used by elements in the area
   - Icons: icon fonts, sprite sheets
4. DOWNLOAD resources to resources/ folder:
   - Images → resources/{area-id}-img-{N}.{ext}
   - SVGs → resources/{area-id}-svg-{N}.svg
   - Fonts → resources/{area-id}-font-{N}.woff2
   - CSS → resources/{area-id}-styles.css (relevant rules only)
   - Canvas → resources/{area-id}-canvas-{N}.png
5. These downloaded resources should be referenced in summarized-uiux-reference.md
   and used during mockup generation for pixel-perfect accuracy
```

### Ground Truth

```
The analysis step must be comprehensive resource detection + download:

1. Use evaluate_script to enumerate all elements within bounding_box:
   document.elementsFromPoint() or iterate all descendants checking
   getBoundingClientRect() intersection with selected area

2. For each element, classify and extract resource URLs:
   - img.src, img.srcset
   - svg outerHTML
   - canvas.toDataURL()
   - video.poster, video.src
   - computed background-image URLs
   - font-face URLs from stylesheets

3. Download each resource:
   - Use evaluate_script with fetch() to get resource as blob/dataURL
   - Or use get_network_request to download from network log
   - Save to resources/ folder with systematic naming

4. Create summarized-uiux-reference.md listing:
   - All detected DOM elements in the area
   - All static resources with local file paths
   - CSS properties relevant to mockup generation
   - Font information and local font file paths

This is the most critical step for mockup accuracy — without actual resources,
the mockup cannot achieve 99% fidelity.
```

### Improvement Proposal

```yaml
type: new_ac
target: ".github/skills/x-ipe-tool-uiux-reference/SKILL.md"
section: "Operation: process_mockup — ANALYZE FLOW"
description: |
  1. Add new step between current steps 4 and 5: "RESOURCE DETECTION AND DOWNLOAD"
     a. Use evaluate_script to enumerate all DOM elements within bounding_box
     b. Classify elements: img, svg, canvas, video, fonts, backgrounds
     c. Extract all resource URLs from elements and computed styles
     d. Download each resource to resources/ folder
     e. Capture canvas content as data URLs
     f. Download relevant CSS rules and save to resources/{area-id}-styles.css
  2. Update step 6b (persist analysis): include downloaded resource file paths
     in the data sent to save_uiux_reference
  3. Update GENERATE FLOW step 10: reference local resource files from
     resources/ folder instead of original URLs when generating mockup
  4. Add AC: "All static resources within selected area are downloaded to
     resources/ folder and referenced in summarized-uiux-reference.md"
```
