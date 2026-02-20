# Feature Specification: Enhanced Deliverable Viewer

> Feature ID: FEATURE-038-C
> Version: v1.0
> Status: Refined
> Last Updated: 02-20-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-20-2026 | Initial specification — folder-type deliverables with file-tree and inline preview |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Refine Idea Modal | HTML | [refine-idea-modal-v1.html](../mockups/refine-idea-modal-v1.html) | Scene 4: deliverable viewer with file-tree and inline preview | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".

## Overview

This feature extends the deliverables section (FEATURE-036-E) to support **folder-type deliverables**. Currently, each deliverable card shows a single file with icon, name, and path. When an action produces a folder of output files (e.g., `refined-idea/`), there is no way to browse or preview the contents.

This CR adds:
1. **Folder detection** — deliverable paths ending with `/` are treated as folder-type
2. **File-tree rendering** — folder deliverables expand into a nested file listing with folder/file icons
3. **Inline preview** — clicking a file opens a preview pane below the tree: markdown rendered via `marked.js`, text/code shown as monospace preformatted text

This is a **CR on FEATURE-036-E** (Deliverables, Polling & Lifecycle).

**Target Users:**
- Workflow users who want to browse multi-file action outputs without leaving the workflow view

## User Stories

- **US-038-C.1:** As a workflow user, I want to see the contents of a folder deliverable as a file tree, so that I can understand what files the action produced.
- **US-038-C.2:** As a workflow user, I want to click a file in the tree to preview its content inline, so that I can quickly review outputs without opening external tools.

## Acceptance Criteria

### Folder Detection

- [ ] AC-038-C.1: Deliverable paths ending with `/` are identified as folder-type
- [ ] AC-038-C.2: Non-folder deliverables continue to render as existing card layout (no regression)

### File-Tree Rendering

- [ ] AC-038-C.3: Folder deliverable cards expand to show a nested file-tree listing
- [ ] AC-038-C.4: Tree shows folder icons (📁) for directories and file icons (📄) for files
- [ ] AC-038-C.5: Nested directories are collapsible/expandable (click folder to toggle)
- [ ] AC-038-C.6: Tree loads lazily — folder contents fetched on first expand
- [ ] AC-038-C.7: Visual layout MUST match mockup Scene 4 for tree structure

### Inline Preview

- [ ] AC-038-C.8: Clicking a file in the tree opens an inline preview pane below the tree
- [ ] AC-038-C.9: Markdown files (`.md`) are rendered as HTML via `marked.parse()`
- [ ] AC-038-C.10: Text/code files are shown as monospace preformatted text
- [ ] AC-038-C.11: Preview pane shows file name as header
- [ ] AC-038-C.12: Only one preview pane open at a time — clicking another file replaces it

### Security & Performance

- [ ] AC-038-C.13: File-tree and preview are scoped to the deliverable's base folder — no path traversal outside
- [ ] AC-038-C.14: File-tree handles up to 50 files per folder without performance degradation
- [ ] AC-038-C.15: Binary files are not previewed — show "Binary file" message

## Functional Requirements

**FR-038-C.1: Folder Detection in Deliverable Rendering**
- Input: Deliverable item from `/api/workflow/{name}/deliverables` response
- Process: Check if `item.path` ends with `/`. If yes, render as folder-type card with expand button.
- Output: Folder card with expand toggle, or standard file card

**FR-038-C.2: Folder Contents API**
- Input: Folder path relative to project root
- Process: Use existing `GET /api/ideas/folder-contents?path={folder_path}` or extend deliverables endpoint to support folder listing
- Output: JSON array of `{name, type: 'file'|'dir', path}` entries

**FR-038-C.3: File-Tree DOM Construction**
- Input: Folder contents array
- Process: Build nested `<ul>` structure with `<li>` for each entry. Directories get collapse/expand toggle. Files get click handler for preview.
- Output: DOM subtree appended below deliverable card

**FR-038-C.4: Inline Preview Loading**
- Input: File path from tree item click
- Process: Call `GET /api/ideas/file?path={file_path}`. If response is text, render: markdown → `marked.parse()`, other text → `<pre>`. If 415 (binary), show message.
- Output: Preview pane with rendered content

**FR-038-C.5: Path Scoping Validation**
- Input: Requested file/folder path
- Process: Validate that resolved path is a descendant of the deliverable's base folder. Reject path traversal attempts (`../`).
- Output: Valid path proceeds; invalid path shows error

## Non-Functional Requirements

- **NFR-038-C.1:** File-tree render must complete within 500ms for folders with up to 50 files
- **NFR-038-C.2:** File preview fetch and render must complete within 1s for files up to 100KB
- **NFR-038-C.3:** No additional JS libraries — uses native DOM + existing `marked.js`

## UI/UX Requirements

### Components (from mockup Scene 4)

| Component | Description | Behavior |
|-----------|-------------|----------|
| Folder Card | Deliverable card with expand toggle (▸/▾) | Click header to expand/collapse tree |
| File-Tree | Nested `<ul>` with folder/file icons | Directories collapsible, files clickable |
| Preview Pane | Below tree, shows file content | Markdown rendered, text as preformatted |
| Preview Header | File name above content | Shows active file name |

### User Flow

```
1. User sees deliverable card for folder-type output (e.g., "refined-idea/")
2. User clicks expand toggle on the card
3. File-tree loads and shows folder contents
4. User clicks a .md file in the tree
5. Preview pane appears below tree with rendered markdown
6. User clicks a different file — preview updates
7. User clicks collapse toggle — tree and preview collapse
```

## Dependencies

### Internal

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-036-E | CR target | Deliverables, Polling & Lifecycle — base card grid being extended |
| `GET /api/ideas/file` | Data source | File content retrieval for preview |
| `GET /api/ideas/folder-contents` | Data source | Folder listing for tree |
| `marked.js` | Rendering | Already loaded globally for markdown rendering |

### External

None.

## Business Rules

- **BR-038-C.1:** Folder detection is based solely on trailing `/` in the path — no filesystem stat.
- **BR-038-C.2:** File-tree only shows the immediate folder and its descendants — no parent navigation.
- **BR-038-C.3:** Preview supports only text-based files. Binary files show a placeholder message.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty folder deliverable | Tree shows "No files" message |
| Folder with >50 files | Show first 50 with "N more files..." truncation message |
| Nested folders 3+ levels deep | Tree renders all levels (no depth limit) |
| File with no extension | Preview as plain text |
| Large file (>100KB) | Show first 100KB with "File truncated" message |
| Folder path doesn't exist on disk | Card shows "⚠️ folder not found" (same as existing missing file pattern) |
| Path traversal attempt (`../../etc/passwd`) | Rejected by path scoping validation, shows error |

## Out of Scope

- **File editing** — preview is read-only
- **File download** — no download button
- **Image/binary preview** — text-based only
- **File search within tree** — browse only
- **Syntax highlighting** — plain preformatted text for code files

## Technical Considerations

- Extend `_renderDeliverables()` in `workflow-stage.js` to detect folder-type and call new `_renderFolderDeliverable()` method
- File-tree CSS: simple nested `<ul>` with `padding-left` indentation, `cursor: pointer` on items
- Preview pane: `<div class="deliverable-preview">` with content area, positioned below tree
- Reuse `GET /api/ideas/folder-contents` for tree data — may need to pass full relative path (not just ideas folder)
- `marked.js` already loaded globally — no additional setup needed

## Open Questions

None.
