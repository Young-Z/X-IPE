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
