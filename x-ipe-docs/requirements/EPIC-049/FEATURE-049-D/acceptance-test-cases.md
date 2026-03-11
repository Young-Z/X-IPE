# Acceptance Test Cases

> Feature: FEATURE-049-D - KB Article Editor
> Generated: 2025-07-18
> Status: Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-049-D |
| Feature Title | KB Article Editor |
| Total Test Cases | 34 |
| Priority | P1 (High) |
| Target URL | N/A (unit tests via Vitest + jsdom) |

---

## Prerequisites

- [x] Feature is deployed and accessible
- [x] Test environment is ready
- [x] Vitest + jsdom configured
- [x] FEATURE-049-A (KB Backend) implemented
- [x] EasyMDE library available (mocked in tests)
- [x] `kb-article-editor.js` loaded from `src/x_ipe/static/js/features/`

---

## Test Cases

### TC-001: Exports KBArticleEditor class

**Acceptance Criteria Reference:** Engineering quality (non-AC)

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- `kb-article-editor.js` script loaded

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `globalThis.KBArticleEditor` | Defined | Class exported |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Check `globalThis.KBArticleEditor` | — | — | Defined |

**Expected Outcome:** KBArticleEditor class is exported and accessible globally.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-002: Accepts options in constructor

**Acceptance Criteria Reference:** Engineering quality (non-AC)

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBArticleEditor class available

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | options | `{ folder: 'test', editPath: null }` | Create mode |
| Expected | instance | Defined | Constructor works |
| Expected | editMode | `false` | No editPath → create mode |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Instantiate KBArticleEditor | — | `{ folder: 'test', editPath: null }` | Instance created |
| 2 | Check `editMode` | instance | — | `false` |

**Expected Outcome:** Constructor accepts options and defaults to create mode.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-003: Sets editMode when editPath provided

**Acceptance Criteria Reference:** Engineering quality (non-AC)

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBArticleEditor class available

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | options | `{ editPath: 'docs/guide.md' }` | Edit mode |
| Expected | editMode | `true` | editPath present → edit mode |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Instantiate KBArticleEditor | — | `{ editPath: 'docs/guide.md' }` | Instance created |
| 2 | Check `editMode` | instance | — | `true` |

**Expected Outcome:** Providing editPath sets the editor to edit mode.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-004: Creates overlay with kb-editor-overlay class

**Acceptance Criteria Reference:** AC-049-D-02 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBArticleEditor instantiated in create mode

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-editor-overlay` | Not null | Overlay element created |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Instantiate editor | — | `{ folder: 'test' }` | — |
| 2 | Call `open()` | editor | — | Overlay rendered |
| 3 | Query `.kb-editor-overlay` | document | — | Element exists |

**Expected Outcome:** Opening the editor creates a modal overlay element.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-005: Adds active class on open

**Acceptance Criteria Reference:** AC-049-D-02 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBArticleEditor instantiated

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-editor-overlay` classList | Contains `active` | Animation trigger |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | — |
| 2 | Wait 50ms | — | — | Animation frame fires |
| 3 | Check overlay classList | `.kb-editor-overlay` | — | Has `active` class |

**Expected Outcome:** Overlay receives `active` class after opening for animation.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-006: Header shows "📝 New Article" in create mode

**Acceptance Criteria Reference:** AC-049-D-02 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened in create mode (no editPath)

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | options | `{ folder: 'test' }` | Create mode |
| Expected | `.kb-editor-header h3` text | Contains "New Article" | Header label |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor in create mode | editor | `{ folder: 'test' }` | — |
| 2 | Query header | `.kb-editor-header h3` | — | Text contains "New Article" |

**Expected Outcome:** Create mode shows "New Article" in the modal header.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-007: Header shows "✏️ Edit Article" in edit mode

**Acceptance Criteria Reference:** AC-049-D-02 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened in edit mode (editPath provided)

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | options | `{ editPath: 'docs/guide.md' }` | Edit mode |
| Expected | `.kb-editor-header h3` text | Contains "Edit Article" | Header label |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor in edit mode | editor | `{ editPath: 'docs/guide.md' }` | — |
| 2 | Query header | `.kb-editor-header h3` | — | Text contains "Edit Article" |

**Expected Outcome:** Edit mode shows "Edit Article" in the modal header.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-008: Renders title input

