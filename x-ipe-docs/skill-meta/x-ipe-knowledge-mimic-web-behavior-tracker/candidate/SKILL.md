---
name: x-ipe-knowledge-mimic-web-behavior-tracker
description: Observe and record user behavior on websites via Chrome DevTools MCP. Injects tracker IIFE, captures DOM events with PII masking, and produces structured observation summaries. Triggers on operations like "start_tracking", "stop_tracking", "get_observations".
---

# Mimic Web Behavior Tracker — Knowledge Skill

## Purpose

AI Agents follow this skill to perform behavior observation operations:
1. Start tracking user interactions on a target website via Chrome DevTools MCP
2. Stop tracking and produce structured observation summaries with flow narrative, key paths, pain points, and AI annotations
3. Retrieve filtered observations from completed or active tracking sessions

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.
CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
BLOCKING: Requires active Chrome DevTools MCP connection (`navigate_page` + `evaluate_script` tools).
CRITICAL: Use `references/tracker-toolbar.mini.js` for injection — the minified version. `references/tracker-toolbar.js` is the readable source for development.
CRITICAL: Password fields are NEVER revealed, even if whitelisted. PII masking defaults to mask-everything.
BLOCKING: IIFE guard `window.__xipeBehaviorTrackerInjected` prevents double injection. If guard is already set, return the existing session ID without error.
CRITICAL: All writes go to `x-ipe-docs/.mimicked/` — NOT `.working/` or persistent memory tiers.

---

## About

This skill wraps a JavaScript IIFE that is injected into target web pages via Chrome DevTools Protocol. The IIFE runs in a minimal toolbar UI and records user interactions as structured events. Events are stored in a circular buffer, masked for PII, and post-processed into observation summaries.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation declares `x-ipe-docs/.mimicked/` as its write target (or null for read-only), enabling the orchestrator to predict side effects.
- **IIFE Guard** — `window.__xipeBehaviorTrackerInjected` flag prevents duplicate injection on the same page.
- **Circular Buffer** — Fixed-capacity (default 10,000) event store in the browser; silently prunes oldest events when full.
- **PII Masking** — Default mask-everything with CSS-selector whitelist for opt-in reveal; password fields are never exposed regardless of whitelist.
- **Post-Processing** — `scripts/post_processor.py` generates flow narrative, key paths, pain points, and per-event AI annotations from raw events.

---

## When to Use

```yaml
triggers:
  - "Start tracking user behavior on a website"
  - "Stop tracking and collect behavior observations"
  - "Retrieve observations from a tracking session"

not_for:
  - "UX analytics dashboards — this produces AI training data, not business metrics"
  - "Automated testing — use testing frameworks instead"
  - "Orchestration decisions — belong to assistant skills"
```

---

## Input Parameters

