# FEATURE-038-C: Enhanced Deliverable Viewer — Acceptance Test Results

**Tested by:** Nova (agent)
**Date:** 2026-02-20
**Method:** Chrome DevTools MCP — manual UI testing

## Test Results Summary

| # | Test Case | Result | Notes |
|---|-----------|--------|-------|
| 1 | Folder deliverable shows 📁 icon | ✅ PASS | "wf-001-test-the-workflow" renders with folder icon |
| 2 | Folder card has ▸ expand toggle | ✅ PASS | Clickable toggle arrow visible |
| 3 | Expand toggle loads folder tree | ✅ PASS | Tree fetched from `/deliverables/tree` endpoint, shows 📄 idea.md |
| 4 | Collapse toggle hides tree (▾ → ▸) | ✅ PASS | Tree items hidden, toggle reverts to ▸ |
| 5 | File click in tree triggers inline preview | ✅ PASS | Clicking idea.md shows preview with rendered markdown |
| 6 | Inline preview renders markdown | ✅ PASS | `.preview-content` contains `<p>做一个贪吃蛇</p>` (via marked.parse) |
| 7 | File deliverable renders with 💡 icon | ✅ PASS | "idea.md" deliverable shows idea icon |
| 8 | File deliverable shows path subtitle | ✅ PASS | Path "x-ipe-docs/ideas/wf-001-test-the-workflow/idea.md" displayed |
| 9 | Extensionless paths detected as folders | ✅ PASS | "wf-001-test-the-workflow" (no extension) correctly identified |

## Bugs Found & Fixed

### BUG-2: Folder deliverable rendered as regular file card
- **Root cause:** `isFolderType()` only checked `path.endsWith('/')`, but stored paths don't have trailing slashes
- **Fix:** Added extensionless path detection — if basename has no `.`, treat as folder
- **Files changed:** `deliverable-viewer.js`, `deliverable-viewer.test.js`

### BUG-3: Clicking file in folder tree did nothing
- **Root cause:** `buildTreeDOM()` is static, sets `dataset.path` on file items but no click handler
- **Fix:** Added click handler wiring in `_expandFolderTree()` — binds `.file-item[data-path]` clicks to `this.showPreview()`
- **Files changed:** `deliverable-viewer.js`

---

## CR-001: .docx / .msg File Content Preview — Acceptance Test Results

**Tested by:** Cipher 🔐 (agent)
**Date:** 2026-03-16
**Method:** pytest (backend unit + integration) + vitest (frontend unit)

### CR-001 Test Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 23 |
| Passed | 23 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | **100%** |

| Type | Passed | Failed | Blocked | Total |
|------|--------|--------|---------|-------|
| Unit (pytest) | 12 | 0 | 0 | 12 |
| Backend-API (pytest) | 7 | 0 | 0 | 7 |
| Frontend-Unit (vitest) | 4 | 0 | 0 | 4 |

### Unit Tests (pytest)

| TC | AC | Description | Priority | Status |
|----|------|-------------|----------|--------|
| TC-001 | 04a | _convert_docx returns HTML with headings/lists | P0 | ✅ PASS |
| TC-002 | 04e | _convert_docx raises on corrupted file | P0 | ✅ PASS |
| TC-003 | 04b | _convert_msg returns HTML with From/To/CC/Date/Subject/Body | P0 | ✅ PASS |
| TC-004 | 04d | _convert_msg uses htmlBody when present | P1 | ✅ PASS |
| TC-005 | 04e | _convert_msg closes msg on any outcome | P1 | ✅ PASS |
| TC-006 | 04g | _sanitize strips `<script>` tags | P0 | ✅ PASS |
| TC-007 | 04g | _sanitize strips `<iframe>` tags | P0 | ✅ PASS |
| TC-008 | 04g | _sanitize strips on* event attributes | P0 | ✅ PASS |
| TC-009 | 04g | _sanitize strips `<object>` and `<embed>` | P1 | ✅ PASS |
| TC-010 | 04g | _sanitize preserves safe HTML | P1 | ✅ PASS |
| TC-011 | — | CONVERTIBLE_EXTENSIONS contains .docx/.msg only | P2 | ✅ PASS |
| TC-012 | — | MAX_CONVERSION_SIZE == 10MB | P2 | ✅ PASS |

### Backend-API Tests (pytest)

| TC | AC | Description | Priority | Status |
|----|------|-------------|----------|--------|
| TC-013 | 04a | GET .docx → 200 + X-Converted: true + text/html | P0 | ✅ PASS |
| TC-014 | 04b | GET .msg → 200 + X-Converted: true | P0 | ✅ PASS |
| TC-015 | 04f | GET .docx >10MB → 413 "too large" | P0 | ✅ PASS |
| TC-016 | 04e | GET corrupted .docx → 415 graceful | P0 | ✅ PASS |
| TC-017 | 04h | GET .zip → 415 unchanged | P1 | ✅ PASS |
| TC-018 | — | GET .md → 200 text (regression) | P0 | ✅ PASS |
| TC-019 | 04g | GET .docx with script → sanitized output | P0 | ✅ PASS |

