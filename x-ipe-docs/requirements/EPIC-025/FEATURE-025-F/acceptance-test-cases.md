# Acceptance Test Cases

> Feature: FEATURE-025-F - KB Navigation & Polish
> Generated: 03-03-2026
> Status: Blocked (Chrome DevTools MCP unavailable)

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-025-F |
| Feature Title | KB Navigation & Polish |
| Total Test Cases | 10 |
| Priority | P0 (Critical) / P1 (High) / P2 (Medium) |
| Target URL | http://localhost:5858/ → Workplace → Knowledge Base |

---

## Prerequisites

- [x] Feature is deployed and accessible
- [x] Test environment is ready
- [ ] Chrome DevTools MCP is available — **BLOCKED** (browser instance from another session)

---

## Test Cases

### TC-001: Section Tabs Render on KB Load

**Acceptance Criteria Reference:** AC-1.1, AC-1.2, AC-1.3, AC-1.4

**Priority:** P0

**Preconditions:**
- App running on localhost:5858
- User on Workplace page

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5858/ | Page loads |
| 2 | Click | `[data-action="knowledge-base"]` | - | KB panel loads |
| 3 | Verify | `#kb-section-tabs` | - | Section tabs container exists between header and search |
| 4 | Verify | `.kb-section-tab[data-tab="landing"]` | - | Landing tab with bi-inbox icon and "Landing" text |
| 5 | Verify | `.kb-section-tab[data-tab="topics"]` | - | Topics tab with bi-layers icon and "Topics" text |
| 6 | Verify | `.kb-section-tab` count | - | Exactly 2 tab buttons exist |

**Expected Outcome:** Two section tabs ("Landing" and "Topics") visible in sidebar with correct icons

**Status:** ⬜ Not Run

---

### TC-002: Tab Badges Show Correct Counts

**Acceptance Criteria Reference:** AC-2.1, AC-2.2

**Priority:** P0

**Preconditions:**
- KB loaded with known number of landing files and topics

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to KB | - | - | KB loads |
| 2 | Verify | `#kb-badge-landing` | - | Badge text = count of files in landing/ |
| 3 | Verify | `#kb-badge-topics` | - | Badge text = count of topics |
| 4 | Verify | `.kb-tab-badge` | - | Badges are pill-shaped (border-radius: 10px) |

**Expected Outcome:** Both badges show accurate counts

**Status:** ⬜ Not Run

---

### TC-003: Landing Tab Active by Default (No Topics)

**Acceptance Criteria Reference:** AC-6.2

**Priority:** P0

**Preconditions:**
- KB has no topics (empty topics list)

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to KB | - | - | KB loads |
| 2 | Verify | `.kb-section-tab.active` | - | Landing tab has .active class |
| 3 | Verify | `#kb-tree .kb-folder` | - | Only landing folder visible |

**Expected Outcome:** Landing tab is selected by default when no topics exist

**Status:** ⬜ Not Run

---

### TC-004: Topics Tab Active by Default (Topics Exist)

**Acceptance Criteria Reference:** AC-6.1

**Priority:** P0

**Preconditions:**
- KB has at least 1 topic

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to KB | - | - | KB loads |
| 2 | Verify | `.kb-section-tab[data-tab="topics"].active` | - | Topics tab has .active class |
| 3 | Verify | `#kb-tree .kb-folder` | - | Only topic folders visible in tree |

**Expected Outcome:** Topics tab is selected by default when topics exist

**Status:** ⬜ Not Run

---

### TC-005: Click Landing Tab Switches View

**Acceptance Criteria Reference:** AC-3.1, AC-3.3, AC-3.4

**Priority:** P0

**Preconditions:**
- KB loaded, Topics tab currently active

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Verify | `.kb-section-tab[data-tab="topics"]` | - | Topics tab is active (accent bg, white text) |
| 2 | Click | `.kb-section-tab[data-tab="landing"]` | - | Tab click registered |
| 3 | Verify | `.kb-section-tab[data-tab="landing"].active` | - | Landing tab now has .active class |
| 4 | Verify | `.kb-section-tab[data-tab="topics"]` | - | Topics tab no longer has .active class |
| 5 | Verify | `#kb-tree` | - | Tree shows only landing folder/files |
| 6 | Verify | `#kb-content` | - | Content panel shows Landing view (kbLanding) |

**Expected Outcome:** Clicking Landing tab switches sidebar tree and content panel to landing view

**Status:** ⬜ Not Run

---

### TC-006: Click Topics Tab Switches View

**Acceptance Criteria Reference:** AC-3.2

**Priority:** P0

**Preconditions:**
- KB loaded, Landing tab currently active

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Click | `.kb-section-tab[data-tab="topics"]` | - | Tab click registered |
| 2 | Verify | `.kb-section-tab[data-tab="topics"].active` | - | Topics tab has .active class |
| 3 | Verify | `#kb-tree` | - | Tree shows topic folders only |
| 4 | Verify | `#kb-content` | - | Content panel shows Topics view (kbTopics) |

