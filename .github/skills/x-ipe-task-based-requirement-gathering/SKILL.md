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

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

MANDATORY: Every requirement MUST create an Epic with ID format `EPIC-{nnn}` (e.g., EPIC-001, EPIC-035). Features created during Feature Breakdown use format `FEATURE-{nnn}-{X}` (e.g., FEATURE-035-A). The `{nnn}` in Feature IDs always matches the parent Epic number.

⛔ **NEVER use an EPIC ID as a Feature ID.** `EPIC-{nnn}` identifies a grouping container; `FEATURE-{nnn}-{X}` identifies a deliverable unit of work. They are separate concepts. Do NOT place EPIC IDs in Feature ID columns, Feature List tables, or feature board entries.

> **Transition Note:** During migration, both old (`FEATURE-{nnn}/`) and new (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`) folder structures may coexist. Skills must handle both formats when scanning existing files.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Requirement Gathering"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    action: "requirement_gathering"  # workflow action name for status updates
    extra_context_reference:  # optional, default: N/A for all refs
      refined-idea: "path | N/A | auto-detect"
      mockup-html: "path | N/A | auto-detect"

  # Task type attributes
  category: "requirement-stage"
  next_task_based_skill: "Feature Breakdown"
  require_human_review: "yes"

  # Required inputs
  auto_proceed: false
  epic_id: "EPIC-{nnn}"  # Auto-assigned: scan x-ipe-docs/requirements/ for highest EPIC-{nnn}, next is EPIC-{nnn+1}
  mockup_list:
    - mockup_name: "Description of what function the mockup is for"
      mockup_link: "URL to the mockup"
    # or N/A if no mockups
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="epic_id" source="auto-assigned">
    <steps>
      1. Scan x-ipe-docs/requirements/ for existing EPIC-{nnn} folders
      2. Find the highest {nnn} value
      3. Assign EPIC-{nnn+1} (e.g., if EPIC-003 exists, assign EPIC-004)
      4. If no EPICs exist, assign EPIC-001
    </steps>
  </field>
  <field name="mockup_list" source="previous task | human input | N/A">
    <steps>
      1. Check previous task (Idea Mockup) output for task_output_links
      2. If not available, ask human for mockup links
      3. If none provided, set to N/A
    </steps>
  </field>
  <field name="extra_context_reference" source="workflow context | auto-detect">
    <steps>
      1. If workflow-mode: read from workflow context extra_context_reference
      2. If free-mode: auto-detect from existing project files
      3. Default: N/A for all refs
    </steps>
  </field>
</input_init>
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
      0. Resolve extra_context_reference inputs:
         - FOR EACH ref in [refined-idea, mockup-html]:
           IF workflow mode AND extra_context_reference.{ref} is a file path:
             READ the file at that path
           ELIF extra_context_reference.{ref} is "auto-detect":
             Use existing discovery logic
           ELIF extra_context_reference.{ref} is "N/A":
             Skip this context input
           ELSE (free-mode / absent):
             Use existing behavior
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
           > - **New Feature Ref:** EPIC-{nnn} — see {requirement-details-part-N.md}
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
      1. Create Epic folder structure:
         - Create x-ipe-docs/requirements/EPIC-{nnn}/ directory
         - Create x-ipe-docs/requirements/EPIC-{nnn}/mockups/ sub-directory
         - If mockup_list is provided, copy mockups to EPIC-{nnn}/mockups/
      2. Use [references/requirement-details-template.md](references/requirement-details-template.md) as template for new files
      3. Use ## EPIC-{nnn}: {Epic Title} as the section header in requirement-details (NOT ## FEATURE-{nnn})
      4. Fill all sections based on gathered information
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
      - MANDATORY: All internal markdown links MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). Do NOT use relative paths like `../` or `./`.
    </constraints>
    <output>requirement-details.md created or updated</output>
  </step_6>

  <step_7>
    <name>Complete</name>
    <action>
      1. IF execution_mode == "workflow-mode":
         a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
            - workflow_name: {from context}
            - action: {workflow.action}
            - status: "done"
            - deliverables: {"requirement-doc": "{path to requirement doc}", "requirements-folder": "{path to requirements/ folder}"}
         b. Log: "Workflow action status updated to done"
      2. Verify all DoD checkpoints
      3. Request human review
    </action>
    <output>Task completion output, workflow_action_updated</output>
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
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"       # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  task_output_links:
    - "x-ipe-docs/requirements/requirement-details.md"  # or requirement-details-part-X.md
  mockup_list: "{inherited from input or N/A}"
  # Dynamic attributes
  requirement_summary_updated: true | false
  requirement_details_part: 1  # current active part number
  conflict_review_completed: true | false
  conflicts_found: 0  # number of conflicts identified
  impacted_features: []  # list of FEATURE-XXX IDs marked with CR impact
  epic_id: "EPIC-{nnn}"  # The Epic created by this requirement gathering
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
  <checkpoint required="if-applicable">
    <name>Workflow Action Status Updated</name>
    <verification>If execution_mode == "workflow-mode", called the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with status "done" and deliverables keyed dict</verification>
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

### Pattern: Epic Folder Creation

**When:** Creating any new requirement
**Then:**
```
1. Determine next EPIC-{nnn} (scan x-ipe-docs/requirements/ for highest existing)
2. Create EPIC-{nnn}/ folder
3. Create EPIC-{nnn}/mockups/ sub-directory
4. Store any mockups in EPIC-{nnn}/mockups/
5. Write requirement-details section with ## EPIC-{nnn}: {Title} header
6. Note: Feature sub-folders are created later during Feature Breakdown
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

See [references/examples.md](.github/skills/x-ipe-task-based-requirement-gathering/references/examples.md) for concrete execution examples.
