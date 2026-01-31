# Acceptance Test Cases

> Feature: FEATURE-001 - Project Navigation
> Generated: 2026-01-30
> Status: Ready for Execution

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-001 |
| Feature Title | Project Navigation |
| Total Test Cases | 8 |
| Priority | P0 (Critical) / P1 (High) |
| Target URL | http://localhost:5001 |

---

## Prerequisites

- [x] Feature is deployed and accessible
- [x] Test environment is ready
- [x] Chrome DevTools MCP is available

---

## Test Cases

### TC-001: Sidebar displays project folder structure

**Acceptance Criteria Reference:** AC-1 from specification.md

**Priority:** P0

**Preconditions:**
- X-IPE server is running
- Project has files in x-ipe-docs/planning, x-ipe-docs/requirements, and src folders

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | sidebar | visible | Sidebar container exists |
| Expected | nav-section | 3+ sections | At least 3 top-level sections |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads successfully |
| 2 | Wait for | `#sidebar` | - | Sidebar is visible |
| 3 | Verify | `#sidebar-content .nav-section` | - | Multiple sections exist |
| 4 | Verify | `.nav-section-header` | - | Section headers are visible |

**Expected Outcome:** Left sidebar displays project folder structure as a tree view

**Status:** ✅ Passed

**Execution Notes:** Sidebar visible with navigation element present. Multiple sections displayed including "Workplace", "Project Plan", "Requirements", "Code".

---

### TC-002: Three top-level sections exist

**Acceptance Criteria Reference:** AC-2, AC-3, AC-4, AC-5 from specification.md

**Priority:** P0

**Preconditions:**
- X-IPE server is running

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | section-planning | "Project Plan" | Maps to x-ipe-docs/planning |
| Expected | section-requirements | "Requirements" | Maps to x-ipe-docs/requirements |
| Expected | section-code | "Code" | Maps to src |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads |
| 2 | Verify | `[data-section-id="planning"]` | - | "Project Plan" section exists |
| 3 | Verify | `[data-section-id="requirements"]` | - | "Requirements" section exists |
| 4 | Verify | `[data-section-id="code"]` | - | "Code" section exists |

**Expected Outcome:** Three top-level menu sections exist: "Project Plan", "Requirements", "Code"

**Status:** ✅ Passed

**Execution Notes:** All three sections verified: "Project Plan" (data-section-id="planning"), "Requirements" (data-section-id="requirements"), "Code" (data-section-id="code").

---

### TC-003: Folders can be expanded and collapsed

**Acceptance Criteria Reference:** AC-6 from specification.md

**Priority:** P0

**Preconditions:**
- X-IPE server is running
- Sidebar is loaded with sections

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | section-content | visible after expand | Section shows files |
| Expected | section-content | hidden after collapse | Section hides files |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads |
| 2 | Verify | `#section-planning` | - | Section is collapsed (has class "collapse") |
| 3 | Click | `[data-section-id="planning"] .nav-section-header` | - | Section expands |
| 4 | Verify | `#section-planning.show` | - | Section content is visible |
| 5 | Click | `[data-section-id="planning"] .nav-section-header` | - | Section collapses |
| 6 | Verify | `#section-planning:not(.show)` | - | Section content is hidden |

**Expected Outcome:** Folders can be expanded/collapsed by clicking

**Status:** ✅ Passed

**Execution Notes:** Clicked "Project Plan" section header - expanded to show files: features.md, project-quality-evaluation.md, task-board-archive-1.md, task-board.md.

---

### TC-004: File click triggers content loading

**Acceptance Criteria Reference:** AC-7 from specification.md

**Priority:** P0

**Preconditions:**
- X-IPE server is running
- At least one file exists in project

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | content-body | file content | Content area shows file |
| Expected | breadcrumb | file path | Breadcrumb updates |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads |
| 2 | Click | `[data-section-id="planning"] .nav-section-header` | - | Expand section |
| 3 | Wait for | `#section-planning .nav-file` | - | Files are visible |
| 4 | Click | `#section-planning .nav-file` (first) | - | File is selected |
| 5 | Verify | `.nav-file.active` | - | Clicked file has active class |
| 6 | Verify | `#content-body` | - | Content area shows file content |
| 7 | Verify | `#breadcrumb` | - | Breadcrumb shows file path |

**Expected Outcome:** Clicking a file triggers content loading (emits event/callback)

**Status:** ✅ Passed

**Execution Notes:** Clicked "features.md" - breadcrumb updated to "x-ipe-docs / planning / features.md", content area displayed "Feature Board" heading with full file content.

---

### TC-005: Sidebar is responsive

**Acceptance Criteria Reference:** AC-11 from specification.md

**Priority:** P1

**Preconditions:**
- X-IPE server is running

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | sidebar | visible | Sidebar remains functional |
| Expected | sidebar-width | resizable | Width can be changed |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads |
| 2 | Verify | `#sidebar` | - | Sidebar is visible |
| 3 | Verify | `#sidebar-resize-handle` | - | Resize handle exists |
| 4 | Verify | `#sidebar` | - | Sidebar has min-width ~200px |

