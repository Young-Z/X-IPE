# Feature Specification: Project Quality Evaluation UI

> Feature ID: FEATURE-024  
> Version: v1.1  
> Status: Implemented  
> Last Updated: 02-02-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.1 | 02-02-2026 | Updated AC status - backend implemented, version timeline UI complete |
| v1.0 | 02-01-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| Quality Evaluation View | HTML | [quality-evaluation.html](mockups/quality-evaluation.html) | Full UI mockup with action bar, version timeline, and preview |

> **Note:** UI/UX requirements below are derived from these mockups.

## Overview

The Project Quality Evaluation UI feature provides a dedicated interface within the X-IPE Workplace for viewing, managing, and acting on project quality evaluations. This feature transforms quality evaluation from an informal file-based workflow into a first-class UI experience with proper navigation, action controls, and version history.

Users can trigger quality evaluations via Copilot, view styled markdown reports, compare historical evaluations, and execute targeted refactoring actions—all from a single integrated view. The feature integrates with the existing console and Copilot prompt system to provide seamless developer experience.

This feature addresses the need for formal quality gate management in software projects, enabling developers to track code health over time and take systematic action on identified gaps.

## User Stories

1. As a **developer**, I want to **view my project's quality evaluation in a styled format**, so that **I can quickly understand the health of my codebase**.

2. As a **developer**, I want to **trigger a new quality evaluation with one click**, so that **I don't have to remember command syntax**.

3. As a **developer**, I want to **execute targeted refactoring actions based on evaluation gaps**, so that **I can systematically improve code quality**.

4. As a **developer**, I want to **compare current evaluation with previous versions**, so that **I can track quality improvements over time**.

5. As a **team lead**, I want to **customize refactoring prompts**, so that **the actions match our team's workflow and standards**.

## Acceptance Criteria

### AC-1: Sidebar Integration

| # | Criterion | Priority |
|---|-----------|----------|
| AC-1.1 | "Project Quality Evaluation" submenu MUST appear under Workplace section in sidebar | Must |
| AC-1.2 | Submenu MUST use Bootstrap icon `bi-clipboard-check` | Must |
| AC-1.3 | Submenu MUST always be visible regardless of evaluation file existence | Must |
| AC-1.4 | Clicking submenu MUST load Quality Evaluation view in content area | Must |
| AC-1.5 | Submenu MUST show active state when Quality Evaluation view is displayed | Must |

### AC-2: Empty State

| # | Criterion | Priority |
|---|-----------|----------|
| AC-2.1 | When no evaluation file exists, view MUST display empty state UI | Must |
| AC-2.2 | Empty state MUST show centered icon `bi-clipboard-check` in circular container | Must |
| AC-2.3 | Empty state MUST display title: "No Evaluation Yet" | Must |
| AC-2.4 | Empty state MUST display description encouraging first evaluation | Must |
| AC-2.5 | Empty state MUST include prominent CTA button: "Evaluate Project Quality" | Must |
| AC-2.6 | Clicking CTA MUST open console with evaluate prompt from config | Must |

### AC-3: Content View with Data

| # | Criterion | Priority |
|---|-----------|----------|
| AC-3.1 | When evaluation file exists, view MUST show action bar at top | Must |
| AC-3.2 | View MUST show version timeline below action bar | Must |
| AC-3.3 | View MUST render evaluation markdown as styled readonly preview | Must |
| AC-3.4 | Markdown preview MUST support tables, lists, code blocks, and headings | Must |
| AC-3.5 | Preview MUST be scrollable when content exceeds viewport | Must |

### AC-4: Action Bar

| # | Criterion | Priority |
|---|-----------|----------|
| AC-4.1 | Action bar MUST display "Refactoring" dropdown button with chevron | Must |
| AC-4.2 | Action bar MUST display "Evaluate" primary button | Must |
| AC-4.3 | Both buttons MUST be right-aligned in action bar | Must |
| AC-4.4 | "Refactoring" MUST be positioned left of "Evaluate" | Must |
| AC-4.5 | Action bar MUST have light background to distinguish from content | Should |

### AC-5: Refactoring Dropdown

