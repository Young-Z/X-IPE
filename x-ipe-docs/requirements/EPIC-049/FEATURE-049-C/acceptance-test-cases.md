# FEATURE-049-C: KB Browse & Search — Acceptance Test Cases

## Overview

| Field | Value |
|-------|-------|
| Feature ID | FEATURE-049-C |
| Test File | `tests/frontend-js/kb-browse.test.js` |
| Total Tests | 31 |
| Framework | Vitest + jsdom |
| Status | ✅ All Passing |

## Test Coverage Matrix

### AC-049-C-01: Grid View

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 1 | Renders article cards in a grid | unit | vitest | ✅ Pass |
| 2 | Displays title from frontmatter | unit | vitest | ✅ Pass |
| 3 | Displays content snippet | unit | vitest | ✅ Pass |
| 4 | Truncates snippet to 100 characters | unit | vitest | ✅ Pass |
| 5 | Displays last modified date on cards | unit | vitest | ✅ Pass |

### AC-049-C-02: Tag Display

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 6 | Lifecycle tags render with `▸` prefix and amber style | unit | vitest | ✅ Pass |
| 7 | Domain tags render with `#` prefix and blue style | unit | vitest | ✅ Pass |
| 8 | Untagged articles show "Needs Tags" amber badge | unit | vitest | ✅ Pass |

### AC-049-C-03: Sort Dropdown

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 9 | Renders sort dropdown | unit | vitest | ✅ Pass |
| 10 | Has 4 sort options (Last Modified, Name A→Z, Date Created, Untagged First) | unit | vitest | ✅ Pass |
| 11 | Defaults to Last Modified | unit | vitest | ✅ Pass |
| 12 | Reloads files with new sort parameter on change | unit | vitest | ✅ Pass |

### AC-049-C-04: Keyword Search

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 13 | Renders search input | unit | vitest | ✅ Pass |
| 14 | Debounces search on input (300ms) | unit | vitest | ✅ Pass |
| 15 | Calls /api/kb/search with correct query parameter | unit | vitest | ✅ Pass |

### AC-049-C-05: Tag Filter Chips

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 16 | Renders lifecycle filter chips | unit | vitest | ✅ Pass |
| 17 | Renders domain filter chips | unit | vitest | ✅ Pass |
| 18 | Toggles filter chip active class on click | unit | vitest | ✅ Pass |

### AC-049-C-06: Untagged Filter

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 19 | Renders untagged filter chip with ⚠ label | unit | vitest | ✅ Pass |
| 20 | Filters to only untagged files when chip active | unit | vitest | ✅ Pass |

### AC-049-C-07: Card Click Navigation

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 21 | Dispatches fileSelected event on card click | unit | vitest | ✅ Pass |
| 22 | Calls contentRenderer.load(path) on card click | unit | vitest | ✅ Pass |

### AC-049-C-08: New Article Button

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 23 | Renders New Article button | unit | vitest | ✅ Pass |
| 24 | Opens KBArticleEditor when clicked | unit | vitest | ✅ Pass |

### AC-049-C-09: Empty State

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 25 | Shows "No articles yet" message when no files | unit | vitest | ✅ Pass |
| 26 | Shows create button in empty state | unit | vitest | ✅ Pass |

### AC-049-C-10: kb:changed Refresh

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 27 | Refreshes on kb:changed event (fetch called) | unit | vitest | ✅ Pass |

### Lifecycle (Non-AC — Engineering Quality)

| # | Test Case | Test Type | Assigned Tool | Status |
|---|-----------|-----------|---------------|--------|
| 28 | Exports KBBrowseView class | unit | vitest | ✅ Pass |
| 29 | Accepts container element | unit | vitest | ✅ Pass |
| 30 | Accepts container by string ID | unit | vitest | ✅ Pass |
| 31 | Stops listening to kb:changed after destroy() | unit | vitest | ✅ Pass |

## Metrics

| Metric | Value |
|--------|-------|
| Acceptance Criteria Covered | 10/10 (100%) |
| Total Test Cases | 31 |
| Tests Added This Session | 7 |
| Test Type | unit |
| Assigned Tool | vitest |
| Pass Rate | 31/31 (100%) |
| Execution Time | ~260ms |
