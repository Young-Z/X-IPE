# Acceptance Test Cases

> Feature: FEATURE-049-C - KB Browse & Search
> Generated: 2025-07-18
> Status: Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-049-C |
| Feature Title | KB Browse & Search |
| Total Test Cases | 31 |
| Priority | P1 (High) |
| Target URL | N/A (unit tests via Vitest + jsdom) |

---

## Prerequisites

- [x] Feature is deployed and accessible
- [x] Test environment is ready
- [x] Vitest + jsdom configured
- [x] FEATURE-049-A (KB Backend) implemented
- [x] FEATURE-049-B (KB Storage) implemented
- [x] `kb-browse.js` loaded from `src/x_ipe/static/js/features/`

---

## Test Cases

### TC-001: Renders article cards in a grid

**Acceptance Criteria Reference:** AC-049-C-01 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView class loaded
- Container element exists in DOM
- Mock API returns 3 article files

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | container | `<div id="content-area">` | DOM element |
| Input | API response | 3 MOCK_FILES | getting-started, api-reference, untagged-note |
| Expected | `.kb-card` count | 3 | One card per article |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Instantiate KBBrowseView | container | — | Instance created |
| 2 | Call render() | browseView | — | Fetch called, cards rendered |
| 3 | Query `.kb-card` | container | — | 3 elements found |

**Expected Outcome:** Grid displays one card per article returned by the API.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-002: Displays title from frontmatter

**Acceptance Criteria Reference:** AC-049-C-01 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered with MOCK_FILES
- First article has frontmatter title "Getting Started"

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | frontmatter.title | `Getting Started` | First mock file |
| Expected | `.kb-card-title` text | `Getting Started` | Exact match |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | Cards rendered |
| 2 | Query first `.kb-card-title` | container | — | Text is "Getting Started" |

**Expected Outcome:** Card title matches the frontmatter `title` field.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-003: Displays content snippet

**Acceptance Criteria Reference:** AC-049-C-01 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered with MOCK_FILES

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | content_preview | `This guide helps you get started...` | First mock file |
| Expected | `.kb-card-snippet` text | Contains "get started" | Substring match |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | Cards rendered |
| 2 | Query `.kb-card-snippet` | container | — | Contains "get started" |

**Expected Outcome:** Card displays a content snippet from article preview.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-004: Truncates snippet to 100 characters

**Acceptance Criteria Reference:** AC-049-C-01 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Mock file with content_preview of 200 characters ('A' × 200)

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | content_preview | 200-char string | Exceeds limit |
| Expected | `.kb-card-snippet` length | ≤ 100 | Truncated |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Override fetch mock | API | Single file, 200-char preview | — |
| 2 | Render browse view | container | — | Card rendered |
| 3 | Measure snippet length | `.kb-card-snippet` | — | ≤ 100 characters |

**Expected Outcome:** Snippets exceeding 100 characters are truncated.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-005: Displays last modified date on cards

**Acceptance Criteria Reference:** AC-049-C-01 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered with MOCK_FILES containing `mtime` values

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | mtime | `1700000000` | Unix timestamp |
| Expected | `.kb-card-meta` | Non-empty text | Formatted date |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | Cards rendered |
| 2 | Query `.kb-card-meta` | container | — | Non-null, non-empty text |

**Expected Outcome:** Each card shows a last-modified date.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-006: Lifecycle tags render with ▸ prefix and amber style

**Acceptance Criteria Reference:** AC-049-C-02 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Article has lifecycle tag "Requirement"

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | frontmatter.tags.lifecycle | `["Requirement"]` | First mock file |
| Expected | `.kb-tag-lifecycle` text | Contains `▸` | Prefix check |
| Expected | `.kb-tag-lifecycle` count | ≥ 1 | At least one rendered |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | Cards rendered |
| 2 | Query `.kb-tag-lifecycle` | container | — | ≥ 1 elements, text contains "▸" |

**Expected Outcome:** Lifecycle tags display with `▸` prefix and amber styling class.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-007: Domain tags render with # prefix and blue style

