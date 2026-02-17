# FEATURE-036-B: Workflow View Shell & CRUD

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-17 | Cipher | Initial specification |

## Linked Mockups

| Mockup | Status | Notes |
|--------|--------|-------|
| [workflow-view-v1.html](../mockups/workflow-view-v1.html) | current | Shared EPIC-036 mockup — shows workflow list panel, create button, expandable panels |

## Overview

FEATURE-036-B provides the frontend shell for the Engineering Workflow system. It adds a new "Engineering Workflow" button to the top navigation bar, renders a workflow list view in the main content area, and provides CRUD operations (create via modal, delete via action menu) backed by the Workflow Manager API (FEATURE-036-A).

This feature establishes the visual container into which subsequent features (Stage Ribbon, Feature Lanes, Deliverables) will render their sub-components.

## User Stories

### US-001: View Workflow List
**As** a developer using X-IPE,  
**I want** to see all my active engineering workflows in one view,  
**So that** I can quickly navigate to and manage my ongoing projects.

### US-002: Create New Workflow
**As** a developer,  
**I want** to create a new engineering workflow with a single click and name entry,  
**So that** I can begin tracking a new development effort immediately.

### US-003: Delete Workflow
**As** a developer,  
**I want** to delete a workflow I no longer need,  
**So that** my workflow list stays clean and relevant.

### US-004: View Workflow Details
**As** a developer,  
**I want** to expand a workflow panel to see its current stage, creation date, and feature count,  
**So that** I can get a quick status overview without leaving the list.

## Acceptance Criteria

### AC Group: Navigation Integration

- **AC-001**: "Engineering Workflow" button appears in the top-menu `.menu-actions` bar alongside Knowledge, Toolbox, Skills, Settings.
- **AC-002**: Button uses Bootstrap icon `bi-diagram-3` and label text "Workflow".
- **AC-003**: Clicking the button replaces the content area (`#content-body`) with the workflow view, hiding sidebar and breadcrumb.
- **AC-004**: Clicking another top-nav button (e.g., Knowledge) restores the default layout and hides the workflow view.
- **AC-005**: The active state (CSS class) is applied to the Workflow button when the view is active.

### AC Group: Workflow List

- **AC-006**: On view activation, `GET /api/workflow/list` is called and results render as vertically stacked expandable panels.
- **AC-007**: Each panel header displays: workflow name (bold), creation date (formatted), feature count badge, current stage indicator pill.
- **AC-008**: Clicking a panel header toggles the panel body open/closed.
- **AC-009**: When no workflows exist, an empty-state placeholder is shown ("No workflows yet — create one to get started").
- **AC-010**: Panel list auto-refreshes on view activation (re-fetches from API).

### AC Group: Create Workflow

- **AC-011**: A "+ Create Workflow" button is positioned at the top-right of the workflow view.
- **AC-012**: Clicking "+ Create Workflow" opens a modal dialog with a single text input for workflow name.
- **AC-013**: The modal validates name format (alphanumeric + hyphens, ≤100 chars) with inline error feedback before submission.
- **AC-014**: Submitting the modal calls `POST /api/workflow/create` with `{name}`.
- **AC-015**: On success (201), the modal closes and the new workflow panel appears in the list without full page reload.
- **AC-016**: On duplicate name (409), the modal shows an error message "Workflow already exists".
- **AC-017**: On invalid name (400), the modal shows a validation error.

### AC Group: Delete Workflow

- **AC-018**: Each panel header has a "⋮" action menu button (3-dot vertical).
- **AC-019**: The action menu includes a "Delete" option with red text and trash icon.
- **AC-020**: Clicking "Delete" shows a confirmation dialog: "Delete workflow '{name}'? This cannot be undone."
- **AC-021**: Confirming delete calls `DELETE /api/workflow/{name}` and removes the panel from the list.
- **AC-022**: On API error, a toast notification shows the error message.

### AC Group: Mockup Alignment

