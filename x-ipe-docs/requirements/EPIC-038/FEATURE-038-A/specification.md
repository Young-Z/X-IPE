# Feature Specification: Action Execution Modal

> Feature ID: FEATURE-038-A
> Version: v1.0
> Status: Refined
> Last Updated: 02-20-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-20-2026 | Initial specification — reusable modal for CLI Agent workflow actions |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Refine Idea Modal | HTML | [refine-idea-modal-v1.html](x-ipe-docs/requirements/EPIC-038/mockups/refine-idea-modal-v1.html) | 4 scenes: action button states, modal dialog, post-refinement workflow, deliverable viewer | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

This feature introduces a reusable **Action Execution Modal** for all CLI Agent workflow actions in the engineering workflow view. Currently, CLI Agent actions (like Refine Idea) dispatch a command directly to the terminal via `_dispatchCliAction()` without any intermediate UI. This CR adds a modal dialog that opens between the button click and terminal dispatch, providing:

1. **Readonly instructions** loaded from `copilot-prompt.json` — so users understand what the action will do
2. **Extra instructions textarea** — so users can provide additional guidance to the agent (ephemeral, max 500 chars)
3. **Copilot execution button** — triggers the full console session flow (find idle → rename → type command)
4. **Progress indicator** — spinner/pulse on the action button during execution

This is a **CR on FEATURE-036-C** (Stage Ribbon & Action Execution), extending the existing action execution pattern from "click → terminal" to "click → modal → terminal". The modal follows the proven `ComposeIdeaModal` lifecycle pattern.

**Target Users:**
- Product owners / idea authors who want guided one-click action execution
- Developers who need a consistent, reusable pattern for all workflow actions

## User Stories

- **US-038-A.1:** As a workflow user, I want to see instructions before a CLI Agent action runs, so that I understand what the agent will do and can provide additional guidance.
- **US-038-A.2:** As a workflow user, I want to type extra instructions in a text field, so that I can customize the agent's behavior for this specific execution.
- **US-038-A.3:** As a workflow user, I want a visual progress indicator on the action button, so that I know the agent is working without blocking my other tasks.
- **US-038-A.4:** As a developer, I want a reusable modal component for CLI Agent actions, so that new actions can be added without duplicating UI code.

## Acceptance Criteria

### Modal Opening & Content

- [ ] AC-038-A.1: Clicking a CLI Agent action button (e.g., "Refine Idea") opens the Action Execution Modal instead of directly dispatching to terminal
- [ ] AC-038-A.2: Modal title displays the action label from `ACTION_MAP` (e.g., "Refine Idea")
- [ ] AC-038-A.3: Modal contains a readonly instructions area populated from `copilot-prompt.json`, matched by action ID (e.g., `refine-idea`)
- [ ] AC-038-A.4: If the action ID is not found in `copilot-prompt.json`, the instructions area shows a fallback message and the Copilot button is disabled
- [ ] AC-038-A.5: Modal contains an editable "Extra Instructions" textarea with a live character counter showing `{current}/{max}` (max 500)
- [ ] AC-038-A.6: Extra instructions textarea enforces 500-character limit client-side (input truncated beyond limit)
- [ ] AC-038-A.7: UI layout MUST match the approved mockup (refine-idea-modal-v1.html Scene 2) for modal structure
- [ ] AC-038-A.8: Visual styling (colors, spacing, typography) MUST be consistent with mockup (refine-idea-modal-v1.html Scene 2)

### Copilot Execution

- [ ] AC-038-A.9: Clicking the "Copilot" button triggers the console session flow: find idle session → rename session → construct CLI command → type into session
- [ ] AC-038-A.10: Agent CLI tool is detected from `cli-adapters.yaml` configuration (supports copilot, opencode, claude-code)
- [ ] AC-038-A.11: CLI command is constructed using the adapter's `prompt_format` template with the prompt from `copilot-prompt.json` and extra instructions appended
- [ ] AC-038-A.12: The command is sent to the terminal via `window.terminalManager.sendCopilotPromptCommandNoEnter()` — user must press Enter to confirm
- [ ] AC-038-A.13: After command is typed, modal closes and action button transitions to "in progress" state

### Progress Indicator & Status