**Acceptance Criteria Reference:** AC-049-C-02 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Article has domain tag "Onboarding"

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | frontmatter.tags.domain | `["Onboarding"]` | First mock file |
| Expected | `.kb-tag-domain` text | Contains `#` | Prefix check |
| Expected | `.kb-tag-domain` count | ≥ 1 | At least one rendered |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | Cards rendered |
| 2 | Query `.kb-tag-domain` | container | — | ≥ 1 elements, text contains "#" |

**Expected Outcome:** Domain tags display with `#` prefix and blue styling class.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-008: Untagged articles show "Needs Tags" amber badge

**Acceptance Criteria Reference:** AC-049-C-02 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Third mock file has empty lifecycle and domain tag arrays

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | frontmatter.tags | `{ lifecycle: [], domain: [] }` | Untagged file |
| Expected | `.kb-tag-badge-untagged` text | `Needs Tags` | Exact match |
| Expected | `.kb-tag-badge-untagged` count | 1 | Only one untagged file |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | Cards rendered |
| 2 | Query `.kb-tag-badge-untagged` | container | — | 1 element, text "Needs Tags" |

**Expected Outcome:** Untagged articles display an amber "Needs Tags" badge.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-009: Renders sort dropdown

**Acceptance Criteria Reference:** AC-049-C-03 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-sort-select` | Not null | Dropdown exists |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query `.kb-sort-select` | container | — | Element exists |

**Expected Outcome:** Sort dropdown is rendered in the browse view.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-010: Sort dropdown has 4 options

**Acceptance Criteria Reference:** AC-049-C-03 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-sort-select option` count | 4 | Last Modified, Name A→Z, Date Created, Untagged First |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query `.kb-sort-select option` | container | — | 4 option elements |

**Expected Outcome:** Dropdown contains exactly 4 sort options.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-011: Sort defaults to Last Modified

**Acceptance Criteria Reference:** AC-049-C-03 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-sort-select` value | `modified_desc` | Default selection |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Check `.kb-sort-select` value | — | — | `modified_desc` |

**Expected Outcome:** Sort dropdown defaults to "Last Modified" (modified_desc).

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-012: Reloads files with new sort parameter on change

**Acceptance Criteria Reference:** AC-049-C-03 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | `.kb-sort-select` value | `name_asc` | Change event |
| Expected | fetch URL | Contains `sort=name_asc` | New sort parameter |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Record fetch call count | fetchMock | — | Baseline count |
| 3 | Set select value to `name_asc` | `.kb-sort-select` | — | — |
| 4 | Dispatch `change` event | `.kb-sort-select` | — | Fetch called with `sort=name_asc` |

**Expected Outcome:** Changing sort triggers a new API call with the updated sort parameter.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-013: Renders search input

**Acceptance Criteria Reference:** AC-049-C-04 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-search-input` | Not null | Input element exists |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query `.kb-search-input` | container | — | Element exists |

**Expected Outcome:** Search input field is rendered in the browse view.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-014: Debounces search on input (300ms)

**Acceptance Criteria Reference:** AC-049-C-04 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered
- Vitest fake timers enabled

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | `.kb-search-input` value | `test` | Search query |
| Expected | fetch calls before 300ms | No new calls | Debounce active |
| Expected | fetch calls after 350ms | ≥ 1 new call | Debounce expired |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Enable fake timers | vi | — | — |
| 3 | Set input value and dispatch `input` | `.kb-search-input` | `test` | — |
| 4 | Check fetch call count | fetchMock | — | No new calls yet |
| 5 | Advance timers by 350ms | vi | — | New fetch call made |

**Expected Outcome:** Search input is debounced at 300ms before triggering an API call.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-015: Calls /api/kb/search with correct query parameter

**Acceptance Criteria Reference:** AC-049-C-04 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered
- Vitest fake timers enabled

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | `.kb-search-input` value | `api docs` | Search query |
| Expected | fetch URL | Contains `/api/kb/search` and `q=api%20docs` | URL-encoded query |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Set input value and dispatch `input` | `.kb-search-input` | `api docs` | — |
| 3 | Advance timers past debounce | vi | 350ms | — |
| 4 | Inspect fetch calls | fetchMock | — | Call to `/api/kb/search?q=api%20docs` |

**Expected Outcome:** Search API is called with the URL-encoded query string.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-016: Renders lifecycle filter chips