| # | Criterion | Priority |
|---|-----------|----------|
| AC-5.1 | Refactoring button MUST NOT execute action on direct click | Must |
| AC-5.2 | Dropdown menu MUST appear on hover (not click) | Must |
| AC-5.3 | Dropdown options MUST be loaded from `copilot-prompt.json` → `evaluation.refactoring[]` | Must |
| AC-5.4 | Each option MUST display icon and label from config | Must |
| AC-5.5 | Clicking any option MUST open console with configured command | Must |
| AC-5.6 | Dropdown MUST support visual dividers between option groups | Should |
| AC-5.7 | Dropdown MUST close when mouse leaves dropdown area | Should |

### AC-6: Evaluate Button

| # | Criterion | Priority |
|---|-----------|----------|
| AC-6.1 | Clicking Evaluate MUST open console with evaluate command | Must |
| AC-6.2 | Command MUST be loaded from `copilot-prompt.json` → `evaluation.evaluate.command` | Must |
| AC-6.3 | Button MUST have primary/accent styling (teal fill) | Should |
| AC-6.4 | Button MUST show icon `bi-clipboard-check` with label | Should |

### AC-7: Version Timeline

| # | Criterion | Priority |
|---|-----------|----------|
| AC-7.1 | Timeline MUST display as horizontal tabs below action bar | Must |
| AC-7.2 | Timeline MUST show up to 5 most recent evaluation versions | Must |
| AC-7.3 | Most recent version MUST appear on the left (first position) | Must |
| AC-7.4 | Each tab MUST display version number (e.g., "v5") | Must |
| AC-7.5 | Each tab MUST display abbreviated date (e.g., "Feb 1") | Must |
| AC-7.6 | Active version MUST have visual indicator (underline/border) | Must |
| AC-7.7 | Clicking a tab MUST load that version's markdown content | Must |
| AC-7.8 | If fewer than 5 versions exist, MUST only show existing versions | Must |

### AC-8: File Storage & Versioning

| # | Criterion | Priority |
|---|-----------|----------|
| AC-8.1 | Evaluation files MUST be stored in `x-ipe-docs/quality-evaluation/` folder | Must |
| AC-8.2 | Latest evaluation MUST be named `project-quality-evaluation.md` | Must |
| AC-8.3 | Historical versions MUST be named `project-quality-evaluation-vN.md` | Must |
| AC-8.4 | System MUST retain maximum 5 versions | Should |
| AC-8.5 | When creating new evaluation, current MUST be versioned first | Must |
| AC-8.6 | Oldest version MUST be deleted when exceeding 5 versions | Should |

### AC-9: Config File Structure

| # | Criterion | Priority |
|---|-----------|----------|
| AC-9.1 | `copilot-prompt.json` MUST support top-level `ideation` and `evaluation` sections | Must |
| AC-9.2 | Existing ideation prompts MUST continue working after restructure | Must |
| AC-9.3 | `evaluation.evaluate` MUST contain label, icon, and command | Must |
| AC-9.4 | `evaluation.refactoring` MUST be array of prompt objects | Must |
| AC-9.5 | Each refactoring prompt MUST have id, label, icon, and command | Must |
| AC-9.6 | `placeholder.evaluation-file` MUST be defined for runtime substitution | Must |

### AC-10: Placeholder Resolution

| # | Criterion | Priority |
|---|-----------|----------|
| AC-10.1 | `<evaluation-file>` placeholder MUST be replaced at runtime | Must |
| AC-10.2 | Placeholder MUST resolve to current evaluation file path | Must |
| AC-10.3 | When viewing historical version, placeholder SHOULD resolve to that version | Should |

## Functional Requirements

### FR-1: Sidebar Menu Registration

**Description:** Register new submenu item in Workplace section

**Details:**
- Input: None (static registration)
- Process: Add menu item during sidebar initialization
- Output: Clickable menu item that loads Quality Evaluation view

**Implementation Notes:**
- Follow existing Workplace submenu pattern (Ideas, Requirements, etc.)
- Use `bi-clipboard-check` icon
- Register click handler to load quality evaluation content

### FR-2: Quality Evaluation View Loading

**Description:** Load and display the Quality Evaluation view based on file existence

**Details:**
- Input: User clicks "Project Quality Evaluation" submenu
- Process:
  1. Check if `x-ipe-docs/quality-evaluation/project-quality-evaluation.md` exists
  2. If exists: Load content view with action bar, timeline, preview
  3. If not exists: Load empty state view
