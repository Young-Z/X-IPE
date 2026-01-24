# Skill Structure Guidelines

Detailed guidelines for X-IPE skill structure and organization.

## How to Use This Document

| Need | Go To |
|------|-------|
| Understand what a section is for | This document (Key Sections Explained) |
| Copy-paste skill format | [task-type-skill.md](../templates/task-type-skill.md) or [skill-category-skill.md](../templates/skill-category-skill.md) |
| Learn workflow patterns | [workflows.md](workflows.md) |
| Learn output patterns | [output-patterns.md](output-patterns.md) |

**This document explains WHY. Templates show HOW.**

---

## Directory Structure

```
.github/skills/{skill-name}/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── templates/     - Document templates
    ├── references/    - Additional documentation
    └── scripts/       - Executable code
```

---

## SKILL.md Structure

**⚠️ SECTION ORDER IS MANDATORY.** All sections must appear in the exact order defined in templates. See templates for the authoritative section order.

### Frontmatter (Required)

```yaml
---
name: {skill-name}
description: {Comprehensive description including triggers}
---
```

**Guidelines:**
- `name`: Use lowercase with hyphens
- `description`: Include BOTH what skill does AND when to use it
- No other fields in frontmatter

### Body Structure by Skill Type

For complete body structure with all required sections, see the templates:
- **Task Type Skills**: [task-type-skill.md](../templates/task-type-skill.md)
- **Skill Category Skills**: [skill-category-skill.md](../templates/skill-category-skill.md)

---

## Key Sections Explained

### Purpose

Brief numbered list (4-6 items) of what the skill accomplishes. Start with a one-line description followed by numbered action items.

### Important Notes

Always include skill prerequisite for task type skills. This ensures agents learn foundational skills before executing specialized ones.

### Task Type Default Attributes

Standard 4 attributes for all task type skills:

| Attribute | Description | Values |
|-----------|-------------|--------|
| Task Type | Name of this task type | String |
| Category | Lifecycle category | standalone, feature-stage, requirement-stage, ideation-stage |
| Next Task Type | What follows | Task Type name or null |
| Require Human Review | Needs approval | Yes or No |

### Task Type Required Input Attributes

Inputs the skill accepts when invoked. Always include `Auto Proceed` (default: False). Add task-specific inputs with their default values. For complex inputs, include YAML structure description.

### Skill/Task Completion Output Attributes

What the skill returns upon completion. Must include: category, status, next_task_type, require_human_review, task_output_links, and any dynamic attributes specific to the category.

### Definition of Ready (DoR)

Entry criteria that must be met before starting. Use numbered table format with Required column (Yes/No).

### Execution Flow

High-level overview table showing step sequence with gates. Each step has: Step #, Name, Action, Gate to Next. Always include **⛔ BLOCKING RULES** after the table.

### Execution Procedure

Detailed instructions for each step. Include:
- **Action:** statement describing what to do
- Numbered instructions or rules
- **Output:** what the step produces

### Definition of Done (DoD)

Exit criteria that must be met before completing. Use numbered table format. Always end with reminder to return to `task-execution-guideline` skill.

### Patterns

Common scenarios with **When/Then** format. Include 1-2 patterns showing condition and steps to take.

### Anti-Patterns

Table of things to avoid with: Anti-Pattern, Why Bad, Do Instead columns. Include 2-3 anti-patterns.

---

## Best Practices

### 1. Keep SKILL.md Under 500 Lines

Split into references if larger.

### 2. Use Consistent Formatting

- Tables for structured data
- Code blocks for YAML/pseudocode
- Numbered lists for sequences
- Bullet points for options

### 3. Include Concrete Examples

At least one full example showing:
1. Request/trigger
2. Step-by-step execution
3. Output format

### 4. Use Visual Indicators

- ⛔ for blocking rules
- ⚠️ for warnings
- ✅ for required actions
- 🔄 for in-progress
- ⏳ for pending

### 5. Reference Other Skills Correctly

Use backticks: `task-execution-guideline`
Use links for files: [template.md](templates/template.md)

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing DoR/DoD | Add entry/exit criteria |
| Vague description | Be specific about triggers |
| Duplicate output sections | Keep only Skill/Task Completion Output |
| No blocking rules | Add ⛔ BLOCKING RULES to Execution Flow |
| Missing skill prerequisite | Add Important Notes section |
