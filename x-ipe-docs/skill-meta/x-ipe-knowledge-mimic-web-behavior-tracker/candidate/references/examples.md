# Examples — x-ipe-knowledge-mimic-web-behavior-tracker

Worked examples for each operation of the mimic-web-behavior-tracker knowledge skill.

---

## Example 1: start_tracking — Track Checkout Flow

**Scenario:** The Knowledge Librarian needs to observe user behavior on an e-commerce checkout page.

**Input:**
```yaml
operation: start_tracking
context:
  target_app: "https://shop.example.com/checkout"
  session_config:
    pii_whitelist: ["#product-name", ".price-tag"]
    buffer_capacity: 10000
    purpose: "Observe checkout flow to understand user interactions with cart, payment, and confirmation steps"
```

**Execution Flow:**
1. Session ID generated: `mimic-20260416-a3f8b2`
2. Session directory created: `x-ipe-docs/.mimicked/mimic-20260416-a3f8b2/`
3. Chrome DevTools navigates to `https://shop.example.com/checkout`
4. IIFE guard checked — not set, proceeding with injection
5. `__xipeConfig` built with sessionId, purpose, piiWhitelist, bufferCapacity
6. `tracker-toolbar.mini.js` injected via `evaluate_script`
7. Recording started, toolbar visible at bottom of page
8. `session.json` written with metadata

**Output:**
```yaml
operation_output:
  success: true
  operation: "start_tracking"
  result:
    tracking_session_id: "mimic-20260416-a3f8b2"
  writes_to: "x-ipe-docs/.mimicked/mimic-20260416-a3f8b2/"
  errors: []
```

---

## Example 2: start_tracking — Double Injection Guard

**Scenario:** The orchestrator calls start_tracking on a page where tracking is already active.

**Input:**
```yaml
operation: start_tracking
context:
  target_app: "https://shop.example.com/checkout"
  session_config:
    pii_whitelist: []
    buffer_capacity: 10000
    purpose: "Re-observe checkout flow"
```

**Execution Flow:**
1. Chrome DevTools navigates to URL
2. IIFE guard check: `window.__xipeBehaviorTrackerInjected === true`
3. Guard already set → skip injection
4. Return existing session ID (no error)

**Output:**
```yaml
operation_output:
  success: true
  operation: "start_tracking"
  result:
    tracking_session_id: "mimic-20260416-a3f8b2"
  writes_to: "x-ipe-docs/.mimicked/mimic-20260416-a3f8b2/"
  errors: []
```

---

## Example 3: stop_tracking — Collect Events and Generate Summary

**Scenario:** User has finished interacting with the website. The orchestrator stops tracking and retrieves the observation summary.

**Input:**
```yaml
operation: stop_tracking
context:
  tracking_session_id: "mimic-20260416-a3f8b2"
```

**Execution Flow:**
1. Session directory validated: `x-ipe-docs/.mimicked/mimic-20260416-a3f8b2/`
2. Events collected via `evaluate_script`: 847 events from circular buffer
3. Tracker IIFE stopped
4. Post-processor runs on 847 events with session metadata
5. `raw-events.json` written (847 event records)
6. `observation-summary.json` written with flow narrative, key paths, pain points, AI annotations
7. `session.json` updated with stopped_at timestamp

**Output:**
```yaml
operation_output:
  success: true
  operation: "stop_tracking"
  result:
    observation_summary:
      flow_narrative: "User visited shop.example.com (Observe checkout flow). Navigating through 3 page(s). Performing 42 click(s). 12 input(s). Interacting with: button#add-to-cart, input#email, button#pay-now. Total: 847 events."
      key_paths:
        - path: ["/checkout", "/checkout/payment"]
          frequency: 3
          description: "/checkout → /checkout/payment"
        - path: ["/checkout/payment", "/checkout/confirm"]
          frequency: 2
          description: "/checkout/payment → /checkout/confirm"
      pain_points:
        - type: "hesitation"
          description: "8s pause before event at index 234"
          eventIndex: 234
          duration_ms: 8000
        - type: "repeated_action"
          description: "click on button#pay-now repeated 4 times within 30s"
          eventIndices: [401, 405, 408, 412]
      ai_annotations:
        - eventIndex: 0
          comment: ""
          is_key_path: true
          intent_category: "selection"
          confidence: 0.8
    raw_events: [...]
    statistics:
      totalEvents: 847
      byType: { click: 42, input: 12, scroll: 780, navigation: 3, focus: 10 }
      pageCount: 3
      uniquePages: ["/checkout", "/checkout/payment", "/checkout/confirm"]
  writes_to: "x-ipe-docs/.mimicked/mimic-20260416-a3f8b2/"
  errors: []
```

