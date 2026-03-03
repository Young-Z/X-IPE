# Acceptance Test Cases: Link Interception & Preview Modal

> Feature ID: FEATURE-043-A
> Epic ID: EPIC-043
> Test Date: 2026-03-03
> Tester: Sage 🌿 (AI Agent via Chrome DevTools MCP)

## Test Environment

- **URL:** http://localhost:5858/
- **Browser:** Chrome (via DevTools MCP)
- **Test Page:** Ideation → 201. Playground-Draw Architecture Diagram for itself → idea-summary-v2.md
- **Reason:** Contains `.github/skills/` links with `data-preview-path` attributes

## Linked Mockup

| Mockup | Status | Path |
|--------|--------|------|
| file-link-preview-v1.html | current | x-ipe-docs/requirements/EPIC-043/FEATURE-043-A/mockups/file-link-preview-v1.html |

---

## Test Cases

### TC-001: Internal link has data-preview-path attribute (AC-043-A.1, AC-043-A.2)

| Priority | P0 |
|----------|-----|
| **Precondition** | Page with markdown containing `.github/skills/` or `x-ipe-docs/` links is loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to idea-summary-v2.md | Page loads with rendered markdown |
| 2 | Query `a[data-preview-path]` elements | At least 1 link found with `data-preview-path` attribute |
| 3 | Verify attribute value matches href | `data-preview-path` value equals `.github/skills/...` |

**Status:** ✅ Pass
**Result:** 2 links found: "Architecture DSL Skill" (.github/skills/x-ipe-tool-architecture-dsl/SKILL.md), "Architecture Draw Skill" (.github/skills/tool-architecture-draw/SKILL.md). External links (Microsoft Docs, C4Model.com) have no `data-preview-path`.

---

### TC-002: Click internal link opens preview modal (AC-043-A.1, AC-043-A.2)

| Priority | P0 |
|----------|-----|
| **Precondition** | Page with `data-preview-path` links is loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click link with `data-preview-path` | `preventDefault` fires, no page navigation |
| 2 | Observe DOM | `.link-preview-backdrop.active` element appears |
| 3 | Verify modal structure | Header with filename + close button, content area present |

**Status:** ✅ Pass
**Result:** Page stayed at `http://localhost:5858/`, backdrop.active=true, modal with title + close button + content area all present. **Bug found & fixed:** Initial test FAILED because `workplace.js` did not call `LinkPreviewManager.attachTo()` after rendering markdown — fix applied, re-test passed.

---

### TC-003: Preview modal renders markdown content (AC-043-A.3)

| Priority | P0 |
|----------|-----|
| **Precondition** | Modal opened for a .md file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click `.github/skills/x-ipe-tool-architecture-dsl/SKILL.md` link | Modal opens |
| 2 | Wait for content to load | Loading spinner disappears |
| 3 | Verify content area | Contains rendered markdown (headings, paragraphs, code blocks) |
| 4 | Verify `.markdown-body` wrapper | Content wrapped in `.markdown-body` div |

**Status:** ✅ Pass
**Result:** `.markdown-body` present, 21 headings, 3 lists rendered. Content shows full SKILL.md with "Architecture DSL Tool" heading, purpose section, etc.

---

### TC-004: Modal shows filename in header (AC-043-A.7)

| Priority | P0 |
|----------|-----|
| **Precondition** | Modal opened for SKILL.md |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read `.link-preview-title` text | Shows "SKILL.md" |
| 2 | Read `.link-preview-close` text | Shows "✕" |

**Status:** ✅ Pass
**Result:** Title = "SKILL.md", close button = "✕"

---

### TC-005: Modal closes via close button (AC-043-A.18)

| Priority | P0 |
|----------|-----|
| **Precondition** | Modal is open |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click `.link-preview-close` button | Backdrop loses `.active` class |
| 2 | Verify modal state | `_isOpen` is false |

**Status:** ✅ Pass
**Result:** `.active` removed, `_isOpen` = false

---

### TC-006: Modal closes via Escape key (AC-043-A.18)

| Priority | P0 |
|----------|-----|
| **Precondition** | Modal is open |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Press Escape key | Backdrop loses `.active` class |

**Status:** ✅ Pass
**Result:** Escape pressed, `.active` removed, `_isOpen` = false

---

### TC-007: External links NOT intercepted (AC-043-A.16)

