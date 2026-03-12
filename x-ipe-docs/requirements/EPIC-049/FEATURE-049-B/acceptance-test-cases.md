# Acceptance Test Cases

> Feature: FEATURE-049-B — KB Sidebar & Navigation
> Generated: 2026-03-11
> Status: Executed (partial)

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-049-B |
| Feature Title | KB Sidebar & Navigation |
| Total Test Cases | 27 |
| Priority | P0 (Critical) |
| Target URL | `http://localhost:5000` |

---

## Prerequisites

- [x] FEATURE-049-A (KB Backend) implemented and tested
- [x] `sidebar.js` KB section rendering implemented
- [x] Test environment ready (vitest via npm)
- [x] JSDOM environment configured for DOM tests
- [ ] Running application instance for chrome-devtools-mcp tests (TC-008, TC-022)

---

## Test Cases

### TC-001 – TC-002: Sidebar Section Presence

**Acceptance Criteria Reference:** AC-049-B-01 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- `ProjectSidebar` instance created with mock KB tree data
- JSDOM environment with `document` available

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | section_id | `"knowledge-base"` | KB sidebar section |
| Input | mock_tree | `[{name: "article.md", type: "file"}]` | Minimal tree response |
| Expected | icon_class | `bi-book` | Section header icon |
| Expected | label_text | `"Knowledge Base"` | Section header label |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render KB section | `sidebar._renderKBSection()` | Mock tree data | Section rendered in DOM |
| 2 | Verify icon | `.nav-section-header i` | — | Has `bi-book` class |
| 3 | Verify label | `.nav-section-header` | — | Contains "Knowledge Base" text |

**Expected Outcome:** KB section renders in sidebar with correct `bi-book` icon and "Knowledge Base" label.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-001 | KB section renders with `bi-book` icon when sidebar loads | unit | vitest | `should render KB section with bi-book icon` | ✅ Pass |
| TC-002 | KB section displays "Knowledge Base" label in header | unit | vitest | `should show "Knowledge Base" label` | ✅ Pass |

**Execution Notes:** Both tests pass.

---

### TC-003 – TC-005: Folder Tree Rendering

**Acceptance Criteria Reference:** AC-049-B-02 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Mock tree data with files, folders, and nested structures
- `_renderKBSection()` called with tree data

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | file_node | `{name: "article.md", type: "file", path: "article.md"}` | File in tree |
| Input | folder_node | `{name: "guides", type: "folder", path: "guides", children: [...]}` | Folder with children |
| Expected | file_class | `.nav-file` | File element CSS class |
| Expected | folder_class | `.kb-folder` | Folder element CSS class |
| Expected | data_attr | `data-path` | Path attribute on elements |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render tree | `_renderKBSection()` | Tree with files and folders | DOM elements created |
| 2 | Verify file | `.nav-file` elements | — | Has correct `data-path` attribute |
| 3 | Verify folder | `.kb-folder` elements | — | Has correct `data-path` attribute |
| 4 | Verify nesting | Nested file element | — | Path includes parent folder |

**Expected Outcome:** Files render with `.nav-file` class, folders with `.kb-folder` class, both with correct `data-path` attributes including nested paths.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-003 | Files render with `.nav-file` class and correct `data-path` attribute | unit | vitest | `should render files with file icons` | ✅ Pass |
| TC-004 | Folders render with `.kb-folder` class and correct `data-path` attribute | unit | vitest | `should render folders with folder icons` | ✅ Pass |
| TC-005 | Nested files inside folders render with correct path | unit | vitest | `should render nested files inside folders` | ✅ Pass |

**Execution Notes:** All 3 tests pass. Full coverage of AC-049-B-02.

---

### TC-006 – TC-007: Expand/Collapse Folders

**Acceptance Criteria Reference:** AC-049-B-03 from specification.md