**Acceptance Criteria Reference:** AC-049-D-04 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-editor-title` | Not null | Input element exists |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | `{ folder: 'test' }` | — |
| 2 | Query `.kb-editor-title` | document | — | Element exists |

**Expected Outcome:** Title input field is rendered in the form area.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-009: Renders lifecycle tag chips from config

**Acceptance Criteria Reference:** AC-049-D-04 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Config returns 3 lifecycle tags: Ideation, Design, Implementation

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | config.tags.lifecycle | `["Ideation","Design","Implementation"]` | From /api/kb/config |
| Expected | `.kb-chip-lifecycle` count | 3 | One chip per tag |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | Config fetched |
| 2 | Query `.kb-chip-lifecycle` | document | — | 3 chip elements |

**Expected Outcome:** Lifecycle tag chips are rendered from the config API response.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-010: Renders domain tag chips from config

**Acceptance Criteria Reference:** AC-049-D-04 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Config returns 3 domain tags: API, UI-UX, Security

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | config.tags.domain | `["API","UI-UX","Security"]` | From /api/kb/config |
| Expected | `.kb-chip-domain` count | 3 | One chip per tag |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | Config fetched |
| 2 | Query `.kb-chip-domain` | document | — | 3 chip elements |

**Expected Outcome:** Domain tag chips are rendered from the config API response.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-011: Toggles chip active state on click

**Acceptance Criteria Reference:** AC-049-D-04 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened with tag chips rendered

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | click × 2 | `.kb-chip-lifecycle` (first) | Toggle on then off |
| Expected | classList after 1st click | Has `active` | Toggled on |
| Expected | classList after 2nd click | No `active` | Toggled off |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | Chips rendered |
| 2 | Check initial state | `.kb-chip-lifecycle` | — | No `active` class |
| 3 | Click chip | `.kb-chip-lifecycle` | — | `active` class added |
| 4 | Click chip again | `.kb-chip-lifecycle` | — | `active` class removed |

**Expected Outcome:** Tag chip toggles active state on each click.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-012: Initializes EasyMDE instance on open

**Acceptance Criteria Reference:** AC-049-D-03 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- EasyMDE constructor mocked on globalThis
- Editor opened

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `editor.easyMDE` | Not null | Instance created |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | `{ folder: 'test' }` | — |
| 2 | Wait 50ms | — | — | EasyMDE initialization |
| 3 | Check `editor.easyMDE` | — | — | Not null |

**Expected Outcome:** EasyMDE editor instance is initialized when the modal opens.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-013: Cleans up EasyMDE on close (NFR-049-D-04)

**Acceptance Criteria Reference:** AC-049-D-03 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened with EasyMDE initialized

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `editor.easyMDE` after close | `null` | Memory leak prevention |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | EasyMDE initialized |
| 2 | Verify `editor.easyMDE` not null | — | — | Confirmed |
| 3 | Call `close(true)` | editor | — | — |
| 4 | Check `editor.easyMDE` | — | — | `null` |

**Expected Outcome:** EasyMDE instance is cleaned up on modal close to prevent memory leaks.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-014: Save button disabled when title empty

**Acceptance Criteria Reference:** AC-049-D-06 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened, title input empty

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | (empty) | Default state |
| Expected | `.kb-editor-btn-save` disabled | `true` | Cannot save without title |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | `{ folder: 'test' }` | — |
| 2 | Query save button | `.kb-editor-btn-save` | — | `disabled === true` |

**Expected Outcome:** Save button is disabled when title field is empty.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-015: Save button enabled when title provided

**Acceptance Criteria Reference:** AC-049-D-06 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | `.kb-editor-title` value | `My Article` | Non-empty title |
| Expected | `.kb-editor-btn-save` disabled | `false` | Save allowed |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | — |
| 2 | Set title value | `.kb-editor-title` | `My Article` | — |
| 3 | Dispatch `input` event | `.kb-editor-title` | — | — |
| 4 | Query save button | `.kb-editor-btn-save` | — | `disabled === false` |

**Expected Outcome:** Save button becomes enabled when a title is entered.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-016: Calls POST /api/kb/files for new articles

**Acceptance Criteria Reference:** AC-049-D-06 from specification.md

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened in create mode
- Title filled in
- Fetch mocked

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `My Article` | Required field |
| Expected | fetch URL | `/api/kb/files` | Create endpoint |
| Expected | fetch method | `POST` | Create verb |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor in create mode | editor | `{ folder: 'test' }` | — |
| 2 | Set title | `.kb-editor-title` | `My Article` | — |
| 3 | Call `_save()` | editor | — | — |
| 4 | Inspect fetch calls | mockFetch | — | POST to `/api/kb/files` |

**Expected Outcome:** Saving a new article calls POST /api/kb/files with the correct payload.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-017: Dispatches kb:changed on successful save

**Acceptance Criteria Reference:** AC-049-D-09 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Title filled
- Save mock returns success

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Test` | Required |
| Expected | `kb:changed` event | Dispatched | Event spy called |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Add event listener | document `kb:changed` | vi.fn() spy | — |
| 2 | Open editor, set title | editor | `Test` | — |
| 3 | Call `_save()` | editor | — | — |
| 4 | Check event spy | — | — | Called once |

