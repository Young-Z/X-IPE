---
title: "Change Interaction Mode"
section: "05-common-workflows"
extraction_round: 2
---

# Change Interaction Mode

## Overview
Each workflow can be set to one of three interaction modes that control how the AI agent interacts with you during task execution.

## The Three Modes

| Mode | Icon | Description |
|------|------|-------------|
| **Human Direct** | 👤 | AI agent asks you directly at every decision point |
| **DAO Represents Human** | 🤖 | DAO skill acts as your representative, answering on your behalf |
| **DAO Inner-Skill Only** | 🤖⚡ | DAO answers within-skill decisions only; cross-skill decisions go to you |

## Step-by-Step

### Step 1: Locate the Dropdown
1. Find the **"Interaction Mode"** label on the workflow card header
2. Below it, a dropdown button shows the current mode (e.g., "👤 Human Direct")

![Interaction Mode Dropdown](screenshots/interaction-mode-dropdown.png)

### Step 2: Open and Select
1. Click the dropdown button to expand
2. Three options appear:
   - 👤 Human Direct
   - 🤖 DAO Represents Human
   - 🤖⚡ DAO Inner-Skill Only
3. Click your desired mode

### Step 3: Confirmation
1. The dropdown closes and shows the new mode
2. API call updates `global.process_preference.interaction_mode` in workflow state
3. Change takes effect for **all future actions** in this workflow

## Important Notes

- Changing mode does **NOT** affect actions already in progress
- **Human Direct** gives you maximum control but requires more interaction
- **DAO Represents Human** is best for autonomous execution — the DAO skill makes decisions for you based on project context
- **DAO Inner-Skill Only** is a middle ground — you handle big decisions, DAO handles small ones
