# Idea Summary v2: Toolbox Expansion

## Overview
Transform the current Ideation Toolbox into a comprehensive **Stage Toolbox** that supports all development stages (Ideation, Requirement, Feature, Quality, Refactoring) with a modern modal UI similar to the Skills modal.

## Problem Statement
The current toolbox is limited to ideation stage only and uses a dropdown/inline UI. As the platform evolves, users need access to tools across multiple development stages in a more organized, scalable interface.

## Proposed Solution

### 1. UI/UX Design

#### Modal Window
- **Trigger**: Top bar icon/button (new location, moved from Workplace)
- **Style**: Dark-themed modal matching Skills modal reference
- **Layout**: Full-height scrollable content area

#### Stage Organization: Accordion Sections
```
┌─────────────────────────────────────────┐
│  🛠️ Stage Toolbox                    ✕  │
├─────────────────────────────────────────┤
│  ▼ Ideation Stage                       │
│    ├─ Ideation                          │
│    │   ☐ antv-infographic               │
│    │   ☐ mermaid                        │
│    ├─ Mockup                            │
│    │   ☑ frontend-design                │
│    └─ Sharing                           │
│        (no tools configured)            │
│                                         │
│  ▶ Requirement Stage (placeholder)      │
│  ▶ Feature Stage (placeholder)          │
│  ▶ Quality Stage (placeholder)          │
│  ▶ Refactoring Stage (placeholder)      │
└─────────────────────────────────────────┘
```

#### Interaction
- **Accordion**: Click stage header to expand/collapse
- **Toggle**: Simple on/off switch for each tool
- **Visual feedback**: Checkmark or toggle switch indicator

### 2. Configuration

#### File Location
- **Old**: `x-ipe-docs/ideas/.ideation-tools.json`
- **New**: `x-ipe-docs/config/tools.json` (project root)

#### Structure: Nested 3-Level Hierarchy
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "ideation": {
        "antv-infographic": false,
        "mermaid": false
      },
      "mockup": {
        "frontend-design": true
      },
      "sharing": {}
    },
    "requirement": {
      "gathering": {},
      "analysis": {}
    },
    "feature": {
      "design": {},
      "implementation": {}
    },
    "quality": {
      "testing": {},
      "review": {}
    },
    "refactoring": {
      "analysis": {},
      "execution": {}
    }
  }
}
```

#### Scope
- **Project-level**: Configuration applies to entire project
- **Location**: `{project_root}/x-ipe-docs/config/tools.json`

### 3. Technical Considerations

#### Backend Changes
- New API endpoint: `GET/POST /api/config/tools`
- Read/write `x-ipe-docs/config/tools.json`
- Migration from old `.ideation-tools.json` format

#### Frontend Changes
- Remove toolbox from Workplace panel
- Add toolbox icon to top bar
- New modal component: `StageToolboxModal`
- Accordion component for stages
- Toggle component for tools

#### Migration Path
1. Auto-detect old `.ideation-tools.json`
2. Migrate to new `x-ipe-docs/config/tools.json` format
3. Preserve existing tool states

### 4. Future Extensibility

#### Placeholder Stages
The following stages are defined but not yet implemented:
- **Requirement Stage**: gathering, analysis phases
- **Feature Stage**: design, implementation phases
- **Quality Stage**: testing, review phases
- **Refactoring Stage**: analysis, execution phases

These placeholders allow the UI to be built now while tools are added incrementally.

## Out of Scope (v1)
- Per-tool configuration/settings
- Idea-level overrides
- Keyboard shortcuts
- Tool search/filter
- Tool descriptions/documentation

## Success Criteria
1. ✅ Modal opens from top bar
2. ✅ All 5 stages visible as accordion sections
3. ✅ Ideation stage tools functional (migrated from old config)
4. ✅ Other stages show as placeholders
5. ✅ Config saved to `x-ipe-docs/config/tools.json`
6. ✅ Existing functionality preserved

## Questions Resolved
| Question | Answer |
|----------|--------|
| Stage organization | Accordion sections |
| Sub-phases consistency | Unique per stage, loaded from config |
| Tool interaction | Simple on/off toggle |
| Config structure | Nested 3-levels |
| Modal trigger | Top bar icon/button |
| Config scope | Project-level |

## Reference
- UI Reference: `skill modal window.png` (dark modal with scrollable list)

---

## Mockups & Prototypes

| Mockup | Type | Path | Tool Used |
|--------|------|------|-----------|
| Stage Toolbox Modal v1 (dark) | HTML | [mockups/stage-toolbox-modal-v1.html](mockups/stage-toolbox-modal-v1.html) | frontend-design |
| Stage Toolbox Modal v2 (light) ✅ | HTML | [mockups/stage-toolbox-modal-v2.html](mockups/stage-toolbox-modal-v2.html) | frontend-design |

### Preview Instructions
1. Open `mockups/stage-toolbox-modal-v2.html` in a browser (approved version)
2. Click the **green toolbox button** in the top bar to open the modal
3. Click accordion headers to expand/collapse stages
4. Toggle tools on/off to see the interaction
5. Badge counts update dynamically

### Mockup Features Demonstrated (v2 - Approved)
- ✅ Light-themed modal with clean white backgrounds
- ✅ Wider modal (680px) for better readability
- ✅ Accordion sections for 5 stages with color-coded icons
- ✅ Sub-phases displayed under each expanded stage
- ✅ Tools stack vertically within each phase
- ✅ Simple on/off toggle switches for each tool
- ✅ Top bar icon triggers modal
- ✅ "N active" badge shows enabled tool count per stage
- ✅ Placeholder badges for unimplemented stages
- ✅ Empty state for phases with no tools

---
*Generated: 2026-01-24 | Version: 2 (with mockups)*
