# Feature Specification: Tracing Dashboard UI

> Feature ID: FEATURE-023-B  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-01-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-01-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| Tracing Dashboard v4 | HTML | [mockups/tracing-dashboard-v4.html](mockups/tracing-dashboard-v4.html) | Full dashboard with duration toggle, countdown timer, trace list sidebar |

> **Note:** UI/UX requirements below are derived from this mockup.

---

## Overview

**Tracing Dashboard UI** is a web-based interface for managing application action tracing sessions within X-IPE Workplace. It provides controls to start/stop tracing with configurable durations, displays a countdown timer, and shows a sidebar list of captured trace logs for selection.

This feature builds on FEATURE-023-A (Core Tracing Backend) and provides the user-facing interface for:
- Starting tracing sessions with duration presets (3/15/30 minutes)
- Monitoring active tracing with a live countdown timer
- Browsing and selecting captured trace logs
- Accessing configuration and ignored APIs settings

The dashboard integrates into the X-IPE Workplace as a new view accessible from the sidebar.

---

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US-1 | Developer | start tracing with a single click | I can quickly capture execution traces without config files |
| US-2 | Developer | see a countdown timer when tracing is active | I know when tracing will automatically stop |
| US-3 | Developer | stop tracing early if needed | I don't capture unnecessary data |
| US-4 | Developer | see a list of captured traces | I can select which trace to view |
| US-5 | Developer | resume tracing session after page refresh | I don't lose my tracing session on navigation |
| US-6 | QA Engineer | configure tracing retention settings | old logs are automatically cleaned up |
| US-7 | Operations | manage ignored APIs | I can exclude health checks and noisy endpoints |

---

## Acceptance Criteria

### 1. Workplace Integration

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | Tracing Dashboard MUST be accessible from Workplace sidebar | Must |
| AC-1.2 | Dashboard MUST display in the main content area (right panel) | Must |
| AC-1.3 | Dashboard MUST follow X-IPE design system (colors, typography) | Must |
| AC-1.4 | Dashboard SHOULD use light theme matching other X-IPE views | Should |

### 2. Header Controls

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | Header MUST display "Tracing" title | Must |
| AC-2.2 | Header MUST include "Config" button to open settings modal | Must |
| AC-2.3 | Header MUST include "Ignored APIs" button to manage exclusions | Must |
| AC-2.4 | Duration buttons (3 min, 15 min, 30 min) MUST be visible in header | Must |
| AC-2.5 | Clicking duration button MUST start tracing and set countdown | Must |
| AC-2.6 | Only one duration can be active at a time | Must |
| AC-2.7 | Active duration button MUST show selected/active styling | Must |

### 3. Countdown Timer

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | Countdown timer MUST display remaining time in MM:SS format | Must |
| AC-3.2 | Timer MUST update every second when tracing is active | Must |
| AC-3.3 | Timer MUST show green color when > 1 minute remaining | Must |
| AC-3.4 | Timer MUST show yellow/warning color when < 1 minute remaining | Should |
| AC-3.5 | Timer MUST show gray when tracing is inactive | Must |
| AC-3.6 | "Stop" button MUST appear when tracing is active | Must |
| AC-3.7 | Clicking "Stop" MUST immediately stop tracing | Must |
| AC-3.8 | When countdown reaches 0, tracing MUST stop automatically | Must |

### 4. Trace Session Persistence

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Tracing state MUST persist across page refresh | Must |
| AC-4.2 | `tracing_stop_at` timestamp MUST be stored in tools.json | Must |
| AC-4.3 | On page load, dashboard MUST check tools.json for active session | Must |
| AC-4.4 | If `tracing_stop_at` > now, dashboard MUST resume countdown | Must |
| AC-4.5 | If `tracing_stop_at` < now, dashboard MUST show inactive state | Must |

