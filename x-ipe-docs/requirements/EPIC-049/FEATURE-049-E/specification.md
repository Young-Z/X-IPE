# Feature Specification: KB File Upload

> Feature ID: FEATURE-049-E  
> Version: v2.0  
> Status: Refined  
> Last Updated: 03-11-2026

## Version History

| Version | Date       | Description                                              |
|---------|------------|----------------------------------------------------------|
| v1.0    | 07-13-2025 | Retroactive specification from implemented code & tests  |
| v2.0    | 03-11-2026 | Template alignment — GWT format for ACs, Test Type Legend |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| KB Interface v1 (Scene 4 — Upload View) | HTML | [../../mockups/kb-interface-v1.html](../../mockups/kb-interface-v1.html) | Upload modal layout and interaction flow | current | 03-11-2026 |

## Overview

FEATURE-049-E provides a modal-based file upload experience for the Knowledge Base. Users can upload one or more files via drag-and-drop or a click-to-browse file picker, choose a destination folder from a dropdown tree, and create new folders inline — all without leaving the KB interface.

The upload flow validates files client-side (10 MB size limit), sends them to the `POST /api/kb/upload` endpoint as `multipart/form-data`, and displays per-file progress status (uploading → success/error). The backend handles archive extraction: `.zip` and `.7z` files are automatically unpacked, preserving their internal folder structure within the chosen destination.

The component is implemented as the `KBFileUpload` class (298 lines, vanilla JS) with an accompanying CSS file for modal styling. It integrates with the broader KB interface via the `kb:changed` custom event, which triggers sidebar and content panel refreshes after successful uploads or folder creation.

## User Stories

- **US-049-E-01:** As a knowledge base user, I want to drag-and-drop files into an upload zone so that I can quickly add documents without navigating file dialogs.
- **US-049-E-02:** As a knowledge base user, I want to browse and select files from my system so that I have an alternative to drag-and-drop.
- **US-049-E-03:** As a knowledge base user, I want to choose a destination folder before uploading so that files land in the correct location.
- **US-049-E-04:** As a knowledge base user, I want to create a new folder inline during upload so that I don't have to leave the upload flow to organize content.
- **US-049-E-05:** As a knowledge base user, I want to upload `.zip` or `.7z` archives and have them auto-extracted so that I can bulk-import structured content.
- **US-049-E-06:** As a knowledge base user, I want immediate feedback on upload success or failure per file so that I know which files were accepted.
- **US-049-E-07:** As a knowledge base user, I want files exceeding the size limit to be rejected before upload so that I don't waste time on failed transfers.

## Acceptance Criteria

### AC-049-E-01: Modal Lifecycle

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-01a | GIVEN KBFileUpload is instantiated WHEN `open()` is called THEN modal overlay appears with fade-in animation (`active` class), body scroll is locked, AND modal contains header ("📤 Upload Files"), folder selector, drop zone, and close button | UI |
| AC-049-E-01b | GIVEN upload modal is open WHEN user clicks close button or overlay background THEN modal fades out, is removed from DOM, AND body scroll is restored | UI |

### AC-049-E-02: Drag-and-Drop Upload

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-02a | GIVEN upload modal is open WHEN files are dragged over the drop zone THEN drop zone highlights with blue border and background tint (`dragover` class) | UI |
| AC-049-E-02b | GIVEN files are dragged over the drop zone WHEN user drops the files THEN `dragover` visual state is removed AND upload flow begins for all dropped files | UI |
| AC-049-E-02c | GIVEN files are dragged over the drop zone WHEN drag leaves the drop zone without a drop THEN `dragover` visual state is removed | UI |

### AC-049-E-03: File Picker Browse

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-03a | GIVEN upload modal is open WHEN user clicks drop zone or "browse" link THEN system file picker opens with `multiple` selection enabled | UI |
| AC-049-E-03b | GIVEN system file picker is open WHEN user selects files and confirms THEN upload flow begins for all selected files | UI |

