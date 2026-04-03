# Feature Specification: behavior-recording.json Output & Post-Processing

> Feature ID: FEATURE-054-F
> Version: v1.0
> Status: Refined
> Last Updated: 04-02-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-02-2026 | Initial specification |

## Linked Mockups

_No feature-specific mockups. Output is a data file; post-processing is automated._

## Overview

FEATURE-054-F is the output and post-processing stage of the recording pipeline. When a recording session is stopped, post-processing automatically triggers to produce a structured `behavior-recording.json` file. This file follows a defined schema (v1.0) containing session metadata, pages visited, all captured events with AI annotations, a flow narrative summarizing the user journey, a key-path summary of ordered goal-oriented steps, and detected pain points.

The schema is designed with additive upgrade support — future versions can add fields (e.g., real-time annotations) without breaking existing consumers. The output file is saved to the project folder alongside other artifacts and is consumable by downstream skills (requirement gathering, code implementation).

## User Stories

- **US-1:** As a Workplace user, I want a structured recording file produced automatically when I stop recording, so that I don't need a manual export step.
- **US-2:** As a downstream AI skill, I want the recording file to include annotated events with key-path classification, so that I can understand user intent.
- **US-3:** As a Workplace user, I want pain points automatically detected, so that I can see where the user experience was frustrating.

## Acceptance Criteria

### AC-054F-01: Output Schema

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054F-01a | GIVEN a recording session is stopped WHEN the output file is generated THEN it follows the schema: `session` (metadata), `pages[]`, `events[]` (with annotations), `flow_narrative`, `key_path_summary`, `pain_points` | Unit |
| AC-054F-01b | GIVEN the output file is generated WHEN inspecting the schema version field THEN it is set to `"1.0"` | Unit |
| AC-054F-01c | GIVEN a v1.0 output file WHEN a future v1.1 consumer reads it THEN it processes successfully (additive fields are ignored by older consumers) | Unit |

### AC-054F-02: Automatic Trigger

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054F-02a | GIVEN a recording session is active WHEN user clicks "Stop" in the toolbox THEN post-processing starts automatically without requiring a separate action | Integration |
| AC-054F-02b | GIVEN post-processing is running WHEN processing completes successfully THEN the output file is saved to the project folder | Integration |
| AC-054F-02c | GIVEN post-processing fails WHEN the session list displays the session THEN a retry option is available | UI |

### AC-054F-03: Flow Narrative

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054F-03a | GIVEN a completed recording WHEN post-processing generates the flow narrative THEN it produces a natural language summary describing the user's journey across pages | Unit |
| AC-054F-03b | GIVEN the flow narrative WHEN reading it THEN it references page transitions, key actions, and overall goal in human-readable prose | Unit |

### AC-054F-04: Key-Path Summary

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054F-04a | GIVEN a completed recording WHEN post-processing generates the key-path summary THEN it produces an ordered list of steps the user took toward their goal | Unit |
| AC-054F-04b | GIVEN events with `is_key_path: true` annotation WHEN key-path summary is generated THEN only key-path events are included in the ordered list | Unit |

### AC-054F-05: Pain Points Detection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054F-05a | GIVEN a completed recording with repeated actions (same element clicked >3 times) WHEN pain points are analyzed THEN a "repeated action" pain point is detected | Unit |
| AC-054F-05b | GIVEN a completed recording with back-and-forth navigation (A→B→A pattern) WHEN pain points are analyzed THEN a "navigation confusion" pain point is detected | Unit |
| AC-054F-05c | GIVEN a completed recording with hesitation (>5s gap between interactions) WHEN pain points are analyzed THEN a "hesitation" pain point is detected | Unit |

### AC-054F-06: AI Annotations

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054F-06a | GIVEN a completed recording WHEN post-processing annotates events THEN each event includes: `comment`, `is_key_path`, `intent_category`, `confidence` fields | Unit |
| AC-054F-06b | GIVEN AI annotation is performed WHEN annotations are generated THEN `intent_category` is one of: "navigation", "data_entry", "selection", "exploration", "confirmation", "error_recovery" | Unit |

