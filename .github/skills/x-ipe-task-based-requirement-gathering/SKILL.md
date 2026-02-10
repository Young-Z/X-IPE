---
name: x-ipe-task-based-requirement-gathering
description: Gather requirements from user requests and create requirement summary. Use when starting a new feature or receiving a new user request. Triggers on requests like "new feature", "add feature", "I want to build", "create requirement".
---

# Task-Based Skill: Requirement Gathering

## Purpose

Gather and document requirements from user requests by:
1. Understanding the user request
2. Asking clarifying questions
3. Creating requirement summary document
4. Preparing for Feature Breakdown

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

MANDATORY: Every feature mentioned or identified in the output MUST have a feature ID in the format `FEATURE-{nnn}` (e.g., FEATURE-001, FEATURE-027). This applies regardless of the output language used.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Requirement Gathering"

  # Task type attributes
  category: "requirement-stage"
  next_task_based_skill: "Feature Breakdown"
  require_human_review: "yes"

  # Required inputs
  auto_proceed: false
  mockup_list:
    - mockup_name: "Description of what function the mockup is for"
      mockup_link: "URL to the mockup"
    # or N/A if no mockups
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>User request received</name>
    <verification>A user request or feature idea has been communicated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human available for clarification</name>
    <verification>Human is reachable to answer follow-up questions</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>AI Agent has no more clarifying questions</name>
    <verification>All ambiguities resolved before documenting</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Understand | Parse what, who, why from user request (optional: web research) | Initial understanding |
| 2 | Clarify | Ask clarifying questions (3-5 at a time) | All questions answered |
| 3 | Check File | Check if requirement-details needs splitting (>500 lines) | File ready |
| 4 | Document | Create/update `requirement-details.md` (or current part) | Document created |
| 5 | Complete | Verify DoD, request human review | Human review |

BLOCKING: Continue asking in Step 2 until ALL ambiguities are resolved.
BLOCKING: MUST split file in Step 3 if current part exceeds 500 lines before adding new content.
BLOCKING: Human MUST approve requirements before proceeding to Feature Breakdown.

---

## Execution Procedure

```xml
<procedure name="requirement-gathering">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Understand User Request</name>
    <action>
      1. Identify WHAT is being requested
      2. Identify WHO will use the feature
      3. Identify WHY this is needed (business value)
      4. Note any constraints mentioned
      5. IF domain knowledge is insufficient: use web search to research industry standards, competitor features, domain terminology, and regulatory requirements
    </action>
    <constraints>
      - CRITICAL: Do not skip scope identification
    </constraints>
    <output>Initial understanding summary</output>
  </step_1>

  <step_2>
    <name>Ask Clarifying Questions</name>
    <action>
      1. Identify ambiguities across: Scope, Users, Edge Cases, Priorities, Constraints
      2. Ask questions in batches of 3-5
      3. Wait for human response before next batch
      4. Document answers immediately
      5. Repeat until all ambiguities are resolved
    </action>
    <constraints>
      - BLOCKING: Do not proceed until ALL ambiguities are resolved
      - BLOCKING: Do not make assumptions - always ask
      - CRITICAL: Unless Human enforces, do not skip any clarifications
    </constraints>
    <output>Complete set of clarified requirements</output>
  </step_2>

  <step_3>
    <name>Check File Size and Split if Needed</name>
    <action>
      1. Determine current active file (requirement-details.md or latest part)
      2. Count lines in current active file
      3. If > 500 lines, split per file-splitting procedure
    </action>
    <constraints>
      - BLOCKING: MUST split before adding new content if over threshold
    </constraints>

    <output>Active file path determined</output>
  </step_3>

  <step_4>
    <name>Create Requirement Details Document</name>
    <action>
      1. Use [references/requirement-details-template.md](references/requirement-details-template.md) as template for new files
      2. Fill all sections based on gathered information
      3. Include all clarifications and decisions from Step 2
      4. Add new content to the current active part file
    </action>
    <constraints>
      - CRITICAL: Document the "why" behind requirements, not just the "what"
      - CRITICAL: Be thorough - vague requirements lead to incorrect implementations
      - CRITICAL: Include examples and edge cases discussed with the human
      - CRITICAL: Capture constraints, assumptions, and dependencies
    </constraints>
    <output>requirement-details.md created or updated</output>
  </step_4>

  <step_5>
    <name>Complete</name>
    <action>
      1. Verify all DoD checkpoints
      2. Request human review
    </action>
    <output>Task completion output</output>
  </step_5>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "requirement-stage"
  status: completed | blocked
  next_task_based_skill: "Feature Breakdown"
  require_human_review: "yes"
  auto_proceed: "{from input auto_proceed}"
  task_output_links:
    - "x-ipe-docs/requirements/requirement-details.md"  # or requirement-details-part-X.md
  mockup_list: "{inherited from input or N/A}"
  # Dynamic attributes
  requirement_summary_updated: true | false
  requirement_details_part: 1  # current active part number
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Requirement details document created or updated</name>
    <verification>x-ipe-docs/requirements/requirement-details.md (or current part) exists and is populated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All clarifying questions answered</name>
    <verification>No open ambiguities remain in the requirement document</verification>
  </checkpoint>
  <checkpoint required="conditional">
    <name>File split handled correctly</name>
    <verification>If split occurred, old file renamed and index updated per references/file-splitting.md</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

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

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Assuming requirements | Missing features | Ask clarifying questions |
| Skipping documentation | Lost context | Always create requirement-details.md |
| Too many questions at once | Overwhelms human | Batch 3-5 questions |
| Skip to Feature Breakdown | Missing requirements | Complete this task first |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
