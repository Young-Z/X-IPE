# Feature Specification: KB Landing Zone

> Feature ID: FEATURE-025-B  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-11-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 02-11-2026 | Initial specification | - |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| kb-landing-view | HTML | [mockups/knowledge-base-v1.html](mockups/knowledge-base-v1.html) | Landing view showing file grid, upload zone, action toolbar, and preview panel | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".  
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

**What:** FEATURE-025-B adds file upload, drag-and-drop support, a landing view file grid, and landing actions (delete, move to topic) to the Knowledge Base. This transforms the KB from a read-only indexed view into an interactive workspace where users can ingest new knowledge items.

**Why:** Without upload and landing actions, users must manually copy files into the `x-ipe-docs/knowledge-base/landing/` directory. This feature provides a GUI-based workflow for adding, selecting, and managing files before they are processed by the KB Manager Skill (FEATURE-025-C).

**Who:**
- End users who want to add documents, code snippets, and research materials to their knowledge base
- AI agents that trigger file processing after upload
- Developers building downstream features (025-C KB Manager Skill, 025-D Topics & Summaries)

## User Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-1 | As a **user**, I want to **upload files to the Knowledge Base via a button**, so that **I can add knowledge without touching the file system** | Must |
| US-2 | As a **user**, I want to **drag and drop files onto the KB view**, so that **I can quickly add content** | Must |
| US-3 | As a **user**, I want to **see uploaded files as cards in a grid**, so that **I can visually browse my landing items** | Must |
| US-4 | As a **user**, I want to **select multiple files via checkboxes**, so that **I can perform batch actions** | Must |
| US-5 | As a **user**, I want to **delete selected files from landing**, so that **I can remove unwanted items** | Must |
| US-6 | As a **user**, I want to **see an empty state with drag-drop zone** when the landing folder is empty, so that **I know how to get started** | Must |
| US-7 | As a **user**, I want to **toggle between grid and list view**, so that **I can choose my preferred layout** | Should |

## Acceptance Criteria

### 1. File Upload

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-1.1 | "Upload" button MUST appear in the KB top bar when KB view is active | Navigate to KB view → "Upload" button visible with `bi-cloud-upload` icon |
| AC-1.2 | Clicking Upload MUST open a file picker dialog | Click Upload → native file picker dialog opens |
| AC-1.3 | Upload MUST support file types: PDF, MD, TXT, DOCX, XLSX, code files (.py, .js, .ts, .java, .go, .rs, .c, .cpp, .h, .html, .css, .json, .yaml), images (.png, .jpg, .jpeg, .gif, .svg, .webp) | Select each file type → upload succeeds |
| AC-1.4 | Maximum file size MUST be 50MB per file | Upload 51MB file → error message displayed, file not saved |
| AC-1.5 | Uploaded files MUST be saved to `x-ipe-docs/knowledge-base/landing/` | Upload file → file appears at `landing/{filename}` on disk |
| AC-1.6 | Upload MUST support multiple file selection in a single dialog | Select 3 files → all 3 uploaded |
| AC-1.7 | Folder upload MUST be supported (preserves folder structure under landing) | Upload folder → subfolder appears in `landing/{folder-name}/` |
| AC-1.8 | Upload progress indicator MUST display during upload | Upload large file → progress bar or spinner visible |
| AC-1.9 | After upload, the file index MUST be refreshed automatically | Upload file → file appears in sidebar tree and file grid without manual refresh |
| AC-1.10 | Duplicate file detection MUST warn user and skip by default (not overwrite) | Upload file with same name → warning toast shown, original preserved |

### 2. Drag-and-Drop

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-2.1 | Dragging files over KB content area MUST show visual drop zone overlay | Drag file over content area → overlay with dashed border and "Drop files here" message |
| AC-2.2 | Dropping files MUST upload them to landing folder | Drop file → saved to `landing/` and appears in file grid |
| AC-2.3 | Drop zone MUST accept the same file types as the Upload button | Drop .pdf file → accepted; drop .exe → rejected with message |
| AC-2.4 | Dragging files away MUST dismiss the drop zone overlay | Drag file out of content area → overlay disappears |