**Acceptance Criteria Reference:** AC-049-C-05 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered
- Config returns 4 lifecycle tags

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | config.tags.lifecycle | `["Requirement","Feature","Technical Design","Implementation"]` | From /api/kb/config |
| Expected | `.kb-filter-lifecycle` count | 4 | One chip per tag |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query `.kb-filter-lifecycle` | container | — | 4 chip elements |

**Expected Outcome:** One lifecycle filter chip is rendered per lifecycle tag from config.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-017: Renders domain filter chips

**Acceptance Criteria Reference:** AC-049-C-05 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered
- Config returns 3 domain tags

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | config.tags.domain | `["Onboarding","Architecture","Testing"]` | From /api/kb/config |
| Expected | `.kb-filter-domain` count | 3 | One chip per tag |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query `.kb-filter-domain` | container | — | 3 chip elements |

**Expected Outcome:** One domain filter chip is rendered per domain tag from config.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-018: Toggles filter chip active class on click

**Acceptance Criteria Reference:** AC-049-C-05 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered with filter chips

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | click | `.kb-filter-lifecycle` (first) | Toggle interaction |
| Expected | classList before click | No `active` class | Initially inactive |
| Expected | classList after click | Has `active` class | Toggled on |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query first `.kb-filter-lifecycle` | container | — | No `active` class |
| 3 | Click chip | `.kb-filter-lifecycle` | — | `active` class added |

**Expected Outcome:** Clicking a filter chip toggles its active state.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-019: Renders untagged filter chip with ⚠ label

**Acceptance Criteria Reference:** AC-049-C-06 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-filter-untagged` | Not null | Chip exists |
| Expected | `.kb-filter-untagged` text | Contains "Untagged" | Label check |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query `.kb-filter-untagged` | container | — | Exists, text contains "Untagged" |

**Expected Outcome:** An untagged filter chip with ⚠ label is rendered.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-020: Filters to only untagged files when chip active

**Acceptance Criteria Reference:** AC-049-C-06 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered with mix of tagged and untagged files

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | click | `.kb-filter-untagged` | Activate filter |
| Expected | `.kb-card` count | 1 | Only the untagged article |
| Expected | card `data-path` | Contains "untagged" | Correct file filtered |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | 3 cards initially |
| 2 | Click untagged chip | `.kb-filter-untagged` | — | Filter active |
| 3 | Query `.kb-card` | container | — | 1 card, path contains "untagged" |

**Expected Outcome:** Only untagged articles are visible when untagged filter is active.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-021: Dispatches fileSelected event on card click

**Acceptance Criteria Reference:** AC-049-C-07 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered with MOCK_FILES

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | click | First `.kb-card` | Card interaction |
| Expected | `fileSelected` event detail.path | `knowledge-base/getting-started.md` | Correct path dispatched |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | MOCK_FILES | Cards rendered |
| 2 | Add `fileSelected` listener | document | — | Capture path |
| 3 | Click first `.kb-card` | card | — | Event dispatched with correct path |

**Expected Outcome:** Clicking a card dispatches a `fileSelected` custom event with the article path.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-022: Calls contentRenderer.load on card click

**Acceptance Criteria Reference:** AC-049-C-07 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered
- `window.contentRenderer` mocked with `load` spy

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | click | First `.kb-card` | Card interaction |
| Expected | `contentRenderer.load` arg | `knowledge-base/getting-started.md` | Path passed |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Mock `window.contentRenderer.load` | — | vi.fn() | Spy ready |
| 2 | Render browse view | container | MOCK_FILES | Cards rendered |
| 3 | Click first `.kb-card` | card | — | `load` called with path |

**Expected Outcome:** Card click delegates to the content rendering pipeline.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-023: Renders New Article button

**Acceptance Criteria Reference:** AC-049-C-08 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-browse-new-btn` | Not null | Button exists |
| Expected | `.kb-browse-new-btn` text | Contains "New Article" | Label check |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Query `.kb-browse-new-btn` | container | — | Exists, text "New Article" |

**Expected Outcome:** A "New Article" button is rendered in the browse view.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-024: Opens KBArticleEditor when New Article clicked

