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

### AC-049-C-01: Grid View
**Given** the KB content area is displayed  
**When** articles exist in the current folder  
**Then** articles show as card-based grid: title, snippet (first 100 chars), tags, last modified date

### AC-049-C-02: Tag Display
**Given** an article card with tags  
**When** the card renders  
**Then** lifecycle tags show as amber gradient pill with `▸` prefix; domain tags show as blue outlined pill with `#` prefix

### AC-049-C-03: Sort Dropdown
**Given** the KB browse view  
**When** the user opens the sort dropdown  
**Then** options include: Last Modified (default), Name A→Z, Date Created, Untagged First

### AC-049-C-04: Keyword Search
**Given** the search bar  
**When** the user types a query  
**Then** results filter by filename + frontmatter fields (title, tags, author), debounced 300ms

### AC-049-C-05: Tag Filter Chips
**Given** the browse view  
**When** rendered  
**Then** 2D tag filter chips appear below search bar; clicking toggles filter; active chip highlighted

### AC-049-C-06: Untagged Filter
**Given** the tag filter area  
**When** "⚠ Untagged" chip clicked  
**Then** only files without tags are shown; untagged cards show "Needs Tags" amber badge

### AC-049-C-07: Card Click Navigation
**Given** an article card  
**When** the user clicks it  
**Then** the file opens in the content area via the existing content rendering pipeline

### AC-049-C-08: New Article Button
**Given** the browse view  
**When** rendered  
**Then** a "New Article" button is available that opens the KB Article Editor modal (FEATURE-049-D)

### AC-049-C-09: Empty State
**Given** no articles in current folder  
**When** the browse view renders  
**Then** shows "No articles yet — create one!" with a button to open the editor

### AC-049-C-10: kb:changed Refresh
**Given** the browse view is displayed  
**When** a `kb:changed` event fires  
**Then** the browse view refreshes automatically

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
