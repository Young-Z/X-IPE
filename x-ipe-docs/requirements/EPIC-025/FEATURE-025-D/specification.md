# Feature Specification: KB Topics & Summaries

> Feature ID: FEATURE-025-D  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-12-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-12-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Processed Topic View | HTML | [mockups/knowledge-base-processed-v1.html](mockups/knowledge-base-processed-v1.html) | Topic detail with AI summary, version history, source files, knowledge graph | current |
| KB Overview | HTML | [mockups/knowledge-base-v1.html](mockups/knowledge-base-v1.html) | KB landing/overview (for sidebar context only) | outdated — use as directional reference only |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".  
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

FEATURE-025-D delivers the **Topics & Summaries view** for the Knowledge Base — the primary way users explore organized knowledge after files have been classified (via FEATURE-025-C). When a user navigates to the KB section and has processed topics, they see a sidebar listing all topics with metadata (item count, summary count) and a content panel showing the selected topic's AI-generated summary card, version history, source files, and knowledge graph preview.

This feature bridges the gap between raw uploaded files (FEATURE-025-B) and searchable knowledge (FEATURE-025-E). Without it, classified files exist in topic folders with no way to view summaries or navigate between topics in the UI.

The target users are developers and knowledge managers who want to review AI-generated summaries, browse version history of summaries, see source files under a topic, and trigger reprocessing when new files are added.

## User Stories

1. **US-1:** As a user, I want to see a list of all topics in the sidebar so that I can navigate between different knowledge areas.
2. **US-2:** As a user, I want to view an AI-generated summary for a selected topic so that I can quickly understand the topic's content without reading every file.
3. **US-3:** As a user, I want to switch between summary versions so that I can see how the topic summary evolved over time.
4. **US-4:** As a user, I want to see which source files belong to a topic so that I can access the original materials.
5. **US-5:** As a user, I want to trigger reprocessing for a topic so that the summary updates when I add new files.
6. **US-6:** As a user, I want to add new knowledge files to an existing topic so that I can expand a topic's content.

## Acceptance Criteria

### Topics Sidebar (AC-1.x)

- **AC-1.1:** Topics sidebar MUST display all topics returned by `GET /api/kb/topics`, each showing topic name, item count, and summary count.
- **AC-1.2:** Clicking a topic in the sidebar MUST load that topic's detail view in the content panel.
- **AC-1.3:** The currently selected topic MUST be visually highlighted (active state) in the sidebar.
- **AC-1.4:** If no topics exist, the sidebar MUST show an empty state message ("No topics yet. Upload and classify files to create topics.").
- **AC-1.5:** Topic sidebar MUST show topic icon, name, metadata line ("{N} items • {M} summaries"), and item count badge.
- **AC-1.6:** UI layout of the topics sidebar MUST match the approved mockup (knowledge-base-processed-v1.html) for the sidebar section.

### Topic Detail Header (AC-2.x)

- **AC-2.1:** Topic detail header MUST display the topic name, "Processed" status badge, and action buttons ("Reprocess", "Add Knowledge").
- **AC-2.2:** Topic stats row MUST show: Raw Files count, Summaries count, Last Updated (relative time), and Related Topics count.
- **AC-2.3:** Stats values MUST be derived from `GET /api/kb/topics/<name>` response data.
- **AC-2.4:** Visual styling (colors, spacing, typography) of the header MUST be consistent with mockup (knowledge-base-processed-v1.html).

### AI Summary Card (AC-3.x)

- **AC-3.1:** Summary card MUST render the latest summary markdown from `processed/{topic}/summary-vN.md` with proper formatting (headings, lists, code, blockquotes, highlights).
- **AC-3.2:** Summary card header MUST show "AI-Generated Summary" title with stars icon and version/date badge (e.g., "v2 • Feb 5, 2026").
- **AC-3.3:** Summary card MUST include source references section linking to the source files used for generation.
- **AC-3.4:** If no summaries exist for a topic, the card MUST show an empty state ("No summary generated yet. Click Reprocess to generate one.").
- **AC-3.5:** Markdown rendering MUST support: h4 headings with icons, paragraphs, unordered lists, inline code, blockquotes, and highlighted spans.
- **AC-3.6:** Interactive elements shown in mockup (knowledge-base-processed-v1.html) MUST be present and functional.

