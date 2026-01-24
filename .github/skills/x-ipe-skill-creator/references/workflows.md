# Workflow Patterns

## Sequential Workflows

For complex tasks, break operations into clear, sequential steps. It is often helpful to give AI Agent an overview of the process towards the beginning of SKILL.md:

```markdown
Execute {Task Type Name} by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Analyze | Parse input and understand scope | Understanding complete |
| 2 | Plan | Create execution plan | Plan approved |
| 3 | Execute | Perform the main action | Execution complete |
| 4 | Verify | Check results against criteria | Verification passed |
| 5 | Complete | Finalize and output results | Done |
```

## Conditional Workflows

For tasks with branching logic, guide AI Agent through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## X-IPE Specific Workflow Patterns

### Task Type Execution Flow

Every task type skill should include an Execution Flow table:

```markdown
## Execution Flow

Execute {Task Type Name} by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | {Name} | {Brief action} | {Gate condition} |
| 2 | {Name} | {Brief action} | {Gate condition} |
| 3 | Complete | Verify DoD, request human review | Human review |

**⛔ BLOCKING RULES:**
- {Rule 1}: {Description}
- {Rule 2}: {Description}
```

### Operation-Based Workflows (Skill Category)

For skills that provide CRUD operations:

```markdown
## Operations

### Operation 1: {Name}

**When:** {Trigger condition}
**Then:** {What happens}

```
1. {Step 1}
2. {Step 2}
3. Return {result}
```

### Operation 2: {Name}

**When:** {Trigger condition}
**Then:** {What happens}

```
Input: {Input description}

Process:
1. {Step 1}
2. IF {condition}:
   → {Action A}
   ELSE:
   → {Action B}
3. {Step 3}
```
```

### Blocking Rules Pattern

Use for critical checkpoints that must not be skipped:

```markdown
**⛔ BLOCKING RULES:**
- Step 3: Continue asking until ALL ambiguities resolved
- Step 5 → Human Review: Human MUST approve before proceeding
- Step 2: MUST validate input before processing
```

### Gate Conditions

Common gate condition patterns:

| Gate Type | Example |
|-----------|---------|
| Completion | "Document created", "Analysis complete" |
| Validation | "All tests pass", "Schema valid" |
| Approval | "Human review", "Approval received" |
| Threshold | "Coverage ≥ 80%", "Score > 0.9" |
