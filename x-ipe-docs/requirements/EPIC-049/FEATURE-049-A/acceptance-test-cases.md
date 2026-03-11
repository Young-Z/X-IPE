# Acceptance Test Cases

> Feature: FEATURE-049-A — KB Backend & Storage Foundation
> Generated: 2026-03-11
> Status: Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-049-A |
| Feature Title | KB Backend & Storage Foundation |
| Total Test Cases | 69 |
| Priority | P0 (Critical) |
| Target URL | N/A (backend) |

---

## Prerequisites

- [x] Feature code implemented (`kb_service.py`, `kb_routes.py`)
- [x] Test environment ready (pytest via `uv`)
- [x] Flask test client available
- [x] Temporary project directory for isolated tests
- [x] 69 unit tests passing (67 original + 2 gap fixes)

---

## Test Cases

### TC-001 – TC-007: KB Root Initialization

**Acceptance Criteria Reference:** AC-049-A-01 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit

**Assigned Tool:** pytest

**Preconditions:**
- KB service instantiated with a temporary project directory
- No pre-existing `knowledge-base/` directory

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | project_root | `{temp_dir}` | Pytest `tmp_path` fixture |
| Expected | kb_root | `{temp_dir}/x-ipe-docs/knowledge-base/` | Auto-created |
| Expected | config_file | `kb-config.json` | Auto-generated with defaults |
| Expected | lifecycle_tags | Ideation, Requirement, Design, Implementation, Testing, Deployment, Maintenance | 7 default tags |
| Expected | domain_tags | API, Authentication, UI-UX, Database, Infrastructure, Security, Performance, Integration, Documentation, Analytics | 10 default tags |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Initialize KB service | `KBService(project_root)` | temp directory | Service created |
| 2 | Call ensure_kb_root | `kb_service.ensure_kb_root()` | — | KB root directory created |
| 3 | Verify config | `kb-config.json` | — | Contains default lifecycle, domain tags, empty allowlist, ai_librarian |
| 4 | Call again | `kb_service.ensure_kb_root()` | — | Idempotent — no overwrite |

**Expected Outcome:** KB root directory and `kb-config.json` auto-created with correct default tags; repeated calls are idempotent.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-001 | Auto-create KB root directory on first API call | unit | `test_ensure_kb_root_creates_directory` | ✅ Pass |
| TC-002 | Auto-generate `kb-config.json` with defaults | unit | `test_ensure_kb_root_creates_config` | ✅ Pass |
| TC-003 | Default lifecycle tags match spec | unit | `test_default_lifecycle_tags` | ✅ Pass |
| TC-004 | Default domain tags match spec | unit | `test_default_domain_tags` | ✅ Pass |
| TC-005 | Empty `agent_write_allowlist` array in config | unit | `test_default_agent_write_allowlist` | ✅ Pass |
| TC-006 | `ai_librarian` settings in config | unit | `test_default_ai_librarian_settings` | ✅ Pass |
| TC-007 | Idempotent — second call does not overwrite | unit | `test_ensure_kb_root_idempotent` | ✅ Pass |

**Execution Notes:** All 7 tests pass. Gap-free coverage of AC-049-A-01.

---

### TC-008 – TC-014: Folder Listing API

**Acceptance Criteria Reference:** AC-049-A-02 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized with `ensure_kb_root()`
- Test files and folders seeded as needed per TC

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | endpoint | `GET /api/kb/tree` | Route-level test |
| Input | test_file | `article.md` | Seeded in KB root |
| Input | test_folder | `guides/` | Seeded with children |
| Input | excluded_dir | `.intake/` | Must not appear in tree |
| Expected | node_fields | name, path, type, children | Per tree node |
| Expected | file_metadata | size_bytes, modified_date, file_type | File nodes only |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Seed empty KB | KB root | — | Empty directory |
| 2 | Call get_tree | `kb_service.get_tree()` | — | Returns empty list |
| 3 | Add files | KB root | `article.md` | Tree includes file node |
| 4 | Add folders | KB root | `guides/intro.md` | Tree includes folder with children |
| 5 | Add .intake | KB root | `.intake/staging.md` | .intake excluded from tree |
| 6 | Verify metadata | File node | — | size_bytes, modified_date, file_type present |
| 7 | Test route | `GET /api/kb/tree` | — | Returns 200 with tree JSON |

