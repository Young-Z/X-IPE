# Feature Specification: Stage Ribbon & Action Execution

> Feature ID: FEATURE-036-C  
> Epic: EPIC-036 (Engineering Workflow View)  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-17-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Engineering Workflow View | HTML | [../mockups/workflow-view-v1.html](../mockups/workflow-view-v1.html) | Full workflow view — stage ribbon section, action buttons area | current |

> **Note:** The shared mockup covers the full EPIC-036 UI. FEATURE-036-C focuses on the stage ribbon bar and action buttons area within each expanded workflow panel.

## Overview

FEATURE-036-C adds a horizontal stage progression ribbon and per-stage action buttons inside each expanded workflow panel. The ribbon visualizes the 5 delivery stages (Ideation → Requirement → Implement → Validation → Feedback) with distinct visual states (completed, active, pending, locked). Below the ribbon, stage-specific action buttons allow users to trigger skill execution via the console or open modal UIs for idea management.

This feature bridges the visual workflow view (FEATURE-036-B) with the backend Workflow Manager (FEATURE-036-A) by rendering live stage/action state and enabling action execution. It is the core interaction layer that turns the workflow view from a passive display into an active orchestration tool.

The primary user is a developer using X-IPE who wants to see where they are in the delivery lifecycle and trigger the next action without manually navigating to skills or typing console commands.

## User Stories

### US-001: View Stage Progression
**As** a developer using X-IPE,  
**I want** to see a visual stage ribbon showing which stages are done, active, and pending,  
**So that** I can instantly understand where my workflow stands in the delivery lifecycle.

### US-002: See Available Actions
**As** a developer,  
**I want** to see action buttons for the current stage with clear visual states (done, suggested, normal),  
**So that** I know what's been completed, what's recommended next, and what's available.

### US-003: Execute CLI Agent Action
**As** a developer,  
**I want** to click an action button that auto-types the skill command into an idle console session,  
**So that** I can trigger skill execution without manually navigating to the console and typing commands.

### US-004: Execute Modal Action (Compose Idea)
**As** a developer,  
**I want** to click "Compose Idea" and have it prompt me for an idea folder (if not linked), then open the idea creation UI,  
**So that** I can start the ideation stage without leaving the workflow view.

### US-005: See Locked Stages
**As** a developer,  
**I want** locked stages to be visually grayed out with a message explaining what needs to be completed first,  
**So that** I understand the gating rules and don't try to skip steps.

## Acceptance Criteria

### AC Group: Stage Ribbon

- **AC-001**: Stage ribbon renders inside expanded workflow panel body, between panel header and action buttons area.
- **AC-002**: Ribbon shows 5 stages in order: Ideation → Requirement → Implement → Validation → Feedback, separated by `›` arrow separators.
- **AC-003**: Stage visual states:
  - Completed: green background, ✓ check icon, green text
  - Active: accent/green gradient background, animated pulsing dot, white text
  - Pending: white/light background, numbered circle (4, 5), gray text
  - Locked: grayed out, opacity reduced, lock icon
- **AC-004**: Stage states are derived from the workflow JSON returned by `GET /api/workflow/{name}` — specifically each stage's `status` field (`completed`, `in_progress`, `pending`, `locked`).
- **AC-005**: Stage ribbon updates when the panel re-renders (e.g., after action completion triggers a refresh).

### AC Group: Action Buttons

- **AC-006**: Below the stage ribbon, an actions area displays action buttons for the current active stage and all completed stages.
- **AC-007**: Completed stage actions are grouped under a "COMPLETED ACTIONS" label.
- **AC-008**: Active stage actions are grouped under a "{STAGE_NAME} ACTIONS" label (e.g., "IDEATION ACTIONS").
- **AC-009**: Locked stage actions are grouped under a "{STAGE_NAME} ACTIONS" label with a sub-label "— complete {previous_stage} to unlock".
- **AC-010**: Action button visual states:
  - Done: green background/border, ✓ prefix, green text
  - Suggested (next recommended): yellow dashed border, → prefix, amber text, subtle glow animation
  - Normal (available but not suggested): white background, gray border, ○ prefix
  - Locked: gray background, lock icon prefix, reduced opacity, `cursor: not-allowed`
- **AC-011**: Each action button displays an emoji icon and action name matching the action-to-skill mapping table.
- **AC-012**: The "suggested" action is determined by `GET /api/workflow/{name}/next-action` response.

### AC Group: Action-to-Skill Mapping

- **AC-013**: The following 12 actions are mapped to their respective stages and skills:

