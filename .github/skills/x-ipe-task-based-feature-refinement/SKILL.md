---
name: x-ipe-task-based-feature-refinement
description: Refine feature specification for a single feature. Queries feature board for context, creates/updates specification document. Use when a feature needs detailed requirements. Triggers on requests like "refine feature", "detail specification", "clarify requirements".
---

# Task-Based Skill: Feature Refinement

## Purpose

Refine feature requirements for a single feature by:
1. Querying feature board for full Feature Data Model
2. Creating/updating detailed feature specification
3. Documenting user stories, acceptance criteria, and requirements
4. NO board status update (handled by category skill)

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**BLOCKING: Single Feature Only.** This skill operates on exactly ONE feature at a time. Do NOT batch or combine multiple features in a single execution. If multiple features need processing, run this skill separately for each feature.

MANDATORY: Every feature MUST have a feature ID in the format `FEATURE-{nnn}` (e.g., FEATURE-001, FEATURE-027). This applies regardless of the output language used.

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Feature Refinement"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      requirement-doc: "path | N/A | auto-detect"
      features-list: "path | N/A | auto-detect"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "Technical Design"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  feature_phase: "Feature Refinement"

  # Required inputs
  mockup_list: "N/A"  # Path to mockup file(s) from previous Idea Mockup task or context

  # Context (from previous task or project)
  feature_id: "{FEATURE-XXX}"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.auto_proceed" source="from caller (x-ipe-workflow-task-execution) or default 'manual'" />
  <field name="feature_id" source="previous task (Feature Breakdown) output OR task board OR human input">
    <steps>
      1. IF previous task was "Feature Breakdown" → extract from task_output_links.feature_ids
      2. ELIF task board has feature_id in task data → use it
      3. ELSE → IF auto_proceed == "auto": derive from workflow context or x-ipe-dao-end-user-representative; ELSE: ask human for feature_id
    </steps>
  </field>
  <field name="extra_context_reference" source="workflow context OR auto-detect">
    <steps>
      1. IF workflow-mode → use workflow.extra_context_reference values
      2. FOR EACH ref in [requirement-doc, features-list]:
         IF ref is a file path → use it
         ELIF "auto-detect" → use existing discovery logic
         ELIF "N/A" → skip
      3. ELSE (free-mode) → use existing behavior
    </steps>
  </field>
  <field name="mockup_list" source="see Mockup List Resolution section below">
    <steps>
      1. IF previous task was "Idea Mockup" → extract from task_output_links
      2. ELIF human provides explicit path → use human-provided value
      3. ELIF idea-summary-vN.md exists → extract from "Mockups &amp; Prototypes" section
      4. ELSE → set to "N/A"
    </steps>
  </field>
