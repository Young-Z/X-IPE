# Feature Specification: Link Interception & Preview Modal

> Feature ID: FEATURE-043-A
> Epic ID: EPIC-043
> Version: v1.0
> Status: Refined
> Last Updated: 03-03-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-03-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| File Link Preview — Full Interactive | HTML | [mockups/file-link-preview-v1.html](x-ipe-docs/requirements/EPIC-043/FEATURE-043-A/mockups/file-link-preview-v1.html) | 5-scenario mockup covering link distinction, preview modal, breadcrumb nav, error/loading states | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

FEATURE-043-A provides the core click-to-preview functionality for internal file links in rendered markdown. When a user clicks a link whose `href` starts with `x-ipe-docs/` or `.github/skills/` in any rendered markdown content, the link is intercepted and the referenced file's content is displayed in a modal overlay instead of navigating away from the current page.

This is the MVP (P0) feature of EPIC-043 (File Link Preview). It covers link interception, modal display, error handling, and loading states. Breadcrumb navigation and visual link distinction are deferred to FEATURE-043-B.

**Target users:** Developers reviewing cross-referenced docs, AI agents generating linked markdown, project managers following documentation chains.

## User Stories

1. **US-043-A.1:** As a developer viewing a feature specification, I want to click an internal link (e.g., to a technical design document) and see it rendered in a modal, so that I don't lose my place in the current document.

2. **US-043-A.2:** As a developer viewing an idea summary that links to a skill file, I want to click the `.github/skills/` link and preview the skill document in a modal, so that I can quickly reference skill instructions without navigating away.

3. **US-043-A.3:** As a developer clicking an internal link to a file that doesn't exist, I want to see a clear error message in the modal, so that I know the link is broken and what path it was looking for.

4. **US-043-A.4:** As a developer clicking multiple links quickly, I want the previous request to be cancelled and the latest link to load, so that I'm not confused by stale content appearing.

## Acceptance Criteria

### Core Preview Functionality

- [ ] **AC-043-A.1:** Clicking a link whose `href` starts with `x-ipe-docs/` in any rendered `.markdown-body` container opens a preview modal (does NOT navigate away)
- [ ] **AC-043-A.2:** Clicking a link whose `href` starts with `.github/skills/` in any rendered `.markdown-body` container opens a preview modal
- [ ] **AC-043-A.3:** Preview modal renders markdown (.md) files correctly using ContentRenderer (with Mermaid, code highlighting, etc.)
- [ ] **AC-043-A.4:** Preview modal renders HTML (.html/.htm) files correctly
- [ ] **AC-043-A.5:** Preview modal renders plain text and code files with syntax highlighting
- [ ] **AC-043-A.6:** Binary files (.png, .jpg, .pdf, etc.) show "Cannot preview binary file" message in modal
- [ ] **AC-043-A.7:** UI layout of the preview modal MUST match the approved mockup (file-link-preview-v1.html) for the "② Preview Modal" scenario
- [ ] **AC-043-A.8:** Visual styling (backdrop blur, header bar, content area) MUST be consistent with mockup (file-link-preview-v1.html)

### Error & Loading States

- [ ] **AC-043-A.9:** While file is loading, modal shows a spinner with the file path displayed below it
- [ ] **AC-043-A.10:** On 404 response, modal shows inline error: "File not found: {path}" with hint text
- [ ] **AC-043-A.11:** On network error, modal shows inline error: "Failed to load file" with a retry button
- [ ] **AC-043-A.12:** Clicking retry button re-fetches the same file
- [ ] **AC-043-A.13:** Error state layout MUST match mockup (file-link-preview-v1.html) "④ Error State" scenario
- [ ] **AC-043-A.14:** Loading state layout MUST match mockup (file-link-preview-v1.html) "⑤ Loading State" scenario

### Abort & Non-Interference

- [ ] **AC-043-A.15:** Clicking a new internal link while a file is loading aborts the pending request and loads the new file
- [ ] **AC-043-A.16:** External links (not starting with `x-ipe-docs/` or `.github/skills/`) continue to behave normally (no interception)
- [ ] **AC-043-A.17:** Links inside code blocks (rendered as `<code>` elements) are NOT intercepted
- [ ] **AC-043-A.18:** Modal can be closed via close button (✕) or clicking the backdrop