```yaml
input:
  operation: "start_tracking | stop_tracking | get_observations | start_active_tracking | poll_tick"
  context:
    # For start_tracking:
    target_app: "string"            # URL to track (https:// required)
    session_config:
      pii_whitelist: "string[]"     # CSS selectors to reveal (default: [])
      buffer_capacity: "int"        # Max events before pruning (default: 10000)
      purpose: "string"             # Tracking purpose (≤200 words, required)
    # For start_active_tracking (CR-001): same as start_tracking PLUS:
    active_config:
      polling_interval_s: "int"     # default: 5
      auto_screenshot: "bool"       # default: true
      auto_reinject: "bool"         # default: true
    # For stop_tracking:
    tracking_session_id: "string"   # Session ID from start_tracking
    # For poll_tick (CR-001): invoked by orchestrating agent each tick
    tracking_session_id: "string"
    tick_n: "int"                   # Monotonic counter from agent
    # For get_observations:
    tracking_session_id: "string"   # Session ID to query
    filter:                         # Optional filter criteria
      event_type: "string?"         # e.g., "click", "input", "navigation"
      time_range:                   # Optional time window
        start_ms: "int?"
        end_ms: "int?"
      element_selector: "string?"   # CSS selector to match event targets
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here. Do NOT embed field initialization logic in operation steps.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: start_tracking, stop_tracking, get_observations, start_active_tracking, poll_tick</validation>
  </field>

  <field name="context.target_app" source="Orchestrator provides URL for start_tracking/start_active_tracking">
    <validation>Must have https:// or http:// protocol and valid hostname</validation>
  </field>

  <field name="context.session_config.purpose" source="Orchestrator provides tracking purpose">
    <validation>Non-empty string, max 200 words</validation>
  </field>

  <field name="context.session_config.pii_whitelist" source="Orchestrator provides CSS selectors to reveal">
    <default>[] (mask everything)</default>
    <validation>Array of valid CSS selector strings</validation>
  </field>

  <field name="context.session_config.buffer_capacity" source="Orchestrator specifies max event count">
    <default>10000</default>
    <validation>Positive integer</validation>
  </field>

  <field name="context.tracking_session_id" source="Returned by start_tracking, passed for stop/get">
    <validation>Must reference an existing session directory in x-ipe-docs/.mimicked/</validation>
  </field>

  <field name="context.active_config.polling_interval_s" source="Optional start_active_tracking config">
    <default>5</default>
    <validation>Positive integer; recommended value is 5</validation>
  </field>

  <field name="context.active_config.auto_screenshot" source="Optional start_active_tracking config">
    <default>true</default>
    <validation>Boolean</validation>
  </field>

  <field name="context.active_config.auto_reinject" source="Optional start_active_tracking config">
    <default>true</default>
    <validation>Boolean</validation>
  </field>

  <field name="context.tick_n" source="Agent monotonic counter for poll_tick">
    <validation>Positive integer starting at 1</validation>
  </field>

  <field name="context.filter" source="Optional filter for get_observations">
    <default>null (return all observations)</default>
    <validation>If provided, must contain at least one sub-field</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation specified</name>
    <verification>input.operation matches one of: start_tracking, stop_tracking, get_observations, start_active_tracking, poll_tick</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Chrome DevTools available (start/stop)</name>
    <verification>navigate_page and evaluate_script tools accessible via Chrome DevTools MCP</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation-specific inputs present</name>
    <verification>start_tracking/start_active_tracking: target_app + purpose; stop_tracking/get_observations: tracking_session_id; poll_tick: tracking_session_id + tick_n</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: start_tracking

> **Contract:**
> - **Input:** target_app: string (URL), session_config: { pii_whitelist: string[], buffer_capacity: int, purpose: string }
> - **Output:** tracking_session_id: string
> - **Writes To:** x-ipe-docs/.mimicked/{session_id}/
> - **Constraints:** Chrome DevTools MCP required; IIFE guard prevents double injection; PII mask-everything default; passwords NEVER revealed; purpose required (≤200 words)

**When:** Orchestrator needs to begin observing user behavior on a target website.

```xml
<operation name="start_tracking">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: target_app URL, session_config (pii_whitelist, buffer_capacity, purpose)
      2. APPLY defaults: pii_whitelist → [], buffer_capacity → 10000
      3. GENERATE tracking_session_id: format "mimic-{YYYYMMDD}-{short_uuid}"
      4. DETERMINE session directory: x-ipe-docs/.mimicked/{tracking_session_id}/
    </action>
    <output>Input context understood, session ID generated, target directory identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE target_app has http:// or https:// protocol
      2. VALIDATE purpose is non-empty and ≤200 words
      3. VALIDATE pii_whitelist entries are strings (CSS selectors)
      4. VALIDATE buffer_capacity is a positive integer
      5. VERIFY Chrome DevTools MCP tools are available (navigate_page, evaluate_script)
    </action>
    <constraints>
      - BLOCKING: Invalid URL → return error INVALID_URL
      - BLOCKING: Empty purpose → return error PURPOSE_REQUIRED
      - BLOCKING: Chrome DevTools not available → return error DEVTOOLS_UNAVAILABLE
    </constraints>
    <output>Input validated, Chrome DevTools confirmed available</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. CREATE session directory: x-ipe-docs/.mimicked/{tracking_session_id}/
      2. NAVIGATE to target_app via Chrome DevTools MCP:
         - Call navigate_page with url=target_app
      3. CHECK IIFE guard via evaluate_script:
         - Run: () => !!window.__xipeBehaviorTrackerInjected
         - IF true → SKIP injection, RETURN existing session ID
      4. BUILD injection script:
         a. Define __xipeConfig: { sessionId, purpose, piiWhitelist, bufferCapacity }
         b. READ references/tracker-toolbar.mini.js content
         c. Concatenate: config assignment + IIFE source
      5. INJECT via evaluate_script:
         - Run the concatenated script on the page
      6. VERIFY injection succeeded:
         - evaluate_script: () => !!window.__xipeBehaviorTrackerInjected
      7. START recording via evaluate_script:
         - Run: () => { window.__xipeBehaviorTracker.start(); return true; }
      8. WRITE session metadata to x-ipe-docs/.mimicked/{tracking_session_id}/session.json:
         - { session_id, target_app, purpose, pii_whitelist, buffer_capacity, started_at }
    </action>
    <output>IIFE injected and recording started, session directory created</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY session directory exists at x-ipe-docs/.mimicked/{tracking_session_id}/
      2. VERIFY session.json written with correct metadata
      3. VERIFY IIFE guard is set on page (window.__xipeBehaviorTrackerInjected === true)
      4. IF any verification fails → return error INJECTION_FAILED with details
    </action>
    <output>Injection and session setup verified</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "start_tracking"
         - result: { tracking_session_id }
         - writes_to: "x-ipe-docs/.mimicked/{tracking_session_id}/"
         - errors: []
    </action>
    <output>Start tracking complete, session ID returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: stop_tracking