### AC-049-E-04: Folder Selection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-04a | GIVEN upload modal is open AND `GET /api/kb/tree` returns folder data WHEN folder selector renders THEN `<select>` dropdown displays all KB folders in hierarchical indented list with `/ (root)` as first option | Integration |
| AC-049-E-04b | GIVEN upload modal is open WHEN user selects a folder from the dropdown THEN `folder` property updates to selected path AND subsequent uploads target that folder | UI |
| AC-049-E-04c | GIVEN `folder` option is passed to KBFileUpload constructor WHEN upload modal opens THEN dropdown pre-selects the matching folder | Unit |

### AC-049-E-05: Inline Folder Creation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-05a | GIVEN upload modal is open WHEN user clicks "+ Folder" button THEN inline input row with text field, "Create" button, and "Cancel" button appears | UI |
| AC-049-E-05b | GIVEN inline folder creation input is visible AND user enters a valid folder name WHEN user clicks "Create" button THEN `POST /api/kb/folders` request is sent with path, dropdown refreshes with new folder selected, AND `kb:changed` event is dispatched | Integration |
| AC-049-E-05c | GIVEN inline folder creation input is visible AND name field is empty or whitespace-only WHEN user clicks "Create" THEN no API call is made AND no folder is created | Unit |
| AC-049-E-05d | GIVEN inline folder creation input is visible WHEN user clicks "Cancel" THEN new-folder input row is hidden | UI |

### AC-049-E-06: Upload Progress & Feedback

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-06a | GIVEN user has selected files for upload WHEN upload begins THEN progress area shows each file name with "⏳ Uploading..." status indicator | UI |
| AC-049-E-06b | GIVEN files are uploading WHEN API responds THEN each successfully uploaded file shows "✅ Uploaded" AND each server-rejected file shows "❌ {error message}" | Integration |
| AC-049-E-06c | GIVEN files are uploading WHEN all uploads complete with at least one success THEN `kb:changed` event is dispatched AND `onComplete` callback is invoked | Integration |

### AC-049-E-07: Archive Extraction

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-07a | GIVEN user uploads a `.zip` archive file WHEN upload completes THEN archive is extracted preserving internal folder structure within destination folder AND all extracted files appear in response `uploaded` array | API |
| AC-049-E-08a | GIVEN user uploads a `.7z` archive file WHEN upload completes THEN archive is extracted preserving internal folder structure within destination folder AND all extracted files appear in response `uploaded` array | API |
| AC-049-E-09a | GIVEN an archive contains nested archive files WHEN the outer archive is extracted THEN nested archives are stored as-is without recursive extraction | API |

### AC-049-E-08: File Validation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-10a | GIVEN user selects a file exceeding 10 MB WHEN file validation runs THEN file is immediately rejected client-side with "❌ Too large (>10MB)" status AND excluded from FormData | Unit |
| AC-049-E-10b | GIVEN user selects a mix of valid and oversized files WHEN upload begins THEN only valid files are sent to server AND oversized files show rejection status alongside upload results | Unit |
| AC-049-E-11a | GIVEN user uploads a file with unsupported file type WHEN backend processes the upload THEN backend returns error entry with file name and descriptive message AND error is displayed in upload progress list | API |

### AC-049-E-09: Security & Error Handling

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-E-12a | GIVEN a file has HTML/script characters in its name (e.g., `<script>alert(1)</script>.md`) WHEN file name is rendered in the UI THEN name is escaped and rendered as plain text, preventing XSS | Unit |
| AC-049-E-13a | GIVEN files are uploading WHEN network request fails THEN all in-progress files are marked "❌ Upload failed" AND no `kb:changed` event is dispatched | Integration |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB)

## Functional Requirements

