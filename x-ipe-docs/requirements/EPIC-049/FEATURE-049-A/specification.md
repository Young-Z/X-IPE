# Feature Specification: KB Backend & Storage Foundation

> Feature ID: FEATURE-049-A
> Epic ID: EPIC-049
> Version: v1.0
> Status: Refined
> Last Updated: 03-11-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-11-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| KB Browse Articles | HTML | [../mockups/kb-interface-v1.html](../mockups/kb-interface-v1.html) | Scene 1 — grid/list browse with tags, search, sort | current |
| KB Article Detail | HTML | [../mockups/kb-interface-v1.html](../mockups/kb-interface-v1.html) | Scene 2 — article detail with frontmatter display | current |

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

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-01a | KB root (`x-ipe-docs/knowledge-base/`) auto-created on first API call when it does not exist | API |
| AC-049-A-01b | `kb-config.json` auto-generated with default lifecycle tags: Ideation, Requirement, Design, Implementation, Testing, Deployment, Maintenance | Unit |
| AC-049-A-01c | `kb-config.json` auto-generated with default domain tags: API, Authentication, UI-UX, Database, Infrastructure, Security, Performance, Integration, Documentation, Analytics | Unit |
| AC-049-A-01d | `kb-config.json` includes empty `agent_write_allowlist` array and `ai_librarian` settings object | Unit |

### AC-049-A-02: Folder Listing API

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-02a | `GET /api/kb/tree` returns full folder/file tree structure as nested JSON | API |
| AC-049-A-02b | Each tree node includes: name, path (relative to KB root), type (`folder` or `file`), children (for folders) | API |
| AC-049-A-02c | File nodes include metadata: size_bytes, modified_date, file_type extension | API |
| AC-049-A-02d | `.intake/` folder excluded from tree response | API |
| AC-049-A-02e | Response returns within 500ms for up to 500 files (NFR-049.2) | API |

### AC-049-A-03: Folder CRUD Operations

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-03a | `POST /api/kb/folders` creates folder at specified path; returns 201 with folder info | API |
| AC-049-A-03b | `PATCH /api/kb/folders` renames a folder; returns 200 with updated info | API |
| AC-049-A-03c | `PUT /api/kb/folders/move` moves folder to new parent; returns 200 | API |
| AC-049-A-03d | `DELETE /api/kb/folders` deletes folder and contents; returns 200 with deleted count | API |
| AC-049-A-03e | Creating folder with existing name at same level returns 409 Conflict | API |
| AC-049-A-03f | Moving folder into itself or a descendant returns 400 Bad Request | API |

### AC-049-A-04: File Listing with Metadata

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-04a | `GET /api/kb/files?folder={path}` returns files in specified folder with frontmatter metadata | API |
| AC-049-A-04b | Each file includes: name, path, size_bytes, modified_date, frontmatter (title, tags, author, created, auto_generated) | API |
| AC-049-A-04c | Files without YAML frontmatter return null for frontmatter fields (no error) | API |
| AC-049-A-04d | Non-markdown files (PDF, images) return file metadata without frontmatter parsing | API |
| AC-049-A-04e | Results sortable via `sort` query param: `modified` (default), `name`, `created`, `untagged` | API |

### AC-049-A-05: File CRUD Operations

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-05a | `GET /api/kb/files/{path}` returns file content (markdown body) and parsed frontmatter | API |
| AC-049-A-05b | `POST /api/kb/files` creates new file with content and optional frontmatter; returns 201 | API |
| AC-049-A-05c | `PUT /api/kb/files/{path}` updates file content and/or frontmatter; returns 200 | API |
| AC-049-A-05d | `DELETE /api/kb/files/{path}` deletes a file; returns 200 | API |
| AC-049-A-05e | Missing frontmatter auto-populates: title (from filename), tags (empty), author ("unknown"), created (current date), auto_generated (false) | Unit |
| AC-049-A-05f | Files >10MB rejected with 413 Payload Too Large | API |

### AC-049-A-06: File Move Operation

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-06a | `PUT /api/kb/files/move` moves file to new folder; returns 200 with new path | API |
| AC-049-A-06b | Moving to non-existent folder returns 404 Not Found | API |
| AC-049-A-06c | Move operation creates destination file and removes source file atomically | Integration |

### AC-049-A-07: YAML Frontmatter Parsing

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-07a | Frontmatter extracted from `---` delimited YAML block at top of .md files | Unit |
| AC-049-A-07b | Supported fields: title (string), tags (object with lifecycle[] and domain[]), author (string), created (date string), auto_generated (boolean) | Unit |
| AC-049-A-07c | Invalid YAML in frontmatter returns file with frontmatter as null (graceful degradation) | Unit |
| AC-049-A-07d | Frontmatter update preserves markdown body content below the `---` block | Unit |

### AC-049-A-08: Tag Taxonomy API

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-08a | `GET /api/kb/config` returns parsed kb-config.json including tags.lifecycle and tags.domain arrays | API |
| AC-049-A-08b | Tag arrays contain string values matching predefined taxonomy | Unit |
| AC-049-A-08c | Response includes agent_write_allowlist and ai_librarian configuration sections | API |

### AC-049-A-09: Search API

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-09a | `GET /api/kb/search?q={query}` returns files matching query against filename and frontmatter fields | API |
| AC-049-A-09b | Search matches against: filename, frontmatter.title, frontmatter.tags (lifecycle + domain), frontmatter.author | Unit |
| AC-049-A-09c | Search is case-insensitive | Unit |
| AC-049-A-09d | Results include full file metadata (same as file listing response) | API |
| AC-049-A-09e | `GET /api/kb/search?tag={tag}&tag_type={lifecycle\|domain}` filters by specific tag | API |
| AC-049-A-09f | Combined query + tag filter supported: `?q={query}&tag={tag}&tag_type={type}` | API |
| AC-049-A-09g | Search returns within 300ms for filename+frontmatter matching (NFR-049.3) | API |

### AC-049-A-10: URL Bookmark Format

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-10a | `.url.md` files parsed with additional frontmatter field: `url` (string, required) | Unit |
| AC-049-A-10b | `GET /api/kb/files/{path}` for `.url.md` files returns url field in frontmatter | API |
| AC-049-A-10c | Creating `.url.md` file requires `url` field in frontmatter; missing url returns 400 | API |
| AC-049-A-10d | URL bookmarks included in file listing and search results with `file_type: "url_bookmark"` indicator | API |

### AC-049-A-11: File Type Validation

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-A-11a | Accepted file types: `.md`, `.url.md`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.svg` | Unit |
| AC-049-A-11b | Upload of unsupported file types returns 415 Unsupported Media Type | API |
| AC-049-A-11c | File type determined by extension, not content sniffing | Unit |

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
