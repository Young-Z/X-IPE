# FEATURE-036-D: Feature Lanes & Dependencies

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 02-17-2026 | Spark | Initial specification |

## Linked Mockups

| Mockup | Path | Status |
|--------|------|--------|
| Workflow View v1 | `../mockups/workflow-view-v1.html` | Current — feature lanes section (lines ~640–800) |

## Overview

Feature Lanes & Dependencies extends the Workflow View with per-feature progress tracking within the implement, validation, and feedback stages. After Feature Breakdown populates features in the workflow JSON, each feature appears as a horizontal swimlane showing its independent stage progression. Dependencies between features are visualized with SVG curved arrows and badge/tag indicators. A Working Item Selector dropdown allows users to pick a feature to focus on, highlighting its lane and filtering suggested actions.

### Problem Statement

FEATURE-036-C renders a single action grid per stage. When multiple features exist in implement/validation/feedback stages, users cannot see per-feature progress, dependencies, or which feature is ready to work on next.

### Solution

Render feature lanes (swimlanes) within per-feature stages, each showing per-action progress dots. Add dependency visualization (SVG arrows, ⛓ needs tags, ⇉ Parallel badges). Add a Working Item Selector dropdown to pick and highlight a feature.

## User Stories

### US-1: View Per-Feature Progress
**As a** developer using the Engineering Workflow view,  
**I want to** see each feature as a separate lane with per-stage progress indicators,  
**So that** I can quickly understand which features are ahead and which need attention.

### US-2: Understand Feature Dependencies
**As a** developer managing multiple features,  
**I want to** see dependency relationships between features (arrows, tags, badges),  
**So that** I know which features are blocked and which can proceed in parallel.

### US-3: Select Working Feature
**As a** developer switching between features,  
**I want to** select a feature from a dropdown and have its lane highlighted,  
**So that** I can focus on one feature's actions at a time.

### US-4: Safe Dependent Action Dispatch
**As a** developer clicking an action on a feature with unfinished dependencies,  
**I want to** see a confirmation dialog warning about the unfinished dependency,  
**So that** I can decide whether to proceed or wait.

## Acceptance Criteria

### AC-1: Feature Lane Rendering

| ID | Criterion |
|----|-----------|
| AC-1.1 | After Feature Breakdown completes (features exist in workflow JSON), feature lanes appear in the workflow panel body for implement/validation/feedback stages |
| AC-1.2 | Each lane shows: feature ID (monospace), feature name (bold), per-stage progress dots (done=green ✓, active=accent dot, pending=gray) |
| AC-1.3 | Lane stages show with arrows between them: Refinement › Tech Design › Implementation › Testing › Quality › CR |
| AC-1.4 | Hovering a lane highlights its border with accent color |
| AC-1.5 | Feature lanes container uses `position: relative` for SVG overlay positioning |
| AC-1.6 | If no features exist (pre-Feature Breakdown), no lanes section renders — stage ribbon shows normally |

### AC-2: Dependency Visualization