**Acceptance Criteria Reference:** AC-049-C-08 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered
- `globalThis.KBArticleEditor` mocked with `open` spy

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | click | `.kb-browse-new-btn` | Button interaction |
| Expected | KBArticleEditor.open | Called | Editor modal opened |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Mock KBArticleEditor | globalThis | Spy on open() | — |
| 2 | Render browse view | container | — | View rendered |
| 3 | Click `.kb-browse-new-btn` | button | — | `open` spy called |

**Expected Outcome:** Clicking "New Article" opens the KBArticleEditor modal.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-025: Shows "No articles yet" message when no files

**Acceptance Criteria Reference:** AC-049-C-09 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Mock API returns empty file list

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | API response | `{ files: [] }` | Empty list |
| Expected | `.kb-browse-empty` text | Contains "No articles yet" | Empty message |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Override fetch to return empty files | API | `{ files: [] }` | — |
| 2 | Render browse view | container | — | Empty state rendered |
| 3 | Query `.kb-browse-empty` | container | — | Text contains "No articles yet" |

**Expected Outcome:** Empty state message displayed when no articles exist.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-026: Shows create button in empty state

**Acceptance Criteria Reference:** AC-049-C-09 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Mock API returns empty file list

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | API response | `{ files: [] }` | Empty list |
| Expected | `.kb-browse-create-btn` | Not null | Button exists |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Override fetch to return empty files | API | `{ files: [] }` | — |
| 2 | Render browse view | container | — | Empty state rendered |
| 3 | Query `.kb-browse-create-btn` | container | — | Button exists |

**Expected Outcome:** A create button is shown in the empty state.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-027: Refreshes on kb:changed event

**Acceptance Criteria Reference:** AC-049-C-10 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | CustomEvent | `kb:changed` | Dispatched on document |
| Expected | fetch call count | Increased | Refresh triggered |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Record fetch call count | fetchMock | — | Baseline |
| 3 | Dispatch `kb:changed` | document | — | — |
| 4 | Wait 50ms | — | — | Fetch count increased |

**Expected Outcome:** Browse view refreshes automatically when `kb:changed` fires.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-028: Exports KBBrowseView class

**Acceptance Criteria Reference:** Engineering quality (non-AC)

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- `kb-browse.js` script loaded

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `globalThis.KBBrowseView` type | `function` | Class exported |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Check `globalThis.KBBrowseView` | — | — | typeof === 'function' |

**Expected Outcome:** KBBrowseView class is exported and accessible globally.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-029: Accepts container element

**Acceptance Criteria Reference:** Engineering quality (non-AC)

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Container `<div>` element exists in DOM

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | container | DOM element | Direct reference |
| Expected | browseView.container | Same reference | Stored correctly |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Instantiate KBBrowseView | container element | — | Instance created |
| 2 | Check `.container` property | browseView | — | Matches input element |

**Expected Outcome:** Constructor accepts and stores a DOM element reference.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-030: Accepts container by string ID

**Acceptance Criteria Reference:** Engineering quality (non-AC)

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Container element with `id="content-area"` exists in DOM

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | container | `"content-area"` | String ID |
| Expected | browseView.container | Resolved DOM element | Matches `#content-area` |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Instantiate KBBrowseView | `"content-area"` | — | Instance created |
| 2 | Check `.container` property | browseView | — | Matches `#content-area` element |

**Expected Outcome:** Constructor resolves a string ID to the corresponding DOM element.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-031: Stops listening to kb:changed after destroy()

**Acceptance Criteria Reference:** Engineering quality (non-AC)

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBBrowseView rendered and then destroyed

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | destroy() | browseView | Teardown call |
| Input | CustomEvent | `kb:changed` | Dispatched after destroy |
| Expected | fetch call count | Unchanged | Listener removed |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Render browse view | container | — | View rendered |
| 2 | Call destroy() | browseView | — | Cleanup done |
| 3 | Record fetch call count | fetchMock | — | Baseline |
| 4 | Dispatch `kb:changed` | document | — | — |
| 5 | Wait 50ms | — | — | Fetch count unchanged |

**Expected Outcome:** After destroy(), the view no longer responds to `kb:changed` events.

**Status:** ✅ Pass

**Execution Notes:** —