**Expected Outcome:** A `kb:changed` custom event is dispatched after successful save.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-018: Builds valid YAML frontmatter

**Acceptance Criteria Reference:** AC-049-D-05 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Title set and tags selected

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Test Article` | — |
| Input | selectedTags.lifecycle | `Set(["Design"])` | — |
| Input | selectedTags.domain | `Set(["API"])` | — |
| Expected | frontmatter | Contains `title:`, `author:`, `auto_generated:`, tags | Valid YAML |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor, set title | editor | `Test Article` | — |
| 2 | Add tags to selectedTags | editor | Design, API | — |
| 3 | Call `_buildFrontmatter()` | editor | — | YAML string |
| 4 | Verify contents | — | — | Contains title, author, auto_generated, tags, starts/ends with `---` |

**Expected Outcome:** Frontmatter builder produces valid YAML with all required fields.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-019: Auto-populates created date with today

**Acceptance Criteria Reference:** AC-049-D-05 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Date Test` | — |
| Expected | frontmatter `created` | Today's ISO date | Auto-populated |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor, set title | editor | `Date Test` | — |
| 2 | Call `_buildFrontmatter()` | editor | — | YAML string |
| 3 | Check `created` field | — | — | Matches today's date (YYYY-MM-DD) |

**Expected Outcome:** The `created` field is auto-populated with today's ISO date.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-020: Omits tags section when no tags selected

**Acceptance Criteria Reference:** AC-049-D-05 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened, no tags selected

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `No Tags` | — |
| Input | selectedTags | Empty sets | No selections |
| Expected | frontmatter | Does NOT contain `tags:` | Omitted |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor, set title | editor | `No Tags` | — |
| 2 | Call `_buildFrontmatter()` | editor | — | YAML string |
| 3 | Check for `tags:` | — | — | Not present |

**Expected Outcome:** Tags section is omitted from frontmatter when no tags are selected.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-021: Sanitizes title for filename

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBArticleEditor instantiated

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `My Test Article!` | Special chars |
| Expected | filename | `my-test-article` | Sanitized |
| Input | title | `Hello   World` | Multiple spaces |
| Expected | filename | `hello-world` | Collapsed |
| Input | title | `API & Auth Guide` | Ampersand |
| Expected | filename | `api-auth-guide` | Stripped |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Call `_sanitizeFilename('My Test Article!')` | editor | — | `my-test-article` |
| 2 | Call `_sanitizeFilename('Hello   World')` | editor | — | `hello-world` |
| 3 | Call `_sanitizeFilename('API & Auth Guide')` | editor | — | `api-auth-guide` |

**Expected Outcome:** Filenames are lowercased, special chars removed, spaces replaced with hyphens.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-022: Parses frontmatter from YAML content

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBArticleEditor instantiated

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | content | `---\ntitle: "My Guide"\nauthor: user\ntags:\n  lifecycle:\n    - Design\n  domain:\n    - API\n---\n# Hello` | Full frontmatter |
| Expected | frontmatter.title | `"My Guide"` | Parsed |
| Expected | frontmatter.tags.lifecycle | `["Design"]` | Parsed |
| Expected | body | `# Hello` | After frontmatter |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Call `_parseFrontmatter(content)` | editor | YAML content | `{ frontmatter, body }` |
| 2 | Check frontmatter fields | — | — | title, tags parsed correctly |
| 3 | Check body | — | — | `# Hello` |

