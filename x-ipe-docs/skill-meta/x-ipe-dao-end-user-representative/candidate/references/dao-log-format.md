# DAO Semantic Log Format

## File Naming
- Target: `x-ipe-docs/dao/decisions_made_{semantic_task_type}.md`
- semantic_task_type derived from calling_skill (e.g., "bug-fix" → "bug_fix")

## Entry ID
- Format: DAO-{NNN} (zero-padded 3 digits, starting at DAO-001)
- Read existing registry table to determine next ID

## Registry Table Row

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|

## Detail Section

```
## {Entry ID}
- **Timestamp:** {ISO 8601}
- **Task ID:** {task_id}
- **Feature ID:** {feature_id or N/A}
- **Workflow:** {workflow_name or N/A}
- **Calling Skill:** {calling_skill}
- **Source:** {source}
- **Disposition:** {disposition}
- **Confidence:** {confidence}

### Message
> {original message content}

### Guidance Returned
> {DAO response content}

### Rationale
> {rationale_summary}

### Suggested Skills
> suggested_skills:   # from Step 2.1 — may be empty list
>   - skill_name: "x-ipe-task-based-{name}"
>     match_strength: "strong | partial"
>     reason: "why this skill matches the input"
>     execution_steps:
>       - phase: "1. Phase Name"
>         step: "1.1 Step Name"

### Follow-up
> {follow-up or "None"}
```