### 5. Trace List Sidebar

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | Left sidebar MUST display list of captured trace log files | Must |
| AC-5.2 | Each trace entry MUST show trace ID (truncated) | Must |
| AC-5.3 | Each trace entry MUST show API name/path | Must |
| AC-5.4 | Each trace entry MUST show timestamp | Must |
| AC-5.5 | Each trace entry MUST show status indicator (green=success, red=error) | Must |
| AC-5.6 | Clicking trace entry MUST select it for viewing | Must |
| AC-5.7 | Selected trace MUST be highlighted | Must |
| AC-5.8 | Trace list MUST be scrollable if many entries | Must |
| AC-5.9 | Trace list SHOULD refresh automatically when new traces arrive | Should |
| AC-5.10 | Empty state MUST show "No traces captured" message | Must |

### 6. Config Modal

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | Config modal MUST open when "Config" button is clicked | Must |
| AC-6.2 | Modal MUST allow setting retention hours (default: 24) | Must |
| AC-6.3 | Modal MUST allow setting log path (default: instance/traces/) | Should |
| AC-6.4 | Modal MUST have Save and Cancel buttons | Must |
| AC-6.5 | Save MUST update tools.json via API | Must |
| AC-6.6 | Modal MUST close after successful save | Must |

### 7. Ignored APIs Modal

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | Ignored APIs modal MUST open when button is clicked | Must |
| AC-7.2 | Modal MUST display list of ignored API patterns | Must |
| AC-7.3 | User MUST be able to add new patterns | Must |
| AC-7.4 | User MUST be able to remove existing patterns | Must |
| AC-7.5 | Patterns MUST support wildcards (e.g., /api/health/*) | Should |
| AC-7.6 | Changes MUST persist to tools.json | Must |

### 8. API Integration

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-8.1 | Dashboard MUST call `GET /api/tracing/status` on load | Must |
| AC-8.2 | Starting tracing MUST call `POST /api/tracing/start` | Must |
| AC-8.3 | Stopping tracing MUST call `POST /api/tracing/stop` | Must |
| AC-8.4 | Trace list MUST call `GET /api/tracing/logs` | Must |
| AC-8.5 | API errors MUST display user-friendly error messages | Must |
| AC-8.6 | Loading states MUST show appropriate indicators | Should |

---

## Functional Requirements

### FR-1: Workplace Tracing View

**Description:** Add Tracing as a new view in Workplace sidebar.

**Input:** User clicks "Tracing" in Workplace sidebar

**Process:**
1. Register "Tracing" view in Workplace navigation
2. Load TracingDashboard component
3. Fetch tracing status from API
4. Render dashboard with current state

**Output:** Tracing Dashboard displayed in main content area

### FR-2: Duration-Based Tracing Start

**Description:** Start tracing with selected duration preset.

**Input:** User clicks duration button (3 min, 15 min, or 30 min)

**Process:**
1. Calculate stop time: `now + duration`
2. Call `POST /api/tracing/start` with `duration_minutes`
3. Update UI to show active state
4. Start countdown timer
5. Store `tracing_stop_at` in tools.json (via API)

**Output:** Tracing active, countdown timer running

### FR-3: Countdown Timer Display

**Description:** Show live countdown of remaining tracing time.

**Input:** Tracing session active with `tracing_stop_at` set

**Process:**
1. Calculate remaining: `tracing_stop_at - now`
2. Update display every second
3. Change color based on remaining time
4. When remaining <= 0, trigger auto-stop

**Output:** MM:SS display updating in real-time

### FR-4: Tracing Session Persistence

**Description:** Maintain tracing state across page navigation.

**Input:** Page load or refresh

**Process:**
1. Call `GET /api/tracing/status`
2. If `tracing_stop_at` is set and > now:
   - Resume countdown timer
   - Show active state
3. If `tracing_stop_at` is null or < now:
   - Show inactive state
   - Clear any stale UI

**Output:** Dashboard reflects actual tracing state

### FR-5: Trace List Fetching

**Description:** Display list of captured trace logs.

**Input:** Dashboard loaded or refresh triggered

**Process:**
1. Call `GET /api/tracing/logs`
2. Parse response: `[{ trace_id, api, timestamp, size, has_error }]`
3. Sort by timestamp (newest first)
4. Render list items with status indicators

**Output:** Scrollable list of trace entries

### FR-6: Config Management

**Description:** Allow users to configure tracing settings.

**Input:** User opens Config modal

**Process:**
1. Fetch current config from `GET /api/tracing/status`
2. Display form with current values
3. On Save: `POST /api/tracing/config` with updated values
4. Close modal and show success toast

**Output:** Updated tracing configuration

### FR-7: Ignored APIs Management

**Description:** Allow users to manage ignored API patterns.

**Input:** User opens Ignored APIs modal

**Process:**
1. Fetch patterns from tools.json `tracing_ignored_apis` field
2. Display editable list
3. Allow add/remove operations
4. On Save: Update tools.json via API

**Output:** Updated ignored APIs list

---

## Non-Functional Requirements

### NFR-1: Performance

| Metric | Target |
|--------|--------|
| Dashboard load time | < 500ms |
| Countdown timer accuracy | ± 100ms |
| Trace list refresh | < 1s for 100 entries |
| API response handling | < 200ms |

### NFR-2: Usability

| Requirement | Implementation |
|-------------|----------------|
| Keyboard shortcuts | ESC to close modals |
| Touch support | Buttons sized for touch targets |
| Visual feedback | Loading spinners, success toasts |
| Error handling | Clear error messages |

### NFR-3: Accessibility

| Requirement | Implementation |
|-------------|----------------|
| Screen reader | ARIA labels on buttons and timer |
| Color contrast | WCAG AA compliance |
| Focus management | Logical tab order |

---

## Dependencies

### Internal Dependencies

| Feature | Dependency Type | What It Provides |
|---------|-----------------|------------------|
| FEATURE-023-A | Required | Tracing API endpoints (`/api/tracing/*`) |
| FEATURE-008 | Required | Workplace framework and sidebar navigation |

### External Dependencies

| Library | Purpose | CDN/Package |
|---------|---------|-------------|
| None | Dashboard uses vanilla JS | N/A |

---

## UI/UX Requirements

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER                                                          │
│ ┌─────────┐  ┌────────┐ ┌─────────────┐  ┌──────┐ ┌──────────┐ │
│ │ Tracing │  │ Config │ │Ignored APIs │  │ 3min │ │ 15min    │ │
│ └─────────┘  └────────┘ └─────────────┘  └──────┘ └──────────┘ │
│                                                                 │
│ ┌──────────┐  ┌────────────────────────┐                       │
│ │ 30min    │  │ ⏱️ 12:34 remaining     │  [Stop]               │
│ └──────────┘  └────────────────────────┘                       │
├─────────────────────────────────────────────────────────────────┤
│ MAIN CONTENT                                                    │
│ ┌──────────────────┬────────────────────────────────────────┐  │
│ │ TRACE LIST       │ DETAIL PANEL (FEATURE-023-C)           │  │
│ │                  │                                        │  │
│ │ 🟢 POST /api/... │ (Select a trace to view)               │  │
│ │    550e84..      │                                        │  │
│ │    10:30:15      │                                        │  │
│ │                  │                                        │  │
│ │ 🔴 GET /api/...  │                                        │  │
│ │    a7b3c2..      │                                        │  │
│ │    10:28:42      │                                        │  │
│ │                  │                                        │  │
│ └──────────────────┴────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### UI Elements

| Element | Type | Behavior |
|---------|------|----------|
| Duration buttons | Button group | Toggle selection, start tracing |
| Countdown timer | Text display | Updates every second |
| Stop button | Danger button | Stops tracing immediately |
| Config button | Icon button | Opens config modal |
| Ignored APIs button | Icon button | Opens ignored APIs modal |
| Trace list | List/Table | Selectable, scrollable |
| Status indicator | Icon (colored dot) | Green=success, Red=error |

### Color Scheme

| State | Color | Usage |
|-------|-------|-------|
| Active/Success | Green (#22c55e) | Timer active, success traces |
| Warning | Yellow (#eab308) | Timer < 1 minute |
| Error | Red (#ef4444) | Error traces |
| Inactive | Gray (#9ca3af) | Timer inactive |
| Selected | Blue (#3b82f6) | Selected trace item |

### Empty States

| State | Display |
|-------|---------|
| No traces | "No traces captured. Start tracing to begin." |
| Tracing inactive | Timer shows "00:00" in gray |

---

## Business Rules

### BR-1: Tracing Duration Exclusivity

**Rule:** Only one tracing duration can be active at a time. Starting a new duration replaces the previous one.

**Example:** If 30 min is active and user clicks 15 min, timer resets to 15 minutes.

### BR-2: Automatic Stop on Countdown End

**Rule:** When countdown reaches zero, tracing must stop automatically and `tracing_stop_at` must be cleared.

### BR-3: Manual Stop Clears Timer

**Rule:** Clicking Stop must immediately stop tracing and clear the countdown, regardless of remaining time.

### BR-4: Trace List Ordering

**Rule:** Traces must be displayed newest-first (descending by timestamp).

---

## Edge Cases & Constraints

### EC-1: Page Refresh During Active Tracing

**Scenario:** User refreshes page while tracing is active with 5 minutes remaining.
**Expected:** Dashboard loads, detects active session from API, resumes countdown.

### EC-2: Network Error During Start

**Scenario:** User clicks duration button but API call fails.
**Expected:** Show error toast, remain in inactive state, don't start timer.

### EC-3: Very Old Tracing Session

**Scenario:** `tracing_stop_at` in tools.json is from yesterday.
**Expected:** Treat as inactive, clear stale timestamp.

### EC-4: Many Traces (100+)

**Scenario:** Trace list has hundreds of entries.
**Expected:** List scrolls smoothly, pagination or virtual scrolling if needed.

### EC-5: Backend Unavailable

**Scenario:** Tracing API returns 500 error.
**Expected:** Show error message, disable controls, retry button.

---

## Out of Scope

- **Trace content visualization** (FEATURE-023-C handles DAG view)
- **Real-time trace streaming** (deferred to future version)
- **Trace export/download** (deferred to future version)
- **Multiple trace selection** (single selection only for v1)
- **Trace filtering/search** (deferred to future version)

---

## Technical Considerations

### Frontend Implementation

- Use existing Workplace view registration pattern
- Vanilla JavaScript (consistent with X-IPE codebase)
- CSS following X-IPE design system
- Timer uses `setInterval` with cleanup on unmount

### API Contract

```javascript
// GET /api/tracing/status
{
  "enabled": true,
  "stop_at": "2026-02-01T04:30:00Z",  // ISO timestamp or null
  "retention_hours": 24,
  "log_path": "instance/traces/"
}

// POST /api/tracing/start
Request: { "duration_minutes": 15 }
Response: { "stop_at": "2026-02-01T04:30:00Z" }

// POST /api/tracing/stop
Response: { "success": true }

// GET /api/tracing/logs
[
  {
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "api": "POST /api/orders",
    "timestamp": "2026-02-01T04:15:30Z",
    "size": 2048,
    "has_error": false
  }
]
```

### State Management

- Timer state managed in component
- Tracing state fetched from API on load
- Config changes trigger immediate save

---

## Open Questions

- [x] Should trace list auto-refresh? → Yes, polling every 5 seconds when tracing active
- [x] Keyboard shortcuts for start/stop? → Defer to v2
- [ ] Should we show trace file size in list? (Nice to have)
- [ ] Max traces to display before pagination? (100 for v1)

---