</input_init>
```

### Mockup List Resolution

The `mockup_list` value is resolved in this priority order:

1. IF previous task was "Idea Mockup" -- extract from previous task's `task_output_links`
2. ELSE IF human provides explicit path -- use human-provided value
3. ELSE IF `idea-summary-vN.md` exists -- extract from "Mockups & Prototypes" section
4. ELSE -- set to N/A

MANDATORY: When `mockup_list` is provided, analyze mockups during Step 2 and extract UI/UX requirements into the specification.

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Feature exists on feature board</name>
    <verification>Query feature board for feature_id</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is "Planned"</name>
    <verification>Check feature status field equals "Planned"</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Query Feature Board, 1.2 Gather Context, 1.3 Process Mockups | Load feature data, read requirements, analyze mockups | Full context gathered |
| 2. 审问之 — Inquire Thoroughly | 2.1 Specification Review Questions | Challenge spec completeness, probe gaps and assumptions | Questions resolved |
| 3. 慎思之 — Think Carefully | 3.1 AC Quality Reflection | Assess testability, measurability, completeness of ACs | AC quality validated |
| 4. 明辨之 — Discern Clearly | 4.1 Specification Scope Decision | Finalize in/out scope, resolve edge cases | Scope decided |
| 5. 笃行之 — Practice Earnestly | 5.1 Create/Update Specification, 5.2 Complete & Verify | Write specification document, verify DoD | Specification created |

BLOCKING: Phase 1 fails if feature not on board or status not "Planned".
BLOCKING: Step 1.3 MUST scan for mockups if feature folder has no `mockups/` directory.
BLOCKING (manual/stop_for_question): Human MUST confirm specification is complete before Technical Design.
BLOCKING (auto): Proceed automatically after DoD verification.

---

## Execution Procedure

```xml
<procedure name="feature-refinement">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Query Feature Board</name>
      <action>
        1. CALL x-ipe+feature+feature-board-management skill:
           operation: query_feature, feature_id: {feature_id from task_data}
        2. RECEIVE Feature Data Model (feature_id, title, version, status, description, dependencies, timestamps)
        3. Use data to understand context, check dependencies, determine if specification exists
      </action>
      <constraints>
        - BLOCKING: Feature must exist on board with status "Planned"
      </constraints>
      <output>Feature Data Model loaded</output>
    </step_1_1>

    <step_1_2>
      <name>Gather Context</name>
      <action>
        0. Resolve extra_context_reference inputs (requirement-doc, features-list)
        1. IF requirement-details.md exists: read for context, related features, business goals
        2. IF feature has dependencies: check if specs exist, read integration points
        3. IF architecture implications: check x-ipe-docs/architecture/
        4. Web search: domain rules, compliance, UX best practices, accessibility (WCAG)
        5. IF mockup_list provided: analyze mockups, extract UI/UX requirements, identify gaps
      </action>
      <output>Full context gathered including mockup analysis</output>
    </step_1_2>

    <step_1_3>
      <name>Process Mockups</name>
      <action>
        1. CHECK x-ipe-docs/requirements/{FEATURE-ID}/mockups/
           IF exists AND contains files → skip
        2. IF mockups NOT in feature folder:
           a. Check requirement-details.md for idea folder reference
           b. IF idea folder exists → scan x-ipe-docs/ideas/{idea-folder}/mockups/
           c. IF mockups found: create folder, copy ALL mockup files, update paths
        3. IF mockup_list provided AND not yet copied: create folder, copy, update paths
        4. IF no mockups found → log and proceed
      </action>
      <constraints>
        - CRITICAL: Only copy if NOT already in feature folder
      </constraints>
      <output>Mockups in feature folder (or confirmed absent)</output>
    </step_1_3>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Specification Review Questions</name>
      <action>
        1. Review gathered context and identify gaps:
           - Are user stories comprehensive? Missing personas?
           - Are acceptance criteria testable and measurable?
           - Are edge cases documented?
           - Are dependencies clearly identified?
           - Are non-functional requirements addressed?
        2. Ask clarifying questions about identified gaps (batch 3-5 questions)

        Response source (based on auto_proceed):
        IF process_preference.auto_proceed == "auto":
          → Resolve via x-ipe-dao-end-user-representative
        ELSE (manual/stop_for_question):
          → Ask human for answers
        4. Document all answers and clarifications
      </action>
      <constraints>
        - CRITICAL: Do not skip — incomplete specs lead to incorrect implementations
      </constraints>
      <output>Clarified specification requirements with all gaps addressed</output>
    </step_2_1>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">

    <step_3_1>
      <name>AC Quality Reflection</name>
      <action>
        1. For each acceptance criterion, verify:
           - Is it specific (not vague)?
           - Is it measurable (can be tested programmatically)?
           - Is it achievable (technically feasible)?
           - Is it relevant (directly tied to a user story)?
        2. Flag any ACs that fail SMART criteria
        3. Identify missing ACs for: error states, loading states, empty states, edge cases
        4. Consider testability: can each AC be verified with an automated test?
      </action>
      <output>AC quality assessment with improvement recommendations</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>Specification Scope Decision</name>
      <action>
        1. Review all gathered context, questions, and AC assessment
        2. Decide final scope: what's IN scope vs OUT of scope
        3. Resolve any remaining edge case decisions
        4. IF mockups exist: decide freshness status (current vs outdated)
        5. Present scope decisions for confirmation

        Response source (based on auto_proceed):
        IF process_preference.auto_proceed == "auto":
          → Log via x-ipe-dao-end-user-representative
        ELSE (manual/stop_for_question):
          → Ask human to confirm scope
      </action>
      <output>Final specification scope with all decisions documented</output>
    </step_4_1>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Create/Update Feature Specification</name>
      <action>
        1. Create or update: x-ipe-docs/requirements/FEATURE-XXX/specification.md
        2. Follow specification-template.md structure
        3. Include all sections: Version History, Linked Mockups, Overview, User Stories,
           Acceptance Criteria, Functional Requirements, NFRs, UI/UX Requirements,
           Dependencies, Business Rules, Edge Cases, Out of Scope, Technical Considerations
        4. IF mockups exist and marked "current":
           a. Add mockup-comparison ACs (layout, styling, interactive elements)
        5. IF mockups marked "outdated": note as directional reference only
      </action>
      <constraints>
        - MANDATORY: Single file with version history
        - CRITICAL: Focus on WHAT not HOW in Technical Considerations
        - CRITICAL: Only add mockup-comparison ACs for current mockups
        - MANDATORY: Use full project-root-relative paths for links
      </constraints>
      <output>specification.md created/updated</output>
    </step_5_1>

    <step_5_2>
      <name>Complete & Verify</name>
      <action>
        1. IF workflow-mode: call update_workflow_action with:
           - workflow_name, action, status: "done", feature_id
           - deliverables: {"specification": "{path}", "feature-docs-folder": "{path}"}
        2. Verify all DoD checkpoints
        3. Verify all DoD checkpoints are met
        4. IF manual/stop_for_question: present specification, ask if anything is missing or incorrect
      </action>
      <output>Task completion output with specification path, workflow_action_updated</output>
    </step_5_2>

  </phase_5>

  <routing>
    <name>Routing</name>
    <actions>
      Collect the full task_completion_output from this skill execution.

      IF next_task_based_skill EXISTS (not null):
        IF process_preference.auto_proceed == "auto":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the full output to decide best next action."
          → DAO studies the complete output context and decides the best next action
          → Return to x-ipe-workflow-task-execution Step 1
        ELIF process_preference.auto_proceed == "stop_for_question":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the full output and recommend next action."
          → Present DAO's recommendation to human and wait for confirmation
          → Return to x-ipe-workflow-task-execution Step 1
        ELSE (manual):
          → Present next task suggestion to human and wait for instruction
      ELSE (next_task_based_skill is null):
        → STOP — return to x-ipe-workflow-task-execution
    </actions>
    <gate>Routing decision made — return to x-ipe-workflow-task-execution</gate>
  </routing>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "x-ipe-task-based-technical-design"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"   # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Feature Refinement"
  mockup_list: "{updated with copied paths if mockups were copied}"
  linked_mockups:  # if applicable
    - mockup_name: "Description of mockup function"
      mockup_path: "x-ipe-docs/requirements/FEATURE-XXX/mockups/mockup-name.html"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Specification file created</name>
    <verification>x-ipe-docs/requirements/FEATURE-XXX/specification.md exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All specification sections completed</name>
    <verification>Check all template sections are present and filled</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Acceptance criteria are testable</name>
    <verification>Each criterion is specific and measurable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Dependencies documented</name>
    <verification>Internal and external dependencies listed</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockups copied to feature folder</name>
    <verification>If mockups found in idea folder, copied to FEATURE-XXX/mockups/</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockup list analyzed</name>
    <verification>If mockups provided or copied, UI/UX requirements extracted</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Linked Mockups section populated</name>
    <verification>If mockups exist, Linked Mockups table in specification with freshness status (current/outdated)</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockup-comparison ACs added</name>
    <verification>If current (non-outdated) mockups exist, acceptance criteria reference mockup comparison for UI layout, styling, and interactive elements</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Workflow Action Updated</name>
    <verification>If execution_mode == "workflow-mode", called the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with status "done" and deliverables keyed dict</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

| Pattern | When | Then |
|---------|------|------|
| Mockup-Driven | Mockup list provided | Assess freshness, extract UI elements, add mockup-comparison ACs for current mockups |
| Well-Defined Feature | Clear scope from breakdown | Query board → read requirements → create specification |
| Feature with Dependencies | Depends on other features | Read dependent specs, identify integration points, document assumptions |
| Complex Domain | Unfamiliar domain rules | Web research, document compliance, include domain glossary |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip board query | Missing context | Always query feature board first |
| Vague acceptance criteria | Untestable | Make criteria specific and measurable |
| Technical implementation details | Wrong focus | Focus on WHAT, not HOW |
| Ignore dependencies | Integration failures | Document all dependencies |
| Ignore mockup when provided | Missing UI requirements | Always analyze mockup_list |
| Compare against outdated mockup | Wrong ACs | Check freshness; only add ACs for current mockups |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-feature-refinement/references/examples.md) for detailed execution examples including:
- User authentication specification
- Enhancement refinement from change request
- Missing feature entry (blocked)
- Complex feature requiring split
- Specification with thorough edge case coverage
