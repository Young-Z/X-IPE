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
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| Task Type | Requirement Gathering |
| Standalone | No |
| Next Task | Feature Breakdown |
| Auto-advance | No |

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | User request received | Yes |
| 2 | Human available for clarification | Yes |
| 3 | AI Agent no more clarifying questions | Yes |


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

### Step 3: Create Requirement Summary

**Action:** Create or update `docs/requirements/requirement-details.md`

**Rules:**
- Use [requirement-details.md](templates/requirement-details.md) as template
- Ensure all sections are filled based on gathered information

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `docs/requirements/requirement-details.md` created/updated | Yes |
| 2 | All clarifying questions answered | Yes |
| 3 | Human has reviewed requirements | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Task Completion Output

Upon completion, return:
```yaml
feature_id: N/A
feature_status: Requirements Gathered
next_task_type: Feature Breakdown
task_output_links:
  - docs/requirements/requirement-details.md
```

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

4. Create docs/requirements/requirement-details.md:
   # Requirement Summary
   ... (fill all sections) ...

5. Return task_output_links:
   - docs/requirements/requirement-details.md

6. Resume Task Flow from task-execution-guideline skill
```
