# Feature Specification: KB Browse & Search

> Feature ID: FEATURE-049-C  
> Version: v2.0  
> Status: Refined  
> Last Updated: 03-11-2026

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 03-11-2026 | Initial specification |
| v2.0 | 03-11-2026 | Template alignment — added GWT acceptance criteria, overview, UI/UX requirements, dependencies, business rules, edge cases & constraints, out of scope, technical considerations |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| KB Interface v1 — Browse Articles (Scene 1) | Interactive HTML | [x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html](x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html) | Grid card layout for browsing KB articles with search, sort, and tag filtering | Current | 03-11-2026 |

## Overview

The KB Browse & Search feature provides a grid-based card view for browsing Knowledge Base articles within X-IPE. Users can view articles organized by folder, with each card displaying the title, a content snippet, tags, and the last modified date. This view serves as the primary entry point for discovering and accessing KB content.

Beyond browsing, the feature supports search with debounced input, sorting by multiple criteria (last modified, alphabetical, date created, untagged first), and two-dimensional tag filtering using clickable chip controls. Lifecycle and domain tags are visually differentiated with distinct color schemes. An empty state guides new users toward creating their first article.

This feature targets developers and knowledge workers using X-IPE who need efficient access to project knowledge. It integrates with the KB sidebar navigation (FEATURE-049-B) for folder selection and delegates article rendering to the existing content pipeline.

## User Stories

- As a developer using X-IPE, I want to browse KB articles in a grid view with search, sort, and tag filtering so that I can quickly find relevant knowledge.
- As a knowledge author, I want to see which articles are untagged so that I can maintain consistent categorization across the knowledge base.
- As a new team member, I want a clear empty state when no articles exist so that I know how to get started creating content.

## Acceptance Criteria

### AC-049-C-01: Grid Layout

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-01a | GIVEN KB browse view is opened WHEN articles exist in the current folder THEN articles render as card-based grid layout in the KB content area | UI |
| AC-049-C-01b | GIVEN KB browse view displays article cards WHEN an article has content THEN each card displays title, snippet (first 100 chars), tags, and last modified date | UI |

### AC-049-C-02: Tag Rendering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-02a | GIVEN an article card is rendered WHEN the article has lifecycle tags THEN lifecycle tags render as amber gradient pill with `▸` prefix | UI |
| AC-049-C-02b | GIVEN an article card is rendered WHEN the article has domain tags THEN domain tags render as blue outlined pill with `#` prefix | UI |

### AC-049-C-03: Sort Controls

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-03a | GIVEN KB browse view is opened WHEN the view renders THEN a sort dropdown is available in the KB browse toolbar | UI |
| AC-049-C-03b | GIVEN user clicks the sort dropdown WHEN options are displayed THEN sort options include Last Modified (default), Name A→Z, Date Created, AND Untagged First | UI |

### AC-049-C-04: Search Filtering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-04a | GIVEN user is in KB browse view WHEN user types in the search bar THEN results are filtered by filename and frontmatter fields (title, tags, author) | UI |
| AC-049-C-04b | GIVEN user is typing in the search bar WHEN keystrokes occur THEN search input is debounced at 300ms before triggering the filter | Unit |

### AC-049-C-05: Tag Filter Chips

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-05a | GIVEN KB browse view is opened WHEN tag configuration is loaded THEN 2D tag filter chips appear below the search bar | UI |
| AC-049-C-05b | GIVEN tag filter chips are displayed WHEN user clicks a chip THEN the filter is toggled AND the active chip is highlighted | UI |

### AC-049-C-06: Untagged Filter

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-06a | GIVEN tag filter chips are displayed WHEN user clicks the "⚠ Untagged" chip THEN only files without tags are shown | UI |
| AC-049-C-06b | GIVEN the untagged filter is active WHEN untagged articles are displayed THEN each untagged card displays a "Needs Tags" amber badge | UI |

### AC-049-C-07: Article Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-07a | GIVEN KB browse view displays article cards WHEN user clicks an article card THEN the file opens in the content area via existing rendering pipeline | UI |