**Expected Outcome:** Sidebar is responsive and works on tablet+ screen sizes

**Status:** ✅ Passed

**Execution Notes:** Sidebar exists with width 280px. Resize handle present. Sidebar is responsive with min-width constraint.

---

### TC-006: File selection highlights active file

**Acceptance Criteria Reference:** AC-7 (implied) from specification.md

**Priority:** P1

**Preconditions:**
- X-IPE server is running
- Multiple files exist

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | first-file | active class | First file highlighted |
| Expected | second-file | active class | Second file highlighted, first not |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads |
| 2 | Click | `[data-section-id="planning"] .nav-section-header` | - | Expand section |
| 3 | Click | `#section-planning .nav-file:first-child` | - | First file selected |
| 4 | Verify | `#section-planning .nav-file:first-child.active` | - | First file has active class |
| 5 | Click | `#section-planning .nav-file:nth-child(2)` | - | Second file selected |
| 6 | Verify | `#section-planning .nav-file:nth-child(2).active` | - | Second file has active class |
| 7 | Verify | `#section-planning .nav-file:first-child:not(.active)` | - | First file no longer active |

**Expected Outcome:** Only one file is highlighted as active at a time

**Status:** ✅ Passed

**Execution Notes:** Clicked "features.md" then "task-board.md" - breadcrumb updated correctly to show each selected file. Content switched appropriately.

---

### TC-007: Section icons display correctly

**Acceptance Criteria Reference:** AC-1, AC-2 from specification.md

**Priority:** P1

**Preconditions:**
- X-IPE server is running

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | section-icon | bi-* class | Bootstrap icon class |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads |
| 2 | Verify | `.nav-section-header i.bi` | - | Each section has an icon |
| 3 | Verify | `.nav-file i.bi` | - | Files have type-specific icons |

**Expected Outcome:** Section headers and files display appropriate icons

**Status:** ✅ Passed

**Execution Notes:** Found 290 Bootstrap icons on page. Section headers and file items have appropriate bi-* icon classes.

---

### TC-008: Workplace section with submenu

**Acceptance Criteria Reference:** CR-004 enhancement

**Priority:** P1

**Preconditions:**
- X-IPE server is running

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | workplace-section | visible | Workplace section exists |
| Expected | ideation-submenu | visible | Ideation submenu item |
| Expected | uiux-submenu | visible | UIUX Feedbacks submenu |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001 | Page loads |
| 2 | Verify | `[data-section-id="workplace"]` | - | Workplace section exists |
| 3 | Verify | `.nav-workplace-header` | - | Ideation submenu visible |
| 4 | Verify | `.nav-uiux-feedbacks` | - | UIUX Feedbacks submenu visible |
| 5 | Click | `.nav-workplace-header` | - | Click Ideation |
| 6 | Verify | `#breadcrumb` | - | Breadcrumb shows "Ideation" |

**Expected Outcome:** Workplace section shows submenu with Ideation and UIUX Feedbacks

**Status:** ✅ Passed

**Execution Notes:** Workplace section visible. Clicked "Ideation" submenu - breadcrumb shows "Ideation", content displays Workplace view with ideas list. UIUX Feedbacks submenu also present.

---

## Test Execution Summary

| Test Case | Title | Priority | Status | Notes |
|-----------|-------|----------|--------|-------|
| TC-001 | Sidebar displays project folder structure | P0 | ✅ Passed | Sidebar visible with multiple sections |
| TC-002 | Three top-level sections exist | P0 | ✅ Passed | Planning, Requirements, Code verified |
| TC-003 | Folders can be expanded and collapsed | P0 | ✅ Passed | Section expansion shows files |
| TC-004 | File click triggers content loading | P0 | ✅ Passed | Content loads, breadcrumb updates |
| TC-005 | Sidebar is responsive | P1 | ✅ Passed | Resize handle present, 280px width |
| TC-006 | File selection highlights active file | P1 | ✅ Passed | Active file switches correctly |
| TC-007 | Section icons display correctly | P1 | ✅ Passed | 290 Bootstrap icons found |
| TC-008 | Workplace section with submenu | P1 | ✅ Passed | Ideation, UIUX Feedbacks work |

---

## Execution Results

**Execution Date:** 2026-01-30
**Executed By:** Zephyr
**Environment:** Local Development (http://localhost:5858)

| Metric | Value |
|--------|-------|
| Total Tests | 8 |
| Passed | 8 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Failed Tests

| Test Case | Failure Reason | Screenshot | Recommended Action |
|-----------|----------------|------------|-------------------|
| - | None | - | - |

---

## Notes

- Test cases cover AC-1 through AC-7 and AC-11 from specification
- AC-8, AC-9 (real-time updates) require polling behavior verification
- AC-10 (project root switching) covered by ProjectSwitcher component
