# Feature Specification: Workplace Learn Module GUI

> Feature ID: FEATURE-054-A
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
| Learn Panel | HTML | [x-ipe-docs/requirements/EPIC-054/FEATURE-054-A/mockups/learn-panel-v1.html](x-ipe-docs/requirements/EPIC-054/FEATURE-054-A/mockups/learn-panel-v1.html) | Workplace Learn panel with URL input, session list, event timeline, draggable divider | current | 04-02-2026 |

> **Note:** UI/UX requirements and acceptance criteria below are derived from the mockup marked as "current".

## Overview

The Workplace Learn Module GUI provides the user-facing entry point for EPIC-054's web behavior tracking capability. It adds a "Learn" menu item under the Workplace ideation area, presenting a panel where users enter a target URL, describe their tracking purpose in freeform text, and initiate recording sessions via a "Track Behavior" call-to-action.

The panel also displays a session list showing all recording sessions for the current project — with status indicators (recording, paused, completed), domain, elapsed time, event count, and page count. Active sessions are highlighted with a live pulsing indicator. Completed sessions link to their behavior-recording.json output.

This feature is the first in the MVP implementation order (zero dependencies), enabling early user validation of the Learn module's interaction model before backend injection and recording features are integrated.

## User Stories

- **US-1:** As a Workplace user, I want to see a "Learn" menu item in the ideation area, so that I can access the behavior tracking module.
- **US-2:** As a Workplace user, I want to enter a target URL and tracking purpose, so that I can initiate a behavior recording session with context.
- **US-3:** As a Workplace user, I want to view a list of my recording sessions with status and metrics, so that I can track progress and access completed recordings.
- **US-4:** As a Workplace user, I want the active session to be visually highlighted, so that I know recording is in progress.

## Acceptance Criteria

### AC-054A-01: Learn Menu Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054A-01a | GIVEN Workplace is open WHEN user navigates to the ideation area THEN a "Learn" menu item is visible in the navigation sidebar | UI |
| AC-054A-01b | GIVEN user is in Workplace WHEN user clicks the "Learn" menu item THEN the Learn panel opens displaying URL input, tracking purpose field, and session list sections | UI |

### AC-054A-02: Target URL Input

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054A-02a | GIVEN Learn panel is open WHEN user enters a valid URL (protocol + domain, e.g., "https://example.com") THEN URL field shows accepted state with no error | UI |
| AC-054A-02b | GIVEN Learn panel is open WHEN user enters text that is not a valid URL THEN inline validation error is displayed below the field (red border + "Please enter a valid URL") | UI |
| AC-054A-02c | GIVEN Learn panel is open AND URL field is empty or invalid WHEN user views "Track Behavior" button THEN the button is disabled until URL passes client-side format validation | UI |
| AC-054A-02d | GIVEN URL field is empty WHEN user focuses and then blurs the field without entering text THEN inline error displays "URL is required" | UI |

### AC-054A-03: Tracking Purpose Field

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054A-03a | GIVEN Learn panel is open WHEN user views the tracking purpose field THEN placeholder text displays examples (e.g., "e.g., Checkout flow for AI agent training") | UI |
| AC-054A-03b | GIVEN user types into tracking purpose field WHEN any freeform text is entered THEN text is accepted without validation constraints | UI |

### AC-054A-04: Track Behavior Action

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054A-04a | GIVEN valid URL is entered AND tracking purpose is provided WHEN user clicks "Track Behavior" THEN a terminal session opens AND the `x-ipe-learning-behavior-tracker-for-web` skill is invoked with URL and purpose parameters | Integration |
| AC-054A-04b | GIVEN a recording session is already active WHEN user clicks "Track Behavior" THEN an error message indicates the active session must be stopped first AND no new session starts | UI |
| AC-054A-04c | GIVEN valid URL is entered AND tracking purpose is empty WHEN user clicks "Track Behavior" THEN session starts with purpose defaulting to empty string (purpose is optional) | Integration |

### AC-054A-05: Session List Display

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054A-05a | GIVEN recording sessions exist for the current project WHEN Learn panel loads THEN session list displays all sessions with status indicators (recording / paused / completed) | UI |
| AC-054A-05b | GIVEN sessions exist in the list WHEN user views a session card THEN the card shows domain, elapsed time, event count, and page count | UI |
| AC-054A-05c | GIVEN a session is actively recording WHEN Learn panel is visible THEN the active session card displays a pulsing emerald dot indicator | UI |
| AC-054A-05d | GIVEN a completed session exists WHEN user clicks on the session card THEN the behavior-recording.json file opens in the content viewer | UI |
| AC-054A-05e | GIVEN no recording sessions exist for the project WHEN Learn panel loads THEN an empty state message is displayed with guidance to start a first session | UI |

