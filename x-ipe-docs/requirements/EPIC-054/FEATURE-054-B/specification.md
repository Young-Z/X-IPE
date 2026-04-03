# Feature Specification: Chrome DevTools Injection & Page Lifecycle

> Feature ID: FEATURE-054-B
> Version: v1.0
> Status: Refined
> Last Updated: 04-02-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-02-2026 | Initial specification |

## Linked Mockups

_No feature-specific mockups. Injection is a backend capability with no direct UI._

## Overview

FEATURE-054-B provides the Chrome DevTools injection foundation that all other EPIC-054 features depend on. It opens a target URL via `navigate_page`, injects the `tracker-toolbar.js` script as an IIFE via `evaluate_script`, and manages the full page lifecycle — including navigation detection, automatic re-injection after page transitions, and LocalStorage backup to prevent event loss during re-injection gaps.

This feature consumes the shared Chrome DevTools integration utility extracted from EPIC-030-B via CR. If the shared utility is not yet available, the spec defines an inline fallback interface that will be refactored when the shared utility ships.

A session ID is assigned at recording start and correlates all events across page transitions within a single recording session.

## User Stories

- **US-1:** As the behavior tracker skill, I want to open a target URL in Chrome DevTools, so that the recording script can be injected.
- **US-2:** As the behavior tracker skill, I want the script to be auto-re-injected after page navigation, so that recording continues seamlessly across pages.
- **US-3:** As the behavior tracker skill, I want event data backed up to LocalStorage during re-injection, so that no events are lost during brief gaps.
- **US-4:** As the behavior tracker skill, I want a unique session ID assigned per recording, so that events across page transitions can be correlated.

## Acceptance Criteria

### AC-054B-01: Script Injection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054B-01a | GIVEN a target URL is provided WHEN the skill starts recording THEN `navigate_page` opens the URL in Chrome DevTools browser | Integration |
| AC-054B-01b | GIVEN the target page has loaded WHEN injection executes THEN `evaluate_script` injects `tracker-toolbar.js` as an IIFE into the page context | Integration |
| AC-054B-01c | GIVEN `tracker-toolbar.js` is injected WHEN `window.__xipeBehaviorTrackerInjected` is already `true` THEN the script skips initialization AND does not duplicate event listeners | Unit |
| AC-054B-01d | GIVEN `tracker-toolbar.js` is injected WHEN `window.__xipeBehaviorTrackerInjected` is `undefined` or `false` THEN the script initializes AND sets the flag to `true` | Unit |

### AC-054B-02: Page Lifecycle Management

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054B-02a | GIVEN recording is active WHEN user navigates to a new page (click link, form submit, URL change) THEN DevTools page lifecycle monitoring detects the navigation event | Integration |
| AC-054B-02b | GIVEN page navigation is detected WHEN the new document is ready THEN `tracker-toolbar.js` is automatically re-injected into the new page | Integration |
| AC-054B-02c | GIVEN re-injection occurs after navigation WHEN the new page loads THEN the same session ID is preserved across the page transition | Unit |

### AC-054B-03: LocalStorage Backup

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054B-03a | GIVEN recording is active WHEN events are captured THEN event data is periodically flushed to LocalStorage as backup | Unit |
| AC-054B-03b | GIVEN a page navigation occurs WHEN there is a brief gap before re-injection THEN events captured during the gap are recoverable from LocalStorage | Integration |
| AC-054B-03c | GIVEN the script is re-injected after navigation WHEN LocalStorage backup exists THEN backed-up events are merged into the main event buffer without duplicates | Unit |

### AC-054B-04: Session ID Management

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054B-04a | GIVEN the user starts a new recording WHEN the skill initializes THEN a unique session ID (UUID v4) is generated and assigned | Unit |
| AC-054B-04b | GIVEN a session ID is assigned WHEN events are recorded across multiple pages THEN all events carry the same session ID | Unit |

