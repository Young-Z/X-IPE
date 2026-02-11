---
name: x-ipe-task-based-requirement-gathering
description: Gather requirements from user requests and create requirement summary. Use when starting a new feature or receiving a new user request. Triggers on requests like "new feature", "add feature", "I want to build", "create requirement".
---

# Task-Based Skill: Requirement Gathering

## Purpose

Gather and document requirements from user requests by:
1. Understanding the user request
2. Asking clarifying questions
3. Reviewing existing requirements for conflicts/overlaps
4. Updating impacted features with CR markers
5. Creating requirement summary document
6. Preparing for Feature Breakdown

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
| 3 | Conflict Review | Scan existing requirements for conflicts/overlaps, ask human to decide | Human decision on each conflict |
| 4 | Update Impacted | Mark impacted features with CR notes in requirement-details files | Impacted features marked |
| 5 | Check File | Check if requirement-details needs splitting (>500 lines) | File ready |
| 6 | Document | Create/update `requirement-details.md` (or current part) | Document created |
| 7 | Complete | Verify DoD, request human review | Human review |

BLOCKING: Continue asking in Step 2 until ALL ambiguities are resolved.
BLOCKING: MUST split file in Step 5 if current part exceeds 500 lines before adding new content.
BLOCKING: Human MUST decide on each conflict in Step 3 before proceeding.
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
    <name>Conflict and Overlap Review</name>
    <action>
      1. Read requirement-details-index.md to get list of all requirement-details parts
      2. Scan each requirement-details file, extracting existing feature IDs and their scope (high-level requirements, FRs, constraints)
      3. Compare new requirements (from Steps 1-2) against each existing feature:
         - Functional overlap: new FRs that duplicate or contradict existing FRs
         - Scope overlap: new feature covers same user scenarios as existing feature
         - Dependency conflict: new feature changes behavior that existing feature depends on
      4. IF no conflicts/overlaps found:
         - Report "No conflicts found with existing requirements"
         - Proceed to Step 5 (skip Step 4)
      5. IF conflicts/overlaps found, for EACH conflict:
         - Present a conflict summary table to human:
           | Aspect | New Requirement | Existing Feature | Overlap Type |
           |--------|----------------|-----------------|--------------|
         - Provide recommendation based on these principles:
           a. Single Responsibility: If the new requirement extends the SAME responsibility → recommend CR on existing feature
           b. Cohesion: If the new requirement is functionally cohesive with existing feature (same domain, same users, same data) → recommend CR
           c. Independence: If the new requirement can stand alone with its own lifecycle → recommend new feature
           d. Minimal coupling: If merging would create tight coupling between unrelated concerns → recommend new feature
         - Ask human: "Should this be handled as a Change Request (CR) on {FEATURE-XXX}, or as a new standalone feature?"
      6. Record human decisions for each conflict
    </action>
    <constraints>
      - BLOCKING: Do not proceed until human has decided on EVERY conflict
      - CRITICAL: Always provide a recommendation with reasoning, do not just ask
      - CRITICAL: Scan ALL requirement-details parts, not just the latest
    </constraints>
    <output>Conflict review result: list of conflicts with human decisions (CR | new feature)</output>
  </step_3>

  <step_4>
    <name>Update Impacted Features</name>
    <requires>Conflict review result from Step 3</requires>
    <action>
      1. IF no conflicts were found in Step 3: skip this step entirely
      2. For each conflict where human decided "CR on existing feature":
         - Locate the feature in its requirement-details part file
         - Add a CR impact marker at the end of that feature's section:
           ```
           > **⚠️ CR Impact Note** (added {date}, ref: {new_feature_id})
           > - **Change:** {brief description of what changes}
           > - **Affected FRs:** {list of FR IDs that need updating}
           > - **Action Required:** Feature specification refactoring needed before implementation
           > - **New Feature Ref:** {FEATURE-XXX} — see {requirement-details-part-N.md}
           ```
         - Do NOT modify the existing FRs/ACs themselves — only add the marker
      3. For each conflict where human decided "new standalone feature":
         - Add a dependency note to the new requirement (in Step 6) referencing the related existing feature
         - No changes to existing requirement-details files
      4. Report summary of all updates made
    </action>
    <constraints>
      - CRITICAL: Do NOT modify existing FRs, ACs, or NFRs — only append CR impact markers
      - CRITICAL: Markers must include date, new feature reference, and action required
    </constraints>
    <output>List of impacted features and files updated</output>
  </step_4>

  <step_5>
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
  </step_5>

  <step_6>
    <name>Create Requirement Details Document</name>
    <action>
      1. Use [references/requirement-details-template.md](references/requirement-details-template.md) as template for new files
      2. Fill all sections based on gathered information
      3. Include all clarifications and decisions from Step 2
      4. IF conflicts were found in Step 3:
         - Add a "Related Features" section listing all overlapping features and human decisions
         - For "CR" decisions: note that existing feature has CR impact markers
         - For "new feature" decisions: add cross-reference dependency
      5. Add new content to the current active part file
    </action>
    <constraints>
      - CRITICAL: Document the "why" behind requirements, not just the "what"
      - CRITICAL: Be thorough - vague requirements lead to incorrect implementations
      - CRITICAL: Include examples and edge cases discussed with the human
      - CRITICAL: Capture constraints, assumptions, and dependencies
    </constraints>
    <output>requirement-details.md created or updated</output>
  </step_6>

  <step_7>
    <name>Complete</name>
    <action>
      1. Verify all DoD checkpoints
      2. Request human review
    </action>
    <output>Task completion output</output>
  </step_7>

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
  conflict_review_completed: true | false
  conflicts_found: 0  # number of conflicts identified
  impacted_features: []  # list of FEATURE-XXX IDs marked with CR impact
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
  <checkpoint required="true">
    <name>Conflict review completed</name>
    <verification>All existing requirement-details files scanned for overlaps; conflicts (if any) presented to human with decisions recorded</verification>
  </checkpoint>
  <checkpoint required="conditional">
    <name>Impacted features marked</name>
    <verification>If conflicts found with CR decision, affected features have CR impact markers appended in their requirement-details files</verification>
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
3. Review conflicts, then create requirement summary
```

### Pattern: Detailed Request

**When:** User gives detailed request with clear scope
**Then:**
```
1. Confirm understanding with user
2. Ask about edge cases only
3. Review conflicts, then create requirement summary
```

### Pattern: Existing Project Addition

**When:** Adding feature to existing project
**Then:**
```
1. Read existing requirement-details.md
2. Understand current scope
3. Scan for conflicts/overlaps with new request
4. Ask human to decide CR vs new feature for each overlap
5. Mark impacted features, then create requirement summary
```

### Pattern: Overlap with Existing Feature

**When:** New requirement overlaps an existing feature's scope
**Then:**
```
1. Present overlap table showing new vs existing
2. Recommend based on principles:
   - Same responsibility/cohesion → CR on existing
   - Independent lifecycle → new feature
3. Wait for human decision
4. Add CR impact marker or cross-reference dependency
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Assuming requirements | Missing features | Ask clarifying questions |
| Skipping documentation | Lost context | Always create requirement-details.md |
| Too many questions at once | Overwhelms human | Batch 3-5 questions |
| Skip to Feature Breakdown | Missing requirements | Complete this task first |
| Skipping conflict review | Duplicate/conflicting features | Always scan existing requirements |
| Modifying existing FRs during impact update | Breaks existing specs | Only append CR impact markers |
| Deciding CR vs new feature without human | Wrong architectural decision | Always ask human with recommendation |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