### AC-054A-06: Mockup Layout Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054A-06a | GIVEN Learn panel is rendered WHEN comparing to learn-panel-v1.html mockup THEN the panel uses a multi-column grid layout with icon sidebar, Learn panel content, divider, and event timeline sections | UI |
| AC-054A-06b | GIVEN Learn panel is rendered WHEN user drags the panel divider THEN the Learn panel width adjusts between 280px minimum and 600px maximum with 480px as default | UI |
| AC-054A-06c | GIVEN Learn panel is rendered WHEN inspecting typography THEN DM Sans is used for UI text and DM Mono for code/data elements per design system | UI |

## Functional Requirements

- **FR-1:** The Learn module GUI shall render as a panel in the Workplace ideation area, accessible via a "Learn" menu item.
- **FR-2:** The target URL input shall accept HTTP and HTTPS URLs with client-side format validation (protocol + domain minimum).
- **FR-3:** The tracking purpose field shall accept freeform text with no length or format constraints. Purpose is optional.
- **FR-4:** The "Track Behavior" button shall invoke the `x-ipe-learning-behavior-tracker-for-web` skill via terminal session, passing URL and purpose parameters.
- **FR-5:** The session list shall load from the project folder's behavior-recording.json files, displaying all sessions for the current project.
- **FR-6:** Session status shall be derived from recording file contents: "recording" if no `stopped_at` field, "completed" if `stopped_at` exists, "paused" if `paused_at` exists.
- **FR-7:** Only one recording session may be active at a time. The GUI shall prevent starting a new session while one is active.

## Non-Functional Requirements

- **NFR-1:** Session list load time shall be under 200ms for up to 50 sessions.
- **NFR-2:** Panel shall be responsive to width changes via the draggable divider (280px–600px range).
- **NFR-3:** All interactive elements shall be keyboard navigable and screen reader compatible (WCAG 2.1 AA).
- **NFR-4:** Learn panel shall render without layout shift or flash of unstyled content.

## UI/UX Requirements

> Derived from [learn-panel-v1.html](x-ipe-docs/requirements/EPIC-054/FEATURE-054-A/mockups/learn-panel-v1.html) mockup (current).

- **Layout:** Multi-column grid — icon sidebar (56px) + Learn panel (480px default) + draggable divider (6px) + event timeline (remaining space)
- **Typography:** DM Sans for UI text, DM Mono for code/data elements
- **Colors:** Primary #0f172a (dark navy), Accent #10b981 (emerald), Surface #1e293b (slate)
- **Session Cards:** Rounded cards with status badge (emerald for recording, gray for completed), domain text, metric row (time, events, pages, key-paths)
- **Active Indicator:** Pulsing emerald dot animation on active session card
- **Draggable Divider:** 6px wide, col-resize cursor, emerald highlight on hover, grip dots (⋮) visual indicator
- **Empty State:** Centered message with guidance text when no sessions exist
- **URL Input:** Full-width text field with protocol prefix hint
- **CTA Button:** "Track Behavior" button with emerald accent, disabled state when validation fails

## Dependencies

| Type | Dependency | Impact |
|------|-----------|--------|
| Internal | `x-ipe-learning-behavior-tracker-for-web` skill (FEATURE-054-B+) | GUI invokes skill via terminal — skill must accept URL and purpose params |
| Internal | Workplace UI framework (existing patterns) | Learn menu item follows existing menu extension patterns |
| Internal | Content viewer (EPIC-002) | Completed session click opens behavior-recording.json in viewer |

## Business Rules

- **BR-1:** Only one recording session may be active at any time. User must stop the current session before starting a new one.
- **BR-2:** Tracking purpose is optional — sessions can start with empty purpose.
- **BR-3:** URL validation is client-side format only — no reachability check (KISS).
- **BR-4:** Session list shows all sessions for the current project, ordered by most recent first.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty session list (first use) | Display empty state with guidance message |
| Very long URL (>2000 chars) | Accept but truncate display with ellipsis; full URL passed to skill |
| Very long tracking purpose text | Accept without limit; scroll if exceeds visible area |
| Workspace restart during active session | Session appears as "recording" if process still running; "completed" if stopped |
| Project has 100+ sessions | All sessions displayed; consider virtual scrolling for performance |
| behavior-recording.json is malformed | Session card shows "Error" status with tooltip |

## Out of Scope

- Session editing or deletion (v1)
- Multi-tab session display
- Real-time event stream in Learn panel (handled by FEATURE-054-D injected toolbox)
- Export/import sessions across projects
- Session search or filtering
- Session tagging or categorization

## Technical Considerations

- Sessions stored as `behavior-recording.json` files in the project folder
- Session metadata (domain, event count, page count, elapsed time) derived from file contents
- Session status determined by presence of `stopped_at` / `paused_at` fields in recording file
- Active session detection via process tracking or heartbeat mechanism
- Learn menu item added via existing Workplace menu extension patterns (same as EPIC-022-A Browser Simulator)

## Open Questions

None — all specification questions resolved via DAO-107.