> **Contract:**
> - **Input:** tracking_session_id: string
> - **Output:** observation_summary: { flow_narrative: string, key_paths: KeyPath[], pain_points: PainPoint[], ai_annotations: Annotation[] }, raw_events: Event[]
> - **Writes To:** x-ipe-docs/.mimicked/{session_id}/
> - **Constraints:** Session must exist; events collected via IIFE; post_processor.py generates summary; SESSION_NOT_FOUND on invalid ID

**When:** Orchestrator needs to end a tracking session and collect structured observations.

```xml
<operation name="stop_tracking">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: tracking_session_id
      2. DETERMINE session directory: x-ipe-docs/.mimicked/{tracking_session_id}/
      3. READ session.json from session directory for metadata (target_app, purpose)
    </action>
    <output>Input context understood, session directory and metadata identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE tracking_session_id is a non-empty string
      2. VALIDATE session directory exists at x-ipe-docs/.mimicked/{tracking_session_id}/
      3. VALIDATE session.json exists and is readable
      4. VERIFY Chrome DevTools MCP tools are available (evaluate_script)
    </action>
    <constraints>
      - BLOCKING: Session directory not found → return error SESSION_NOT_FOUND
      - BLOCKING: Chrome DevTools not available → return error DEVTOOLS_UNAVAILABLE
    </constraints>
    <output>Session validated, ready for event collection</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. COLLECT events via evaluate_script:
         - Run: () => window.__xipeBehaviorTracker.collect()
         - Returns: { events: Event[], eventCount: int, url: string }
      2. STOP the tracker via evaluate_script:
         - Run: () => { window.__xipeBehaviorTracker.stop(); return true; }
      3. BUILD session_meta from session.json:
         - { domain: parsed hostname from target_app, purpose }
      4. RUN post-processor:
         - Execute: python3 scripts/post_processor.py (or call PostProcessor.process(events, session_meta) inline)
         - Input: collected events + session_meta
         - Output: { statistics, analysis: { flow_narrative, key_paths, key_path_summary, pain_points, ai_annotations } }
      5. WRITE raw events to x-ipe-docs/.mimicked/{tracking_session_id}/raw-events.json
      6. WRITE observation summary to x-ipe-docs/.mimicked/{tracking_session_id}/observation-summary.json
      7. UPDATE session.json with stopped_at timestamp and event statistics
    </action>
    <output>Events collected, post-processed, and written to session directory</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY raw-events.json exists and contains event array
      2. VERIFY observation-summary.json exists with flow_narrative, key_paths, pain_points, ai_annotations
      3. VERIFY session.json updated with stopped_at timestamp
      4. IF any verification fails → return error POST_PROCESSING_FAILED with details
    </action>
    <output>Output files validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "stop_tracking"
         - result:
             observation_summary: { flow_narrative, key_paths, pain_points, ai_annotations }
             raw_events: Event[]
             statistics: { totalEvents, byType, pageCount, uniquePages }
         - writes_to: "x-ipe-docs/.mimicked/{tracking_session_id}/"
         - errors: []
    </action>
    <output>Stop tracking complete, observation summary returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: get_observations

> **Contract:**
> - **Input:** tracking_session_id: string, filter?: { event_type?: string, time_range?: { start_ms?: int, end_ms?: int }, element_selector?: string }
> - **Output:** observations: Observation[]
> - **Writes To:** null (READ-ONLY)
> - **Constraints:** Session must exist; no writes; filter applied in-memory; SESSION_NOT_FOUND on invalid ID

**When:** Orchestrator needs to query recorded observations from a session (active or completed).

```xml
<operation name="get_observations">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: tracking_session_id, filter (optional)
      2. DETERMINE session directory: x-ipe-docs/.mimicked/{tracking_session_id}/
      3. IDENTIFY available data files: observation-summary.json, raw-events.json
    </action>
    <output>Input context understood, session directory identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE tracking_session_id is a non-empty string
      2. VALIDATE session directory exists at x-ipe-docs/.mimicked/{tracking_session_id}/
      3. VALIDATE at least one data file (observation-summary.json or raw-events.json) exists
      4. IF filter provided: validate filter fields are correct types
    </action>
    <constraints>
      - BLOCKING: Session directory not found → return error SESSION_NOT_FOUND
      - BLOCKING: No data files found → return error NO_DATA_AVAILABLE
    </constraints>
    <output>Session validated, data files confirmed</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. READ raw-events.json → parse as Event[]
      2. READ observation-summary.json → parse summary
      3. APPLY filter criteria (if provided):
         a. event_type filter: keep events where event.type == filter.event_type
         b. time_range filter: keep events where start_ms ≤ event.timestamp ≤ end_ms
         c. element_selector filter: keep events where event.target.cssSelector matches filter.element_selector
         d. Filters are AND-combined when multiple specified
      4. BUILD observations list from filtered events + relevant summary data
    </action>
    <output>Filtered observations assembled</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY observations is a valid array
      2. VERIFY filter was correctly applied (result count ≤ total events)
      3. CONFIRM no files were written (read-only operation)
    </action>
    <output>Output validated, read-only confirmed</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "get_observations"
         - result: { observations: Observation[], total_count: int, filtered_count: int }
         - writes_to: null
         - errors: []
    </action>
     <output>Get observations complete, filtered results returned to orchestrator</output>
   </phase_5>

