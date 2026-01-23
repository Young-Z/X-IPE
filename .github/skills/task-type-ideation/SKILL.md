---
name: task-type-ideation
description: Learn and refine user ideas through brainstorming. Use when user uploads idea files to the Workplace. Analyzes uploaded content, asks clarifying questions, and produces structured idea summary. Triggers on requests like "ideate", "brainstorm", "refine idea", "analyze my idea".
---

# Task Type: Ideation

## Purpose

Learn and refine user ideas through collaborative brainstorming by:
1. Analyzing uploaded idea files from Workplace
2. Generating an initial understanding summary
3. Asking clarifying questions to brainstorm with user
4. Creating a structured idea summary document with visual infographics
5. Preparing for Share Idea or Requirement Gathering

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.
- **Infographic Skill:** Learn `infographic-syntax-creator` skill to generate visual infographics in the idea summary.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| Task Type | Ideation |
| Category | ideation-stage |
| Standalone | No |
| Next Task | Share Idea or Requirement Gathering |
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

## Execution Flow

Execute Ideation by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Analyze Files | Read all files in idea folder | Files analyzed |
| 2 | Generate Summary | Create understanding summary for user | Summary shared |
| 3 | Brainstorm | Ask clarifying questions (3-5 at a time) | Idea refined |
| 4 | Research | Search for common principles if topic is established | Research complete |
| 5 | Create Summary | Write `idea-summary-vN.md` with infographics | Summary created |
| 6 | Complete | Request human review and approval | Human approves |

**⛔ BLOCKING RULES:**
- Step 3: Continue brainstorming until idea is well-defined
- Step 6 → Human Review: Human MUST approve idea summary before proceeding

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

### Step 4: Research Common Principles (If Applicable)

**Action:** Identify if the idea involves common/established topics and research relevant principles

**When to Research:**
- The idea touches well-known domains (e.g., authentication, e-commerce, data pipelines)
- Industry best practices exist for the problem space
- Established patterns or frameworks are relevant
- The idea could benefit from proven approaches

**Research Process:**
```
1. Identify if topic is common/established
2. Use web_search tool to research:
   - Industry best practices
   - Common design patterns
   - Established principles
   - Reference implementations
3. Document findings as "Common Principles"
4. Note authoritative sources for references
```

**Example Common Topics & Principles:**

| Topic | Common Principles to Research |
|-------|------------------------------|
| Authentication | OAuth 2.0, JWT best practices, MFA patterns |
| API Design | REST conventions, OpenAPI, rate limiting |
| Data Storage | ACID properties, CAP theorem, data modeling |
| UI/UX | Nielsen heuristics, accessibility (WCAG), mobile-first |
| Security | OWASP Top 10, zero-trust, encryption standards |
| Scalability | Horizontal scaling, caching strategies, CDN usage |
| DevOps | CI/CD pipelines, IaC, observability |

**Output:** List of relevant principles with sources to include in idea summary

---

### Step 5: Create Idea Summary Document

**Action:** Create versioned summary file `docs/ideas/{folder}/idea-summary-vN.md`

**Important:** 
- Do NOT update existing idea-summary files
- Always create a NEW versioned file: `idea-summary-v1.md`, `idea-summary-v2.md`, etc.
- The version number auto-increments based on existing files in the folder
- **Use infographic DSL** to visually represent key information (see Infographic Guidelines below)

**Template:**
```markdown
# Idea Summary

> Idea ID: IDEA-XXX
> Folder: {folder_name}
> Version: vN
> Created: {date}
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

{Use infographic for features list - see example below}

```infographic
infographic list-grid-badge-card
data
  title Key Features
  lists
    - label Feature 1
      desc Description of feature 1
      icon flash
    - label Feature 2
      desc Description of feature 2
      icon shield
```

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

## References & Common Principles
{Include if the idea involves common/established topics}

### Applied Principles
- **Principle 1:** {Description} - [Source](URL)
- **Principle 2:** {Description} - [Source](URL)

### Further Reading
- [Resource 1](URL) - {Brief description}
- [Resource 2](URL) - {Brief description}
```