### AC-049-C-08: New Article Action

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-08a | GIVEN KB browse view is opened WHEN the view renders THEN a "New Article" button is visible in the browse toolbar | UI |
| AC-049-C-08b | GIVEN "New Article" button is visible WHEN user clicks the button THEN the KB Article Editor modal (FEATURE-049-D) opens | UI |

### AC-049-C-09: Empty State

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-09a | GIVEN KB browse view is opened WHEN no articles exist in the current folder THEN a "No articles yet — create one!" message is displayed | UI |
| AC-049-C-09b | GIVEN the empty state message is displayed WHEN user views the empty state THEN a button to open the KB Article Editor is included | UI |

### AC-049-C-10: Live Refresh

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-C-10a | GIVEN KB browse view is active WHEN a `kb:changed` event fires THEN the browse view refreshes automatically | Unit |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB)

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

## UI/UX Requirements

| ID | Requirement |
|----|-------------|
| UX-049-C-01 | Card grid uses responsive layout: 1 column on mobile, 2 on tablet, 3–4 on desktop |
| UX-049-C-02 | Cards have consistent height with content truncation for long snippets |
| UX-049-C-03 | Lifecycle tags use amber gradient pill styling; domain tags use blue outlined pill styling |
| UX-049-C-04 | Search bar is prominently positioned at the top of the browse view |
| UX-049-C-05 | Sort dropdown uses standard select styling consistent with X-IPE design tokens |
| UX-049-C-06 | Tag filter chips use toggle behavior with visual active state |
| UX-049-C-07 | Empty state uses centered layout with instructional messaging |
| UX-049-C-08 | "Needs Tags" badge uses amber color to indicate actionable items |

## Dependencies

### Internal Dependencies

| Feature | Dependency Type | Description |
|---------|----------------|-------------|
| FEATURE-049-A | Required | KB Backend & Storage Foundation — provides `/api/kb/files`, `/api/kb/search`, `/api/kb/config` endpoints |
| FEATURE-049-B | Required | KB Sidebar Navigation — provides folder selection that triggers browse view rendering |
| FEATURE-049-D | Optional | KB Article Editor — "New Article" button opens the editor modal |

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| None | — | No new external dependencies required |

## Business Rules

| ID | Rule |
|----|------|
| BR-049-C-01 | Default sort order is "Last Modified" (most recent first) |
| BR-049-C-02 | Search is case-insensitive and matches against filename, title, tags, and author fields |
| BR-049-C-03 | Tag filters are additive — selecting multiple tags shows articles matching ANY selected tag |
| BR-049-C-04 | The "⚠ Untagged" filter is exclusive — when active, only untagged articles are shown regardless of other filters |
| BR-049-C-05 | Card snippet displays the first 100 characters of the article body content |
| BR-049-C-06 | Browse view scope is limited to the currently selected folder in the sidebar |

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Folder with no articles | Display empty state with "No articles yet — create one!" message and editor button |
| Article with no frontmatter | Card displays filename as title, empty snippet, no tags |
| Article with very long title | Title is truncated with ellipsis on the card |
| Search with no matching results | Display "No results found" message with option to clear search |
| API error on file list fetch | Display error toast and retry option |
| Folder with 100+ articles | Paginate or virtualize card rendering for performance |
| Tag config endpoint unavailable | Hide tag filter chips; search and sort remain functional |

## Out of Scope

- Full-text content search (only filename and frontmatter fields are searchable)
- Drag-and-drop article reordering
- Article bulk operations (multi-select, bulk delete, bulk tag)
- Folder creation from the browse view (handled by FEATURE-049-B)
- Article version history or diff view
- Inline article editing from the browse view (editing uses FEATURE-049-D modal)

## Technical Considerations

- Browse view must integrate with the existing content rendering pipeline for article navigation
- Search debounce (300ms) must prevent excessive API calls during rapid typing
- Card grid must be responsive across viewport sizes (1–4 columns)
- The `kb:changed` event listener must be properly cleaned up when the browse view is unmounted
- Tag configuration is fetched once on view load and cached for filter chip rendering

## Open Questions

- None at this time.
