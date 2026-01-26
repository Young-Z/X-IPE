---
name: ideation-stage+ideation-board-management
description: Manage idea tracking during ideation-stage tasks. This is a category-level skill called during Step 4 (Category Closing) for ideation-stage tasks. Accepts Task Data Model. Outputs category_level_change_summary.
---

# Ideation Board Management

## Purpose

AI Agents follow this skill to manage idea tracking - ensuring ideas are properly documented, refined, and ready for sharing. This skill is called during **Step 4 (Category Closing)** for tasks with `category: ideation-stage`.

**Operations:**
1. **Locate** idea folders and files
2. **Track** idea refinement status
3. **Manage** versioned summaries
4. **Track** shared documents

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Input: Task Data Model

This skill receives the Task Data Model from task execution. For ideation-stage tasks, it expects these dynamic attributes:

```yaml
Task:
  # Core fields
  task_id: TASK-XXX
  task_type: <Task Type>
  task_description: <≤50 words>
  category: ideation-stage
  status: <status>
  
  # Dynamic attributes (from ideation-stage task type skills)
  idea_id: IDEA-XXX | null              # Idea identifier
  idea_folder: x-ipe-docs/ideas/{folder}       # Folder path
  idea_version: vN                       # Current version number
  idea_status: Draft | Refined | Shared  # Idea status
  shared_formats: [pptx, docx, ...]      # Formats generated (for Share Idea)
  # ... other dynamic attributes
```

---

## Output: category_level_change_summary

This skill MUST return a `category_level_change_summary` (≤100 words) describing what changed.

**Example outputs:**
```
"Refined idea in x-ipe-docs/ideas/mobile-app/, created idea-summary-v2.md"
"Shared idea as PowerPoint: formal-idea-summary-v2.pptx"
"Created 2 share formats: formal-idea-summary-v1.pptx, formal-idea-summary-v1.docx"
```

---

## Integration with Task Lifecycle

This skill is called during Step 4 (Category Closing) when `category = ideation-stage`.

**Flow:**
```
Step 3: Task Work Execution
   ↓ (task type skill returns idea-related attributes)
Step 4: Category Closing
   → task-board-management (MANDATORY)
   → ideation-stage+ideation-board-management (this skill)
      - Receives Task Data Model
      - Updates idea tracking
      - Returns category_level_change_summary
   ↓
Step 5: Check Global DoD
```

---

## Operations

### Operation 1: Track Idea Refinement

**When:** Ideation task completes
**Then:** Verify idea summary was created

```
Input: Task Data Model with:
  - task_type: Ideation
  - idea_folder: x-ipe-docs/ideas/{folder}
  - idea_version: vN
  - idea_status: Refined
  - task_output_links: [path to idea-summary-vN.md]

Process:
1. Verify x-ipe-docs/ideas/{folder}/idea-summary-vN.md exists
2. Confirm idea is marked as Refined
3. Return summary of changes

Output:
  category_level_change_summary: "Refined idea in {folder}, created idea-summary-vN.md"
```

### Operation 2: Track Mockup Artifacts

**When:** Idea Mockup task completes
**Then:** Track created mockup files

```
Input: Task Data Model with:
  - task_type: Idea Mockup
  - idea_folder: x-ipe-docs/ideas/{folder}
  - mockups_created: [{type, path}, ...]
  - idea_summary_version: vN+1
  - task_output_links: [paths to mockup files]

Process:
1. Verify each mockup file exists
2. Confirm files are in {folder}/mockups/
3. Verify idea summary was updated
4. Return summary

Output:
  category_level_change_summary: "Created {N} mockups in {folder}/mockups/"
```

### Operation 3: Track Architecture Diagrams

**When:** Idea to Architecture task completes
**Then:** Track created architecture diagrams

```
Input: Task Data Model with:
  - task_type: Idea to Architecture
  - idea_folder: x-ipe-docs/ideas/{folder}
  - diagrams_created: [{type, path}, ...]
  - idea_summary_version: vN+1
  - task_output_links: [paths to diagram files]

Process:
1. Verify each diagram file exists
2. Confirm files are in {folder}/architecture/
3. Verify idea summary was updated
4. Return summary

Output:
  category_level_change_summary: "Created {N} architecture diagrams in {folder}/architecture/"
```

### Operation 4: Track Shared Documents

**When:** Share Idea task completes
**Then:** Track generated documents

```
Input: Task Data Model with:
  - task_type: Share Idea
  - idea_folder: x-ipe-docs/ideas/{folder}
  - source_file: idea-summary-vN.md
  - shared_formats: [pptx, docx, ...]
  - task_output_links: [paths to generated files]

Process:
1. Verify each generated file exists
2. Confirm naming convention: formal-{source}.{ext}
3. Return summary

Output:
  category_level_change_summary: "Created {N} share formats: {file_list}"
```

---

## Idea Folder Structure

```
x-ipe-docs/
└── ideas/
    └── {idea-folder}/
        ├── files/                        # Original uploaded files
        │   └── {uploaded files}
        ├── mockups/                      # UI mockups (from Idea Mockup task)
        │   ├── dashboard-v1.html
        │   └── dashboard-v1.css
        ├── architecture/                 # Architecture diagrams (from Idea to Architecture task)
        │   ├── system-architecture-v1.md
        │   └── data-flow-v1.md
        ├── idea-summary-v1.md            # First refined version
        ├── idea-summary-v2.md            # Updated with mockups/architecture
        ├── formal-idea-summary-v1.pptx   # Shared PowerPoint
        ├── formal-idea-summary-v1.docx   # Shared Word document
        └── ...
```

---

## Task Type to Operation Mapping

| Task Type Skill | Operation | Next Task |
|-----------------|-----------|-----------|
| task-type-ideation | Track Idea Refinement | Idea Mockup, Idea to Architecture, or Requirement Gathering |
| task-type-idea-mockup | Track Mockup Artifacts | Requirement Gathering |
| task-type-idea-to-architecture | Track Architecture Diagrams | Requirement Gathering |
| task-type-share-idea | Track Shared Documents | - |

---

## Idea Status Flow

```
Draft → Refined → Mockup/Architecture → Shared
  ↑        ↓              ↓                ↓
Upload   Ideation   Mockup/Arch Tasks   Share Idea
```

---

## Examples

### Example 1: Ideation Complete

**Input Task Data Model:**
```yaml
task_id: TASK-067
task_type: Ideation
category: ideation-stage
status: completed
idea_id: IDEA-001
idea_folder: x-ipe-docs/ideas/mobile-app-idea
idea_version: v1
idea_status: Refined
task_output_links:
  - x-ipe-docs/ideas/mobile-app-idea/idea-summary-v1.md
```

**Output:**
```yaml
category_level_change_summary: "Refined idea in mobile-app-idea, created idea-summary-v1.md with 5 key features defined"
```

### Example 2: Share Idea Complete

**Input Task Data Model:**
```yaml
task_id: TASK-070
task_type: Share Idea
category: ideation-stage
status: completed
idea_folder: x-ipe-docs/ideas/mobile-app-idea
source_file: idea-summary-v1.md
shared_formats:
  - pptx
  - docx
task_output_links:
  - x-ipe-docs/ideas/mobile-app-idea/formal-idea-summary-v1.pptx
  - x-ipe-docs/ideas/mobile-app-idea/formal-idea-summary-v1.docx
```

**Output:**
```yaml
category_level_change_summary: "Created 2 share formats: formal-idea-summary-v1.pptx, formal-idea-summary-v1.docx"
```
