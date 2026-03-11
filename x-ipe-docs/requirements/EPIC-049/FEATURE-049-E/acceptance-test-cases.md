# Acceptance Test Cases

> Feature: FEATURE-049-E - KB File Upload
> Generated: 2025-07-13
> Status: Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-049-E |
| Feature Title | KB File Upload |
| Total Test Cases | 41 |
| Priority | P0 (Critical) |
| Target URL | N/A (unit tests via vitest) |

---

## Prerequisites

- [x] Feature is deployed and accessible
- [x] Test environment is ready
- [x] `KBFileUpload` class is implemented in `kb-file-upload.js`
- [x] Mock API endpoints available (`/api/kb/tree`, `/api/kb/upload`, `/api/kb/folders`)
- [x] vitest configured with jsdom environment

---

## Test Cases

### TC-001: KBFileUpload Class Export

**Acceptance Criteria Reference:** AC-049-E-01 from specification.md

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- `kb-file-upload.js` is loaded via `loadFeatureScript`

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `typeof globalThis.KBFileUpload` | `'function'` | Class constructor |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Check global export | `globalThis.KBFileUpload` | — | typeof is `'function'` |

**Expected Outcome:** KBFileUpload is exported as a constructor function.

**Status:** ✅ Pass

**Execution Notes:** Test: `should export KBFileUpload class`

---

### TC-002: Modal Overlay Creation

**Acceptance Criteria Reference:** AC-049-E-01 from specification.md

**Priority:** P0

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- KBFileUpload instance created
- Fetch mock returns tree data

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-overlay` | not null | Overlay appended to DOM |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create uploader | `new KBFileUpload()` | — | Instance created |
| 2 | Call open | `uploader.open()` | — | Overlay appended |
| 3 | Query overlay | `.kb-upload-overlay` | — | Element exists |

**Expected Outcome:** Modal overlay is appended to the document body on open().

**Status:** ✅ Pass

**Execution Notes:** Test: `should create overlay on open`

---

### TC-003: Modal Active Class Animation

**Acceptance Criteria Reference:** AC-049-E-01 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal opened via `open()`

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-overlay.active` | true | Class added after rAF |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal visible |
| 2 | Wait 50ms | — | — | Animation frame fires |
| 3 | Check class | `.kb-upload-overlay` | — | Has `active` class |

**Expected Outcome:** The `active` class is added after open for fade-in animation.

**Status:** ✅ Pass

**Execution Notes:** Test: `should add active class after open`

---

### TC-004: Modal Close Removes Overlay

**Acceptance Criteria Reference:** AC-049-E-01 from specification.md

**Priority:** P0

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-overlay` | null | Removed from DOM |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Overlay exists |
| 2 | Close modal | `uploader.close()` | — | Fade-out starts |
| 3 | Wait 350ms | — | — | Animation completes |
| 4 | Query overlay | `.kb-upload-overlay` | — | null (removed) |

**Expected Outcome:** Overlay is removed from the DOM after close animation.

**Status:** ✅ Pass

**Execution Notes:** Test: `should remove overlay on close`

---

### TC-005: Close on Overlay Background Click

**Acceptance Criteria Reference:** AC-049-E-01 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Click target | `.kb-upload-overlay` | Background area |
| Expected | `.kb-upload-overlay` | null | Removed from DOM |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Overlay exists |
| 2 | Click overlay | `.kb-upload-overlay` | click event | Close triggered |
| 3 | Wait 350ms | — | — | Animation completes |
| 4 | Query overlay | `.kb-upload-overlay` | — | null (removed) |

**Expected Outcome:** Clicking the overlay background closes the modal.

**Status:** ✅ Pass

**Execution Notes:** Test: `should close on overlay background click`

---

### TC-006: Body Scroll Lock and Restore

**Acceptance Criteria Reference:** AC-049-E-01 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Page body is scrollable

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected (open) | `document.body.style.overflow` | `'hidden'` | Scroll locked |
| Expected (close) | `document.body.style.overflow` | `''` | Scroll restored |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Body overflow = `hidden` |
| 2 | Close modal | `uploader.close()` | — | Body overflow = `''` |

**Expected Outcome:** Body scroll is locked on open and restored on close.

**Status:** ✅ Pass

**Execution Notes:** Test: `should lock body scroll when open and restore on close`

---

### TC-007: Upload Header Display

**Acceptance Criteria Reference:** AC-049-E-01 from specification.md

**Priority:** P2

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-header h3` | Contains "Upload" | Header text |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal rendered |
| 2 | Check header | `.kb-upload-header h3` | — | Contains "Upload" |

