---
name: x-ipe-tool-learning-behavior-tracker-for-web
description: Record and analyze user behavior on any website for AI agent training. Injects tracker IIFE via Chrome DevTools, captures DOM events (click, dblclick, contextmenu, input, scroll, navigation, resize, focus, drag) with PII masking, and outputs structured behavior-recording JSON with flow narrative, key paths, pain points, and AI annotations. Triggers on "track behavior", "record user behavior", "learn from website".
---

> **⚠️ CRITICAL RULE FOR AI AGENTS EXECUTING SUGGESTED SKILLS:**
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.

# Web Behavior Learning & Tracker

## Purpose

AI Agents follow this skill to record and analyze user behavior on target websites for AI agent training data:
1. Open target URL and inject tracker IIFE via Chrome DevTools MCP
2. Capture DOM events with PII masking in a circular buffer
3. On stop: collect events, run post-processing, output structured JSON

---

## Important Notes

BLOCKING: Requires active Chrome DevTools MCP connection (`navigate_page` + `evaluate_script` tools).
CRITICAL: Use `tracker-toolbar.mini.js` for injection — the minified version. `tracker-toolbar.js` is the readable source for development.
CRITICAL: Password fields are NEVER revealed, even if whitelisted. PII masking defaults to mask-everything.
BLOCKING: IIFE guard `window.__xipeBehaviorTrackerInjected` prevents double injection. Re-injection on navigation requires clearing the flag first.

---

## About

This tool injects a JavaScript IIFE into target web pages via Chrome DevTools Protocol. The IIFE runs in a closed Shadow DOM and records user interactions as structured events. Events are stored in a circular buffer, masked for PII, and post-processed into training-ready JSON.

**Key Concepts:**
- **IIFE Guard** — `window.__xipeBehaviorTrackerInjected` flag prevents duplicate injection
- **Circular Buffer** — Fixed-capacity (default 10,000) event store; silently prunes oldest
- **PII Masking** — Default mask-everything with CSS-selector whitelist for opt-in reveal; password fields never exposed
- **Shadow DOM Toolbox** — Glass-morphism floating toolbar (closed mode, z-index 2147483640)
- **Post-Processing** — Generates flow narrative, key paths, pain points, and per-event AI annotations

---

## When to Use

```yaml
triggers:
  - "track behavior"
  - "record user behavior"
  - "learn from website"
  - "behavior tracking"
  - "capture user interactions"

not_for:
  - "UX analytics dashboards — this produces AI training data, not business metrics"
  - "Automated testing — use testing frameworks instead"
```

---

## Input Parameters

```yaml
input:
  operation: "inject | collect | stop | post_process"
  session:
    url: "https://example.com"           # Required — target website URL
    purpose: "Checkout flow analysis"     # Required — tracking purpose (≤200 words)
  config:
    pii_whitelist: []                     # Optional — CSS selectors to reveal
    buffer_capacity: 10000                # Optional — max events before pruning
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />

  <field name="session.url">
    <steps>
      1. Validate URL has http:// or https:// protocol
      2. IF invalid → fail with INVALID_URL
    </steps>
  </field>

  <field name="session.purpose">
    <steps>
      1. Read from user input (required, max 200 words)
      2. IF empty → fail with PURPOSE_REQUIRED
    </steps>
  </field>

  <field name="config.pii_whitelist">
    <steps>
      1. Default: [] (mask everything)
      2. IF provided: validate CSS selectors are strings
    </steps>
  </field>

  <field name="config.buffer_capacity">
    <steps>
      1. Default: 10000
      2. IF provided: must be positive integer
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Chrome DevTools Available</name>
    <verification>navigate_page and evaluate_script tools accessible via MCP</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Valid URL Provided</name>
    <verification>URL has http:// or https:// protocol and valid hostname</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Purpose Provided</name>
    <verification>Non-empty purpose string, ≤200 words</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Setup

**When:** Creating a new tracking session with output folder.

```xml
<operation name="setup">
  <action>
    1. Create BehaviorTrackerSkill instance with URL and purpose
    2. Call setup_output_folder(project_root, folder_name) to create:
       - x-ipe-docs/learning/{folder_name}/track/
       - x-ipe-docs/learning/{folder_name}/imgs/
    3. The folder_name should be semantic (e.g., "checkout-flow-shopify")
  </action>
  <output>session_id, output_folder_path</output>
</operation>
```

### Operation: Inject

**When:** Injecting the passive event capture IIFE into a target page.

```xml
<operation name="inject">
  <action>
    1. Call navigate_page to open target URL in Chrome
    2. Build injection script via InjectionManager.build_injection_script()
       - Reads tracker-toolbar.mini.js (< 5KB)
       - Prepends __xipeConfig with sessionId, purpose, piiWhitelist, bufferCapacity
    3. Call evaluate_script to inject the IIFE into the page
    4. Mark session as started
  </action>
  <constraints>
    - BLOCKING: Must use tracker-toolbar.mini.js for injection
    - BLOCKING: IIFE guard prevents double injection
    - BLOCKING: After injection, start polling IMMEDIATELY — do NOT ask user if they are ready
  </constraints>
  <output>injection_status</output>