**Expected Outcome:** Tree API returns complete folder/file hierarchy excluding `.intake/` and `kb-config.json`, with file metadata on leaf nodes.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-008 | Empty KB returns empty tree | unit | `test_get_tree_empty_kb` | ✅ Pass |
| TC-009 | Tree includes files | unit | `test_get_tree_with_files` | ✅ Pass |
| TC-010 | Tree includes folders with children | unit | `test_get_tree_with_folders` | ✅ Pass |
| TC-011 | `.intake/` excluded from tree | unit | `test_get_tree_excludes_intake` | ✅ Pass |
| TC-012 | `kb-config.json` excluded from tree | unit | `test_get_tree_excludes_config` | ✅ Pass |
| TC-013 | File nodes include size, modified_date, file_type | unit | `test_get_tree_file_has_metadata` | ✅ Pass |
| TC-014 | `GET /api/kb/tree` route returns 200 | backend-api | `test_get_tree_route` | ✅ Pass |

**Execution Notes:** All 7 tests pass. Full coverage of AC-049-A-02.

---

### TC-015 – TC-022: Folder CRUD Operations

**Acceptance Criteria Reference:** AC-049-A-03 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized
- Target parent folders exist for nested/move operations

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | folder_name | `"guides"` | New folder to create |
| Input | nested_path | `"guides/advanced"` | Nested folder |
| Input | rename_to | `"tutorials"` | Rename target |
| Input | move_target | `"archive/"` | Move destination |
| Expected | create_status | 201 | Created |
| Expected | duplicate_status | 409 | Conflict |
| Expected | self_move_status | 400 | Bad Request |
| Expected | delete_root_status | 403 | Forbidden |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create folder | `POST /api/kb/folders` | `{"path": "guides"}` | 201 with folder info |
| 2 | Create nested | `POST /api/kb/folders` | `{"path": "guides/advanced"}` | 201 |
| 3 | Duplicate create | `POST /api/kb/folders` | `{"path": "guides"}` | 409 Conflict |
| 4 | Rename folder | `PATCH /api/kb/folders` | `{"old": "guides", "new": "tutorials"}` | 200 |
| 5 | Move folder | `PUT /api/kb/folders/move` | `{"path": "tutorials", "dest": "archive/"}` | 200 |
| 6 | Move into self | `PUT /api/kb/folders/move` | `{"path": "a", "dest": "a/b"}` | 400 Bad Request |
| 7 | Delete folder | `DELETE /api/kb/folders` | `{"path": "archive"}` | 200 |
| 8 | Delete root | `DELETE /api/kb/folders` | `{"path": ""}` | 403 Forbidden |

**Expected Outcome:** Full CRUD lifecycle for folders with proper error handling for duplicates, self-move, and root deletion.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-015 | Create folder returns 201 | unit | `test_create_folder` | ✅ Pass |
| TC-016 | Create nested folder | unit | `test_create_folder_nested` | ✅ Pass |
| TC-017 | Duplicate folder returns 409 | unit | `test_create_folder_duplicate_409` | ✅ Pass |
| TC-018 | Rename folder | unit | `test_rename_folder` | ✅ Pass |
| TC-019 | Move folder to new parent | unit | `test_move_folder` | ✅ Pass |
| TC-020 | Move folder into itself returns 400 | unit | `test_move_folder_into_self_400` | ✅ Pass |
| TC-021 | Delete folder | unit | `test_delete_folder` | ✅ Pass |
| TC-022 | Delete KB root forbidden (403) | unit | `test_delete_root_403` | ✅ Pass |