| Stage | Action | Icon | Mandatory | Interaction | Skill |
|-------|--------|------|-----------|-------------|-------|
| Ideation | Compose/Upload Idea | 📝 | ✅ | Modal | (built-in) |
| Ideation | Reference UIUX | 🎨 | ❌ | CLI Agent | x-ipe-tool-uiux-reference |
| Ideation | Refine Idea | 💡 | ✅ | CLI Agent | x-ipe-task-based-ideation-v2 |
| Ideation | Design Mockup | 🖼 | ❌ | CLI Agent | x-ipe-task-based-idea-mockup |
| Requirement | Requirement Gathering | 📋 | ✅ | CLI Agent | x-ipe-task-based-requirement-gathering |
| Requirement | Feature Breakdown | 🔀 | ✅ | CLI Agent | x-ipe-task-based-feature-breakdown |
| Implement | Feature Refinement | 📐 | ✅ | CLI Agent | x-ipe-task-based-feature-refinement |
| Implement | Technical Design | ⚙ | ✅ | CLI Agent | x-ipe-task-based-technical-design |
| Implement | Implementation | 💻 | ✅ | CLI Agent | x-ipe-task-based-code-implementation |
| Validation | Acceptance Testing | ✅ | ✅ | CLI Agent | x-ipe-task-based-feature-acceptance-test |
| Validation | Quality Evaluation | 📊 | ❌ | CLI Agent | (deferred — v2) |
| Feedback | Change Request | 🔄 | ❌ | CLI Agent | x-ipe-task-based-change-request |

### AC Group: CLI Agent Action Execution

- **AC-014**: Clicking a CLI Agent action button calls `GET /api/workflow/{name}/next-action` to verify the action is allowed (not locked/already done).
- **AC-015**: If action is allowed, the console panel opens (if not already visible) and an idle session is selected.
- **AC-016**: The skill command is auto-typed into the selected console session (e.g., the skill trigger phrase). The command is NOT auto-submitted — user must press Enter to confirm.
- **AC-017**: If no idle session is available, a toast notification informs the user: "No idle console session available. Open a new session first."
- **AC-018**: If the action is locked or already done, clicking the button shows a toast with the reason (e.g., "Action already completed" or "Stage is locked").

### AC Group: Modal Action Execution (Compose/Upload Idea)

- **AC-019**: Clicking "Compose/Upload Idea" checks if the workflow has an `idea_folder` linked.
- **AC-020**: If no idea folder is linked, a prompt dialog asks the user to enter an idea folder name or select an existing one.
- **AC-021**: After idea folder is provided, `POST /api/workflow/{name}/link-idea` is called to persist the link.
- **AC-022**: Once the idea folder is linked, the existing idea creation/upload UI opens (same as FEATURE-008 Workplace).
- **AC-023**: The idea folder link is persisted in the workflow JSON and shown in subsequent renders.

### AC Group: Locked Stage Behavior

- **AC-024**: Locked stages in the ribbon have reduced opacity and show a lock icon instead of a number.
- **AC-025**: Action buttons for locked stages show the lock prefix icon and are non-clickable (`cursor: not-allowed`).
- **AC-026**: Hovering a locked action button shows a tooltip: "Complete {required_stage} to unlock this action."

### AC Group: Mockup Alignment

- **AC-027**: Stage ribbon layout MUST match the mockup `workflow-view-v1.html` — horizontal pills with arrow separators, color-coded states.
- **AC-028**: Action buttons area MUST match the mockup — grid layout with icon + label, state-based styling (done/suggested/normal/locked).
- **AC-029**: Visual styling (colors, spacing, typography, animations) MUST be consistent with the mockup design system.

## Functional Requirements

### FR-036-C.1: Stage Ribbon Rendering

**Description:** Render a horizontal stage progression bar inside each expanded workflow panel.

**Details:**
- Input: Workflow state from `GET /api/workflow/{name}` containing per-stage status
- Process: For each of the 5 stages, determine visual state from status field, render pill element with appropriate icon and styling
- Output: DOM elements for the stage ribbon inserted into the panel body

### FR-036-C.2: Action Buttons Rendering

**Description:** Render stage-specific action buttons below the stage ribbon.

**Details:**
- Input: Workflow state (action statuses per stage), next-action recommendation from API
- Process: Group actions by stage, apply visual state (done/suggested/normal/locked), render button grid
- Output: DOM elements for the actions area with clickable buttons

### FR-036-C.3: CLI Agent Action Dispatch

**Description:** Dispatch CLI agent actions by auto-typing skill commands into an idle console session.

**Details:**
- Input: Action button click with mapped skill name
- Process: Verify action allowed → find idle console session → open console panel → auto-type command
- Output: Skill command typed into console session, awaiting user confirmation (Enter)

### FR-036-C.4: Modal Action Dispatch (Compose/Upload Idea)

**Description:** Handle Compose/Upload Idea action via modal UI flow.

**Details:**
- Input: Action button click for Compose/Upload Idea
- Process: Check idea_folder linked → prompt if not → link via API → open idea creation UI
- Output: Idea folder linked to workflow, idea creation UI opened

### FR-036-C.5: Stage Data Fetching

**Description:** Fetch full workflow state including stage and action details for ribbon rendering.

