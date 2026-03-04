# Idea Summary

> Idea ID: IDEA-023
> Folder: 023. CR-Compose Idea in Workflow
> Version: v2.1
> Created: 2026-02-18
> Status: Mockup Ready

## Overview

Replace the current simple prompt-based "Compose Idea" workflow action with a rich modal dialog that supports **creating new ideas** or **linking existing ideas** — all without leaving the workflow view. The modal embeds the Workplace compose/upload tabs for new ideas and a mini file-tree browser with preview for linking existing ones.

## Problem Statement

Currently, clicking "Compose Idea" in the workflow opens a basic text prompt asking for a folder name, then navigates away to the Workplace tab. This creates a disjointed experience:

1. **Context switching** — Users lose the workflow context when redirected to Workplace
2. **No link-existing option** — Users cannot link an already-composed idea to the workflow
3. **No preview** — Users cannot see what they're linking before committing
4. **Poor folder naming** — Manual folder naming without consistent convention

## Target Users

- X-IPE users who run engineering workflows and need to compose or attach ideas as the first step of the ideation stage

## Proposed Solution

A **full-featured modal dialog** that opens when clicking "Compose Idea" in the workflow stage view:

```mermaid
flowchart TD
    A["Click 'Compose Idea'"] --> B["Open Modal Dialog"]
    B --> C{"Top Bar Toggle"}
    C -->|"Create New"| D["Name Input < 10 words"]
    C -->|"Link Existing"| E["Mini File Tree + Preview"]
    D --> F["Compose / Upload Tabs"]
    F --> G["Submit Idea"]
    E --> H["Select Idea File"]
    H --> I["Preview Content"]
    I --> J["Confirm Link"]
    G --> K["Auto-generate folder: wf-NNN-name"]
    J --> L["Use existing root folder name"]
    K --> M["Update Deliverables"]
    L --> M
    M --> N["Auto-complete compose_idea action"]
    N --> O{"Error?"}
    O -->|No| P["Close modal, refresh stage"]
    O -->|Yes| Q["Show error toast, keep modal open"]
```

### Modal Layout — Create New Mode

```
┌──────────────────────────────────────────────────┐
│  Compose Idea                              [  ×  ]│
├──────────────────────────────────────────────────┤
│  [ Create New ●]  [ Link Existing ]              │
├──────────────────────────────────────────────────┤
│                                                   │
│  Idea Name: [________________________] < 10 words │
│                                                   │
│  ┌─────────┬─────────┬──────────────┐            │
│  │ Compose │ Upload  │                    │
│  ├─────────┴─────────┴──────────────┤            │
│  │                                   │            │
│  │  (Reused Workplace tabs content)  │            │
│  │                                   │            │
│  └───────────────────────────────────┘            │
│                                                   │
│                        [ Cancel ]  [ Submit Idea ]│
└──────────────────────────────────────────────────┘
```

### Modal Layout — Link Existing Mode

```
┌──────────────────────────────────────────────────┐
│  Compose Idea                              [  ×  ]│
├──────────────────────────────────────────────────┤
│  [ Create New ]  [ Link Existing ●]              │
├──────────────────────────────────────────────────┤
│  ┌──────────────┬─────────────────────────┐      │
│  │ 📁 001.      │                         │      │
│  │ 📁 002.      │  Preview of selected    │      │
│  │ 📁 003.      │  idea file content      │      │
│  │  └ 📄 idea.. │                         │      │
│  │ 📁 004.      │  (read-only markdown    │      │
│  │ ...          │   rendered view)         │      │
│  │              │                         │      │
│  │ [🔍 Search]  │                         │      │
│  └──────────────┴─────────────────────────┘      │
│                                                   │
│                        [ Cancel ]  [ Link Idea  ] │
└──────────────────────────────────────────────────┘
```

## Key Features

### Feature 1: Toggle Mode Selection
- Top bar with **[Create New]** / **[Link Existing]** toggle buttons
- Switches the entire content area below based on selection
- Default mode: "Create New"