### AC-054F-07: File Output

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054F-07a | GIVEN post-processing completes WHEN the file is saved THEN it is written to the project folder as `behavior-recording-{sessionId}.json` | Unit |
| AC-054F-07b | GIVEN the output file WHEN consumed by requirement gathering or code implementation skills THEN it is parseable as valid JSON with the expected schema | Unit |

## Functional Requirements

- **FR-1:** Post-processing shall trigger automatically when a recording session is stopped.
- **FR-2:** Output schema shall include: `session`, `pages[]`, `events[]`, `flow_narrative`, `key_path_summary`, `pain_points`.
- **FR-3:** Schema version field shall be `"1.0"` with documented additive upgrade path.
- **FR-4:** Flow narrative shall be generated as natural language summary of the user journey.
- **FR-5:** Key-path summary shall be an ordered list of key-path events.
- **FR-6:** Pain points shall detect: repeated actions (>3 clicks same element), back-and-forth navigation, hesitation (>5s gaps).
- **FR-7:** AI annotations shall include: `comment`, `is_key_path`, `intent_category`, `confidence`.
- **FR-8:** Output file shall be saved to the project folder as `behavior-recording-{sessionId}.json`.

## Non-Functional Requirements

- **NFR-1:** Post-processing shall complete within 30s for a 10,000-event session.
- **NFR-2:** Output JSON file shall be pretty-printed for human readability.
- **NFR-3:** Schema shall support additive fields without breaking existing consumers.

## UI/UX Requirements

_No direct UI. Post-processing status indicated in session card (FEATURE-054-A). Retry on failure available in session list._

## Dependencies

| Type | Dependency | Impact |
|------|-----------|--------|
| Internal | FEATURE-054-C (Recording Engine) | Reads event buffer for processing |
| Internal | FEATURE-054-E (PII Protection) | Events are pre-masked; whitelist config included in output |
| Consumed by | FEATURE-054-A (GUI) | Session card shows processing status |
| Consumed by | Downstream skills (requirement gathering, code implementation) | Output file is the primary deliverable |

## Business Rules

- **BR-1:** Post-processing is automatic on session stop — no manual trigger needed.
- **BR-2:** If post-processing fails, the raw event data is preserved and retry is available.
- **BR-3:** Intent categories are a fixed enum for v1.0 — extensible in future versions.
- **BR-4:** Pain point detection uses heuristic thresholds (configurable in future versions).

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Session with 0 events | Output file created with empty events array; flow narrative says "No interactions recorded" |
| Session with only scroll events | Valid output; key-path summary may be empty; flow narrative describes scrolling behavior |
| Very long session (10,000 events at buffer limit) | Process all events in buffer; note that oldest events may have been pruned |
| Post-processing interrupted (e.g., network failure during AI annotation) | Save partial output with annotation errors noted; retry available |
| Multiple sessions for same URL | Each produces separate file with unique sessionId |

## Out of Scope

- Real-time AI annotation during recording (post-processing only for MVP)
- Visual session replay generation
- Output format other than JSON (no CSV, no video)
- Streaming output (complete file written at end)
- Compression of output file

## Technical Considerations

- AI annotations generated via LLM post-processing pass over the event sequence
- Pain point detection is rule-based heuristic (not ML) for v1.0
- Flow narrative generated by summarizing event sequence with page transitions as chapter boundaries
- Schema should define all top-level fields as required; annotation sub-fields as optional (for additive upgrade)
- File naming: `behavior-recording-{sessionId}.json` where sessionId is the UUID v4 from FEATURE-054-B
- PII whitelist config stored in `session.config.pii_whitelist` field

## Open Questions

None — all specification questions resolved via DAO-107.
