## EPIC-043: File Link Preview

> **Idea Ref:** IDEA-033 (x-ipe-docs/ideas/wf-001-feature-file-link-preview/refined-idea/idea-summary-v1.md)
> **Created:** 2026-03-03
> **Priority:** P0 (MVP) → P1 (complete) → P2 (follow-up)

### Project Overview

Enhance X-IPE's handling of internal file links in rendered markdown. When markdown references project resources via `x-ipe-docs/` or `.github/skills/` paths, clicking those links opens an in-app preview modal instead of navigating away. Also standardize all internal link paths to full project-root-relative format, update the 12 skills that generate markdown, and retrofit existing files.

### User Request

From user feedback (Feedback-20260303-212659): links in rendered markdown (idea summaries, specifications, skill docs) either navigate away from the app or 404. Need in-app preview with breadcrumb back-navigation, consistent path formatting across all generated files, and visual distinction for preview-capable links.

### Clarifications

| Question | Answer |
|----------|--------|
| Scope of Epic? | All 4 parts in one Epic — features broken down later |
| Backend endpoint? | `/api/file/content` already exists with path traversal protection — no new endpoint needed |
| Migration approach? | Use x-ipe-task-based-change-request skill per-file/per-folder — requirement defines convention and scope, CRs handle execution |
| Which paths trigger preview? | Links starting with `x-ipe-docs/` or `.github/skills/` |
| Where does preview work? | Everywhere markdown is rendered (knowledge base, idea summaries, workflow deliverables, skill docs) |
| Modal behavior? | Reuse existing DeliverableViewer modal |
| Nested link navigation? | Breadcrumb-style within same modal, capped at 5 levels |
| Error handling? | Inline error message in modal ("File not found: path/to/file.md") |
| Visual link distinction? | 📄 icon prefix + "Open preview" hover tooltip + dashed green underline |
| Abort behavior? | AbortController cancels pending request when user clicks new link |

### Target Users

- **Developers** using X-IPE who need to cross-reference specs, designs, and idea summaries
- **AI Agents** that generate markdown output with internal cross-references
- **Project Managers** reviewing documentation chains (idea → requirements → design → implementation)

### High-Level Requirements

#### Part 1: Link Path Standard

1. **HR-043.1:** All markdown links referencing project resources MUST use full project-root-relative paths starting with `x-ipe-docs/` or `.github/skills/`
2. **HR-043.2:** No relative paths (`../`, `./`) or partial paths in generated markdown — only full root-relative paths

| Before (inconsistent) | After (standardized) |
|---|---|
| `[spec](../FEATURE-001/specification.md)` | `[spec](x-ipe-docs/requirements/EPIC-001/FEATURE-001/specification.md)` |
| `[design](./technical-design.md)` | `[design](x-ipe-docs/requirements/EPIC-001/FEATURE-001/technical-design.md)` |
| `[skill](SKILL.md)` | `[skill](.github/skills/x-ipe-task-based-bug-fix/SKILL.md)` |

#### Part 2: Frontend Link Preview

3. **HR-043.3:** Clicking a link whose `href` starts with `x-ipe-docs/` or `.github/skills/` in any rendered markdown MUST open a preview modal instead of navigating away
4. **HR-043.4:** The preview modal MUST reuse the existing DeliverableViewer component
5. **HR-043.5:** The preview modal MUST render markdown, HTML, and code files using ContentRenderer
6. **HR-043.6:** Clicking a link inside the preview modal MUST replace the modal content and add a breadcrumb entry (not open a new modal)
7. **HR-043.7:** Breadcrumb navigation MUST show the full path chain and support "← Back" to previous file
8. **HR-043.8:** Breadcrumb depth MUST be capped at 5 levels
9. **HR-043.9:** Internal links in rendered markdown MUST be visually distinct: 📄 icon prefix, "Open preview" tooltip on hover, dashed underline styling
10. **HR-043.10:** If the linked file is not found, the modal MUST show an inline error message: "File not found: {path}"
11. **HR-043.11:** If a new link is clicked while a file is loading, the pending request MUST be aborted (AbortController) and the new file loaded
12. **HR-043.12:** Supported preview file types: markdown (.md), HTML (.html/.htm), plain text, code files. Binary files show "Cannot preview binary file" message
13. **HR-043.13:** Link interception MUST use event delegation on `.markdown-body` containers for performance and dynamic content support
14. **HR-043.14:** External links (not starting with `x-ipe-docs/` or `.github/skills/`) MUST continue to behave normally (open in browser)

