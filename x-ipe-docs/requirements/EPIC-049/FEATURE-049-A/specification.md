# Feature Specification: KB Backend & Storage Foundation

> Feature ID: FEATURE-049-A
> Epic ID: EPIC-049
> Version: v2.0
> Status: Refined
> Last Updated: 03-11-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-11-2026 | Initial specification |
| v2.0 | 03-11-2026 | Template conformance: GWT acceptance criteria, test type legend, linked mockup dates |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| KB Browse Articles | HTML | [x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html](x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html) | Scene 1 — grid/list browse with tags, search, sort | current | 03-11-2026 |
| KB Article Detail | HTML | [x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html](x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html) | Scene 2 — article detail with frontmatter display | current | 03-11-2026 |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

FEATURE-049-A provides the backend foundation for the Knowledge Base — the file service layer, REST API endpoints, configuration management, and data models that all other KB features depend on. It handles file/folder CRUD operations, YAML frontmatter parsing, 2D tag taxonomy management, and URL bookmark format support.

This is the MVP foundation: no UI components are included (those are in FEATURE-049-B through G). The feature delivers a complete, testable API layer that downstream features consume.

**Target users:** AI Agents (via API), Frontend JS (via REST endpoints), other KB features (via service layer).

## User Stories

1. **US-049-A-1:** As a frontend component, I want to list all folders and files in the KB with their metadata, so that I can render the sidebar tree and browse views.
2. **US-049-A-2:** As a frontend component, I want to create, rename, move, and delete folders, so that users can organize their knowledge base freely.
3. **US-049-A-3:** As a frontend component, I want to create and update markdown files with YAML frontmatter, so that articles are stored with proper metadata.
4. **US-049-A-4:** As a frontend component, I want to read kb-config.json for tag definitions, so that I can render tag filter chips and tag selection dropdowns.
5. **US-049-A-5:** As a system, I want kb-config.json to be auto-created with default tags on first KB access, so that setup is frictionless.
6. **US-049-A-6:** As a frontend component, I want to search files by filename and frontmatter fields, so that users can find articles quickly.
7. **US-049-A-7:** As a frontend component, I want to read and create URL bookmark files (.url.md), so that users can save external references.

## Acceptance Criteria

### AC-049-A-01: KB Root Initialization

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-01a | GIVEN KB root directory does not exist WHEN any KB API endpoint is called THEN KB root is auto-created at `x-ipe-docs/knowledge-base/` | API |
| AC-049-A-01b | GIVEN KB root is initialized for the first time WHEN `kb-config.json` is auto-generated THEN it contains default lifecycle tags: Ideation, Requirement, Design, Implementation, Testing, Deployment, Maintenance | Unit |
| AC-049-A-01c | GIVEN KB root is initialized for the first time WHEN `kb-config.json` is auto-generated THEN it contains default domain tags: API, Authentication, UI-UX, Database, Infrastructure, Security, Performance, Integration, Documentation, Analytics | Unit |
| AC-049-A-01d | GIVEN KB root is initialized for the first time WHEN `kb-config.json` is auto-generated THEN it includes empty `agent_write_allowlist` array AND `ai_librarian` settings object | Unit |

### AC-049-A-02: Folder Listing API

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-02a | GIVEN KB root exists with folders and files WHEN GET /api/kb/tree is called THEN response contains full folder/file tree as nested JSON | API |
| AC-049-A-02b | GIVEN GET /api/kb/tree returns results WHEN a tree node is inspected THEN it includes name, path (relative to KB root), type (`folder` or `file`), AND children array (for folders) | API |
| AC-049-A-02c | GIVEN GET /api/kb/tree returns file nodes WHEN a file node is inspected THEN it includes size_bytes, modified_date, AND file_type extension | API |
| AC-049-A-02d | GIVEN `.intake/` folder exists in KB root WHEN GET /api/kb/tree is called THEN `.intake/` folder is excluded from the response | API |
| AC-049-A-02e | GIVEN KB contains up to 500 files WHEN GET /api/kb/tree is called THEN response returns within 500ms | API |

