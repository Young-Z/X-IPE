# Feature Specification: KB Article Editor

> Feature ID: FEATURE-049-D  
> Version: v2.0  
> Status: Refined  
> Last Updated: 03-11-2026

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 03-11-2026 | Initial specification |
| v2.0 | 03-11-2026 | Template alignment — added GWT acceptance criteria, overview, UI/UX requirements, dependencies, business rules, out of scope, technical considerations |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| KB Interface v1 — Article Detail (Scene 2) | Interactive HTML | [../../mockups/kb-interface-v1.html](../../mockups/kb-interface-v1.html) | Article detail view showing content rendering and metadata layout | Current | 03-11-2026 |

## Overview

The KB Article Editor feature provides a modal-based markdown editor for creating and editing Knowledge Base articles within X-IPE. Users can author content using EasyMDE with a rich toolbar, manage frontmatter metadata (title, tags, author, dates), and save articles directly to the KB storage backend.

The editor follows the compose-idea-modal design pattern — a large (90vw×90vh) overlay with backdrop blur and spring animation — ensuring a focused writing experience. Tag selection uses clickable chip controls with lifecycle (amber) and domain (blue) visual differentiation, sourced from the KB configuration endpoint.

This feature targets developers and knowledge workers who need to create or update KB content without leaving the X-IPE interface. It integrates with the KB Backend (FEATURE-049-A) for file persistence and dispatches events to keep the sidebar and browse view synchronized.

## User Stories

- As a developer using X-IPE, I want a modal-based markdown editor for creating and editing KB articles so that I can author knowledge content with proper frontmatter metadata directly within the X-IPE interface.
- As a knowledge author, I want to edit existing articles with pre-populated fields so that I can update content without re-entering metadata.
- As a developer, I want to be warned before discarding unsaved changes so that I don't accidentally lose my work.

## Acceptance Criteria

### AC-049-D-01: Modal Launch

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-01a | GIVEN user is in KB browse view WHEN user right-clicks a folder OR clicks "New Article" button THEN the KB Article Editor modal opens | UI |
| AC-049-D-01b | GIVEN the KB Article Editor modal is opened from a folder context WHEN the modal renders THEN the target folder is pre-selected | UI |

### AC-049-D-02: Modal Layout

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-02a | GIVEN user triggers the KB Article Editor WHEN the modal opens THEN it uses compose-idea-modal pattern: 90vw×90vh, backdrop blur, spring scale animation, z-index 1051 | UI |

### AC-049-D-03: Markdown Editor

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-03a | GIVEN the KB Article Editor modal is open WHEN the editor area renders THEN EasyMDE renders with toolbar: Bold, Italic, Heading, Lists, Link, Code, Preview toggle | UI |

### AC-049-D-04: Metadata Fields

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-04a | GIVEN the KB Article Editor modal is open WHEN the modal renders THEN a title text input renders above the editor | UI |
| AC-049-D-04b | GIVEN the KB Article Editor modal is open WHEN tag options are loaded THEN lifecycle tags render as multi-select chips sourced from `/api/kb/config` | UI |
| AC-049-D-04c | GIVEN the KB Article Editor modal is open WHEN tag options are loaded THEN domain tags render as multi-select chips sourced from `/api/kb/config` | UI |

### AC-049-D-05: Default Values

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-05a | GIVEN a new article is being created WHEN the editor modal opens THEN the author field is auto-populated with "user" | Unit |
| AC-049-D-05b | GIVEN a new article is being created WHEN the editor modal opens THEN the created date is auto-populated with today's date | Unit |
| AC-049-D-05c | GIVEN a new article is being created WHEN the editor modal opens THEN the `auto_generated` field defaults to false | Unit |

### AC-049-D-06: Save Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-06a | GIVEN user has entered article content WHEN user clicks "Save Article" THEN a `.md` file is created via `POST /api/kb/files` | API |
| AC-049-D-06b | GIVEN an article is saved WHEN the file is created THEN it contains YAML frontmatter (title, tags, author, created, auto_generated) AND body content | Unit |

