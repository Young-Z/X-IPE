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

### Operation: Inject

**When:** Starting a new behavior tracking session on a target URL.

```xml
<operation name="inject">
  <action>
    1. Create BehaviorTrackerSkill instance with URL and purpose
    2. Call navigate_page to open target URL in Chrome
    3. Build injection script via InjectionManager with session config:
       - Read tracker-toolbar.mini.js content
       - Prepend __xipeConfig with sessionId, purpose, piiWhitelist, bufferCapacity
    4. Call evaluate_script to inject the IIFE into the page
    5. Mark session as started
  </action>
  <constraints>
    - BLOCKING: Must use tracker-toolbar.mini.js (minified) for injection
    - BLOCKING: Check IIFE guard before injection to prevent duplicates
  </constraints>
  <output>session_id, injection_status</output>
</operation>
```

### Operation: Collect

**When:** Gathering current event buffer without stopping the session.

```xml
<operation name="collect">
  <action>
    1. Call evaluate_script with collection script:
       `() => window.__xipeBehaviorTracker?.getEvents()`
    2. Parse returned JSON array of events
    3. Return event count and raw events
  </action>
  <output>events[], event_count</output>
</operation>
```

### Operation: Stop

**When:** Ending the recording session and collecting final events.

```xml
<operation name="stop">
  <action>
    1. Call evaluate_script with stop script:
       `() => { const t = window.__xipeBehaviorTracker; if(t) { t.stop(); return t.getEvents(); } }`
    2. Parse returned events
    3. Mark session as stopped
  </action>
  <output>events[], session_metadata</output>
</operation>
```

### Operation: Post-Process & Output

**When:** After stop, generating the final behavior-recording JSON.

```xml
<operation name="post_process">
  <action>
    1. Instantiate PostProcessor
    2. Run process(events, session_meta) to generate:
       - statistics (event counts, page count, duration)
       - flow_narrative (natural language session summary)
       - key_paths (ordered list of significant interactions)
       - key_path_summary (condensed key-path view)
       - pain_points (hesitations, rage clicks, back-navigation)
       - ai_annotations (per-event: comment, is_key_path, intent_category, confidence)
    3. Extract unique pages[] from events
    4. Write behavior-recording-{sessionId}.json to project folder
  </action>
  <constraints>
    - BLOCKING: Auto-retry once on post-processing failure; fallback to raw events with 'failed' status
  </constraints>
  <output>file_path, statistics, analysis</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    session_id: "{uuid}"
    file_path: "behavior-recording-{sessionId}.json"
    statistics:
      totalEvents: 0
      pageCount: 0
    analysis:
      flow_narrative: ""
      key_paths: []
      key_path_summary: []
      pain_points: []
      ai_annotations: []
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
    <name>IIFE Injected (inject op)</name>
    <verification>window.__xipeBehaviorTrackerInjected is true on target page</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Events Captured (collect/stop op)</name>
    <verification>events[] returned with correct schema (type, timestamp, target, metadata)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output File Written (post_process op)</name>
    <verification>behavior-recording-{sessionId}.json exists with schema_version, session, pages, statistics, events, analysis</verification>
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
| `COLLECTION_FAILED` | IIFE not injected or page navigated away | Re-inject tracker before collecting |
| `POST_PROCESSING_FAILED` | PostProcessor error | Auto-retried once; falls back to raw events |
| `DOUBLE_INJECTION` | IIFE guard flag already set | Clear flag or skip injection |

---

## References

| File | Purpose |
|------|---------|
| `references/tracker-toolbar.js` | Readable source — IIFE with RecordingEngine, PIIMasker, TrackerToolbox, CircularBuffer, EventSerializer, BackupManager |
| `references/tracker-toolbar.mini.js` | Minified version for injection (use this in production) |
| `scripts/track_behavior.py` | BehaviorTrackerSkill (session orchestrator) + InjectionManager (script builder) |
| `scripts/post_processor.py` | PostProcessor — flow narrative, key paths, pain points, AI annotations |
| `scripts/__init__.py` | Package init |

---

## Examples

**Example 1: Track checkout flow**
```
User: "Track behavior on https://shop.example.com"
Agent:
  1. inject → navigates to URL, injects tracker-toolbar.mini.js
  2. User interacts with checkout flow
  3. stop → collects 847 events
  4. post_process → writes behavior-recording-abc123.json
     - 12 key paths identified
     - 3 pain points (hesitation on payment form, back-navigation)
     - Per-event AI annotations with intent categories
```

**Example 2: Record onboarding flow**
```
User: "Learn from website https://app.example.com/onboard"
Agent:
  1. inject with purpose "Onboarding flow for AI agent training"
  2. User completes 5-step wizard
  3. stop + post_process → 234 events, 5 pages
  4. Analysis: linear flow, no pain points, clear key path through wizard steps
```
