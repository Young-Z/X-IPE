---
name: x-ipe-tool-uiux-reference
description: Execute UIUX reference workflow v3.1 — open target URL via Chrome DevTools MCP, inject two-mode toolbar (Catch Design Theme + Copy Design as Mockup) via direct evaluate_script injection, collect design data with semantic element naming/purpose/relationships, save as referenced-elements.json via MCP. Triggers on "uiux-reference", "execute uiux-reference", "collect design references".
---

# UIUX Reference Tool v3.1

## Purpose

AI Agents follow this skill to execute the UIUX reference workflow:
1. Navigate to a target URL via Chrome DevTools MCP
2. Optionally handle an authentication prerequisite page
3. Inject the toolbar via direct `evaluate_script` call using `toolbar.min.js`
4. Await user data collection (colors with roles, or areas with instructions)
5. Process based on mode: theme → brand-theme-creator, mockup → deep capture + generate

---

## Important Notes

BLOCKING: Chrome DevTools MCP must be configured and Chrome must be open with DevTools MCP connected before executing this skill.

CRITICAL: The toolbar source is at `references/toolbar.min.js`. The agent must READ this file, wrap its entire contents in an arrow function `() => { <contents> }`, and pass that as the `function` parameter to `evaluate_script`. No parsing or IIFE stripping needed. This works because CDP's `Runtime.evaluate` bypasses page CSP. Do NOT use `eval()`, compressed injection, or `<script>` tags.

CRITICAL: Do NOT modify the toolbar code. Read and inject exactly as provided.

CRITICAL: Do NOT use `<script src="...">` tag injection — external sites block cross-origin scripts via CSP/CORB. Always use direct code evaluation via `evaluate_script`.

CRITICAL: After completing analyze or generate processing, the agent MUST re-enable toolbar buttons. See `references/code-snippets.md#re-enable-buttons` for the exact evaluate_script code.

CRITICAL: Area screenshots MUST use coordinate-based cropping from a viewport screenshot — do NOT use `take_screenshot(uid: ...)` for area captures. The DOM element's rendered size often differs from the user's selected bounding box (e.g., the element may be 197px tall but the user selected a 305px area that includes siblings below). Correct approach: take viewport screenshot → crop to `bounding_box` coordinates (scaled by `devicePixelRatio`).

---

## About

This tool skill automates the collection of design reference data from external web pages using a two-mode wizard toolbar:

- **Catch Design Theme** — Pick colors via magnifier, annotate roles (primary/secondary/accent/custom), create design theme
- **Copy Design as Mockup** — Select areas via smart-snap, add instructions, agent analyzes via 6-dimension rubric, generate mockup with 99% accuracy target

**Key Concepts:**
- **Direct Injection** — Toolbar source (`toolbar.min.js`, ~20KB IIFE) is read and passed directly to `evaluate_script`. CDP's `Runtime.evaluate` bypasses page CSP, so no `eval()` or script tags are needed.
- **EyeDropper API** — Uses native browser EyeDropper API (Chromium) for pixel-accurate color picking. Falls back to `elementsFromPoint` CSS sampling.
- **Bi-directional Communication** — `__xipeRefReady` (toolbar→agent) + `__xipeRefCommand` (agent→toolbar) for deep captures.
- **Data Schema v2.0** — `colors[]` with `role` field, `areas[]` with `html_css`, `instruction`, `agent_analysis`. See `references/data-schema.md`.

---

## When to Use

```yaml
triggers:
  - "uiux-reference"
  - "execute uiux-reference"
  - "collect design references"
  - "extract colors from page"
  - "catch design theme"
  - "copy design as mockup"

not_for:
  - "x-ipe-task-based-code-implementation: Building or modifying the toolbar code"
  - "mcp-builder: Creating MCP servers"
```

---

## Input Parameters

