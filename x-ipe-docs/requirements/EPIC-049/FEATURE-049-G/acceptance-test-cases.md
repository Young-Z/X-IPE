# FEATURE-049-G: KB Reference Picker — Acceptance Test Cases

> Derived from implementation (`kb-reference-picker.js`, 271 LOC) since no specification.md exists.

## Acceptance Criteria (Derived)

| AC | Description |
|----|-------------|
| AC1 | Modal opens with two-panel layout (folder tree + file list) |
| AC2 | Modal closes via ✕ button and overlay backdrop click |
| AC3 | Search input triggers debounced API call (300ms) |
| AC4 | Tag filter chips (lifecycle + domain) toggle and filter file list |
| AC5 | Multi-select via checkboxes for files and folders |
| AC6 | Selected count display updates on check/uncheck |
| AC7 | Copy button copies selected paths to clipboard (with fallback) |
| AC8 | Insert button invokes onInsert callback + dispatches `kb:references-inserted` event |
| AC9 | Parallel API loading: `/api/kb/tree`, `/api/kb/config`, `/api/kb/files` |
| AC10 | HTML escaping prevents XSS in file names and tag text |
| AC11 | Graceful degradation on API failure (no crash) |
| AC12 | Body scroll locked on open, restored on close |

---

## Test Cases

### TC-01: Modal opens with overlay
- **AC:** AC1
- **Given:** KBReferencePicker instantiated
- **When:** `open()` called
- **Then:** `.kb-ref-overlay` appended to body
- **Coverage:** ✅ Existing test `should create overlay on open`

### TC-02: Modal shows header with title
- **AC:** AC1
- **Given:** Picker opened
- **When:** Modal rendered
- **Then:** Header contains "Reference Picker"
- **Coverage:** ✅ Existing test `should show header`

### TC-03: Two-panel layout — tree panel
- **AC:** AC1
- **Given:** Picker opened with tree data
- **When:** Modal rendered
- **Then:** `.kb-ref-tree-panel` present
- **Coverage:** ✅ Existing test `should render tree panel`

### TC-04: Two-panel layout — list panel
- **AC:** AC1
- **Given:** Picker opened with file data
- **When:** Modal rendered
- **Then:** `.kb-ref-list-panel` present with file items
- **Coverage:** ✅ Existing test `should render list panel`

### TC-05: Folder tree shows nested folders with checkboxes
- **AC:** AC1, AC5
- **Given:** Tree has nested folders (guides > setup)
- **When:** Modal rendered
- **Then:** 2 folder checkboxes with `data-type="folder"`
- **Coverage:** ✅ Existing test `should show folders in tree with checkboxes`

### TC-06: File list renders file items
- **AC:** AC1
- **Given:** Files loaded from API
- **When:** Modal rendered
- **Then:** File items match file count
- **Coverage:** ✅ Existing test `should show files in list panel`

### TC-07: Close via ✕ button
- **AC:** AC2
- **Given:** Modal open
- **When:** ✕ button clicked
- **Then:** Overlay removed after 300ms animation
- **Coverage:** ✅ Existing test `should remove overlay on close`

### TC-08: Close via overlay backdrop click
- **AC:** AC2
- **Given:** Modal open
- **When:** Overlay background clicked
- **Then:** Modal closes
- **Coverage:** 🆕 Added test `should close on overlay backdrop click`

### TC-09: Search input present
- **AC:** AC3
- **Given:** Modal open
- **When:** Modal rendered
- **Then:** `.kb-ref-search-input` present
- **Coverage:** ✅ Existing test `should render search input`

### TC-10: Search debounce triggers API
- **AC:** AC3
- **Given:** Modal open
- **When:** User types in search input and 300ms elapses
- **Then:** Fetch called with `/api/kb/search?q=...`
- **Coverage:** 🆕 Added test `should debounce search and call API`

### TC-11: Lifecycle filter chips rendered
- **AC:** AC4
- **Given:** Config has lifecycle tags
- **When:** Modal rendered
- **Then:** Lifecycle chips count matches config
- **Coverage:** ✅ Existing test `should render lifecycle filter chips`

### TC-12: Domain filter chips rendered
- **AC:** AC4
- **Given:** Config has domain tags
- **When:** Modal rendered
- **Then:** Domain chips count matches config
- **Coverage:** ✅ Existing test `should render domain filter chips`

