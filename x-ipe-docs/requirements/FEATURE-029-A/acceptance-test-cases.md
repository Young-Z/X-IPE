# Acceptance Test Cases: Session Explorer Core

> Feature ID: FEATURE-029-A
> Version: v1.0
> Test Date: 02-11-2026
> Tester: Spark (Agent)
> Target URL: http://localhost:18080/

## Test Summary

| ID | Test Case | AC | Priority | Status | Notes |
|----|-----------|-----|----------|--------|-------|
| TC-001 | Explorer panel renders on right side | AC-029-A.1 | P0 | ✅ Pass | #session-explorer exists, width=220px, right of #terminal-content |
| TC-002 | Session bar shows session name | AC-029-A.1 | P0 | ✅ Pass | 1 bar with "Session 1" on load |
| TC-003 | "+" button visible in explorer | AC-029-A.2 | P0 | ✅ Pass | #explorer-add-btn visible, not disabled |
| TC-004 | Click "+" creates new session | AC-029-A.2 | P0 | ✅ Pass | 2 bars after click, Session 2 active |
| TC-005 | New session gets default name | AC-029-A.2 | P1 | ✅ Pass | Sequential: Session 1..10 |
| TC-006 | Max 10 sessions enforced | AC-029-A.2 | P1 | ✅ Pass | 10 bars, "+" disabled |
| TC-007 | Only active session visible | AC-029-A.3 | P0 | ✅ Pass | 1 active container with 2 & 10 sessions |
| TC-008 | No split-pane layout | AC-029-A.3 | P0 | ✅ Pass | No .terminal-panes or .pane-splitter in DOM |
| TC-009 | Click session bar switches active | AC-029-A.4 | P0 | ✅ Pass | Session 1 active after clicking its bar |
| TC-010 | Terminal output preserved on switch | AC-029-A.4 | P0 | ✅ Pass | "hello_test_123" visible after round-trip switch |
| TC-011 | Background sessions continue running | AC-029-A.5 | P0 | ✅ Pass | "BG_DONE_MARKER" found after bg exec + switch |
| TC-012 | Default session on load | AC-029-A.6 | P0 | ✅ Pass | 1 bar "Session 1" active on page load |
| TC-013 | Explorer expanded by default | AC-029-A.6 | P1 | ✅ Pass | Width=220px, display=flex |
| TC-014 | Terminal resize works | AC-029-A.7 | P1 | ✅ Pass | FitAddon present, 176cols×15rows |
| TC-015 | Zen mode hides explorer | AC-029-A.7 | P1 | ✅ Pass | display:none in zen, flex after exit |
| TC-016 | Layout matches mockup | AC-029-A.1 | P1 | ✅ Pass | Screenshot verified: right panel, session list, status dots, naming |

## Element Selectors

| Element | Selector | Type |
|---------|----------|------|
| Session Explorer Panel | `#session-explorer` | id |
| Session List | `#session-list` | id |
| Add Button | `#explorer-add-btn` | id |
| Session Bar | `.session-bar` | class |
| Session Bar (by key) | `[data-session-key="sN"]` | data attr |
| Active Session Bar | `.session-bar[data-active="true"]` | class+attr |
| Session Name | `.session-name` | class |
| Session Status Dot | `.session-status-dot` | class |
| Terminal Content | `#terminal-content` | id |
| Terminal Container | `.terminal-session-container` | class |
| Active Container | `.terminal-session-container.active` | class |
| Terminal Panel | `#terminal-panel` | id |
| Zen Button | `#terminal-zen-btn` | id |
| Terminal Body | `#terminal-body` | id |
| Explorer Title | `.explorer-title` | class |

---

## Test Cases

### TC-001: Explorer panel renders on right side
**AC:** AC-029-A.1 | **Priority:** P0

**Steps:**
1. Navigate to http://localhost:18080/
2. Expand console panel (if collapsed)
3. Verify `#session-explorer` element exists
4. Verify explorer is positioned to the right of `#terminal-content`

**Expected:** Explorer panel visible on right side of console.

---

### TC-002: Session bar shows session name
**AC:** AC-029-A.1 | **Priority:** P0

**Steps:**
1. Navigate to page
2. Verify `.session-bar` exists in `#session-list`
3. Verify `.session-name` text is "Session 1"

**Expected:** Session bar displays "Session 1".

---

### TC-003: "+" button visible in explorer
**AC:** AC-029-A.2 | **Priority:** P0

**Steps:**
1. Navigate to page
2. Verify `#explorer-add-btn` exists and is visible
3. Verify button is not disabled

**Expected:** "+" button visible and enabled.

---

### TC-004: Click "+" creates new session
**AC:** AC-029-A.2 | **Priority:** P0

**Steps:**
1. Navigate to page (Session 1 exists)
2. Click `#explorer-add-btn`
3. Wait for new session bar to appear
4. Verify 2 session bars in `#session-list`
5. Verify new session is active (`data-active="true"`)

**Expected:** New session created and becomes active.

---

### TC-005: New session gets default name
**AC:** AC-029-A.2 | **Priority:** P1

**Steps:**
1. Start with Session 1
2. Click "+" to create Session 2
3. Click "+" to create Session 3
4. Verify session names are "Session 1", "Session 2", "Session 3"

**Expected:** Sequential naming pattern.

---

### TC-006: Max 10 sessions enforced
**AC:** AC-029-A.2 | **Priority:** P1

