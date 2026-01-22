---
name: task-type-ideation-@requirement-stage
description: Learn and refine user ideas through brainstorming. Use when user uploads idea files to the Workplace. Analyzes uploaded content, asks clarifying questions, and produces structured idea summary. Triggers on requests like "ideate", "brainstorm", "refine idea", "analyze my idea".
---

# Task Type: Ideation

## Purpose

Learn and refine user ideas through collaborative brainstorming by:
1. Analyzing uploaded idea files from Workplace
2. Generating an initial understanding summary
3. Asking clarifying questions to brainstorm with user
4. Creating a structured idea summary document
5. Preparing for Requirement Gathering

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| Task Type | Ideation |
| Category | requirement-stage |
| Standalone | No |
| Next Task | Requirement Gathering |
| Auto-advance | No |
| Human Review | Yes |

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Idea files uploaded to `docs/ideas/{folder}/` | Yes |
| 2 | Human available for brainstorming | Yes |
| 3 | Idea folder path provided | Yes |

---

## Execution Procedure

### Step 1: Locate and Analyze Idea Files

**Action:** Read all files in the specified idea folder

```
1. Navigate to docs/ideas/{folder}/files/
2. Read each file (text, markdown, code, etc.)
3. Identify key themes, concepts, and goals
4. Note any gaps or ambiguities
```

**Output:** Initial analysis summary

### Step 2: Generate Understanding Summary

**Action:** Create a summary of what you understand from the uploaded content

**Summary Structure:**
```markdown
## Idea Understanding Summary

### Core Concept
{What is the main idea about?}

### Key Goals
{What does the user want to achieve?}

### Identified Components
{What features/parts are mentioned?}

### Questions & Ambiguities
{What needs clarification?}
```

**Output:** Share summary with user for validation

### Step 3: Brainstorming Session

**Action:** Engage user with clarifying questions to refine the idea

**Question Categories:**

| Category | Example Questions |
|----------|-------------------|
| Problem Space | "What problem does this solve?" |
| Target Users | "Who will benefit from this?" |
| Scope | "What should be included in v1?" |
| Constraints | "Are there any technical limitations?" |
| Success Criteria | "How will we know it's successful?" |
| Alternatives | "Have you considered approach X?" |

**Rules:**
- Ask questions in batches (3-5 at a time)
- Wait for human response before proceeding
- Build on previous answers
- Challenge assumptions constructively
- Suggest alternatives when appropriate

**Important:**
1. This is a collaborative brainstorming session, not an interview
2. Offer creative suggestions and perspectives
3. Help user think through implications
4. Continue until idea is well-defined

### Step 4: Create Idea Summary Document

**Action:** Create `docs/ideas/{folder}/idea-summary.md`

**Template:**
```markdown
# Idea Summary

> Idea ID: IDEA-XXX
> Folder: {folder_name}
> Created: {date}
> Last Updated: {date}
> Status: Refined

## Overview
{Brief description of the refined idea}

## Problem Statement
{What problem does this idea solve?}

## Target Users
{Who will benefit?}

## Proposed Solution
{High-level description of the solution}

## Key Features
| Feature | Description | Priority |
|---------|-------------|----------|
| ... | ... | High/Medium/Low |

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints & Considerations
- Constraint 1
- Constraint 2

## Brainstorming Notes
{Key insights from brainstorming session}

## Source Files
- file1.md
- file2.txt

## Next Steps
- [ ] Proceed to Requirement Gathering
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | All idea files analyzed | Yes |
| 2 | Brainstorming session completed | Yes |
| 3 | `docs/ideas/{folder}/idea-summary.md` created | Yes |
| 4 | Human has reviewed and approved idea summary | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Task Completion Output

Upon completion, return:
```yaml
idea_id: IDEA-XXX
idea_status: Refined
next_task_type: Requirement Gathering
require_human_review: true
task_output_links:
  - docs/ideas/{folder}/idea-summary.md
```

---

## Patterns

### Pattern: Raw Notes Upload

**When:** User uploads unstructured notes or braindump
**Then:**
```
1. Extract key themes from notes
2. Organize into logical categories
3. Ask clarifying questions about each category
4. Help structure into coherent idea
```

### Pattern: Technical Specification Upload

**When:** User uploads detailed technical spec
**Then:**
```
1. Validate technical feasibility
2. Ask about business goals (why this spec?)
3. Identify missing user context
4. Connect technical details to user value
```

### Pattern: Competitive Analysis Upload

**When:** User uploads competitor analysis or inspiration
**Then:**
```
1. Identify what user likes about competitors
2. Ask what should be different/better
3. Help define unique value proposition
4. Document differentiators
```

### Pattern: Multiple Conflicting Ideas

**When:** Uploaded files contain conflicting approaches
**Then:**
```
1. Surface the conflicts clearly
2. Ask user to prioritize or choose
3. Help evaluate trade-offs
4. Document decision rationale
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Just summarizing without questions | Misses refinement opportunity | Engage in brainstorming |
| Too many questions at once | Overwhelms user | Batch 3-5 questions |
| Accepting everything at face value | May miss issues | Challenge assumptions constructively |
| Skipping to requirements | Idea not refined | Complete ideation first |
| Being passive | Not collaborative | Offer suggestions actively |

---

## Example

**Scenario:** User uploads business plan draft to `docs/ideas/mobile-app-idea/files/`

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Analyze Files:
   - Read business-plan.md
   - Read user-research.txt
   - Read competitor-notes.md

3. Generate Summary:
   "I understand you want to build a mobile app for..."
   
4. Brainstorming Questions:
   - "Your notes mention both iOS and Android - should v1 target both?"
   - "The user research shows two distinct personas - which is primary?"
   - "Have you considered a web-first approach instead?"

5. Create docs/ideas/mobile-app-idea/idea-summary.md

6. Resume Task Flow from task-execution-guideline skill
```
