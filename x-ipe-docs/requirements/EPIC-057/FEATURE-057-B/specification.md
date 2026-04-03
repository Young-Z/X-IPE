# Feature Specification: Feature Board Web Page

> Feature ID: FEATURE-057-B
> Version: v1.0
> Status: Refined
> Last Updated: 04-03-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-03-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Feature Board V1 | HTML | [x-ipe-docs/requirements/EPIC-057/FEATURE-057-B/mockups/feature-board-v1.html](x-ipe-docs/requirements/EPIC-057/FEATURE-057-B/mockups/feature-board-v1.html) | Feature board with epic accordion grouping, progress bars, status badges | current | 04-03-2026 |

## Overview

FEATURE-057-B delivers a view-only web page for browsing features tracked by the X-IPE feature board system. The page consumes `/api/features/list`, `/api/features/get/<id>`, and `/api/features/epic-summary` endpoints (FEATURE-056-B). Features are grouped by Epic in collapsible accordion sections with per-epic progress bars showing status distribution.

The page extends `base.html`, uses DM Sans/DM Mono fonts with the Slate/Emerald palette, and follows the same architectural pattern as FEATURE-057-A (Task Board Web Page).

## User Stories

- **US-057-B-01:** As a developer, I want to view all features grouped by Epic so that I can understand the project's feature landscape.
- **US-057-B-02:** As a developer, I want to see per-epic progress bars so that I can gauge completion at a glance.
- **US-057-B-03:** As a developer, I want to filter features by status so that I can focus on specific phases.
- **US-057-B-04:** As a developer, I want to search by feature ID, title, or Epic ID so that I can quickly locate a feature.
- **US-057-B-05:** As a developer, I want to expand a feature row to see details so that I can inspect specs and dependencies.

## Acceptance Criteria

### AC-057-B-01: Page Routing & Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-01a | GIVEN the Flask app is running WHEN a user navigates to `/feature-board` THEN the feature board HTML page is returned with HTTP 200 | API |
| AC-057-B-01b | GIVEN the page is loaded WHEN inspected THEN it extends `base.html` and inherits the app menu bar | UI |
| AC-057-B-01c | GIVEN any page in the app WHEN the user looks at navigation THEN a "Features" link navigates to `/feature-board` | UI |

### AC-057-B-02: Epic Accordion Grouping

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-02a | GIVEN the page loads WHEN epic-summary data is fetched THEN each epic is displayed as a collapsible accordion section with epic ID, name, and feature count | UI |
| AC-057-B-02b | GIVEN the page loads WHEN the initial render completes THEN all epic sections are collapsed by default | UI |
| AC-057-B-02c | GIVEN a collapsed epic section WHEN the user clicks the epic header THEN the section expands showing features for that epic | UI |
| AC-057-B-02d | GIVEN an expanded epic section WHEN the user clicks the header again THEN the section collapses | UI |
| AC-057-B-02e | GIVEN an epic header WHEN rendered THEN it shows a chevron icon that rotates 90° when expanded per mockup | UI |

### AC-057-B-03: Per-Epic Progress Bars

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-03a | GIVEN an epic header is rendered WHEN the epic has features in multiple statuses THEN a stacked progress bar shows the status distribution | UI |
| AC-057-B-03b | GIVEN an epic with 6 features where 3 are Completed, 2 Tested, 1 Planned WHEN the progress bar renders THEN segments are proportionally sized and colored per status | UI |

### AC-057-B-04: Status Filter

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-04a | GIVEN the page is loaded WHEN the user selects "Completed" from status dropdown THEN only features with status "Completed" are shown | UI |
| AC-057-B-04b | GIVEN the status dropdown WHEN rendered THEN it contains: All Statuses, Planned, Refined, Designed, Implemented, Tested, Completed, Retired | UI |

### AC-057-B-05: Search

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-05a | GIVEN the search input WHEN the user types "FEATURE-055" THEN only matching features are displayed | UI |
| AC-057-B-05b | GIVEN the search input WHEN typing occurs THEN API calls are debounced by 300ms | Unit |

### AC-057-B-06: Feature Table Display

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-06a | GIVEN features are loaded for an epic WHEN rendered THEN each row shows: Feature ID, Title, Version, Status badge, Specification link, Last Updated | UI |
| AC-057-B-06b | GIVEN a feature with status "Completed" WHEN rendered THEN the badge is green (#22c55e) per mockup | UI |
| AC-057-B-06c | GIVEN a feature with status "Planned" WHEN rendered THEN the badge is gray (#94a3b8) per mockup | UI |
| AC-057-B-06d | GIVEN a feature with status "Retired" WHEN rendered THEN the badge is slate (#64748b) | UI |
| AC-057-B-06e | GIVEN features within an epic WHEN rendered THEN they are sorted by status priority (Planned→Retired) then by feature_id ascending | UI |

### AC-057-B-07: Inline Feature Detail Expansion

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-07a | GIVEN a feature row WHEN the user clicks it THEN an expanded detail section shows description, dependencies, and specification link | UI |
| AC-057-B-07b | GIVEN an expanded feature WHEN clicked again THEN the detail collapses | UI |
| AC-057-B-07c | GIVEN a feature with a specification_link WHEN expanded THEN the link opens in a new tab | UI |

### AC-057-B-08: Empty & Error States

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-08a | GIVEN no features exist WHEN the page loads THEN "No features found" message is displayed | UI |
| AC-057-B-08b | GIVEN the API fails WHEN the page tries to load THEN an error banner is shown | UI |

### AC-057-B-09: Mockup Visual Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-B-09a | GIVEN the page WHEN inspecting fonts THEN DM Sans body and DM Mono monospace per mockup | UI |
| AC-057-B-09b | GIVEN the page WHEN inspecting colors THEN Slate/Emerald palette per mockup | UI |
| AC-057-B-09c | GIVEN the page WHEN inspecting epic headers THEN they show epic ID badge, name, feature count, and progress bar per mockup | UI |

## Functional Requirements

- **FR-01:** Served at `/feature-board` via Flask route using `render_template('feature-board.html')`.
- **FR-02:** Extends `base.html` for app chrome.
- **FR-03:** On load, fetches `/api/features/epic-summary` for accordion headers.
- **FR-04:** On epic expand, fetches `/api/features/list?epic_id=X` for that epic's features.
- **FR-05:** Status filter passes `status` param; search passes `search` param with 300ms debounce.
- **FR-06:** Feature rows sorted by status priority then feature_id within each epic.

## Non-Functional Requirements

- **NFR-01:** Page initial render < 500ms.
- **NFR-02:** Epic expand + fetch + render < 2s.
- **NFR-03:** Keyboard-accessible (tab, enter, escape).
- **NFR-04:** No external CDN dependencies.

## UI/UX Requirements

- **UIR-01:** Same DM Sans/DM Mono font stack as task board.
- **UIR-02:** 7 feature status colors: Planned #94a3b8, Refined #8b5cf6, Designed #3b82f6, Implemented #f59e0b, Tested #06b6d4, Completed #22c55e, Retired #64748b.
- **UIR-03:** Epic accordion with chevron rotation animation, per-epic stacked progress bar.
- **UIR-04:** Epic ID badge in green accent, feature count on right side of header.

## Dependencies

- **FEATURE-056-B** (Feature Board API) — provides all 3 endpoints. **Status: Completed**.
- **base.html** template.

## Out of Scope

- Feature creation/editing (read-only), global progress bar, "Flat List" view toggle, pagination within epics, auto-refresh, export.