**Steps:**
1. Create 9 additional sessions (total 10)
2. Verify `#explorer-add-btn` is disabled
3. Verify 10 `.session-bar` elements exist

**Expected:** "+" disabled at 10/10.

---

### TC-007: Only active session visible
**AC:** AC-029-A.3 | **Priority:** P0

**Steps:**
1. Create 2 sessions
2. Verify only 1 `.terminal-session-container.active` exists
3. Verify other containers are not active

**Expected:** Single active container.

---

### TC-008: No split-pane layout
**AC:** AC-029-A.3 | **Priority:** P0

**Steps:**
1. Navigate to page
2. Verify `.terminal-panes` does NOT exist
3. Verify `.pane-splitter` does NOT exist

**Expected:** No split-pane DOM elements.

---

### TC-009: Click session bar switches active
**AC:** AC-029-A.4 | **Priority:** P0

**Steps:**
1. Create 2 sessions (Session 2 is active)
2. Click Session 1 bar
3. Verify Session 1 bar has `data-active="true"`
4. Verify Session 2 bar has `data-active="false"`

**Expected:** Active indicator switches.

---

### TC-010: Terminal output preserved on switch
**AC:** AC-029-A.4 | **Priority:** P0

**Steps:**
1. In Session 1, type `echo hello` + Enter
2. Create Session 2
3. Switch back to Session 1
4. Verify "hello" text is visible in terminal

**Expected:** Output preserved after switch.

---

### TC-011: Background sessions continue running
**AC:** AC-029-A.5 | **Priority:** P0

**Steps:**
1. In Session 1, start `sleep 2 && echo done`
2. Switch to Session 2
3. Wait 3 seconds
4. Switch back to Session 1
5. Verify "done" appears in terminal output

**Expected:** Background process completed.

---

### TC-012: Default session on load
**AC:** AC-029-A.6 | **Priority:** P0

**Steps:**
1. Navigate to fresh page (clear localStorage first)
2. Expand console
3. Verify 1 `.session-bar` exists
4. Verify session name is "Session 1"
5. Verify terminal is active

**Expected:** Auto-created "Session 1".

---

### TC-013: Explorer expanded by default
**AC:** AC-029-A.6 | **Priority:** P1

**Steps:**
1. Navigate to page
2. Verify `#session-explorer` is visible (width > 0)

**Expected:** Explorer panel visible on load.

---

### TC-014: Terminal resize works
**AC:** AC-029-A.7 | **Priority:** P1

**Steps:**
1. Navigate to page with active session
2. Resize browser window
3. Verify terminal adapts (no overflow, no scroll bars)

**Expected:** FitAddon resizes terminal.

---

### TC-015: Zen mode hides explorer
**AC:** AC-029-A.7 | **Priority:** P1

**Steps:**
1. Navigate to page
2. Click `#terminal-zen-btn`
3. Verify `#session-explorer` is hidden (display: none)
4. Exit zen mode
5. Verify `#session-explorer` is visible again

**Expected:** Explorer hidden in zen mode.

---

### TC-016: Layout matches mockup
**AC:** AC-029-A.1 | **Priority:** P1 | **Mockup:** console-explorer-v1.html

**Steps:**
1. Navigate to page
2. Take screenshot
3. Compare layout: right-side panel, session list, "+" button placement
4. Verify color scheme, spacing consistent with mockup

**Expected:** Layout matches approved mockup structure.

---

## Execution Results

| ID | Status | Execution Notes |
|----|--------|-----------------|
| TC-001 | ✅ Pass | explorer exists, width=220, positioned right of terminal-content |
| TC-002 | ✅ Pass | 1 session-bar, .session-name="Session 1" |
| TC-003 | ✅ Pass | #explorer-add-btn visible, disabled=false |
| TC-004 | ✅ Pass | barCount=2 after click, Session 2 data-active="true" |
| TC-005 | ✅ Pass | Names: Session 1..Session 10 sequential |
| TC-006 | ✅ Pass | barCount=10, addBtn.disabled=true |
| TC-007 | ✅ Pass | 1 .terminal-session-container.active out of 2 (and 10) |
| TC-008 | ✅ Pass | .terminal-panes=null, .pane-splitter=null |
| TC-009 | ✅ Pass | Session 1 data-active="true", Session 2 data-active="false" after click |
| TC-010 | ✅ Pass | "hello_test_123" found in terminal buffer after switch away and back |
| TC-011 | ✅ Pass | "BG_DONE_MARKER" found after `sleep 2 && echo` ran while in Session 2 |
| TC-012 | ✅ Pass | 1 bar "Session 1" data-active="true" on page load |
| TC-013 | ✅ Pass | explorer width=220, display=flex on load |
| TC-014 | ✅ Pass | fitAddon present, terminal 176×15, fit() succeeds |
| TC-015 | ✅ Pass | zen: display=none, exit zen: display=flex |
| TC-016 | ✅ Pass | Screenshot matches mockup: right panel, session list, dots, "+" button |

## Mockup Validation Summary

| Mockup | Status | Deviations |
|--------|--------|------------|
| console-explorer-v1.html | ✅ Match | Header says "SESSIONS" (mockup uses "Sessions") — minor capitalization. Layout, session bars, status dots, "+" button all match structure. |

## Metrics

- **Total Test Cases:** 16
- **Passed:** 16
- **Failed:** 0
- **Blocked:** 0
- **Pass Rate:** 100%