**Execution Notes:** All 8 tests pass. Full coverage of AC-049-A-03.

---

### TC-023 – TC-031: File Listing with Metadata

**Acceptance Criteria Reference:** AC-049-A-04 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized with markdown files containing YAML frontmatter
- Files with and without frontmatter present for null-check tests

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | endpoint | `GET /api/kb/files?folder={path}` | File listing route |
| Input | sort_options | `name`, `created`, `untagged` | Sort parameter values |
| Input | md_with_fm | `article.md` with `title`, `tags`, `author` | Frontmatter present |
| Input | md_without_fm | `plain.md` with no YAML block | Frontmatter null |
| Input | non_md | `diagram.png` | Non-markdown file |
| Expected | file_fields | name, path, size_bytes, modified_date, frontmatter | Per file |
| Expected | nonexistent_status | 404 | Not Found |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | List root files | `kb_service.list_files("")` | — | Returns files in root |
| 2 | List subfolder | `kb_service.list_files("guides")` | — | Returns files in subfolder |
| 3 | Check frontmatter | File with YAML | — | Frontmatter parsed into object |
| 4 | Check no frontmatter | File without YAML | — | Frontmatter is null |
| 5 | Sort by name | `sort="name"` | — | Alphabetical ascending |
| 6 | Sort by created | `sort="created"` | — | By frontmatter created date descending |
| 7 | Sort untagged-first | `sort="untagged"` | — | Untagged files appear first |
| 8 | Nonexistent folder | `GET /api/kb/files?folder=missing` | — | 404 |
| 9 | Non-markdown file | `diagram.png` | — | Metadata without frontmatter |

**Expected Outcome:** File listing returns metadata with parsed frontmatter, supports multiple sort modes, and returns 404 for nonexistent folders.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-023 | List files in root folder | unit | `test_list_files_in_root` | ✅ Pass |
| TC-024 | List files in subfolder | unit | `test_list_files_in_subfolder` | ✅ Pass |
| TC-025 | Files include parsed frontmatter | unit | `test_list_files_with_frontmatter` | ✅ Pass |
| TC-026 | Files without frontmatter return null | unit | `test_list_files_no_frontmatter_returns_null` | ✅ Pass |
| TC-027 | Sort by name (ascending) | unit | `test_list_files_sort_by_name` | ✅ Pass |
| TC-028 | Sort by created date (descending) | unit | `test_list_files_sort_by_created` | ✅ Pass |
| TC-029 | Sort untagged-first | unit | `test_list_files_sort_untagged_first` | ✅ Pass |
| TC-030 | Non-existent folder returns 404 | backend-api | `test_list_files_nonexistent_folder_404` | ✅ Pass |
| TC-031 | Non-markdown files omit frontmatter | unit | `test_non_markdown_file_no_frontmatter` | ✅ Pass |

**Execution Notes:** All 9 tests pass. TC-028 was a gap fix for `sort=created`.

---

### TC-032 – TC-039: File CRUD Operations

**Acceptance Criteria Reference:** AC-049-A-05 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized
- Target folders exist for file creation

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | file_path | `"guides/intro.md"` | New file path |
| Input | content | `"# Introduction\nBody text"` | Markdown content |
| Input | frontmatter | `{title: "Intro", tags: {lifecycle: ["Design"]}}` | Optional YAML |
| Input | oversize_content | 11 MB string | Exceeds 10 MB limit |
| Expected | create_status | 201 | Created |
| Expected | oversize_status | 413 | Payload Too Large |
| Expected | auto_fields | title (from filename), tags (empty), author ("unknown"), created (now) | Auto-populated |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create file | `POST /api/kb/files` | path, content, frontmatter | 201 with file info |
| 2 | Verify auto-populate | Create without frontmatter | — | title, tags, author, created auto-set |
| 3 | Get file | `GET /api/kb/files/{path}` | — | Returns content + frontmatter |
| 4 | Update content | `PUT /api/kb/files/{path}` | new content | 200 with updated file |
| 5 | Update frontmatter | `PUT /api/kb/files/{path}` | new tags | 200 with updated frontmatter |
| 6 | Delete file | `DELETE /api/kb/files/{path}` | — | 200 |
| 7 | Size limit | `POST /api/kb/files` | 11 MB content | 413 |
| 8 | Route test | `POST /api/kb/files` via Flask client | — | 201 |

