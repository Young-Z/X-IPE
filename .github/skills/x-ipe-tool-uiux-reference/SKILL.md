---
name: x-ipe-tool-uiux-reference
description: Execute UIUX reference workflow v2.0 — open target URL via Chrome DevTools MCP, inject two-mode toolbar (Catch Design Theme + Copy Design as Mockup), collect design data, save via MCP. Triggers on "uiux-reference", "execute uiux-reference", "collect design references".
---

# UIUX Reference Tool v2.0

## Purpose

AI Agents follow this skill to execute the UIUX reference workflow:
1. Navigate to a target URL via Chrome DevTools MCP
2. Optionally handle an authentication prerequisite page
3. Inject the v2.0 toolbar via 3-stage injection (core + theme mode + mockup mode)
4. Provide viewport screenshot for offscreen canvas color picking
5. Await user data collection (colors with roles, or components with instructions)
6. Process based on mode: theme → brand-theme-creator, mockup → deep capture + generate

---

## Important Notes

BLOCKING: Chrome DevTools MCP must be configured and Chrome must be open with DevTools MCP connected before executing this skill.

CRITICAL: The toolbar is split into 3 files for staged injection:
- `references/toolbar-core.min.js` — Shell (inject first)
- `references/toolbar-theme.min.js` — Theme mode
- `references/toolbar-mockup.min.js` — Mockup mode

CRITICAL: Do NOT modify the toolbar code. Inject each file exactly as provided.

CRITICAL: After core injection, provide a viewport screenshot via `__xipeViewportScreenshot` for the offscreen canvas color picker.

---

## About

This tool skill automates the collection of design reference data from external web pages using a two-mode wizard toolbar:

- **Catch Design Theme** — Pick colors via magnifier, annotate roles (primary/secondary/accent/custom), create design theme
- **Copy Design as Mockup** — Select components via smart-snap, add instructions, agent analyzes via 5-dimension rubric, generate mockup

**Key Concepts:**
- **Staged Injection** — Core shell first (<10KB), then mode scripts. Faster first paint vs v1.x single-file approach.
- **Offscreen Canvas** — Agent provides viewport screenshot, toolbar loads into canvas for pixel-accurate color picking.
- **Bi-directional Communication** — `__xipeRefReady` (toolbar→agent) + `__xipeRefCommand` (agent→toolbar) for deep captures.
- **Data Schema v2.0** — `colors[]` with `role` field, `components[]` with `html_css`, `instruction`, `agent_analysis`.

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
    <verification>App-Agent Interaction MCP server is running</verification>
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
       c. LOOP every 3 seconds (max 5 minutes):
          - current_url = evaluate_script(() => window.location.href)
          - IF current_url path/domain changed from auth_url: AUTH COMPLETE, break
          - IF 5 minutes elapsed: ASK user "Auth timeout. Type 'skip' to proceed or 'retry'."
       d. IF user skips or auth completes: continue to step 3

    3. CALL navigate_page(url: target_url)
       - Wait for page load (30s timeout)
       - IF page fails to load: REPORT error "Failed to load {url}", STOP

    4. INJECT TOOLBAR (3-stage):
       a. READ references/toolbar-core.min.js
          - CALL evaluate_script(function: CORE_CODE)
       b. POLL: evaluate_script(() => window.__xipeToolbarReady) every 1s, max 10s
          - IF timeout: REPORT error "Core toolbar failed to initialize", STOP
       c. READ references/toolbar-theme.min.js
          - CALL evaluate_script(function: THEME_CODE)
       d. READ references/toolbar-mockup.min.js
          - CALL evaluate_script(function: MOCKUP_CODE)
       e. INFORM user: "Toolbar injected. Use Catch Theme or Copy Mockup mode."
       f. IF --extra provided: INFORM user the extra instructions

    5. PROVIDE VIEWPORT SCREENSHOT:
       - CALL take_screenshot(format: "png") — returns base64 data
       - CALL evaluate_script with function:
         (dataUrl) => { window.__xipeViewportScreenshot = dataUrl; }
         passing the screenshot data URL as argument
       - This populates the offscreen canvas for color picking

    6. AWAIT USER DATA:
       LOOP every 3 seconds (max 30 minutes):
       - result = evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
       - IF result is not null: DATA RECEIVED, break
       - IF 30 minutes elapsed: INFORM user "Session timed out.", STOP

    7. PROCESS BASED ON MODE:

       IF result.mode === "theme":
         → Go to Operation: process_theme

       IF result.mode === "mockup":
         → Go to Operation: process_mockup

  </action>
  <constraints>
    - BLOCKING: Do NOT proceed past step 3 if page fails to load
    - CRITICAL: Inject toolbar files exactly as read — do NOT modify code
    - CRITICAL: Do NOT click or interact with the toolbar — user does this manually
    - CRITICAL: Provide viewport screenshot AFTER toolbar injection
  </constraints>
  <output>Mode-specific processing triggered</output>