### TC-13: Tag chip toggle
- **AC:** AC4
- **Given:** Modal open
- **When:** Chip clicked
- **Then:** `.active` class toggled
- **Coverage:** ✅ Existing test `should toggle active on chip click`

### TC-14: Tag filter actually filters file list
- **AC:** AC4
- **Given:** Modal open with files having different tags
- **When:** Domain chip "Architecture" clicked
- **Then:** Only files with Architecture tag shown
- **Coverage:** 🆕 Added test `should filter file list when tag chip activated`

### TC-15: Checkbox updates selected count
- **AC:** AC5, AC6
- **Given:** Modal open
- **When:** File checkbox checked
- **Then:** Count shows "1 selected"
- **Coverage:** ✅ Existing test `should update selected count when checkbox checked`

### TC-16: Selected paths tracked in Set
- **AC:** AC5
- **Given:** Modal open
- **When:** File checkbox checked
- **Then:** `picker.selected` contains path
- **Coverage:** ✅ Existing test `should track selected paths`

### TC-17: Deselect reduces count
- **AC:** AC5, AC6
- **Given:** File already selected
- **When:** Checkbox unchecked
- **Then:** Count returns to "0 selected"
- **Coverage:** 🆕 Added test `should deselect and reduce count`

### TC-18: Copy button rendered
- **AC:** AC7
- **Given:** Modal open
- **When:** Modal rendered
- **Then:** `.kb-ref-copy-btn` present
- **Coverage:** ✅ Existing test `should render copy button`

### TC-19: Copy invokes clipboard API
- **AC:** AC7
- **Given:** 1 file selected
- **When:** Copy button clicked
- **Then:** `navigator.clipboard.writeText` called with path
- **Coverage:** ✅ Existing test `should call clipboard API on copy`

### TC-20: Multiple paths copied as newline-separated
- **AC:** AC7
- **Given:** 2 files selected
- **When:** Copy button clicked
- **Then:** Clipboard called with paths joined by `\n`
- **Coverage:** 🆕 Added test `should copy multiple paths newline-separated`

### TC-21: Insert button rendered
- **AC:** AC8
- **Given:** Modal open
- **When:** Modal rendered
- **Then:** `.kb-ref-insert-btn` present
- **Coverage:** ✅ Existing test `should render insert button`

### TC-22: Insert calls onInsert callback
- **AC:** AC8
- **Given:** File selected, onInsert provided
- **When:** Insert clicked
- **Then:** onInsert called with paths array
- **Coverage:** ✅ Existing test `should call onInsert callback`

### TC-23: Insert dispatches custom event
- **AC:** AC8
- **Given:** File selected
- **When:** Insert clicked
- **Then:** `kb:references-inserted` event dispatched with paths
- **Coverage:** ✅ Existing test `should dispatch kb:references-inserted event`

### TC-24: Body scroll locked on open
- **AC:** AC12
- **Given:** Body scrollable
- **When:** Picker opened
- **Then:** `document.body.style.overflow === 'hidden'`
- **Coverage:** 🆕 Added test `should lock body scroll on open`

### TC-25: Body scroll restored on close
- **AC:** AC12
- **Given:** Modal open (scroll locked)
- **When:** Picker closed
- **Then:** `document.body.style.overflow === ''`
- **Coverage:** 🆕 Added test `should restore body scroll on close`

### TC-26: Empty tree shows placeholder
- **AC:** AC11
- **Given:** API returns empty tree
- **When:** Modal rendered
- **Then:** "No folders" message shown
- **Coverage:** 🆕 Added test `should show empty message when no folders`

### TC-27: API failure handled gracefully
- **AC:** AC11
- **Given:** All API calls reject
- **When:** `open()` called
- **Then:** Modal still opens without crashing
- **Coverage:** 🆕 Added test `should handle API failure gracefully`

### TC-28: HTML escaping in file names
- **AC:** AC10
- **Given:** File name contains `<script>alert(1)</script>`
- **When:** File list rendered
- **Then:** Script tag is escaped, not executed
- **Coverage:** 🆕 Added test `should escape HTML in file names`

---

## Coverage Summary

| Status | Count |
|--------|-------|
| ✅ Existing (pre-refactor) | 19 |
| 🆕 New tests added | 10 |
| **Total** | **29** |