</operation>
```

### Operation: Poll (5s Loop)

**When:** Every 5 seconds after injection to collect events and detect changes.

```xml
<operation name="poll">
  <action>
    1. Call evaluate_script with InjectionManager.build_collect_script()
       - Returns: {events, eventCount, url, analysisRequested, status}
    2. Call skill.process_poll_result(poll_data) which returns:
       - new_events: bool — if event count increased
       - url_changed: bool — if page URL differs from last known
       - analysis_requested: bool — user clicked Analysis button
    3. IF new_events:
       a. Call take_screenshot → save to skill.get_screenshot_path()
       b. Call skill.write_track_list() to update track-list.json
    4. IF url_changed:
       a. evaluate_script(build_clear_guard_script()) to clear guard
       b. Re-inject: evaluate_script(build_injection_script())
       c. IIFE auto-restores events from localStorage (flushed every 1s during recording)
    5. IF analysis_requested:
       a. Write final track-list.json with all events
       b. Delegate to x-ipe-task-based-application-knowledge-extractor skill
          with track-list.json + screenshots as input
       c. evaluate_script(build_reset_analysis_ui_script()) to reset button
    6. Wait 5 seconds, repeat from step 1
  </action>
  <constraints>
    - BLOCKING: Start polling IMMEDIATELY after inject — do NOT prompt, ask, or wait for user confirmation
    - BLOCKING: Polling interval is 5 seconds (not configurable)
    - BLOCKING: During tracking, the skill ONLY calls evaluate_script to collect data.
      Do NOT use chrome-devtools for navigation, clicking, or any other action.
      The only permitted MCP calls are: evaluate_script (collect/reinject) and take_screenshot.
    - Screenshot only on event count change (not every poll)
    - Analysis triggered ONLY when user clicks Analysis button in toolbar
    - IIFE flushes events to localStorage every 1s during recording — survives page redirects
  </constraints>
  <output>poll_result per iteration</output>
</operation>
```

### Operation: Stop

**When:** Ending the recording session.

```xml
<operation name="stop">
  <action>
    1. Call evaluate_script with InjectionManager.build_stop_script()
    2. Parse returned final events
    3. Mark session as stopped
    4. Write final track-list.json
    5. Update x-ipe-docs/learning/README.md content listing (see Content Listing below)
  </action>
  <output>events[], session_metadata</output>
</operation>
```

### Content Listing

**x-ipe-docs/learning/README.md** is a markdown index of all learning sessions.
The agent MUST update this file after each stop or analysis operation.

Format:
```markdown
# Learning Sessions

| Session | Purpose | URL | Events | Screenshots | Date |
|---------|---------|-----|--------|-------------|------|
| [session-name](./session-name/) | purpose text | url | N | N | YYYY-MM-DD |
```

Each row links to the session folder. Data is read from `track/track-list.json`.

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    session_id: "{uuid}"
    output_folder: "x-ipe-docs/learning/{folder_name}/"
    track_list: "x-ipe-docs/learning/{folder_name}/track/track-list.json"
    screenshots: "x-ipe-docs/learning/{folder_name}/imgs/"
    statistics:
      totalEvents: 0
      pageCount: 0
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation Completed</name>
    <verification>operation_output.success is true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>IIFE Injected</name>
    <verification>window.__xipeBehaviorTrackerInjected is true on target page</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Polling Active</name>
    <verification>Events collected every 5s, screenshots taken on change</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output Folder Created</name>
    <verification>x-ipe-docs/learning/{name}/track/ and imgs/ directories exist</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Track List Written</name>
    <verification>track-list.json exists with schema_version 2.0, session, events</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>PII Masked</name>
    <verification>No raw PII in events — masked with [MASKED] or [PASSWORD_FIELD]</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INJECTION_FAILED` | Chrome DevTools MCP not connected or page not loaded | Verify MCP connection, retry navigate_page |
| `INVALID_URL` | URL missing protocol or invalid hostname | Provide URL with https:// protocol |
| `PURPOSE_REQUIRED` | Empty purpose string | Provide non-empty tracking purpose |
| `COLLECTION_FAILED` | IIFE not injected or page navigated away | Re-inject tracker (poll loop handles this) |
| `POST_PROCESSING_FAILED` | PostProcessor error | Auto-retried once; falls back to raw events |
| `URL_CHANGE_DETECTED` | Page navigated to new URL | Auto-handled: clear guard → reinject → restore from localStorage |

---

## References

| File | Purpose |
|------|---------|
| `references/tracker-toolbar.js` | Readable source — IIFE with RecordingEngine, PIIMasker, CircularBuffer, EventSerializer, minimal UI bar |
| `references/tracker-toolbar.mini.js` | Minified version for injection |
| `scripts/track_behavior.py` | BehaviorTrackerSkill (session orchestrator with polling model) + InjectionManager (script builder) |
| `scripts/__init__.py` | Package init |

---

## Examples

**Example 1: Track checkout flow with 5s polling**
```
User: "Use x-ipe-tool-learning-behavior-tracker-for-web skill to track behavior on https://shop.example.com"
Agent:
  1. setup → creates x-ipe-docs/learning/checkout-flow-shopify/
  2. inject → navigates to URL, injects tracker-toolbar.mini.js
  3. poll loop (every 5s):
     - Events detected → screenshot saved to imgs/
     - track-list.json updated
  4. User clicks Analysis → delegates to knowledge extractor skill
     → generates user manual from tracked behavior
  5. stop → final track-list.json with 847 events, 15 screenshots
```

**Example 2: Multi-page onboarding with URL change detection**
```
User: "Use x-ipe-tool-learning-behavior-tracker-for-web skill to learn from website https://app.example.com/onboard"
Agent:
  1. setup with folder "onboarding-app-example"
  2. inject with purpose "Onboarding flow for AI agent training"
  3. poll loop detects URL change (step1 → step2) → reinjects → continues
  4. 5 URL changes handled automatically
  5. stop → 234 events across 5 pages, screenshots at each transition
```