- [ ] AC-038-A.14: Action button shows a spinner/pulse CSS animation when action status is `in_progress`
- [ ] AC-038-A.15: Spinner is non-blocking — user can interact with the rest of the UI during execution
- [ ] AC-038-A.16: Status refresh follows the agent → MCP → workflow-manager → UI chain (same pattern as Compose Idea)
- [ ] AC-038-A.17: When action status transitions to `done`, the action button shows the completed (✓) state
- [ ] AC-038-A.18: After completion, the deliverables section updates to show output artifacts
- [ ] AC-038-A.19: Interactive elements shown in mockup (refine-idea-modal-v1.html Scene 1) MUST be present and functional for action button states

### Modal Lifecycle

- [ ] AC-038-A.20: Modal can be closed via X button, Escape key, or clicking overlay backdrop
- [ ] AC-038-A.21: Modal can be re-opened while agent is running (shows "in progress" message instead of Copilot button)
- [ ] AC-038-A.22: Modal properly cleans up DOM elements and event listeners on close (no memory leaks)

### Reusability

- [ ] AC-038-A.23: The modal component accepts `actionKey`, `workflowName`, and `onComplete` callback as constructor parameters
- [ ] AC-038-A.24: Any CLI Agent action in `ACTION_MAP` with `interaction: 'cli'` can use this modal without code changes
- [ ] AC-038-A.25: The `_dispatchCliAction()` method in `workflow-stage.js` is updated to open this modal instead of directly sending to terminal

## Functional Requirements

**FR-038-A.1: Modal Construction**
- Input: `actionKey` (string), `workflowName` (string), `onComplete` (callback)
- Process: Create DOM structure with overlay, modal container, header (title + close btn), instructions area, extra instructions textarea with counter, and action buttons (Cancel + Copilot)
- Output: Modal appended to document body, visible with fade-in animation

**FR-038-A.2: Instructions Loading**
- Input: `actionKey` (e.g., `refine_idea`)
- Process: Map `actionKey` to `copilot-prompt.json` ID format (underscore → hyphen), fetch the matching prompt entry, extract the command text for the current language
- Output: Readonly instructions area populated, or fallback message if not found

**FR-038-A.3: Extra Instructions Input**
- Input: User keystrokes in textarea
- Process: Client-side validation — count characters, update counter display, prevent input beyond 500 chars
- Output: Character counter shows `{current}/500`, textarea value available for command construction

**FR-038-A.4: CLI Command Construction**
- Input: Prompt from `copilot-prompt.json`, extra instructions from textarea, `workflowName`, agent adapter config from `cli-adapters.yaml`
- Process: Build command using adapter's `prompt_format` template. If extra instructions provided, append `--extra-instructions "{text}"` or integrate into prompt string depending on adapter format.
- Output: Complete CLI command string ready to type into terminal

**FR-038-A.5: Console Session Dispatch**
- Input: Constructed CLI command
- Process: Call FEATURE-038-B's `find_idle_session()` via `SessionManager` → rename session to `wf-{workflowName}-{actionKey}` → type command via `terminalManager.sendCopilotPromptCommandNoEnter(command)`
- Output: Command visible in terminal, awaiting user Enter confirmation

**FR-038-A.6: Action Status Transition**
- Input: Agent execution lifecycle events
- Process: On modal submit → set button state to `in_progress` with spinner. Agent → MCP `update_workflow_action()` → workflow JSON updated → next UI render shows `done` state.
- Output: Button transitions: normal → in_progress (spinner) → done (✓)

**FR-038-A.7: Workflow Stage Integration**
- Input: Action button click event for any CLI Agent action
- Process: Update `_dispatchCliAction()` in `workflow-stage.js` to instantiate `ActionExecutionModal` instead of directly calling `terminalManager`
- Output: All CLI Agent actions now go through the modal flow

## Non-Functional Requirements

- **NFR-038-A.1:** Modal opening must complete within 200ms (instructions loaded from config already in memory via initial page load)
- **NFR-038-A.2:** Character count validation must respond to keystrokes without noticeable lag (<16ms per keystroke)
- **NFR-038-A.3:** Modal must work on viewport widths ≥ 768px (same as existing workflow view constraint)
- **NFR-038-A.4:** Extra instructions are ephemeral — never persisted to workflow JSON or local storage

## UI/UX Requirements

### Components (from mockup Scene 2)

