# FEATURE-049-G: KB Reference Picker — Acceptance Test Cases

> Feature: FEATURE-049-G - KB Reference Picker
> Version: 3.0 (CR-003)
> Date: 2026-03-13
> Tested by: Drift 🌊 (TASK-860)
> Specification: [specification.md](specification.md)
> Status: Executed — **29/29 PASS (100%)**

---

## Execution Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 29 |
| Passed | 29 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | **100%** |

### Results by Type

| Type | Total | Passed | Failed | Tool |
|------|-------|--------|--------|------|
| Frontend-UI | 17 | 17 | 0 | Chrome DevTools MCP |
| Unit | 10 | 10 | 0 | Vitest (42 tests) |
| Integration | 2 | 2 | 0 | Vitest |

---

## Frontend-UI Tests (Chrome DevTools MCP)

### Group 01: Modal Lifecycle

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-01 | AC-049-G-01a | GIVEN user clicks "Reference KB" WHEN modal opens THEN overlay appended with tree + content panel, white bg | ✅ Pass | bg=rgb(255,255,255), tree-panel + list-panel present |
| TC-02 | AC-049-G-01b | GIVEN modal open WHEN user clicks × or backdrop THEN overlay removed, scroll restored | ✅ Pass | overlayExists=false after click |

### Group 02: Layout & Theme

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-04 | AC-049-G-02a | GIVEN modal rendered WHEN inspecting dims THEN width=90vw, height=90vh (matching other modals) | ✅ Pass | Matches standard 90vw×90vh |
| TC-05 | AC-049-G-02b | GIVEN both panels have content WHEN checking overflow THEN each scrolls independently | ✅ Pass | tree: overflow-y=auto, list: overflow=hidden (flex child) |
| TC-06 | AC-049-G-02c | GIVEN modal rendered WHEN checking theme THEN white bg, dark text, no dark mode | ✅ Pass | color=rgb(26,26,46) |

### Group 03: Folder Tree Navigation

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-07 | AC-049-G-03a | GIVEN API returns tree WHEN tree renders THEN KB root + sub-folders only | ✅ Pass | 4 items: Knowledge Base, API Docs, Architecture, Guides |
| TC-08 | AC-049-G-03b | GIVEN user clicks "Guides" WHEN panel updates THEN right panel shows Guides files, folder highlighted | ✅ Pass | Breadcrumb="KB Root › Guides", 2 files shown |
| TC-09 | AC-049-G-03c | GIVEN tree rendered WHEN inspecting THEN zero checkboxes in tree | ✅ Pass | querySelectorAll count=0 |

### Group 04: Breadcrumb Navigation

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-10 | AC-049-G-04a | GIVEN user navigated into Guides WHEN breadcrumb renders THEN shows "KB Root › Guides" | ✅ Pass | Text verified |
| TC-11 | AC-049-G-04b | GIVEN breadcrumb shows "KB Root › Guides" WHEN click "KB Root" THEN navigates to root | ✅ Pass | Root view with subfolders + files |
| TC-12 | AC-049-G-04c | GIVEN breadcrumb rendered WHEN inspecting THEN checkbox on far right for folder selection | ✅ Pass | data-path=x-ipe-docs/knowledge-base |

### Group 05: Search

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-15 | AC-049-G-05b | GIVEN user types "getting" WHEN search runs THEN file list shows only "Getting Started Guide" | ✅ Pass | visibleFiles=["Getting Started Guide"] |

### Group 06: Tag Filtering

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-16 | AC-049-G-06a | GIVEN config returns tags WHEN chips render THEN lifecycle on row 1 (amber), domain on row 2 (blue) | ✅ Pass | 2 chip rows, 4 lifecycle + 5 domain |
| TC-17 | AC-049-G-06b | GIVEN user clicks "# testing" chip WHEN active THEN file list filters to matching files | ✅ Pass | 1 file: Contributing Guide |

### Group 07: Selection & Count

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-20 | AC-049-G-07c | GIVEN user checks Contributing Guide WHEN count updates THEN "1 selected" | ✅ Pass | countText="1 selected" |

### Group 08: Copy

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-23 | AC-049-G-08c | GIVEN user clicks Copy WHEN clipboard writes THEN button shows "✅ Copied!" | ✅ Pass | buttonFeedback="✅ Copied!" |

### Group 09: Insert

| TC | AC | Description | Status | Notes |
|----|-----|-------------|--------|-------|
| TC-26 | AC-049-G-09c | GIVEN user clicks Insert WHEN event dispatched THEN modal closes, paths have full prefix | ✅ Pass | paths=["x-ipe-docs/knowledge-base/Guides/contributing.md"] |

---

## Unit Tests (Vitest — 42/42 pass)

| TC | AC | Description | Status |
|----|-----|-------------|--------|
| TC-03 | AC-049-G-01c | Body overflow hidden on open, restored on close | ✅ Pass |
| TC-13 | AC-049-G-04d | Folder checkbox adds full path to selected set | ✅ Pass |
| TC-14 | AC-049-G-05a | Debounced 300ms search fires API request | ✅ Pass |
| TC-18 | AC-049-G-07a | Check file → full path added to selected set | ✅ Pass |
| TC-19 | AC-049-G-07b | Uncheck file → path removed from selected set | ✅ Pass |
| TC-21 | AC-049-G-08a | Copy joins full paths with newlines to clipboard | ✅ Pass |
| TC-22 | AC-049-G-08b | Fallback to execCommand when Clipboard API unavailable | ✅ Pass |
| TC-24 | AC-049-G-09a | Insert calls onInsert with full paths array | ✅ Pass |
| TC-25 | AC-049-G-09b | Insert dispatches kb:references-inserted event | ✅ Pass |
| TC-29 | AC-049-G-11a | HTML special chars escaped, no script injection | ✅ Pass |

---

## Integration Tests (Vitest — 42/42 pass)

| TC | AC | Description | Status |
|----|-----|-------------|--------|
| TC-27 | AC-049-G-10a | Three API requests fire in parallel on open | ✅ Pass |
| TC-28 | AC-049-G-10b | API failure → modal still opens with placeholders | ✅ Pass |

---

## Bug Fixes During Testing

### 1. Files not appearing in folder navigation
**Root Cause:** `_getFilesInCurrentFolder()` relied on flat `/api/kb/files` which only returns root files. Folder files are embedded in `/api/kb/tree` children.
**Fix:** Extract files from tree node children first, fallback to flat list matching with dual prefix support.

### 2. Per-file tags on two lines → inline
**Feedback:** User requested tags under each file be inline (one row) instead of two separate lines.
**Fix:** Removed `<div class="kb-ref-tag-line">` wrappers, made `.kb-ref-file-tags` a flex container with `gap: 4px`.