---

## Infographic Guidelines

**When to use infographics in idea summaries:**

Use the `infographic-syntax-creator` skill to generate visual representations. Embed them in markdown using fenced code blocks:

````markdown
```infographic
infographic <template-name>
data
  ...
```
````

### Recommended Infographic Usage

| Information Type | Recommended Template | Example Use |
|-----------------|---------------------|-------------|
| Feature list | `list-grid-badge-card`, `list-row-horizontal-icon-arrow` | Key Features section |
| Process/Workflow | `sequence-snake-steps-simple`, `sequence-timeline-simple` | User journey, implementation phases |
| Pros/Cons | `compare-binary-horizontal-badge-card-arrow` | Trade-off analysis |
| SWOT Analysis | `compare-swot` | Strategic analysis |
| Priority Matrix | `compare-quadrant-quarter-simple-card` | Feature prioritization |
| Architecture | `hierarchy-tree-tech-style-badge-card` | System overview |
| Mind Map | `hierarchy-mindmap-branch-gradient-capsule-item` | Concept exploration |
| Metrics/KPIs | `chart-pie-compact-card`, `chart-column-simple` | Success metrics |

### Infographic Examples for Ideas

**Feature List:**
```infographic
infographic list-grid-badge-card
data
  title Core Features
  lists
    - label Fast Performance
      desc Sub-second response times
      icon flash
    - label Secure by Default
      desc End-to-end encryption
      icon shield check
    - label Easy Integration
      desc REST API & SDKs
      icon puzzle
    - label Real-time Sync
      desc Live collaboration
      icon sync
```

**Implementation Phases:**
```infographic
infographic sequence-roadmap-vertical-simple
data
  title Implementation Roadmap
  sequences
    - label Phase 1: MVP
      desc Core features only
    - label Phase 2: Beta
      desc User testing & feedback
    - label Phase 3: Launch
      desc Public release
    - label Phase 4: Scale
      desc Performance optimization
```

**Pros/Cons Analysis:**
```infographic
infographic compare-binary-horizontal-badge-card-arrow
data
  compares
    - label Pros
      children
        - label Lower cost
        - label Faster delivery
        - label Better UX
    - label Cons
      children
        - label Learning curve
        - label Migration effort
```

### When NOT to Use Infographics

- Simple bullet lists (< 3 items)
- Highly technical specifications
- Code examples or API documentation
- Legal/compliance text

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | All idea files analyzed | Yes |
| 2 | Brainstorming session completed | Yes |
| 3 | Common principles researched (if topic is common/established) | If Applicable |
| 4 | `docs/ideas/{folder}/idea-summary-vN.md` created (versioned) | Yes |
| 5 | Infographics used for visual elements where appropriate | Recommended |
| 6 | References included for researched principles | If Applicable |
| 7 | Human has reviewed and approved idea summary | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Task Completion Output

Upon completion, return:
```yaml
idea_id: IDEA-XXX
idea_status: Refined
idea_version: vN
next_task_type: Requirement Gathering
require_human_review: true
task_output_links:
  - docs/ideas/{folder}/idea-summary-vN.md
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
| Plain text for everything | Harder to scan visually | Use infographics for lists, flows, comparisons |

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

5. Research Common Principles (if applicable):
   - Mobile app → Research: Mobile UX best practices, offline-first patterns
   - User auth → Research: OAuth 2.0, biometric auth standards
   - Document sources for references section

6. Create docs/ideas/mobile-app-idea/idea-summary-v1.md with:
   - Overview and problem statement (text)
   - Key Features (infographic: list-grid-badge-card)
   - Implementation Phases (infographic: sequence-roadmap-vertical-simple)
   - Platform Comparison (infographic: compare-binary-horizontal-badge-card-arrow)
   - References & Common Principles section with researched sources

7. Resume Task Flow from task-execution-guideline skill
```
