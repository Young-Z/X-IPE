# Feature Specification: Content Viewer

> Feature ID: FEATURE-002  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-18-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 01-18-2026 | Initial specification | - |

## Overview

The Content Viewer feature renders file contents in the main content area when a user selects a file from the sidebar navigation. It supports two primary content types: Markdown documents (rendered as styled HTML with Mermaid diagram support) and code files (displayed with syntax highlighting).

This feature transforms the raw file content into a visually appealing, readable format that enhances the human reviewer's experience when browsing AI-generated project documentation. Markdown files are the primary use case, as AI agents typically generate documentation in Markdown format.

The viewer integrates with FEATURE-001 (Project Navigation) by listening for file selection events and loading the corresponding file content via the backend API.

## User Stories

- As a **human reviewer**, I want to **see markdown files rendered as formatted HTML**, so that **I can read documentation easily without seeing raw markdown syntax**.

- As a **human reviewer**, I want to **see Mermaid diagrams rendered visually**, so that **I can understand flowcharts and sequence diagrams in technical designs**.

- As a **human reviewer**, I want to **see code with syntax highlighting**, so that **I can read code files with proper formatting and colors**.

- As a **human reviewer**, I want to **see the file path of what I'm viewing**, so that **I know which file I'm currently reading**.

## Acceptance Criteria

- [ ] AC-1: Markdown files (.md) render as styled HTML
- [ ] AC-2: Headings, lists, tables, code blocks render correctly
- [ ] AC-3: Mermaid code blocks render as diagrams
- [ ] AC-4: Code files display with syntax highlighting
- [ ] AC-5: Python (.py) files have proper highlighting
- [ ] AC-6: JavaScript (.js) files have proper highlighting
- [ ] AC-7: HTML/CSS files have proper highlighting
- [ ] AC-8: JSON/YAML files have proper highlighting
- [ ] AC-9: Content area shows loading state while fetching
- [ ] AC-10: Error state displayed if file cannot be loaded
- [ ] AC-11: Clean typography with readable font sizes

## Functional Requirements

### FR-1: File Content API

**Description:** Backend API to fetch file content

**Details:**
- Input: Relative file path from project root
- Process: Read file from filesystem, determine type
- Output: File content with metadata

**API Endpoint:** `GET /api/file/content?path=<relative_path>`

**Response Format:**
```json
{
  "path": "x-ipe-docs/planning/task-board.md",
  "content": "# Task Board\n...",
  "type": "markdown",
  "extension": ".md"
}
```

### FR-2: Markdown Rendering

**Description:** Render markdown content as HTML

**Details:**
- Input: Raw markdown string
- Process: Parse markdown, convert to HTML
- Output: Styled HTML content

**Supported Elements:**
- Headings (h1-h6)
- Paragraphs
- Bold, italic, strikethrough
- Links (open in new tab for external)
- Images
- Code blocks (inline and fenced)
- Lists (ordered and unordered)
- Tables
- Blockquotes
- Horizontal rules
- Task lists (checkboxes)

### FR-3: Mermaid Diagram Rendering

**Description:** Render Mermaid code blocks as diagrams

**Details:**
- Input: Code block with language `mermaid`
- Process: Parse Mermaid syntax, render SVG
- Output: Visual diagram

**Supported Diagram Types:**
- Flowcharts
- Sequence diagrams
- Class diagrams
- State diagrams
- Entity relationship diagrams

### FR-4: Code Syntax Highlighting

**Description:** Display code files with syntax highlighting

**Details:**
- Input: Code file content + language
- Process: Apply syntax highlighting
- Output: Colored code display

**Supported Languages:**
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- HTML (.html)
- CSS (.css)
- JSON (.json)
- YAML (.yaml, .yml)
- Markdown (.md) - for code blocks within

### FR-5: Content Area Integration

**Description:** Display rendered content in main area

**Details:**
- Input: File selection event from sidebar
- Process: Fetch content, render based on type
- Output: Updated content area

## Non-Functional Requirements

### NFR-1: Performance

- File content API response: < 500ms for files up to 1MB
- Markdown rendering: < 200ms for typical documents
- Mermaid diagram rendering: < 1s per diagram

### NFR-2: Usability

- Readable font: 16px base, monospace for code
- Line numbers for code files
- Copy button for code blocks
- Responsive content area

## UI/UX Requirements

### Content Area Layout

```
+------------------+------------------------+
|                  | ┌──────────────────┐   |
|     Sidebar      | │ x-ipe-docs/planning/   │   |
|                  | │ task-board.md    │   |
|                  | ├──────────────────┤   |
|                  | │                  │   |
|                  | │ # Task Board     │   |
|                  | │                  │   |
|                  | │ Content here...  │   |
|                  | │                  │   |
|                  | │ ```mermaid       │   |
|                  | │ [DIAGRAM]        │   |
|                  | │ ```              │   |
|                  | │                  │   |
|                  | └──────────────────┘   |
+------------------+------------------------+
```

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Body | System UI | 16px | 400 |
| H1 | System UI | 2rem | 700 |
| H2 | System UI | 1.5rem | 600 |
| Code | Monospace | 14px | 400 |
| Code Block | Monospace | 13px | 400 |

## Dependencies

### Internal Dependencies

- **FEATURE-001:** Provides file selection events and sidebar integration

### External Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| marked.js | Markdown parsing | 9.x |
| highlight.js | Syntax highlighting | 11.x |
| Mermaid.js | Diagram rendering | 10.x |

## Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| File not found | Show "File not found" error message |
| Binary file selected | Show "Cannot display binary file" message |
| Very large file (>1MB) | Show warning, offer to load anyway |
| Invalid Mermaid syntax | Show error message in place of diagram |
| Network error | Show retry button |

## Out of Scope

- File editing (FEATURE-003)
- Auto-refresh on file changes (FEATURE-004)
- PDF rendering
- Image gallery view
- Search within content

## Technical Considerations

- Use marked.js for markdown parsing (fast, well-maintained)
- Use highlight.js for syntax highlighting (wide language support)
- Use Mermaid.js for diagrams (industry standard)
- Lazy-load Mermaid.js (large library, only needed for diagrams)
- Sanitize HTML output to prevent XSS

---