**Expected Outcome:** Clicking Topics tab switches sidebar tree and content panel to topics view

**Status:** ⬜ Not Run

---

### TC-007: Tab Hover Effect

**Acceptance Criteria Reference:** AC-5.1, AC-5.2, AC-5.3

**Priority:** P1

**Preconditions:**
- KB loaded

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Hover | `.kb-section-tab:not(.active)` | - | Background changes to var(--bg-hover) |
| 2 | Verify | CSS transition | - | 150ms transition applied |

**Expected Outcome:** Inactive tabs show hover highlight with smooth transition

**Status:** ⬜ Not Run

---

### TC-008: Tree Filtering by Active Tab

**Acceptance Criteria Reference:** AC-4.1, AC-4.2

**Priority:** P0

**Preconditions:**
- KB has both landing files and topic files

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Click | `.kb-section-tab[data-tab="landing"]` | - | Switch to landing |
| 2 | Verify | `#kb-tree .kb-folder` | - | Only landing/ folder shown, no topic folders |
| 3 | Click | `.kb-section-tab[data-tab="topics"]` | - | Switch to topics |
| 4 | Verify | `#kb-tree .kb-folder` | - | Only topic folders shown, no landing folder |

**Expected Outcome:** Sidebar tree displays only the files/folders belonging to the active tab's section

**Status:** ⬜ Not Run

---

### TC-009: Folder Toggle Works in Both Tabs

**Acceptance Criteria Reference:** AC-4.4

**Priority:** P1

**Preconditions:**
- KB has files in both sections

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Click | `.kb-folder-header` (in landing tab) | - | Folder collapses, chevron changes to right |
| 2 | Click same | `.kb-folder-header` | - | Folder expands, chevron changes to down |
| 3 | Switch tab | `.kb-section-tab[data-tab="topics"]` | - | Topics tab active |
| 4 | Click | `.kb-folder-header` (topic folder) | - | Topic folder collapses/expands |

**Expected Outcome:** Folder toggle (collapse/expand) works in both Landing and Topics tree views

**Status:** ⬜ Not Run

---

### TC-010: Mockup Visual Comparison

**Acceptance Criteria Reference:** AC-1.5, AC-1.6, AC-2.4

**Priority:** P1

**Preconditions:**
- KB loaded with section tabs visible
- Mockup file: mockups/knowledge-base-v1.html

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Screenshot | KB sidebar with tabs | - | Capture current UI |
| 2 | Open mockup | knowledge-base-v1.html | - | Reference mockup visible |
| 3 | Compare | Section tabs area | - | Tab layout matches: flex, equal width, 6px radius |
| 4 | Compare | Active tab style | - | Accent bg color, white text, matching mockup |
| 5 | Compare | Badge style | - | Pill shape, 10px font, semi-transparent bg |
| 6 | Compare | Spacing/padding | - | 8px/12px padding, 4px gap between tabs |

**Expected Outcome:** Section tabs UI matches the approved mockup design

**Status:** ⬜ Not Run

---

## Test Execution Summary

| Test Case | Title | Priority | Status | Notes |
|-----------|-------|----------|--------|-------|
| TC-001 | Section Tabs Render | P0 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-002 | Tab Badges Counts | P0 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-003 | Landing Default (No Topics) | P0 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-004 | Topics Default (Topics Exist) | P0 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-005 | Click Landing Tab | P0 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-006 | Click Topics Tab | P0 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-007 | Tab Hover Effect | P1 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-008 | Tree Filtering by Tab | P0 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-009 | Folder Toggle Both Tabs | P1 | ⬜ Not Run | Blocked: MCP unavailable |
| TC-010 | Mockup Visual Comparison | P1 | ⬜ Not Run | Blocked: MCP unavailable |

---

## Execution Results

**Execution Date:** 03-03-2026
**Executed By:** Nova ✨
**Environment:** dev (localhost:5858)

| Metric | Value |
|--------|-------|
| Total Tests | 10 |
| Passed | 0 |
| Failed | 0 |
| Blocked | 10 |
| Pass Rate | N/A |

### Blocked Reason

Chrome DevTools MCP is unavailable — browser instance already running from another session. All 10 test cases are ready for manual execution or re-run when MCP becomes available.

### Unit Test Coverage

All 27 TDD unit tests pass (Vitest + jsdom): section tabs rendering, tab switching, badge counts, tree filtering, default tab selection, and edge cases are fully validated at the unit test level.

---

## Notes

- Chrome DevTools MCP blocked by existing browser session — tests documented for manual execution
- 27/27 unit tests pass, covering all acceptance criteria at the code level
- No regressions in full test suite (382/383 pass, 1 pre-existing unrelated failure)