**Expected Outcome:** Modal header displays "Upload Files" title.

**Status:** ✅ Pass

**Execution Notes:** Test: `should show upload header`

---

### TC-008: Dropzone Rendering

**Acceptance Criteria Reference:** AC-049-E-02 from specification.md

**Priority:** P0

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-dropzone` | not null | Dropzone element exists |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal rendered |
| 2 | Query dropzone | `.kb-upload-dropzone` | — | Element exists |

**Expected Outcome:** Drag-and-drop zone is rendered in the modal.

**Status:** ✅ Pass

**Execution Notes:** Test: `should render dropzone`

---

### TC-009: Dragover Visual Highlight

**Acceptance Criteria Reference:** AC-049-E-02 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, dropzone rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Event | `dragover` | On dropzone |
| Expected | `.kb-upload-dropzone` | Has `dragover` class | Visual highlight |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Dropzone rendered |
| 2 | Dispatch dragover | `.kb-upload-dropzone` | dragover event | `dragover` class added |

**Expected Outcome:** Dropzone visually highlights with `dragover` class on drag.

**Status:** ✅ Pass

**Execution Notes:** Test: `should add dragover class on dragover`

---

### TC-010: Dragleave Removes Highlight

**Acceptance Criteria Reference:** AC-049-E-02 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, dropzone has `dragover` class

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Event | `dragleave` | On dropzone |
| Expected | `.kb-upload-dropzone` | No `dragover` class | Highlight removed |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Add dragover class | `.kb-upload-dropzone` | — | Class present |
| 2 | Dispatch dragleave | `.kb-upload-dropzone` | dragleave event | `dragover` class removed |

**Expected Outcome:** The `dragover` visual state is removed when drag leaves the zone.

**Status:** ✅ Pass

**Execution Notes:** Test: `should remove dragover class on dragleave`

---

### TC-011: Drop Triggers Upload

**Acceptance Criteria Reference:** AC-049-E-02 from specification.md

**Priority:** P0

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, fetch mock configured for upload

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `test.md` (text/markdown) | Dropped file |
| Expected | Fetch call | `/api/kb/upload` | Upload API called |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Dropzone rendered |
| 2 | Create file | `new File(['hello'], 'test.md')` | — | File object created |
| 3 | Dispatch drop | `.kb-upload-dropzone` | drop event with file | Upload triggered |
| 4 | Wait 50ms | — | — | API called |
| 5 | Check fetch calls | `/api/kb/upload` | — | Upload endpoint called |

**Expected Outcome:** Dropping files on the dropzone triggers the upload flow.

**Status:** ✅ Pass

**Execution Notes:** Test: `should trigger upload on drop`

---

### TC-012: File Input with Multiple Attribute

**Acceptance Criteria Reference:** AC-049-E-03 from specification.md

**Priority:** P0

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-file-input` | not null, `multiple=true` | Supports multi-file |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal rendered |
| 2 | Query file input | `.kb-upload-file-input` | — | Element exists |
| 3 | Check multiple attr | `.kb-upload-file-input.multiple` | — | true |

**Expected Outcome:** Hidden file input supports multiple file selection.

**Status:** ✅ Pass

**Execution Notes:** Test: `should render file input`

---

### TC-013: Folder Dropdown Rendering

**Acceptance Criteria Reference:** AC-049-E-04 from specification.md

