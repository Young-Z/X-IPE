---
name: task-type-requirement-gathering
description: Gather requirements from user requests and create requirement summary. Use when starting a new feature or receiving a new user request. Triggers on requests like "new feature", "add feature", "I want to build", "create requirement".
---

# Task Type: Requirement Gathering

## Purpose

Gather and document requirements from user requests by:
1. Understanding the user request
2. Asking clarifying questions
3. Creating requirement summary document
4. Preparing for Feature Breakdown

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Requirement Gathering |
| Category | requirement-stage |
| Next Task Type | Feature Breakdown |
| Require Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| Mockup List | N/A |

**Mockup List Structure:**
```yaml
mockup_list:
  - mockup_name: "Description of what function the mockup is for"
    mockup_list: "URL to the mockup"
  - mockup_name: "Another mockup description"
    mockup_list: "URL to the mockup"
```

---

## Skill/Task Completion Output Attributes

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: requirement-stage
  status: completed | blocked
  next_task_type: Feature Breakdown
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [x-ipe-docs/requirements/requirement-details.md] # or requirement-details-part-X.md
  mockup_list: [inherited from input or N/A]
  # Dynamic attributes for requirement-stage
  requirement_summary_updated: true | false
  requirement_details_part: 1 | 2 | 3 | ... # current active part number
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | User request received | Yes |
| 2 | Human available for clarification | Yes |
| 3 | AI Agent no more clarifying questions | Yes |

---

## Execution Flow

Execute Requirement Gathering by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Understand | Parse what, who, why from user request (optional: web research) | Initial understanding |
| 2 | Clarify | Ask clarifying questions (3-5 at a time) | All questions answered |
| 3 | Check File | Check if requirement-details needs splitting (>500 lines) | File ready |
| 4 | Document | Create/update `requirement-details.md` (or current part) | Document created |
| 5 | Complete | Verify DoD, request human review | Human review |

**⛔ BLOCKING RULES:**
- Step 2: Continue asking until ALL ambiguities resolved
- Step 3: MUST split file if current part exceeds 500 lines before adding new content
- Step 5 → Human Review: Human MUST approve requirements before Feature Breakdown

---

## Execution Procedure

### Step 1: Understand User Request

**Action:** Parse the user request to understand scope

```
1. Identify WHAT is being requested
2. Identify WHO will use the feature
3. Identify WHY this is needed (business value)
4. Note any constraints mentioned
```

**🌐 Web Search (Optional):**
Use web search capability to research:
- Industry standards and best practices for similar features
- Competitor products and their feature sets
- Domain-specific terminology and concepts
- Regulatory or compliance requirements in the domain

**Output:** Initial understanding summary

### Step 2: Ask Clarifying Questions

**Action:** Resolve ambiguities with human

**Question Categories:**

| Category | Example Questions |
|----------|-------------------|
| Scope | "Should this include X?" |
| Users | "Who will use this feature?" |
| Edge Cases | "What happens when Y?" |
| Priorities | "Is A more important than B?" |
| Constraints | "Are there performance requirements?" |

**Rules:**
- Ask questions in batches (3-5 at a time)
- Wait for human response before proceeding
- Document answers immediately

**Important:**
1. Repeat until all ambiguities are resolved
2. Avoid making assumptions
3. Unless Human enforces, do not skip any clarifications

### Step 3: Check File Size and Split if Needed

**Action:** Check if requirement-details file needs splitting before adding new content

**Splitting Rules:**
- **Threshold:** 500 lines
- **When:** Before adding NEW requirements, check current file line count
- **How:** If current file > 500 lines, create new part

**Procedure:**
```
1. Determine current active file:
   a. Check if x-ipe-docs/requirements/requirement-details.md exists
   b. Check if x-ipe-docs/requirements/requirement-details-part-X.md files exist
   c. Find the highest part number (latest active part)

2. Count lines in current active file:
   - If no file exists → current_lines = 0, active_file = requirement-details.md
   - If requirement-details.md exists (no parts) → count its lines
   - If parts exist → count lines in highest part number file

3. IF current_lines > 500:
   a. IF file is requirement-details.md (original, no parts yet):
      - Rename requirement-details.md → requirement-details-part-1.md
      - Create new requirement-details-part-2.md with header template
      - New file becomes active
   
   b. ELSE IF file is requirement-details-part-X.md:
      - Create new requirement-details-part-(X+1).md with header template
      - New file becomes active

4. ELSE (current_lines <= 500):
   - Continue using current active file
```

