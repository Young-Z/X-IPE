---
title: "Run Requirement Stage"
section: "05-common-workflows"
extraction_round: 2
---

# Run the Requirement Stage

## Overview
The Requirement stage transforms your refined idea into structured requirements and breaks them into implementable features.

## Available Actions

| Action | Icon | Mandatory | Description |
|--------|------|-----------|-------------|
| Requirement Gathering | 📋 | ✅ Yes | AI analyzes idea → creates requirement docs |
| Feature Breakdown | 🔀 | ✅ Yes | Splits requirements into EPICs and features |

## Step-by-Step

### Step 1: Requirement Gathering
1. Click **📋 Requirement Gathering**
2. Skill `x-ipe-task-based-requirement-gathering` is sent to the terminal
3. **Press Enter** in the terminal to execute
4. AI reads refined idea deliverables and creates requirement documents
5. Output saved to `x-ipe-docs/requirements/` folder
6. ✅ Action shows checkmark (✓)

### Step 2: Feature Breakdown
1. Click **🔀 Feature Breakdown**
2. Skill `x-ipe-task-based-feature-breakdown` is sent to terminal
3. **Press Enter** to execute
4. AI creates EPIC and feature entries in `x-ipe-docs/planning/features.md`
5. **Feature lanes appear** in the workflow card
6. Dependencies between features are established
7. ✅ Action shows checkmark (✓)

### Stage Completion
- When both actions are done → Requirement stage completes
- **Implement stage unlocks** with feature lanes visible
- Each feature shows its dependency badge (⇉ Parallel or ⛓ needs X)
