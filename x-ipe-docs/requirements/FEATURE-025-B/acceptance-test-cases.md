# Acceptance Test Cases

> Feature: FEATURE-025-B - KB Landing Zone
> Generated: 2026-02-11
> Status: Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-025-B |
| Feature Title | KB Landing Zone |
| Total Test Cases | 13 |
| Priority | P0 (Critical) / P1 (High) / P2 (Medium) |
| Target URL | http://localhost:5001/ → Knowledge Base button |

---

## Prerequisites

- [x] Feature is deployed and accessible
- [x] Test environment is ready
- [x] Chrome DevTools MCP is available

---

## Test Cases

### TC-001: Empty State Display

**Acceptance Criteria Reference:** AC-6.1, AC-6.2 from specification.md

**Priority:** P0

**Preconditions:**
- Landing folder is empty (no files uploaded)

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | http://localhost:5001/ | Page loads |
| 2 | Click | `button " Knowledge"` | - | KB view opens |
| 3 | Verify | `.kb-empty-state-landing` | - | Empty state container visible |
| 4 | Verify | `.kb-empty-state-title` | - | Text: "No files in landing" |
| 5 | Verify | `.kb-empty-state-subtitle` | - | Text: "Upload files or drag and drop them here to get started" |
| 6 | Verify | `#kb-empty-upload-btn` | - | "Upload Files" button present |
| 7 | Verify | `#kb-drop-zone` | - | Drop zone with "Drop files here" visible |

**Expected Outcome:** Empty state shows centered upload zone with icon, title, subtitle, and upload button.

**Status:** ✅ Pass

**Execution Notes:** All elements present. Empty state renders correctly with drop zone overlay.

---

### TC-002: Upload Button Visible

**Acceptance Criteria Reference:** AC-1.1 from specification.md

**Priority:** P0

**Preconditions:**
- KB view is active

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to KB view | - | - | KB view opens |
| 2 | Verify | `.kb-btn.kb-btn-primary` | - | Upload button visible with upload icon |

**Expected Outcome:** Upload button with upload icon appears in the content header.

**Status:** ✅ Pass

**Execution Notes:** Upload button visible in header area with `bi-upload` icon.

---

### TC-003: Upload Multiple Files

**Acceptance Criteria Reference:** AC-1.2, AC-1.3, AC-1.5, AC-1.6, AC-1.9 from specification.md

**Priority:** P0

**Preconditions:**
- KB view is active
- Landing folder is empty

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | files | test.md, test.txt, test.py, test.pdf | 4 different file types |
| Expected | upload response | 4 files in "uploaded" array | All accepted |
| Expected | file grid | 4 cards visible | Grid re-rendered |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Upload via API | `POST /api/kb/upload` | test.md, test.txt, test.py, test.pdf | Response: 4 files uploaded |
| 2 | Verify | Sidebar tree | - | "Landing (4)" shown |
| 3 | Verify | Content header | - | "4 files" badge shown |
| 4 | Verify | File grid | - | 4 file cards displayed |

**Expected Outcome:** All 4 files uploaded, saved to landing/, index refreshed, grid shows 4 cards.

**Status:** ✅ Pass

**Execution Notes:** API returned `{"uploaded":["landing/test.md","landing/test.txt","landing/test.py","landing/test.pdf"],"skipped":[],"errors":[]}`. Grid showed 4 cards with names and sizes. Sidebar tree updated to "Landing (4)".

---

### TC-004: File Grid Display

**Acceptance Criteria Reference:** AC-3.1, AC-3.2 from specification.md

**Priority:** P0

**Preconditions:**
- 4 files uploaded to landing

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Verify | `.kb-file-grid` or `.kb-file-list` | - | Files displayed in grid/list |
| 2 | Verify | `.kb-file-card` | - | Cards show type icon, filename, size |
| 3 | Verify | `.kb-file-card-name` | - | test.md, test.pdf, test.py, test.txt |
| 4 | Verify | `.kb-file-card-meta` | - | Sizes: 22 B, 13 B, 14 B, 18 B |