**Priority:** P0

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, tree API returns folder data

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-folder-dropdown` | not null | Select element rendered |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Tree API called |
| 2 | Query dropdown | `.kb-upload-folder-dropdown` | — | Element exists |

**Expected Outcome:** Folder destination dropdown is rendered from tree API data.

**Status:** ✅ Pass

**Execution Notes:** Test: `should render folder dropdown`

---

### TC-014: Root Option in Dropdown

**Acceptance Criteria Reference:** AC-049-E-04 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, dropdown rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | First `<option>` value | `''` (empty) | Root path |
| Expected | First `<option>` text | Contains "root" | Label |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Dropdown rendered |
| 2 | Get first option | `.kb-upload-folder-dropdown option:first-child` | — | Value `''`, text contains "root" |

**Expected Outcome:** The `/ (root)` option appears as the first dropdown item.

**Status:** ✅ Pass

**Execution Notes:** Test: `should include root option`

---

### TC-015: Folder Tree Listing

**Acceptance Criteria Reference:** AC-049-E-04 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Tree API returns `guides` folder with `intro` subfolder

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Tree API | `[{name:'guides', children:[{name:'intro'}]}]` | Nested folders |
| Expected | Option count | 3 | root + guides + intro |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Tree loaded |
| 2 | Count options | `.kb-upload-folder-dropdown option` | — | 3 options |

**Expected Outcome:** All folders (including nested) are listed; files are excluded.

**Status:** ✅ Pass

**Execution Notes:** Test: `should list folders from tree`

---

### TC-016: Folder Dropdown Change Updates Selection

**Acceptance Criteria Reference:** AC-049-E-04 from specification.md

**Priority:** P0

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, dropdown has folder options

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Dropdown value | `'guides'` | Selected folder |
| Expected | `uploader.folder` | `'guides'` | Property updated |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Dropdown rendered |
| 2 | Set dropdown value | `.kb-upload-folder-dropdown` | `'guides'` | Value set |
| 3 | Dispatch change | `.kb-upload-folder-dropdown` | change event | Folder updated |
| 4 | Check property | `uploader.folder` | — | `'guides'` |

**Expected Outcome:** Selecting a folder updates the `folder` property for subsequent uploads.

**Status:** ✅ Pass

**Execution Notes:** Test: `should update folder on dropdown change`

---

### TC-017: Pre-Select Folder from Constructor

**Acceptance Criteria Reference:** AC-049-E-04 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Tree API returns `guides` folder

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Constructor option | `{ folder: 'guides' }` | Pre-select |
| Expected | Dropdown value | `'guides'` | Auto-selected |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create uploader | `new KBFileUpload({ folder: 'guides' })` | — | Instance with folder |
| 2 | Open modal | `uploader.open()` | — | Dropdown rendered |
| 3 | Check dropdown | `.kb-upload-folder-dropdown` | — | Value is `'guides'` |

**Expected Outcome:** Dropdown pre-selects the folder passed via constructor option.

**Status:** ✅ Pass

**Execution Notes:** Test: `should pre-select folder from constructor option`

---

### TC-018: New Folder Button Rendering

**Acceptance Criteria Reference:** AC-049-E-05 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-newfolder-btn` | not null | Button exists |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal rendered |
| 2 | Query button | `.kb-upload-newfolder-btn` | — | Element exists |

**Expected Outcome:** The "+ Folder" button is rendered in the modal.

**Status:** ✅ Pass

**Execution Notes:** Test: `should show new folder button`

---

### TC-019: Toggle New Folder Input

**Acceptance Criteria Reference:** AC-049-E-05 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, new folder input initially hidden

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected (before) | `.kb-upload-newfolder-input` display | `'none'` | Hidden |
| Expected (after) | `.kb-upload-newfolder-input` display | `'flex'` | Visible |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Input hidden |
| 2 | Click button | `.kb-upload-newfolder-btn` | click | Input visible (`flex`) |

**Expected Outcome:** Clicking "+ Folder" toggles the inline folder creation input.

**Status:** ✅ Pass

**Execution Notes:** Test: `should toggle new folder input on button click`

