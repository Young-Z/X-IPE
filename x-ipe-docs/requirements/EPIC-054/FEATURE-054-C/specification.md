# Feature Specification: Event Recording Engine

> Feature ID: FEATURE-054-C
> Version: v1.0
> Status: Refined
> Last Updated: 04-02-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-02-2026 | Initial specification |

## Linked Mockups

_No feature-specific mockups. Recording engine is a backend capture layer with no direct UI._

## Overview

The Event Recording Engine is the core capture layer for EPIC-054. Running inside the injected `tracker-toolbar.js` script (bootstrapped by FEATURE-054-B), it attaches event listeners to the target page's document and captures 7 event types: click, double-click, right-click, drag, typing, scroll, and navigation.

Each captured event includes full element metadata (CSS selector, tag, text content, a11y role/name, classes, bounding box), page coordinates, and dual timestamps (absolute ISO 8601 + relative ms since session start). Events are stored in a circular buffer with a configurable capacity (default 10,000 events) to handle long sessions gracefully.

The engine uses capture-phase listeners on the document for maximum reliability across DOM changes, and applies performance throttling to high-frequency events (scroll: 200ms, drag: 50ms).

## User Stories

- **US-1:** As the behavior tracker, I want to capture all 7 user interaction types with rich metadata, so that downstream AI can understand what the user did and why.
- **US-2:** As the behavior tracker, I want events stored in a bounded buffer, so that long sessions don't exhaust memory.
- **US-3:** As the behavior tracker, I want each event timestamped with both absolute and relative time, so that events can be analyzed in context of the session timeline.

## Acceptance Criteria

### AC-054C-01: Click Events

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-01a | GIVEN recording is active WHEN user clicks an element THEN a click event is captured with target CSS selector, element text, a11y role/name, bounding box, and page coordinates | Unit |
| AC-054C-01b | GIVEN recording is active WHEN user double-clicks an element THEN a double-click event is captured with `is_double_click: true` flag and full target metadata | Unit |
| AC-054C-01c | GIVEN recording is active WHEN user right-clicks an element THEN a contextmenu event is captured with target metadata and coordinates | Unit |

### AC-054C-02: Drag Events

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-02a | GIVEN recording is active WHEN user drags an element THEN a drag event is captured with start position, end position, delta, duration, and target element selector | Unit |
| AC-054C-02b | GIVEN recording is active WHEN a drag event is captured THEN only start and end positions are recorded (no intermediate positions for MVP) | Unit |

### AC-054C-03: Typing Events

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-03a | GIVEN recording is active WHEN user types into an input field THEN a typing event is captured with field CSS selector, masked value (default PII), and field type attribute | Unit |
| AC-054C-03b | GIVEN recording is active WHEN user types into a textarea THEN a typing event is captured with the same metadata as input fields | Unit |

### AC-054C-04: Scroll Events

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-04a | GIVEN recording is active WHEN user scrolls the page THEN scroll events are captured with scrollX, scrollY, and viewport dimensions | Unit |
| AC-054C-04b | GIVEN recording is active WHEN user scrolls rapidly THEN scroll events are throttled to one capture per 200ms maximum | Unit |

### AC-054C-05: Navigation Events

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-05a | GIVEN recording is active WHEN user navigates to a new page THEN a navigation event is captured with source URL, destination URL, and trigger element selector | Unit |

### AC-054C-06: Event Metadata & Timestamps

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-06a | GIVEN any event is captured WHEN the event is recorded THEN it includes an absolute timestamp (ISO 8601) AND a relative timestamp (ms since session start) | Unit |
| AC-054C-06b | GIVEN any event targeting a DOM element WHEN the event is recorded THEN it includes: CSS selector, tag name, element text (truncated to 200 chars), a11y role, a11y name, class list, and bounding box | Unit |