**Expected Outcome:** Full file CRUD with auto-populated frontmatter, size validation, and proper route responses.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-032 | Create file with frontmatter | unit | `test_create_file_with_frontmatter` | ✅ Pass |
| TC-033 | Auto-populate frontmatter on create | unit | `test_create_file_auto_populate` | ✅ Pass |
| TC-034 | Get file returns content + frontmatter | unit | `test_get_file` | ✅ Pass |
| TC-035 | Update file content | unit | `test_update_file_content` | ✅ Pass |
| TC-036 | Update file frontmatter | unit | `test_update_file_frontmatter` | ✅ Pass |
| TC-037 | Delete file | unit | `test_delete_file` | ✅ Pass |
| TC-038 | File >10 MB rejected with 413 | unit | `test_create_file_size_limit` | ✅ Pass |
| TC-039 | `POST /api/kb/files` route returns 201 | backend-api | `test_create_file_route_201` | ✅ Pass |

**Execution Notes:** All 8 tests pass. Full coverage of AC-049-A-05.

---

### TC-040 – TC-041: File Move Operation

**Acceptance Criteria Reference:** AC-049-A-06 from specification.md

**Priority:** P1 (High)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized with source file and destination folder
- Non-existent target folder for error case

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | source_path | `"article.md"` | File to move |
| Input | dest_folder | `"archive/"` | Existing destination |
| Input | missing_folder | `"nonexistent/"` | Does not exist |
| Expected | move_status | 200 | Success with new path |
| Expected | missing_status | 404 | Not Found |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Move file | `PUT /api/kb/files/move` | source + dest | 200 with new path |
| 2 | Move to missing | `PUT /api/kb/files/move` | source + nonexistent | 404 |

**Expected Outcome:** File move succeeds to existing folders and returns 404 for nonexistent destinations.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-040 | Move file to new folder | unit | `test_move_file` | ✅ Pass |
| TC-041 | Move to non-existent folder returns 404 | backend-api | `test_move_file_to_nonexistent_folder_404` | ✅ Pass |

**Execution Notes:** All 2 tests pass. Full coverage of AC-049-A-06.

---

### TC-042 – TC-045: YAML Frontmatter Parsing

**Acceptance Criteria Reference:** AC-049-A-07 from specification.md

**Priority:** P0 (Critical)

**Test Type:** unit

**Assigned Tool:** pytest

**Preconditions:**
- KB service initialized
- Test markdown files with valid, missing, and malformed YAML frontmatter

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | valid_yaml | `---\ntitle: Test\ntags:\n  lifecycle: [Design]\n---\nBody` | Valid frontmatter |
| Input | no_yaml | `# Just markdown\nNo frontmatter block` | Missing `---` delimiters |
| Input | bad_yaml | `---\n[invalid: yaml: :\n---\nBody` | Malformed YAML |
| Expected | valid_result | `{title: "Test", tags: {lifecycle: ["Design"]}}` | Parsed object |
| Expected | missing_result | `None` | Graceful null |
| Expected | bad_result | `None` | Graceful degradation |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Parse valid | Frontmatter parser | Valid YAML markdown | Returns parsed object |
| 2 | Parse missing | Frontmatter parser | No YAML markdown | Returns None |
| 3 | Parse malformed | Frontmatter parser | Bad YAML markdown | Returns None (no error) |
| 4 | Update frontmatter | File with body | New frontmatter values | Body content preserved |