---

### TC-020: Create Folder via API and Refresh

**Acceptance Criteria Reference:** AC-049-E-05 from specification.md

**Priority:** P0

**Test Type:** integration

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, fetch mock handles `/api/kb/folders`

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Folder name | `'new-folder'` | Text field value |
| Expected | Fetch call | `/api/kb/folders` | POST request |
| Expected | `uploader.folder` | `'new-folder'` | Updated selection |
| Expected | Event | `kb:changed` | Dispatched |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal rendered |
| 2 | Set name | `.kb-newfolder-name` | `'new-folder'` | Value set |
| 3 | Click create | `.kb-newfolder-create-btn` | click | API called |
| 4 | Wait 50ms | — | — | Response processed |
| 5 | Check API call | Fetch mock | — | `/api/kb/folders` called |
| 6 | Check folder | `uploader.folder` | — | `'new-folder'` |
| 7 | Check event | `kb:changed` listener | — | Event dispatched |

**Expected Outcome:** New folder is created via API, dropdown refreshes, new folder is selected, and `kb:changed` event fires.

**Status:** ✅ Pass

**Execution Notes:** Test: `should create new folder via API and refresh dropdown`

---

### TC-021: Empty Folder Name Rejection

**Acceptance Criteria Reference:** AC-049-E-05 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, new folder input visible

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Folder name | `'   '` | Whitespace only |
| Expected | Fetch call to `/api/kb/folders` | undefined | No API call |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal rendered |
| 2 | Set name | `.kb-newfolder-name` | `'   '` | Whitespace |
| 3 | Click create | `.kb-newfolder-create-btn` | click | No API call |
| 4 | Check fetch | Fetch mock | — | No `/api/kb/folders` call |

**Expected Outcome:** Empty or whitespace-only folder names are silently rejected without an API call.

**Status:** ✅ Pass

**Execution Notes:** Test: `should ignore empty folder name on create`

---

### TC-022: Cancel Hides New Folder Input

**Acceptance Criteria Reference:** AC-049-E-05 from specification.md

