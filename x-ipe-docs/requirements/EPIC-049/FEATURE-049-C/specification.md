# FEATURE-049-C: KB Browse & Search — Specification

## Feature Overview

| Field | Value |
|-------|-------|
| Feature ID | FEATURE-049-C |
| Epic | EPIC-049 (Knowledge Base) |
| Version | v1.0 |
| Status | Refined |
| Dependencies | FEATURE-049-A, FEATURE-049-B |

## User Story

As a developer using X-IPE, I want to browse KB articles in a grid view with search, sort, and tag filtering so that I can quickly find relevant knowledge.

## Acceptance Criteria

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-C-01a | Articles render as card-based grid layout in the KB content area | UI |
| AC-049-C-01b | Each card displays title, snippet (first 100 chars), tags, and last modified date | UI |
| AC-049-C-02a | Lifecycle tags render as amber gradient pill with `▸` prefix | UI |
| AC-049-C-02b | Domain tags render as blue outlined pill with `#` prefix | UI |
| AC-049-C-03a | Sort dropdown is available in the KB browse view | UI |
| AC-049-C-03b | Sort options include: Last Modified (default), Name A→Z, Date Created, Untagged First | UI |
| AC-049-C-04a | Search bar filters results by filename and frontmatter fields (title, tags, author) | UI |
| AC-049-C-04b | Search input is debounced at 300ms | Unit |
| AC-049-C-05a | 2D tag filter chips appear below the search bar | UI |
| AC-049-C-05b | Clicking a chip toggles the filter; active chip is highlighted | UI |
| AC-049-C-06a | Clicking "⚠ Untagged" chip shows only files without tags | UI |
| AC-049-C-06b | Untagged cards display a "Needs Tags" amber badge | UI |
| AC-049-C-07a | Clicking an article card opens the file in the content area via existing rendering pipeline | UI |
| AC-049-C-08a | "New Article" button is visible in the browse view | UI |
| AC-049-C-08b | Clicking the button opens the KB Article Editor modal (FEATURE-049-D) | UI |
| AC-049-C-09a | When no articles exist in current folder, shows "No articles yet — create one!" message | UI |
| AC-049-C-09b | Empty state includes a button to open the editor | UI |
| AC-049-C-10a | Browse view refreshes automatically when a `kb:changed` event fires | Unit |

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-049-C-01 | `KBBrowseView` class in `src/x_ipe/static/js/features/kb-browse.js` |
| FR-049-C-02 | Renders into main content area when KB sidebar section/folder is clicked |
| FR-049-C-03 | Fetches file list from `GET /api/kb/files?folder=&sort=` |
| FR-049-C-04 | Fetches tag config from `GET /api/kb/config` for filter chips |
| FR-049-C-05 | Search calls `GET /api/kb/search?q=&tag=&tag_type=` with 300ms debounce |
| FR-049-C-06 | Card click delegates to `window.contentRenderer.load(path)` or sidebar `onFileSelect` |
| FR-049-C-07 | "New Article" opens `KBArticleEditor` from FEATURE-049-D |
| FR-049-C-08 | CSS in `src/x_ipe/static/css/kb-browse.css` |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-049-C-01 | Search results render within 300ms |
| NFR-049-C-02 | Grid layout responsive (1-4 columns based on viewport) |
| NFR-049-C-03 | No new external dependencies |