### AC-049-A-03: Folder CRUD Operations

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-03a | GIVEN a valid folder path is provided WHEN POST /api/kb/folders is called THEN folder is created AND response returns 201 with folder info | API |
| AC-049-A-03b | GIVEN an existing folder path is provided WHEN PATCH /api/kb/folders is called with new name THEN folder is renamed AND response returns 200 with updated info | API |
| AC-049-A-03c | GIVEN an existing folder and valid destination WHEN PUT /api/kb/folders/move is called THEN folder is moved to new parent AND response returns 200 | API |
| AC-049-A-03d | GIVEN an existing folder path is provided WHEN DELETE /api/kb/folders is called THEN folder and all contents are deleted AND response returns 200 with deleted count | API |
| AC-049-A-03e | GIVEN a folder with the same name exists at the target level WHEN POST /api/kb/folders is called THEN response returns 409 Conflict | API |
| AC-049-A-03f | GIVEN a folder is selected for move WHEN destination is the folder itself or a descendant THEN response returns 400 Bad Request | API |

### AC-049-A-04: File Listing with Metadata

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-04a | GIVEN a folder exists with files WHEN GET /api/kb/files?folder={path} is called THEN response contains files in that folder with frontmatter metadata | API |
| AC-049-A-04b | GIVEN GET /api/kb/files returns results WHEN a file entry is inspected THEN it includes name, path, size_bytes, modified_date, AND frontmatter (title, tags, author, created, auto_generated) | API |
| AC-049-A-04c | GIVEN a markdown file has no YAML frontmatter block WHEN GET /api/kb/files returns the file THEN frontmatter fields are null AND no error is returned | API |
| AC-049-A-04d | GIVEN a non-markdown file (PDF, image) exists in KB WHEN GET /api/kb/files returns the file THEN file metadata is included AND frontmatter parsing is skipped | API |
| AC-049-A-04e | GIVEN files exist in a folder WHEN GET /api/kb/files is called with `sort` query param THEN results are sorted by the specified field (`modified` default, `name`, `created`, or `untagged`) | API |

### AC-049-A-05: File CRUD Operations

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-05a | GIVEN a file exists at the specified path WHEN GET /api/kb/files/{path} is called THEN response contains file content (markdown body) AND parsed frontmatter | API |
| AC-049-A-05b | GIVEN valid file content is provided WHEN POST /api/kb/files is called THEN file is created with content and optional frontmatter AND response returns 201 | API |
| AC-049-A-05c | GIVEN a file exists at the specified path WHEN PUT /api/kb/files/{path} is called with updated content THEN file content and/or frontmatter is updated AND response returns 200 | API |
| AC-049-A-05d | GIVEN a file exists at the specified path WHEN DELETE /api/kb/files/{path} is called THEN file is deleted AND response returns 200 | API |
| AC-049-A-05e | GIVEN a new file is created without frontmatter WHEN the file is saved THEN frontmatter auto-populates with title (from filename), tags (empty), author ("unknown"), created (current date), AND auto_generated (false) | Unit |
| AC-049-A-05f | GIVEN a file upload exceeds 10MB WHEN the upload request is made THEN response returns 413 Payload Too Large | API |

### AC-049-A-06: File Move Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-06a | GIVEN a file exists and a valid destination folder is specified WHEN PUT /api/kb/files/move is called THEN file is moved to new folder AND response returns 200 with new path | API |
| AC-049-A-06b | GIVEN a destination folder does not exist WHEN PUT /api/kb/files/move is called THEN response returns 404 Not Found | API |
| AC-049-A-06c | GIVEN a file move operation is initiated WHEN the move is executed THEN destination file is created AND source file is removed atomically | Integration |

