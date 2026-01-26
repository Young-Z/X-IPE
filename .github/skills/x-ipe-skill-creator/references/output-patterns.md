# Output Patterns

Use these patterns when skills need to produce consistent, high-quality output.

## Template Pattern

Provide templates for output format. Match the level of strictness to your needs.

**For strict requirements (like YAML output or data formats):**

```markdown
## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  status: completed | blocked
  next_task_type: {Next Task Type}
  require_human_review: {Yes | No}
  task_output_links: [{output file paths}]
  # Dynamic attributes
  {attr_1}: {value}
  {attr_2}: {value}
```
```

**For flexible guidance (when adaptation is useful):**

```markdown
## Output Format

Here is a sensible default format, but use your best judgment:

# {Document Title}

## Overview
[Summary of what was accomplished]

## Details
[Adapt sections based on the specific task]

## Next Steps
[Tailor to the specific context]
```

## Examples Pattern

For skills where output quality depends on seeing examples, provide input/output pairs:

```markdown
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

4. Return Task Completion Output:
   status: completed
   next_task_type: Feature Breakdown
   require_human_review: Yes
   task_output_links:
     - x-ipe-docs/requirements/requirement-details.md

5. Resume Task Flow from task-execution-guideline skill
```
```

Examples help AI Agent understand the desired style and level of detail more clearly than descriptions alone.

## X-IPE Specific Output Patterns

### Task Type Default Attributes Table

Standard format for all task type skills:

```markdown
## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | {Task Type Name} |
| Category | {standalone | feature-stage | requirement-stage | ideation-stage} |
| Next Task Type | {Next Task Type | null} |
| Require Human Review | {Yes | No} |
```

### Definition of Done (DoD) Table

Standard format for exit criteria:

```markdown
## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | {Output created/updated} | Yes |
| 2 | {Verification passed} | Yes |
| 3 | {Optional checkpoint} | Recommended |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.
```

### Patterns Section Format

Standard format for common patterns:

```markdown
## Patterns

### Pattern: {Pattern Name}

**When:** {Condition that triggers this pattern}
**Then:**
```
1. {Action 1}
2. {Action 2}
3. {Action 3}
```

### Pattern: {Another Pattern}

**When:** {Condition}
**Then:**
```
1. {Action 1}
2. {Action 2}
```
```

### Anti-Patterns Table Format

Standard format for what to avoid:

```markdown
## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| {Bad practice 1} | {Reason} | {Better approach} |
| {Bad practice 2} | {Reason} | {Better approach} |
| {Bad practice 3} | {Reason} | {Better approach} |
```

### Status Symbols

Standard symbols for visual indicators:

| Symbol | Meaning | Usage |
|--------|---------|-------|
| ⛔ | Blocking rule | Critical rules that must not be skipped |
| ⚠️ | Warning | Important cautions |
| ✅ | Required/Complete | Mandatory items or completed status |
| 🔄 | In progress | Currently being worked on |
| ⏳ | Pending | Waiting to start |
| 🚫 | Blocked | Cannot proceed |
| ⏸️ | Deferred | Paused by human |
| ❌ | Cancelled | Stopped |
