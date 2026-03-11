# Acceptance Test Cases

> Feature: FEATURE-049-A — KB Backend & Storage Foundation
> Generated: 2026-03-11
> Status: Executed

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-049-A |
| Feature Title | KB Backend & Storage Foundation |
| Total Test Cases | 69 |
| Test Types | backend-api, unit |
| Assigned Tool | x-ipe-tool-implementation-python |

## Prerequisites

- [x] Feature code implemented (`kb_service.py`, `kb_routes.py`)
- [x] Test environment ready (pytest via `uv`)
- [x] 69 unit tests passing (67 original + 2 gap fixes)

---

## Test Cases

### AC-049-A-01: KB Root Initialization

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-001 | Auto-create KB root directory on first API call | unit | `test_ensure_kb_root_creates_directory` | ✅ Pass |
| TC-002 | Auto-generate `kb-config.json` with defaults | unit | `test_ensure_kb_root_creates_config` | ✅ Pass |
| TC-003 | Default lifecycle tags match spec | unit | `test_default_lifecycle_tags` | ✅ Pass |
| TC-004 | Default domain tags match spec | unit | `test_default_domain_tags` | ✅ Pass |
| TC-005 | Empty `agent_write_allowlist` array in config | unit | `test_default_agent_write_allowlist` | ✅ Pass |
| TC-006 | `ai_librarian` settings in config | unit | `test_default_ai_librarian_settings` | ✅ Pass |
| TC-007 | Idempotent — second call does not overwrite | unit | `test_ensure_kb_root_idempotent` | ✅ Pass |

### AC-049-A-02: Folder Listing API

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-008 | Empty KB returns empty tree | unit | `test_get_tree_empty_kb` | ✅ Pass |
| TC-009 | Tree includes files | unit | `test_get_tree_with_files` | ✅ Pass |
| TC-010 | Tree includes folders with children | unit | `test_get_tree_with_folders` | ✅ Pass |
| TC-011 | `.intake/` excluded from tree | unit | `test_get_tree_excludes_intake` | ✅ Pass |
| TC-012 | `kb-config.json` excluded from tree | unit | `test_get_tree_excludes_config` | ✅ Pass |
| TC-013 | File nodes include size, modified_date, file_type | unit | `test_get_tree_file_has_metadata` | ✅ Pass |
| TC-014 | `GET /api/kb/tree` route returns 200 | backend-api | `test_get_tree_route` | ✅ Pass |

### AC-049-A-03: Folder CRUD Operations

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

### AC-049-A-04: File Listing with Metadata

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

### AC-049-A-05: File CRUD Operations

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

### AC-049-A-06: File Move Operation

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-040 | Move file to new folder | unit | `test_move_file` | ✅ Pass |
| TC-041 | Move to non-existent folder returns 404 | unit | `test_move_file_to_nonexistent_folder_404` | ✅ Pass |

### AC-049-A-07: YAML Frontmatter Parsing

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-042 | Valid frontmatter parsed correctly | unit | `test_valid_frontmatter` | ✅ Pass |
| TC-043 | No frontmatter returns None | unit | `test_no_frontmatter_returns_none` | ✅ Pass |
| TC-044 | Malformed YAML returns None | unit | `test_malformed_yaml_returns_none` | ✅ Pass |
| TC-045 | Frontmatter update preserves body | unit | `test_frontmatter_preserves_body_on_update` | ✅ Pass |

### AC-049-A-08: Tag Taxonomy API

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-046 | `GET /api/kb/config` returns config | backend-api | `test_get_config` | ✅ Pass |
| TC-047 | Config includes `ai_librarian` section | unit | `test_get_config_includes_ai_librarian` | ✅ Pass |
| TC-048 | Config route returns 200 | backend-api | `test_get_config_route` | ✅ Pass |
| TC-049 | Corrupt config returns 500 | backend-api | `test_corrupt_config_500` | ✅ Pass |

### AC-049-A-09: Search API

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

### AC-049-A-10: URL Bookmark Format

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-059 | Create `.url.md` bookmark | unit | `test_create_url_bookmark` | ✅ Pass |
| TC-060 | Missing `url` field returns 400 | unit | `test_create_url_bookmark_missing_url_400` | ✅ Pass |
| TC-061 | URL bookmark appears in search | unit | `test_url_bookmark_in_search` | ✅ Pass |

### AC-049-A-11: File Type Validation

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-062 | `.md` files accepted | unit | `test_accepted_md` | ✅ Pass |
| TC-063 | Unsupported type returns 415 | unit | `test_unsupported_type_415` | ✅ Pass |
| TC-064 | `.url.md` accepted | unit | `test_url_md_accepted` | ✅ Pass |

### Edge Cases & Error Handling

| TC | Description | Type | Test Function | Status |
|----|-------------|------|---------------|--------|
| TC-065 | Path traversal blocked (400) | unit | `test_traversal_attempt_400` | ✅ Pass |
| TC-066 | Path traversal in create blocked (400) | unit | `test_traversal_in_create_400` | ✅ Pass |
| TC-067 | Error response format is JSON | backend-api | `test_error_format` | ✅ Pass |
| TC-068 | File size limit 413 (route-level) | backend-api | `test_file_413` | ✅ Pass |

---

## Execution Results

| Metric | Value |
|--------|-------|
| Total Test Cases | 69 |
| Passed | 69 |
| Failed | 0 |
| Skipped | 0 |
| Coverage Gaps Fixed | 2 (TC-028: sort by created, TC-053: search by author) |
| Test Runner | `uv run python -m pytest tests/test_kb_service.py -v` |
| Execution Date | 2026-03-11 |

### Gap Fixes Applied

| Gap | AC | Test Added | Description |
|-----|----|------------|-------------|
| Gap 1 | AC-049-A-04 | `test_list_files_sort_by_created` | Verifies `sort='created'` orders files by frontmatter `created` date descending |
| Gap 2 | AC-049-A-09 | `test_search_by_author` | Verifies search query matches `frontmatter.author` field |