**Expected Outcome:** Frontmatter parsing handles valid, missing, and malformed YAML gracefully; updates preserve body content.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-042 | Valid frontmatter parsed correctly | unit | `test_valid_frontmatter` | ✅ Pass |
| TC-043 | No frontmatter returns None | unit | `test_no_frontmatter_returns_none` | ✅ Pass |
| TC-044 | Malformed YAML returns None | unit | `test_malformed_yaml_returns_none` | ✅ Pass |
| TC-045 | Frontmatter update preserves body | unit | `test_frontmatter_preserves_body_on_update` | ✅ Pass |

**Execution Notes:** All 4 tests pass. Full coverage of AC-049-A-07.

---

### TC-046 – TC-049: Tag Taxonomy API

**Acceptance Criteria Reference:** AC-049-A-08 from specification.md

**Priority:** P1 (High)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized with valid `kb-config.json`
- Corrupted config file for error case

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | endpoint | `GET /api/kb/config` | Config route |
| Input | corrupt_config | `"not valid json {{"` | Malformed JSON |
| Expected | config_fields | tags.lifecycle, tags.domain, agent_write_allowlist, ai_librarian | Required sections |
| Expected | route_status | 200 | Success |
| Expected | corrupt_status | 500 | Internal Server Error |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Get config | `kb_service.get_config()` | — | Returns parsed config |
| 2 | Verify ai_librarian | Config object | — | `ai_librarian` section present |
| 3 | Test route | `GET /api/kb/config` | — | 200 with config JSON |
| 4 | Corrupt config | Write invalid JSON to config file | — | 500 with error message |

**Expected Outcome:** Config API returns complete taxonomy including ai_librarian; corrupt config returns 500.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-046 | `GET /api/kb/config` returns config | backend-api | `test_get_config` | ✅ Pass |
| TC-047 | Config includes `ai_librarian` section | unit | `test_get_config_includes_ai_librarian` | ✅ Pass |
| TC-048 | Config route returns 200 | backend-api | `test_get_config_route` | ✅ Pass |
| TC-049 | Corrupt config returns 500 | backend-api | `test_corrupt_config_500` | ✅ Pass |

**Execution Notes:** All 4 tests pass. Full coverage of AC-049-A-08.

---

### TC-050 – TC-058: Search API

**Acceptance Criteria Reference:** AC-049-A-09 from specification.md

**Priority:** P1 (High)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized with multiple markdown files
- Files with various frontmatter fields (title, author, tags) for search matching

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | search_endpoint | `GET /api/kb/search?q={query}` | Search route |
| Input | query_filename | `"intro"` | Matches filename |
| Input | query_title | `"Getting Started"` | Matches frontmatter title |
| Input | query_author | `"Alice"` | Matches frontmatter author |
| Input | tag_filter | `tag=Design&tag_type=lifecycle` | Tag filter |
| Input | empty_query | `""` | Returns all files |
| Expected | case_insensitive | `"INTRO"` matches `"intro.md"` | Case-insensitive matching |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Search by filename | `kb_service.search(q="intro")` | — | Matches filename |
| 2 | Search by title | `kb_service.search(q="Getting Started")` | — | Matches frontmatter title |
| 3 | Search by author | `kb_service.search(q="Alice")` | — | Matches frontmatter author |
| 4 | Case-insensitive | `kb_service.search(q="INTRO")` | — | Still matches |
| 5 | Filter by lifecycle tag | `search(tag="Design", tag_type="lifecycle")` | — | Filtered results |
| 6 | Filter by domain tag | `search(tag="API", tag_type="domain")` | — | Filtered results |
| 7 | Combined query + tag | `search(q="intro", tag="Design")` | — | Intersection of matches |
| 8 | Empty query | `kb_service.search(q="")` | — | Returns all files |
| 9 | Route test | `GET /api/kb/search?q=test` | — | 200 with results |

