# Acceptance Test Cases: Explorer UI Controls

> Feature ID: FEATURE-029-D
> Version: v1.1 (CR-001: Border Toggle)
> Executed: 03-16-2026
> Executor: Ember 🔥 (automated via Chrome DevTools MCP + vitest)

## Test Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 25 |
| Passed | 25 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

## v1.0 Test Results (previously passed 02-12-2026)

### Toggle & Collapse

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-01 | AC-1 | Toggle button in terminal header collapses/expands explorer | ✅ Pass | `#terminal-explorer-toggle` exists and toggles `.collapsed` class |
| TC-02 | AC-2 | Collapsed state: width=0, visibility=hidden, terminal full width | ✅ Pass | Verified: width=0px, visibility=hidden, class=collapsed |

### Drag-to-Resize

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-03 | AC-3 | 5px vertical drag handle between terminal and explorer | ✅ Pass | `#explorer-resize-handle` exists, computed width=5px |
| TC-04 | AC-4 | Drag left increases width, drag right decreases | ✅ Pass | Simulated drag to 300px — explorer width changed from 220→300px |
| TC-05 | AC-5 | Width clamped to [160, 360]px | ✅ Pass | Min clamp: 50px target → 160px stored. Max clamp: 500px target → 360px stored |
| TC-06 | AC-6 | col-resize cursor on handle | ✅ Pass | Computed cursor = `col-resize` |
| TC-07 | AC-7 | Handle highlights on hover | ✅ Pass | CSS rule verified. Hover accent + dot indicator present |
| TC-08 | AC-8 | Terminal re-fits after drag ends | ✅ Pass | `fitActive()` called in mouseup handler |

### Persistence

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-10 | AC-10 | Width saved to localStorage after resize | ✅ Pass | `console_explorer_width` = "300" after drag to 300px |
| TC-11 | AC-11 | Collapsed state saved after toggle | ✅ Pass | `console_explorer_collapsed` = "true" after collapse |
| TC-12 | AC-12 | Width restored from localStorage on reload | ✅ Pass | Set 250px, reloaded, computed width = 250px |
| TC-13 | AC-13 | Collapsed state restored on reload | ✅ Pass | Set collapsed=true, reloaded, explorer has .collapsed class |
| TC-14 | AC-14 | Default 220px when no localStorage | ✅ Pass | Initial load with no stored value = 220px |

### Session Identity Persistence

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-15 | AC-15 | Session names stored as UUID→name JSON map | ✅ Pass | `terminal_session_names` contains map |
| TC-16 | AC-16 | Session names restored on reload | ✅ Pass | Names restored from localStorage |

### Mockup Compliance

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-17 | AC-17 | Handle styling matches mockup | ✅ Pass | 5px width, accent hover, dot indicator |
| TC-18 | AC-18 | Collapse transition matches mockup | ✅ Pass | width 0.25s ease transition verified |

---

## v1.1 CR-001 Tests (Border Toggle)

### Unit Tests (vitest)

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-U01 | AC-19 | Click to collapse (mousedown+mouseup, no movement) | ✅ Pass | vitest: explorerVisible=false, .collapsed added |
| TC-U02 | AC-20 | Click collapsed handle to expand | ✅ Pass | vitest: explorerVisible=true, .collapsed removed |
| TC-U03 | AC-21 | Click expanded handle → collapse to 0 | ✅ Pass | vitest: .collapsed class, width=0 |
| TC-U04 | AC-22 | Handle gets .collapsed class (controls chevron via CSS) | ✅ Pass | vitest: handle.classList.contains('collapsed') |
| TC-U05 | AC-23 | Persist collapsed state on border click | ✅ Pass | vitest: localStorage 'console_explorer_collapsed'='true' |
| TC-U06 | AC-24 | Drag (≥3px) resizes, doesn't toggle | ✅ Pass | vitest: width changed, explorerVisible=true |
| TC-U07 | AC-25 | Restore handle .collapsed class on page load | ✅ Pass | vitest: handle.classList.contains('collapsed'), no display:none |
| TC-U08 | AC-9 | Handle NOT display:none when collapsed | ✅ Pass | vitest: handle.style.display != 'none' |
| TC-U09 | EC-7 | Animation guard prevents rapid toggle | ✅ Pass | vitest: second toggle ignored within 300ms |
| TC-U10 | EC-9 | Touch tap toggles explorer | ✅ Pass | vitest: touchstart→touchend fires toggle |
| TC-U11 | EC-9 | Touch with movement doesn't toggle | ✅ Pass | vitest: 10px touchmove → no toggle |
| TC-U12 | AC-12 | Width restored from localStorage | ✅ Pass | vitest: stored 250 → panel.explorerWidth=250 |
| TC-U13 | AC-14 | Default 220px when no stored value | ✅ Pass | vitest: explorerWidth=220 |
| TC-U14 | AC-10 | Drag saves width to localStorage | ✅ Pass | vitest: localStorage='310' after drag |
| TC-U15 | AC-20 | Expand restores previous width from localStorage | ✅ Pass | vitest: stored 300→collapse→expand→width=300px |
| TC-U16 | AC-23 | Expand persists 'false' to localStorage | ✅ Pass | vitest: localStorage='false' after re-expand |
| TC-U17 | AC-9 | Drag disabled when collapsed | ✅ Pass | vitest: collapsed handle drag doesn't resize |
| TC-U18 | AC-22 | Collapsed class removed from handle on expand | ✅ Pass | vitest: handle.classList.contains('collapsed')=false |