</operation>
```

### Operation: start_active_tracking

> **Contract (CR-001):**
> - **Input:** target_app: string (URL), session_config (same as start_tracking), active_config: { polling_interval_s: int (default 5), auto_screenshot: bool (default true), auto_reinject: bool (default true) }
> - **Output:** tracking_session_id: string, polling_started: true, sub_op_contract: { name: "poll_tick", interval_s: int, until: "stop_tracking called for tracking_session_id" }
> - **Writes To:** x-ipe-docs/.mimicked/{session_id}/ (session.json + track-list.json + screenshots/)
> - **Constraints:** Reuses start_tracking's injection; persists active_config to session.json so poll_tick can read it; seeds navigation_history with target_app; returns control to agent — does NOT block or spawn subprocess; agent owns the 5s loop timing.

**When:** Orchestrator needs continuous capture with auto-reinject + auto-screenshot for sessions longer than the in-page buffer can hold, or where URL changes are expected.

```xml
<operation name="start_active_tracking">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: target_app, session_config, active_config
      2. APPLY defaults: polling_interval_s → 5, auto_screenshot → true, auto_reinject → true
      3. DELEGATE to start_tracking phases 1-3 to: validate input, navigate, inject IIFE, generate session_id, start recording
    </action>
    <output>Session created and IIFE injected (start_tracking semantics)</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE active_config.polling_interval_s ≥ 1 (recommended: 5)
      2. VALIDATE active_config.auto_screenshot is bool
      3. VALIDATE active_config.auto_reinject is bool
    </action>
    <constraints>
      - BLOCKING: polling_interval_s &lt; 1 → return error INVALID_POLLING_INTERVAL
    </constraints>
    <output>active_config validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. CALL `scripts/active_tracking.py::init_session` with active_config to:
         - Create/update session.json with active_config + navigation_history seeded with target_app
      2. PREPARE poll_tick contract for the agent (interval_s, helper script paths)
    </action>
    <output>session.json updated with active_config + navigation_history; poll_tick contract ready</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY session.json contains active_config and navigation_history
      2. VERIFY IIFE guard is set on page (window.__xipeBehaviorTrackerInjected === true)
    </action>
    <output>Active session setup verified</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "start_active_tracking"
         - result: {
             tracking_session_id,
             polling_started: true,
             sub_op_contract: {
               name: "poll_tick",
               interval_s: active_config.polling_interval_s,
               until: "stop_tracking called for tracking_session_id"
             }
           }
         - writes_to: "x-ipe-docs/.mimicked/{tracking_session_id}/"
         - errors: []
      2. AGENT INSTRUCTION: Begin polling loop — every interval_s seconds, call poll_tick(tracking_session_id, tick_n) where tick_n is monotonic from 1. Continue until stop_tracking returns successfully OR poll_tick returns error TRACKER_LOST with auto_reinject=false.
    </action>
    <output>Active tracking ready; agent owns the 5s timing loop</output>
  </phase_5>