### AC-049-A-07: YAML Frontmatter Parsing

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-07a | GIVEN a .md file has a YAML block delimited by `---` at the top WHEN the file is parsed THEN frontmatter is extracted from the YAML block | Unit |
| AC-049-A-07b | GIVEN frontmatter is parsed from a .md file WHEN fields are extracted THEN supported fields include title (string), tags (object with lifecycle[] and domain[]), author (string), created (date string), AND auto_generated (boolean) | Unit |
| AC-049-A-07c | GIVEN a .md file contains invalid YAML in the frontmatter block WHEN the file is parsed THEN frontmatter is returned as null (graceful degradation) | Unit |
| AC-049-A-07d | GIVEN a file's frontmatter is being updated WHEN the update is saved THEN markdown body content below the `---` block is preserved | Unit |

### AC-049-A-08: Tag Taxonomy API

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-08a | GIVEN kb-config.json exists with tag definitions WHEN GET /api/kb/config is called THEN response contains parsed config including tags.lifecycle and tags.domain arrays | API |
| AC-049-A-08b | GIVEN GET /api/kb/config returns tag arrays WHEN tag values are inspected THEN they contain string values matching the predefined taxonomy | Unit |
| AC-049-A-08c | GIVEN kb-config.json includes agent and AI sections WHEN GET /api/kb/config is called THEN response includes agent_write_allowlist AND ai_librarian configuration sections | API |

### AC-049-A-09: Search API

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-09a | GIVEN files exist in KB WHEN GET /api/kb/search?q={query} is called THEN response contains files matching query against filename and frontmatter fields | API |
| AC-049-A-09b | GIVEN a search query is submitted WHEN matching is performed THEN search matches against filename, frontmatter.title, frontmatter.tags (lifecycle + domain), AND frontmatter.author | Unit |
| AC-049-A-09c | GIVEN a search query with mixed case WHEN search is performed THEN matching is case-insensitive | Unit |
| AC-049-A-09d | GIVEN search returns results WHEN result entries are inspected THEN each includes full file metadata (same as file listing response) | API |
| AC-049-A-09e | GIVEN files are tagged in KB WHEN GET /api/kb/search?tag={tag}&tag_type={lifecycle\|domain} is called THEN results are filtered to files with the specified tag | API |
| AC-049-A-09f | GIVEN files exist in KB WHEN GET /api/kb/search is called with both q={query} AND tag={tag}&tag_type={type} THEN results are filtered by both query match and tag match | API |
| AC-049-A-09g | GIVEN KB contains up to 500 files WHEN search is performed THEN results return within 300ms for filename+frontmatter matching | API |

### AC-049-A-10: URL Bookmark Format

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-10a | GIVEN a `.url.md` file exists WHEN it is parsed THEN frontmatter includes additional field `url` (string, required) | Unit |
| AC-049-A-10b | GIVEN a `.url.md` file exists at the specified path WHEN GET /api/kb/files/{path} is called THEN response includes url field in frontmatter | API |
| AC-049-A-10c | GIVEN a `.url.md` file creation request is made WHEN `url` field is missing from frontmatter THEN response returns 400 Bad Request | API |
| AC-049-A-10d | GIVEN `.url.md` files exist in KB WHEN file listing or search results are returned THEN URL bookmarks include `file_type: "url_bookmark"` indicator | API |

### AC-049-A-11: File Type Validation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------------------------------|-----------|
| AC-049-A-11a | GIVEN a file upload is attempted WHEN file type is `.md`, `.url.md`, `.pdf`, `.png`, `.jpg`, `.jpeg`, or `.svg` THEN the file is accepted | Unit |
| AC-049-A-11b | GIVEN a file upload is attempted WHEN file type is not in the accepted list THEN response returns 415 Unsupported Media Type | API |
| AC-049-A-11c | GIVEN a file is uploaded WHEN file type validation is performed THEN type is determined by file extension, not content sniffing | Unit |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB)