**Expected Outcome:** Search matches against filename, title, author, and tags with case-insensitive matching and combined filters.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-050 | Search matches filename | unit | `test_search_by_filename` | ✅ Pass |
| TC-051 | Search matches frontmatter title | unit | `test_search_by_title` | ✅ Pass |
| TC-052 | Search is case-insensitive | unit | `test_search_case_insensitive` | ✅ Pass |
| TC-053 | Search matches frontmatter author | unit | `test_search_by_author` | ✅ Pass |
| TC-054 | Filter by lifecycle tag | unit | `test_search_by_tag_lifecycle` | ✅ Pass |
| TC-055 | Filter by domain tag | unit | `test_search_by_tag_domain` | ✅ Pass |
| TC-056 | Combined query + tag filter | unit | `test_search_combined_query_and_tag` | ✅ Pass |
| TC-057 | Empty query returns all files | unit | `test_search_empty_query_returns_all` | ✅ Pass |
| TC-058 | `GET /api/kb/search` route returns 200 | backend-api | `test_search_route` | ✅ Pass |

**Execution Notes:** All 9 tests pass. TC-053 was a gap fix for author search.

---

### TC-059 – TC-061: URL Bookmark Format

**Acceptance Criteria Reference:** AC-049-A-10 from specification.md

**Priority:** P2 (Medium)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized
- URL bookmark requires `url` field in frontmatter

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | bookmark_path | `"links/reference.url.md"` | URL bookmark file |
| Input | bookmark_fm | `{url: "https://example.com", title: "Example"}` | Required url field |
| Input | missing_url_fm | `{title: "No URL"}` | Missing required url |
| Expected | create_status | 201 | Created |
| Expected | missing_url_status | 400 | Bad Request |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create bookmark | `POST /api/kb/files` | .url.md with url field | 201 |
| 2 | Missing url | `POST /api/kb/files` | .url.md without url | 400 |
| 3 | Search includes bookmark | `kb_service.search()` | — | Bookmark in results |

**Expected Outcome:** URL bookmarks created with required `url` field; missing url rejected; bookmarks appear in search.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-059 | Create `.url.md` bookmark | unit | `test_create_url_bookmark` | ✅ Pass |
| TC-060 | Missing `url` field returns 400 | backend-api | `test_create_url_bookmark_missing_url_400` | ✅ Pass |
| TC-061 | URL bookmark appears in search | unit | `test_url_bookmark_in_search` | ✅ Pass |

**Execution Notes:** All 3 tests pass. Full coverage of AC-049-A-10.

---

### TC-062 – TC-064: File Type Validation

**Acceptance Criteria Reference:** AC-049-A-11 from specification.md

**Priority:** P1 (High)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized
- Various file extensions to test acceptance/rejection

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | accepted_ext | `.md` | Standard markdown |
| Input | accepted_url | `.url.md` | URL bookmark |
| Input | rejected_ext | `.exe` | Unsupported type |
| Expected | accepted_status | 201 | Created |
| Expected | rejected_status | 415 | Unsupported Media Type |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Create .md | `POST /api/kb/files` | `article.md` | Accepted (201) |
| 2 | Create unsupported | `POST /api/kb/files` | `script.exe` | 415 Unsupported |
| 3 | Create .url.md | `POST /api/kb/files` | `link.url.md` | Accepted (201) |

**Expected Outcome:** Accepted file types (.md, .url.md) pass validation; unsupported types rejected with 415.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-062 | `.md` files accepted | unit | `test_accepted_md` | ✅ Pass |
| TC-063 | Unsupported type returns 415 | backend-api | `test_unsupported_type_415` | ✅ Pass |
| TC-064 | `.url.md` accepted | unit | `test_url_md_accepted` | ✅ Pass |

**Execution Notes:** All 3 tests pass. Full coverage of AC-049-A-11.

---

### TC-065 – TC-068: Edge Cases & Error Handling

**Acceptance Criteria Reference:** Edge Cases table from specification.md

**Priority:** P1 (High)

**Test Type:** unit, backend-api

**Assigned Tool:** pytest

