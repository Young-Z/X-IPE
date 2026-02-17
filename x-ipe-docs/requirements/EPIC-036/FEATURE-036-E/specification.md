# FEATURE-036-E: Deliverables, Polling & Lifecycle

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 02-17-2026 | Spark | Initial specification |

## Linked Mockups

| Mockup | Path | Status |
|--------|------|--------|
| Workflow View v1 | `../mockups/workflow-view-v1.html` | Current — deliverables section (lines ~856–964, 1537–1605) |

## Overview

### Problem Statement

The current Workflow View shows stage progression and feature lanes but has no visibility into produced artifacts (deliverables), no automatic state refresh, and no workflow lifecycle management. Users must manually reload the page to see updates, cannot browse deliverables from completed actions, and have no way to archive old workflows.

### Solution

Three capabilities:
1. **Deliverables Section** — Collapsible panel showing categorized artifacts (Ideas, Mockups, Requirements, Implementations, Quality Reports) with file existence verification
2. **Polling** — Automatic 7-second polling for workflow state changes with smart UI refresh
3. **Lifecycle** — Auto-archive workflows inactive for 30 days; error recovery with retry/manual override

## User Stories

### US-1: View Deliverables
**As a** developer reviewing a workflow,  
**I want to** see all produced artifacts categorized by type (Ideas, Mockups, Requirements, etc.),  
**So that** I can quickly find and access relevant files.

### US-2: Automatic State Refresh
**As a** developer with multiple agent sessions running,  
**I want** the workflow view to automatically update when actions complete,  
**So that** I see real-time progress without manual page reloads.

### US-3: Workflow Archival
**As a** developer with many workflows,  
**I want** inactive workflows to be automatically archived,  
**So that** the active list stays clean and manageable.

### US-4: Error Recovery
**As a** developer encountering a failed action,  
**I want to** retry or manually override the action status,  
**So that** I can recover from errors without recreating the workflow.

## Acceptance Criteria

### AC-1: Deliverables Section

| ID | Criterion |
|----|-----------|
| AC-1.1 | Collapsible deliverables section appears below feature lanes (or action area) in expanded workflow panel |
| AC-1.2 | Deliverables header shows "Deliverables" title with count badge |
| AC-1.3 | Click header toggles grid visibility (▾ expanded / ▸ collapsed) |
| AC-1.4 | Deliverables are categorized with color-coded icons: 💡 Ideas (purple), 🎨 Mockups (pink), 📋 Requirements (blue), 💻 Implementations (yellow), 📊 Quality (green) |
| AC-1.5 | Each deliverable card shows: category icon, filename, file path (monospace) |
| AC-1.6 | Missing files show "⚠️ not found" indicator on the card |
| AC-1.7 | Deliverable data comes from a backend API endpoint that resolves paths and checks file existence |
| AC-1.8 | UI layout MUST match the approved mockup (workflow-view-v1.html) for deliverables section |

### AC-2: Polling & Auto-Refresh

| ID | Criterion |
|----|-----------|
| AC-2.1 | Frontend polls `GET /api/workflow/{name}` every 7 seconds for expanded workflow panels |
| AC-2.2 | On state change detected (via `last_activity` timestamp comparison), UI re-renders affected panel body |
| AC-2.3 | Polling does not run for collapsed panels |
| AC-2.4 | Polling stops when navigating away from Workflow view |
| AC-2.5 | No visible UI flicker or layout shift during refresh |
| AC-2.6 | Polling does not cause noticeable CPU usage or network congestion |

### AC-3: Lifecycle — Auto-Archive

| ID | Criterion |
|----|-----------|
| AC-3.1 | Workflows with no activity for 30 days are automatically archived |
| AC-3.2 | Archived workflows are moved to `engineering-workflow/archive/` directory |
| AC-3.3 | Archived workflows are NOT shown in the active workflow list |
| AC-3.4 | Archive check runs on app startup and periodically (every hour) |

### AC-4: Error Recovery

| ID | Criterion |
|----|-----------|
| AC-4.1 | Context menu (right-click) on action buttons shows "Mark as Done" and "Reset to Pending" options |
| AC-4.2 | "Mark as Done" updates action status to "done" via API |
| AC-4.3 | "Reset to Pending" updates action status to "pending" via API |
| AC-4.4 | Context menu uses custom popup (NOT native browser context menu) |
| AC-4.5 | UI refreshes after manual override |

### AC-5: Integration

| ID | Criterion |
|----|-----------|
| AC-5.1 | Deliverables section integrates below feature lanes or action area in panel body |
| AC-5.2 | Polling works alongside feature lanes and stage ribbon without interference |
| AC-5.3 | Manual override works on both global actions and per-feature actions |

## Functional Requirements