## Functional Requirements

- **FR-049-A-01:** KB service module (`kb_service.py`) handles all file system operations for the knowledge base
- **FR-049-A-02:** KB routes module (`kb_routes.py`) exposes REST API endpoints under `/api/kb/` prefix
- **FR-049-A-03:** All file paths in API responses are relative to KB root (`x-ipe-docs/knowledge-base/`)
- **FR-049-A-04:** kb-config.json schema validated on read; invalid config returns 500 with descriptive error
- **FR-049-A-05:** All write operations (create, update, move, delete) return the affected resource in response body
- **FR-049-A-06:** Frontmatter serialization uses Python `yaml.safe_dump` with `default_flow_style=False`

## Non-Functional Requirements

- **NFR-049-A-01:** Tree listing returns within 500ms for up to 500 files
- **NFR-049-A-02:** Search returns within 300ms for filename+frontmatter matching across 500 files
- **NFR-049-A-03:** No external database dependency — all operations are file-system based
- **NFR-049-A-04:** All API endpoints return standard JSON error responses with `error` and `message` fields
- **NFR-049-A-05:** File operations are atomic where possible (write to temp, then rename)

## UI/UX Requirements

None — this is a backend-only feature. UI is provided by FEATURE-049-B through G.

## Dependencies

### Internal
- None (this is the foundation feature with no dependencies)

### External
- Python `yaml` module (PyYAML — already a project dependency)
- Python `zipfile` module (stdlib — for archive support in FEATURE-049-E, not this feature)
- Flask routing framework (already in project)

## Business Rules

- **BR-049-A-01:** The `.intake/` folder is reserved for AI Librarian staging and MUST be excluded from all browse/search APIs
- **BR-049-A-02:** Files >10MB are rejected at the API level — no partial uploads
- **BR-049-A-03:** Tag values in frontmatter are validated against kb-config.json taxonomy; unknown tags are preserved but flagged
- **BR-049-A-04:** Auto-created kb-config.json uses the exact default tags from HR-049.8; no customization during auto-creation
- **BR-049-A-05:** Folder deletion is recursive — all files and sub-folders are deleted

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| KB root doesn't exist on first API call | Auto-create root + kb-config.json with defaults |
| .md file has no YAML frontmatter block | Return file with frontmatter fields as null |
| .md file has malformed YAML frontmatter | Return file with frontmatter as null (graceful degradation) |
| Folder name contains special characters | Allow any characters valid for the OS file system; reject `/` and `\0` |
| File path traversal attempt (`../`) | Reject with 400 Bad Request — all paths must resolve within KB root |
| Empty folder listing | Return empty array (not error) |
| Concurrent write to same file | Last-write-wins (file-system semantics) |
| kb-config.json manually corrupted | Return 500 with descriptive error message |
| Delete KB root folder | Reject with 403 Forbidden — root cannot be deleted |
| Search with empty query string | Return all files (unfiltered listing) |

## Out of Scope

- Full-text content search within markdown body (V2)
- File versioning / history (git provides this)
- Pagination for file listings (YAGNI for ≤500 files)
- kb-config.json modification API (V2 — manual edit only for V1)
- Archive extraction (.zip/.7z) — handled by FEATURE-049-E
- Real-time file watching / websocket notifications
- Binary file content serving (PDFs/images served as static files)

## Technical Considerations

- Follow existing X-IPE service patterns in `src/x_ipe/services/` for service layer
- Follow existing X-IPE route patterns in `src/x_ipe/routes/` for API endpoints
- YAML frontmatter parsing: split on first two `---` markers, parse YAML between them
- File tree can be built with `os.walk()` — single pass, filter out `.intake/`
- Search implementation: iterate files, match against cached frontmatter (in-memory for V1)
- Consider caching the file tree + frontmatter index on first load, invalidate on write operations

## Open Questions

- None — all questions resolved via DAO (DAO-037)
