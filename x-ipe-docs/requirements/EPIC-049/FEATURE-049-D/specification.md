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

### AC-049-D-01: New Article Button
**Given** the KB sidebar is visible  
**When** the user right-clicks a folder or clicks a "New Article" action  
**Then** the article editor modal opens with the target folder pre-selected

### AC-049-D-02: Modal Shell
**Given** the editor modal opens  
**When** the modal renders  
**Then** it uses the compose-idea-modal pattern: 90vw×90vh, backdrop blur, spring scale animation, z-index 1051

### AC-049-D-03: EasyMDE Editor
**Given** the editor modal is open  
**When** the editor initializes  
**Then** EasyMDE renders with toolbar: Bold, Italic, Heading, Lists, Link, Code, Preview toggle

### AC-049-D-04: Frontmatter Form
**Given** the editor modal is open  
**When** the form renders above the editor  
**Then** it shows: Title (text input), Lifecycle tags (multi-select chips from /api/kb/config), Domain tags (multi-select chips from /api/kb/config)

### AC-049-D-05: Auto-Populated Fields
**Given** a new article is being created  
**When** the frontmatter form renders  
**Then** author is auto-populated with "user", created date with today, auto_generated defaults to false

### AC-049-D-06: Save Creates File
**Given** the user fills in title and content  
**When** the user clicks "Save Article"  
**Then** a `.md` file is created via `POST /api/kb/files` with YAML frontmatter (title, tags, author, created, auto_generated) and body content

### AC-049-D-07: Edit Existing Article
**Given** an existing KB article is opened for editing  
**When** the modal opens  
**Then** it pre-populates the title, tags, and content from the existing file's frontmatter and body

### AC-049-D-08: Cancel with Confirmation
**Given** the user has modified content in the editor  
**When** the user clicks Cancel or presses Escape  
**Then** a confirmation dialog appears ("Discard changes?"); confirming closes the modal, declining returns to editing

### AC-049-D-09: kb:changed Event
**Given** the user saves an article  
**When** the save succeeds  
**Then** a `kb:changed` custom event is dispatched to refresh the sidebar tree

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
