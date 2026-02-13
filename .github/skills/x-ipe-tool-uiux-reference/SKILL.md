---
name: x-ipe-tool-uiux-reference
description: Execute UIUX reference workflow — open target URL via Chrome DevTools MCP, inject interactive toolbar, collect colors and elements, take screenshots, save reference data via save_uiux_reference MCP tool. Triggers on "uiux-reference", "execute uiux-reference", "collect design references".
---

# UIUX Reference Tool

## Purpose

AI Agents follow this skill to execute the UIUX reference workflow:
1. Navigate to a target URL via Chrome DevTools MCP
2. Optionally handle an authentication prerequisite page
3. Inject an interactive toolbar (Color Picker + Element Highlighter)
4. Await user data collection and "Send References" callback
5. Take element screenshots and save reference data via MCP

---

## Important Notes

BLOCKING: Chrome DevTools MCP must be configured and Chrome must be open with DevTools MCP connected before executing this skill.

CRITICAL: The toolbar IIFE source is in `references/toolbar-template.md`. Read that file and pass the code block contents to `evaluate_script` for injection.

CRITICAL: Do NOT modify the toolbar IIFE code. Inject it exactly as provided.

---

## About

This tool skill automates the collection of design reference data (colors, element screenshots, CSS selectors) from external web pages. The agent acts as an intermediary between the user's browser interactions and the X-IPE data persistence layer.

**Key Concepts:**
- **Toolbar IIFE** — A self-contained JavaScript function injected into the target page via `evaluate_script`. It provides Color Picker and Element Highlighter tools.
- **Callback Mechanism** — The toolbar sets `window.__xipeRefReady = true` and stores data in `window.__xipeRefData` when the user clicks "Send References". The agent polls via `evaluate_script` to detect this.
- **Reference Data Schema** — JSON v1.0 format with `colors[]`, `elements[]`, and optional `design_tokens`.

---

## When to Use

```yaml
triggers:
  - "uiux-reference"
  - "execute uiux-reference"
  - "collect design references"
  - "extract colors from page"

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
    <verification>Verify chrome-devtools MCP tools are available (navigate_page, evaluate_script, take_screenshot)</verification>
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

    4. READ toolbar IIFE source from references/toolbar-template.md
       - Extract the JavaScript code block content
       - CALL evaluate_script(function: TOOLBAR_IIFE_CODE)
       - INFORM user: "Toolbar injected. Use Color Picker or Element Highlighter, then click 'Send References' when done."
       - IF --extra provided: INFORM user the extra instructions

    5. LOOP every 3 seconds (max 30 minutes):
       - result = evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
       - IF result is not null: DATA RECEIVED, break
       - IF 30 minutes elapsed: INFORM user "Session timed out.", STOP

    6. FOR each element in result.elements:
       a. Mark element for screenshot:
          evaluate_script((sel) => { const el = document.querySelector(sel); if(el) el.setAttribute('data-xipe-target','true'); }, with selector arg)
       b. full_screenshot = take_screenshot(fullPage: true)
       c. snapshot = take_snapshot()
       d. Find element with data-xipe-target in snapshot, get its UID
       e. IF UID found: element_screenshot = take_screenshot(uid: found_uid)
       f. Remove marker: evaluate_script(() => { const el = document.querySelector('[data-xipe-target]'); if(el) el.removeAttribute('data-xipe-target'); })
       g. Attach screenshots to element data (base64-encoded with "base64:" prefix)

    7. CONSTRUCT Reference Data JSON:
       {
         version: "1.0",
         source_url: target_url,
         auth_url: auth_url or null,
         timestamp: ISO 8601 now,
         idea_folder: idea_folder,
         colors: result.colors,
         elements: result.elements (with screenshot data),
         design_tokens: result.design_tokens
       }

    8. CALL save_uiux_reference(data: constructed_json)
       - IF success: INFORM user "Reference data saved — {N} colors, {M} elements from {url}. Session: {session_file}"
       - IF failure: REPORT error from MCP response
  </action>
  <constraints>
    - BLOCKING: Do NOT proceed past step 3 if page fails to load
    - CRITICAL: Inject toolbar IIFE exactly as read from toolbar-template.md
    - CRITICAL: Do NOT click or interact with the toolbar — user does this manually
  </constraints>
  <output>Reference data saved via save_uiux_reference MCP tool</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    colors_count: "{N}"
    elements_count: "{M}"
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
    <name>Toolbar injected</name>
    <verification>evaluate_script executed without errors</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>User data received</name>
    <verification>__xipeRefReady returned true with data</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Screenshots captured</name>
    <verification>Each element has full_page and element_crop screenshots</verification>
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
| URL is required | No --url parameter in prompt | Report error, ask user to provide URL |
| Failed to load page | Network error, invalid URL, 4xx/5xx | Report error with URL, suggest user check URL |
| Auth timeout | User didn't complete login within 5 min | Prompt user to skip or retry |
| Toolbar injection failed | CSP or page error | Retry once; if fails again, report to user |
| Session timeout | User didn't click Send within 30 min | Inform user, suggest re-running command |
| Screenshot failed | Element not found in snapshot | Log warning, skip element crop, continue |
| Save failed | MCP server error or Flask endpoint down | Report MCP error message to user |

---

## Templates

| File | Purpose |
|------|---------|
| `references/toolbar-template.md` | Contains the toolbar IIFE source code for injection |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