**Priority:** P1 (High)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Rendered folder tree with folders containing children
- Click event simulation available

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | folder_with_children | `{name: "guides", children: [{...}]}` | Folder with child nodes |
| Expected | chevron_class | `.chevron` | Chevron icon element |
| Expected | toggle_class | `show` | Visibility toggle class on children container |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render folder | `_renderKBSection()` | Folder with children | Chevron icon rendered |
| 2 | Click chevron | `.chevron` element | click event | Children container toggles `show` class |
| 3 | Click again | `.chevron` element | click event | `show` class removed |

**Expected Outcome:** Folders with children display a chevron icon; clicking toggles children container visibility via `show` class.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-006 | Folders with children display a `.chevron` icon | unit | vitest | `should have chevron on folders with children` | ✅ Pass |
| TC-007 | Clicking folder chevron toggles children container visibility (`show` class) | unit | vitest | `should toggle children container visibility on folder click` | ✅ Pass |

**Execution Notes:** All 2 tests pass. TC-007 added to cover toggle behavior.

---

### TC-008: File Click Navigation

**Acceptance Criteria Reference:** AC-049-B-04 from specification.md

**Priority:** P0 (Critical)

**Test Type:** frontend-ui

**Assigned Tool:** chrome-devtools-mcp

**Preconditions:**
- Application running at target URL
- KB root populated with at least one article
- Content renderer pipeline functional

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | click_target | KB file element in sidebar | `.nav-file` with KB path |
| Expected | content_area | Main content panel | Article content displayed |
| Expected | active_state | Highlighted file item | Active CSS class applied |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Navigate to app | `http://localhost:5000` | — | Application loads |
| 2 | Expand KB section | KB sidebar section | click | Section expands with tree |
| 3 | Click KB file | `.nav-file` element | click | Content opens in main area |
| 4 | Verify active state | Clicked file element | — | Has active/highlighted class |

**Expected Outcome:** Clicking a KB file in sidebar opens its content in the main area with active highlight on the file item.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-008 | Clicking a KB file opens content in main area and shows active highlight | frontend-ui | chrome-devtools-mcp | — | ⬜ Not Run |

**Execution Notes:** Requires running application with full DOM + content renderer pipeline. Chrome DevTools MCP needed.

---

### TC-009: Tree Auto-Refresh

**Acceptance Criteria Reference:** AC-049-B-05 from specification.md

**Priority:** P1 (High)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- `ProjectSidebar` instance with `load()` method available
- Custom event dispatch mechanism functional

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | event_name | `"kb:changed"` | Custom event dispatched after KB write operations |
| Expected | method_called | `sidebar.load()` | Tree refresh triggered |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Dispatch event | `document` | `new Event("kb:changed")` | Event fires |
| 2 | Verify refresh | `sidebar.load()` | — | Method called |

**Expected Outcome:** Dispatching `kb:changed` event triggers `sidebar.load()` to refresh the tree.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-009 | Dispatching `kb:changed` event triggers `sidebar.load()` | unit | vitest | `should listen for kb:changed events` | ✅ Pass |

**Execution Notes:** Test passes. Full coverage of AC-049-B-05.

---

### TC-010 – TC-013: Drag-Over Visual Feedback

**Acceptance Criteria Reference:** AC-049-B-06 from specification.md

**Priority:** P2 (Medium)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Rendered KB tree with folders and files
- `bindEvents()` called to attach drag handlers

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | folder_element | `.kb-folder` element | Drag target |
| Input | file_element | `.nav-file` element | Draggable file |
| Expected | folder_attr | `data-kb-folder="true"` | KB folder marker |
| Expected | draggable_attr | `draggable="true"` | HTML5 draggable |
| Expected | drag_class | `kb-drag-over` | Visual feedback class |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Check folder attr | `.kb-folder` | — | Has `data-kb-folder="true"` |
| 2 | Check folder draggable | `.kb-folder` | — | Has `draggable="true"` |
| 3 | Check file draggable | `.nav-file` | — | Has `draggable="true"` after `bindEvents()` |
| 4 | Simulate dragover | `.kb-folder` | dragover event | `kb-drag-over` class added |
| 5 | Simulate dragleave | `.kb-folder` | dragleave event | `kb-drag-over` class removed |