### Frontend-Unit Tests (vitest)

| TC | AC | Description | Priority | Status |
|----|------|-------------|----------|--------|
| TC-020 | 04a | X-Converted → sandboxed iframe (allow-same-origin) | P0 | ✅ PASS |
| TC-021 | 04f | 413 → "too large" message | P0 | ✅ PASS |
| TC-022 | 04h | 415 → "Binary file" unchanged | P1 | ✅ PASS |
| TC-023 | 04g | Converted iframe has no allow-scripts | P0 | ✅ PASS |

### Execution Commands

```bash
uv run python -m pytest tests/test_cr001_docx_msg_preview.py -v  # 19 passed, 0.40s
npm test -- tests/frontend-js/deliverable-viewer.test.js          # 50 passed (4 CR-001)
```

### Full Suite Regression

- **Frontend:** 750/750 passed (32 test files)
- **Backend (related):** 172/173 passed (1 pre-existing failure unrelated to CR-001)

---

## CR-002: Preview Header Toolbar — Acceptance Test Results

**Tested by:** Quill ✒️ (TASK-1007)
**Date:** 2026-03-27
**Method:** Vitest unit/integration tests (JSDOM)

### Test Results Summary

| # | TC ID | AC | Test Case | Type | Result |
|---|-------|----|-----------|------|--------|
| 1 | TC-001 | 06a | Header toolbar layout for text-renderable file | unit | ✅ PASS |
| 2 | TC-002 | 06b | Header hides toggle for non-text file | unit | ✅ PASS |
| 3 | TC-003 | 06c | Download link has href with download=true | unit | ✅ PASS |
| 4 | TC-004 | 06f | Smart default raw for /src/ path | unit | ✅ PASS |
| 5 | TC-005 | 06g | Smart default auto for non-src path | unit | ✅ PASS |
| 6 | TC-006 | 06j | Non-text under /src/ hides toggle | unit | ✅ PASS |
| 7 | TC-007 | 06a,b | isTextRenderable classifications (6 sub-tests) | unit | ✅ PASS |
| 8 | TC-008 | 06f,g | renderMode constructor option (2 sub-tests) | unit | ✅ PASS |
| 9 | TC-009 | 06d,e,h | setRenderMode re-renders cached content (4 sub-tests) | unit | ✅ PASS |
| 10 | TC-010 | 06i | destroy clears cache | unit | ✅ PASS |
| 11 | TC-011 | 06d | Toggle switches preview → raw (end-to-end) | integration | ✅ PASS |
| 12 | TC-012 | 06h | Toggle does not trigger new fetch | integration | ✅ PASS |
| 13 | TC-013 | 06i | File switch resets to smart default | integration | ✅ PASS |

### Metrics

| Metric | Value |
|--------|-------|
| Total ACs | 10 (AC-038-C.06a–06j) |
| Total TCs | 13 |
| Passed | 13 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | **100%** |

### AC Coverage Matrix

| AC ID | Criterion | Test Cases | Status |
|-------|-----------|-----------|--------|
| AC-038-C.06a | Header toolbar for text-renderable | TC-001, TC-007 | ✅ |
| AC-038-C.06b | Header toolbar for non-text | TC-002, TC-007 | ✅ |
| AC-038-C.06c | Download icon triggers download | TC-003 | ✅ |
| AC-038-C.06d | Toggle preview → raw | TC-009, TC-011 | ✅ |
| AC-038-C.06e | Toggle raw → preview | TC-009 | ✅ |
| AC-038-C.06f | Smart default raw for /src/ | TC-004, TC-008 | ✅ |
| AC-038-C.06g | Smart default auto for non-src | TC-005, TC-008 | ✅ |
| AC-038-C.06h | Toggle re-renders without API call | TC-009, TC-012 | ✅ |
| AC-038-C.06i | File switch resets toggle | TC-010, TC-013 | ✅ |
| AC-038-C.06j | Non-text under /src/ hides toggle | TC-006 | ✅ |

### Backend Verification

`?download=true` bypass added at [ideas_routes.py:717-718](src/x_ipe/routes/ideas_routes.py). Returns `send_file(target, as_attachment=True)` before conversion logic. Verified via code inspection.

### Execution Commands

```bash
npm test -- tests/frontend-js/file-preview-renderer-cr008.test.js  # 53 passed (15 CR-002)
npm test -- tests/frontend-js/deliverable-viewer.test.js           # 59 passed (9 CR-002)
```

### Full Suite Regression

- **Frontend:** 915/915 passed (41 test files)
- **Pre-existing:** 2 unhandled errors in kb-intake-049f.test.js (unrelated to CR-002)