---

## Example 4: stop_tracking — Session Not Found

**Scenario:** The orchestrator provides an invalid session ID.

**Input:**
```yaml
operation: stop_tracking
context:
  tracking_session_id: "mimic-20260416-nonexistent"
```

**Output:**
```yaml
operation_output:
  success: false
  operation: "stop_tracking"
  result: null
  errors:
    - code: "SESSION_NOT_FOUND"
      message: "No session directory found at x-ipe-docs/.mimicked/mimic-20260416-nonexistent/"
```

---

## Example 5: get_observations — Filtered Query

**Scenario:** The orchestrator needs only click events from a specific time range.

**Input:**
```yaml
operation: get_observations
context:
  tracking_session_id: "mimic-20260416-a3f8b2"
  filter:
    event_type: "click"
    time_range:
      start_ms: 1713260000000
      end_ms: 1713260300000
```

**Execution Flow:**
1. Session directory validated
2. `raw-events.json` loaded (847 events)
3. Filter applied: event_type == "click" AND timestamp in range
4. 15 events match criteria
5. No files written (read-only operation)

**Output:**
```yaml
operation_output:
  success: true
  operation: "get_observations"
  result:
    observations:
      - type: "click"
        timestamp: 1713260001234
        target: { tagName: "BUTTON", cssSelector: "button#add-to-cart" }
        metadata: { pageUrl: "https://shop.example.com/checkout" }
        details: { x: 450, y: 320 }
      - type: "click"
        timestamp: 1713260045678
        target: { tagName: "A", cssSelector: "a.continue-shopping" }
        metadata: { pageUrl: "https://shop.example.com/checkout" }
        details: { x: 200, y: 150 }
    total_count: 847
    filtered_count: 15
  writes_to: null
  errors: []
```

---

## Example 6: get_observations — No Filter (All Observations)

**Scenario:** The orchestrator wants all observations from a session without filtering.

**Input:**
```yaml
operation: get_observations
context:
  tracking_session_id: "mimic-20260416-a3f8b2"
```

**Output:**
```yaml
operation_output:
  success: true
  operation: "get_observations"
  result:
    observations: [...all 847 events...]
    total_count: 847
    filtered_count: 847
  writes_to: null
  errors: []
```

---

## Example 7: PII Masking Behavior

**Scenario:** Demonstrates how PII masking works during tracking.

During `start_tracking`, the IIFE is configured with:
```json
{
  "piiWhitelist": ["#product-name", ".price-tag"],
  "bufferCapacity": 10000
}
```

**Captured event (input on email field — NOT whitelisted):**
```json
{
  "type": "input",
  "target": {
    "tagName": "INPUT",
    "cssSelector": "input#email",
    "value": "[MASKED]",
    "textContent": "[MASKED]"
  }
}
```

**Captured event (input on password field — NEVER revealed even if whitelisted):**
```json
{
  "type": "input",
  "target": {
    "tagName": "INPUT",
    "cssSelector": "input#password",
    "value": "[PASSWORD_FIELD]",
    "textContent": "[PASSWORD_FIELD]"
  }
}
```

**Captured event (click on product name — whitelisted via `#product-name`):**
```json
{
  "type": "click",
  "target": {
    "tagName": "SPAN",
    "cssSelector": "span#product-name",
    "textContent": "Wireless Headphones Pro"
  }
}
```