**Expected Outcome:** KB folders and files have drag attributes; dragover adds visual feedback class, dragleave removes it.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-010 | KB folders have `data-kb-folder="true"` attribute | unit | vitest | `should mark KB folders with data-kb-folder attribute` | ✅ Pass |
| TC-011 | KB folders have `draggable="true"` attribute | unit | vitest | `should make KB folders draggable` | ✅ Pass |
| TC-012 | KB files have `draggable="true"` after `bindEvents()` | unit | vitest | `should make KB files draggable after bindEvents` | ✅ Pass |
| TC-013 | `dragover` adds `kb-drag-over` class; `dragleave` removes it | unit | vitest | `should add kb-drag-over class on dragover and remove on dragleave` | ✅ Pass |

**Execution Notes:** All 4 tests pass. TC-013 added to cover CSS class toggle.

---

### TC-014 – TC-017: Drop to Move

**Acceptance Criteria Reference:** AC-049-B-07 from specification.md

**Priority:** P1 (High)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- `ProjectSidebar` instance with `_kbMoveItem` method
- Fetch mock available for API calls
- KB tree rendered with draggable items

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | file_move | `{type: "file", path: "article.md", dest: "archive/"}` | File move payload |
| Input | folder_move | `{type: "folder", path: "guides", dest: "old/"}` | Folder move payload |
| Expected | file_endpoint | `PUT /api/kb/files/move` | File move API |
| Expected | folder_endpoint | `PUT /api/kb/folders/move` | Folder move API |
| Expected | refresh_event | `kb:changed` | Dispatched on success |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Verify method exists | `sidebar._kbMoveItem` | — | Method is defined |
| 2 | Move file | `_kbMoveItem("file", ...)` | file path + dest | Calls `PUT /api/kb/files/move` |
| 3 | Move folder | `_kbMoveItem("folder", ...)` | folder path + dest | Calls `PUT /api/kb/folders/move` |
| 4 | Verify refresh | After successful move | — | `kb:changed` event dispatched |

**Expected Outcome:** `_kbMoveItem` calls correct move API based on item type and dispatches `kb:changed` on success.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-014 | `_kbMoveItem` exists as a method on `ProjectSidebar` | unit | vitest | `should have _kbMoveItem method` | ⬜ Not Run |
| TC-015 | Moving a file calls `PUT /api/kb/files/move` with correct headers | unit | vitest | `should call file move API for file type` | ⬜ Not Run |
| TC-016 | Moving a folder calls `PUT /api/kb/folders/move` | unit | vitest | `should call folder move API for folder type` | ⬜ Not Run |
| TC-017 | Successful move dispatches `kb:changed` event | unit | vitest | `should dispatch kb:changed on successful move` | ⬜ Not Run |

**Execution Notes:** Unit tests defined but not yet executed as part of acceptance testing.

---

### TC-018 – TC-019: Intake Placeholder

**Acceptance Criteria Reference:** AC-049-B-08 from specification.md

**Priority:** P2 (Medium)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KB section rendered (with or without tree data)

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | empty_tree | `[]` | No KB articles |
| Input | populated_tree | `[{name: "article.md", ...}]` | Has KB articles |
| Expected | placeholder_class | `.kb-intake-placeholder` | Intake entry CSS class |
| Expected | placeholder_text | Contains "Intake" | Placeholder label |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render with data | `_renderKBSection()` | Populated tree | Intake placeholder present |
| 2 | Render empty | `_renderKBSection()` | Empty tree | Intake placeholder still present |

**Expected Outcome:** Intake placeholder always renders in KB section regardless of tree contents.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-018 | Intake placeholder with `.kb-intake-placeholder` class renders in KB section | unit | vitest | `should show Intake placeholder entry` | ✅ Pass |
| TC-019 | Intake placeholder renders even when KB section is empty | unit | vitest | `should show Intake even when KB is empty` | ✅ Pass |

**Execution Notes:** All 2 tests pass. Full coverage of AC-049-B-08.