**Details:**
- Input: Workflow name
- Process: Call `GET /api/workflow/{name}` which returns stages with their statuses and action statuses
- Output: Parsed stage/action data for rendering

## Non-Functional Requirements

- **NFR-001**: Stage ribbon and action buttons must render within 200ms after workflow data is available.
- **NFR-002**: Action button click-to-console-type latency must be under 500ms.
- **NFR-003**: CSS animations (pulsing dot, suggested glow) must not cause noticeable CPU usage.
- **NFR-004**: Must work in latest Chrome (primary target).
- **NFR-005**: Stage ribbon must be horizontally scrollable on narrow viewports without breaking layout.

## UI/UX Requirements

- **UIR-001**: Stage ribbon uses pill/badge styling with rounded corners, matching the mockup's `.stage-item` design.
- **UIR-002**: Active stage has a pulsing animated dot (CSS animation `pulse-dot`, 2s infinite).
- **UIR-003**: Suggested action button has a subtle glowing animation (CSS animation `gentle-glow`, 3s infinite) with dashed border.
- **UIR-004**: Action buttons use consistent emoji icons from the action-to-skill mapping table.
- **UIR-005**: Completed/active/pending stages use the color system: green (#22c55e / #ecfdf5) for done, accent (#10b981) for active, gray (#94a3b8 / #e2e8f0) for pending.
- **UIR-006**: Action area sections have uppercase label headers (e.g., "COMPLETED ACTIONS", "IDEATION ACTIONS") matching the mockup's `.actions-label` style.

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-036-A | Required | Workflow Manager API — stage statuses, action statuses, next-action, gating logic |
| FEATURE-036-B | Required | Workflow View Shell — panel container, panel body where ribbon/actions render |
| FEATURE-005/029 | Reference | Console/Terminal — session APIs for finding idle session, auto-typing commands |
| FEATURE-008 | Reference | Workplace/Idea Management — idea creation modal UI for Compose/Upload Idea action |

## Business Rules

- **BR-001**: Only actions for completed stages, the active stage, and the first locked stage are rendered. Stages further ahead show no action buttons.
- **BR-002**: The "suggested" action (yellow dashed) is always the next recommended action from the Workflow Manager's `next-action` API.
- **BR-003**: CLI agent commands are auto-typed but NEVER auto-submitted — the user must press Enter to confirm execution.
- **BR-004**: Optional actions (Reference UIUX, Design Mockup, Quality Evaluation, Change Request) can be skipped without blocking stage progression.
- **BR-005**: Stage gating is enforced server-side by the Workflow Manager — the frontend displays the result but does not compute gating logic.

## Edge Cases & Constraints

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | All actions in a stage are done but stage not yet marked completed | Frontend shows actions as done; stage status comes from API (may still be "active" until gating re-evaluation) |
| 2 | No idle console session available for CLI action | Toast: "No idle console session available. Open a new session first." |
| 3 | API returns error when fetching workflow state | Stage ribbon area shows error message with retry button |
| 4 | Action execution triggered while another action is in_progress | Allow it — multiple actions can be in_progress simultaneously (different console sessions) |
| 5 | User clicks done action | Toast: "Action already completed" — no re-execution |
| 6 | User clicks locked action | Toast: "Complete {required_stage} to unlock this action" — no execution |
| 7 | Quality Evaluation action (deferred to v2) | Render button with "Coming Soon" tooltip, disabled state |
| 8 | Workflow has no features yet (pre-Feature Breakdown) | Implement/Validation/Feedback stages show as locked with message "Complete Requirement to unlock" |
| 9 | Stage ribbon overflow on narrow screen | Horizontal scroll with `overflow-x: auto` |

## Out of Scope

- Feature lanes rendering (FEATURE-036-D)
- Deliverables section (FEATURE-036-E)
- Working Item Selector dropdown (FEATURE-036-D)
- Dependency visualization (FEATURE-036-D)
- Auto-archive lifecycle (FEATURE-036-E)
- Polling for real-time updates (FEATURE-036-E)
- Mobile/responsive layout
- Keyboard shortcuts for actions

## Technical Considerations

- Stage ribbon and action buttons render inside the existing `.workflow-panel-body` from FEATURE-036-B. The current body content (Created, Last Activity, etc.) should move below or be replaced by the richer ribbon + actions view.
- The `GET /api/workflow/{name}` response must include full stage and action details (not just `current_stage` string). If the current list endpoint only returns summary data, the panel expand should fetch the full workflow state.
- Console integration should reuse the same pattern as the existing copilot button in the ideation view — find an idle session via DOM inspection or session API, then programmatically type into the terminal input.
- Action-to-skill mapping is a static configuration object in the JS module — no API call needed for the mapping itself.
- The stage ribbon CSS should be added to `workflow.css` to keep styles co-located with the feature module.

## Open Questions

None — all design decisions resolved during EPIC-036 requirement gathering and mockup review.
