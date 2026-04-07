---
title: "Feature Implementation Lifecycle"
section: "05-common-workflows"
extraction_round: 2
---

# Feature Implementation Lifecycle

## Overview
After Feature Breakdown, each feature has its own lane with 8 steps that progress through the implementation lifecycle.

## Feature Lane Steps

| Step | Icon | Skill | Description |
|------|------|-------|-------------|
| Refinement | 📐 | `x-ipe-task-based-feature-refinement` | Detail feature specification |
| Tech Design | ⚙ | `x-ipe-task-based-technical-design` | Create technical design |
| Implement | 💻 | `x-ipe-task-based-code-implementation` | Write code |
| Testing | ✅ | `x-ipe-task-based-feature-acceptance-test` | Run acceptance tests |
| Refactor | 🔧 | `x-ipe-task-based-code-refactor` | Code quality improvements |
| Closing | 🏁 | `x-ipe-task-based-feature-closing` | Create PR, finalize |
| Playground | 🎮 | `x-ipe-task-based-human-playground` | Interactive testing |
| CR | 🔄 | `x-ipe-task-based-change-request` | Handle change requests |

## Step-by-Step (Per Feature)

### Step 1: Click Feature Lane Step
1. Find your feature lane (e.g., "FEATURE-050-A — Extractor Skill Foundation")
2. Click the step dot (e.g., "Refinement")
3. If already done → toast: "{Step} is already completed for {featureId}"
4. If pending/active → action dispatched to terminal

### Step 2: Execute in Terminal
1. Skill command appears in terminal
2. **Press Enter** to execute
3. AI performs the task (reads previous deliverables, generates output)
4. Results saved to feature-specific deliverables folder

### Step 3: Verify Completion
1. Step dot turns green (✓) when done
2. Next step becomes available (blue ◉)
3. Polling auto-refreshes every 7 seconds

## Dependency Rules

| Badge | Meaning |
|-------|---------|
| ⇉ **Parallel** | Feature can start immediately, no dependencies |
| ⛓ **needs FEATURE-XXX** | Must wait for named feature to complete the same step |

Example: If FEATURE-050-B "⛓ needs FEATURE-050-A", then B's Refinement step won't execute until A's Refinement is done.

## Manual Override
- **Right-click** any step → context menu with "Mark as Done" / "Reset to Pending"
- Useful for recovering from stuck steps or correcting status
