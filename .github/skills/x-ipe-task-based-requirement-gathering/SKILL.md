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

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-requirement-gathering"

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
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-breakdown"
      condition: "Break requirements into features"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
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
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
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
      1. Check previous task (Idea Mockup) output for mockup_list (array of {mockup_name, mockup_link})
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

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Understand User Request, 1.2 Domain & Context Research | Parse what/who/why, research domain standards and competitors | Domain context established |
| 2. 审问之 — Inquire Thoroughly | 2.1 Ask Clarifying Questions, 2.2 Conflict and Overlap Review | Resolve ambiguities, scan existing requirements for conflicts | All questions answered, conflicts decided |
| 3. 慎思之 — Think Carefully | 3.1 Feasibility & Risk Reflection | Assess technical feasibility, identify risks and constraints | Risks documented |
| 4. 明辨之 — Discern Clearly | 4.1 Update Impacted Features, 4.2 Scope Decision | Mark impacted features, finalize in/out scope boundaries | Scope decided |
| 5. 笃行之 — Practice Earnestly | 5.1 Create Requirement Document, 5.2 Complete & Verify | Create/update requirement-details, verify DoD | Document created |
| 继续执行 | 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: Continue asking in Phase 2 until ALL ambiguities are resolved.
BLOCKING: Each conflict in step 2.2 MUST be decided before proceeding (manual/stop_for_question: human decides; auto: x-ipe-dao-end-user-representative decides).
BLOCKING (manual/stop_for_question): Human MUST confirm requirements are complete before proceeding to Feature Breakdown.
BLOCKING (auto): Proceed automatically after DoD verification.

---

## Execution Procedure