---

## Test Execution Summary

| Test Case | Title | Type | Priority | Status | Notes |
|-----------|-------|------|----------|--------|-------|
| TC-001 | Renders article cards in a grid | unit | P1 | ✅ Pass | AC-049-C-01 |
| TC-002 | Displays title from frontmatter | unit | P1 | ✅ Pass | AC-049-C-01 |
| TC-003 | Displays content snippet | unit | P1 | ✅ Pass | AC-049-C-01 |
| TC-004 | Truncates snippet to 100 characters | unit | P2 | ✅ Pass | AC-049-C-01 |
| TC-005 | Displays last modified date on cards | unit | P2 | ✅ Pass | AC-049-C-01 |
| TC-006 | Lifecycle tags render with ▸ prefix and amber style | unit | P1 | ✅ Pass | AC-049-C-02 |
| TC-007 | Domain tags render with # prefix and blue style | unit | P1 | ✅ Pass | AC-049-C-02 |
| TC-008 | Untagged articles show "Needs Tags" amber badge | unit | P1 | ✅ Pass | AC-049-C-02 |
| TC-009 | Renders sort dropdown | unit | P1 | ✅ Pass | AC-049-C-03 |
| TC-010 | Sort dropdown has 4 options | unit | P1 | ✅ Pass | AC-049-C-03 |
| TC-011 | Sort defaults to Last Modified | unit | P2 | ✅ Pass | AC-049-C-03 |
| TC-012 | Reloads files with new sort parameter on change | unit | P1 | ✅ Pass | AC-049-C-03 |
| TC-013 | Renders search input | unit | P1 | ✅ Pass | AC-049-C-04 |
| TC-014 | Debounces search on input (300ms) | unit | P1 | ✅ Pass | AC-049-C-04 |
| TC-015 | Calls /api/kb/search with correct query parameter | unit | P1 | ✅ Pass | AC-049-C-04 |
| TC-016 | Renders lifecycle filter chips | unit | P1 | ✅ Pass | AC-049-C-05 |
| TC-017 | Renders domain filter chips | unit | P1 | ✅ Pass | AC-049-C-05 |
| TC-018 | Toggles filter chip active class on click | unit | P1 | ✅ Pass | AC-049-C-05 |
| TC-019 | Renders untagged filter chip with ⚠ label | unit | P1 | ✅ Pass | AC-049-C-06 |
| TC-020 | Filters to only untagged files when chip active | unit | P1 | ✅ Pass | AC-049-C-06 |
| TC-021 | Dispatches fileSelected event on card click | unit | P1 | ✅ Pass | AC-049-C-07 |
| TC-022 | Calls contentRenderer.load on card click | unit | P1 | ✅ Pass | AC-049-C-07 |
| TC-023 | Renders New Article button | unit | P1 | ✅ Pass | AC-049-C-08 |
| TC-024 | Opens KBArticleEditor when New Article clicked | unit | P1 | ✅ Pass | AC-049-C-08 |
| TC-025 | Shows "No articles yet" message when no files | unit | P1 | ✅ Pass | AC-049-C-09 |
| TC-026 | Shows create button in empty state | unit | P2 | ✅ Pass | AC-049-C-09 |
| TC-027 | Refreshes on kb:changed event | unit | P1 | ✅ Pass | AC-049-C-10 |
| TC-028 | Exports KBBrowseView class | unit | P0 | ✅ Pass | Lifecycle |
| TC-029 | Accepts container element | unit | P0 | ✅ Pass | Lifecycle |
| TC-030 | Accepts container by string ID | unit | P2 | ✅ Pass | Lifecycle |
| TC-031 | Stops listening to kb:changed after destroy() | unit | P1 | ✅ Pass | Lifecycle |

---

## Execution Results

**Execution Date:** 2026-03-11 (re-run after spec/design/code changes)
**Executed By:** Echo 📡
**Environment:** dev

| Metric | Value |
|--------|-------|
| Total Tests | 31 |
| Passed | 31 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Test Type | Passed | Total | Tool |
|-----------|--------|-------|------|
| Unit | 31 | 31 | vitest |

**Test Runner:** `npx vitest run tests/frontend-js/kb-browse.test.js`