</operation>
```

### Operation: process_theme

**When:** User clicks "Create Theme" and result.mode === "theme".

```xml
<operation name="process_theme">
  <action>
    1. READ annotated colors from result.colors
       - Each color has: id, hex, rgb, hsl, source_selector, role

    2. CONSTRUCT theme reference data:
       {
         version: "2.0",
         source_url: target_url,
         timestamp: ISO 8601 now,
         idea_folder: idea_folder,
         colors: result.colors (with roles)
       }

    3. CALL save_uiux_reference(data: constructed_json)

    4. INVOKE brand-theme-creator skill with the annotated colors
       - Pass colors with their semantic roles
       - This generates design-system.md and component-visualization.html

    5. INFORM user: "Theme created — {N} colors extracted from {url}"
  </action>
</operation>
```

### Operation: process_mockup

**When:** User clicks "Analyze" or "Generate" and result.mode === "mockup".

```xml
<operation name="process_mockup">
  <action>
    1. READ components from result.components
       - Each has: id, selector, tag, bounding_box, screenshot_dataurl,
         html_css (level, computed_styles, outer_html), instruction

    2. EVALUATE each component via 5-dimension rubric:
       For each component:
       - layout: Can I determine the layout structure? (confident/uncertain/missing)
       - typography: Do I have font info? (confident/uncertain/missing)
       - color_palette: Do I have color info? (confident/uncertain/missing)
       - spacing: Do I have margin/padding/gap info? (confident/uncertain/missing)
       - visual_effects: Do I have shadow/border/gradient info? (confident/uncertain/missing)

    3. IF any dimension is "missing":
       a. WRITE deep capture command:
          evaluate_script(() => {
            window.__xipeRefCommand = { action: "deep_capture", target: "{comp_id}" };
          })
       b. POLL: evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
          - Toolbar will capture full computed styles + outerHTML
          - Wait for __xipeRefReady (max 15s per component)
       c. Re-evaluate rubric with enriched data

    4. TAKE element screenshots:
       - CALL take_screenshot(fullPage: true, filePath: "{screenshots_path}/full-page.png")
       - FOR each component: use take_snapshot() + bounding_box matching to take_screenshot(uid: ...)
       - Save to {idea_folder}/uiux-references/screenshots/

    5. CONSTRUCT reference data:
       {
         version: "2.0",
         source_url: target_url,
         timestamp: ISO 8601 now,
         idea_folder: idea_folder,
         components: result.components (with analysis),
         colors: result.colors (if any from theme mode)
       }

    6. CALL save_uiux_reference(data: constructed_json) — Step 4a: PERSIST BEFORE GENERATE

    7. GENERATE mockup from captured data
       - Use component data to create HTML/CSS mockup
       - Take screenshot of generated mockup
       - Compare to original component screenshots
       - IF match < target: re-analyze and regenerate (max 3 iterations)
       - IF 3 iterations exhausted: ASK user "Approve current result?"

    8. INFORM user: "Mockup generated — {N} components from {url}"
  </action>
  <constraints>
    - CRITICAL: Save data (step 6) BEFORE generation (step 7)
    - Deep capture command waits for toolbar to process and signal ready
    - Max 3 auto-iterations for mockup validation
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
    components_count: "{M}"
    source_url: "{url}"
    session_file: "ref-session-{NNN}.json"
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
    <name>Toolbar injected (3-stage)</name>
    <verification>evaluate_script executed for core + theme + mockup without errors. __xipeToolbarReady is true.</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Viewport screenshot provided</name>
    <verification>__xipeViewportScreenshot set on page</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>User data received</name>
    <verification>__xipeRefReady returned true with data</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Data saved via MCP</name>
    <verification>save_uiux_reference returned success</verification>
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
| Core toolbar init failed | CSP or page error | Retry once; if fails, report to user |
| Session timeout | User didn't send data in 30 min | Inform user, suggest re-running |
| Deep capture failed | Element removed from DOM | Log warning, use available data |
| Screenshot failed | Element not in snapshot | Skip element crop, continue |
| Save failed | MCP server error | Report MCP error to user |

---

## Templates

| File | Purpose |
|------|---------|
| `references/toolbar-core.min.js` | Core shell IIFE — inject first |
| `references/toolbar-theme.min.js` | Theme mode IIFE — inject second |
| `references/toolbar-mockup.min.js` | Mockup mode IIFE — inject third |
| `references/toolbar-template.md` | DEPRECATED — v1.x single-file template |