### Frontend-UI Tests (Chrome DevTools MCP)

| TC | AC | Description | Priority | Status | Notes |
|----|-----|-------------|----------|--------|-------|
| TC-B01 | AC-9 | Handle visible when collapsed (CR-001) | P0 | ✅ Pass | display=block, .collapsed class, cursor=pointer |
| TC-B02 | AC-19 | Click handle to collapse explorer | P0 | ✅ Pass | mousedown+mouseup → .collapsed added, explorerVisible=false |
| TC-B03 | AC-20 | Click collapsed handle to expand | P0 | ✅ Pass | width=220px, visibility=visible, cursor=col-resize |
| TC-B04 | AC-22 | Chevron `‹` expanded, `›` collapsed | P0 | ✅ Pass | expanded: content='‹' opacity=0; collapsed: content='›' opacity=1 |
| TC-B05 | AC-24 | Drag preserves resize behavior | P1 | ✅ Pass | Drag 50px left → width 220→266px, still expanded |
| TC-B06 | AC-23 | Persistence survives page reload | P1 | ✅ Pass | Collapsed state restored after reload, width=0px |
| TC-B07 | AC-9 | TC-09 regression: handle no longer display:none | P0 | ✅ Pass | handle.style.display !== 'none', computed display=block |

---

## Edge Cases Tested

| # | Scenario | Result | Notes |
|---|----------|--------|-------|
| 1 | localStorage unavailable | ✅ Pass | All localStorage ops wrapped in try/catch |
| 2 | Stored width outside range (999) | ✅ Pass | Clamped to 360px on load |
| 3 | Stored collapsed not boolean ("garbage") | ✅ Pass | Defaults to expanded (only "true" triggers collapse) |
| 7 | Animation guard — rapid clicks | ✅ Pass | Second toggle ignored within 300ms (vitest) |
| 8 | Fast click during transition | ✅ Pass | _toggleAnimating flag prevents re-entry (vitest) |
| 9 | Touch tap toggle | ✅ Pass | touchstart→touchend without movement fires toggle (vitest) |

---

## Execution Results

**Execution Date:** 03-16-2026
**Executed By:** Ember 🔥
**Environment:** dev (localhost:5858)

| Metric | Value |
|--------|-------|
| Total Tests | 25 |
| Passed | 25 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Type | Passed | Failed | Blocked | Total |
|------|--------|--------|---------|-------|
| unit (vitest) | 18 | 0 | 0 | 18 |
| frontend-ui (Chrome MCP) | 7 | 0 | 0 | 7 |

---

## Mockup Validation Summary

| Aspect | Mockup | Implementation | Match |
|--------|--------|---------------|-------|
| Handle width | 5px | 5px | ✅ |
| Handle background | var(--border-subtle) | #333 | ✅ (theme equivalent) |
| Handle hover | var(--accent-dim) | rgba(78,201,176,0.3) | ✅ |
| Chevron `‹` (expanded, on hover) | ::before content '‹' | CSS ::before content '‹', opacity 0→1 on hover | ✅ |
| Chevron `›` (collapsed, always) | ::before content '›' | CSS .collapsed::before content '›', opacity 1 | ✅ |
| Handle cursor (collapsed) | pointer | .collapsed { cursor: pointer } | ✅ |
| Collapse transition | 0.25s ease | 0.25s ease | ✅ |
| Width range | [160, 360] | [160, 360] | ✅ |