- Output: Appropriate view rendered in content area

### FR-3: Markdown Preview Rendering

**Description:** Render evaluation markdown as styled readonly preview

**Details:**
- Input: Markdown content from evaluation file
- Process: Parse and render markdown with styling
- Output: Styled HTML preview matching X-IPE design system

**Supported Elements:**
- Headings (h1-h6)
- Tables with borders and hover
- Ordered/unordered lists
- Code blocks with syntax highlighting
- Inline code
- Bold/italic text

### FR-4: Version Timeline Loading

**Description:** Load and display available evaluation versions

**Details:**
- Input: None (scans folder on load)
- Process:
  1. Scan `x-ipe-docs/quality-evaluation/` for evaluation files
  2. Parse version numbers from filenames
  3. Sort by version (newest first)
  4. Limit to 5 most recent
  5. Extract dates from file metadata or content
- Output: Array of version objects with number and date

### FR-5: Version Switching

**Description:** Switch displayed content when user clicks version tab

**Details:**
- Input: Version tab click event
- Process:
  1. Determine file path for selected version
  2. Load markdown content
  3. Re-render preview
  4. Update active tab indicator
- Output: Updated preview showing selected version

### FR-6: Refactoring Dropdown Population

**Description:** Dynamically populate refactoring dropdown from config

**Details:**
- Input: None (reads config on load)
- Process:
  1. Read `x-ipe-docs/config/copilot-prompt.json`
  2. Parse `evaluation.refactoring` array
  3. Build dropdown items with icons and labels
  4. Attach click handlers with command templates
- Output: Populated dropdown menu

### FR-7: Console Command Execution

**Description:** Open console with pre-populated command when action clicked

**Details:**
- Input: Button/option click with command template
- Process:
  1. Get command template from config
  2. Replace `<evaluation-file>` placeholder with actual path
  3. Open/focus console
  4. Populate command input
  5. Optionally auto-submit (based on UX decision)
- Output: Console open with command ready

### FR-8: File Versioning on New Evaluation

**Description:** Version existing file before creating new evaluation

**Details:**
- Input: New evaluation content (from Copilot)
- Process:
  1. If `project-quality-evaluation.md` exists:
     - Determine next version number
     - Rename to `project-quality-evaluation-vN.md`
  2. Save new content as `project-quality-evaluation.md`
  3. If more than 5 versions: delete oldest
- Output: Updated file structure with versioning

### FR-9: Config File Migration

**Description:** Restructure copilot-prompt.json to support both ideation and evaluation

**Details:**
- Input: Existing copilot-prompt.json (v1.0 format)
- Process:
  1. Read existing config
  2. Wrap existing prompts in `ideation.prompts`
  3. Add `evaluation` section with defaults
  4. Update version to 2.0
  5. Save restructured config
- Output: Updated config with backward compatibility

## Non-Functional Requirements

### NFR-1: Performance

| Metric | Requirement |
|--------|-------------|
| View load time | < 500ms for initial render |
| Markdown render | < 200ms for typical evaluation file |
| Version switch | < 300ms for tab click response |
| Dropdown appear | < 100ms on hover |

### NFR-2: Accessibility

| Requirement | Details |
|-------------|---------|
| Keyboard navigation | All actions accessible via keyboard |
| Focus management | Proper focus states on interactive elements |
| Screen reader | ARIA labels for buttons and tabs |
| Color contrast | WCAG AA compliance for text |

### NFR-3: Responsiveness

| Breakpoint | Behavior |
|------------|----------|
| Desktop (> 1024px) | Full layout with sidebar visible |
| Tablet (768-1024px) | Collapsible sidebar, full action bar |
| Mobile (< 768px) | Out of scope for v1.0 |

## UI/UX Requirements

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│ Action Bar                    [Refactoring▼] [Evaluate] │
├─────────────────────────────────────────────────────┤
│ Version Timeline: [v5 Feb 1] [v4 Jan 31] [v3] ...   │
├─────────────────────────────────────────────────────┤
│                                                     │
│            Markdown Preview (scrollable)            │
│                                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Color Palette (Quality Theme)