**Expected Outcome:** YAML frontmatter is parsed into structured object with body separated.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-023: Handles content without frontmatter

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- KBArticleEditor instantiated

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | content | `# Just content` | No YAML block |
| Expected | frontmatter | `{}` | Empty object |
| Expected | body | `# Just content` | Full content as body |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Call `_parseFrontmatter('# Just content')` | editor | — | `{ frontmatter: {}, body }` |
| 2 | Check frontmatter | — | — | Empty object |
| 3 | Check body | — | — | `# Just content` |

**Expected Outcome:** Content without frontmatter returns empty frontmatter and full body.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-024: Removes overlay on force close

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `.kb-editor-overlay` after close | `null` | Removed from DOM |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | Overlay created |
| 2 | Call `close(true)` | editor | — | Force close |
| 3 | Wait 350ms | — | — | Animation completes |
| 4 | Query `.kb-editor-overlay` | document | — | `null` |

**Expected Outcome:** Overlay element is removed from DOM after close animation.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-025: Restores body scroll on close

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened (body overflow set to hidden)

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | `document.body.style.overflow` on open | `hidden` | Scroll locked |
| Expected | `document.body.style.overflow` after close | `''` | Scroll restored |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | — |
| 2 | Check body overflow | `document.body.style.overflow` | — | `hidden` |
| 3 | Call `close(true)` | editor | — | — |
| 4 | Check body overflow | `document.body.style.overflow` | — | `''` (empty) |

**Expected Outcome:** Body scroll is restored when the modal closes.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-026: Loads existing article and pre-populates title

**Acceptance Criteria Reference:** AC-049-D-07 from specification.md

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened in edit mode
- API returns existing article content with title "My Guide"

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | editPath | `docs/guide.md` | Existing file |
| Input | API content | YAML with `title: My Guide` | Pre-existing |
| Expected | `.kb-editor-title` value | `My Guide` | Pre-populated |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Mock fetch for config + article content | API | Guide article | — |
| 2 | Open editor in edit mode | editor | `{ editPath: 'docs/guide.md' }` | — |
| 3 | Wait 100ms | — | — | Async load completes |
| 4 | Check title input | `.kb-editor-title` | — | value === `My Guide` |

**Expected Outcome:** Title input is pre-populated from existing article frontmatter.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-027: Pre-populates tags from existing frontmatter

**Acceptance Criteria Reference:** AC-049-D-07 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened in edit mode
- Existing article has lifecycle tag "Design" and domain tag "API"

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | existing tags | `lifecycle: ["Design"], domain: ["API"]` | From frontmatter |
| Expected | `selectedTags.lifecycle` | Contains `Design` | Set membership |
| Expected | `selectedTags.domain` | Contains `API` | Set membership |
| Expected | Design chip | Has `active` class | Visual state |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Mock fetch with tagged article | API | Design + API tags | — |
| 2 | Open editor in edit mode | editor | `{ editPath: 'docs/guide.md' }` | — |
| 3 | Wait 100ms | — | — | Async load completes |
| 4 | Check selectedTags | editor | — | Design in lifecycle, API in domain |
| 5 | Check chip active class | `.kb-chip-lifecycle[data-tag="Design"]` | — | Has `active` |

**Expected Outcome:** Tags from existing article are pre-selected in chip UI.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-028: Calls PUT /api/kb/files/{path} for edit mode

**Acceptance Criteria Reference:** AC-049-D-07 from specification.md

**Priority:** P0

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened in edit mode
- Title filled

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | editPath | `docs/guide.md` | Edit target |
| Input | title | `Updated Title` | Modified |
| Expected | fetch URL | Contains `/api/kb/files/` | Edit endpoint |
| Expected | fetch method | `PUT` | Update verb |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor in edit mode | editor | `{ editPath: 'docs/guide.md' }` | — |
| 2 | Set title | `.kb-editor-title` | `Updated Title` | — |
| 3 | Call `_save()` | editor | — | — |
| 4 | Inspect fetch calls | mockFetch | — | PUT to `/api/kb/files/{path}` |

**Expected Outcome:** Saving in edit mode calls PUT with the file path.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-029: Prompts confirmation when dirty, user declines → stays open

