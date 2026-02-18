# Idea Summary

> Idea ID: IDEA-023
> Folder: 023. CR-Compose Idea in Workflow
> Version: v1
> Created: 2026-02-18
> Status: Refined

## Overview

Replace the current simple prompt-based "Compose Idea" workflow action with a rich modal dialog that supports **creating new ideas** or **linking existing ideas** — all without leaving the workflow view. The modal embeds the full Workplace compose/upload/UIUX-reference tabs for new ideas and a mini file-tree browser with preview for linking existing ones.

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
    D --> F["Compose / Upload / UIUX Ref Tabs"]
    F --> G["Submit Idea"]
    E --> H["Select Idea File"]
    H --> I["Preview Content"]
    I --> J["Confirm Link"]
    G --> K["Auto-generate folder: wf-NNN-name"]
    J --> L["Use existing root folder name"]
    K --> M["Update Deliverables"]
    L --> M
    M --> N["Auto-complete compose_idea action"]
```

### Modal Layout

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
│  │ Compose │ Upload  │ UIUX Ref     │            │
│  ├─────────┴─────────┴──────────────┤            │
│  │                                   │            │
│  │  (Reused Workplace tabs content)  │            │
│  │                                   │            │
│  └───────────────────────────────────┘            │
│                                                   │
│                        [ Cancel ]  [ Submit Idea ]│
└──────────────────────────────────────────────────┘
```

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
- **Tabbed interface** reusing Workplace's Compose / Upload / UIUX Reference tabs
- Compose tab: Markdown text editor (EasyMDE)
- Upload tab: Drag-and-drop file upload zone
- UIUX Reference tab: Design reference capture

### Feature 3: Link Existing Idea
- **Mini file tree** (left panel) mirroring the Workplace sidebar tree
- Fetches from `/api/ideas/tree` API
- **Search/filter** bar at the bottom of the tree
- **Preview panel** (right side) showing read-only rendered content of selected file
- No editing operations (no create, rename, delete, move)

### Feature 4: Auto-Generated Folder Naming
- New ideas: `wf-{NNN}-{sanitized-idea-name}` under `x-ipe-docs/ideas/`
- `NNN` auto-increments from highest existing `wf-XXX` folder
- Linked ideas: use the root folder name (e.g., `003. Feature-Toolbox Design`)

### Feature 5: Dual Deliverables
Two deliverables produced by the compose_idea action:
1. **Idea file** — the new idea file path or the linked idea file path
2. **Idea folder** — `wf-NNN-{name}` for new ideas, or root folder name for linked ideas

### Feature 6: Auto-Complete Workflow Action
- After submit/link, the compose_idea action automatically marks as "done"
- Deliverables are immediately visible in the workflow stage view
- Workflow can auto-advance to the next action

## Success Criteria

- [ ] Modal opens when clicking "Compose Idea" in workflow stage
- [ ] Toggle between "Create New" and "Link Existing" modes works
- [ ] "Create New" embeds the full Compose/Upload/UIUX Reference tabs
- [ ] "Link Existing" shows mini file tree with search and preview
- [ ] Idea name validation enforces < 10 words
- [ ] New idea folders follow `wf-NNN-{sanitized-name}` convention
- [ ] Linked ideas use root folder name as deliverable folder
- [ ] compose_idea action auto-completes with correct deliverables
- [ ] Deliverables appear in workflow stage view after submit
- [ ] No navigation away from workflow view required

## Constraints & Considerations

- **Reuse existing components** — The Compose/Upload/UIUX Reference tabs must reuse the same logic from `workplace.js` (setupComposer, setupUploader, UIUX reference tab)
- **Modal size** — Must be large enough to comfortably edit markdown and browse files (~80% viewport width, ~70% viewport height)
- **Performance** — File tree loading should use the existing `/api/ideas/tree` API with lazy loading
- **File preview** — Markdown rendering should use the same renderer already in the app
- **Keyboard support** — Enter to submit, Escape to cancel, consistent with existing modal patterns
- **EasyMDE cleanup** — Must properly destroy EasyMDE instances when modal closes to avoid memory leaks