**Priority:** P2

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, new folder input is visible

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-upload-newfolder-input` display | `'none'` | Hidden after cancel |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal rendered |
| 2 | Show input | `.kb-upload-newfolder-btn` click | — | Input visible |
| 3 | Click cancel | `.kb-newfolder-cancel-btn` | click | Input hidden |

**Expected Outcome:** Clicking "Cancel" hides the new folder input row.

**Status:** ✅ Pass

**Execution Notes:** Test: `should hide new folder input on cancel`

---

### TC-023: Upload API Call with FormData

**Acceptance Criteria Reference:** AC-049-E-06 from specification.md

**Priority:** P0

**Test Type:** integration

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, folder set to `'guides'`

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `test.md` (text/markdown) | Valid file |
| Input | Folder | `'guides'` | Constructor option |
| Expected | Fetch call | `/api/kb/upload` | POST with FormData |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create uploader | `new KBFileUpload({ folder: 'guides' })` | — | Instance |
| 2 | Open modal | `uploader.open()` | — | Modal ready |
| 3 | Upload file | `uploader._uploadFiles([file])` | `test.md` | API called |
| 4 | Check fetch | Fetch mock | — | `/api/kb/upload` called |

**Expected Outcome:** Files are uploaded via `POST /api/kb/upload` with FormData.

**Status:** ✅ Pass

**Execution Notes:** Test: `should call upload API with FormData`

---

### TC-024: kb:changed Event on Successful Upload

**Acceptance Criteria Reference:** AC-049-E-06 from specification.md

**Priority:** P0

**Test Type:** integration

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, upload API returns success

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `test.md` | Valid file |
| Expected | Event | `kb:changed` | Dispatched on document |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal ready |
| 2 | Add event listener | `document` | `kb:changed` | Listener attached |
| 3 | Upload file | `uploader._uploadFiles([file])` | `test.md` | Upload succeeds |
| 4 | Check event | listener flag | — | Event was dispatched |

**Expected Outcome:** A `kb:changed` custom event is dispatched after successful upload.

**Status:** ✅ Pass

**Execution Notes:** Test: `should dispatch kb:changed on successful upload`

---

### TC-025: Success Status Display

**Acceptance Criteria Reference:** AC-049-E-06 from specification.md

**Priority:** P1

**Test Type:** frontend-ui

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open, upload API returns success

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `test.md` | Valid file |
| Expected | `.kb-upload-success` count | 1 | Success indicator |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal ready |
| 2 | Upload file | `uploader._uploadFiles([file])` | `test.md` | Upload succeeds |
| 3 | Query success items | `.kb-upload-success` | — | 1 element found |

**Expected Outcome:** Successfully uploaded files show "✅ Uploaded" status.

**Status:** ✅ Pass

**Execution Notes:** Test: `should show success status for uploaded files`

---

### TC-026: Error Status for Server-Rejected Files

**Acceptance Criteria Reference:** AC-049-E-06, AC-049-E-11 from specification.md

**Priority:** P0

**Test Type:** integration

**Assigned Tool:** vitest

**Preconditions:**
- Upload API returns error for the submitted file

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `bad.txt` | Unsupported type |
| Input | API response | `{ errors: [{ file: 'bad.txt', error: 'Invalid format' }] }` | Server rejection |
| Expected | `.kb-upload-error` count | 1 | Error indicator |
| Expected | Error text | Contains "Invalid format" | Server error message |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Override fetch mock | Upload returns error | — | Mock configured |
| 2 | Open modal | `uploader.open()` | — | Modal ready |
| 3 | Upload file | `uploader._uploadFiles([file])` | `bad.txt` | Server rejects |
| 4 | Query errors | `.kb-upload-error` | — | 1 element, text contains "Invalid format" |

**Expected Outcome:** Server-rejected files display the error message in the progress list.

**Status:** ✅ Pass

**Execution Notes:** Test: `should show error status for server-rejected files`

---

### TC-027: onComplete Callback

**Acceptance Criteria Reference:** AC-049-E-06 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBFileUpload created with `onComplete` callback

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Constructor option | `{ onComplete: vi.fn() }` | Callback function |
| Expected | Callback | Called once | After successful upload |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create uploader | `new KBFileUpload({ onComplete: cb })` | — | Instance with callback |
| 2 | Open modal | `uploader.open()` | — | Modal ready |
| 3 | Upload file | `uploader._uploadFiles([file])` | `test.md` | Upload succeeds |
| 4 | Check callback | `cb` | — | Called once |

**Expected Outcome:** The `onComplete` callback is invoked after successful uploads.

**Status:** ✅ Pass

**Execution Notes:** Test: `should call onComplete callback on successful upload`

---

### TC-028: .zip Archive Auto-Extraction

**Acceptance Criteria Reference:** AC-049-E-07 from specification.md

**Priority:** P0

**Test Type:** backend-api

**Assigned Tool:** pytest

**Preconditions:**
- Backend running with `POST /api/kb/upload` endpoint
- `.zip` file available for upload

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `archive.zip` containing files | ZIP archive |
| Input | Destination folder | `'guides'` | Target folder |
| Expected | Response `uploaded` array | Contains extracted file entries | Preserves internal structure |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | POST upload | `/api/kb/upload` | `archive.zip` + folder=guides | Archive received |
| 2 | Check response | `uploaded` array | — | Extracted files listed |
| 3 | Check structure | File system | — | Internal folder structure preserved |

**Expected Outcome:** .zip archives are auto-extracted server-side, preserving internal folder structure.

**Status:** ⬜ Not Run

**Execution Notes:** Backend integration test needed — no frontend test coverage for server-side extraction logic. Covered in `kb_routes.py` lines 447-449.

---

### TC-029: .7z Archive Auto-Extraction

**Acceptance Criteria Reference:** AC-049-E-08 from specification.md

**Priority:** P0

**Test Type:** backend-api

**Assigned Tool:** pytest

**Preconditions:**
- Backend running with `POST /api/kb/upload` endpoint
- `.7z` file available for upload
- `py7zr` library installed

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `archive.7z` containing files | 7z archive |
| Input | Destination folder | `'guides'` | Target folder |
| Expected | Response `uploaded` array | Contains extracted file entries | Preserves internal structure |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | POST upload | `/api/kb/upload` | `archive.7z` + folder=guides | Archive received |
| 2 | Check response | `uploaded` array | — | Extracted files listed |
| 3 | Check structure | File system | — | Internal folder structure preserved |

**Expected Outcome:** .7z archives are auto-extracted server-side, preserving internal folder structure.

**Status:** ⬜ Not Run

**Execution Notes:** Backend integration test needed — no frontend test coverage for server-side extraction logic. Covered in `kb_routes.py` lines 450-452.

---

### TC-030: Nested Archive Handling

**Acceptance Criteria Reference:** AC-049-E-09 from specification.md

**Priority:** P1

**Test Type:** backend-api

**Assigned Tool:** pytest

**Preconditions:**
- Backend running with `POST /api/kb/upload` endpoint
- Archive containing nested archives available

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `outer.zip` containing `inner.zip` | Nested archive |
| Expected | `inner.zip` | Stored as-is | Not recursively extracted |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | POST upload | `/api/kb/upload` | `outer.zip` | Outer extracted |
| 2 | Check nested | File system | — | `inner.zip` stored as file, not extracted |

**Expected Outcome:** Nested archives within extracted content are stored as-is without recursive extraction.

**Status:** ⬜ Not Run

**Execution Notes:** Backend integration test needed — no frontend test coverage for nested archive behavior.

---

### TC-031: Files Over 10MB Rejected Client-Side

**Acceptance Criteria Reference:** AC-049-E-10 from specification.md

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File | `big.md` with size 11 MB | Oversized file |
| Expected | `.kb-upload-error` count | 1 | Rejected |
| Expected | Error text | Contains "Too large" | Client-side rejection |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal ready |
| 2 | Create oversized file | `File` with size > 10MB | — | 11 MB file |
| 3 | Upload file | `uploader._uploadFiles([file])` | — | Client-side rejection |
| 4 | Check error | `.kb-upload-error` | — | Contains "Too large" |

**Expected Outcome:** Files exceeding 10 MB are immediately rejected client-side with "Too large" status.

**Status:** ✅ Pass

**Execution Notes:** Test: `should reject files over 10MB`

---

### TC-032: Mixed Valid and Oversized Files

**Acceptance Criteria Reference:** AC-049-E-10 from specification.md

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File 1 | `ok.md` (small) | Valid file |
| Input | File 2 | `huge.md` (11 MB) | Oversized file |
| Expected | `.kb-upload-success` count | 1 | Valid file uploaded |
| Expected | `.kb-upload-error` count | 1 | Oversized rejected |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal ready |
| 2 | Create mixed files | valid + oversized | — | Two files |
| 3 | Upload both | `uploader._uploadFiles([valid, large])` | — | Mixed processing |
| 4 | Check success | `.kb-upload-success` | — | 1 success |
| 5 | Check error | `.kb-upload-error` | — | 1 error |

**Expected Outcome:** Only valid files are sent to server; oversized files show rejection status alongside upload results.

**Status:** ✅ Pass

**Execution Notes:** Test: `should handle mixed valid and oversized files`

---

### TC-033: HTML Escaping in File Names

**Acceptance Criteria Reference:** AC-049-E-12 from specification.md

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Modal is open

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | File name | `<script>alert(1)</script>.md` | XSS payload |
| Expected | `.kb-upload-fname` innerHTML | Does not contain `<script>` | Escaped |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open modal | `uploader.open()` | — | Modal ready |
| 2 | Upload XSS file | `uploader._uploadFiles([file])` | Script-tagged name | File processed |
| 3 | Check rendering | `.kb-upload-fname` | — | innerHTML has no `<script>` tag |

**Expected Outcome:** File names with HTML/script characters are escaped and rendered as plain text.

**Status:** ✅ Pass

**Execution Notes:** Test: `should escape HTML in file names`

---

### TC-034: Network Error Handling

**Acceptance Criteria Reference:** AC-049-E-13 from specification.md

**Priority:** P0

**Test Type:** integration

**Assigned Tool:** vitest

**Preconditions:**
- Upload API configured to reject with network error

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Fetch behavior | `Promise.reject(new Error('Network failure'))` | Simulated failure |
| Expected | `.kb-upload-error` count | 1 | All files marked failed |
| Expected | Error text | Contains "Upload failed" | Error status |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Override fetch | Upload rejects | — | Network error simulated |
| 2 | Open modal | `uploader.open()` | — | Modal ready |
| 3 | Upload file | `uploader._uploadFiles([file])` | `test.md` | Network error |
| 4 | Check error | `.kb-upload-error` | — | Contains "Upload failed" |

**Expected Outcome:** All in-progress files are marked with "Upload failed" status on network error.

**Status:** ✅ Pass

**Execution Notes:** Test: `should handle network error gracefully`

---

### TC-035: Constructor Accepts Folder Option

**Acceptance Criteria Reference:** AC-049-E-04 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- None

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Constructor option | `{ folder: 'guides/intro' }` | Folder path |
| Expected | `uploader.folder` | `'guides/intro'` | Property set |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create uploader | `new KBFileUpload({ folder: 'guides/intro' })` | — | Instance created |
| 2 | Check property | `uploader.folder` | — | `'guides/intro'` |

**Expected Outcome:** Constructor correctly accepts and stores the folder option.

**Status:** ✅ Pass

**Execution Notes:** Test: `should accept folder option`

---

### TC-036: Constructor Accepts onComplete Callback

**Acceptance Criteria Reference:** AC-049-E-06 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- None

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | Constructor option | `{ onComplete: vi.fn() }` | Callback |
| Expected | `uploader.onComplete` | Same function reference | Property set |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create callback | `vi.fn()` | — | Mock function |
| 2 | Create uploader | `new KBFileUpload({ onComplete: cb })` | — | Instance created |
| 3 | Check property | `uploader.onComplete` | — | Same as `cb` |

**Expected Outcome:** Constructor correctly accepts and stores the onComplete callback.

**Status:** ✅ Pass

**Execution Notes:** Test: `should accept onComplete callback`

---

## Test Execution Summary

| Test Case | Title | Type | Priority | Status | Notes |
|-----------|-------|------|----------|--------|-------|
| TC-001 | KBFileUpload Class Export | unit | P0 | ✅ Pass | `should export KBFileUpload class` |
| TC-002 | Modal Overlay Creation | frontend-ui | P0 | ✅ Pass | `should create overlay on open` |
| TC-003 | Modal Active Class Animation | frontend-ui | P1 | ✅ Pass | `should add active class after open` |
| TC-004 | Modal Close Removes Overlay | frontend-ui | P0 | ✅ Pass | `should remove overlay on close` |
| TC-005 | Close on Overlay Background Click | frontend-ui | P1 | ✅ Pass | `should close on overlay background click` |
| TC-006 | Body Scroll Lock and Restore | frontend-ui | P1 | ✅ Pass | `should lock body scroll when open and restore on close` |
| TC-007 | Upload Header Display | frontend-ui | P2 | ✅ Pass | `should show upload header` |
| TC-008 | Dropzone Rendering | frontend-ui | P0 | ✅ Pass | `should render dropzone` |
| TC-009 | Dragover Visual Highlight | frontend-ui | P1 | ✅ Pass | `should add dragover class on dragover` |
| TC-010 | Dragleave Removes Highlight | frontend-ui | P1 | ✅ Pass | `should remove dragover class on dragleave` |
| TC-011 | Drop Triggers Upload | frontend-ui | P0 | ✅ Pass | `should trigger upload on drop` |
| TC-012 | File Input with Multiple Attribute | frontend-ui | P0 | ✅ Pass | `should render file input` |
| TC-013 | Folder Dropdown Rendering | frontend-ui | P0 | ✅ Pass | `should render folder dropdown` |
| TC-014 | Root Option in Dropdown | frontend-ui | P1 | ✅ Pass | `should include root option` |
| TC-015 | Folder Tree Listing | frontend-ui | P1 | ✅ Pass | `should list folders from tree` |
| TC-016 | Folder Dropdown Change Updates Selection | frontend-ui | P0 | ✅ Pass | `should update folder on dropdown change` |
| TC-017 | Pre-Select Folder from Constructor | frontend-ui | P1 | ✅ Pass | `should pre-select folder from constructor option` |
| TC-018 | New Folder Button Rendering | frontend-ui | P1 | ✅ Pass | `should show new folder button` |
| TC-019 | Toggle New Folder Input | frontend-ui | P1 | ✅ Pass | `should toggle new folder input on button click` |
| TC-020 | Create Folder via API and Refresh | integration | P0 | ✅ Pass | `should create new folder via API and refresh dropdown` |
| TC-021 | Empty Folder Name Rejection | unit | P1 | ✅ Pass | `should ignore empty folder name on create` |
| TC-022 | Cancel Hides New Folder Input | frontend-ui | P2 | ✅ Pass | `should hide new folder input on cancel` |
| TC-023 | Upload API Call with FormData | integration | P0 | ✅ Pass | `should call upload API with FormData` |
| TC-024 | kb:changed Event on Successful Upload | integration | P0 | ✅ Pass | `should dispatch kb:changed on successful upload` |
| TC-025 | Success Status Display | frontend-ui | P1 | ✅ Pass | `should show success status for uploaded files` |
| TC-026 | Error Status for Server-Rejected Files | integration | P0 | ✅ Pass | `should show error status for server-rejected files` |
| TC-027 | onComplete Callback | unit | P1 | ✅ Pass | `should call onComplete callback on successful upload` |
| TC-028 | .zip Archive Auto-Extraction | backend-api | P0 | ⬜ Not Run | Backend integration test needed |
| TC-029 | .7z Archive Auto-Extraction | backend-api | P0 | ⬜ Not Run | Backend integration test needed |
| TC-030 | Nested Archive Handling | backend-api | P1 | ⬜ Not Run | Backend integration test needed |
| TC-031 | Files Over 10MB Rejected Client-Side | unit | P0 | ✅ Pass | `should reject files over 10MB` |
| TC-032 | Mixed Valid and Oversized Files | unit | P0 | ✅ Pass | `should handle mixed valid and oversized files` |
| TC-033 | HTML Escaping in File Names | unit | P0 | ✅ Pass | `should escape HTML in file names` |
| TC-034 | Network Error Handling | integration | P0 | ✅ Pass | `should handle network error gracefully` |
| TC-035 | Constructor Accepts Folder Option | unit | P2 | ✅ Pass | `should accept folder option` |
| TC-036 | Constructor Accepts onComplete Callback | unit | P2 | ✅ Pass | `should accept onComplete callback` |

---

## Execution Results

**Execution Date:** 2026-03-11 (re-run after spec/design/code changes)
**Executed By:** Echo 📡
**Environment:** dev (vitest + jsdom + pytest)

| Metric | Value |
|--------|-------|
| Total Tests | 41 |
| Passed | 41 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Test Type | Passed | Total | Tool |
|-----------|--------|-------|------|
| Unit (frontend) | 33 | 33 | vitest |
| Unit (backend) | 8 | 8 | pytest |

**Test Runners:**
- `npx vitest run tests/frontend-js/kb-file-upload.test.js`
- `uv run python -m pytest tests/test_kb_service.py -k "Zip or SevenZip or Nested or upload" -v`

> **Previously blocked TCs now passing:** TC-028 (.zip extraction), TC-029 (.7z extraction), TC-030 (nested archive handling) — covered by Python pytest tests added in TASK-847. Additionally, 4 route-level upload tests added (single file, subfolder, zip auto-extract, no-files error).
