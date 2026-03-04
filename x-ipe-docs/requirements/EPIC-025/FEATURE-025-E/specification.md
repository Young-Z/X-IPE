# Feature Specification: KB Search & Preview

> Feature ID: FEATURE-025-E  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-19-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 02-19-2026 | Initial specification | - |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| KB Landing View | HTML | [mockups/knowledge-base-v1.html](x-ipe-docs/requirements/EPIC-025/FEATURE-025-E/mockups/knowledge-base-v1.html) | KB landing with search modal, sidebar search, and preview panel | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from the mockup marked as "current".

## Overview

**What:** FEATURE-025-E adds search and preview capabilities to the Knowledge Base. It provides two search mechanisms — an inline sidebar search for quick filtering and a global search modal (Cmd+K) for cross-section searching — plus a right-side preview panel that shows file details, AI-suggested tags, and action buttons when a file is selected.

**Why:** Users currently have no way to quickly find specific knowledge items across landing files, topics, and processed summaries. The existing sidebar search only filters by file name in the tree view. Without a proper preview panel, users must navigate away from the current view to inspect file details. This feature bridges the gap between raw file listing and efficient knowledge discovery.

**Who:**
- End users who need to quickly locate knowledge items across the entire KB
- Developers and knowledge managers reviewing file metadata before processing
- AI agents that interact with search results via KB Manager Skill

## Dependencies

| Dependency | Type | Status | Integration Points |
|------------|------|--------|-------------------|
| FEATURE-025-A | Feature | Complete | KB Core Infrastructure — file index, sidebar, `GET /api/kb/index`, `kbCore` JS object |
| FEATURE-025-B | Feature | Complete | KB Landing Zone — landing files, upload, `kbLanding` JS object |
| FEATURE-025-C | Feature | Complete | KB Manager Skill — `GET /api/kb/search`, AI tags/keywords |
| FEATURE-025-D | Feature | Complete | KB Topics & Summaries — topics list, `kbTopics` JS object |

## User Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-1 | As a **user**, I want to **type in the sidebar search box** to filter visible files and topics instantly, so that **I can narrow down the tree view without opening a modal** | Must |
| US-2 | As a **user**, I want to **press Cmd+K to open a global search modal** that searches across file names, topic names, and content, so that **I can find any knowledge item from anywhere** | Must |
| US-3 | As a **user**, I want to **see search results grouped by section** (Recent, Files, Topics, Summaries) with matched terms highlighted, so that **I can quickly identify the right result** | Must |
| US-4 | As a **user**, I want to **navigate search results with keyboard** (↑/↓ to move, Enter to select, Esc to close), so that **I can use the modal without reaching for the mouse** | Should |
| US-5 | As a **user**, I want to **click a file in the tree or search results to see its preview** in a right-side panel with metadata, tags, and actions, so that **I can inspect files without leaving the current view** | Must |
| US-6 | As a **user**, I want to **close the preview panel** via an X button, so that **I can reclaim horizontal space when I don't need it** | Should |
| US-7 | As a **user**, I want to **filter search results by file type and topic**, so that **I can narrow results to specific categories** | Should |

## Acceptance Criteria

### 1. Sidebar Inline Search (AC-1.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-1.1 | Sidebar search input MUST appear below the sidebar header (existing `#kb-search`) | Navigate to KB → search input visible in sidebar |
| AC-1.2 | Typing in sidebar search MUST instantly filter the tree view by file name, topic name, and keywords | Type "neural" → only matching files/topics shown |
| AC-1.3 | Sidebar search MUST be case-insensitive | Type "PDF" → matches "report.pdf" |
| AC-1.4 | Clearing the search input MUST restore the full tree view | Clear input → all files shown |
| AC-1.5 | Matched terms MUST be highlighted in the tree view results | Type "report" → "report" portion highlighted in matching file names |

