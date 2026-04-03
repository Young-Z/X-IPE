---
name: x-ipe-learning-behavior-tracker-for-web
description: Track user behavior on any website for AI agent training. Records DOM events (clicks, inputs, scrolls, navigation, resize, focus, drag), applies PII masking, and produces structured behavior-recording JSON with flow narrative, key paths, pain points, and AI annotations. Triggers on "track behavior", "record user behavior", "learn from website".
---

# Skill: Web Behavior Learning & Tracker

## Purpose

Record and analyze user behavior on any target website for AI agent training data. This skill:
1. Opens target URL in Chrome via DevTools MCP
2. Injects `tracker-toolbar.js` IIFE into the page
3. Manages page lifecycle (navigation, re-injection, LocalStorage backup)
4. Captures DOM events with PII masking
5. On stop: collects events, runs post-processing, outputs behavior-recording JSON

## Input

```yaml
input:
  url: "https://example.com"        # Required — target website URL
  purpose: "Checkout flow"           # Optional — tracking purpose description
  pii_whitelist: []                  # Optional — CSS selectors to reveal (override masking)
  buffer_capacity: 10000             # Optional — max events in circular buffer
```

## Execution

1. **Open Page:** `navigate_page` → target URL
2. **Inject:** `evaluate_script` → `tracker-toolbar.js` IIFE with session config
3. **Monitor:** Listen for page lifecycle events (navigation → re-inject)
4. **User interacts** with the page; events are captured by injected script
5. **Stop:** User signals stop → collect event buffer → run post-processing
6. **Output:** Write `behavior-recording-{sessionId}.json` to project folder

## Output

```yaml
output:
  file: "behavior-recording-{sessionId}.json"
  schema_version: "1.0"
  sections:
    - session: metadata (id, domain, purpose, timestamps)
    - statistics: event counts, page count
    - events: array of captured events
    - analysis: flow_narrative, key_paths, pain_points, ai_annotations
```

## References

| File | Purpose |
|------|---------|
| `scripts/track_behavior.py` | Main skill orchestrator — injection + lifecycle |
| `scripts/post_processor.py` | Post-processing — narrative, key paths, pain points |
| `references/tracker-toolbar.js` | Injected IIFE — recording engine, PII masker, toolbox |
