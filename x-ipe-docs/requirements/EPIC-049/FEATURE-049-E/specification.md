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

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-E-01a | Modal overlay appears with fade-in animation (`active` class), body scroll is locked, and modal contains header ("📤 Upload Files"), folder selector, drop zone, and close button when `open()` is called | UI |
| AC-049-E-01b | Modal fades out, is removed from DOM, and body scroll is restored when user clicks close button or overlay background | UI |
| AC-049-E-02a | Drop zone highlights with blue border and background tint (`dragover` class) when files are dragged over it | UI |
| AC-049-E-02b | `dragover` visual state is removed and upload flow begins for all dropped files on drop | UI |
| AC-049-E-02c | `dragover` visual state is removed when drag leaves the drop zone without a drop | UI |
| AC-049-E-03a | System file picker opens with `multiple` selection enabled when user clicks drop zone or "browse" link | UI |
| AC-049-E-03b | Upload flow begins for all files selected via the file picker | UI |
| AC-049-E-04a | `<select>` dropdown displays all KB folders in hierarchical indented list with `/ (root)` as first option, populated from `GET /api/kb/tree` | Integration |
| AC-049-E-04b | `folder` property updates to selected path and subsequent uploads target that folder when user selects a folder | UI |
| AC-049-E-04c | Dropdown pre-selects matching folder when `folder` option is passed to constructor | Unit |
| AC-049-E-05a | Inline input row with text field, "Create" button, and "Cancel" button appears when user clicks "+ Folder" button | UI |
| AC-049-E-05b | `POST /api/kb/folders` request sent with path, dropdown refreshes with new folder selected, and `kb:changed` event dispatched when user creates a folder with valid name | Integration |
| AC-049-E-05c | No API call made and no folder created when user clicks "Create" with empty or whitespace-only name | Unit |
| AC-049-E-05d | New-folder input row is hidden when user clicks "Cancel" | UI |
| AC-049-E-06a | Progress area shows each file name with "⏳ Uploading..." status indicator when upload begins | UI |
| AC-049-E-06b | Each successfully uploaded file shows "✅ Uploaded" and each server-rejected file shows "❌ {error message}" when API responds | Integration |
| AC-049-E-06c | `kb:changed` event dispatched and `onComplete` callback invoked when all uploads complete with at least one success | Integration |
| AC-049-E-07a | `.zip` archive extracted preserving internal folder structure within destination folder; all extracted files appear in response `uploaded` array | API |
| AC-049-E-08a | `.7z` archive extracted preserving internal folder structure within destination folder; all extracted files appear in response `uploaded` array | API |
| AC-049-E-09a | Nested archives within extracted content are stored as-is without recursive extraction | API |
| AC-049-E-10a | Oversized file (>10 MB) immediately rejected client-side with "❌ Too large (>10MB)" status and excluded from FormData | Unit |
| AC-049-E-10b | Only valid files sent to server when mixed with oversized files; oversized files show rejection status alongside upload results | Unit |
| AC-049-E-11a | Backend returns error entry with file name and descriptive message for unsupported file types, displayed in upload progress list | API |
| AC-049-E-12a | File names containing HTML/script characters (e.g., `<script>alert(1)</script>.md`) are escaped and rendered as plain text, preventing XSS | Unit |
| AC-049-E-13a | All in-progress files marked "❌ Upload failed" and no `kb:changed` event dispatched on network request failure | Integration |

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