### Feature 2: Create New Idea
- **Name input** field (max 10 words) — required before submit
- **Tabbed interface** reusing Workplace's Compose / Upload tabs
- Compose tab: Markdown text editor (EasyMDE)
- Upload tab: Drag-and-drop file upload zone
- **Note:** `setupComposer()` and `setupUploader()` in workplace.js currently use hardcoded DOM IDs (e.g., `#workplace-submit-idea`, `#workplace-compose-textarea`). These must be refactored to accept a container element parameter, enabling reuse in both the Workplace page and this modal.

### Feature 3: Link Existing Idea
- **Mini file tree** (left panel) mirroring the Workplace sidebar tree
- Fetches from `/api/ideas/tree` API (already exists)
- **Search/filter** bar: client-side filtering on folder and file names (reuse existing `/api/ideas/search` endpoint if available, otherwise client-side filter on the loaded tree)
- **Preview panel** (right side) showing read-only rendered content of selected file
- Preview fetched via `/api/ideas/download` endpoint (already exists) — rendered using the app's existing markdown renderer (marked.js or EasyMDE preview)
- **Granularity:** User selects a specific **file** within an idea folder; the deliverable records both the file path and its root folder name
- No editing operations (no create, rename, delete, move)

### Feature 4: Auto-Generated Folder Naming
- New ideas: `wf-{NNN}-{sanitized-idea-name}` under `x-ipe-docs/ideas/`
- `NNN` auto-increments from highest existing `wf-XXX` folder (scan `x-ipe-docs/ideas/wf-*` folders)
- Linked ideas: use the root folder name (e.g., `003. Feature-Toolbox Design`)
- **Sanitization rules:** lowercase, replace spaces with hyphens, strip non-alphanumeric characters except hyphens, max 50 chars
- **Coexistence:** `wf-` folders coexist with numbered folders in the ideas directory; tree sorting places them after numbered folders

### Feature 5: Dual Deliverables
Two deliverables produced by the compose_idea action:
1. **Idea file** — the new idea file path or the linked idea file path
2. **Idea folder** — `wf-NNN-{name}` for new ideas, or root folder name for linked ideas

### Feature 6: Auto-Complete Workflow Action
- After submit/link, the compose_idea action automatically marks as "done"
- Deliverables are immediately visible in the workflow stage view
- Workflow can auto-advance to the next action

### Feature 7: Error Handling
- **Folder creation failure** (name collision, disk error): show error toast in modal, keep modal open, user can retry
- **Workflow action update failure** after file save: show warning that files were saved but workflow status failed, suggest manual refresh
- **Modal closed mid-upload**: cancel in-flight requests, no partial files saved (or clean up temp files)
- **Empty/invalid idea name**: inline validation error, prevent submit

## Success Criteria

- [ ] Modal opens when clicking "Compose Idea" in workflow stage
- [ ] Toggle between "Create New" and "Link Existing" modes works
- [ ] "Create New" embeds the full Compose/Upload tabs
- [ ] "Link Existing" shows mini file tree with search and preview
- [ ] Idea name validation enforces < 10 words
- [ ] Name sanitization produces valid folder names (lowercase, hyphens, max 50 chars)
- [ ] New idea folders follow `wf-NNN-{sanitized-name}` convention
- [ ] Linked ideas use root folder name as deliverable folder
- [ ] compose_idea action auto-completes with correct deliverables
- [ ] Deliverables appear in workflow stage view after submit
- [ ] No navigation away from workflow view required
- [ ] EasyMDE instances properly destroyed on modal close (no memory leaks)
- [ ] Error states handled gracefully (folder collision, API failure, mid-upload cancel)

## Constraints & Considerations