### Non-Regression

- [ ] **AC-043-A.19:** Existing ContentRenderer rendering behavior is unchanged for all non-link functionality
- [ ] **AC-043-A.20:** Existing DeliverableViewer `showPreview()` functionality is unchanged when called directly
- [ ] **AC-043-A.21:** Existing FolderBrowserModal functionality is unchanged
- [ ] **AC-043-A.22:** Link interception uses event delegation (single handler per `.markdown-body` container, not per-link)

## Functional Requirements

### FR-043-A.1: Custom Link Renderer in Marked.js

- **Input:** Markdown content with links to `x-ipe-docs/` or `.github/skills/` paths
- **Process:** Configure a custom link renderer in `ContentRenderer.initMarked()` that:
  1. Detects links whose `href` starts with `x-ipe-docs/` or `.github/skills/`
  2. Adds a `data-preview-path="{href}"` attribute to those `<a>` tags
  3. Leaves all other links unchanged
- **Output:** Rendered HTML where internal links have `data-preview-path` attribute

### FR-043-A.2: Delegated Click Interception

- **Input:** Click event on any element inside a `.markdown-body` container
- **Process:**
  1. Check if clicked element (or closest `<a>` ancestor) has `data-preview-path` attribute
  2. If yes: call `preventDefault()`, extract the path value, trigger preview
  3. If no: let the event propagate normally
- **Output:** Internal link clicks trigger preview; external clicks pass through
- **Constraint:** Single delegated listener per `.markdown-body` container (not per `<a>` tag)

### FR-043-A.3: File Content Fetching

- **Input:** File path from `data-preview-path` attribute
- **Process:**
  1. Create or reuse AbortController instance for the modal
  2. Abort any pending request from a previous link click
  3. Show loading state in modal
  4. Fetch `GET /api/file/content?path={encodeURIComponent(path)}`
  5. Handle response based on status code and content type
- **Output:** File content for rendering, or error state
- **API:** Uses existing `/api/file/content` endpoint (no backend changes needed)

### FR-043-A.4: Preview Modal Display

- **Input:** File content and metadata from API response
- **Process:**
  1. Open modal overlay with backdrop blur
  2. Display file name in header bar with close (✕) button
  3. Render content based on type:
     - `markdown` → ContentRenderer.renderMarkdown()
     - `html` → render in iframe or sanitized container
     - `code` → ContentRenderer with syntax highlighting
     - Binary → "Cannot preview binary file" message
  4. Attach click handler for close button and backdrop
- **Output:** Modal displaying rendered file content
- **Constraint:** Reuse existing DeliverableViewer modal styling and structure

### FR-043-A.5: Error State Display

- **Input:** API error response (404, network error, etc.)
- **Process:**
  1. On 404: show "File not found: {path}" with suggestion text
  2. On network error: show "Failed to load file" with retry button
  3. On binary file: show "Cannot preview binary file" message
- **Output:** Error message displayed inline in the modal content area
- **Constraint:** Error states stay in the modal (no toast notifications)

### FR-043-A.6: Abort Controller Management

- **Input:** New link click while previous request is pending
- **Process:**
  1. Maintain single AbortController instance per modal session
  2. On new link click: call `abort()` on existing controller
  3. Create new AbortController for the new request
  4. Pass `signal` to fetch call
- **Output:** Previous request cancelled, new request initiated
- **Constraint:** No stale content displayed from cancelled requests

## Non-Functional Requirements

- **NFR-043-A.1 (Performance):** File content fetched on-demand — no preloading. Single delegated event listener per `.markdown-body` container.
- **NFR-043-A.2 (Progressive Enhancement):** If JavaScript fails, internal links remain standard `<a>` tags and navigate normally (no broken state).
- **NFR-043-A.3 (Accessibility):** Modal should trap focus while open. Close on Escape key. Backdrop click closes modal.
- **NFR-043-A.4 (Security):** Backend `/api/file/content` already validates paths (path traversal protection). Frontend does not need additional security checks.

## UI/UX Requirements