**Acceptance Criteria Reference:** AC-049-D-08 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Title modified (dirty state)

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Unsaved` | Makes editor dirty |
| Input | confirm() return | `false` | User declines |
| Expected | confirm | Called | Dialog shown |
| Expected | `.kb-editor-overlay` | Still exists | Modal stays open |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | — |
| 2 | Set title (make dirty) | `.kb-editor-title` | `Unsaved` | dirty === true |
| 3 | Mock `confirm` → false | globalThis | — | — |
| 4 | Call `close()` | editor | — | — |
| 5 | Check confirm was called | — | — | Called |
| 6 | Check overlay exists | `.kb-editor-overlay` | — | Still in DOM |

**Expected Outcome:** Declining the discard confirmation keeps the modal open.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-030: Closes when user confirms discard

**Acceptance Criteria Reference:** AC-049-D-08 from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened and dirty

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Unsaved` | Makes editor dirty |
| Input | confirm() return | `true` | User confirms |
| Expected | `.kb-editor-overlay` after 350ms | `null` | Modal closed |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor, make dirty | editor | `Unsaved` | dirty === true |
| 2 | Mock `confirm` → true | globalThis | — | — |
| 3 | Call `close()` | editor | — | — |
| 4 | Wait 350ms | — | — | Animation completes |
| 5 | Check overlay | `.kb-editor-overlay` | — | `null` |

**Expected Outcome:** Confirming discard closes the modal and removes the overlay.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-031: Closes without confirmation when not dirty

**Acceptance Criteria Reference:** AC-049-D-08 from specification.md

**Priority:** P2

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened, no changes made

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Expected | dirty | `false` | No modifications |
| Expected | confirm | NOT called | No prompt needed |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Open editor | editor | — | dirty === false |
| 2 | Mock `confirm` | globalThis | vi.fn() | — |
| 3 | Call `close()` | editor | — | — |
| 4 | Check confirm | — | — | NOT called |

**Expected Outcome:** Clean editor closes without a confirmation prompt.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-032: Shows error toast on API save failure

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Fetch mocked to return `{ ok: false, error: 'File already exists' }`

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Duplicate` | — |
| Input | API response | `{ ok: false, error: 'File already exists' }` | Conflict |
| Expected | `.kb-editor-toast` text | `File already exists` | Error message |
| Expected | `.kb-editor-toast` class | `kb-toast-error` | Error style |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Mock fetch → failure | API | Error response | — |
| 2 | Open editor, set title | editor | `Duplicate` | — |
| 3 | Call `_save()` | editor | — | — |
| 4 | Check toast | `.kb-editor-toast` | — | Text + error class |

**Expected Outcome:** API errors display an error toast with the server message.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-033: Re-enables save button on error

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Save fails

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Error Test` | — |
| Input | API response | `{ ok: false, error: 'Conflict' }` | Save fails |
| Expected | `.kb-editor-btn-save` disabled | `false` | Re-enabled after error |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Mock fetch → failure | API | Conflict | — |
| 2 | Open editor, set title | editor | `Error Test` | — |
| 3 | Call `_save()` | editor | — | — |
| 4 | Check save button | `.kb-editor-btn-save` | — | `disabled === false` |

**Expected Outcome:** Save button is re-enabled after a save error to allow retry.

**Status:** ✅ Pass

**Execution Notes:** —

---

### TC-034: Handles network error gracefully

**Acceptance Criteria Reference:** Edge case from specification.md

**Priority:** P1

**Test Type:** unit

**Assigned Tool:** vitest

**Preconditions:**
- Editor opened
- Fetch rejects with network error

**Test Data:**
> Data Source: Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | title | `Net Error` | — |
| Input | fetch | Rejects with `Error('Network error')` | Network failure |
| Expected | `.kb-editor-toast` text | Contains "Network error" | Error displayed |

**Test Steps:**

| Step | Action | Element/Target | Input Data | Expected Result |
|------|--------|----------------|------------|-----------------|
| 1 | Mock fetch → reject | API | `new Error('Network error')` | — |
| 2 | Open editor, set title | editor | `Net Error` | — |
| 3 | Call `_save()` | editor | — | — |
| 4 | Check toast | `.kb-editor-toast` | — | Contains "Network error" |

**Expected Outcome:** Network errors are caught and displayed in a toast message.

**Status:** ✅ Pass

**Execution Notes:** —

---

## Test Execution Summary