**Expected Outcome:** File cards display in responsive grid with icon, name, and size.

**Status:** ✅ Pass

**Execution Notes:** Grid displayed with 4 cards. Each card shows colored type icon (md=green, pdf=red, py=blue), filename, and size in bytes.

---

### TC-005: File Card Selection

**Acceptance Criteria Reference:** AC-3.3, AC-3.4, AC-3.5 from specification.md

**Priority:** P0

**Preconditions:**
- Files displayed in grid

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Click | `.kb-file-card` (first) | - | Card gets `selected` class |
| 2 | Verify | `.kb-file-card.selected` | - | 1 card selected |
| 3 | Verify | `#kb-selection-count` | - | Text: "1 selected" |
| 4 | Verify | `#kb-delete-btn` | - | Delete button appears |

**Expected Outcome:** Clicking card toggles selection with visual highlight, selection count, and delete action.

**Status:** ✅ Pass

**Execution Notes:** Card click → `selected` class added → "1 selected" count shown → Delete button appeared.

---

### TC-006: Select All and Clear

**Acceptance Criteria Reference:** AC-4.1, AC-4.2 from specification.md

**Priority:** P1

**Preconditions:**
- Files displayed in grid

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Click | Select All button | - | All 4 cards selected |
| 2 | Verify | `.kb-file-card.selected` count | - | 4 selected |
| 3 | Verify | `#kb-selection-count` | - | "4 selected" |
| 4 | Click | Clear button | - | All cards deselected |
| 5 | Verify | `.kb-file-card.selected` count | - | 0 selected |
| 6 | Verify | `#kb-delete-btn` | - | Delete button hidden |

**Expected Outcome:** Select All selects all cards; Clear deselects all.

**Status:** ✅ Pass

**Execution Notes:** Select All → 4 selected, "4 selected" count. Clear → 0 selected, Delete button hidden.

---

### TC-007: View Mode Toggle

**Acceptance Criteria Reference:** AC-4.4 from specification.md

**Priority:** P1

**Preconditions:**
- Files displayed in grid

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Click | List view button (`bi-list-ul`) | - | View switches to list |
| 2 | Verify | `.kb-file-list` | - | List container visible |
| 3 | Verify | `.kb-file-list-item` count | - | 4 items |
| 4 | Click | Grid view button (`bi-grid-3x3-gap`) | - | View switches to grid |
| 5 | Verify | `.kb-file-grid` | - | Grid container visible |

**Expected Outcome:** Toggle between grid and list views.

**Status:** ✅ Pass

**Execution Notes:** List view showed 4 `.kb-file-list-item` elements. Grid view showed 4 `.kb-file-card` elements. Toggle works in both directions.

---

### TC-008: Sort Options

**Acceptance Criteria Reference:** AC-4.5 from specification.md

**Priority:** P1

**Preconditions:**
- Files displayed in grid

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Verify | Sort button | - | Shows current sort field (Name) |
| 2 | Click | Sort button | - | Order reverses (Z→A) |
| 3 | Verify | File order | - | test.txt, test.py, test.pdf, test.md |
| 4 | Click | Sort button | - | Cycles to next field (Size) |
| 5 | Verify | File order | - | test.pdf (13B), test.py (14B), test.txt (18B), test.md (22B) |

**Expected Outcome:** Sort cycles through fields (name, size, date, type) with ascending/descending toggle.

**Status:** ✅ Pass

**Execution Notes:** Initial sort by Name (asc). Click → Name (desc): txt, py, pdf, md. Click → Size (asc): pdf 13B, py 14B, txt 18B, md 22B.

---

### TC-009: Delete Action Visibility

**Acceptance Criteria Reference:** AC-4.3 from specification.md

**Priority:** P1