### 2. Global Search Modal (AC-2.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-2.1 | Pressing `Cmd+K` (Mac) / `Ctrl+K` (Win) MUST open the search modal | Press Cmd+K → modal appears with focused input |
| AC-2.2 | Search modal MUST overlay the page with a semi-transparent backdrop with blur | Modal open → backdrop visible, content behind blurred |
| AC-2.3 | Search modal MUST call `GET /api/kb/search?q={query}` for server-side search | Type query → network request made to search API |
| AC-2.4 | Search results MUST be grouped into sections: "Recent", "Files", "Topics", "Summaries" | Search results → section headers visible |
| AC-2.5 | Each result MUST show an icon (by file type), title, and path | Result items → icon + title + path displayed |
| AC-2.6 | Matched terms in titles MUST be highlighted with `<span class="search-result-highlight">` | Search "machine" → "machine" wrapped in highlight span |
| AC-2.7 | Pressing `Esc` or clicking backdrop MUST close the modal | Press Esc → modal closes |
| AC-2.8 | `↑`/`↓` arrow keys MUST navigate between results with visual active indicator | Press ↓ → next result highlighted |
| AC-2.9 | `Enter` on a selected result MUST navigate to that item (file preview, topic detail, or summary) | Select + Enter → item loaded in content area |
| AC-2.10 | Search modal footer MUST show keyboard shortcut hints (↑↓ to navigate, Enter to select) | Modal open → footer shows keyboard hints |
| AC-2.11 | UI layout of search modal MUST match the approved mockup (knowledge-base-v1.html) | Visual comparison → matches mockup |
| AC-2.12 | Search input MUST debounce API calls (300ms delay) | Type rapidly → only one API call after pause |

### 3. Preview Panel (AC-3.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-3.1 | Clicking a file in the tree or search results MUST open the preview panel on the right side | Click file → preview panel slides in from right |
| AC-3.2 | Preview panel MUST show: file thumbnail/icon (type-specific), file name, type, size, date added, and status | Panel open → all metadata fields displayed |
| AC-3.3 | Preview panel MUST show AI-suggested tags (keywords from file index) as badges | Panel open → tag badges visible below metadata |
| AC-3.4 | Preview panel MUST include "Process" action button (calls `POST /api/kb/process`) | Click Process → triggers processing API |
| AC-3.5 | Preview panel MUST include "Open" action button (navigates to file in Content Viewer) | Click Open → file opened in viewer |
| AC-3.6 | Preview panel header MUST include a close (X) button | Panel header → X button visible |
| AC-3.7 | Clicking the close button MUST hide the preview panel | Click X → panel hidden, content area expands |
| AC-3.8 | Preview panel width MUST be 360px (as per mockup) | Inspect → panel width is 360px |
| AC-3.9 | Preview panel MUST update when a different file is selected | Click another file → preview updates |
| AC-3.10 | If file has status "Processed", status value MUST be shown in green; "Pending" in amber | Check colors → processed=green, pending=amber |
| AC-3.11 | File icons MUST be type-specific: PDF (bi-file-pdf), Markdown (bi-markdown), code (bi-code-square), folder (bi-folder) | Check icon classes → type-appropriate |
| AC-3.12 | UI layout of preview panel MUST match the approved mockup (knowledge-base-v1.html) | Visual comparison → matches mockup |

### 4. Filter Options (AC-4.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-4.1 | Search modal MUST provide filter chips for file types (PDF, Markdown, Code, Other) | Modal open → filter chips visible |
| AC-4.2 | Clicking a filter chip MUST narrow results to that file type | Click "PDF" → only PDF results shown |
| AC-4.3 | Filter chips MUST support multi-select (combine filters) | Click PDF + Markdown → both types shown |
| AC-4.4 | Active filter MUST be visually distinguished (filled background) | Active chip → different style from inactive |
| AC-4.5 | Topic filter dropdown MUST list available topics from `GET /api/kb/topics` | Open dropdown → topics listed |

### 5. Integration (AC-5.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-5.1 | Search modal MUST be accessible from both Landing and Topics views | Switch views → Cmd+K works in both |
| AC-5.2 | Selecting a search result MUST navigate to the correct view (Landing for files, Topics for topics) | Select topic result → Topics view loaded |
| AC-5.3 | Preview panel MUST work in both Landing and Topics views | Select file in either view → preview shows |
| AC-5.4 | Existing sidebar search filtering MUST continue working alongside global search | Both search mechanisms → independent operation |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | **Sidebar Search Enhancement** — Enhance existing `#kb-search` input to support highlighting of matched terms in tree view results. Current filtering by name/topic/keywords continues. Add visual feedback for match highlighting. | Must |
| FR-2 | **Global Search Modal** — Create a search modal triggered by `Cmd+K`/`Ctrl+K` that calls `GET /api/kb/search?q={query}` and displays grouped results with keyboard navigation. Debounce API calls at 300ms. | Must |
| FR-3 | **Preview Panel** — Create a 360px right-side panel inside `kb-container` that displays file metadata, AI tags, and action buttons when a file is selected. Panel is hidden by default and toggles on file click. | Must |
| FR-4 | **Search Result Navigation** — Selecting a search result navigates to the item: files open preview panel, topics switch to Topics view, summaries open the topic detail with selected summary version. | Must |
| FR-5 | **Filter System** — Add filter chips to search modal for file type filtering. Populate topic filter from `GET /api/kb/topics`. Filters narrow server-side results via query parameters. | Should |
| FR-6 | **Search API Enhancement** — Extend `GET /api/kb/search` to accept optional `type` and `topic` query parameters for server-side filtering. Return results grouped by category (files, topics, summaries). | Should |