```yaml
input:
  url: "{target URL}"           # Required — page to extract references from
  auth_url: "{auth URL}"        # Optional — login page to visit first
  extra: "{instructions}"       # Optional — focus instructions for user
  idea_folder: "{folder name}"  # Required — derived from context or asked
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Chrome DevTools MCP connected</name>
    <verification>Verify chrome-devtools MCP tools are available (navigate_page, evaluate_script, take_screenshot, take_snapshot)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target URL provided</name>
    <verification>url parameter is a valid HTTP/HTTPS URL</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Idea folder identified</name>
    <verification>idea_folder is known from context or asked from user</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>save_uiux_reference MCP tool available</name>
    <verification>App-Agent Interaction MCP server is running (provides save_uiux_reference tool)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: execute_reference

**When:** Agent receives `uiux-reference` prompt with `--url` parameter.

```xml
<operation name="execute_reference">
  <action>
    1. PARSE prompt arguments:
       - Extract --url (required), --auth-url (optional), --extra (optional)
       - IF --url is missing: REPORT error "URL is required", STOP
       - IF idea_folder is unknown: ASK user "Which idea folder should I save to?"

    2. IF --auth-url provided:
       a. CALL navigate_page(url: auth_url)
       b. INFORM user: "Please log in. I'll detect when authentication completes."
       c. LOOP every 3s (max 5 min): check if current_url changed from auth_url
       d. IF timeout: ASK user "Auth timeout. Type 'skip' to proceed or 'retry'."

    3. CALL navigate_page(url: target_url)
       - Wait for page load (30s timeout)
       - IF page fails to load: REPORT error "Failed to load {url}", STOP

    4. INJECT TOOLBAR (direct evaluate_script):
       a. READ file: .github/skills/x-ipe-tool-uiux-reference/references/toolbar.min.js
       b. Wrap the entire file contents in an arrow function: `() => { <file contents> }`
          and pass to `evaluate_script(function: "() => { <file contents> }")`.
          No parsing or stripping needed — the IIFE executes inside the wrapper function.
          This works because CDP Runtime.evaluate bypasses page CSP entirely.
       c. VERIFY: evaluate_script(() => window.__xipeToolbarReady) returns true. Retry up to 5 times if false.
       d. INFORM user: "Toolbar injected. Use Catch Theme or Copy Mockup mode."
       e. IF --extra provided: INFORM user the extra instructions

    5. AWAIT USER DATA (two-phase polling):
       PHASE 1 — Auto-poll (10 min):
       - LOOP every 10s (max 10 min / 60 iterations):
         - result = evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
         - IF result is not null: DATA RECEIVED, break
       PHASE 2 — Manual poll (after 10 min timeout):
       - INFORM user: "Auto-poll timed out after 10 min. Type 'poll' when ready."
       - WAIT for user to say "poll", then:
         - result = evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
         - IF result is null: INFORM user "No data yet. Type 'poll' again."
         - IF result is not null: DATA RECEIVED, proceed

    6. PROCESS BASED ON MODE:
       IF result.mode === "theme" → Go to Operation: process_theme
       IF result.mode === "mockup" → Go to Operation: process_mockup
  </action>
  <constraints>
    - BLOCKING: Do NOT proceed past step 3 if page fails to load
    - CRITICAL: Inject via direct evaluate_script with toolbar.min.js contents — do NOT use eval(), compressed injection, or script tags
    - CRITICAL: Do NOT click or interact with the toolbar — user does this manually
  </constraints>
  <output>Mode-specific processing triggered</output>
</operation>
```

### Operation: process_theme

**When:** User clicks "Create Theme" and result.mode === "theme".

```xml
<operation name="process_theme">
  <action>
    1. READ annotated colors from result.colors (each has: id, hex, rgb, hsl, source_selector, role)

    2. CONSTRUCT theme reference data:
       { version: "2.0", source_url, timestamp: ISO 8601 now, idea_folder, colors: result.colors }

    3. CALL save_uiux_reference(data: constructed_json)

    4. INVOKE brand-theme-creator skill with the annotated colors
       - Pass colors with their semantic roles → generates design-system.md + component-visualization.html

    5. INFORM user: "Theme created — {N} colors extracted from {url}"
  </action>