### Version History (AC-4.x)

- **AC-4.1:** Version history section MUST list all available summary versions (up to last 5), showing version label and generation date.
- **AC-4.2:** The current (latest) version MUST be visually distinguished with a highlighted dot and border.
- **AC-4.3:** Clicking a version item MUST load that version's summary content into the summary card.
- **AC-4.4:** Version history MUST be sorted newest-first (latest version at top).

### Source Files (AC-5.x)

- **AC-5.1:** Source Files section MUST list all raw files under `topics/{topic}/raw/` with file icon (by type), file name, and metadata (size, description).
- **AC-5.2:** Each file item MUST show View and Download action buttons on hover.
- **AC-5.3:** File icons MUST be type-specific: PDF (red), Markdown (purple), code/folder (green).
- **AC-5.4:** Source file count MUST be shown in the section header ("Source Files (N)").

### Actions (AC-6.x)

- **AC-6.1:** "Reprocess" button MUST trigger `POST /api/kb/process` with the topic's file paths, then refresh the summary card on completion.
- **AC-6.2:** "Add Knowledge" button MUST open a file upload dialog scoped to the current topic.
- **AC-6.3:** During reprocessing, a loading indicator MUST be shown on the summary card.
- **AC-6.4:** After reprocessing completes, the summary card and version history MUST update to show the new version.

### Knowledge Graph Preview (AC-7.x)

- **AC-7.1:** Knowledge graph preview MUST display a visual representation of related topics with connected nodes.
- **AC-7.2:** The current topic MUST be the central node with related topics as peripheral nodes.
- **AC-7.3:** Graph MUST include an "Expand" button (placeholder for Phase 2 full graph).

## Functional Requirements

- **FR-1: Topics List API Integration** — The frontend MUST call `GET /api/kb/topics` to populate the sidebar. Each topic object includes `name`, `file_count`, `last_updated`, and the frontend derives summary count from scanning `processed/` folder metadata.

- **FR-2: Topic Detail Loading** — When a topic is selected, the frontend MUST call `GET /api/kb/topics/<name>` for metadata and read the latest `summary-vN.md` file content for display.

- **FR-3: Summary Markdown Rendering** — Summary markdown MUST be rendered to HTML with styled headings (h4 with icons), lists, code blocks, blockquotes, and highlighted spans per the design system.

- **FR-4: Version Switching** — The frontend MUST support loading any available summary version by reading `summary-vN.md` from the topic's `processed/` directory.

- **FR-5: Reprocess Flow** — Reprocess triggers `POST /api/kb/process` → confirms automatically → refreshes summary card and version history.

- **FR-6: File Upload to Topic** — "Add Knowledge" uploads files via `POST /api/kb/upload` with topic-scoped path, then optionally triggers reprocessing.

## Non-Functional Requirements

- **NFR-1: Performance** — Topic sidebar MUST load within 500ms. Summary card rendering MUST complete within 300ms for summaries up to 50KB.
- **NFR-2: Responsiveness** — Content body padding adjusts at viewport < 1200px (24px → 16px per mockup @media query).
- **NFR-3: Accessibility** — All interactive elements MUST be keyboard-navigable. Topic items MUST be focusable with Enter/Space activation.
- **NFR-4: Consistency** — All colors, fonts, spacing MUST follow the existing KB design system (CSS variables from `--bg-primary`, `--accent-primary`, etc.).
- **NFR-5: No Breaking Changes** — Existing KB landing zone (FEATURE-025-B) functionality MUST remain unaffected.

## UI/UX Requirements

### Layout (from mockup)

- **Sidebar** (280px width): Topics list with header ("Topics" title + "+" add button), scrollable topic items
- **Content Panel** (flex: 1): Header with title/badge/actions/stats → scrollable body with summary card, knowledge graph preview, source files
- **Terminal Footer** (36px): "Console" and "KB Manager Logs" tabs

### Component Inventory