### 3. Landing View — File Grid

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-3.1 | Landing view MUST show file cards in a responsive grid layout | Navigate to KB → files displayed as cards in grid with `auto-fill, minmax(180px, 1fr)` |
| AC-3.2 | Each file card MUST display: type icon, filename, size, and relative date | Inspect card → icon, name, "2.4 MB", "Today" visible |
| AC-3.3 | File cards MUST show checkbox on hover | Hover over card → checkbox appears at top-left corner |
| AC-3.4 | Clicking a file card checkbox MUST toggle selection (visual highlight + checkbox check) | Click checkbox → card gets `selected` class, checkbox shows check icon |
| AC-3.5 | Selected cards MUST have distinct visual style (border highlight, background change) | Select card → border color and background change to accent color |
| AC-3.6 | UI layout MUST match the approved mockup (knowledge-base-v1.html) for file grid | Compare rendered grid vs mockup → card layout, spacing, sizing consistent |
| AC-3.7 | Visual styling (colors, spacing, typography) MUST be consistent with mockup (knowledge-base-v1.html) | Compare colors and fonts → match warm dark theme |
| AC-3.8 | Interactive elements shown in mockup (knowledge-base-v1.html) MUST be present and functional | Verify all interactive elements from mockup exist and work |

### 4. Action Toolbar

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-4.1 | "Select All" button MUST select all file cards | Click Select All → all cards have `selected` class |
| AC-4.2 | "Clear" button MUST deselect all file cards | Click Clear → no cards have `selected` class |
| AC-4.3 | "Delete" action MUST appear when items are selected | Select 2 items → Delete button visible/enabled |
| AC-4.4 | View mode toggle (grid/list) MUST switch between grid and list layouts | Click list icon → files displayed in rows; click grid icon → cards return |
| AC-4.5 | Sort options MUST include: name, date, size, type | Click Sort → dropdown with 4 options; selecting each reorders files |

### 5. Delete Action

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-5.1 | Clicking Delete with selected items MUST show confirmation dialog | Click Delete → "Are you sure?" dialog appears with file count |
| AC-5.2 | Confirming delete MUST remove files from disk and refresh index | Confirm → files removed from `landing/`, index updated, grid re-rendered |
| AC-5.3 | Cancelling delete MUST preserve all files | Cancel → files still on disk, grid unchanged |
| AC-5.4 | Delete MUST support batch operations (multiple selected files) | Select 5 files → Delete → all 5 removed |

### 6. Empty State

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-6.1 | When landing folder is empty, MUST show centered empty state with upload zone | Delete all files → empty state with dashed border drop zone visible |
| AC-6.2 | Empty state MUST display upload icon, title "Your Knowledge Base is empty", and subtitle "Drag & drop files or click Upload" | Inspect empty state → icon, title, subtitle present |
| AC-6.3 | Empty state drop zone MUST accept drag-and-drop (same behavior as AC-2.1 through AC-2.4) | Drop file on empty state → file uploaded to landing |
| AC-6.4 | After uploading to empty state, MUST transition to file grid view | Drop file → empty state replaced by file grid showing new file |

### 7. Processing Indicator

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-7.1 | Processing indicator bar MUST appear when KB Manager Skill is running | Trigger processing → indicator bar shows spinner, text, and cancel button |
| AC-7.2 | Processing indicator MUST show descriptive text ("Processing N files...") | During processing → text reads "Processing 3 files..." |
| AC-7.3 | Cancel button MUST stop the processing operation | Click Cancel → processing stops, remaining files stay in landing |

## Functional Requirements

### FR-1: File Upload API

**Description:** Backend endpoint to receive uploaded files and store them in the landing folder.

**Details:**
- Input: Multipart form data with one or more files, optional `subfolder` parameter for folder uploads
- Process:
  1. Validate each file: check size ≤ 50MB, validate extension against allowed list
  2. Check for duplicate filename in landing folder
  3. If duplicate detected, return warning (do not overwrite)
  4. Save file(s) to `x-ipe-docs/knowledge-base/landing/` (or `landing/{subfolder}/` for folder uploads)
  5. Trigger index refresh
- Output: JSON response with list of uploaded file paths, warnings for duplicates, errors for rejections

### FR-2: File Delete API

**Description:** Backend endpoint to delete files from the landing folder.

**Details:**
- Input: JSON body with list of file paths (relative to KB root)
- Process:
  1. Validate each path starts with `landing/` (prevent deletion outside landing)
  2. Delete files from disk
  3. Trigger index refresh
- Output: JSON response with list of deleted files and any errors

### FR-3: Landing File Grid Rendering

**Description:** Frontend renders landing files as interactive card grid.

**Details:**
- Input: File index data from `/api/kb/index`
- Process:
  1. Filter files with paths starting with `landing/`
  2. Render each file as a card with icon, name, size, date
  3. Attach selection event handlers to checkboxes
  4. Maintain selection state in memory
- Output: Interactive file grid with selection support

### FR-4: Drag-and-Drop Upload

**Description:** Frontend handles file drop events on the KB content area.

**Details:**
- Input: DragEvent with file(s) from OS
- Process:
  1. Show drop zone overlay on `dragenter`/`dragover`
  2. Hide overlay on `dragleave`
  3. On `drop`, extract files from event
  4. Validate file types and sizes
  5. Send to upload API
  6. Refresh grid on success
