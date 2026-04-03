# Feature Specification: Injected Tracker Toolbox (Shadow DOM)

> Feature ID: FEATURE-054-D
> Version: v1.0
> Status: Refined
> Last Updated: 04-02-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-02-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Tracker Toolbox | HTML | [x-ipe-docs/requirements/EPIC-054/FEATURE-054-D/mockups/tracker-toolbox-v1.html](x-ipe-docs/requirements/EPIC-054/FEATURE-054-D/mockups/tracker-toolbox-v1.html) | Glass-morphism floating overlay with recording controls, event list, AI annotations, session stats | current | 04-02-2026 |

> **Note:** UI/UX requirements and acceptance criteria below are derived from the mockup marked as "current".

## Overview

The Injected Tracker Toolbox is a floating panel rendered inside the target website via Shadow DOM for complete CSS isolation. It provides the in-page user interface for the behavior recording session — displaying a chronological event list, recording controls (start/stop/pause), key-path vs not-on-key-path event indicators, session statistics, and a PII masking badge.

The toolbox is injected as part of the `tracker-toolbar.js` script (FEATURE-054-B) and reads events from the recording engine buffer (FEATURE-054-C). It must coexist with the EPIC-030-B UIUX toolbar by using a lower z-index in a shared z-index registry.

The toolbox defaults to the bottom-right corner of the viewport and is draggable (repositionable) and collapsible (minimizable) to reduce visual intrusion on the target site.

## User Stories

- **US-1:** As a user recording behavior on a target website, I want a floating toolbox showing captured events, so that I can monitor what's being recorded in real-time.
- **US-2:** As a user, I want recording controls (start/stop/pause) in the toolbox, so that I can manage the recording without leaving the target page.
- **US-3:** As a user, I want to drag and minimize the toolbox, so that it doesn't obstruct the website I'm interacting with.
- **US-4:** As a user, I want key-path events highlighted, so that I can quickly see which interactions are classified as important.

## Acceptance Criteria

### AC-054D-01: Shadow DOM Rendering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-01a | GIVEN the tracker script is injected WHEN the toolbox renders THEN it is contained within a Shadow DOM root for complete CSS isolation from the target site | UI |
| AC-054D-01b | GIVEN the toolbox is rendered in Shadow DOM WHEN the target site has conflicting CSS classes/styles THEN the toolbox appearance is unaffected | UI |
| AC-054D-01c | GIVEN the toolbox is rendered WHEN inspecting the target site's global styles THEN no toolbox styles leak into the target site | UI |

### AC-054D-02: Event List Display

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-02a | GIVEN recording is active WHEN events are captured THEN the toolbox displays a chronological event list with type icons and timestamps | UI |
| AC-054D-02b | GIVEN events in the list WHEN an event is classified as key-path (`is_key_path: true`) THEN it is visually highlighted (emerald accent) | UI |
| AC-054D-02c | GIVEN events in the list WHEN an event is classified as not-on-key-path THEN it is greyed out and collapsed by default | UI |
| AC-054D-02d | GIVEN collapsed not-on-key-path events WHEN user clicks on a collapsed event THEN it expands to show full event details | UI |

### AC-054D-03: Recording Controls

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-03a | GIVEN recording is active WHEN user clicks "Pause" button THEN recording pauses AND the button changes to "Resume" | UI |
| AC-054D-03b | GIVEN recording is paused WHEN user clicks "Resume" button THEN recording resumes AND new events appear in the list | UI |
| AC-054D-03c | GIVEN recording is active or paused WHEN user clicks "Stop" button THEN recording stops AND post-processing triggers (FEATURE-054-F) | Integration |
| AC-054D-03d | GIVEN recording state changes WHEN the controls update THEN button states visually reflect the current recording state (recording/paused/stopped) | UI |

### AC-054D-04: Session Statistics

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-04a | GIVEN recording is active WHEN user views the toolbox header THEN it displays: tracking purpose, page count, event count, and elapsed time | UI |
| AC-054D-04b | GIVEN recording is active WHEN a new event is captured or a page transition occurs THEN statistics update in real-time | UI |

### AC-054D-05: PII Badge

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-05a | GIVEN PII masking is active (default) WHEN the toolbox displays status THEN a PII masking badge shows "Masking: ON" | UI |
| AC-054D-05b | GIVEN CSS selector whitelist has entries WHEN the toolbox displays status THEN the badge shows whitelist count (e.g., "Masking: ON (2 revealed)") | UI |

### AC-054D-06: Drag & Minimize

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-06a | GIVEN the toolbox is rendered WHEN it first appears THEN it is positioned in the bottom-right corner of the viewport | UI |
| AC-054D-06b | GIVEN the toolbox is visible WHEN user drags the toolbox header THEN the toolbox moves to the new position on the page | UI |
| AC-054D-06c | GIVEN the toolbox is visible WHEN user clicks the minimize button THEN the toolbox collapses to a small icon/indicator | UI |
| AC-054D-06d | GIVEN the toolbox is minimized WHEN user clicks the minimized indicator THEN the toolbox expands back to full size at its last position | UI |

### AC-054D-07: UIUX Toolbar Coexistence

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-07a | GIVEN EPIC-030-B UIUX toolbar is also present on the page WHEN both toolbars render THEN the UIUX toolbar has higher z-index than the tracker toolbox | UI |
| AC-054D-07b | GIVEN both toolbars are present WHEN user interacts with either THEN clicks and interactions do not bleed through to the other toolbar | UI |