### AC-054B-05: Shared Utility Consumption

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054B-05a | GIVEN the shared Chrome DevTools utility from EPIC-030-B CR is available WHEN the skill initializes THEN it consumes the shared `navigate_page` and `evaluate_script` wrappers | Integration |
| AC-054B-05b | GIVEN the shared utility is NOT yet available WHEN the skill initializes THEN it uses an inline fallback that directly calls Chrome DevTools MCP tools | Integration |

## Functional Requirements

- **FR-1:** The skill shall open a target URL in Chrome via `navigate_page` tool.
- **FR-2:** The skill shall inject `tracker-toolbar.js` as an IIFE via `evaluate_script`.
- **FR-3:** Double injection shall be prevented by checking `window.__xipeBehaviorTrackerInjected` flag.
- **FR-4:** Page navigation shall be detected via DevTools page lifecycle events.
- **FR-5:** Script shall be automatically re-injected when a new document is ready after navigation.
- **FR-6:** Event data shall be backed up to LocalStorage periodically (configurable interval).
- **FR-7:** After re-injection, backed-up events from LocalStorage shall be merged without duplicates.
- **FR-8:** A UUID v4 session ID shall be generated per recording session and shared across all page transitions.

## Non-Functional Requirements

- **NFR-1:** Script injection shall complete within 500ms of page load.
- **NFR-2:** Re-injection after navigation shall complete within 1s of new document ready.
- **NFR-3:** LocalStorage backup shall not exceed 4MB (leaving 1MB headroom from 5MB limit).
- **NFR-4:** Event merge after re-injection shall complete within 100ms.

## UI/UX Requirements

_No direct UI — this feature is a backend injection capability. The injected script initializes the recording engine (FEATURE-054-C) and toolbox (FEATURE-054-D)._

## Dependencies

| Type | Dependency | Impact |
|------|-----------|--------|
| External | EPIC-030-B CR (shared Chrome DevTools utility) | Primary injection path — inline fallback if unavailable |
| External | Chrome DevTools MCP (`navigate_page`, `evaluate_script`) | Core injection mechanism |
| Internal | FEATURE-054-C (Event Recording Engine) | Injected script bootstraps event listeners |
| Internal | FEATURE-054-D (Tracker Toolbox) | Injected script bootstraps Shadow DOM toolbox |

## Business Rules

- **BR-1:** CSP bypass is by design — `evaluate_script` operates outside Content Security Policy (same pattern as UIUX reference skill EPIC-030-B).
- **BR-2:** Only one browser tab is tracked at a time (v1).
- **BR-3:** The skill must work on any standard Chromium-rendered website.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Target site blocks LocalStorage | Graceful degradation — events still captured in memory buffer; warn that backup is unavailable |
| Page navigation to cross-origin redirect (OAuth) | Document as known limitation — re-injection may fail on intermediate redirect pages |
| Page uses `beforeunload` to prevent navigation | DevTools detects actual navigation only; `beforeunload` dialogs handled by Chrome |
| Very rapid sequential navigations | Queue re-injection; skip intermediate pages if navigation occurs before injection completes |
| Target site modifies `window.__xipeBehaviorTrackerInjected` | Use Symbol or unique property name to minimize collision risk |

## Out of Scope

- Multi-tab tracking (v1 — single tab only)
- Service Worker injection
- iframe content tracking (main frame only for v1)
- WebSocket-based event streaming to host

## Technical Considerations

- Injection uses Chrome DevTools Protocol via MCP tools — not browser extension APIs
- `evaluate_script` executes in the page's main world (has access to page's DOM, LocalStorage, etc.)
- LocalStorage key should be namespaced (e.g., `__xipe_behavior_backup_{sessionId}`) to avoid conflicts
- Session ID should be generated on the host (skill) side and passed to injected script via the IIFE closure
- Re-injection timing depends on DevTools `Page.lifecycleEvent` with `name: "load"` or `"DOMContentLoaded"`

## Open Questions

None — all specification questions resolved via DAO-107.