| Test Case | Title | Type | Priority | Status | Notes |
|-----------|-------|------|----------|--------|-------|
| TC-001 | Exports KBArticleEditor class | unit | P0 | ✅ Pass | Lifecycle |
| TC-002 | Accepts options in constructor | unit | P0 | ✅ Pass | Lifecycle |
| TC-003 | Sets editMode when editPath provided | unit | P0 | ✅ Pass | Lifecycle |
| TC-004 | Creates overlay with kb-editor-overlay class | unit | P1 | ✅ Pass | AC-049-D-02 |
| TC-005 | Adds active class on open | unit | P1 | ✅ Pass | AC-049-D-02 |
| TC-006 | Header shows "New Article" in create mode | unit | P1 | ✅ Pass | AC-049-D-02 |
| TC-007 | Header shows "Edit Article" in edit mode | unit | P1 | ✅ Pass | AC-049-D-02 |
| TC-008 | Renders title input | unit | P1 | ✅ Pass | AC-049-D-04 |
| TC-009 | Renders lifecycle tag chips from config | unit | P1 | ✅ Pass | AC-049-D-04 |
| TC-010 | Renders domain tag chips from config | unit | P1 | ✅ Pass | AC-049-D-04 |
| TC-011 | Toggles chip active state on click | unit | P1 | ✅ Pass | AC-049-D-04 |
| TC-012 | Initializes EasyMDE instance on open | unit | P1 | ✅ Pass | AC-049-D-03 |
| TC-013 | Cleans up EasyMDE on close (NFR-049-D-04) | unit | P1 | ✅ Pass | AC-049-D-03 |
| TC-014 | Save button disabled when title empty | unit | P1 | ✅ Pass | AC-049-D-06 |
| TC-015 | Save button enabled when title provided | unit | P1 | ✅ Pass | AC-049-D-06 |
| TC-016 | Calls POST /api/kb/files for new articles | unit | P0 | ✅ Pass | AC-049-D-06 |
| TC-017 | Dispatches kb:changed on successful save | unit | P1 | ✅ Pass | AC-049-D-09 |
| TC-018 | Builds valid YAML frontmatter | unit | P1 | ✅ Pass | AC-049-D-05 |
| TC-019 | Auto-populates created date with today | unit | P1 | ✅ Pass | AC-049-D-05 |
| TC-020 | Omits tags section when no tags selected | unit | P2 | ✅ Pass | AC-049-D-05 |
| TC-021 | Sanitizes title for filename | unit | P2 | ✅ Pass | Edge case |
| TC-022 | Parses frontmatter from YAML content | unit | P1 | ✅ Pass | Edge case |
| TC-023 | Handles content without frontmatter | unit | P2 | ✅ Pass | Edge case |
| TC-024 | Removes overlay on force close | unit | P1 | ✅ Pass | Edge case |
| TC-025 | Restores body scroll on close | unit | P1 | ✅ Pass | Edge case |
| TC-026 | Loads existing article and pre-populates title | unit | P0 | ✅ Pass | AC-049-D-07 |
| TC-027 | Pre-populates tags from existing frontmatter | unit | P1 | ✅ Pass | AC-049-D-07 |
| TC-028 | Calls PUT /api/kb/files/{path} for edit mode | unit | P0 | ✅ Pass | AC-049-D-07 |
| TC-029 | Prompts confirmation when dirty, user declines | unit | P1 | ✅ Pass | AC-049-D-08 |
| TC-030 | Closes when user confirms discard | unit | P1 | ✅ Pass | AC-049-D-08 |
| TC-031 | Closes without confirmation when not dirty | unit | P2 | ✅ Pass | AC-049-D-08 |
| TC-032 | Shows error toast on API save failure | unit | P1 | ✅ Pass | Edge case |
| TC-033 | Re-enables save button on error | unit | P1 | ✅ Pass | Edge case |
| TC-034 | Handles network error gracefully | unit | P1 | ✅ Pass | Edge case |

---

## Execution Results

**Execution Date:** 2026-03-11 (re-run after spec/design/code changes)
**Executed By:** Echo 📡
**Environment:** dev

| Metric | Value |
|--------|-------|
| Total Tests | 34 |
| Passed | 34 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Test Type | Passed | Total | Tool |
|-----------|--------|-------|------|
| Unit | 34 | 34 | vitest |

**Test Runner:** `npx vitest run tests/frontend-js/kb-article-editor.test.js`
