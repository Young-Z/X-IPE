# Task Type Skill Template

Use this template when creating a new task type skill.

---

```markdown
---
name: task-type-{skill-name}
description: {Brief description of what this task type does}. Use when {trigger conditions}. Triggers on requests like "{example trigger 1}", "{example trigger 2}".
---

# Task Type: {Skill Name}

## Purpose

{Brief description of what this task type accomplishes} by:
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. {Step 4}

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | {Task Type Name} |
| Category | {standalone \| feature-stage \| requirement-stage \| ideation-stage} |
| Next Task Type | {Next Task Type \| null} |
| Require Human Review | {Yes \| No} |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| {Additional Input 1} | {Default Value} |
| {Additional Input 2} | {Default Value} |

{If complex input structure, add description:}
**{Input Name} Structure:**
```yaml
{input_name}:
  - field1: "description"
    field2: "value"
```

---

## Skill/Task Completion Output Attributes

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: {standalone | feature-stage | requirement-stage | ideation-stage}
  status: completed | blocked
  next_task_type: {Next Task Type}
  require_human_review: {Yes | No}
  task_output_links: [{output file paths}]
  # Dynamic attributes for {category}
  {dynamic_attr_1}: {value}
  {dynamic_attr_2}: {value}
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | {Prerequisite 1} | Yes |
| 2 | {Prerequisite 2} | Yes |
| 3 | {Prerequisite 3} | {Yes \| No} |

---

## Execution Flow

Execute {Task Type Name} by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | {Step Name} | {Brief action description} | {Gate condition} |
| 2 | {Step Name} | {Brief action description} | {Gate condition} |
| 3 | {Step Name} | {Brief action description} | {Gate condition} |
| 4 | {Step Name} | {Brief action description} | {Gate condition} |
| 5 | Complete | Verify DoD, request human review | Human review |

**⛔ BLOCKING RULES:**
- {Rule 1}: {Description}
- {Rule 2}: {Description}

---

## Execution Procedure

### Step 1: {Step Name}

**Action:** {What to do}

```
1. {Detailed instruction 1}
2. {Detailed instruction 2}
3. {Detailed instruction 3}
```

**Output:** {What this step produces}

### Step 2: {Step Name}

**Action:** {What to do}

{Instructions or rules}

### Step 3: {Step Name}

**Action:** {What to do}

**Rules:**
- {Rule 1}
- {Rule 2}
- {Rule 3}

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | {Output 1 created/updated} | Yes |
| 2 | {Verification 1 passed} | Yes |
| 3 | {Optional checkpoint} | {Recommended \| No} |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: {Pattern Name}

**When:** {Condition}
**Then:**
```
1. {Action 1}
2. {Action 2}
3. {Action 3}
```

### Pattern: {Pattern Name}

**When:** {Condition}
**Then:**
```
1. {Action 1}
2. {Action 2}
3. {Action 3}
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| {Anti-pattern 1} | {Reason} | {Better approach} |
| {Anti-pattern 2} | {Reason} | {Better approach} |
| {Anti-pattern 3} | {Reason} | {Better approach} |

---

## Example

See [references/examples.md](references/examples.md) for concrete execution examples.

```
```

---

## Template Usage Notes

### ⚠️ SKILL.md Line Limit: 500 Lines Max

**CRITICAL:** SKILL.md body MUST stay under 500 lines to minimize context bloat.

**What to keep in SKILL.md:**
- Purpose, Attributes, DoR, DoD (core structure)
- Execution Flow (overview table)
- Execution Procedure (essential steps only)
- Patterns and Anti-Patterns (concise tables)

**What to move to references/:**
- `references/examples.md` - Detailed execution examples (MANDATORY)
- `references/detailed-procedures.md` - Complex step-by-step guides
- `references/edge-cases.md` - Edge case handling details

**If SKILL.md > 500 lines:**
1. Move Example section content to `references/examples.md`
2. Keep only reference link in SKILL.md
3. Move verbose procedure details to references
4. Simplify Patterns to essential info only

---

### Required Sections (Must Include - IN THIS ORDER)

**⚠️ SECTION ORDER IS MANDATORY.** Sections must appear in this exact sequence:

| # | Section Name | Validation |
|---|--------------|------------|
| 1 | Frontmatter | name and description |
| 2 | Purpose | numbered list of what skill does |
| 3 | Important Notes | skill prerequisite |
| 4 | Task Type Default Attributes | 4 standard attributes |
| 5 | Task Type Required Input Attributes | at least Auto Proceed |
| 6 | Skill/Task Completion Output Attributes | YAML with `category` first |
| 7 | Definition of Ready (DoR) | entry criteria table |
| 8 | Execution Flow | overview table with gates + blocking rules |
| 9 | Execution Procedure | detailed steps |
| 10 | Definition of Done (DoD) | exit criteria table |
| 11 | Patterns | at least 1-2 common patterns (concise) |
| 12 | Anti-Patterns | at least 2-3 anti-patterns (table format) |
| 13 | Example | **Link to references/examples.md** |

**Validation Warnings:**
- ⚠️ Section out of order → Reorder to match template
- ⚠️ Section missing → Add required section
- ⚠️ Section renamed → Use exact section name from template
- ⚠️ Output YAML: `category` not first → Move `category` before `status`
- ⚠️ **SKILL.md > 500 lines → Move examples to references/examples.md**
- ⚠️ **Example section has inline content → Replace with link to references**

### Required Reference Files

| File | Purpose | When Required |
|------|---------|---------------|
| `references/examples.md` | Concrete execution examples | **ALWAYS for Task Type Skills** |

### Optional Sections (Add if Needed)

Insert optional sections AFTER the required section they relate to:
- **Output Artifacts** - after Skill/Task Completion Output Attributes
- **Templates** - after Execution Procedure
- **References** - after Execution Procedure
- **Best Practices** - before Patterns

### Category Values

| Category | Description | Board Management |
|----------|-------------|------------------|
| standalone | No board tracking | None |
| feature-stage | Updates feature board | feature-stage+feature-board-management |
| requirement-stage | Updates requirement board | requirement-stage+requirement-board-management |
| ideation-stage | Updates ideation board | ideation-stage+ideation-board-management |