Derived from mockup (file-link-preview-v1.html):

### Preview Modal Layout

- **Backdrop:** Semi-transparent overlay covering full viewport, closes modal on click
- **Modal:** Large overlay (approx 90vw × 90vh or similar), centered, with rounded corners and shadow
- **Header bar:** File path/name displayed on the left, close (✕) button on the right
- **Content area:** Scrollable rendered content below header bar
- **Animation:** Fade-in on open, fade-out on close

### Loading State

- Centered spinner in content area
- File path text displayed below spinner
- No flickering — spinner appears immediately on link click

### Error State

- Centered error icon/illustration
- Primary text: "File not found" or "Failed to load file"
- Secondary text: full file path attempted
- Retry button (for network errors only)

### Interactive Elements

- Close button (✕) in header — always visible
- Backdrop click — closes modal
- Escape key — closes modal
- Retry button — visible only on network errors

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| ContentRenderer (content-renderer.js) | Modification | Add custom link renderer to `initMarked()`, add click delegation |
| DeliverableViewer (deliverable-viewer.js) | Reuse | Reuse modal overlay pattern and styling |
| `/api/file/content` endpoint | Reuse | Existing endpoint, no changes needed |

### External Dependencies

- None — all dependencies are internal to the X-IPE codebase

## Business Rules

- **BR-043-A.1:** Only links with `href` starting with `x-ipe-docs/` or `.github/skills/` are intercepted. All other link patterns pass through normally.
- **BR-043-A.2:** The interception applies globally wherever `.markdown-body` containers are rendered — knowledge base, idea summaries, workflow deliverables, skill docs, specifications, etc.
- **BR-043-A.3:** If the file extension is known to be binary (.png, .jpg, .pdf, .csv, .json), show "Cannot preview" message rather than attempting to render raw binary data.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Link href is `x-ipe-docs/` with trailing slash only (no file) | Show "File not found" error in modal |
| Link href has query parameters (e.g., `?line=5`) | Strip query params, use base path for fetch |
| Link inside `<code>` block (rendered code, not markdown code fence) | NOT intercepted — code blocks contain example paths, not actionable links |
| Link with anchor fragment (e.g., `#section-2`) | Ignore fragment for fetch, display full file |
| Multiple rapid clicks on different links | Each click aborts previous, only last one loads |
| Modal already open, user clicks another internal link in the page behind | Close existing modal, open new one |
| File content is very large (>1MB) | Render normally — browser handles large DOM. No size limit enforced. |
| File path contains special characters or spaces | URL-encode path in fetch call |
| Server returns 500 error | Show "Failed to load file" with retry button |
| Link clicks while JavaScript is disabled/failed | Links behave as normal `<a>` tags (progressive enhancement) |

## Out of Scope

- **Breadcrumb navigation** within the preview modal (FEATURE-043-B)
- **Visual link distinction** — 📄 icon, tooltip, dashed underline (FEATURE-043-B)
- **Skill updates** for path convention (FEATURE-043-C)
- **Existing file migration** (FEATURE-043-D)
- **Image/PDF preview** inside the modal (binary files show message only)
- **Caching** of fetched file content (on-demand every time)
- **Editing** file content from within the preview modal
- **Deep linking** — URLs do not change when preview opens

## Technical Considerations

- The custom link renderer in marked.js should be added during `initMarked()` by extending the default renderer's `link()` method — this ensures all markdown rendering automatically tags internal links
- Event delegation on `.markdown-body` is critical for performance and for handling dynamically rendered content (e.g., markdown loaded after initial page render)
- The existing `/api/file/content` endpoint returns `{content, type, path, extension}` — the `type` field can drive rendering decisions (markdown/html/code)
- AbortController is the standard Web API for request cancellation — one instance per modal session, recreated on each new request
- Modal structure should follow the existing DeliverableViewer pattern (backdrop + modal container + header + content) for visual consistency
- Content inside the modal's `.markdown-body` should also have link interception active (this enables FEATURE-043-B breadcrumb later) — even though FEATURE-043-A doesn't add breadcrumbs, clicking links inside the preview should work by re-rendering the modal content

## Open Questions

- None — all requirements clarified during ideation and requirement gathering