| ID           | Requirement                                                                                       |
|--------------|---------------------------------------------------------------------------------------------------|
| FR-049-E-01  | The component SHALL render as a modal overlay with `z-index: 1051` and backdrop blur.             |
| FR-049-E-02  | The modal SHALL contain a drag-and-drop zone that accepts files via HTML5 drag events.            |
| FR-049-E-03  | The drop zone SHALL also function as a click target that opens the native file picker.            |
| FR-049-E-04  | The file input SHALL support `multiple` file selection.                                           |
| FR-049-E-05  | The modal SHALL include a folder destination dropdown populated from `GET /api/kb/tree`.          |
| FR-049-E-06  | The dropdown SHALL display folders in hierarchical order with indentation indicating depth.       |
| FR-049-E-07  | The dropdown SHALL include a `/ (root)` option as the default destination.                       |
| FR-049-E-08  | A "+ Folder" button SHALL toggle an inline new-folder creation input.                             |
| FR-049-E-09  | New folder creation SHALL POST to `/api/kb/folders` with the computed path.                       |
| FR-049-E-10  | After folder creation, the dropdown SHALL refresh and select the newly created folder.            |
| FR-049-E-11  | Files SHALL be uploaded via `POST /api/kb/upload` using `multipart/form-data`.                    |
| FR-049-E-12  | The `FormData` SHALL include a `folder` field with the selected destination path.                 |
| FR-049-E-13  | Each file SHALL show individual upload status: pending → success or error.                        |
| FR-049-E-14  | Files exceeding 10 MB SHALL be rejected client-side before upload.                                |
| FR-049-E-15  | `.zip` files SHALL be auto-extracted server-side preserving internal folder structure.            |
| FR-049-E-16  | `.7z` files SHALL be auto-extracted server-side preserving internal folder structure.             |
| FR-049-E-17  | Nested archives within extracted content SHALL NOT be recursively extracted.                       |
| FR-049-E-18  | The component SHALL dispatch a `kb:changed` custom event on successful upload or folder creation. |
| FR-049-E-19  | File names displayed in the UI SHALL be HTML-escaped to prevent XSS.                              |
| FR-049-E-20  | The modal SHALL support an `onComplete` callback invoked after successful uploads.                |

## Non-Functional Requirements

| ID            | Requirement                                                                              |
|---------------|------------------------------------------------------------------------------------------|
| NFR-049-E-01  | Upload modal open/close transitions SHALL complete within 300ms.                         |
| NFR-049-E-02  | Client-side file validation SHALL be instantaneous (no server round-trip for size check). |
| NFR-049-E-03  | The component SHALL handle up to 100 MB compressed archives server-side (per NFR-049.5). |
| NFR-049-E-04  | All user-supplied strings (file names) SHALL be sanitized before DOM insertion.           |
| NFR-049-E-05  | The component SHALL gracefully handle network failures without crashing.                  |

## UI/UX Requirements

| ID            | Requirement                                                                                      |
|---------------|--------------------------------------------------------------------------------------------------|
| UIX-049-E-01  | Modal uses dark theme variables (`--bg-primary`, `--text-primary`, `--accent-primary`).           |
| UIX-049-E-02  | Drop zone uses a 2px dashed border with 10px radius; highlights blue on dragover/hover.          |
| UIX-049-E-03  | Modal has 12px border-radius, consistent with the X-IPE modal pattern.                           |
| UIX-049-E-04  | Modal max-width is 600px, max-height is 80vh, centered with flex layout.                         |
| UIX-049-E-05  | Body scroll is locked when modal is open and restored on close.                                  |
| UIX-049-E-06  | File status indicators use emoji icons: ⏳ (pending), ✅ (success), ❌ (error).                  |
| UIX-049-E-07  | File names are truncated with ellipsis when they overflow (max-width 60%).                       |
| UIX-049-E-08  | Upload hint text displays supported file types: `.md, .txt, .json, .yaml, .csv, .zip`.          |
| UIX-049-E-09  | Modal opens with a scale-up animation (0.95 → 1.0) alongside fade-in.                           |
| UIX-049-E-10  | Close button (×) is positioned in the header, styled as a borderless icon button.                |

