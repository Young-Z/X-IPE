---
name: x-ipe-meta-lesson-learned
description: Capture issues and feedback for skill improvement. Use when a skill execution had problems, human provides feedback, or agent observes suboptimal behavior. Triggers on requests like "capture lesson", "record issue", "this skill failed", "improve this skill". Records lessons in x-ipe-docs/skill-meta/{skill}/x-ipe-meta-lesson-learned.md for future skill updates.
---

# Lesson Learned

## Purpose

Capture issues, errors, and feedback to improve skills over time by:
1. Identifying which skill had the issue
2. Analyzing what went wrong (observed vs expected)
3. Documenting the correct behavior (ground truth)
4. Recording a structured lesson for future skill updates

---

## About

This meta skill operates on the X-IPE skill improvement loop. When a skill produces incorrect output, throws errors, or receives human feedback, this skill captures the lesson in a structured format that can be consumed during future skill updates.

### Key Concepts

- **Ground Truth** - The verified correct output or behavior, captured after manual fix or human clarification
- **Lesson Entry** - A structured record (LL-{NNN}) stored per-skill with observed/expected/ground-truth data
- **Improvement Proposal** - A suggested change (new AC, updated instruction, added example) derived from the lesson

### Scope

```yaml
operates_on:
  - "Skill execution issues and failures"
  - "Human feedback on skill output"
  - "Edge cases not covered by existing skills"

does_not_handle:
  - "Applying fixes to skills (handled by x-ipe-meta-skill-creator)"
  - "Automated detection of skill issues"
```

---

## Important Notes

BLOCKING: Do NOT proceed past Step 4 without ground truth. A lesson without ground truth cannot generate valid tests.

CRITICAL: Always assign severity (critical/major/minor/enhancement) so lessons can be prioritized during skill updates.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Primary input
  trigger: "Human request or agent-observed issue (e.g. 'capture lesson', 'this skill failed')"

  # Context (from current session)
  skill_name: "Name of skill that had the issue (auto-detected or asked)"
  task_id: "TASK-ID if available from current session"

  # Optional
  error_output: "Actual output or error message if available"
  fixed_output: "Manually corrected output if human already fixed it"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Issue identified</name>
    <verification>Human reported issue, agent observed failure, or feedback provided</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Skill exists</name>
    <verification>Target skill folder exists at .github/skills/{skill-name}/</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Task context available</name>
    <verification>TASK-ID or session context provides scenario details</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Identify Skill | Determine and verify target skill | Skill folder exists |
| 2 | Gather Context | Collect task ID, scenario, inputs | Context documented |
| 3 | Document Issue | Record observed vs expected behavior | Both behaviors captured |
| 4 | Capture Ground Truth | Get verified correct output | Ground truth confirmed |
| 5 | Propose Improvement | Suggest AC or instruction change | Proposal type selected |
| 6 | Save Lesson | Append entry to x-ipe-meta-lesson-learned.md | File updated with LL-{NNN} |

---

## Execution Procedure

```xml
<procedure name="x-ipe-meta-lesson-learned">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Identify Skill</name>
    <action>
      1. Determine which skill had the issue:
         - If context is clear: extract skill name from conversation
         - If unclear: ask user "Which skill had the issue?"
      2. Verify skill exists at .github/skills/{skill-name}/
      3. Check if x-ipe-docs/skill-meta/{skill-name}/ exists; create if missing
    </action>
    <constraints>
      - BLOCKING: If skill folder does not exist, abort with error
    </constraints>
    <output>Verified skill name and skill-meta folder path</output>
  </step_1>

  <step_2>
    <name>Gather Context</name>
    <action>
      1. Collect task ID from current session (if available)
      2. Document the scenario (what was being done)
      3. Record what inputs were provided to the skill
      4. Note skill version if known
    </action>
    <output>Context block with task_id, scenario, inputs, skill_version</output>
  </step_2>

  <step_3>
    <name>Document Issue</name>
    <action>
      1. Record observed behavior:
         - What the skill actually did
         - Include actual output or error messages if available
      2. Record expected behavior:
         - What the skill should have done
         - Be specific about correct behavior
    </action>
    <output>Observed vs expected behavior documentation</output>
  </step_3>

  <step_4>
    <name>Capture Ground Truth</name>
    <action>
      1. Ask: "What should the correct output look like?"
      2. Record the ground truth:
         - If human provides correction: record exactly as provided
         - If human fixed output manually: reference the fixed file path and key differences
         - If unclear: ask clarifying questions
    </action>
    <constraints>
      - BLOCKING: Do NOT proceed without ground truth
      - CRITICAL: Ground truth becomes the test case for validation
    </constraints>
    <output>Verified correct output or behavior</output>
  </step_4>

  <step_5>
    <name>Propose Improvement</name>
    <action>
      1. Classify the improvement type:
         - new_ac: issue reveals missing requirement -> add to acceptance_criteria
         - update_ac: existing AC is incomplete -> modify specific AC
         - update_instruction: skill procedure unclear -> target SKILL.md section
         - add_example: edge case not covered -> target references/examples.md
      2. IF issue is a missing section or validation gap: propose new_ac with specific acceptance criteria
         ELSE: propose update_instruction or add_example as appropriate
      3. Draft the proposed change with target location
    </action>
    <output>Improvement proposal with type, target, and description</output>
  </step_5>

  <step_6>
    <name>Save Lesson</name>
    <action>
      1. Read template from x-ipe-docs/skill-meta/templates/x-ipe-meta-lesson-learned.md (if exists)
      2. Generate unique lesson ID: LL-{NNN} (increment from last entry)
      3. Create lesson entry with status: raw and all gathered information
      4. Append to x-ipe-docs/skill-meta/{skill-name}/x-ipe-meta-lesson-learned.md
      5. If file did not exist: create with YAML frontmatter
    </action>
    <success_criteria>
      - Lesson entry has unique ID
      - All fields populated (context, observed, expected, ground_truth, proposal)
      - Severity assigned (critical/major/minor/enhancement)
      - Status set to raw
    </success_criteria>
    <output>Updated x-ipe-meta-lesson-learned.md file path</output>
  </step_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill: null
  require_human_review: "no"
  task_output_links:
    - "x-ipe-docs/skill-meta/{skill-name}/x-ipe-meta-lesson-learned.md"
  lesson_id: "LL-{NNN}"
  target_skill: "{skill-name}"
  severity: "{critical|major|minor|enhancement}"
  improvement_type: "{new_ac|update_ac|update_instruction|add_example}"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Skill identified and verified</name>
    <verification>Skill folder exists at .github/skills/{skill-name}/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Context documented</name>
    <verification>Task ID (if available), scenario, and inputs are recorded</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Issue described</name>
    <verification>Both observed and expected behavior are documented</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Ground truth captured</name>
    <verification>Verified correct output or behavior is recorded</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Improvement proposed</name>
    <verification>Proposal includes type, target, and description</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Lesson saved</name>
    <verification>x-ipe-meta-lesson-learned.md exists at x-ipe-docs/skill-meta/{skill-name}/ with new LL-{NNN} entry</verification>
  </checkpoint>
</definition_of_done>
```

---

## Templates

| File | Purpose | When to Use |
|------|---------|-------------|
| `x-ipe-docs/skill-meta/templates/x-ipe-meta-lesson-learned.md` | Lesson entry template | When creating a new x-ipe-meta-lesson-learned.md or appending entries |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