- Output: Files saved to landing, grid updated

### FR-5: Batch Actions (Select All, Clear, Delete)

**Description:** Action toolbar provides batch operations on selected files.

**Details:**
- Input: User clicks on toolbar buttons
- Process:
  1. Select All: set all cards to selected state
  2. Clear: remove selected state from all cards
  3. Delete: collect selected file paths, send to delete API, show confirmation first
- Output: Grid state updated, files deleted if confirmed

## Non-Functional Requirements

| # | Requirement | Metric | Priority |
|---|-------------|--------|----------|
| NFR-1 | File upload MUST complete within 5 seconds for files < 10MB | < 5000ms for 10MB file | Should |
| NFR-2 | File grid MUST render within 300ms for up to 100 files | < 300ms render time | Should |
| NFR-3 | Drag-and-drop overlay MUST appear within 100ms of dragenter | < 100ms overlay display | Must |
| NFR-4 | Delete operation MUST complete within 2 seconds for up to 50 files | < 2000ms for 50 files | Should |
| NFR-5 | Upload MUST show progress for files > 1MB | Progress visible for large files | Should |

## UI/UX Requirements

### UI-1: Upload Button (Top Bar)

**Based on mockup:** [knowledge-base-v1.html](mockups/knowledge-base-v1.html)

| Element | Specification |
|---------|--------------|
| Position | Top bar, right side, primary styled button |
| Icon | `bi-cloud-upload` |
| Label | "Upload" |
| Style | Primary button (accent color fill) |
| Behavior | Opens native file picker on click |

### UI-2: File Grid Cards

**Based on mockup:** [knowledge-base-v1.html](mockups/knowledge-base-v1.html)

| Element | Specification |
|---------|--------------|
| Layout | CSS Grid: `grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))` |
| Card Background | Elevated background (`--bg-elevated` / `#323338`) |
| Card Border | Subtle border, rounded corners |
| Hover Effect | Scale up slightly, border glow, cursor pointer |
| Selected State | Accent border, accent background tint, visible checkbox with check icon |
| Checkbox | Top-left corner, hidden by default, shown on hover and when selected |

### UI-3: Action Toolbar

**Based on mockup:** [knowledge-base-v1.html](mockups/knowledge-base-v1.html)

| Element | Specification |
|---------|--------------|
| Position | Between content header and file grid |
| Left Group | "Select All" button, "Clear" button |
| Center Group | Grid/List view toggle icons |
| Right Group | "Sort" dropdown, "Filter" button |
| Dividers | Vertical dividers between groups |

### UI-4: Empty State / Drop Zone

| Element | Specification |
|---------|--------------|
| Layout | Centered vertically and horizontally in content area |
| Border | Dashed border (`2px dashed`) with subtle color |
| Drag-Over | Border color changes to accent, background tint |
| Icon | Large upload icon (`bi-cloud-upload`, ~48px) |
| Title | "Your Knowledge Base is empty" |
| Subtitle | "Drag & drop files or click Upload to get started" |

### UI-5: Content Header

**Based on mockup:** [knowledge-base-v1.html](mockups/knowledge-base-v1.html)

| Element | Specification |
|---------|--------------|
| Title | "Landing Folder" with `bi-inbox-fill` icon (warm accent color) |
| Status Badge | "{N} items awaiting processing" badge |
| Actions | "Process Selected" button (primary), "Move to Topic" button (ghost) |

### UI-6: Processing Indicator

**Based on mockup:** [knowledge-base-v1.html](mockups/knowledge-base-v1.html)

| Element | Specification |
|---------|--------------|
| Position | Between action toolbar and file grid |
| Layout | Horizontal bar: spinner + text + cancel link |
| Background | Accent-tinted translucent bar |
| Spinner | CSS animation spinner |
| Text | "Processing N files... Analyzing content and generating summaries" |
| Cancel | Text link "Cancel" on right side |

### User Flow: Upload Files

1. User navigates to Knowledge Base view
2. User clicks "Upload" in top bar (or drags files to content area)
3. File picker dialog opens (or drop zone overlay appears)
4. User selects files
5. Upload progress indicator shows
6. Files saved to `landing/`
7. Index auto-refreshes
8. File grid updates to show new files
9. Sidebar tree updates to show new files under landing

### User Flow: Delete Files

1. User selects files by clicking checkboxes on cards
2. User clicks "Delete" in content header or action toolbar
3. Confirmation dialog appears: "Delete N selected files?"
4. User confirms
5. Files removed from disk
6. Index refreshes
7. Grid and sidebar tree update

## Dependencies

### Internal Dependencies

