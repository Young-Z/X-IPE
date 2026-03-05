# Feature Specification: Enhanced Modal Features

> Feature ID: FEATURE-039-B
> Version: v1.0
> Status: Refined
> Last Updated: 03-04-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-04-2026 | Initial specification — scope adjusted based on existing 039-A implementation |

## Overview

FEATURE-039-B enhances the Folder Browser Modal (implemented in FEATURE-039-A) with search/filter, breadcrumb navigation, typed file icons, image inline preview, download capability, large file handling, improved keyboard accessibility, and ARIA roles. The MVP modal already has two-panel layout, tree loading, file preview (markdown, HTML, code), binary detection, empty folder handling, error retry, and Escape-to-close. This feature adds the remaining polish and accessibility features.

## User Stories

- **US-1:** As a developer browsing deliverables, I want to search/filter files by name so I can quickly find specific files in large folder trees.
- **US-2:** As a developer browsing deliverables, I want breadcrumb navigation showing the current path so I know where I am in the folder hierarchy.
- **US-3:** As a developer browsing deliverables, I want type-specific icons on files so I can visually distinguish file types at a glance.
- **US-4:** As a developer browsing deliverables, I want to preview images inline so I don't need to download them separately.
- **US-5:** As a developer browsing deliverables, I want a download button so I can save files locally.
- **US-6:** As a keyboard user, I want to navigate the modal with Tab and arrow keys so I can use it without a mouse.
- **US-7:** As a screen reader user, I want proper ARIA roles so the modal is accessible.

## Acceptance Criteria

### AC-1: Search/Filter Bar (AC-039.11)
- **AC-1.1:** A search input MUST appear at the top of the tree panel.
- **AC-1.2:** Typing in the search input MUST filter file and folder names case-insensitively.
- **AC-1.3:** Filtering MUST be recursive — matching files inside nested folders MUST remain visible with their parent folders expanded.
- **AC-1.4:** Filtering MUST be debounced at 200ms to avoid excessive DOM updates.
- **AC-1.5:** Clearing the search input MUST restore the full tree.

### AC-2: Breadcrumb Navigation (AC-039.12)
- **AC-2.1:** A breadcrumb bar MUST appear between the header and the body panels.
- **AC-2.2:** Breadcrumb MUST show the current folder path as clickable segments.
- **AC-2.3:** Clicking a breadcrumb segment MUST navigate to that folder level.
- **AC-2.4:** When path has >5 segments, leading segments MUST be collapsed to "…" with a tooltip showing the full path.

### AC-3: Typed File Icons (AC-039.13)
- **AC-3.1:** Files MUST show type-specific icons: 📝 for `.md`, 🖼️ for images (.png/.jpg/.svg/.gif/.webp), 💻 for code files (.js/.py/.ts/.css/.html/.json/.yaml/.yml/.sh), 📄 for all other files.
- **AC-3.2:** Folders MUST continue showing 📁.
- **AC-3.3:** Icons MUST be applied in both the main tree and lazy-loaded subtrees.

### AC-4: Image Inline Preview (AC-039.14)
- **AC-4.1:** Clicking an image file (.png/.jpg/.jpeg/.gif/.svg/.webp) MUST render an `<img>` element in the preview panel instead of the "Binary file" message.
- **AC-4.2:** The image MUST be loaded via the file API endpoint (`/api/ideas/file?path=...`) or a blob URL.
- **AC-4.3:** The image MUST be contained within the preview panel (max-width/max-height 100%).

### AC-5: Download Button (AC-039.15)
- **AC-5.1:** A download button MUST appear in the preview panel header when a file is selected.
- **AC-5.2:** Clicking download MUST trigger a browser download of the file.
- **AC-5.3:** The download button MUST be disabled (or hidden) when no file is selected.

### AC-6: Binary/Large File Handling (AC-039.16, AC-039.17)
- **AC-6.1:** Binary files (non-image) MUST show file name, type info, and a "Download" button (not just "Binary file — cannot preview").
- **AC-6.2:** Text files larger than 1MB MUST be truncated with a message: "File too large — download instead" and a download button.

### AC-7: Empty Folder Message (AC-039.18)
- **AC-7.1:** Empty folders MUST show "This folder is empty" (exact text) in the tree panel.

### AC-8: Keyboard Accessibility (AC-039.20)
- **AC-8.1:** Escape MUST close the modal (already implemented).
- **AC-8.2:** Tab MUST move focus between tree panel and preview panel.
- **AC-8.3:** Arrow Up/Down MUST navigate between tree items when tree panel is focused.
- **AC-8.4:** Enter MUST select/expand the focused tree item.

### AC-9: ARIA Roles (AC-039.21)
- **AC-9.1:** The modal container MUST have `role="dialog"` and `aria-modal="true"`.
- **AC-9.2:** The tree panel root `<ul>` MUST have `role="tree"`.
- **AC-9.3:** Each tree item `<li>` MUST have `role="treeitem"`.
- **AC-9.4:** The modal MUST have an `aria-label` or `aria-labelledby` referencing the title.

## Functional Requirements

### FR-1: Search/Filter
- **FR-1.1:** Add an `<input>` element with placeholder "Filter files…" at the top of `.folder-browser-tree`.
- **FR-1.2:** On input, debounce 200ms, then walk tree DOM: hide items not matching query, show matching items and their ancestor `<li>` elements.
- **FR-1.3:** On empty query, show all items.

