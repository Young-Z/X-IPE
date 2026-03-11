# Feature Specification: KB File Upload

> Feature ID: FEATURE-049-E  
> Version: v1.0  
> Status: Refined  
> Last Updated: 07-13-2025

## Version History

| Version | Date       | Description                                              |
|---------|------------|----------------------------------------------------------|
| v1.0    | 07-13-2025 | Retroactive specification from implemented code & tests  |

## Linked Mockups

- **KB Interface Mockup (Scene 4 — Upload View):** `x-ipe-docs/ideas/wf-007-knowledge-base-implementation/mockups/kb-interface-v1.html`  
  ⚠️ *Outdated — directional reference only.* The implementation evolved beyond the original mockup (e.g., folder dropdown replaced breadcrumb picker, inline new-folder creation added). Use as visual context, not as source of truth.

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

### AC-049-E-01: Upload Modal Lifecycle

**Given** the user triggers the upload action  
**When** the `KBFileUpload.open()` method is called  
**Then** a modal overlay appears with a fade-in animation (`active` class), body scroll is locked, and the modal contains a header ("📤 Upload Files"), folder selector, drop zone, and close button.

**Given** the upload modal is open  
**When** the user clicks the close button or the overlay background  
**Then** the modal fades out and is removed from the DOM, and body scroll is restored.

### AC-049-E-02: Drag-and-Drop Upload Zone

**Given** the upload modal is open  
**When** the user drags files over the drop zone  
**Then** the drop zone visually highlights with a blue border and subtle background tint (`dragover` class).

**Given** files are dragged over the drop zone  
**When** the user drops the files  
**Then** the `dragover` visual state is removed and the upload flow begins for all dropped files.

**Given** files are dragged over the drop zone  
**When** the drag leaves the drop zone without a drop  
**Then** the `dragover` visual state is removed.

### AC-049-E-03: Click-to-Browse File Picker

**Given** the upload modal is open  
**When** the user clicks the drop zone area or the "browse" link  
**Then** the system file picker opens with `multiple` selection enabled.

**Given** the user selects files via the file picker  
**When** the file picker closes  
**Then** the upload flow begins for all selected files.

### AC-049-E-04: Folder Destination Selector

**Given** the upload modal opens  
**When** the folder tree is loaded from `GET /api/kb/tree`  
**Then** a `<select>` dropdown displays all KB folders in a hierarchical indented list, with `/ (root)` as the first option.

**Given** the folder dropdown is rendered  
**When** the user selects a folder  
**Then** the `folder` property is updated to the selected path, and subsequent uploads target that folder.

**Given** a `folder` option was passed to the constructor  
**When** the modal opens  
**Then** the dropdown pre-selects the matching folder.

### AC-049-E-05: Inline New Folder Creation

**Given** the upload modal is open  
**When** the user clicks the "+ Folder" button  
**Then** an inline input row appears with a text field, "Create" button, and "Cancel" button.

**Given** the new-folder input is visible and the user has typed a folder name  
**When** the user clicks "Create"  
**Then** a `POST /api/kb/folders` request is sent with the path (relative to current folder), the dropdown refreshes with the new folder, the new folder becomes the selected destination, and a `kb:changed` event is dispatched.

**Given** the new-folder input is visible  
**When** the user clicks "Create" with an empty or whitespace-only name  
**Then** the API call is not made and no folder is created.

**Given** the new-folder input is visible  
**When** the user clicks "Cancel"  
**Then** the input row is hidden.

### AC-049-E-06: Multi-File Upload with Progress

**Given** one or more valid files are submitted for upload  
**When** the upload begins  
**Then** a progress area appears showing each file name with an "⏳ Uploading..." status indicator.

**Given** the upload API responds successfully  
**When** individual file results are returned  
**Then** each successfully uploaded file shows "✅ Uploaded" and each server-rejected file shows "❌ {error message}".

**Given** one or more valid files are submitted  
**When** all uploads complete with at least one success  
**Then** a `kb:changed` event is dispatched and the `onComplete` callback is invoked (if provided).

### AC-049-E-07: Archive Auto-Extraction (.zip)

**Given** the user uploads a `.zip` file  
**When** the backend receives the file via `POST /api/kb/upload`  
**Then** the archive is extracted preserving its internal folder structure within the selected destination folder, and all extracted files appear in the response's `uploaded` array.

### AC-049-E-08: Archive Auto-Extraction (.7z)

**Given** the user uploads a `.7z` file  
**When** the backend receives the file via `POST /api/kb/upload`  
**Then** the archive is extracted preserving its internal folder structure within the selected destination folder, and all extracted files appear in the response's `uploaded` array.

### AC-049-E-09: Nested Archive Handling

**Given** an uploaded archive contains nested archives (e.g., a `.zip` inside a `.zip`)  
**When** the outer archive is extracted  
**Then** the nested archive files are stored as-is and are not recursively extracted.

### AC-049-E-10: File Size Validation

**Given** the user selects or drops files for upload  
**When** any file exceeds 10 MB  
**Then** the oversized file is immediately rejected client-side with "❌ Too large (>10MB)" status, and the file is excluded from the `FormData` sent to the server.

**Given** a mix of valid and oversized files are submitted  
**When** the upload is processed  
**Then** only valid files are sent to the server; oversized files show the rejection status alongside the upload results for valid files.

### AC-049-E-11: File Type Validation (Backend)

**Given** the user uploads a file with an unsupported type  
**When** the backend processes the file  
**Then** the response includes an error entry with the file name and a descriptive error message, which is displayed in the upload progress list.

### AC-049-E-12: Security — HTML Escaping

**Given** a file has a name containing HTML/script characters (e.g., `<script>alert(1)</script>.md`)  
**When** the file name is rendered in the upload progress list  
**Then** the HTML is escaped and rendered as plain text, preventing XSS.

### AC-049-E-13: Network Error Handling

**Given** files are being uploaded  
**When** the network request fails (connection error, timeout, etc.)  
**Then** all in-progress files are marked with "❌ Upload failed" status, and no `kb:changed` event is dispatched.

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
