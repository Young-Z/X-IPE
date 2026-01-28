# Idea Summary

> Idea ID: IDEA-016
> Folder: 004. Change Request to Workplace
> Version: v1
> Created: 2026-01-28
> Status: Refined

## Overview

Restructure the Workplace sidebar navigation to use a submenu pattern with two child sections: **Ideation** (existing Workplace functionality) and **UIUX Feedbacks** (new placeholder page). The Copilot button behavior changes from direct click to hover menu with "Refine idea" as the primary action.

## Problem Statement

The current Workplace navigation is a single flat item that redirects directly to the page. As the product grows, we need:
1. Better organization of related functionality under a parent category
2. Separation between ideation workflows and UIUX feedback collection
3. More intuitive Copilot button interaction with explicit action choices

## Target Users

- **Product Managers**: Using ideation to capture and refine product ideas
- **Designers/Developers**: Providing UIUX feedback on existing features
- **All X-IPE Users**: Benefiting from clearer navigation structure

## Proposed Solution

### Navigation Architecture

```architecture-dsl
@startuml module-view
title "Workplace Submenu Structure"
theme "theme-default"
direction top-to-bottom
grid 12 x 6

layer "Sidebar" {
  color "#f0f9ff"
  border-color "#0ea5e9"
  rows 6
  module "Workplace Parent" {
    cols 12
    rows 2
    grid 1 x 1
    component "Workplace (No Action)" { cols 1, rows 1, description "Parent menu item - click does nothing" }
  }
  module "Submenu Items" {
    cols 12
    rows 4
    grid 2 x 1
    component "Ideation" { cols 1, rows 1, description "Renamed from Workplace, all existing functions preserved" }
    component "UIUX Feedbacks" { cols 1, rows 1, description "New page with WIP banner" }
  }
}

@enduml
```

### Component Changes

| Component | Current State | Target State |
|-----------|--------------|--------------|
| Sidebar - Workplace | Single menu item → redirects | Parent item with always-visible nested children |
| Workplace Page | Named "Workplace" | Renamed to "Ideation" with icon |
| Copilot Button | Clickable (triggers action) | Non-clickable; hover reveals menu |
| Copilot Hover Menu | 3 existing options | "Refine idea" added at top + 3 existing |
| UIUX Feedbacks | Does not exist | New page with WIP banner |

## Key Features

### Feature 1: Sidebar Submenu Structure
- Workplace becomes parent menu item (no action on click)
- Always-visible nested items (indented)
- Two children: Ideation, UIUX Feedbacks
- Icon with label for "Ideation" submenu item

### Feature 2: Ideation Page (Renamed Workplace)
All existing functions must continue working:
- Idea upload/management
- File preview with Copilot integration
- Brainstorming history/sessions
- Mockup gallery

### Feature 3: Copilot Button Behavior Change
- Button is no longer directly clickable
- Hover reveals context menu with 4 options:
  1. **Refine idea** (NEW - top position)
  2. Existing option 2
  3. Existing option 3
  4. Existing option 4
- "Refine idea" triggers original click behavior

### Feature 4: UIUX Feedbacks Page
- New page accessible from sidebar submenu
- Simple "Work in Progress" banner
- Future feature placeholder

## Success Criteria

- [ ] Clicking Workplace parent does nothing (no redirect)
- [ ] Ideation and UIUX Feedbacks visible as nested submenu items
- [ ] Ideation page shows all existing Workplace functions
- [ ] Copilot button hover menu shows 4 options with "Refine idea" at top
- [ ] "Refine idea" triggers the original Copilot button behavior
- [ ] UIUX Feedbacks page shows WIP banner
- [ ] All existing Workplace functions work correctly after rename

## Constraints & Considerations

- Must preserve backward compatibility with existing workflows
- Existing users should find their workflows intact under "Ideation"
- Future extensibility: more submenu items may be added later
- Mobile/responsive behavior for nested menu items

## Brainstorming Notes

1. **Submenu Style**: Always visible (nested indented) - no expand/collapse needed
2. **Copilot Button**: Add "Refine idea" at top of existing 3-option hover menu
3. **Parent Behavior**: No action on click - purely organizational
4. **Verification Scope**: All 4 Workplace functions (upload, preview, history, mockups)
5. **UIUX Placeholder**: Simple banner, full feature comes later

## Source Files

- new idea.md

## Next Steps

- [ ] Proceed to Requirement Gathering (this is a Change Request affecting existing features)

## References & Common Principles

### Applied Principles
- **Progressive Disclosure**: Hide complexity until needed (submenu pattern)
- **Consistency**: Maintain existing workflows while adding new structure
- **Explicit Actions**: Hover menu makes actions discoverable vs hidden behind single click