- **Reuse existing components** — Refactor `setupComposer()`/`setupUploader()` to accept container element parameter instead of hardcoded DOM IDs
- **Existing APIs** — Leverage `/api/ideas/tree`, `/api/ideas/upload`, `/api/ideas/download`, `/api/workflow/{name}/link-idea`, `/api/workflow/{name}/action` — no new endpoints except possibly a content-preview endpoint (or reuse `/api/ideas/download`)
- **Modal size** — ~80% viewport width, ~70% viewport height to comfortably edit markdown and browse files
- **Performance** — File tree uses existing `/api/ideas/tree` with lazy loading
- **Keyboard support** — Enter to submit, Escape to cancel, consistent with existing modal patterns
- **EasyMDE cleanup** — Must properly destroy instances when modal closes
- **`wf-` folder naming** — These are permanent; renaming to numbered convention is a separate manual operation (standard rename in Ideas tab)

## Brainstorming Notes

Key decisions made during brainstorming:

1. **Modal scope**: Full modal with embedded compose/upload tabs — no navigation away from workflow
2. **Mode selection**: Top bar toggle buttons `[Create New] / [Link Existing]`
3. **Link existing UI**: Mini file tree (like sidebar) + read-only preview panel on right side
4. **Folder naming**: Auto-generated `wf-{NNN}-{sanitized-idea-name}` with auto-increment
5. **Numbering**: Auto-increment from highest existing `wf-XXX` folder in ideas directory
6. **Auto-complete**: Yes — after submit, action auto-completes and deliverables appear
7. **Create new tabs**: Embed the same Compose/Upload tabs from Workplace

## User Flow Diagram

```mermaid
sequenceDiagram
    actor User
    participant WF as Workflow Stage View
    participant Modal as Compose Idea Modal
    participant API as Backend API
    participant FS as File System

    User->>WF: Click "Compose Idea"
    WF->>Modal: Open modal dialog

    alt Create New Idea
        User->>Modal: Select "Create New" toggle
        User->>Modal: Enter idea name (< 10 words)
        User->>Modal: Compose/Upload content
        User->>Modal: Click "Submit Idea"
        Modal->>API: POST /api/ideas/upload (folder: wf-NNN-name)
        API->>FS: Create folder & save files
        API-->>Modal: Success + file path
    else Link Existing Idea
        User->>Modal: Select "Link Existing" toggle
        Modal->>API: GET /api/ideas/tree
        API-->>Modal: Idea folder tree
        User->>Modal: Browse & select idea file
        Modal->>API: GET /api/ideas/download (preview)
        API-->>Modal: File content for preview
        User->>Modal: Click "Link Idea"
    end

    Modal->>API: POST /api/workflow/{name}/link-idea
    API-->>Modal: Idea folder linked

    Modal->>API: POST /api/workflow/{name}/action (compose_idea: done, deliverables)
    API-->>Modal: Action updated

    alt Success
        Modal->>WF: Close modal, refresh stage view
        WF->>User: Show updated deliverables
    else API Error
        Modal->>User: Show error toast, keep modal open
    end
```

## Architecture Context

```architecture-dsl
@startuml module-view
title "Compose Idea Modal — Module View"
theme "theme-default"
direction top-to-bottom
grid 12 x 6

layer "UI" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 2

  module "Compose Idea Modal" {
    cols 5
    rows 2
    grid 1 x 1
    align center center
    gap 8px
    component "Toggle / Tabs / Tree / Preview" { cols 1, rows 1 }
  }

  module "Workflow Stage View" {
    cols 4
    rows 2
    grid 1 x 1
    align center center
    gap 8px
    component "workflow-stage.js" { cols 1, rows 1 }
  }

  module "Workplace Components" {
    cols 3
    rows 2
    grid 1 x 1
    align center center
    gap 8px
    component "workplace.js" { cols 1, rows 1 }
  }
}

layer "API" {
  color "#fef9c3"
  border-color "#eab308"
  rows 2

  module "Ideas API" {
    cols 6
    rows 2
    grid 3 x 1
    align center center
    gap 8px
    component "/api/ideas/tree" { cols 1, rows 1 }
    component "/api/ideas/upload" { cols 1, rows 1 }
    component "/api/ideas/download" { cols 1, rows 1 }
  }

  module "Workflow API" {
    cols 6
    rows 2
    grid 2 x 1
    align center center
    gap 8px
    component "/api/workflow/link-idea" { cols 1, rows 1 }
    component "/api/workflow/action" { cols 1, rows 1 }
  }
}

layer "Service" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 2

  module "Workflow Manager" {
    cols 6
    rows 2
    grid 1 x 1
    align center center
    gap 8px
    component "workflow_manager_service.py" { cols 1, rows 1 }
  }

  module "Ideas Service" {
    cols 6
    rows 2
    grid 1 x 1
    align center center
    gap 8px
    component "ideas_routes.py" { cols 1, rows 1 }
  }
}

@enduml
```