| ID | Criterion |
|----|-----------|
| AC-2.1 | Features with `depends_on` entries show a `⛓ needs {ID}` tag in the lane label |
| AC-2.2 | Independent features (empty `depends_on`) show a `⇉ Parallel` badge in the lane label |
| AC-2.3 | SVG curved connector arrows are drawn from source feature lane to dependent feature lane |
| AC-2.4 | Arrow style: dashed stroke (5,3), info color (#3b82f6), opacity 0.7, arrowhead polygon |
| AC-2.5 | Arrows re-draw on window resize |
| AC-2.6 | Dependencies toggle button shows/hides all dependency visualizations (SVG, tags, badges) |
| AC-2.7 | Toggle uses `deps-hidden` class on lanes container to control visibility |

### AC-3: Working Item Selector

| ID | Criterion |
|----|-----------|
| AC-3.1 | A "Select Feature to Work On" dropdown button appears in the workflow panel when features exist |
| AC-3.2 | Dropdown lists all features with: icon (🔄 in-progress, ✅ done, ⏳ pending), feature name, current stage, next suggested action |
| AC-3.3 | Selecting a feature highlights its lane (accent border + shadow) and closes the dropdown |
| AC-3.4 | Clicking outside the dropdown closes it |
| AC-3.5 | Dropdown is disabled (hidden) before Feature Breakdown (no features to show) |

### AC-4: Feature-Level Action Dispatch

| ID | Criterion |
|----|-----------|
| AC-4.1 | Clicking an action button on an independent feature dispatches immediately (same as FEATURE-036-C behavior) |
| AC-4.2 | Clicking an action button on a dependent feature with unfinished dependencies shows a confirmation modal warning about blockers |
| AC-4.3 | Confirmation modal lists the blocking feature(s) and their current stage |
| AC-4.4 | User can "Proceed Anyway" or "Cancel" from the confirmation modal |
| AC-4.5 | Confirmation modal uses Bootstrap-style custom modal (NOT native browser confirm) |
| AC-4.6 | Dependency check calls `GET /api/workflow/{name}/dependencies/{feature_id}` before dispatch |

### AC-5: Parallel Execution

| ID | Criterion |
|----|-----------|
| AC-5.1 | Independent features can have actions dispatched without blocking each other |
| AC-5.2 | Multiple concurrent CLI commands may be dispatched for independent features |

### AC-6: UI Layout Consistency

| ID | Criterion |
|----|-----------|
| AC-6.1 | Feature lane layout MUST match the approved mockup (workflow-view-v1.html) for component structure and visual hierarchy |
| AC-6.2 | Visual styling (colors, spacing, typography) MUST be consistent with mockup, adapted for dark theme |
| AC-6.3 | Interactive elements shown in mockup (hover, selection, toggle) MUST be present and functional |

### AC-7: Integration with Existing Components

| ID | Criterion |
|----|-----------|
| AC-7.1 | Feature lanes integrate below the stage ribbon within the expanded workflow panel body |
| AC-7.2 | Stage ribbon (FEATURE-036-C) continues to render above feature lanes |
| AC-7.3 | Action buttons within feature lanes follow the same dispatch pattern as FEATURE-036-C (CLI/modal) |
| AC-7.4 | Working Item Selector appears between stage ribbon and feature lanes area |

## Functional Requirements

### FR-1: Feature Lane Component
- Render a `div.lanes-container` containing one `div.feature-lane` per feature in the current stage's `features` object
- Each lane has a `div.lane-label` (180px wide, left side) and `div.lane-stages` (right side, scrollable)
- Lane label contains: feature ID (monospace, 10px), feature name (13px, bold), dependency badge/tag
- Lane stages contain per-action progress indicators with arrows between them

### FR-2: Dependency Visualization
- Read `depends_on` array from each feature's workflow JSON
- Render `⛓ needs {ID}` tag for dependent features, `⇉ Parallel` badge for independent ones
- Create SVG overlay with curved Bézier paths between dependent lanes
- Toggle button controls visibility via CSS class `deps-hidden`
- Re-draw arrows on `window.resize` event

### FR-3: Working Item Selector
- Dropdown button in panel body, positioned between stage ribbon and lanes
- Lists all features from implement/validation/feedback stages with status icons
- Selection highlights corresponding lane, deselects others
- Close on outside click

### FR-4: Dependency-Aware Action Dispatch
- Before dispatching feature-level action, call `GET /api/workflow/{name}/dependencies/{feature_id}`
- If `blocked: true`, show custom confirmation modal listing blockers
- If user confirms, proceed with normal dispatch; if cancel, abort

### FR-5: Feature Lane Data Source
- Feature data comes from workflow state: `stages[stageName].features` (only present in implement, validation, feedback stages)
- Each feature object: `{ name, depends_on, actions: { action_name: { status, deliverables } } }`
- Next action per feature: compare against `nextAction.feature_id` from next-action API

## Non-Functional Requirements

| NFR | Description |
|-----|-------------|
| NFR-1 | SVG arrow rendering completes within 100ms for up to 20 features |
| NFR-2 | Feature lanes render without layout shift (container height pre-allocated or animated) |
| NFR-3 | Dropdown opens/closes with CSS transition (0.25s ease) |

## UI/UX Requirements

### Dark Theme Adaptation (from mockup)
- Lane background: `var(--card-bg)` instead of `var(--slate-50)`
- Lane border: `1px solid var(--border-color)` instead of `var(--slate-200)`
- Highlighted lane: accent border + `box-shadow 0 0 0 2px rgb(16 185 129 / 0.15)`
- Feature ID color: `var(--accent)` (green)
- Feature name color: `var(--text-primary)` (light text on dark)
- Parallel badge: blue tones (`#1d4ed8` text, `#93c5fd` border, `#eff6ff` bg — may need dark-mode adaptation)
- Dependency tag: amber tones (`#a16207` text, `#fde68a` border, `#fefce8` bg — may need dark-mode adaptation)
- SVG arrows: info blue (`#3b82f6`)

### Stage Progress Indicators
- Done: green ✓ icon
- Active: accent-colored dot with pulse animation
- Pending: gray text, no icon

### Working Item Selector
- Button with dropdown indicator
- Items show status icon, feature name, current stage, next action badge
- Selected item gets accent background

## Dependencies

### Internal
- FEATURE-036-A: Workflow Manager (provides feature data, dependency check API)
- FEATURE-036-B: Workflow View Shell (panel container, expand/collapse)
- FEATURE-036-C: Stage Ribbon & Action Execution (stage ribbon rendering, action dispatch pattern)

### External
- None

## Business Rules

1. Feature lanes ONLY appear in stages that have a `features` object (implement, validation, feedback)
2. Features are independent within a stage — each progresses through its own actions
3. Dependency check is advisory, not blocking — users can override with confirmation
4. Features with no `depends_on` are always safe to work on
5. The Working Item Selector is purely a UI convenience — it does not change backend state

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|------------------|
| No features in workflow (pre-Feature Breakdown) | No lanes section renders; stage ribbon shows normally |
| Single feature, no dependencies | One lane, no SVG arrows, shows ⇉ Parallel badge |
| Circular dependency (A → B → A) | Render both ⛓ tags; both show blocked warning on action click |
| Feature with dependency on non-existent feature | ⛓ tag shows but no SVG arrow (missing target lane) |
| Many features (10+) | Lanes scroll vertically within container; SVG arrows re-draw on scroll |
| All features completed | All lane stages show ✓ done; no suggested actions |
| Window resize | SVG arrows re-drawn with debounced handler |
| Dependency toggle off then back on | SVG arrows and badges reappear via CSS class removal |

## Out of Scope

- Drag-and-drop lane reordering
- Feature creation/deletion from the UI (managed by Feature Breakdown skill)
- Per-feature deliverables display (FEATURE-036-E)
- Real-time polling updates (FEATURE-036-E)
- Cross-workflow feature dependencies

## Technical Considerations

- Feature lane data is already available in the workflow API response — no new backend endpoints needed
- Dependency check endpoint already exists: `GET /api/workflow/{name}/dependencies/{feature_id}`
- SVG overlay must use `pointer-events: none` to not interfere with lane click handlers
- Feature lanes should integrate into the existing `workflowStage.render()` flow
- Action dispatch within lanes reuses the same `_dispatchCliAction` / `_dispatchModalAction` from FEATURE-036-C

## Open Questions

None — all requirements are derived from the approved mockup and existing API.
