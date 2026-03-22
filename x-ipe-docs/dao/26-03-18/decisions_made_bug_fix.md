# DAO Decisions — Bug Fix

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-086 | 2026-03-18T01:57:30Z | TASK-TBD | N/A | instruction | 0.90 | Process UIUX feedback: KB article preview should render image files (.jpg etc.) inline |
| DAO-087 | 2026-03-18T13:17:04Z | TASK-TBD | N/A | instruction | 0.95 | Fix stale `kb-config.json` references → should be `knowledgebase-config.json` |

## DAO-086
- **Timestamp:** 2026-03-18T01:57:30Z
- **Task ID:** TASK-TBD
- **Feature ID:** FEATURE-049-F
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260318-095642 to get details. Feedback: "the knowledge preview should be able to see .jpg and other image files display"

### Guidance Returned
> Process this UIUX feedback as a bug fix. The KB article preview for image files (.jpg, .png, etc.) currently shows only metadata (title, author, date, size) but does not render the actual image inline. The target element is `div.kb-article-main`. Note: TASK-925 (CR-004) is already in_progress with "image/PDF/HTML preview" in its scope — verify whether image rendering was implemented. If not yet complete, treat as a bug fix to add inline image rendering for common image formats in the KB article preview.

### Rationale
> The user submitted UIUX feedback requesting image preview in KB articles. The screenshot confirms the article view shows metadata only for a .jpg file. This is a functional deficiency — a KB system should preview image files inline. TASK-925/CR-004 already lists image preview in scope, so this may be an incomplete implementation or a bug. Best handled as a bug-fix skill.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "KB article preview does not render images — functional deficiency in existing feature"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce the bug"
>       - phase: "2. Fix"
>         step: "2.1 Write failing test, then implement fix"

### Follow-up
> Check TASK-925 (CR-004) status first — if image preview code exists but isn't working, fix it. If not yet implemented, add image rendering to kb-article-main for .jpg/.png/.gif/.webp/.svg files.

## DAO-087
- **Timestamp:** 2026-03-18T13:17:04Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> kb_config.json should be knowledgebase_config.json, i believe someplace still reference wrong name

### Guidance Returned
> Fix stale references: the actual config file is `knowledgebase-config.json` (constant `KB_CONFIG_FILE` in kb_service.py:27), but ~60 references across docstrings, documentation, specifications, technical designs, and skill files still use the old name `kb-config.json`. Update all stale references to use the correct name `knowledgebase-config.json`.

### Rationale
> Clear bug fix — the code correctly uses `knowledgebase-config.json` but documentation/docstrings lag behind. Single domain, single skill, high confidence.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Stale file name references in docstrings and documentation — straightforward find-and-replace bug"
>     execution_steps:
>       - phase: "1. Diagnosis"
>         step: "1.1 Reproduce & confirm"

### Follow-up
> None

---

| DAO-ID | Timestamp | Task | Touchpoint | Disposition | Confidence | Summary |
|--------|-----------|------|------------|-------------|------------|---------|
| DAO-099 | 2026-03-18T15:49:17Z | TASK-978 | Runtime SyntaxError: await in non-async function | instruction | 0.98 | `_renderArticleScene()` in kb-browse-modal.js used `await` but wasn't declared `async`. Made method async + awaited at call site. This is exactly why Chrome DevTools UI testing would have caught this — the unit tests run in Node/jsdom which doesn't execute the actual browser script loading. |

## DAO-099 — Bug Fix: await SyntaxError in _renderArticleScene

### Context
> User reported browser error: "Uncaught SyntaxError: await is only valid in async functions and the top level bodies of modules"

### Disposition: `instruction`

> **Content:** Fix `kb-browse-modal.js`: make `_renderArticleScene` async, await it in `_showArticle()`. Root cause: CR-008 added `await this._filePreviewRenderer.renderPreview(...)` inside a sync method.
>
> **Rationale:** Clear syntax bug from CR-008 implementation. The Vitest tests didn't catch this because jsdom evaluates scripts differently from the browser. This validates the user's earlier question about using Chrome DevTools for UI testing.

---

| DAO-ID | Timestamp | Task | Touchpoint | Disposition | Confidence | Summary |
|--------|-----------|------|------------|-------------|------------|---------|
| DAO-100 | 2026-03-18T15:52:11Z | TASK-978 | "How would you avoid it later" — process improvement question | answer+instruction | 0.95 | Two concrete prevention measures: (1) always run Chrome DevTools smoke test for UI-classified ACs during acceptance testing, (2) capture lesson learned in x-ipe-meta-lesson-learned for the acceptance-test and code-implementation skills. |

---

| DAO-ID | Timestamp | Task | Touchpoint | Disposition | Confidence | Summary |
|--------|-----------|------|------------|-------------|------------|---------|
| DAO-101 | 2026-03-18T15:55:55Z | TASK-979 | DOCX shows "Cannot preview this file type" in KB browse | instruction | 0.98 | Root cause: KB `/api/kb/files/{path}/raw` serves raw binary with `send_file()` — no DOCX/MSG conversion, no X-Converted header. The ideas `/api/ideas/file` endpoint has conversion logic. Fix: add conversion for .docx/.msg in KB raw endpoint using shared `conversion_utils`. |

---
### DAO-103 — Unify remaining preview locations

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-18T16:12:00Z |
| Source | human |
| Task | TASK-979 → new TASK-980 |
| Feature | FEATURE-049-F |
| Disposition | instruction |
| Confidence | 0.95 |

**Need:** User confirms fixing all 4 remaining file preview locations (workplace.js, folder-browser-modal.js, compose-idea-modal.js, link-preview-manager.js) to use the shared FilePreviewRenderer for consistent DOCX/MSG/etc. preview support.

**Decision:** Proceed with bug fix to unify all preview locations. This is a functional consistency bug — same file type renders differently depending on where it's viewed.

**Rationale:** The shared FilePreviewRenderer (CR-008) was only integrated into 2 of 6 locations. The remaining 4 have hardcoded "cannot preview" messages for file types (DOCX, MSG) that the server can convert. All preview locations should behave identically.