- **AC-023**: UI layout MUST match the approved mockup (workflow-view-v1.html) for the workflow list panel section.
- **AC-024**: Visual styling (colors, spacing, typography) MUST be consistent with mockup (workflow-view-v1.html).
- **AC-025**: Interactive elements shown in mockup (expandable panels, create button, action menu) MUST be present and functional.

## Functional Requirements

- **FR-001**: The workflow view JavaScript module (`workflow.js`) MUST be loaded as a feature module in `static/js/features/`.
- **FR-002**: The module MUST expose a `render(container)` function that renders the full workflow view into the given DOM element.
- **FR-003**: Navigation button click MUST call `render()` with `#content-body` as container, hiding sidebar.
- **FR-004**: API calls MUST use `fetch()` with proper error handling (try/catch, response status checks).
- **FR-005**: Panel expansion state MUST be preserved during list re-renders (track expanded panel names).
- **FR-006**: The create modal MUST prevent double-submission (disable button after click, re-enable on error).
- **FR-007**: Delete confirmation MUST be a native `confirm()` dialog or a styled modal consistent with existing X-IPE patterns.

## Non-Functional Requirements

- **NFR-001**: Workflow list must render within 500ms for up to 50 workflows.
- **NFR-002**: JavaScript module must be under 15KB unminified.
- **NFR-003**: Must work in latest Chrome (primary target).
- **NFR-004**: Must use existing CSS variables and design tokens from X-IPE stylesheet.

## UI/UX Requirements

- **UIR-001**: Workflow panels use the same card/panel styling as existing X-IPE components (rounded corners, subtle shadow, dark theme).
- **UIR-002**: Stage indicator pill uses colored background matching stage status (green=completed, blue=active, gray=locked).
- **UIR-003**: Create modal follows existing X-IPE modal patterns (centered overlay, escape to close, focus trap).
- **UIR-004**: Empty state uses centered icon + text pattern consistent with content-placeholder in index.html.
- **UIR-005**: Action menu appears on hover or click of ⋮ button, positions below the button.

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-036-A | Required | Workflow Manager API (CRUD endpoints) |
| FEATURE-001 | Reference | Navigation patterns (sidebar.js) |
| FEATURE-025-B | Reference | Content area takeover pattern (kb-landing.js) |

## Business Rules

- **BR-001**: Workflow names must be unique across the project.
- **BR-002**: No idea folder is required at creation time (lazy linking per EPIC-036 requirements).
- **BR-003**: Deleted workflows cannot be recovered (v1.0 — no soft delete).

## Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | API unreachable during list fetch | Show error banner with retry button |
| 2 | API unreachable during create | Show error in modal, keep modal open |
| 3 | Workflow deleted by another agent while viewing | Panel disappears on next refresh |
| 4 | Very long workflow name (100 chars) | Truncate with ellipsis in panel header |
| 5 | Rapid double-click on Create button | Second click is ignored (double-submit protection) |
| 6 | Browser back/forward navigation | Workflow view state is not persisted in browser history (acceptable for v1.0) |

## Out of Scope

- Stage ribbon rendering (FEATURE-036-C)
- Feature lane rendering (FEATURE-036-D)
- Deliverables section and polling (FEATURE-036-E)
- Workflow archiving (deferred to future version)
- Keyboard shortcuts for navigation
- Mobile/responsive layout

## Technical Considerations

- Content area takeover pattern: follow `kbLanding.render(container)` approach — receive container, build DOM, inject.
- Top-nav button: add alongside existing buttons in `.menu-actions` div in `index.html`.
- JS module: `static/js/features/workflow.js` with IIFE or object literal pattern matching existing feature modules.
- API integration: all calls to `/api/workflow/*` endpoints provided by FEATURE-036-A.
- No new Flask template needed — all rendering via JavaScript DOM manipulation.

## Open Questions

None — all design decisions resolved during EPIC-036 requirement gathering.