### FR-1: Deliverables Resolver API
- New backend endpoint: `GET /api/workflow/{name}/deliverables`
- Reads deliverable paths from all actions in all stages (including per-feature actions)
- Categorizes deliverables by type based on path patterns or action context
- Verifies file existence on disk for each path
- Returns: `{ deliverables: [{ name, path, category, exists }] }`

### FR-2: Deliverables UI Component
- Collapsible section with header (title + count badge + toggle chevron)
- Grid layout: `repeat(auto-fill, minmax(200px, 1fr))`
- Cards with category icon, filename, path, optional "New" badge
- Missing files shown with ⚠️ indicator

### FR-3: Polling Mechanism
- `setInterval` at 7-second intervals for each expanded panel
- Store `last_activity` timestamp; compare on each poll
- On change: re-render panel body (stages + lanes + deliverables)
- Clear interval on panel collapse or view navigation

### FR-4: Auto-Archive Service
- Backend check: compare `last_activity` against `now - 30 days`
- Move workflow JSON from `engineering-workflow/` to `engineering-workflow/archive/`
- Run on app startup and every 60 minutes
- `list_workflows()` excludes archived workflows

### FR-5: Manual Override
- Custom context menu on action buttons (right-click handler)
- Options: "Mark as Done", "Reset to Pending"
- Calls `POST /api/workflow/{name}/action` with status update
- Works for both shared and per-feature actions

## Non-Functional Requirements

| NFR | Description |
|-----|-------------|
| NFR-1 | Polling interval must be configurable (default 7 seconds) |
| NFR-2 | Deliverables resolver must respond within 500ms for up to 100 deliverables |
| NFR-3 | Auto-archive must complete within 5 seconds for up to 50 workflows |
| NFR-4 | Context menu must appear within 100ms of right-click |

## UI/UX Requirements

### Dark Theme Adaptation (from mockup)
- Deliverables area: `var(--card-bg)` background
- Cards: border `var(--border-color)`, hover accent
- Category icon backgrounds adapted for dark theme
- Grid responsive: auto-fill with 200px minimum
- Toggle chevron: ▾ (expanded) / ▸ (collapsed)

### Category Colors (dark theme adapted)
- Ideas (💡): purple tones — bg: `rgba(168,85,247,0.15)`, text: `#a855f7`
- Mockups (🎨): pink tones — bg: `rgba(236,72,153,0.15)`, text: `#ec4899`
- Requirements (📋): blue tones — bg: `rgba(59,130,246,0.15)`, text: `#3b82f6`
- Implementations (💻): yellow tones — bg: `rgba(245,158,11,0.15)`, text: `#f59e0b`
- Quality (📊): green tones — bg: `rgba(16,185,129,0.15)`, text: `#10b981`

### Context Menu
- Positioned at cursor location
- Small popup with 2 options
- Close on outside click
- Custom styled (NOT native browser context menu)

## Dependencies

### Internal
- FEATURE-036-A: Workflow Manager (state API, deliverable paths, archive target directory)
- FEATURE-036-B: Workflow View Shell (panel container for deliverables section)

### External
- None

## Business Rules

1. Deliverables are extracted from all `deliverables` arrays across all actions in all stages
2. File existence is checked at resolve time, not cached
3. Category is inferred from action context (ideation actions → Ideas, requirement actions → Requirements, etc.)
4. Archive threshold is 30 days of inactivity (configurable)
5. Manual override does NOT trigger stage gating re-evaluation (it's a manual recovery tool)
6. Polling only runs for expanded panels to minimize server load

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|------------------|
| No deliverables | Deliverables section shows "No deliverables yet" |
| All files missing | All cards show ⚠️ not found indicator |
| Large number of deliverables (50+) | Grid scrolls vertically within section |
| Concurrent polls for multiple expanded panels | Each panel polls independently |
| Network error during poll | Silently skip, retry on next interval |
| Archive during active view | Panel disappears on next refresh |
| Manual override on completed action | Status changes; UI refreshes |
| Right-click on locked action | Context menu still appears (allows manual override) |

## Out of Scope

- Deliverable file preview/viewer
- Deliverable file download
- Archive view/restore UI (v2)
- Custom polling interval UI control
- Deliverable upload from UI
- Real-time WebSocket push (using polling instead)

## Technical Considerations

- Deliverables Resolver is a backend endpoint to avoid frontend filesystem access
- Category inference based on action-to-stage mapping (reuse ACTION_MAP from workflow-stage.js)
- Polling uses `last_activity` timestamp comparison for efficiency
- Auto-archive uses file system move (rename) for atomicity
- Context menu positioning uses `event.clientX/clientY` with viewport boundary clamping

## Open Questions

None — all requirements derived from approved mockup and existing API.
