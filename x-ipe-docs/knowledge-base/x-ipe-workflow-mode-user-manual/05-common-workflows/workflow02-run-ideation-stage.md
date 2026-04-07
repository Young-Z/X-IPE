---
title: "Run Ideation Stage"
section: "05-common-workflows"
extraction_round: 2
---

# Run the Ideation Stage

## Overview
The Ideation stage is the first stage in every workflow. It involves composing your initial idea, optionally adding UIUX references, and refining the idea with AI assistance.

## Available Actions

| Action | Icon | Mandatory | Description |
|--------|------|-----------|-------------|
| Compose Idea | 📝 | ✅ Yes | Write or upload your initial idea |
| Reference UIUX | 🎨 | ○ Optional | Add UIUX feedback references |
| Refine Idea | 💡 | ✅ Yes | AI-assisted idea refinement |
| Design Mockup | 🖼 | ○ Optional | Create visual mockup |

## Step-by-Step

### Step 1: Compose Idea
1. Expand the workflow card → click **📝 Compose Idea**
2. The Compose Idea Modal opens (see [feature05-compose-idea-modal](../04-core-features/feature05-compose-idea-modal.md))
3. Enter a name (1–10 words) → write markdown content or upload files
4. Click **"Submit Idea"**
5. ✅ Action shows checkmark (✓)

### Step 2: Reference UIUX (Optional)
1. Click **🎨 Reference UIUX** if you have UIUX feedback to attach
2. This dispatches the UIUX reference skill to the terminal
3. Follow terminal prompts to complete

### Step 3: Refine Idea
1. Click **💡 Refine Idea**
2. The skill name is sent to the connected AI CLI tool via the terminal
3. The terminal shows the skill command — **press Enter** to execute
4. AI reads your composed idea and creates a refined idea summary
5. Output saved to `x-ipe-docs/ideas/wf-NNN-{name}/refined-idea/idea-summary-v1.md`
6. ✅ Action shows checkmark (✓)

### Step 4: Design Mockup (Optional)
1. Click **🖼 Design Mockup** for visual prototyping
2. Dispatches the mockup skill to the terminal

### Stage Completion
- When **both mandatory actions** (Compose Idea + Refine Idea) are marked done → Ideation stage auto-completes
- The stage indicator shows ✓ and the Requirement stage unlocks