## Mockups & Prototypes

| Mockup | Description | File |
|--------|-------------|------|
| Compose Idea Modal | Interactive HTML prototype showing both Create New and Link Existing modes with tab navigation, file tree browser, and markdown preview | [compose-idea-modal-v1.html](x-ipe-docs/ideas/023. CR-Compose Idea in Workflow/mockups/compose-idea-modal-v1.html) |

### Mockup Coverage

- ✅ **Create New mode** — Idea name input with word counter, Compose/Upload tabs, rich text editor toolbar
- ✅ **Link Existing mode** — Searchable file tree sidebar, markdown preview panel, file selection highlighting
- ✅ **Top-bar toggle** — Create New / Link Existing pill-style toggle
- ✅ **Modal chrome** — Header, close button, Cancel/Create action buttons
- ✅ **Brand theme** — Uses X-IPE design system (Slate/Emerald palette, DM Sans typography)

## Source Files

- new idea.md (original raw idea)

## Next Steps

- [x] Proceed to Idea Mockup (create visual prototype of the modal)
- [ ] Proceed to Requirement Gathering (formalize as CR for existing workflow feature)

## References & Common Principles

### Applied Principles

- **Modal Dialog UX Best Practices** — Large modals for complex tasks should maintain context, support keyboard navigation, and have clear primary/secondary actions
- **Component Reuse (DRY)** — Compose/Upload tabs are reused from Workplace via parameterized container refactoring
- **Progressive Disclosure** — Toggle between "Create New" and "Link Existing" reduces cognitive load
- **Consistent Naming Convention** — `wf-NNN-{name}` provides predictable, sortable folder names
- **Graceful Error Handling** — Modal stays open on error, allowing retry without data loss

### Critique Feedback Addressed

| # | Feedback | Resolution |
|---|----------|------------|
| 1 | No `/api/ideas/content` endpoint | Changed to `/api/ideas/download` (existing endpoint) |
| 2 | WorkplaceManager methods use hardcoded DOM IDs | Added refactoring note: parameterize container element |
| 3 | `wf-NNN` coexistence with numbered folders | Clarified sort order and coexistence in Feature 4 |
| 4 | Missing error handling flows | Added Feature 7: Error Handling + error alt in sequence diagram |
| 5 | Search/filter behavior unspecified | Specified client-side filter on folder/file names in Feature 3 |
| 6 | Existing `link-idea` API not acknowledged | Referenced existing endpoint in Constraints section |
| 7 | Sanitization rules undefined | Added explicit rules in Feature 4 |
| 8 | EasyMDE cleanup not a success criterion | Added as success criterion |
| Q1 | File vs folder linking granularity | Clarified: select file, deliverable records both file + root folder |
| Q2 | reference_uiux independence | Removed: UIUX Reference tab is not part of compose_idea modal — it remains a separate workflow action |
| Q3 | `wf-NNN` naming reversibility | Clarified: permanent, rename is separate manual operation |
| Q4 | Markdown renderer for preview | Specified: app's existing renderer (marked.js / EasyMDE preview) |