### FR-2: Breadcrumb
- **FR-2.1:** Add a `.folder-browser-breadcrumb` div between header and body.
- **FR-2.2:** Parse the `folderPath` into segments, render as clickable spans separated by " / ".
- **FR-2.3:** Each segment click calls `_loadTree(pathUpToSegment)` and updates breadcrumb.
- **FR-2.4:** If segments > 5, show first segment + "…" + last 3 segments.

### FR-3: Typed Icons
- **FR-3.1:** In `_buildSimpleTree()` and when wiring tree handlers, replace generic 📄 with type-specific icons based on file extension.
- **FR-3.2:** Define icon map: `{ md: '📝', png/jpg/jpeg/gif/svg/webp: '🖼️', js/py/ts/css/html/json/yaml/yml/sh: '💻', default: '📄' }`.

### FR-4: Image Preview
- **FR-4.1:** In `_selectFile()`, check if extension is an image type (.png/.jpg/.jpeg/.gif/.svg/.webp).
- **FR-4.2:** If image, create `<img src="/api/ideas/file?path=...">` instead of calling text fetch.
- **FR-4.3:** Style image with `max-width: 100%; max-height: 100%; object-fit: contain`.

### FR-5: Download
- **FR-5.1:** Add a download `<button>` or `<a>` in the preview header.
- **FR-5.2:** Set `href` to file API URL with `download` attribute, or use `fetch` + blob URL + programmatic click.
- **FR-5.3:** Show only when `this.currentFile` is set.

### FR-6: Large File & Binary Enhancement
- **FR-6.1:** After fetching text content, check `content.length > 1_048_576` (1MB). If exceeded, show truncation message with download button.
- **FR-6.2:** Enhance `_renderBinaryMessage()` to show file info (name, extension, size if available) and a functional download button.

### FR-7: Empty Folder Text
- **FR-7.1:** Change "No files in this folder" (line 124) to "This folder is empty".
- **FR-7.2:** Change "Empty folder" (line 194) to "This folder is empty".

### FR-8: Keyboard Navigation
- **FR-8.1:** Add `tabindex="0"` to tree panel and preview panel.
- **FR-8.2:** On keydown in tree panel: ArrowUp/ArrowDown moves focus between `.tree-item` elements, Enter clicks the focused item.
- **FR-8.3:** Tab cycles focus: search input → tree panel → preview panel.

### FR-9: ARIA Roles
- **FR-9.1:** Set `role="dialog"`, `aria-modal="true"`, `aria-labelledby` on `.folder-browser-modal`.
- **FR-9.2:** Set `role="tree"` on the root `<ul>` element in tree panel.
- **FR-9.3:** Set `role="treeitem"` on each `<li>` tree item.
- **FR-9.4:** Add `id` to title element for `aria-labelledby` reference.

## Non-Functional Requirements

- **NFR-1:** Search filter must not cause visible lag on trees with up to 500 items.
- **NFR-2:** All new features must work without external dependencies (vanilla JS/CSS only).
- **NFR-3:** folder-browser-modal.js must not exceed 20KB after changes.
- **NFR-4:** Changes must not break existing folder browser functionality.

## UI/UX Requirements

- Search input: standard text input with search icon or placeholder text, positioned at top of tree panel.
- Breadcrumb: horizontal path display with " / " separators, subtle styling, clickable segments.
- Download button: small icon button (⬇️ or similar) in preview header, right-aligned.
- Typed icons replace generic file icons — no layout changes needed.
- Image preview fills the preview panel area with `object-fit: contain`.

## Dependencies

### Internal
- **FEATURE-039-A** (Folder Browser Modal MVP) — ✅ Completed. Provides the base modal with tree, preview, close handlers.

### External
- None.

## Business Rules

- **BR-1:** Image preview takes priority over binary detection — image extensions are treated as previewable, not binary.
- **BR-2:** Download works for all file types regardless of preview capability.
- **BR-3:** Large file threshold is 1MB (1,048,576 bytes) for text content truncation.

## Edge Cases & Constraints

- **EC-1:** Search with no results: tree panel shows "No matching files" message.
- **EC-2:** Very long file names in breadcrumb: use CSS text-overflow: ellipsis on individual segments.
- **EC-3:** SVG files: preview as `<img>` (not raw XML), matching the image preview behavior.
- **EC-4:** Network error during image load: show broken image placeholder with download fallback.
- **EC-5:** Multiple rapid file selections: abort previous fetch (already implemented in _selectFile).

## Out of Scope

- **OOS-1:** Drag-and-drop file operations.
- **OOS-2:** File editing within the modal.
- **OOS-3:** Multi-file selection or batch download.
- **OOS-4:** File upload capability.
- **OOS-5:** Syntax highlighting for code files (would require a library).

## Technical Considerations

- The search filter can use a DOM-walking approach similar to `_filterTree()` in other components — hide non-matching `<li>` elements, keep matching items and ancestor `<li>` visible.
- Image preview should use the existing `/api/ideas/file` endpoint with appropriate content-type handling, or construct a direct URL and let the browser handle content negotiation.
- Download can use an `<a>` element with `download` attribute pointing to the file API URL, or fetch + blob URL for cross-origin compatibility.
- ARIA roles can be added directly in `_createDOM()` and `_buildSimpleTree()` without affecting existing functionality.
- Keyboard navigation should use a `keydown` event listener on the tree panel with a focus tracking index.

## Open Questions

None.