| Component | Description | Behavior |
|-----------|-------------|----------|
| Modal Overlay | Semi-transparent backdrop | Click to close modal |
| Modal Container | Centered card, ~500px wide | Contains all modal content |
| Header | Action title + close (×) button | Close button dismisses modal |
| Instructions Area | Readonly text area / pre block | Displays prompt from copilot-prompt.json |
| Extra Instructions | Editable textarea with counter | Max 500 chars, live counter |
| Copilot Button | Primary action button with icon | Triggers execution flow |
| Cancel Button | Secondary button | Closes modal without action |

### Action Button States (from mockup Scene 1)

| State | Visual | Trigger |
|-------|--------|---------|
| Normal | Default button style | Initial state |
| Suggested | Dashed yellow border | Next recommended action |
| In Progress | Spinner/pulse animation | After Copilot button clicked |
| Done | Green with ✓ icon | After MCP status update |

### User Flow

```
1. User clicks CLI Agent action button in stage ribbon
2. Action Execution Modal opens with fade-in
3. User reads instructions, optionally types extra instructions
4. User clicks "Copilot" button
5. Modal closes, console session receives command
6. Action button shows spinner/pulse
7. User presses Enter in terminal to confirm execution
8. Agent executes skill → calls MCP → workflow JSON updated
9. Next UI render: action button shows ✓, deliverables appear
```

## Dependencies

### Internal

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-036-C | CR target | Stage Ribbon & Action Execution — base action button mechanics being extended |
| FEATURE-038-B | Runtime | Session Idle Detection — provides `find_idle_session()` for console session management |
| `ComposeIdeaModal` | Pattern reference | Modal lifecycle pattern (open → populate → submit → close) to follow |
| `workflow-stage.js` | Integration point | `_dispatchCliAction()` updated to open this modal |
| `copilot-prompt.json` | Data source | Provides action instructions text |
| `cli-adapters.yaml` | Data source | Provides agent CLI tool configuration |

### External

None — all dependencies are internal to the X-IPE project.

## Business Rules

- **BR-038-A.1:** Extra instructions are ephemeral — they exist only for the duration of the modal and are included in the CLI command. They are NOT saved anywhere.
- **BR-038-A.2:** The modal is the ONLY entry point for CLI Agent actions — direct terminal dispatch is no longer available from the workflow UI.
- **BR-038-A.3:** If `copilot-prompt.json` lacks instructions for an action, the modal still opens but the Copilot button is disabled with an error message.
- **BR-038-A.4:** The agent CLI command is typed but NOT auto-executed — user must press Enter in the terminal to start the agent.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Action ID missing from copilot-prompt.json | Show fallback message in instructions area, disable Copilot button, show info toast |
| No CLI adapter configured | Show error toast: "No agent CLI tool configured. Check cli-adapters.yaml." |
| User pastes text exceeding 500 chars | Truncate to 500, update counter to "500/500" |
| Modal opened while action already in_progress | Show "Execution in progress" message, hide Copilot button, show "Close" only |
| Terminal not available (console panel closed) | Auto-open console panel before dispatching command |
| Session management fails (FEATURE-038-B not available) | Fall back to creating a new session directly (graceful degradation) |
| User clicks Copilot, then immediately closes modal | Command still typed in terminal — no rollback needed |
| Workflow view re-rendered while modal is open | Modal stays open (attached to body, not workflow DOM) |

## Out of Scope

- **Real-time WebSocket status push** — uses existing polling/event-driven refresh
- **Auto-pressing Enter in terminal** — user always confirms manually
- **Persisting extra instructions** — always ephemeral
- **Customizing instructions per workflow** — instructions come from global copilot-prompt.json
- **Supporting non-CLI action types** — this modal is for `interaction: 'cli'` actions only
- **Deliverable viewer enhancement** — handled by FEATURE-038-C

## Technical Considerations

- New file: `src/x_ipe/static/js/features/action-execution-modal.js` — follows `ComposeIdeaModal` class structure
- Modification: `src/x_ipe/static/js/features/workflow-stage.js` — update `_dispatchCliAction()` to instantiate `ActionExecutionModal`
- Config access: `copilot-prompt.json` is loaded once at page init and available in-memory; `cli-adapters.yaml` served via existing config API
- CSS: Add spinner/pulse animation classes for in_progress state to existing workflow stage stylesheet
- The `ACTION_MAP` in `workflow-stage.js` already has `interaction: 'cli'` vs `'modal'` flags — use this to gate modal behavior

## Open Questions

None — all requirements clarified during ideation and requirement gathering.