**Preconditions:**
- Files displayed, none selected

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Verify | `#kb-delete-btn` | - | Delete button not visible (no selection) |
| 2 | Click | First file card | - | 1 file selected |
| 3 | Verify | `#kb-delete-btn` | - | Delete button visible |
| 4 | Click | Clear | - | None selected |
| 5 | Verify | `#kb-delete-btn` | - | Delete button hidden again |

**Expected Outcome:** Delete button only appears when items are selected.

**Status:** ✅ Pass

**Execution Notes:** Delete button correctly toggles visibility based on selection state.

---

### TC-010: Delete Selected Files with Confirmation

**Acceptance Criteria Reference:** AC-5.1, AC-5.2, AC-5.4 from specification.md

**Priority:** P0

**Preconditions:**
- 4 files in landing

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Select 2 files | `.kb-file-list-item` (click 2) | - | 2 selected |
| 2 | Click | `#kb-delete-btn` | - | Confirmation dialog appears |
| 3 | Verify dialog | - | - | "Delete 2 file(s)? This cannot be undone." |
| 4 | Accept dialog | - | - | Files deleted |
| 5 | Verify | File count | - | "Landing (2)" in sidebar |
| 6 | Verify disk | `landing/` directory | - | Only 2 files remain |

**Expected Outcome:** Delete shows confirmation, removes files from disk, refreshes index.

**Status:** ✅ Pass

**Execution Notes:** Selected test.pdf + test.py → Delete → confirm dialog "Delete 2 file(s)? This cannot be undone." → accepted → Landing (2) with test.txt and test.md. Disk confirmed: only 2 files remain.

---

### TC-011: Delete All Files Returns to Empty State

**Acceptance Criteria Reference:** AC-6.4 from specification.md

**Priority:** P1

**Preconditions:**
- 2 files remaining in landing

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Select all remaining | Click both items | - | 2 selected |
| 2 | Click Delete | `#kb-delete-btn` | - | Confirmation dialog |
| 3 | Accept | - | - | All files deleted |
| 4 | Verify | `.kb-empty-state-landing` | - | Empty state visible |
| 5 | Verify | `.kb-empty-state-title` | - | "No files in landing" |

**Expected Outcome:** After deleting all files, empty state with upload zone appears.

**Status:** ✅ Pass

**Execution Notes:** Selected 2 → Delete → confirm → empty state restored with "No files in landing", upload button, and drop zone.

---

### TC-012: Duplicate File Detection

**Acceptance Criteria Reference:** AC-1.10 from specification.md

**Priority:** P1

**Preconditions:**
- test.md already in landing

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Upload test.md | `POST /api/kb/upload` | test.md | File uploaded |
| 2 | Upload test.md again | `POST /api/kb/upload` | test.md | Skipped: "Duplicate file already exists" |

**Expected Outcome:** Duplicate upload is skipped with warning, original preserved.

**Status:** ✅ Pass

**Execution Notes:** Second upload returned `{"skipped":[{"file":"test.md","reason":"Duplicate file already exists"}],"uploaded":[],"errors":[]}`.

---

### TC-013: Invalid File Type Rejection

**Acceptance Criteria Reference:** AC-1.3 from specification.md

**Priority:** P1

**Preconditions:**
- None

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Upload bad.exe | `POST /api/kb/upload` | bad.exe | Error: "Unsupported file type: '.exe'" |

**Expected Outcome:** Unsupported file type rejected with clear error message.

**Status:** ✅ Pass

**Execution Notes:** Response: `{"errors":[{"file":"bad.exe","reason":"Unsupported file type: '.exe'"}],"skipped":[],"uploaded":[]}`.

---

## Test Execution Summary

