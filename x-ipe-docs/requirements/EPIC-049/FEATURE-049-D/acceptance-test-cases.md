# FEATURE-049-D: KB Article Editor — Acceptance Test Cases

| Field | Value |
|-------|-------|
| Feature | FEATURE-049-D (KB Article Editor) |
| Test File | `tests/frontend-js/kb-article-editor.test.js` |
| Total Tests | 34 |
| Status | ✅ All passing |

## Test Coverage Matrix

| AC | Description | test_type | assigned_tool | Tests | Status |
|----|-------------|-----------|---------------|-------|--------|
| AC-049-D-01 | New Article Button (sidebar trigger) | integration | manual / Playwright | — | Out of scope (sidebar integration) |
| AC-049-D-02 | Modal Shell | unit | vitest | 4 | ✅ Covered |
| AC-049-D-03 | EasyMDE Editor | unit | vitest | 2 | ✅ Covered |
| AC-049-D-04 | Frontmatter Form | unit | vitest | 4 | ✅ Covered |
| AC-049-D-05 | Auto-Populated Fields | unit | vitest | 3 | ✅ Covered |
| AC-049-D-06 | Save Creates File | unit | vitest | 3 | ✅ Covered |
| AC-049-D-07 | Edit Existing Article | unit | vitest | 3 | ✅ Covered |
| AC-049-D-08 | Cancel with Confirmation | unit | vitest | 3 | ✅ Covered |
| AC-049-D-09 | kb:changed Event | unit | vitest | 1 | ✅ Covered |
| Edge Cases | Save errors, filename, parsing | unit | vitest | 8 | ✅ Covered |
| NFR-049-D-04 | EasyMDE cleanup on close | unit | vitest | 1 | ✅ Covered |

## Detailed Test Cases

### AC-049-D-02: Modal Shell
| # | Test Case | Metric |
|---|-----------|--------|
| 1 | Creates overlay with `kb-editor-overlay` class | DOM element exists |
| 2 | Adds `active` class on open | classList check |
| 3 | Header shows "📝 New Article" in create mode | textContent match |
| 4 | Header shows "✏️ Edit Article" in edit mode | textContent match |

### AC-049-D-03: EasyMDE Editor
| # | Test Case | Metric |
|---|-----------|--------|
| 5 | Initializes EasyMDE instance on open | `editor.easyMDE !== null` |
| 6 | Cleans up EasyMDE on close (NFR-049-D-04) | `editor.easyMDE === null` |

### AC-049-D-04: Frontmatter Form
| # | Test Case | Metric |
|---|-----------|--------|
| 7 | Renders title input `.kb-editor-title` | DOM element exists |
| 8 | Renders lifecycle tag chips from config | chip count === config.lifecycle.length |
| 9 | Renders domain tag chips from config | chip count === config.domain.length |
| 10 | Toggles chip active state on click | classList toggle |

### AC-049-D-05: Auto-Populated Fields
| # | Test Case | Metric |
|---|-----------|--------|
| 11 | Builds YAML frontmatter with title, author, auto_generated | string contains expected fields |
| 12 | Auto-populates `created` with today's date | ISO date match |
| 13 | Omits tags section when no tags selected | string does not contain `tags:` |

### AC-049-D-06: Save Creates File
| # | Test Case | Metric |
|---|-----------|--------|
| 14 | Save button disabled when title empty | `saveBtn.disabled === true` |
| 15 | Save button enabled when title provided | `saveBtn.disabled === false` |
| 16 | Calls `POST /api/kb/files` for new articles | fetch mock call verification |

### AC-049-D-07: Edit Existing Article
| # | Test Case | Metric |
|---|-----------|--------|
| 17 | Loads existing article and pre-populates title | `titleInput.value` match |
| 18 | Pre-populates tags from existing frontmatter | `selectedTags` Set membership + chip active class |
| 19 | Calls `PUT /api/kb/files/{path}` for edit mode | fetch mock call verification |

### AC-049-D-08: Cancel with Confirmation
| # | Test Case | Metric |
|---|-----------|--------|
| 20 | Prompts confirmation when dirty, user declines → stays open | `confirm` called, overlay exists |
| 21 | Closes when user confirms discard | overlay removed after animation |
| 22 | Closes without confirmation when not dirty | `confirm` not called |

### AC-049-D-09: kb:changed Event
| # | Test Case | Metric |
|---|-----------|--------|
| 23 | Dispatches `kb:changed` on successful save | event spy called |

### Edge Cases
| # | Test Case | Metric |
|---|-----------|--------|
| 24 | Sanitizes title for filename (special chars, spaces) | string equality |
| 25 | Parses frontmatter from YAML content | object field verification |
| 26 | Handles content without frontmatter | empty object + original body |
| 27 | Shows error toast on API save failure | toast textContent + class |
| 28 | Re-enables save button on error | `saveBtn.disabled === false` |
| 29 | Handles network error gracefully | toast contains error message |
| 30 | Removes overlay on force close | DOM element null |
| 31 | Restores body scroll on close | `overflow === ''` |

### Class Export (Baseline)
| # | Test Case | Metric |
|---|-----------|--------|
| 32 | Exports `KBArticleEditor` class | `globalThis.KBArticleEditor` defined |
| 33 | Accepts options in constructor | instance defined, `editMode === false` |
| 34 | Sets `editMode` when `editPath` provided | `editMode === true` |

## Refactoring Summary

**Pre-refactor quality: 6.5/10 → Post-refactor: 7.5/10**

| Change | Rationale |
|--------|-----------|
| Extracted `CLOSE_ANIMATION_MS`, `TOAST_DURATION_MS`, `MAX_FILENAME_LENGTH` as static constants | Eliminates magic numbers |
| Extracted `_buildContent()` method | Separates content assembly from save flow |
| Extracted `_postArticle()` / `_putArticle()` methods | Single-responsibility for API calls |
| Extracted `_resetSaveButton()` helper | Eliminates duplicated error-recovery logic in `_save` |