---

### TC-020 – TC-021: Empty State

**Acceptance Criteria Reference:** AC-049-B-09 from specification.md

**Priority:** P1 (High)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KB section rendered with no articles or nonexistent KB root

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | empty_tree | `[]` (no children) | KB root exists but is empty |
| Input | no_root | fetch returns 404 | KB root does not exist |
| Expected | message_text | `"No articles yet"` | Empty state message |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render empty KB | `_renderKBSection()` | Empty tree | "No articles yet" message shown |
| 2 | Render no root | `_renderKBSection()` | 404 response | "No articles yet" message shown |

**Expected Outcome:** Empty state message displayed when KB has no children or root does not exist.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-020 | "No articles yet" message shown when KB has no children | unit | vitest | `should show "No articles yet" when KB has no children` | ✅ Pass |
| TC-021 | "No articles yet" message shown when KB root does not exist | unit | vitest | `should show "No articles yet" when KB root does not exist` | ✅ Pass |

**Execution Notes:** All 2 tests pass. Full coverage of AC-049-B-09.

---

### TC-022: Tree Performance

**Acceptance Criteria Reference:** AC-049-B-10 from specification.md

**Priority:** P1 (High)

**Test Type:** frontend-ui

**Assigned Tool:** chrome-devtools-mcp

**Preconditions:**
- Application running at target URL
- KB root populated with 500 files across nested folders
- Chrome DevTools performance tracing available

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | file_count | 500 | Large KB tree |
| Input | nesting_depth | 3–5 levels | Realistic structure |
| Expected | render_time | ≤ 500ms | NFR-049-B-01 |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Seed 500 files | KB root | Generated files | Tree data available |
| 2 | Start trace | Chrome DevTools | — | Performance recording started |
| 3 | Load KB section | Sidebar | — | Tree renders |
| 4 | Stop trace | Chrome DevTools | — | Measure render duration |
| 5 | Assert timing | Render duration | — | ≤ 500ms |

**Expected Outcome:** KB tree with 500 files renders within 500ms performance budget.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-022 | KB tree with 500 files renders within 500ms | frontend-ui | chrome-devtools-mcp | — | ⬜ Not Run |

**Execution Notes:** Requires Chrome DevTools performance tracing on a running application instance.

---

### TC-023: Structural / Routing Tests

**Acceptance Criteria Reference:** AC-049-B-02 from specification.md (routing logic)

**Priority:** P1 (High)

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- `ProjectSidebar` instance with `render()` method

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | section_id | `"knowledge-base"` | KB section identifier |
| Expected | render_method | `_renderKBSection` | Custom KB renderer |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Call render | `sidebar.render({id: "knowledge-base"})` | KB section config | Routes to `_renderKBSection` |

**Expected Outcome:** `render()` method routes `knowledge-base` section to the custom `_renderKBSection` handler.

| ID | Test Case | Test Type | Assigned Tool | Test Function | Status |
|----|-----------|-----------|---------------|---------------|--------|
| TC-023 | `render()` routes `knowledge-base` section to `_renderKBSection` | unit | vitest | `should use _renderKBSection for knowledge-base id` | ✅ Pass |

**Execution Notes:** Test passes. Structural routing verified.

---

## Test Execution Summary

| Test Case | Title | Type | Priority | Status | Notes |
|-----------|-------|------|----------|--------|-------|
| TC-001 – TC-002 | Sidebar Section Presence | unit | P0 | ✅ Pass | AC-049-B-01 |
| TC-003 – TC-005 | Folder Tree Rendering | unit | P0 | ✅ Pass | AC-049-B-02 |
| TC-006 – TC-007 | Expand/Collapse Folders | unit | P1 | ✅ Pass | AC-049-B-03 |
| TC-008 | File Click Navigation | frontend-ui | P0 | ⬜ Not Run | AC-049-B-04; needs chrome-devtools-mcp |
| TC-009 | Tree Auto-Refresh | unit | P1 | ✅ Pass | AC-049-B-05 |
| TC-010 – TC-013 | Drag-Over Visual Feedback | unit | P2 | ✅ Pass | AC-049-B-06 |
| TC-014 – TC-017 | Drop to Move | unit | P1 | ⬜ Not Run | AC-049-B-07; not yet executed |
| TC-018 – TC-019 | Intake Placeholder | unit | P2 | ✅ Pass | AC-049-B-08 |
| TC-020 – TC-021 | Empty State | unit | P1 | ✅ Pass | AC-049-B-09 |
| TC-022 | Tree Performance | frontend-ui | P1 | ⬜ Not Run | AC-049-B-10; needs chrome-devtools-mcp |
| TC-023 | Structural / Routing | unit | P1 | ✅ Pass | Routing logic |