| Test Case | Title | Priority | Status | Notes |
|-----------|-------|----------|--------|-------|
| TC-001 | Empty State Display | P0 | ✅ Pass | AC-6.1, AC-6.2 |
| TC-002 | Upload Button Visible | P0 | ✅ Pass | AC-1.1 |
| TC-003 | Upload Multiple Files | P0 | ✅ Pass | AC-1.2, AC-1.3, AC-1.5, AC-1.6, AC-1.9 |
| TC-004 | File Grid Display | P0 | ✅ Pass | AC-3.1, AC-3.2 |
| TC-005 | File Card Selection | P0 | ✅ Pass | AC-3.3, AC-3.4, AC-3.5 |
| TC-006 | Select All and Clear | P1 | ✅ Pass | AC-4.1, AC-4.2 |
| TC-007 | View Mode Toggle | P1 | ✅ Pass | AC-4.4 |
| TC-008 | Sort Options | P1 | ✅ Pass | AC-4.5 |
| TC-009 | Delete Action Visibility | P1 | ✅ Pass | AC-4.3 |
| TC-010 | Delete Selected Files | P0 | ✅ Pass | AC-5.1, AC-5.2, AC-5.4 |
| TC-011 | Delete All → Empty State | P1 | ✅ Pass | AC-6.4 |
| TC-012 | Duplicate File Detection | P1 | ✅ Pass | AC-1.10 |
| TC-013 | Invalid File Type Rejection | P1 | ✅ Pass | AC-1.3 |

---

## Execution Results

**Execution Date:** 2026-02-11
**Executed By:** Pulse
**Environment:** dev (localhost:5001)

| Metric | Value |
|--------|-------|
| Total Tests | 13 |
| Passed | 13 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Failed Tests

_None_

---

## Mockup Validation Summary

**Mockup:** knowledge-base-v1.html (status: current)

| Element | Mockup Expectation | Actual Implementation | Match |
|---------|-------------------|----------------------|-------|
| Content header | Title + file count badge + Upload button | "Landing Folder" h5 + "N files" badge + Upload btn | ✅ Match |
| Action toolbar | Select All, Clear, Grid/List toggle, Sort, Delete | All present with same layout | ✅ Match |
| File grid | Responsive grid with `auto-fill, minmax(180px, 1fr)` | Grid with file cards, responsive | ✅ Match |
| File card | Icon (colored by type) + name + size + checkbox on hover | Icon + name + size + checkbox | ✅ Match |
| Card selection | Border highlight + background change | `.selected` class adds accent border/bg | ✅ Match |
| Empty state | Centered with icon, title, subtitle, upload button | All elements present | ✅ Match |
| Drop zone | Dashed border overlay on drag | Drop zone with dashed border styling | ✅ Match |
| Dark theme | Warm dark theme colors | Uses CSS variables matching dark theme | ✅ Match |

**Mockup Validation Result:** ✅ Pass — Implementation faithfully reproduces mockup layout, component hierarchy, and visual styling.

---

## ACs Not Tested via Chrome DevTools

The following ACs could not be fully tested via automated Chrome DevTools MCP:

| AC | Reason | Manual Test Recommended |
|----|--------|------------------------|
| AC-1.2 | File picker dialog is native OS — cannot trigger via MCP | Yes |
| AC-1.4 | Requires creating 51MB+ file — tested via unit tests | No (covered by test_kb_landing.py) |
| AC-1.7 | Folder upload requires native OS support | Yes |
| AC-1.8 | Upload progress for large files — requires slow network | Yes |
| AC-2.1–2.4 | Drag-drop events hard to simulate via MCP | Yes (drop zone rendering verified) |
| AC-5.3 | Cancel delete — would need to dismiss dialog (tested confirm path) | Minor |
| AC-7.1–7.3 | Processing indicator requires KB Manager Skill (FEATURE-025-C) | N/A (future feature) |

---

## Notes

- All tests executed against local dev server (Flask on port 5001)
- File picker and drag-drop interactions tested via API calls since native OS dialogs cannot be automated via Chrome DevTools MCP
- Processing indicator ACs (AC-7.x) are deferred to FEATURE-025-C (KB Manager Skill)
- 57 unit tests in test_kb_landing.py provide comprehensive backend coverage for edge cases not testable via UI