</operation>
```

### Operation: process_mockup

**When:** User clicks "Analyze" or "Generate Mockup". The `result.action` field determines sub-flow. After each sub-flow, resume polling. Do NOT auto-trigger generation after analysis.

```xml
<operation name="process_mockup">
  <action>
    1. READ result from __xipeRefData
       - result.action === "analyze" → ANALYZE FLOW (step 2)
       - result.action === "generate" → GENERATE FLOW (step 8)

    === ANALYZE FLOW ===

    2. READ areas from result.areas
       - Each has: id, selector, tag, bounding_box, screenshot_dataurl,
         html_css (level, computed_styles, outer_html), instruction

    3. AREA SCREENSHOTS (coordinate-based crop — NEVER use UID-based):
       a. VIEWPORT screenshot: take_screenshot(filePath: "{path}/full-page.png") — do NOT use fullPage: true
       b. Get devicePixelRatio: evaluate_script(() => window.devicePixelRatio)
       c. FOR EACH area:
          i.   Scroll so bounding_box center is in viewport
          ii.  Take viewport screenshot
          iii. Crop to bounding_box coordinates (multiply x/y/width/height by devicePixelRatio)
          iv.  Save as screenshots/{area_id}.png
       ⚠️ Do NOT use take_screenshot(uid: ...) — the DOM element's rendered size
          often differs from the user's selected bounding_box.
       d. The ARIA workaround (code-snippets.md#aria-workaround-screenshot) is ONLY
          for element-level screenshots in other contexts, NOT for area captures.

    3b. VISUAL INSPECTION OF SCREENSHOTS (agent reasoning — builds key_elements_identified_from_screenshot):
        FOR EACH area:
        a. VIEW area screenshot ({area_id}.png) + full-page screenshot (full-page.png)
        b. Identify ALL visually significant elements by examining the screenshots:
           - From {area_id}.png: headings, text blocks, buttons, inputs, images, icons, etc.
           - From full-page.png: background colors/gradients, overlays, borders, shadows
             that are VISUALLY PRESENT in the area but may come from ancestor elements
        c. For each identified element, record:
           { "element": "<descriptive-name>", "purpose": "<what it does visually>",
             "examined_from_screenshot": "<area-1.png or full-page.png>" }
        d. Store as area.key_elements_identified_from_screenshot
        ⚠️ This step catches visual properties (backgrounds, overlays) inherited from
           ancestors that DOM element discovery within bounding_box would miss.

    4. ELEMENT DISCOVERY + ENRICHMENT:
       FOR EACH area:
       a. Discover ALL elements within bounding_box via evaluate_script
          (see references/code-snippets.md#element-discovery)
       b. Store as area.discovered_elements
       c. ENRICH (agent reasoning step — not DOM queries):
          - element_name: short descriptive name (e.g., "hero-heading", "cta-button")
          - purpose_of_the_element: one sentence describing visual/functional role
          - relationships_to_other_elements: [{element, relationship, mimic_tips}]
            mimic_tips MUST use two-part template:
              "to_element_itself: {describe own styles: color, font, size, margin, padding, border, bg...},
               to_relevant_elements: {describe spatial/structural relationship to the named element}"
            Example: "to_element_itself: font-size:56px, font-weight:440, color:#fff, text-align:center, margin:0,
                      to_relevant_elements: 20px above hero-subtext, centered in flex-column container"
          - element_details: { tag, text_content, classes, styles, resources }
       d. ANCESTOR BACKGROUND CAPTURE:
          FOR EACH area, walk up from snap_selector to <body> via evaluate_script:
          - Collect first non-transparent backgroundColor and any backgroundImage/gradient
          - Add as an enriched element (e.g., "section-background") with the ancestor's styles
          - This ensures backgrounds inherited from parent containers are captured
       e. RECONCILE with key_elements_identified_from_screenshot (from step 3b):
          - Compare visual elements identified from screenshots against DOM-discovered elements
          - IF a screenshot-identified element is MISSING from discovered elements: investigate
            (e.g., background from ancestor, overlay, pseudo-element) and add it
          - IF a discovered element is NOT visually significant: keep but deprioritize
          - This step ensures the enriched elements accurately reflect what the user sees

    5. RESOURCE DOWNLOAD:
       FOR EACH area with enriched elements:
       a. Collect resource URLs from element_details.resources (img src, background-image, fonts)
       b. Deduplicate, download via page-context fetch (see references/code-snippets.md#resource-download)
       c. Detect @font-face URLs (see references/code-snippets.md#font-detection)
       d. Save to resources/ folder, update element_details with local_path

    6. EVALUATE via 6-dimension rubric (layout, typography, color_palette, spacing, visual_effects, static_resources):
       - Rate each dimension: confident/uncertain/missing
       - IF any "missing": write deep capture command, poll for enriched data, re-evaluate

    6b. PERSIST as referenced-elements.json (single source of truth):
        a. Construct from enriched data (see references/data-schema.md for full schema)
        b. Write to {idea_folder}/uiux-references/page-element-references/referenced-elements.json
        c. CALL save_uiux_reference(data: {...}) — service also generates:
           summarized-uiux-reference.md, {area-id}-structure.html, {area-id}-styles.css, mimic-strategy.md
        d. Verify generated files exist; create manually if missing

    7. RE-ENABLE BUTTONS + RESUME POLLING:
       a. Execute re-enable script (see references/code-snippets.md#re-enable-buttons)
       b. INFORM user: "Analysis complete — {N} areas analyzed"
       c. Resume two-phase polling (same as step 5):
          - PHASE 1: Auto-poll every 10s for up to 10 min
          - PHASE 2: Fall back to manual "poll" if timeout

    === GENERATE FLOW ===

    8. LOAD referenced-elements.json from page-element-references/
       - If missing, fall back to result.areas from toolbar data

    9. PERSIST BEFORE GENERATE: CALL save_uiux_reference with current data

    10. GENERATE versioned mockup:
        a. Scan for existing mockup-v*.html → next version. NEVER overwrite.
        b. SCOPE: Include ALL discovered_elements in bounding_box, not just snap element subtree.
           Use element_name as CSS class, replicate tag/text/styles, use relationships for layout.
        c. GENERATE INITIAL MOCKUP:
           - Combine referenced-elements.json, downloaded resources (page-element-references/resources/),
             context insights, and mimic-strategy.md to produce mockup-v{N}.html.
           - Apply mimic_tips (to_element_itself + to_relevant_elements) for exact styling and layout.
        d. SUB-AGENT CRITIQUE (iteration 1):
           - Launch a sub-agent (task tool, agent_type: "general-purpose") with prompt:
             "Review this mockup against the original. You are given:
              1. referenced-elements.json — the enriched element data
              2. area-{n}.png — screenshot of the original area
              3. mockup-v{N}.html — the generated mockup
              Compare every element: colors, fonts, sizes, spacing, layout, backgrounds.
              Provide critique but constructive feedback — list SPECIFIC mismatches with
              exact values (expected vs actual) and how to fix each one."
           - Pass file paths for referenced-elements.json, area-{n}.png, and mockup-v{N}.html
        e. OPTIMIZE MOCKUP (iteration 1):
           - Apply ALL feedback from the sub-agent critique to fix the mockup.
           - Save changes to the SAME mockup-v{N}.html file.
        f. SUB-AGENT PIXEL COMPARISON (iteration 2):
           - Open mockup in a NEW browser tab via new_page(url: "file://...mockup-v{N}.html")
             ⚠️ NEVER navigate_page on the target website tab — always use new_page() so the
             original page with the injected toolbar remains intact for further polling.
           - Take screenshot of the mockup tab → mockup-v{N}-screenshot.png
           - Close the mockup tab via close_page() and re-select the target page via select_page()
           - Launch a sub-agent (task tool, agent_type: "general-purpose") with prompt:
             "Compare mockup-v{N}-screenshot.png with area-{n}.png pixel-by-pixel.
              The mockup should be 100% identical to the selected area.
              If NOT matched: list every remaining difference with critique but constructive
              feedback — exact CSS values, pixel offsets, color hex codes that differ.
              If matched: confirm '100% match achieved'."
           - Pass file paths for both screenshots
        g. FINAL OPTIMIZATION (iteration 2):
           - IF sub-agent reports mismatches: apply feedback, save mockup-v{N}.html.
           - IF sub-agent confirms 100% match: done, proceed to step 11.

    11. RE-ENABLE + RESUME:
        a. Execute re-enable script (see references/code-snippets.md#re-enable-buttons)
        b. INFORM user: "Mockup mockup-v{N}.html generated — {M} areas from {url}"
        c. Resume two-phase polling (same as step 5):
           - PHASE 1: Auto-poll every 10s for up to 10 min
           - PHASE 2: Fall back to manual "poll" if timeout
  </action>
  <constraints>
    - CRITICAL: Do NOT auto-trigger generation after analysis — wait for user click
    - CRITICAL: referenced-elements.json is single source of truth — no session files
    - CRITICAL: Versioned filenames (mockup-v{N}.html) — never overwrite
    - CRITICAL: Mockup scope matches selected area bounding box
    - CRITICAL: Agent MUST enrich elements with semantic names, purpose, relationships (step 4c)
    - CRITICAL: Agent MUST visually inspect screenshots BEFORE element discovery (step 3b) and reconcile after (step 4e)
    - CRITICAL: Agent MUST capture ancestor backgrounds via DOM walk-up (step 4d) — visual backgrounds often come from parent elements, not the selected element itself
    - CRITICAL: For elements without a11y UIDs, use ARIA workaround (step 3d, from LL-001) — but NEVER for area screenshots
    - CRITICAL: Area screenshots MUST use coordinate-based crop (viewport screenshot → crop by bounding_box × devicePixelRatio). NEVER use take_screenshot(uid) for areas.
    - CRITICAL: Generate flow uses 2 sub-agent iterations: (1) critique + optimize, (2) pixel comparison + final fix
    - CRITICAL: Sub-agents must receive file paths to referenced-elements.json, area screenshots, and mockup HTML
    - CRITICAL: When opening mockup for screenshot/comparison, ALWAYS use new_page() to open in a new tab — NEVER navigate_page on the target website tab, as this destroys the injected toolbar and breaks further polling
    - After each flow, always re-enable buttons and resume polling
  </constraints>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    mode: "theme" | "mockup"
    colors_count: "{N}"
    areas_count: "{M}"
    source_url: "{url}"
    referenced_elements_file: "page-element-references/referenced-elements.json"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Target page navigated successfully</name>
    <verification>Page loaded without errors</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Toolbar injected via direct evaluate_script</name>
    <verification>toolbar.min.js read and passed to evaluate_script, __xipeToolbarReady is true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>User data received</name>
    <verification>__xipeRefReady returned true with data</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Data saved via MCP</name>
    <verification>save_uiux_reference returned success</verification>
  </checkpoint>
  <checkpoint required="true" mode="theme">
    <name>Theme colors saved with roles</name>
    <verification>Colors array with role annotations saved, brand-theme-creator invoked</verification>
  </checkpoint>
  <checkpoint required="true" mode="mockup">
    <name>referenced-elements.json persisted</name>
    <verification>Single source of truth file written to page-element-references/ with enriched elements</verification>
  </checkpoint>
  <checkpoint required="true" mode="mockup">
    <name>Buttons re-enabled after processing</name>
    <verification>Re-enable script executed, polling resumed for next user action</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| URL is required | No --url parameter | Report error, ask user to provide URL |
| Failed to load page | Network error, invalid URL | Report error, suggest user check URL |
| Auth timeout | Login not completed in 5 min | Prompt user to skip or retry |
| Toolbar init failed | CSP blocking or page error | Retry evaluate_script injection once |
| Session timeout | User didn't send data in 30 min | Inform user, suggest re-running |
| Deep capture failed | Element removed from DOM | Log warning, use available data |
| Screenshot failed — no UID | Element lacks a11y UID | Use ARIA workaround (LL-001): add temp role/aria-label, re-snapshot |
| Save failed | MCP server error | Report MCP error to user |

---

## Templates

| File | Purpose |
|------|---------|
| `references/toolbar.min.js` | Toolbar IIFE source (~20KB) — primary injection source |
| `references/code-snippets.md` | JavaScript code blocks for evaluate_script calls |
| `references/data-schema.md` | referenced-elements.json full schema and example |
| `references/examples.md` | Usage examples for theme and mockup workflows |
| `references/toolbar-template.md` | Legacy toolbar IIFE template (v1 reference) |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