1. **Topic List Item:** icon (colored by topic), name, meta text, badge count
2. **Topic Stats Row:** 4 stat items (icon + value + label)
3. **Summary Card:** header (icon + title + version badge), body (markdown content + source refs), version history timeline
4. **Knowledge Graph Preview:** header + SVG canvas with nodes and connecting lines
5. **Source File Item:** file-type icon, file name, metadata, hover action buttons (View/Download)
6. **Action Buttons:** "Reprocess" (ghost), "Add Knowledge" (primary)

### States

| Component | States |
|-----------|--------|
| Topic Item | default, hover, active (selected) |
| Summary Card | loaded, empty (no summary), loading (reprocessing) |
| Source File Item | default, hover |
| Version Item | default, hover, current (highlighted) |

### Transitions

- Topic selection: sidebar highlight + content panel update (no page reload)
- Version switching: summary card content swap with fade
- Reprocess: loading spinner overlay on summary card → new content

## Dependencies

### Internal

| Dependency | Feature | Status | Integration Point |
|------------|---------|--------|-------------------|
| KB Core Infrastructure | FEATURE-025-A | Completed | File index, folder structure, `kb-core.js` |
| KB Landing Zone | FEATURE-025-B | Complete | Upload API, landing view, `kb-landing.js` |
| KB Manager Skill | FEATURE-025-C | Complete | Process/classify/search APIs, summary generation |
| Topics API | FEATURE-025-A | Completed | `GET /api/kb/topics`, `GET /api/kb/topics/<name>` |

### External

- Bootstrap Icons (already loaded in project)
- Existing CSS design system variables (already defined)

## Business Rules

- **BR-1:** A topic with zero files SHOULD still appear in the sidebar (may have been emptied by reorganization).
- **BR-2:** Summary versions are immutable — reprocessing creates a new version, never overwrites.
- **BR-3:** Version history displays up to 5 most recent versions. Older versions remain on disk but are not shown.
- **BR-4:** The "Add Knowledge" upload scopes files to the selected topic's `raw/` directory.
- **BR-5:** Breadcrumb updates to show "Workplace / Knowledge Base / {topic-name}" when a topic is selected.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| No topics exist | Show empty state in sidebar and content panel |
| Topic has files but no summaries | Show source files section, summary card shows empty state with "Reprocess" CTA |
| Topic has summaries but all files deleted | Summary card still shows last generated summary; source files section shows empty |
| Summary markdown contains unsupported elements | Render as plain text (graceful degradation) |
| Reprocess fails (LLM error) | Show error toast, keep existing summary, no version increment |
| Multiple rapid topic clicks | Cancel any pending content load, show latest clicked topic |
| Very long summary (>50KB) | Scrollable content body handles it; no truncation |
| Topic name with special characters | URL-encode topic name in API calls |

## Out of Scope

- **Full knowledge graph visualization** — Only preview with "Expand" placeholder (Phase 2: FEATURE-025-F or later)
- **Inline file editing** — View/download only, no editing source files
- **Topic creation from UI** — Topics are created via classification (FEATURE-025-C); "+" button is placeholder
- **Drag-and-drop reordering of topics** — Fixed alphabetical order
- **Summary editing** — Summaries are AI-generated only; no manual editing
- **Search within summaries** — Covered by FEATURE-025-E

## Technical Considerations

- The topics sidebar and summary view need a new JavaScript module (`kb-topics.js`) that integrates with existing `kb-core.js`
- Summary markdown rendering needs an HTML sanitizer to prevent XSS from AI-generated content
- Version switching should cache loaded summaries to avoid repeated API calls
- The `GET /api/kb/topics/<name>` endpoint may need enhancement to return summary metadata (versions list with dates)
- Consider a new API endpoint for reading summary content by version: `GET /api/kb/topics/<name>/summary?version=N`
- Source file size/metadata may need to be derived from file index rather than filesystem stat calls

## Open Questions

1. ~~Should the "+" button in topic sidebar create a new empty topic, or is it deferred?~~ → Deferred (Out of Scope)
2. Should clicking a source file "View" button navigate to the content viewer (FEATURE-002) or show inline preview?
3. Should the knowledge graph preview show actual related topics from the data, or static placeholder for Phase 2?
