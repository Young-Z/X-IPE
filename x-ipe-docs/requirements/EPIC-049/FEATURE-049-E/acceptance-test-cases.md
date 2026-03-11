# FEATURE-049-E: KB File Upload — Acceptance Test Cases

**Feature:** KB File Upload (drag-drop upload zone, folder destination picker, archive auto-extraction)
**Test File:** `tests/frontend-js/kb-file-upload.test.js`
**Total Tests:** 33 (20 original + 13 added)

---

## AC-1: Modal Lifecycle

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 1.1 | KBFileUpload class is exported | ✅ | should export KBFileUpload class |
| 1.2 | Overlay created on `open()` | ✅ | should create overlay on open |
| 1.3 | Active class added for animation | ✅ | should add active class after open |
| 1.4 | Overlay removed on close | ✅ | should remove overlay on close |
| 1.5 | Close on overlay background click | ✅ | should close on overlay background click |
| 1.6 | Body scroll locked/restored | ✅ | should lock body scroll when open and restore on close |
| 1.7 | Header shows "Upload" title | ✅ | should show upload header |

## AC-2: Folder Selection

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 2.1 | Folder dropdown rendered | ✅ | should render folder dropdown |
| 2.2 | Root option included | ✅ | should include root option |
| 2.3 | Folders from tree listed (files excluded) | ✅ | should list folders from tree |
| 2.4 | Dropdown change updates `this.folder` | ✅ | should update folder on dropdown change |
| 2.5 | Pre-selects folder from constructor | ✅ | should pre-select folder from constructor option |

## AC-3: New Folder Creation

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 3.1 | New folder button rendered | ✅ | should show new folder button |
| 3.2 | Toggle new folder input | ✅ | should toggle new folder input on button click |
| 3.3 | Create folder via API + refresh | ✅ | should create new folder via API and refresh dropdown |
| 3.4 | Empty name ignored | ✅ | should ignore empty folder name on create |
| 3.5 | Cancel hides input | ✅ | should hide new folder input on cancel |

## AC-4: Drag-and-Drop

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 4.1 | Dropzone rendered | ✅ | should render dropzone |
| 4.2 | Dragover class added | ✅ | should add dragover class on dragover |
| 4.3 | Dragover class removed on leave | ✅ | should remove dragover class on dragleave |
| 4.4 | Drop triggers upload | ✅ | should trigger upload on drop |

## AC-5: File Input (Browse)

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 5.1 | Hidden file input with `multiple` | ✅ | should render file input |

## AC-6: File Validation

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 6.1 | Files over 10MB rejected | ✅ | should reject files over 10MB |
| 6.2 | Mixed valid + oversized handled | ✅ | should handle mixed valid and oversized files |

## AC-7: Upload Flow

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 7.1 | Calls POST /api/kb/upload with FormData | ✅ | should call upload API with FormData |
| 7.2 | Dispatches kb:changed event | ✅ | should dispatch kb:changed on successful upload |
| 7.3 | Shows success status | ✅ | should show success status for uploaded files |
| 7.4 | Shows error for server-rejected files | ✅ | should show error status for server-rejected files |
| 7.5 | Handles network errors gracefully | ✅ | should handle network error gracefully |
| 7.6 | Calls onComplete callback | ✅ | should call onComplete callback on successful upload |

## AC-8: Security

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 8.1 | HTML-escapes file names in display | ✅ | should escape HTML in file names |

## AC-9: Constructor Options

| # | Test Case | Status | Test Name |
|---|-----------|--------|-----------|
| 9.1 | Accepts folder option | ✅ | should accept folder option |
| 9.2 | Accepts onComplete callback | ✅ | should accept onComplete callback |

## AC-10: Archive Extraction (Backend — POST /api/kb/upload)

| # | Test Case | Coverage | Notes |
|---|-----------|----------|-------|
| 10.1 | .zip auto-extracted server-side | Backend | Covered in `kb_routes.py` lines 447-449, tested via Python backend tests |
| 10.2 | .7z auto-extracted server-side | Backend | Covered in `kb_routes.py` lines 450-452, tested via Python backend tests |

---

## Summary

- **Frontend tests:** 33/33 passing
- **Coverage:** All frontend ACs fully covered
- **Backend ACs:** Archive extraction tested in backend test suite