### AC-054D-08: Mockup Layout Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054D-08a | GIVEN the toolbox is rendered WHEN comparing to tracker-toolbox-v1.html mockup THEN it uses glass-morphism styling (semi-transparent dark background + backdrop blur) | UI |
| AC-054D-08b | GIVEN recording is active WHEN the target page border is visible THEN a red recording border appears at the top of the page with recording status bar per mockup | UI |
| AC-054D-08c | GIVEN the toolbox event list WHEN comparing to mockup THEN events display with type icons, element description, AI annotation badges, and timestamp per mockup layout | UI |

## Functional Requirements

- **FR-1:** Toolbox shall be rendered inside Shadow DOM attached to a host element in the target page.
- **FR-2:** Event list shall display captured events chronologically with type icons and timestamps.
- **FR-3:** Recording controls: Start, Pause/Resume, Stop — with visual state indicators.
- **FR-4:** Key-path events highlighted (emerald); not-on-key-path events greyed out and collapsed.
- **FR-5:** Session stats: tracking purpose, page count, event count, elapsed time — updated real-time.
- **FR-6:** PII masking badge showing status and whitelist count.
- **FR-7:** Toolbox positioned bottom-right by default, draggable via header, collapsible/minimizable.
- **FR-8:** Z-index lower than EPIC-030-B toolbar; shared z-index registry via CSS custom properties.

## Non-Functional Requirements

- **NFR-1:** Toolbox rendering shall not cause visible layout shift on the target page.
- **NFR-2:** Event list updates shall render within 16ms (60fps) for smooth real-time display.
- **NFR-3:** Drag interaction shall be smooth with no jank (requestAnimationFrame-based).
- **NFR-4:** Toolbox total DOM size shall be under 200 nodes to minimize memory impact.

## UI/UX Requirements

> Derived from [tracker-toolbox-v1.html](x-ipe-docs/requirements/EPIC-054/FEATURE-054-D/mockups/tracker-toolbox-v1.html) mockup (current).

- **Styling:** Glass-morphism — `rgba(15,23,42,0.88)` background + `backdrop-filter: blur(24px)`
- **Recording Border:** Red top border (4px) + status bar when recording is active
- **Typography:** DM Sans for labels, DM Mono for technical data (selectors, timestamps)
- **Colors:** Emerald (#10b981) for key-path highlights and active states; red (#ef4444) for recording indicator; grey (#64748b) for not-on-key-path
- **Event Items:** Type icon (left) + element description + AI annotation badge (right) + timestamp
- **AI Badges:** Category badges (e.g., "Navigation", "Data Entry") with confidence indicator
- **Controls:** Rounded pill buttons with hover states; Stop button red, Pause button amber
- **Minimized State:** Small circular icon (e.g., 40px diameter) with event count badge
- **Position:** Bottom-right corner default; remembers last position during session

## Dependencies

| Type | Dependency | Impact |
|------|-----------|--------|
| Internal | FEATURE-054-B (Injection) | Toolbox bootstrapped by injected script |
| Internal | FEATURE-054-C (Recording Engine) | Reads event buffer for display |
| Internal | FEATURE-054-E (PII Protection) | Shows PII masking status badge; hosts whitelist UI |
| Coexists | EPIC-030-B (UIUX Toolbar) | Must not conflict; shared z-index registry |

## Business Rules

- **BR-1:** Toolbox must never interfere with the target site's normal user interactions (clicks, scrolls, typing outside the toolbox).
- **BR-2:** Not-on-key-path events are visible but de-emphasized — user can expand for details.
- **BR-3:** Minimized toolbox still shows event count to indicate recording is active.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Target site uses Shadow DOM itself | Toolbox operates in its own Shadow DOM; no conflict with site's Shadow DOMs |
| Target site has fixed-position elements at bottom-right | Toolbox is draggable; user can reposition to avoid overlap |
| Very long event list (1000+ events) | Virtual scrolling for event list; only render visible items |
| Page with very small viewport (mobile) | Toolbox scales to fit; minimize button prominently accessible |
| User drags toolbox off-screen | Constrain to viewport bounds; snap back if released outside |

## Out of Scope

- Event filtering or search within toolbox (v1)
- Toolbox position persistence across sessions
- Custom toolbox themes or sizing preferences
- Event editing or deletion from toolbox
- Real-time AI annotation display (post-processing badges shown after session stop)

## Technical Considerations

- Shadow DOM host: create a `<div>` at body end, attach shadow root (mode: "closed" to prevent site JS access)
- Z-index registry: CSS custom properties on `:host` — e.g., `--xipe-toolbox-z: 2147483640; --xipe-uiux-toolbar-z: 2147483645`
- Event list: virtual scrolling for performance with large event counts
- Drag: `mousedown` on header → `mousemove` on document → `mouseup` with `requestAnimationFrame`
- Glass-morphism: `backdrop-filter: blur(24px)` — may not work on all browsers; fallback to opaque dark background
- Event capture: toolbox click events must `stopPropagation()` to prevent recording toolbox interactions as user events

## Open Questions

None — all specification questions resolved via DAO-107.