#### Part 3: Skill Updates

15. **HR-043.15:** All 12 markdown-generating skills MUST include a constraint in their execution procedure: "All internal links MUST use full project-root-relative paths"
16. **HR-043.16:** The following 12 skills require CR updates:
    - `x-ipe-task-based-ideation-v2`
    - `x-ipe-task-based-feature-refinement`
    - `x-ipe-task-based-technical-design`
    - `x-ipe-task-based-requirement-gathering`
    - `x-ipe-task-based-feature-breakdown`
    - `x-ipe-task-based-change-request`
    - `x-ipe-task-based-idea-to-architecture`
    - `x-ipe-task-based-feature-acceptance-test`
    - `x-ipe-task-based-refactoring-analysis`
    - `x-ipe-task-based-improve-code-quality`
    - `x-ipe-task-based-code-implementation`
    - `x-ipe-task-based-user-manual`
17. **HR-043.17:** The `x-ipe-meta-skill-creator` skill template MUST be updated to include the path convention for all future skills

#### Part 4: Existing File Migration

18. **HR-043.18:** All existing markdown files in `x-ipe-docs/` and `.github/skills/` with relative or partial internal paths MUST be migrated to full project-root-relative format
19. **HR-043.19:** Migration MUST NOT rewrite paths inside fenced code blocks (` ``` `) or inline code (`` ` ``)
20. **HR-043.20:** If a relative path cannot be unambiguously resolved (target file doesn't exist), it MUST be flagged for manual review, not auto-rewritten
21. **HR-043.21:** Migration is executed via `x-ipe-task-based-change-request` skill per-file or per-folder — not a batch script

### Functional Requirements

#### FR-043.1: Link Interception

- **FR-043.1.1:** Add a custom link renderer to marked.js in ContentRenderer that adds `data-preview-path` attribute to links whose `href` starts with `x-ipe-docs/` or `.github/skills/`
- **FR-043.1.2:** Add delegated click handler on `.markdown-body` containers that intercepts clicks on `[data-preview-path]` links
- **FR-043.1.3:** On interception, call `preventDefault()` and fetch file content via `GET /api/file/content?path={path}`
- **FR-043.1.4:** Display fetched content in DeliverableViewer modal

#### FR-043.2: Preview Modal Enhancement

- **FR-043.2.1:** Add breadcrumb bar to DeliverableViewer showing navigation path
- **FR-043.2.2:** Maintain a navigation stack (max 5 entries) of `{path, title}` objects
- **FR-043.2.3:** "← Back" button pops the stack and loads the previous file
- **FR-043.2.4:** Clicking a breadcrumb entry navigates directly to that level (truncates stack)
- **FR-043.2.5:** When stack reaches depth 5, show a warning tooltip on the next link: "Maximum preview depth reached"

#### FR-043.3: Visual Link Distinction

- **FR-043.3.1:** Internal links rendered with `📄` emoji prefix (inserted via CSS `::before` or during markdown rendering)
- **FR-043.3.2:** Internal links show `title="Open preview"` tooltip on hover
- **FR-043.3.3:** Internal links styled with dashed underline and accent color (Emerald 500 per brand theme)
- **FR-043.3.4:** External links remain unchanged (blue, solid underline, no icon)

#### FR-043.4: Error & Loading States

- **FR-043.4.1:** While file is loading, show spinner with "Loading {path}..." text in modal
- **FR-043.4.2:** On 404 response, show inline error: "File not found: {path}" with hint text
- **FR-043.4.3:** On network error, show inline error: "Failed to load file" with retry button
- **FR-043.4.4:** AbortController instance per modal — abort previous request on new link click

#### FR-043.5: Skill Path Convention Constraint

- **FR-043.5.1:** Each of the 12 skills' `<constraints>` sections gets: "All internal links MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`)"
- **FR-043.5.2:** `x-ipe-meta-skill-creator` template gets the same constraint in its output template

#### FR-043.6: File Migration Convention

- **FR-043.6.1:** Migration target: all `.md` files under `x-ipe-docs/` and `.github/skills/` directories
- **FR-043.6.2:** Migration rule: replace `../path`, `./path`, and bare `path` references with full root-relative `x-ipe-docs/...` or `.github/skills/...` paths
- **FR-043.6.3:** Skip paths inside code blocks (fenced or inline)
- **FR-043.6.4:** Flag unresolvable paths for manual review
- **FR-043.6.5:** Each file or folder migrated as a separate CR task

### Non-Functional Requirements

- **NFR-043.1:** File content fetched on-demand — no preloading
- **NFR-043.2:** Event delegation for link interception — single handler per `.markdown-body` container
- **NFR-043.3:** AbortController cancels pending requests — prevents race conditions
- **NFR-043.4:** No regression in existing ContentRenderer, DeliverableViewer, or FolderBrowserModal functionality
- **NFR-043.5:** Progressive enhancement — links work as standard `<a>` tags if JS fails

### Constraints

- Two interception prefixes only: `x-ipe-docs/` and `.github/skills/` — other project paths (`src/`, `tests/`) behave as normal links
- Reuse existing components (DeliverableViewer, ContentRenderer) — no new rendering engine
- Backend `/api/file/content` already exists — only serve files under project root (path traversal protection in place)
- Backward compatibility during transition: frontend should attempt relative path resolution against current file's location until migration completes

### Dependencies

- **Component dependencies:** ContentRenderer (FEATURE-002-A), DeliverableViewer (FEATURE-038-C), FolderBrowserModal (FEATURE-039)
- **API dependency:** `/api/file/content` endpoint (already exists, verified)
- **Skill dependencies:** 12 skills listed in HR-043.16 (CRs applied separately)

### Acceptance Criteria Summary

| ID | Criterion | Priority |
|----|-----------|----------|
| AC-043.1 | Clicking `x-ipe-docs/` link in rendered markdown opens preview modal | P0 |
| AC-043.2 | Clicking `.github/skills/` link in rendered markdown opens preview modal | P0 |
| AC-043.3 | Preview modal renders markdown files correctly | P0 |
| AC-043.4 | File-not-found shows inline error in modal | P0 |
| AC-043.5 | No regression in ContentRenderer/DeliverableViewer/FolderBrowserModal | P0 |
| AC-043.6 | Clicking link inside preview adds breadcrumb and replaces content | P1 |
| AC-043.7 | ← Back button returns to previous file | P1 |
| AC-043.8 | Internal links show 📄 icon and "Open preview" tooltip | P1 |
| AC-043.9 | All 12 skills updated with path convention constraint | P1 |
| AC-043.10 | Existing markdown files migrated to root-relative paths | P2 |
| AC-043.11 | Skill creation template enforces path convention | P2 |

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| File Link Preview — Full Interactive (5 scenarios) | [file-link-preview-v1.html](EPIC-043/mockups/file-link-preview-v1.html) |

### Related Features

- **FEATURE-002-A (Content Viewer):** EPIC-043 extends ContentRenderer with custom link renderer — additive, no conflict
- **FEATURE-038-C (Enhanced Deliverable Viewer):** EPIC-043 reuses DeliverableViewer as-is — component dependency
- **FEATURE-039-A/B (Folder Browser Modal):** Similar UI pattern but different entry point (link click vs folder browse) — no conflict
- **FEATURE-040/041/042 (Skill Output):** Part 3 skill updates are CRs on these skills — planned dependency

### Open Questions

- None — all clarifications resolved during ideation and requirement gathering