```xml
<procedure name="requirement-gathering">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
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
      </action>
      <constraints>
        - CRITICAL: Do not skip scope identification
      </constraints>
      <output>Initial understanding summary</output>
    </step_1_1>

    <step_1_2>
      <name>Domain & Context Research</name>
      <action>
        1. IF domain knowledge is insufficient: use web search to research industry standards, competitor features, domain terminology, and regulatory requirements
        2. Research best practices for similar features in the domain
        3. Check for compliance requirements (GDPR, PCI-DSS, HIPAA if applicable)
        4. Document key domain concepts and terminology discovered
      </action>
      <constraints>
        - CRITICAL: Research before questioning — informed questions lead to better requirements
      </constraints>
      <output>Domain context summary with key standards and terminology</output>
    </step_1_2>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Ask Clarifying Questions</name>
      <action>
        1. Identify ambiguities across: Scope, Users, Edge Cases, Priorities, Constraints
        2. Ask questions in batches of 3-5 to avoid overwhelming
        3. Wait for response before next batch
        4. Document answers immediately
        5. Repeat until all ambiguities are resolved

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Resolve ambiguities via x-ipe-dao-end-user-representative
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human for responses
      </action>
      <constraints>
        - BLOCKING: Do not proceed until ALL ambiguities are resolved
        - BLOCKING (manual/stop_for_question): Do not make assumptions - always ask
        - BLOCKING (auto): Resolve ambiguities via x-ipe-dao-end-user-representative - never stop to ask human
      </constraints>
      <output>Complete set of clarified requirements</output>
    </step_2_1>

    <step_2_2>
      <name>Conflict and Overlap Review</name>
      <action>
        1. Read requirement-details-index.md to get list of all requirement-details parts
        2. Scan each requirement-details file, extracting existing feature IDs and their scope
        3. Compare new requirements against each existing feature:
           - Functional overlap: new FRs that duplicate or contradict existing FRs
           - Scope overlap: new feature covers same user scenarios
           - Dependency conflict: new feature changes behavior existing feature depends on
        4. IF no conflicts: report "No conflicts found" and proceed to Phase 3
        5. IF conflicts found, for EACH conflict:
           - Present conflict summary table
           - Provide recommendation based on: Single Responsibility, Cohesion, Independence, Minimal Coupling
           - Ask "CR on existing or new standalone feature?"

             Response source (based on interaction_mode):
             IF process_preference.interaction_mode == "dao-represent-human-to-interact":
               → Resolve via x-ipe-dao-end-user-representative
             ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
               → Ask human for decision
        6. Record decisions for each conflict
      </action>
      <constraints>
        - BLOCKING: Do not proceed until EVERY conflict is decided (manual/stop_for_question: human decides; auto: x-ipe-dao-end-user-representative decides)
        - CRITICAL: Scan ALL requirement-details parts, not just the latest
      </constraints>
      <output>Conflict review result with human decisions</output>
    </step_2_2>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">

    <step_3_1>
      <name>Feasibility & Risk Reflection</name>
      <action>
        1. Assess technical feasibility of gathered requirements
        2. Identify potential risks: technical complexity, dependencies, integration challenges
        3. Consider resource constraints and timeline implications
        4. Document assumptions that need validation during design
        5. IF high-risk items found: flag for human attention with mitigation suggestions
      </action>
      <constraints>
        - CRITICAL: Do not filter out requirements — document risks alongside them
      </constraints>
      <output>Feasibility assessment with documented risks and assumptions</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>Update Impacted Features</name>
      <action>
        1. IF no conflicts were found in Phase 2: skip this step
        2. For each "CR" decision:
           a. Add CR impact marker to feature (append only)
           b. Resolve conflicting documents (applies regardless of human or interaction_mode resolution):
              - IF minor conflict (wording overlap, small scope adjustment, additive change):
                → Directly update the conflicting sections in the target requirement-details
              - IF major conflict (contradicting FRs, structural scope overlap, fundamental redesign):
                → Mark affected sections in target requirement-details with "[RETIRED by EPIC-{nnn}]" header
                → Add retirement note: reason, date, and reference to new EPIC
        3. For each "new feature" decision: add dependency note to new requirement
        4. Report summary of updates including docs updated inline and docs marked retired
      </action>
      <constraints>
        - CRITICAL: Do NOT modify existing FRs/ACs beyond CR impact markers and conflict resolution
        - CRITICAL: Conflicting documents MUST be handled — minor conflicts updated inline, major conflicts marked retired
      </constraints>
      <output>List of impacted features, files updated, docs retired</output>
    </step_4_1>

    <step_4_2>
      <name>Scope Decision</name>
      <action>
        1. Review all gathered requirements, conflicts, and feasibility assessment
        2. Explicitly define what is IN scope and OUT of scope
        3. Present scope summary for confirmation

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Resolve via x-ipe-dao-end-user-representative, log rationale
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human for confirmation
        4. Document final scope boundaries
      </action>
      <output>Final scope boundaries (in-scope and out-of-scope items)</output>
    </step_4_2>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Create Requirement Document</name>
      <action>
        1. Determine current active file, check if >500 lines → split per file-splitting procedure
        2. Create Epic folder structure (EPIC-{nnn}/ and mockups/ sub-directory)
        3. Copy mockups if provided
        4. Use requirement-details-template.md, use ## EPIC-{nnn}: {Title} as header
        5. Fill all sections based on gathered information including feasibility notes
        6. IF conflicts found: add "Related Features" section
        7. Add new content to current active part file
      </action>
      <constraints>
        - BLOCKING: MUST split before adding new content if over 500-line threshold
        - CRITICAL: Document the "why", not just the "what"
        - MANDATORY: File links in generated markdown MUST use project-root-relative paths so the UI can intercept them and open a preview modal. **Avoid** relative paths (`../`, `./`, `../../`) and absolute filesystem paths (`/Users/...`). **Correct:** `[spec](x-ipe-docs/requirements/EPIC-001/specification.md)`, `[skill](.github/skills/x-ipe-task-based-bug-fix/SKILL.md)`. **Wrong:** `[spec](../specification.md)`, `[spec](./specification.md)`.
      </constraints>
      <output>requirement-details.md created or updated</output>
    </step_5_1>

    <step_5_2>
      <name>Complete & Verify</name>
      <action>
        1. IF execution_mode == "workflow-mode":
           a. Call update_workflow_action with:
              - workflow_name, action, status: "done"
              - deliverables: {"requirement-doc": "{path}", "requirements-folder": "{path}"}
           b. Log: "Workflow action status updated to done"
        2. Verify all DoD checkpoints
        3. IF manual/stop_for_question:
              → Present requirements document to human
              → Ask if any requirements are missing, incorrect, or unclear
              → IF human identifies issues → revise specific sections
      </action>
      <output>Task completion output, workflow_action_updated</output>
    </step_5_2>

  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (interact-with-human):
          → Present next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (manual): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_6_1>
    <step_6_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 6.1:
        1. Load the target task-based skill's SKILL.md
        2. Generate an execution plan from the skill's Execution Flow table
        3. Start execution from the skill's first phase/step
      </action>
      <constraints>
        - MUST load the skill before executing — do not skip skill loading
        - Execution follows the target skill's procedure, not this skill's
      </constraints>
      <output>Next task execution started</output>
    </step_6_2>
  </phase_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "requirement-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-breakdown"
      condition: "Break requirements into features"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
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
  conflicting_docs_updated: []          # Docs updated inline for minor conflicts
  conflicting_docs_retired: []          # Doc sections marked retired for major conflicts
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
    <verification>All existing requirement-details files scanned for overlaps; conflicts (if any) decided and recorded (manual/stop_for_question: human decides; auto: DAO decides)</verification>
  </checkpoint>
  <checkpoint required="conditional">
    <name>Impacted features marked</name>
    <verification>If conflicts found with CR decision, affected features have CR impact markers appended in their requirement-details files</verification>
  </checkpoint>
  <checkpoint required="conditional">
    <name>Conflicting documents resolved</name>
    <verification>If conflicts found: minor conflicts updated inline in target docs, major conflicts have sections marked "[RETIRED by EPIC-{nnn}]" with replacement content</verification>
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

| Pattern | When | Then |
|---------|------|------|
| Vague Request | Unclear request like "build login" | Ask clarifying questions (auth methods, password reset, security) |
| Detailed Request | Clear scope already provided | Confirm understanding, ask edge cases only |
| Existing Project | Adding feature to existing project | Scan for conflicts/overlaps, ask human CR vs new feature |
| Overlap Found | Requirement overlaps existing feature | Present overlap table, recommend CR or new based on responsibility/cohesion |
| Epic Folder Creation | Any new requirement | Determine next EPIC-{nnn}, create folder + mockups/, write requirement-details |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Assuming requirements | Missing features | Ask clarifying questions |
| Skipping documentation | Lost context | Always create requirement-details.md |
| Too many questions at once | Overwhelms human | Batch 3-5 questions |
| Skipping conflict review | Duplicate/conflicting features | Always scan existing requirements |
| Modifying existing FRs | Breaks existing specs | Only append CR impact markers + resolve conflicts |
| Deciding CR vs new without human | Wrong architectural decision | Always ask human with recommendation (manual/stop_for_question); use DAO in auto mode |
| Leave conflicting docs unresolved | Stale docs mislead future work | Minor → update inline; major → mark retired |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-requirement-gathering/references/examples.md) for concrete execution examples.
