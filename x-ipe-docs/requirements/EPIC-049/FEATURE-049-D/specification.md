# FEATURE-049-D: KB Article Editor — Specification

## Feature Overview

| Field | Value |
|-------|-------|
| Feature ID | FEATURE-049-D |
| Epic | EPIC-049 (Knowledge Base) |
| Version | v1.0 |
| Status | Refined |
| Dependencies | FEATURE-049-A (KB Backend & Storage Foundation) |

## User Story

As a developer using X-IPE, I want a modal-based markdown editor for creating and editing KB articles so that I can author knowledge content with proper frontmatter metadata directly within the X-IPE interface.

## Acceptance Criteria

| AC ID | Criterion | Test Type |
|-------|-----------|-----------|
| AC-049-D-01a | Right-clicking a folder or clicking "New Article" opens the editor modal | UI |
| AC-049-D-01b | Target folder is pre-selected in the modal | UI |
| AC-049-D-02a | Modal uses compose-idea-modal pattern: 90vw×90vh, backdrop blur, spring scale animation, z-index 1051 | UI |
| AC-049-D-03a | EasyMDE renders with toolbar: Bold, Italic, Heading, Lists, Link, Code, Preview toggle | UI |
| AC-049-D-04a | Title text input renders above the editor | UI |
| AC-049-D-04b | Lifecycle tags render as multi-select chips sourced from `/api/kb/config` | UI |
| AC-049-D-04c | Domain tags render as multi-select chips sourced from `/api/kb/config` | UI |
| AC-049-D-05a | Author field auto-populated with "user" | Unit |
| AC-049-D-05b | Created date auto-populated with today's date | Unit |
| AC-049-D-05c | `auto_generated` defaults to false | Unit |
| AC-049-D-06a | Clicking "Save Article" creates a `.md` file via `POST /api/kb/files` | API |
| AC-049-D-06b | File contains YAML frontmatter (title, tags, author, created, auto_generated) and body content | Unit |
| AC-049-D-07a | Opening an existing article pre-populates title, tags, and content from frontmatter and body | UI |
| AC-049-D-08a | Clicking Cancel or pressing Escape shows confirmation dialog ("Discard changes?") when content is modified | UI |
| AC-049-D-08b | Confirming discards changes and closes the modal; declining returns to editing | UI |
| AC-049-D-09a | Successful save dispatches a `kb:changed` custom event | Unit |
| AC-049-D-09b | Event triggers sidebar tree refresh | Integration |

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-049-D-01 | `KBArticleEditor` class in new file `src/x_ipe/static/js/features/kb-article-editor.js` |
| FR-049-D-02 | Modal follows compose-idea-modal CSS pattern (overlay, header, body, footer) |
| FR-049-D-03 | EasyMDE initialized with same config as compose-idea-modal (toolbar, spellcheck off, status off) |
| FR-049-D-04 | Tag selection via clickable chip UI — chips toggle active state, lifecycle uses amber style, domain uses blue style |
| FR-049-D-05 | Frontmatter serialized to YAML string and prepended to markdown content before API call |
| FR-049-D-06 | Create: `POST /api/kb/files` with `{ folder, filename, content }` |
| FR-049-D-07 | Update: `PUT /api/kb/files/{path}` with `{ content }` |
| FR-049-D-08 | Dispatches `kb:changed` event on successful save |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-049-D-01 | Modal open animation ≤ 300ms |
| NFR-049-D-02 | Reuse existing EasyMDE library (no new dependencies) |
| NFR-049-D-03 | CSS follows compose-idea-modal design tokens (slate palette, emerald accent) |
| NFR-049-D-04 | Editor must clean up EasyMDE instance on close to prevent memory leaks |

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty title | Save button disabled |
| File already exists at path | Show error toast from API response |
| API error on save | Show error toast, keep modal open |
| Very long content | EasyMDE handles scrolling; no max content limit |
| Special chars in title | Sanitize for filename (replace spaces with hyphens, lowercase) |