**New Part Header Template:**
```markdown
# Requirement Details - Part {X}

> Continued from: [requirement-details-part-{X-1}.md](requirement-details-part-{X-1}.md)  
> Created: {MM-DD-YYYY}

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup List |
|---------------------|---------|-------------|

---

## Feature Details (Continued)

```

**File Naming Convention:**
| Scenario | File Names |
|----------|------------|
| Single file (< 500 lines total) | `requirement-details.md` |
| After first split | `requirement-details-part-1.md`, `requirement-details-part-2.md` |
| After second split | `requirement-details-part-1.md`, `requirement-details-part-2.md`, `requirement-details-part-3.md` |

**Index File (Required when parts exist):**
When parts exist, create/update `requirement-details-index.md`:
```markdown
# Requirement Details Index

> Last Updated: MM-DD-YYYY

## Parts Overview

| Part | File | Features Covered | Lines |
|------|------|------------------|-------|
| 1 | [Part 1](requirement-details-part-1.md) | FEATURE-001 to FEATURE-005 | ~420 |
| 2 | [Part 2](requirement-details-part-2.md) | FEATURE-006 to FEATURE-010 | ~380 |
```

**Note:** Feature List is NOT in index - each part file has its own Feature List section.

### Step 4: Create Requirement Details Document

**Action:** Create or update the active requirement-details file (determined in Step 3)

**Rules:**
- Use [requirement-details.md](templates/requirement-details.md) as template for new files
- **Document requirements in detail** - this is the source of truth for all downstream tasks
- Ensure all sections are filled based on gathered information
- Include all clarifications and decisions made during the gathering process
- **Add new content to the current active part file**

**Documentation Guidelines:**
- Be thorough and specific - vague requirements lead to incorrect implementations
- Document the "why" behind requirements, not just the "what"
- Include examples and edge cases discussed with the human
- Capture any constraints, assumptions, or dependencies mentioned

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `x-ipe-docs/requirements/requirement-details.md` (or current part) created/updated | Yes |
| 2 | All clarifying questions answered | Yes |
| 3 | If file split occurred, old file renamed correctly | Conditional |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Vague Request

**When:** User gives unclear request like "Build something for users to log in"
**Then:**
```
1. Ask clarifying questions:
   - "What authentication methods? (email/password, OAuth, SSO)"
   - "Should there be password reset?"
   - "Any specific security requirements?"
2. Document answers
3. Create requirement summary
```

### Pattern: Detailed Request

**When:** User gives detailed request with clear scope
**Then:**
```
1. Confirm understanding with user
2. Ask about edge cases only
3. Create requirement summary
```

### Pattern: Existing Project Addition

**When:** Adding feature to existing project
**Then:**
```
1. Read existing requirement-details.md
2. Understand current scope
3. Ask how new feature relates to existing
4. Update requirement summary
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Assuming requirements | Missing features | Ask clarifying questions |
| Skipping documentation | Lost context | Always create requirement-details.md |
| Too many questions at once | Overwhelms human | Batch 3-5 questions |
| Skip to Feature Breakdown | Missing requirements | Complete this task first |

---

## Example

**Request:** "Add user authentication"

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Understand Request:
   - WHAT: User authentication system
   - WHO: End users of the application
   - WHY: Security, user management

3. Ask Clarifying Questions:
   - "Should we support OAuth (Google/GitHub)?" → Yes, Google
   - "Password reset needed?" → Yes, via email
   - "Remember me functionality?" → Yes

4. Create x-ipe-docs/requirements/requirement-details.md:
   # Requirement Summary
   ... (fill all sections) ...

5. Return Task Completion Output:
   category: requirement-stage
   status: completed
   next_task_type: Feature Breakdown
   require_human_review: Yes
   task_output_links:
     - x-ipe-docs/requirements/requirement-details.md

6. Resume Task Flow from task-execution-guideline skill
```