| Priority | P0 |
|----------|-----|
| **Precondition** | Page has external links (https://...) |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Query external links | No `data-preview-path` attribute present |
| 2 | Verify Microsoft Docs link | `href` starts with `https://`, no interception attribute |

**Status:** ✅ Pass
**Result:** 2 external links: Microsoft Docs (https://docs.microsoft.com/...) and C4Model.com (https://c4model.com/) — both have `hasPreviewPath: false`

---

### TC-008: 404 error shows "File not found" (AC-043-A.10)

| Priority | P1 |
|----------|-----|
| **Precondition** | None |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Programmatically call `LinkPreviewManager.instance.open('x-ipe-docs/nonexistent-file.md')` | Modal opens |
| 2 | Wait for fetch to complete | Error state shown |
| 3 | Read `.link-preview-content` text | Contains "file not found" (case-insensitive) |
| 4 | Read `.link-preview-content` text | Contains path "x-ipe-docs/nonexistent-file.md" |

**Status:** ✅ Pass
**Result:** Error div `.link-preview-error` present, text "File not found: x-ipe-docs/nonexistent-file.md" with ⚠️ icon and error-path shown

---

### TC-009: Loading state shows spinner (AC-043-A.9)

| Priority | P1 |
|----------|-----|
| **Precondition** | None |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click internal link | Modal appears |
| 2 | Check `.link-preview-loading` presence | Loading div exists before content loads |
| 3 | Verify loading text | Contains the file path being loaded |

**Status:** ✅ Pass
**Result:** `.link-preview-loading` present with spinner-border and file path `.github/skills/x-ipe-tool-architecture-dsl/SKILL.md` displayed

---

### TC-010: Visual styling matches mockup (AC-043-A.7, AC-043-A.8)

| Priority | P1 |
|----------|-----|
| **Precondition** | Modal is open with content |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Take screenshot of modal | Modal visible with backdrop blur |
| 2 | Verify backdrop | Semi-transparent overlay, full viewport |
| 3 | Verify modal size | ~90vw × 90vh, centered, rounded corners |
| 4 | Verify header | Filename left, close button right, border-bottom |
| 5 | Verify content area | Scrollable, proper padding |

**Status:** ✅ Pass
**Result:** Backdrop: position fixed, z-index 1051, has background color. Modal: border-radius 12px, overflow hidden. Header: display flex, border-bottom 1px solid rgb(226,232,240). Content: overflow auto, padding 20px. Matches mockup design.

**Mockup Reference:** file-link-preview-v1.html (status: current)

---

### TC-011: Non-regression — existing page rendering (AC-043-A.19)

| Priority | P0 |
|----------|-----|
| **Precondition** | None |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to requirement-details-part-15.md | Page renders correctly |
| 2 | Verify headings, tables, code blocks | All render as before |
| 3 | Verify no console errors | No JS errors related to link preview |

**Status:** ✅ Pass
**Result:** EPIC-043 requirement document renders correctly with all headings, feature descriptions, acceptance criteria, code blocks. No link-preview-related JS errors. Only 404 errors from prior testing actions.

---

## Bug Found During Testing

### BUG-001: Workplace.js missing `LinkPreviewManager.attachTo()` call

| Field | Value |
|-------|-------|
| **Severity** | Critical (P0) |
| **Found in** | TC-002 (first attempt) |
| **Root Cause** | `workplace.js` renders markdown via `marked.parse()` (which adds `data-preview-path` via custom renderer) but never calls `LinkPreviewManager.attachTo()` to register click handlers |
| **Fix Applied** | Added `LinkPreviewManager.attachTo(contentBody)` after architecture diagram rendering in `workplace.js` line ~1165 |
| **Verification** | All 411 unit tests pass. TC-002 re-test passed. |

---

## Mockup Validation Summary

| Mockup | Status | Comparison Result |
|--------|--------|-------------------|
| file-link-preview-v1.html | current | ✅ **Match** |

| Aspect | Mockup | Implementation | Match |
|--------|--------|----------------|-------|
| Modal overlay (backdrop) | Dark semi-transparent | Fixed, z-1051, background color | ✅ |
| Modal container | Large centered, rounded | 90vw×90vh, border-radius 12px | ✅ |
| Header (filename + close) | Flex row, border-bottom | display flex, 1px border-bottom | ✅ |
| Content area | Scrollable, padded | overflow auto, padding 20px | ✅ |
| Loading state | Spinner + path | Bootstrap spinner + file path text | ✅ |
| Error state | Warning icon + message | ⚠️ icon + "File not found" + path | ✅ |

---

## Execution Results

| TC | Name | Priority | Status | Notes |
|----|------|----------|--------|-------|
| TC-001 | data-preview-path attribute | P0 | ✅ Pass | 2 `.github/skills/` links tagged |
| TC-002 | Click opens modal | P0 | ✅ Pass | Bug fixed in workplace.js, re-tested |
| TC-003 | Markdown rendering | P0 | ✅ Pass | 21 headings, 3 lists, markdown-body |
| TC-004 | Filename in header | P0 | ✅ Pass | "SKILL.md" + "✕" |
| TC-005 | Close via button | P0 | ✅ Pass | active removed, _isOpen=false |
| TC-006 | Close via Escape | P0 | ✅ Pass | Escape key closes modal |
| TC-007 | External links pass-through | P0 | ✅ Pass | https:// links NOT intercepted |
| TC-008 | 404 error state | P1 | ✅ Pass | Error div with file-not-found message |
| TC-009 | Loading state | P1 | ✅ Pass | Spinner + file path shown |
| TC-010 | Visual styling | P1 | ✅ Pass | Matches mockup design |
| TC-011 | Non-regression | P0 | ✅ Pass | Existing pages render correctly |

### Metrics

- **Total:** 11
- **Passed:** 11
- **Failed:** 0
- **Blocked:** 0
- **Pass Rate:** 100%