## Non-Functional Requirements

| # | Requirement | Priority |
|---|-------------|----------|
| NFR-1 | Sidebar search filtering MUST respond within 100ms (client-side) | Must |
| NFR-2 | Global search API results MUST return within 500ms for index queries | Should |
| NFR-3 | Search modal open/close animation MUST complete within 200ms | Should |
| NFR-4 | Preview panel MUST not cause layout shift on the tree/content area | Must |
| NFR-5 | Search modal MUST be accessible (focus trap, aria labels, screen reader support) | Should |

## UI/UX Requirements

### Search Modal (from mockup)
- **Position:** Centered overlay with dark semi-transparent backdrop (`rgba(0,0,0,0.7)`) and `backdrop-filter: blur(4px)`
- **Width:** `min(640px, 90vw)` for responsive sizing
- **Header:** Search icon + text input + ESC kbd hint
- **Body:** Grouped results with section headers ("Recent", "Files", "Topics", "Summaries")
- **Footer:** Keyboard navigation hints (`↑ ↓ to navigate`, `Enter to select`)
- **Result item:** Type icon + title (with highlighted matches) + path breadcrumb

### Preview Panel (from mockup)
- **Position:** Right side of KB content area, inside `kb-container`
- **Width:** 360px fixed
- **Header:** "Preview" title + close (X) button
- **Thumbnail:** Full-width area with large type-specific icon (48px)
- **Info rows:** Label/value pairs: Name, Type, Size, Added, Status
- **Tags:** Horizontal badge strip below info rows
- **Actions:** Two buttons at bottom: "Process" (primary) + "Open" (ghost/outline)

### Sidebar Search Enhancement
- **Input:** Existing `#kb-search` — no visual changes needed
- **Highlighting:** Matched text in tree items wrapped in `<mark>` or `<span class="kb-search-highlight">`

## Business Rules

| # | Rule | Rationale |
|---|------|-----------|
| BR-1 | Search modal only calls API after 300ms debounce | Prevent excessive API calls during typing |
| BR-2 | Preview panel shows last-selected file; selecting another file replaces it | Only one preview at a time |
| BR-3 | Cmd+K shortcut MUST not conflict with browser defaults (uses `preventDefault`) | Ensure shortcut works reliably |
| BR-4 | Search results limited to 50 items per category | Performance and UX — avoid overwhelming results |
| BR-5 | Empty search query in modal shows "Recent" section (last 5 viewed files) if available | Useful even without typing |

## Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| EC-1 | Search returns zero results | Show "No results found for '{query}'" message in modal body |
| EC-2 | KB index is empty (no files uploaded) | Search modal shows "No knowledge items yet. Upload files to get started." |
| EC-3 | Preview panel file deleted externally | Next index refresh removes stale entry; preview shows "File not found" |
| EC-4 | Very long file names in preview | Truncate with ellipsis, show full name on hover (title attribute) |
| EC-5 | Search while KB index is refreshing | Show loading spinner, queue search until refresh completes |
| EC-6 | Preview panel open + window resize below breakpoint | Hide preview panel on viewport < 1024px |

## Technical Considerations

- **Existing code:** `kbCore.showFilePreview()` already exists as a placeholder — replace with preview panel
- **Existing search:** `kbCore.searchTerm` client-side filtering works — enhance with highlighting
- **Search API:** `GET /api/kb/search` exists in `kb_routes.py` via `KBManagerService.search()` — extend for grouped results and filters
- **Layout:** Preview panel must be inside `kb-container` flex layout, pushing content area narrower
- **CSS:** New file `kb-search.css` for search modal and preview panel styles, or extend `kb-core.css`
- **JS:** New file `kb-search.js` for search modal logic, or extend `kb-core.js`

## Out of Scope (v1)

- Vector/semantic search (Phase 2 with ChromaDB)
- File content preview rendering (PDF viewer, image viewer)
- Search history persistence across sessions
- AI-powered "related items" suggestions in preview
- Drag-and-drop from search results
- Advanced query syntax (AND, OR, NOT operators)
- Date range filter (deferred to FEATURE-025-F if needed)

## Open Questions

| # | Question | Status |
|---|----------|--------|
| OQ-1 | Should "Recent" section track across browser sessions (localStorage) or only current session? | Decided: current session only (in-memory) |
| OQ-2 | Should clicking a topic in search results navigate to Topics view or show topic preview? | Decided: navigate to Topics view (topic detail) |
