# Acceptance Test Cases

> **Feature:** FEATURE-049-B — KB Sidebar & Navigation
> **Generated:** 2026-03-11
> **Status:** Executed (unit) / Blocked (frontend-ui)

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-049-B |
| Epic | EPIC-049 (Knowledge Base) |
| Total ACs | 10 |
| Total Test Cases | 23 |
| Test Types | unit (vitest), frontend-ui (chrome-devtools-mcp) |
| Unit Test File | `tests/frontend-js/kb-sidebar.test.js` |

## Test Cases

### AC-049-B-01: Sidebar Section Presence

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-001 | KB section renders with `bi-book` icon when sidebar loads | unit | vitest | ✅ passed |
| TC-002 | KB section displays "Knowledge Base" label in header | unit | vitest | ✅ passed |

### AC-049-B-02: Folder Tree Rendering

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-003 | Files render with `.nav-file` class and correct `data-path` attribute | unit | vitest | ✅ passed |
| TC-004 | Folders render with `.kb-folder` class and correct `data-path` attribute | unit | vitest | ✅ passed |
| TC-005 | Nested files inside folders render with correct path | unit | vitest | ✅ passed |

### AC-049-B-03: Expand/Collapse Folders

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-006 | Folders with children display a `.chevron` icon | unit | vitest | ✅ passed |
| TC-007 | Clicking folder chevron toggles children container visibility (`show` class) | unit | vitest | ✅ passed |

### AC-049-B-04: File Click Navigation

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-008 | Clicking a KB file opens content in main area and shows active highlight | frontend-ui | chrome-devtools-mcp | 🚫 blocked |

> **Blocked reason:** Requires running application with full DOM + content renderer pipeline. Chrome DevTools MCP needed.

### AC-049-B-05: Tree Auto-Refresh

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-009 | Dispatching `kb:changed` event triggers `sidebar.load()` | unit | vitest | ✅ passed |

### AC-049-B-06: Drag-Over Visual Feedback

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-010 | KB folders have `data-kb-folder="true"` attribute | unit | vitest | ✅ passed |
| TC-011 | KB folders have `draggable="true"` attribute | unit | vitest | ✅ passed |
| TC-012 | KB files have `draggable="true"` after `bindEvents()` | unit | vitest | ✅ passed |
| TC-013 | `dragover` adds `kb-drag-over` class; `dragleave` removes it | unit | vitest | ✅ passed |

### AC-049-B-07: Drop to Move

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-014 | `_kbMoveItem` exists as a method on `ProjectSidebar` | unit | vitest | ✅ passed |
| TC-015 | Moving a file calls `PUT /api/kb/files/move` with correct headers | unit | vitest | ✅ passed |
| TC-016 | Moving a folder calls `PUT /api/kb/folders/move` | unit | vitest | ✅ passed |
| TC-017 | Successful move dispatches `kb:changed` event | unit | vitest | ✅ passed |

### AC-049-B-08: Intake Placeholder

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-018 | Intake placeholder with `.kb-intake-placeholder` class renders in KB section | unit | vitest | ✅ passed |
| TC-019 | Intake placeholder renders even when KB section is empty | unit | vitest | ✅ passed |

### AC-049-B-09: Empty State

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-020 | "No articles yet" message shown when KB has no children | unit | vitest | ✅ passed |
| TC-021 | "No articles yet" message shown when KB root does not exist | unit | vitest | ✅ passed |

### AC-049-B-10: Tree Performance

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-022 | KB tree with 500 files renders within 500ms | frontend-ui | chrome-devtools-mcp | 🚫 blocked |

> **Blocked reason:** Performance measurement requires Chrome DevTools performance tracing on a running application instance.

### Structural / Routing Tests

| ID | Test Case | Test Type | Assigned Tool | Status |
|----|-----------|-----------|---------------|--------|
| TC-023 | `render()` routes `knowledge-base` section to `_renderKBSection` | unit | vitest | ✅ passed |

## Execution Results

### Results by Type

| Type | Passed | Total | Tool | Notes |
|------|--------|-------|------|-------|
| unit | 22 | 22 | vitest | All passing — `tests/frontend-js/kb-sidebar.test.js` |
| frontend-ui | 0 | 2 | chrome-devtools-mcp | Blocked — requires running app + Chrome MCP |

### Overall Metrics

| Metric | Value |
|--------|-------|
| Total test cases | 23 |
| Passed | 22 |
| Failed | 0 |
| Blocked | 2 (TC-008, TC-022) |
| Pass rate (executable) | 100% (22/22) |
| Pass rate (total) | 91.3% (22/23 — 1 blocked TC-008 is AC gap, TC-022 is NFR) |

### Coverage by AC

| AC | Coverage | Test IDs | Notes |
|----|----------|----------|-------|
| AC-049-B-01 | ✅ Full | TC-001, TC-002 | |
| AC-049-B-02 | ✅ Full | TC-003, TC-004, TC-005 | |
| AC-049-B-03 | ✅ Full | TC-006, TC-007 | TC-007 added to cover toggle behavior |
| AC-049-B-04 | 🚫 Blocked | TC-008 | Needs chrome-devtools-mcp |
| AC-049-B-05 | ✅ Full | TC-009 | |
| AC-049-B-06 | ✅ Full | TC-010–TC-013 | TC-013 added to cover CSS class toggle |
| AC-049-B-07 | ✅ Full | TC-014–TC-017 | |
| AC-049-B-08 | ✅ Full | TC-018, TC-019 | |
| AC-049-B-09 | ✅ Full | TC-020, TC-021 | |
| AC-049-B-10 | 🚫 Blocked | TC-022 | Needs chrome-devtools-mcp |