## Brainstorming Notes

Key decisions made during brainstorming:

1. **Modal scope**: Full modal with embedded compose/upload tabs — no navigation away from workflow
2. **Mode selection**: Top bar toggle buttons `[Create New] / [Link Existing]`
3. **Link existing UI**: Mini file tree (like sidebar) + read-only preview panel on right side
4. **Folder naming**: Auto-generated `wf-{NNN}-{sanitized-idea-name}` with auto-increment
5. **Numbering**: Auto-increment from highest existing `wf-XXX` folder in ideas directory
6. **Auto-complete**: Yes — after submit, action auto-completes and deliverables appear
7. **Create new tabs**: Embed the same Compose/Upload/UIUX Reference tabs from Workplace

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
        User->>Modal: Enter idea name
        User->>Modal: Compose/Upload/UIUX Ref content
        User->>Modal: Click "Submit Idea"
        Modal->>API: POST /api/ideas/upload (folder: wf-NNN-name)
        API->>FS: Create folder & save files
        API-->>Modal: Success + file path
    else Link Existing Idea
        User->>Modal: Select "Link Existing" toggle
        Modal->>API: GET /api/ideas/tree
        API-->>Modal: Idea folder tree
        User->>Modal: Browse & select idea file
        Modal->>API: GET /api/ideas/content (preview)
        API-->>Modal: File content for preview
        User->>Modal: Click "Link Idea"
    end

    Modal->>API: POST /api/workflow/{name}/link-idea
    Modal->>API: POST /api/workflow/{name}/action (compose_idea: done)
    API-->>Modal: Deliverables updated
    Modal->>WF: Close modal, refresh stage view
    WF->>User: Show updated deliverables
```

## Architecture Context

```architecture-dsl
view: module
title: Compose Idea Modal — Module View

layer UI {
  [Compose Idea Modal] {
    desc: Full-screen modal with toggle, tabs, tree, preview
    tech: JavaScript, HTML, CSS
  }
  [Workflow Stage View] {
    desc: Existing workflow stage renderer
    tech: workflow-stage.js
  }
  [Workplace Components] {
    desc: Reused Compose/Upload/UIUX tabs
    tech: workplace.js
  }
}

layer API {
  [Ideas API] {
    desc: /api/ideas/tree, /api/ideas/upload, /api/ideas/content
    tech: Flask, ideas_routes.py
  }
  [Workflow API] {
    desc: /api/workflow/{name}/link-idea, /api/workflow/{name}/action
    tech: Flask, workflow_routes.py
  }
}

layer Service {
  [Workflow Manager] {
    desc: State machine, deliverables, action tracking
    tech: workflow_manager_service.py
  }
  [Ideas Service] {
    desc: File management, tree building
    tech: ideas service
  }
}

Compose Idea Modal -> Ideas API
Compose Idea Modal -> Workflow API
Workflow Stage View -> Compose Idea Modal
Compose Idea Modal -> Workplace Components
Ideas API -> Ideas Service
Workflow API -> Workflow Manager
```

## Source Files

- new idea.md (original raw idea)

## Next Steps

- [ ] Proceed to Idea Mockup (create visual prototype of the modal)
- [ ] Or proceed to Requirement Gathering (formalize as CR for existing workflow feature)

## References & Common Principles

### Applied Principles

- **Modal Dialog UX Best Practices** — Large modals for complex tasks should maintain context, support keyboard navigation, and have clear primary/secondary actions
- **Component Reuse (DRY)** — Compose/Upload tabs are reused from Workplace to avoid code duplication
- **Progressive Disclosure** — Toggle between "Create New" and "Link Existing" reduces cognitive load by showing only relevant options
- **Consistent Naming Convention** — `wf-NNN-{name}` provides predictable, sortable folder names
