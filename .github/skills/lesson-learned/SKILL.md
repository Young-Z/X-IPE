---
name: lesson-learned
description: Capture issues and feedback for skill improvement. Use when a skill execution had problems, human provides feedback, or agent observes suboptimal behavior. Triggers on requests like "capture lesson", "record issue", "this skill failed", "improve this skill". Records lessons in x-ipe-docs/skill-meta/{skill}/lesson-learned.md for future skill updates.
---

# Lesson Learned

Capture issues and feedback to improve skills over time.

## Purpose

This skill captures issues, errors, and feedback for specific skills by:
1. Identifying which skill had the issue
2. Analyzing what went wrong
3. Documenting the correct behavior (ground truth)
4. Recording a structured lesson for future skill updates

---

## Important Notes

- **Manual trigger only** (for now) - human must say "capture lesson" or similar
- Lessons are stored per-skill in `x-ipe-docs/skill-meta/{skill-name}/lesson-learned.md`
- Lessons are consumed by `x-ipe-skill-creator` when updating skills
- Ground truth is critical - always capture what the correct output should be

---

## Execution Flow

| Step | Action | Output |
|------|--------|--------|
| 1 | Identify skill | Skill name that had the issue |
| 2 | Gather context | Task ID, scenario, inputs |
| 3 | Document issue | Observed vs expected behavior |
| 4 | Capture ground truth | Correct output (after manual fix) |
| 5 | Propose improvement | Suggested AC or instruction change |
| 6 | Save lesson | lesson-learned.md updated |

---

## Execution Procedure

### Step 1: Identify Skill

Determine which skill had the issue:

```
1. Ask: "Which skill had the issue?"
   - If context clear: extract skill name
   - If unclear: ask user to specify
   
2. Verify skill exists:
   - Check .github/skills/{skill-name}/
   - If not exists: abort with error
   
3. Check/create skill-meta folder:
   - If x-ipe-docs/skill-meta/{skill-name}/ not exists: create it
```

### Step 2: Gather Context

Collect information about when the issue occurred:

```yaml
context:
  task_id: "{TASK-ID if available}"
  scenario: "{What was being done}"
  inputs: "{What inputs were provided to the skill}"
  skill_version: "{Current skill version if known}"
```

### Step 3: Document Issue

Record what went wrong:

```yaml
observed_behavior: |
  {What the skill actually did}
  - Include actual output if available
  - Include error messages if any
  
expected_behavior: |
  {What the skill should have done}
  - Be specific about correct behavior
```

### Step 4: Capture Ground Truth

**Critical step** - This becomes the test case for validation:

```
1. Ask: "What should the correct output look like?"

2. If human provides correction:
   - Record exactly as provided
   
3. If human fixed output manually:
   - Reference the fixed file path
   - Record the key differences
   
4. If unclear:
   - Ask clarifying questions
   - Do NOT proceed without ground truth
```

### Step 5: Propose Improvement

Suggest how to improve the skill:

| Improvement Type | When to Use | Target |
|------------------|-------------|--------|
| `new_ac` | Issue reveals missing requirement | Add to skill-meta acceptance_criteria |
| `update_ac` | Existing AC is incomplete | Modify specific AC |
| `update_instruction` | Skill procedure unclear | SKILL.md section |
| `add_example` | Edge case not covered | references/examples.md |

### Step 6: Save Lesson

Append to or create lesson-learned.md:

```
1. Read template: x-ipe-docs/skill-meta/templates/lesson-learned.md
2. Generate unique lesson ID: LL-{NNN}
3. Create lesson entry with:
   - status: raw
   - All gathered information
4. Append to x-ipe-docs/skill-meta/{skill-name}/lesson-learned.md
5. If file didn't exist: create with YAML frontmatter
```

---

## Definition of Done

| Checkpoint | Required |
|------------|----------|
| Skill identified and verified | Yes |
| Context documented | Yes |
| Issue described (observed vs expected) | Yes |
| Ground truth captured | Yes |
| Improvement proposed | Yes |
| Lesson saved to lesson-learned.md | Yes |

---

## Patterns

### Pattern: Error During Execution

**When:** Skill threw an error or failed
**Then:**
```
1. Capture error message/stack trace
2. Document what operation caused the error
3. Record expected behavior: "Should complete without error"
4. Propose: update_instruction to handle edge case
```

### Pattern: Wrong Output Format

**When:** Skill produced output but format was wrong
**Then:**
```
1. Save actual output (or screenshot/snippet)
2. Show expected format
3. Record ground truth with correct format
4. Propose: new_ac for format validation
```

### Pattern: Missing Content

**When:** Skill output was incomplete
**Then:**
```
1. List what was missing
2. Provide complete expected content
3. Record ground truth with all content
4. Propose: update_ac to require missing content
```

### Pattern: Human Feedback

**When:** Human says "this is wrong" or provides feedback
**Then:**
```
1. Ask: "What specifically is wrong?"
2. Ask: "What should it be instead?"
3. Record feedback as ground truth
4. Propose improvement based on feedback
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Recording without ground truth | Can't generate valid tests | Always capture correct output |
| Vague issue description | Hard to fix skill | Be specific about observed vs expected |
| Not linking to task ID | Lose context | Always include TASK-ID if available |
| Skipping severity | Can't prioritize | Always assign critical/major/minor/enhancement |

---

## Example

See [references/examples.md](references/examples.md) for execution examples.