| Element | Color | CSS Variable |
|---------|-------|--------------|
| Primary accent | Teal #0d9488 | --quality-primary |
| Primary hover | #0f766e | --quality-primary-dark |
| Background accent | #f0fdfa | --quality-bg |
| Success metric | #22c55e | --status-good |
| Warning metric | #f59e0b | --status-warn |
| Error metric | #ef4444 | --status-bad |

### Interactive States

| Element | State | Visual Change |
|---------|-------|---------------|
| Refactoring button | Hover | Border color change, light bg |
| Dropdown menu | Appear | Fade in, slide down |
| Dropdown item | Hover | Background highlight |
| Evaluate button | Hover | Darken, subtle lift shadow |
| Version tab | Hover | Text color darken |
| Version tab | Active | Underline indicator |

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-008 | Feature | Workplace framework, sidebar structure, content area |
| Console | System | Console component for command input/execution |
| Markdown Preview | System | Existing markdown rendering capability |

### External Dependencies

| Dependency | Purpose |
|------------|---------|
| Bootstrap Icons | Icon set for buttons and menu items |
| copilot-prompt.json | Configuration source for prompts |

## Business Rules

### BR-1: Version Limit

**Rule:** System maintains maximum 5 evaluation versions
**Enforcement:** When new evaluation would create 6th version, delete oldest

### BR-2: Config Backward Compatibility

**Rule:** Restructured copilot-prompt.json must not break ideation workflow
**Enforcement:** Ideation code reads from `ideation.prompts` array

### BR-3: Folder Auto-Creation

**Rule:** If `x-ipe-docs/quality-evaluation/` doesn't exist, create on first evaluation
**Enforcement:** Check and create folder before file operations

### BR-4: Dropdown Behavior

**Rule:** Refactoring dropdown shows on hover, not click
**Enforcement:** CSS-based hover trigger, no JavaScript click handler on trigger

## Edge Cases & Constraints

### Edge Case 1: No Evaluation Files

**Scenario:** User opens Quality Evaluation view before any evaluation exists
**Expected Behavior:** Display empty state with CTA button

### Edge Case 2: Config File Missing

**Scenario:** copilot-prompt.json doesn't exist or is invalid
**Expected Behavior:** 
- Show action bar with default hardcoded options
- Log warning about missing/invalid config
- Prompt user to create config

### Edge Case 3: Malformed Evaluation File

**Scenario:** Evaluation markdown is corrupted or empty
**Expected Behavior:**
- Display whatever content can be parsed
- Show error message for unparseable sections
- Don't crash the view

### Edge Case 4: File System Permission Error

**Scenario:** Cannot read/write to quality-evaluation folder
**Expected Behavior:**
- Display error message explaining issue
- Suggest permission fix
- Gracefully degrade (show empty state)

### Edge Case 5: Concurrent Evaluation

**Scenario:** User triggers new evaluation while one is in progress
**Expected Behavior:**
- Disable Evaluate button during evaluation
- Show loading indicator
- Re-enable after completion or timeout

## Out of Scope

- **Report Generation:** Quality evaluation content generation (handled by skill/agent)
- **Refactoring Execution:** Actual code refactoring (handled by Copilot)
- **Diff Comparison:** Side-by-side version comparison view
- **Export/Share:** PDF export or sharing functionality
- **Mobile Layout:** Responsive design for mobile devices
- **Custom Themes:** Theming beyond teal accent color
- **Real-time Updates:** Live refresh when files change

## Technical Considerations

### Frontend Architecture

- Extend Workplace JavaScript module
- Use existing event system for view switching
- Leverage existing markdown preview component
- CSS variables for quality-specific theming

### Config Reading

- Read copilot-prompt.json on view load
- Cache config for session (reload on manual refresh)
- Handle missing/malformed config gracefully

### File System Operations

- Use existing file service for reading/writing
- Implement version rotation logic
- Handle path resolution for placeholder substitution

## Open Questions

- [x] ~~Should dropdown appear on hover or click?~~ → Hover
- [x] ~~Position of Refactoring vs Evaluate button?~~ → Refactoring left, Evaluate right
- [x] ~~Version order in timeline?~~ → Newest on left
- [ ] Should clicking empty state CTA auto-submit the command or just populate console?
- [ ] Should version cleanup happen immediately or on next evaluation?

---