### AC-049-D-07: Edit Existing Article

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-07a | GIVEN an existing article is selected for editing WHEN the editor modal opens THEN title, tags, and content are pre-populated from frontmatter and body | UI |

### AC-049-D-08: Cancel & Discard

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-08a | GIVEN the editor has unsaved changes WHEN user clicks Cancel OR presses Escape THEN a confirmation dialog ("Discard changes?") is shown | UI |
| AC-049-D-08b | GIVEN the discard confirmation dialog is shown WHEN user confirms THEN changes are discarded AND the modal closes; WHEN user declines THEN the modal returns to editing | UI |

### AC-049-D-09: Event Dispatch

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-D-09a | GIVEN an article is saved successfully WHEN the save operation completes THEN a `kb:changed` custom event is dispatched | Unit |
| AC-049-D-09b | GIVEN a `kb:changed` event is dispatched WHEN the sidebar receives the event THEN the sidebar tree refreshes | Integration |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB)

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

## UI/UX Requirements

| ID | Requirement |
|----|-------------|
| UX-049-D-01 | Modal follows compose-idea-modal design pattern: 90vw×90vh, backdrop blur, spring scale animation |
| UX-049-D-02 | Title input is prominently positioned above the editor area |
| UX-049-D-03 | Tag chips use toggle behavior; lifecycle chips use amber gradient, domain chips use blue outlined style |
| UX-049-D-04 | EasyMDE toolbar matches compose-idea-modal configuration (consistent iconography and spacing) |
| UX-049-D-05 | Save and Cancel buttons are clearly positioned in the modal footer |
| UX-049-D-06 | Discard confirmation dialog uses standard X-IPE dialog pattern |
| UX-049-D-07 | Modal z-index (1051) ensures it renders above all other UI layers |

## Dependencies

### Internal Dependencies

| Feature | Dependency Type | Description |
|---------|----------------|-------------|
| FEATURE-049-A | Required | KB Backend & Storage Foundation — provides `POST /api/kb/files`, `PUT /api/kb/files/{path}`, and `/api/kb/config` endpoints |
| FEATURE-049-C | Optional | KB Browse & Search — "New Article" button in browse view triggers the editor modal |

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| EasyMDE | Existing | Markdown editor with toolbar, preview, and syntax highlighting |

## Business Rules

| ID | Rule |
|----|------|
| BR-049-D-01 | Title is required — the Save button is disabled when the title field is empty |
| BR-049-D-02 | Filenames are derived from the title: lowercased, spaces replaced with hyphens, special characters removed |
| BR-049-D-03 | Author defaults to "user" for new articles; preserved from frontmatter for existing articles |
| BR-049-D-04 | Created date defaults to today's date for new articles; preserved from frontmatter for existing articles |
| BR-049-D-05 | The `auto_generated` field defaults to false for manually created articles |
| BR-049-D-06 | Frontmatter is serialized as YAML and prepended to markdown content before saving |

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty title | Save button disabled |
| File already exists at path | Show error toast from API response |
| API error on save | Show error toast, keep modal open |
| Very long content | EasyMDE handles scrolling; no max content limit |
| Special chars in title | Sanitize for filename (replace spaces with hyphens, lowercase) |
| Modal opened without folder context | Default to root KB folder |
| Tag config endpoint unavailable | Render empty tag chip areas; allow save without tags |
| Browser back/forward while modal is open | Modal intercepts navigation; shows discard dialog if content is modified |

## Out of Scope

- Image upload or drag-and-drop media embedding
- Real-time collaborative editing (multi-user)
- Article templates or boilerplate insertion
- Spell-check beyond EasyMDE's built-in capabilities
- Version history or undo beyond the current editing session
- Bulk article creation or import

## Technical Considerations

- EasyMDE instance must be properly destroyed on modal close to prevent memory leaks
- Frontmatter serialization must produce valid YAML that roundtrips correctly on re-edit
- The `kb:changed` event must be dispatched only after a successful API response to prevent stale UI state
- Modal must trap focus for keyboard accessibility (Tab, Shift+Tab cycle within modal)
- Tag configuration should be fetched once on modal open and cached for the session

## Open Questions

- None at this time.