### AC-054C-07: Event Buffer Management

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-07a | GIVEN recording is active WHEN the event buffer reaches the capacity limit (default 10,000 events) THEN the oldest events are pruned silently to make room for new events | Unit |
| AC-054C-07b | GIVEN the buffer capacity is configurable WHEN a custom capacity is set via session settings THEN the buffer uses the custom capacity instead of default | Unit |

### AC-054C-08: Listener Reliability

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054C-08a | GIVEN recording is active WHEN event listeners are attached THEN they use the capture phase on document for maximum reliability across DOM changes | Unit |
| AC-054C-08b | GIVEN recording is active WHEN a target site modifies its DOM dynamically THEN event listeners continue to capture interactions on new elements | Integration |

## Functional Requirements

- **FR-1:** The engine shall capture 7 event types: click, double-click, right-click, drag, typing, scroll, navigation.
- **FR-2:** Each event shall include dual timestamps: absolute ISO 8601 and relative ms since session start.
- **FR-3:** Element metadata shall include: CSS selector, tag, text (≤200 chars), a11y role/name, classes, bounding box.
- **FR-4:** Drag events shall capture start/end positions only (no intermediate for MVP).
- **FR-5:** Scroll events shall be throttled at 200ms intervals.
- **FR-6:** Events shall be stored in a circular buffer with configurable capacity (default 10,000).
- **FR-7:** Buffer overflow shall silently prune oldest events.
- **FR-8:** All event listeners shall use capture phase on `document`.

## Non-Functional Requirements

- **NFR-1:** Event capture latency shall be under 5ms per event (not perceptible to user).
- **NFR-2:** Scroll throttling shall limit to maximum 5 events/second.
- **NFR-3:** Drag mousemove throttling at 50ms intervals during active drag.
- **NFR-4:** Memory usage for 10,000-event buffer shall be under 10MB.

## UI/UX Requirements

_No direct UI. Events are consumed by FEATURE-054-D (Toolbox) for display and FEATURE-054-F (Output) for export._

## Dependencies

| Type | Dependency | Impact |
|------|-----------|--------|
| Internal | FEATURE-054-B (Injection) | Engine runs inside injected script context |
| Internal | FEATURE-054-E (PII) | Typing events consume PII masking before capture |
| Consumed by | FEATURE-054-D (Toolbox) | Toolbox reads event buffer for display |
| Consumed by | FEATURE-054-F (Output) | Output reads event buffer for export |

## Business Rules

- **BR-1:** All events must be capturable without requiring target site cooperation (no data attributes or APIs needed).
- **BR-2:** Event capture must not interfere with the target site's normal functionality.
- **BR-3:** Typing values are masked by default (delegated to FEATURE-054-E PII layer).

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Element has no text content | Capture empty string for text; other metadata (selector, a11y) still captured |
| Element has no a11y role/name | Capture `null` for role/name fields |
| Shadow DOM elements on target site | Capture the shadow host's metadata; deep shadow tree traversal deferred |
| iframe interactions | Main frame only for v1; document as known limitation |
| Very rapid clicks (>10/sec) | Capture all — no click throttling |
| Contenteditable divs | Treat as typing target; capture selector and masked content |

## Out of Scope

- Intermediate drag positions (MVP: start/end only)
- iframe content tracking
- Touch events (desktop web only for v1)
- Hover/focus events (low AI training value)
- Network request capture
- Console/error capture

## Technical Considerations

- CSS selector generation should produce stable, unique selectors (prefer ID > data-testid > nth-child path)
- A11y role/name extraction via `element.getAttribute('role')` and `element.getAttribute('aria-label')` or computed accessible name
- Bounding box via `getBoundingClientRect()` — relative to viewport
- Typing events should debounce per field (capture final value after 300ms idle, not per-keystroke)
- Navigation detection complements FEATURE-054-B page lifecycle — engine captures the event, B handles re-injection

## Open Questions

None — all specification questions resolved via DAO-107.