| Dependency | Type | Description | Status |
|------------|------|-------------|--------|
| FEATURE-025-A | Feature | KB Core Infrastructure — provides folder structure, index management, sidebar integration, KBService, and kb_routes | Completed |
| FEATURE-008 | Feature | Workplace framework — provides sidebar and content area infrastructure | Implemented |

### External Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| File System | System | Read/write access to `x-ipe-docs/knowledge-base/landing/` |
| Flask Backend | System | Existing Flask app for new API endpoints |
| Bootstrap Icons | Library | Icons for file types, buttons, UI elements |

## Business Rules

| # | Rule | Rationale |
|---|------|-----------|
| BR-1 | Uploaded files MUST go to `landing/` by default | Separates unprocessed from organized knowledge |
| BR-2 | Maximum file size is 50MB per file | Prevents excessive storage consumption |
| BR-3 | Duplicate filenames MUST NOT overwrite existing files | Prevents accidental data loss |
| BR-4 | Delete MUST require confirmation | Prevents accidental deletion |
| BR-5 | Only files in `landing/` can be deleted via this feature | Prevents deletion of organized knowledge (topics) |
| BR-6 | File type validation uses allowlist (not blocklist) | Security: only accept known safe types |
| BR-7 | Index MUST auto-refresh after upload and delete | Ensures UI always reflects current state |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Upload file exceeding 50MB | Show error toast: "File too large (max 50MB)", skip file, continue others |
| Upload file with unsupported extension | Show error toast: "Unsupported file type: .exe", skip file, continue others |
| Upload file with duplicate name | Show warning toast: "{filename} already exists", skip file (do not overwrite) |
| Upload with no files selected | Do nothing (dialog closes without action) |
| Drag non-file items (text, URLs) | Ignore drop, no error |
| Upload to full disk | Show error toast: "Upload failed: disk full", preserve existing files |
| Delete with no items selected | Delete button disabled/hidden |
| Delete files that were already removed from disk | Silently skip missing files, refresh index |
| Network error during upload | Show error toast: "Upload failed: network error", file not saved |
| Very long filename (>255 chars) | Truncate display name in card, preserve full name in tooltip and on disk |
| Concurrent uploads | Queue uploads, process sequentially to avoid index conflicts |
| Upload during processing | Allow upload (landing is independent of processing) |
| Empty folder uploaded | Create empty subfolder in landing (valid operation) |
| Upload 100+ files at once | Show progress with file count, upload sequentially or in small batches |
| Special characters in filename | Preserve original filename, URL-encode for API calls |

## Out of Scope

- "Move to Topic" functionality (FEATURE-025-C / FEATURE-025-D handles topic assignment)
- "Process Selected" AI processing logic (FEATURE-025-C KB Manager Skill)
- Preview panel for selected files (FEATURE-025-E KB Search & Preview)
- Section tabs (Landing/Topics) in sidebar (FEATURE-025-F)
- File content preview/rendering
- File editing or in-place modification
- Automatic file type conversion
- Cloud storage integration
- Version control for uploaded files

## Technical Considerations

### New API Endpoints

```
POST /api/kb/upload          - Upload file(s) to landing folder
POST /api/kb/landing/delete  - Delete file(s) from landing folder
GET  /api/kb/landing         - Get landing folder files only
```

### Allowed File Extensions

```
Documents: .pdf, .md, .markdown, .txt, .docx, .xlsx
Code:      .py, .js, .ts, .java, .go, .rs, .c, .cpp, .h, .html, .css, .json, .yaml, .yml
Images:    .png, .jpg, .jpeg, .gif, .svg, .webp
```

### File Card Data Structure

Each card renders from the existing file index entry:
```json
{
  "path": "landing/document.pdf",
  "name": "document.pdf",
  "type": "pdf",
  "size": 1024567,
  "topic": null,
  "created_date": "2026-02-05T14:30:00Z",
  "keywords": ["document"]
}
```

### Integration with Existing KBService

- `KBService.refresh_index()` — call after upload and delete operations
- `KBService.get_index()` — use to populate file grid
- Extend `kb_routes.py` with new upload and delete endpoints
- Extend `kb-core.js` with file grid, drag-drop, and selection logic

### Frontend Module

New functionality adds to existing `kb-core.js` or creates companion `kb-landing.js` (if >800 lines combined, split per project rule).

## Open Questions

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| OQ-1 | Should "Process Selected" button be present but disabled (wired in 025-C), or omitted entirely? | Resolved | Present but disabled with tooltip "Coming in a future update" — provides UI consistency with mockup |
| OQ-2 | Should "Move to Topic" button be present but disabled, or omitted? | Resolved | Present but disabled — same rationale as OQ-1 |
| OQ-3 | Should folder upload preserve subfolder names or flatten? | Resolved | Preserve subfolder structure under `landing/` |