**Preconditions:**
- KB root initialized
- Flask test client for route-level tests

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | traversal_path | `"../../etc/passwd"` | Path traversal attempt |
| Input | traversal_create | `"../outside.md"` | Traversal in create |
| Input | oversize_file | 11 MB content | Exceeds limit |
| Expected | traversal_status | 400 | Bad Request |
| Expected | error_format | `{"error": "...", "message": "..."}` | JSON error body |
| Expected | oversize_status | 413 | Payload Too Large |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Path traversal read | `GET /api/kb/files/../../etc/passwd` | — | 400 Bad Request |
| 2 | Path traversal create | `POST /api/kb/files` | `../outside.md` | 400 Bad Request |
| 3 | Verify error format | Any error response | — | JSON with `error` + `message` fields |
| 4 | File size limit | `POST /api/kb/files` | 11 MB body | 413 |

**Expected Outcome:** Path traversal blocked, error responses use standard JSON format, size limits enforced at route level.

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-065 | Path traversal blocked (400) | unit | `test_traversal_attempt_400` | ✅ Pass |
| TC-066 | Path traversal in create blocked (400) | unit | `test_traversal_in_create_400` | ✅ Pass |
| TC-067 | Error response format is JSON | backend-api | `test_error_format` | ✅ Pass |
| TC-068 | File size limit 413 (route-level) | backend-api | `test_file_413` | ✅ Pass |

**Execution Notes:** All 4 tests pass. Security and error-handling edge cases verified.

---

## Test Execution Summary

| Test Case | Title | Type | Priority | Status | Notes |
|-----------|-------|------|----------|--------|-------|
| TC-001 – TC-007 | KB Root Initialization | unit | P0 | ✅ Pass | AC-049-A-01 |
| TC-008 – TC-014 | Folder Listing API | unit, backend-api | P0 | ✅ Pass | AC-049-A-02 |
| TC-015 – TC-022 | Folder CRUD Operations | unit, backend-api | P0 | ✅ Pass | AC-049-A-03 |
| TC-023 – TC-031 | File Listing with Metadata | unit, backend-api | P0 | ✅ Pass | AC-049-A-04; TC-028 gap fix |
| TC-032 – TC-039 | File CRUD Operations | unit, backend-api | P0 | ✅ Pass | AC-049-A-05 |
| TC-040 – TC-041 | File Move Operation | unit, backend-api | P1 | ✅ Pass | AC-049-A-06 |
| TC-042 – TC-045 | YAML Frontmatter Parsing | unit | P0 | ✅ Pass | AC-049-A-07 |
| TC-046 – TC-049 | Tag Taxonomy API | unit, backend-api | P1 | ✅ Pass | AC-049-A-08 |
| TC-050 – TC-058 | Search API | unit, backend-api | P1 | ✅ Pass | AC-049-A-09; TC-053 gap fix |
| TC-059 – TC-061 | URL Bookmark Format | unit, backend-api | P2 | ✅ Pass | AC-049-A-10 |
| TC-062 – TC-064 | File Type Validation | unit, backend-api | P1 | ✅ Pass | AC-049-A-11 |
| TC-065 – TC-068 | Edge Cases & Error Handling | unit, backend-api | P1 | ✅ Pass | Security + robustness |

---

## Execution Results

**Execution Date:** 2026-03-11
**Executed By:** Echo 📡
**Environment:** dev

| Metric | Value |
|--------|-------|
| Total Tests | 69 |
| Passed | 69 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

**Test Runner:** `uv run python -m pytest tests/test_kb_service.py -v`

### Gap Fixes Applied

| Gap | AC | Test Added | Description |
|-----|----|------------|-------------|
| Gap 1 | AC-049-A-04 | `test_list_files_sort_by_created` (TC-028) | Verifies `sort='created'` orders files by frontmatter `created` date descending |
| Gap 2 | AC-049-A-09 | `test_search_by_author` (TC-053) | Verifies search query matches `frontmatter.author` field |
