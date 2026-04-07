---
title: "Skills Browser"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/init.js
---

# Skills Browser

## Overview

The Skills Browser modal shows all available X-IPE skills that can be used in workflow actions. Skills are the task-based automation units that power each workflow action.

## How to Access

1. Click the **🎯 Skills** button in the top header bar
2. The modal opens showing a scrollable list of all discovered skills

![Skills Modal](screenshots/skills-modal.png)

## Modal Layout

- **Title:** "Available Skills"
- **Skill entries** displayed as cards, each showing:
  - ⚡ **Skill name** (bold heading)
  - Gray description text explaining the skill's purpose and triggers
- **No filtering or search** in the current UI — all skills are shown in a flat list

## How Skills Relate to Workflow Actions

Each workflow action (e.g., "Compose Idea", "Feature Refinement") has an associated skill:

| Action | Skill |
|--------|-------|
| Compose Idea | `x-ipe-task-based-ideation` |
| Refine Idea | `x-ipe-task-based-ideation` |
| Requirement Gathering | `x-ipe-task-based-requirement-gathering` |
| Feature Breakdown | `x-ipe-task-based-feature-breakdown` |
| Feature Refinement | `x-ipe-task-based-feature-refinement` |
| Technical Design | `x-ipe-task-based-technical-design` |
| Implementation | `x-ipe-task-based-code-implementation` |
| Acceptance Testing | `x-ipe-task-based-feature-acceptance-test` |
| Feature Closing | `x-ipe-task-based-feature-closing` |

When an action is triggered, the skill name is sent to the connected AI CLI tool via the terminal.

## Data Source

- **API endpoint:** `GET /api/skills`
- **Response:** `{success: true, skills: [{name, description, ...}]}`
- Skills discovered from `.github/skills/` directory

## Error States

| Condition | Behavior |
|-----------|----------|
| Network error | Alert: "Error loading skills: {message}" |
| Empty response | Shows "No skills found" placeholder |
| API slow (>5s) | Loading spinner continues |

## UI Elements

| Element | Selector | Purpose |
|---------|----------|---------|
| Trigger button | `#skills-btn` | Opens the modal |
| Modal | `#skills-modal` | Bootstrap modal container |
| Content body | `#skills-modal-body` | Skills list container |