</operation>
```

### Operation: poll_tick

> **Contract (CR-001):**
> - **Input:** tracking_session_id: string, tick_n: int (monotonic counter from agent, starts at 1)
> - **Output:** event_count: int, new_events: bool, url_changed: bool, screenshot_path: string?, reinjected: bool
> - **Writes To:** x-ipe-docs/.mimicked/{session_id}/ (track-list.json + screenshots/tick-{n}.png + session.json::navigation_history)
> - **Constraints:** Single accumulating track-list.json (NO per-tick JSON files); screenshots only on new events; URL-change reinject if active_config.auto_reinject=true; if IIFE not injected AND auto_reinject=false → error TRACKER_LOST.

**When:** Invoked by orchestrating agent on each polling tick (every active_config.polling_interval_s seconds) after start_active_tracking returned `polling_started: true`.

```xml
<operation name="poll_tick">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ tracking_session_id, tick_n from input
      2. RESOLVE session_dir = x-ipe-docs/.mimicked/{tracking_session_id}/
      3. READ session.json to get active_config and last navigation
      4. IF session.json not found → return error SESSION_NOT_FOUND
    </action>
    <output>Session context loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. evaluate_script(active_tracking.build_poll_script()) → get {events, eventCount, url, error?}
      2. IF error == "not_injected":
         - IF active_config.auto_reinject == false → return error TRACKER_LOST
         - ELSE → mark reinject_needed = true (handled in phase 3)
    </action>
    <output>In-page poll completed; events + url collected (or reinject flagged)</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. URL CHANGE HANDLING:
         IF active_config.auto_reinject AND active_tracking.detect_url_change(session_dir, current_url):
           a. evaluate_script(active_tracking.build_clear_guard_script())
           b. RE-INJECT IIFE (delegate to start_tracking's phase 3 injection logic)
           c. active_tracking.record_navigation(session_dir, current_url)
           d. SET reinjected = true
           e. SET url_changed = true
      2. EVENT MERGE:
         track_list_path = session_dir / "track-list.json"
         active_tracking.merge_events(track_list_path, events, session_metadata)
      3. SCREENSHOT GATING:
         last_event_count = (read from previous tick state OR 0)
         new_events_flag = active_tracking.should_screenshot(eventCount, last_event_count)
         IF active_config.auto_screenshot AND new_events_flag:
           a. screenshot_p = active_tracking.screenshot_path(session_dir, tick_n)
           b. Chrome DevTools MCP take_screenshot(filePath=screenshot_p, fullPage=false)
           c. active_tracking.record_screenshot(track_list_path, "screenshots/tick-{n}.png".format(n=tick_n))
           d. SET screenshot_path_result = str(screenshot_p)
         ELSE:
           SET screenshot_path_result = null
    </action>
    <constraints>
      - CRITICAL: NO per-tick JSON files. track-list.json is the single accumulating store.
      - CRITICAL: Empty ticks (no new events) MUST NOT trigger screenshots.
      - CRITICAL: Reinject MUST clear the guard flag first or injection will be skipped by IIFE.
    </constraints>
    <output>Events merged, navigation recorded if changed, screenshot captured if new events</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY track-list.json updated with new event_count
      2. IF reinjected: VERIFY window.__xipeBehaviorTrackerInjected === true
      3. IF screenshot taken: VERIFY screenshot file exists
    </action>
    <output>Tick side effects verified</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "poll_tick"
         - result: {
             event_count: eventCount,
             new_events: new_events_flag,
             url_changed: url_changed,
             reinjected: reinjected,
             screenshot_path: screenshot_path_result
           }
         - writes_to: "x-ipe-docs/.mimicked/{tracking_session_id}/"
         - errors: []
    </action>
    <output>Tick complete; agent uses result.event_count as last_event_count for next tick</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "start_tracking | stop_tracking | get_observations | start_active_tracking | poll_tick"
  result:
    # start_tracking:
    tracking_session_id: "mimic-{YYYYMMDD}-{short_uuid}"
    # stop_tracking:
    observation_summary:
      flow_narrative: "string"
      key_paths: "KeyPath[]"
      pain_points: "PainPoint[]"
      ai_annotations: "Annotation[]"
    raw_events: "Event[]"
    statistics: "{ totalEvents, byType, pageCount, uniquePages }"
    # get_observations:
    observations: "Observation[]"
    total_count: "int"
    filtered_count: "int"
    # Common:
    writes_to: "x-ipe-docs/.mimicked/{session_id}/ | null"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>operation_output.success == true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output written to declared path</name>
    <verification>start/stop: files exist at x-ipe-docs/.mimicked/{session_id}/; get: no files written</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output matches contract types</name>
    <verification>tracking_session_id is string; observation_summary has flow_narrative/key_paths/pain_points/ai_annotations; observations is array</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>PII masking active</name>
    <verification>No raw PII in events — masked with [MASKED]; password fields show [PASSWORD_FIELD]</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Scripts functional</name>
    <verification>post_processor.py executes without error; tracker-toolbar.mini.js is valid JavaScript</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation not one of start_tracking, stop_tracking, get_observations | Return error listing valid operations |
| `INVALID_URL` | target_app missing protocol or invalid hostname | Provide URL with https:// protocol |
| `PURPOSE_REQUIRED` | Empty or missing purpose string | Provide non-empty tracking purpose (≤200 words) |
| `DEVTOOLS_UNAVAILABLE` | Chrome DevTools MCP not connected | Verify MCP connection, ensure navigate_page and evaluate_script are available |
| `INJECTION_FAILED` | IIFE injection did not succeed | Verify page loaded, retry injection |
| `SESSION_NOT_FOUND` | tracking_session_id doesn't match any session directory | Verify session ID from start_tracking output |
| `NO_DATA_AVAILABLE` | Session directory exists but no data files found | Run stop_tracking first to generate data |
| `POST_PROCESSING_FAILED` | post_processor.py error during summary generation | Auto-retry once; fall back to raw events without summary |
| `INPUT_VALIDATION_FAILED` | Required input missing or wrong type | Return error with specific field and expected type |

---

## References

| File | Purpose |
|------|---------|
| `references/tracker-toolbar.js` | Readable IIFE source — RecordingEngine, PIIMasker, CircularBuffer, EventSerializer, toolbar UI |
| `references/tracker-toolbar.mini.js` | Minified IIFE for injection (<5KB) |
| `scripts/post_processor.py` | PostProcessor class — generates flow narrative, key paths, pain points, AI annotations |
| `scripts/active_tracking.py` | CR-001 helpers — build_poll_script, build_clear_guard_script, init_session, merge_events, detect_url_change, record_navigation, should_screenshot, screenshot_path, record_screenshot |
| `references/examples.md` | Worked examples for each operation |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Scoped tracking | Privacy-sensitive app | Use tight pii_whitelist, short sessions |
| Multi-session compare | UX research | Run separate sessions per user flow, compare observations |
| Purpose-driven | Focused capture | Always provide purpose in session_config |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip purpose | Unfocused data | Always provide purpose in session_config |
| Long sessions | Memory bloat | Keep sessions under 30 min; stop and restart |
| Whitelist passwords | PII leak | Passwords are NEVER whitelisted regardless of config |

---

## Examples

See `references/examples.md` for usage examples.
