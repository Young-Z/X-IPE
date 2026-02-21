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
