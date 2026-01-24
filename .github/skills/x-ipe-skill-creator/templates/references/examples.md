# {Skill Name} - Examples

> This file contains detailed execution examples for the {skill-name} skill.
> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: {Scenario Name}

**Request:** "{Example request from user}"

**Context:**
- {Relevant context 1}
- {Relevant context 2}

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. {Step 1 - DoR Check}:
   - Verify prerequisite 1: ✓
   - Verify prerequisite 2: ✓

3. {Step 2 - Main Action}:
   - {Detail 1}
   - {Detail 2}
   - {Detail 3}

4. {Step 3 - Verification}:
   - Check output 1: ✓
   - Check output 2: ✓

5. Return Task Completion Output:
   status: completed
   category: {category}
   next_task_type: {Next Task Type}
   require_human_review: {Yes | No}
   task_output_links:
     - {output path 1}
     - {output path 2}

6. Resume Task Flow from task-execution-guideline skill
```

**Output Files Created:**
- `{path/to/output1}` - {description}
- `{path/to/output2}` - {description}

---

## Example 2: {Edge Case Scenario}

**Request:** "{Edge case request}"

**Context:**
- {Special condition 1}
- {Special condition 2}

**Execution:**
```
1. {Handle edge case step 1}
2. {Handle edge case step 2}
3. {Return appropriate output}
```

**Notes:**
- {Important consideration for this edge case}

---

## Example 3: {Error Handling Scenario}

**Request:** "{Request that triggers error path}"

**Context:**
- {Missing prerequisite or invalid state}

**Execution:**
```
1. DoR Check:
   - Prerequisite 1: ✗ NOT MET

2. BLOCKED - Cannot proceed
   - Reason: {why blocked}
   - Action: {what to do}

3. Return to human:
   "Cannot proceed with {task}. 
    Missing: {what's missing}
    Please: {action needed}"
```

---

## Template Notes

When creating examples for a new skill:

1. **Include at minimum:**
   - One happy path example (Example 1)
   - One edge case example (Example 2)
   - One error/blocked scenario (Example 3)

2. **Example structure:**
   - Request: What the user asked
   - Context: Relevant state/conditions
   - Execution: Step-by-step with checkmarks
   - Output: Files created and completion output

3. **Keep examples realistic:**
   - Use concrete file paths and values
   - Show actual output format
   - Include verification steps