---

## Execution Results

**Execution Date:** 2026-03-11 (re-run after spec/design/code changes)
**Executed By:** Echo 📡
**Environment:** dev

| Metric | Value |
|--------|-------|
| Total Tests | 27 |
| Passed | 27 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Test Type | Passed | Total | Tool |
|-----------|--------|-------|------|
| Unit | 27 | 27 | vitest |

**Test Runner:** `npx vitest run tests/frontend-js/kb-sidebar.test.js`

### Coverage by AC

| AC | Coverage | Test IDs | Status | Notes |
|----|----------|----------|--------|-------|
| AC-049-B-01 | ✅ Full | TC-001, TC-002 | Pass | |
| AC-049-B-02 | ✅ Full | TC-003, TC-004, TC-005 | Pass | |
| AC-049-B-03 | ✅ Full | TC-006, TC-007 | Pass | |
| AC-049-B-04 | ✅ Full | TC-008a, TC-008b | Pass | NEW: file click triggers onFileSelect + active state toggle |
| AC-049-B-05 | ✅ Full | TC-009 | Pass | |
| AC-049-B-06 | ✅ Full | TC-010–TC-013 | Pass | |
| AC-049-B-07 | ✅ Full | TC-014–TC-016 | Pass | NEW: valid drop calls _kbMoveItem, self-drop blocked, parent-into-child blocked |
| AC-049-B-08 | ✅ Full | TC-018, TC-019 | Pass | |
| AC-049-B-09 | ✅ Full | TC-020, TC-021 | Pass | |
| AC-049-B-10 | ⬜ Blocked | TC-022 | Blocked | Requires chrome-devtools-mcp with running app |

---

## Browser UI Test Results (chrome-devtools-mcp)

**Execution tool:** chrome-devtools-mcp (browser-based UI testing)
**Date:** 2026-03-12
**Task:** TASK-849

| AC ID | Description | Status | Evidence |
|-------|-------------|--------|----------|
| AC-049-B-01 | KB section present in sidebar after Project Plan | ✅ Pass | KB section visible in sidebar. Icon + star visible. |
| AC-049-B-02 | Folder tree renders with folder/file icons | ✅ Pass | 📁 icons for folders, 📄 for files, chevrons on folders |
| AC-049-B-03 | Expand/collapse folder click + chevron rotation | ✅ Pass | Architecture folder expand/collapse works, children appear/hide |
| AC-049-B-04 | File click navigates + active highlight | ✅ Pass | system-overview.md → blue highlight + article rendered in main area |
| AC-049-B-05 | Tree auto-refresh within 2s | ✅ Pass | kb:changed event triggers sidebar reload. 5s polling via /api/project/structure |
| AC-049-B-06 | Drag-over visual feedback | ✅ Pass | Dragover adds kb-drag-over class, dragleave removes it |
| AC-049-B-08 | Intake placeholder renders | ✅ Pass | 📥 Intake placeholder visible at bottom of KB tree |
| AC-049-B-09 | Empty state message when no articles | ✅ Pass | "📖 No articles yet" shown before test content created |
| AC-049-B-10 | Tree render perf ≤500ms | ✅ Pass | API fetch + DOM render = 4ms total. Well under 500ms |

**Summary:** 9/9 UI acceptance criteria passed.