## Dependencies

| Dependency      | Description                                                                         |
|-----------------|-------------------------------------------------------------------------------------|
| FEATURE-049-A   | KB File/Folder CRUD — provides `POST /api/kb/folders` and `svc.create_file()` APIs  |
| FEATURE-049-B   | KB Sidebar Tree — provides `GET /api/kb/tree` for folder listing                    |
| Bootstrap Icons | Uses `bi-cloud-upload` icon in the drop zone                                        |
| CSS Variables    | Relies on X-IPE theme CSS custom properties (`--bg-primary`, etc.)                  |

## Business Rules

| ID            | Rule                                                                                         |
|---------------|----------------------------------------------------------------------------------------------|
| BR-049-E-01   | Maximum file size is 10 MB per individual file.                                              |
| BR-049-E-02   | Archives (.zip, .7z) are extracted, not stored as archive files.                             |
| BR-049-E-03   | Nested archives within an extracted archive are stored as-is (no recursive extraction).      |
| BR-049-E-04   | Empty folder names (whitespace-only) are silently rejected — no API call is made.            |
| BR-049-E-05   | File type validation is performed server-side; the frontend defers to backend error messages. |

## Edge Cases & Constraints

| ID            | Scenario                                                                                      |
|---------------|-----------------------------------------------------------------------------------------------|
| EC-049-E-01   | User drops zero files (empty drag) — no upload triggered.                                     |
| EC-049-E-02   | Upload with no files selected via file picker — no API call made.                             |
| EC-049-E-03   | All files exceed 10 MB — no server request sent; all marked as "Too large".                  |
| EC-049-E-04   | Mixed valid + oversized files — only valid files sent to server.                              |
| EC-049-E-05   | Server returns errors for some files — per-file error messages displayed.                    |
| EC-049-E-06   | Network failure during upload — all files marked "Upload failed".                            |
| EC-049-E-07   | `GET /api/kb/tree` fails — folder dropdown defaults to root only (graceful degradation).     |
| EC-049-E-08   | File name contains HTML/script tags — escaped before rendering.                              |
| EC-049-E-09   | Folder creation API fails — error logged to console; dropdown unchanged.                     |
| EC-049-E-10   | User clicks close during upload — modal closes; in-flight request completes silently.        |

## Out of Scope

- **Sidebar drag-drop to folders** — Specified in requirements but not implemented in FEATURE-049-E. This is a FEATURE-049-B sidebar enhancement (files dragged onto sidebar folder nodes).
- **Breadcrumb-style folder path selector** — The original requirement specified breadcrumb navigation; the implementation uses a dropdown `<select>` instead, which proved simpler and equally effective.
- **Upload zone dynamic destination path hint** — The drop zone does not dynamically display the selected destination path as hint text. The folder dropdown serves this purpose.
- **Individual file progress bars** — Upload progress is shown per-file as status text, not as a percentage progress bar. The single POST approach makes per-file progress tracking impractical.
- **Resume/retry for failed uploads** — Failed uploads must be re-initiated manually.
- **AI Librarian integration** — Covered by FEATURE-049-F.

## Technical Considerations

- Archive extraction depends on Python `zipfile` (stdlib) for `.zip` and `py7zr` library for `.7z` formats.
- The upload uses a single `POST /api/kb/upload` request for all files (batched `FormData`), rather than per-file requests.
- The component integrates with the KB interface via the `kb:changed` custom event pattern — the same event bus used by file CRUD and sidebar operations.
- Folder tree data is fetched once on modal open; new folder creation triggers a re-fetch to keep the dropdown current.
- The `KBFileUpload` class is instantiated per-use (not a singleton) — each `open()` creates a fresh modal DOM tree.

## Open Questions

_No open questions at this time._
