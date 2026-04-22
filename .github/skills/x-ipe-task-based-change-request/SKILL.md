---
name: x-ipe-task-based-change-request
description: Process change requests by analyzing impact on existing requirements and features, detecting conflicts with specs/designs/code. Determines if CR modifies existing feature (-> refinement) or requires new feature (-> requirement update + feature breakdown). Triggers on "change request", "CR", "modify feature", "update requirement".
---

# Task-Based Skill: Change Request

## Purpose

Process change requests (CRs) systematically by:
1. Analyzing the change request against existing requirements and features
2. Classifying the CR as modification to existing feature or new feature
3. Detecting conflicts with existing specifications, technical designs, and dependencies
4. Routing to appropriate workflow (Feature Refinement or Requirement Update + Feature Breakdown)
5. Maintaining traceability and documentation

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-assistant-user-representative-Engineer` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-change-request"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      closing-report: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"

  # Task type attributes
  category: "standalone"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "When CR modifies an existing feature"
    - skill: "x-ipe-task-based-feature-breakdown"
      condition: "When CR requires a new feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  change_request_description: "{description of the requested change}"
  business_justification: "{why this change is needed}"

  # Optional inputs
  requestor: "{name/role}"
  priority: "medium"

  # Context (from project)
  requirement_details_path: "x-ipe-docs/requirements/requirement-details.md"
  features_path: "x-ipe-docs/planning/features/features.json"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe-tool-task-board-manager (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="change_request_description" source="from human input" />
  <field name="business_justification" source="from human input" />
  <field name="extra_context_reference" source="from workflow context or N/A" />
  <field name="requirement_details_path" source="auto-detect from x-ipe-docs/requirements/ (default: x-ipe-docs/requirements/requirement-details.md)" />
  <field name="features_path" source="default x-ipe-docs/planning/features/features.json" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Change request description provided</name>
    <verification>Input contains clear description of requested change</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Business justification available</name>
    <verification>Rationale for the change is documented</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Requirement details exist</name>
    <verification>x-ipe-docs/requirements/requirement-details.md exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature board exists</name>
    <verification>x-ipe-docs/planning/features/features.json exists</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Requestor identified</name>
    <verification>Name or role of person requesting the change is known</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Understand Change Request, 1.2 CR Context Study | Parse CR context, research similar features and standards | CR context established |
| 2. 审问之 — Inquire Thoroughly | 2.1 CR Challenge, 2.2 Analyze Impact | Challenge CR assumptions, review existing requirements and features | Impact analyzed |
| 3. 慎思之 — Think Carefully | 3.1 Detect Conflicts | Analyze spec/design/dependency conflicts with existing features | Conflicts classified |
| 4. 明辨之 — Discern Clearly | 4.1 Classify CR Type, 4.2 Route Workflow | Classify modification vs new feature, confirm classification | Classification confirmed |
| 5. 笃行之 — Practice Earnestly | 5.1 Execute & Document | Resolve conflicts, confirm large-scope changes with human, update spec + docs (both paths), create CR record | CR documented |
| 继续执行 | 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: Phase 3 must complete before Phase 4 — do NOT classify without conflict analysis.
BLOCKING: Classification MUST be confirmed before Phase 5 execution (manual/stop_for_question: human confirms; auto: DAO confirms via x-ipe-assistant-user-representative-Engineer).
BLOCKING: Specification MUST be updated for BOTH modification and new_feature classifications.
BLOCKING: Large-scope CRs require human confirmation of the proposed feature change solution BEFORE Phase 5 document changes are applied.

---

## Execution Procedure

```xml
<procedure name="change-request">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_0 name="Board — Register Task">
    <step_0_1>
      <name>Create Task on Board</name>
      <action>
        Call `x-ipe-tool-task-board-manager` → `task_create.py`:
        - task_type: "Change Request"
        - description: summarize work from input context
        - status: "in_progress"
        - role: from input context
        - assignee: from input context
        Store returned task_id for later update.
      </action>
      <output>Task created on board with status in_progress</output>
    </step_0_1>
  </phase_0>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Understand the Change Request</name>
      <action>
        1. Identify WHAT change is being requested
        2. Identify WHO requested it and WHY
        3. Identify WHEN it is needed (priority/urgency)
        4. Document the CR context
      </action>
      <output>CR understanding summary</output>
    </step_1_1>

    <step_1_2>
      <name>CR Context Study</name>
      <action>
        1. Use web search to research similar features, industry standards, best practices
        2. Research how similar systems handle this type of change
        3. Identify potential compliance or regulatory implications
        4. Document relevant context for informed decision-making
      </action>
      <constraints>
        - CRITICAL: Research before challenging — informed challenges are more productive
      </constraints>
      <output>CR context research summary</output>
    </step_1_2>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>CR Challenge</name>
      <action>
        1. Challenge CR assumptions:
           - Is this change truly necessary? What problem does it solve?
           - Could the existing feature already handle this with configuration?
           - Is the requested approach the best solution, or are there alternatives?
           - What is the impact if this CR is NOT implemented?
        2. Present challenges and ask for confirmation
        3. Document challenge outcomes and confirmed scope

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Resolve via x-ipe-assistant-user-representative-Engineer
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human for confirmation
      </action>
      <output>Validated CR scope with challenge decisions</output>
    </step_2_1>

    <step_2_2>
      <name>Analyze Impact</name>
      <action>
        0. Resolve extra_context_reference inputs (closing-report, specification)
        1. READ requirement-details.md: understand project scope, identify related requirements
        2. READ features.json (via x-ipe-tool-task-board-manager): list all features, note statuses, identify related features
        3. FOR EACH related feature: read specification if exists (ACs, user stories, out-of-scope)
        4. IF CR involves UI/UX changes:
           a. Check FEATURE-XXX/mockups/ for existing mockups
           b. Check specification Linked Mockups section for status
      </action>
      <output>Related features list with relevance notes, existing mockups identified</output>
    </step_2_2>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">

    <step_3_1>
      <name>Detect Conflicts</name>
      <action>
        1. Spawn sub-agent (Conflict Detector) to analyze CR against existing artifacts:
           - Read specs and technical designs of related features
           - Read implemented code for affected features
           - Identify spec conflicts, design conflicts, dependency conflicts, pending CR conflicts
        2. IF no conflicts: proceed to Phase 4
        3. IF conflicts: classify each as "expected" or "unexpected"
        4. IF any "unexpected": document with explanation, suggest mitigations
      </action>
      <constraints>
        - BLOCKING: Do NOT proceed to Phase 4 with unanalyzed conflicts
        - CRITICAL: Conflict Detector must examine actual artifacts, not just CR description
      </constraints>
      <output>Conflict analysis report with classified conflicts and mitigations</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>Classify CR Type</name>
      <action>
        1. Create comparison matrix (Users, Workflow, Data Model, UI, API)
        2. Apply decision tree (see Classification Criteria below):
           - No related feature → new_feature
           - Related feature + fundamental scope change → new_feature
           - Related feature + works within boundaries → modification
        3. Incorporate conflict analysis results into classification reasoning
        4. Document classification with reasoning
      </action>
      <output>classification (modification|new_feature), reasoning, affected features</output>
    </step_4_1>

    <step_4_2>
      <name>Route Workflow</name>
      <action>
        1. Present CR summary: classification, conflict results, affected features
        2. Wait for confirmation of classification and conflict decisions
        3. IF changes requested: return to step 4.1 or Phase 3

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Confirm via x-ipe-assistant-user-representative-Engineer
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human to confirm
      </action>
      <constraints>
        - BLOCKING (manual/stop_for_question): Do NOT proceed without human confirming classification
        - BLOCKING (auto): Do NOT proceed without DAO confirming classification via x-ipe-assistant-user-representative-Engineer
      </constraints>
      <output>Confirmed classification and conflict decisions</output>
    </step_4_2>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Execute & Document</name>
      <action>
        0. Resolve conflicting documents (from Phase 3 conflict analysis):
           - Applies regardless of resolution method (human confirmation or interaction_mode)
           - FOR EACH conflict with an existing document (spec, design, requirement):
             a. IF minor conflict (wording update, small AC adjustment, additive change):
                → Directly update the target document inline with CR changes
             b. IF major conflict (structural redesign, contradicting requirements, scope change):
                → Mark affected sections in target document with "[RETIRED by CR-XXX]" header
                → Add retirement note: reason, date, and reference to CR-XXX.md
                → Write replacement content in the appropriate location (new section or updated section)
        0b. Large-scope confirmation gate:
           - IF CR impacts a large scope of change (multiple features, structural redesign,
             significant AC rewrites, or new workflows):
             → Present the proposed feature change solution (spec changes, affected ACs,
               conflict resolutions) to human for confirmation BEFORE executing changes
             → Wait for human approval or revision
             Response source (based on interaction_mode):
             IF process_preference.interaction_mode == "dao-represent-human-to-interact":
               → Confirm via x-ipe-assistant-user-representative-Engineer
             ELSE:
               → Ask human directly
           - IF CR is small-scope (single feature, minor AC additions/edits):
             → Proceed without additional confirmation (Phase 4.2 already confirmed classification)
        1. IF classification = "modification":
           a. CREATE CR-XXX.md using templates/change-request.md
           b. UPDATE specification.md: Version History + affected sections/ACs
           c. IF CR affects high-level requirements: update requirement-details.md
           d. IF UI/UX CR with existing mockups: create new mockup version (never override)
           e. SET next_task_based_skill = x-ipe-task-based-feature-refinement
        2. ELSE (classification = "new_feature"):
           a. UPDATE requirement-details.md: add new requirement
           b. UPDATE specification.md: Version History + new sections/ACs for the CR changes
           c. SET next_task_based_skill = x-ipe-task-based-feature-breakdown
           d. NOTE: CR-XXX.md created after feature breakdown creates folder
        3. Create CR record at FEATURE-XXX/CR-XXX.md
        4. IF execution_mode == "workflow-mode": Run `python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py` (action: "change_request", status: "done", deliverables: {cr-doc: CR path})
        5. Verify all DoD checkpoints are met
        6. IF manual/stop_for_question: present CR summary to human
      </action>
      <constraints>
        - CRITICAL: Never override existing mockup files — create new versions
        - CRITICAL: CR files go in feature folders (co-location)
        - CRITICAL: Conflicting documents MUST be handled — minor conflicts updated inline, major conflicts marked retired
        - CRITICAL: Specification MUST be updated for BOTH classification paths (modification AND new_feature)
        - BLOCKING: Large-scope CRs MUST get human confirmation (step 0b) before applying document changes
      </constraints>
      <output>CR documented, conflicting docs resolved, next_task_based_skill set</output>
    </step_5_1>

    <step_5_2>
      <name>Update Task on Board</name>
      <action>
        Call `x-ipe-tool-task-board-manager` → `task_update.py`:
        - task_id: from Phase 0
        - status: "done"
        - output_links: list of deliverables produced in this skill execution
      </action>
      <output>Task marked done on board</output>
    </step_5_2>

  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-assistant-user-representative-Engineer with:
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

### Classification Criteria

**Decision Tree:** No related feature → `new_feature` | Related feature + fundamental scope change → `new_feature` | Related feature + within boundaries → `modification`

| Classification | Indicators |
|---|---|
| `new_feature` (scope change) | New workflows, data models, user types/roles, integration points, purpose change |
| `modification` | Within boundaries, extends user stories, no new endpoints/screens, same users |
| `new_feature` (boundary) | Expands boundaries, new user stories, new UI/API/data models, separate docs |

**Update requirement-details.md (modification path) when:** CR adds high-level capability, changes constraints, affects multiple features, changes user types, or modifies project-level business rules.

---

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "When CR modifies an existing feature"
    - skill: "x-ipe-task-based-feature-breakdown"
      condition: "When CR requires a new feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md"

  # Dynamic attributes
  feature_id: "{FEATURE-XXX}"            # Primary affected feature (modification path)
  cr_id: "CR-XXX"
  cr_classification: modification | new_feature
  affected_features: ["FEATURE-XXX"]    # For modifications
  new_feature_ids: ["FEATURE-XXX"]      # For new features
  requirement_updated: true | false
  mockup_updated: true | false          # Whether a new mockup version was created
  updated_mockup_paths: []              # Paths to new mockup versions (if applicable)
  conflicts_found: []                   # List of conflicts identified (empty if none)
  conflicts_resolution: "none | all_expected | mitigated"  # How conflicts were resolved
  conflicting_docs_updated: []          # Docs updated inline for minor conflicts
  conflicting_docs_retired: []          # Doc sections marked retired for major conflicts
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>CR documented</name>
    <verification>x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md exists with complete details</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Classification determined</name>
    <verification>CR classified as modification or new_feature with documented reasoning</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Conflict analysis completed</name>
    <verification>Conflicts checked against specs, designs, and dependencies; all unexpected conflicts resolved (manual/stop_for_question: with human; auto: via DAO)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Classification and conflicts confirmed</name>
    <verification>Classification confirmed before execution (manual/stop_for_question: human confirmed; auto: DAO confirmed), including conflict decisions</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Version history updated</name>
    <verification>Specification Version History has CR entry (both modification and new_feature paths)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Conflicting documents resolved</name>
    <verification>All conflicting documents from Phase 3 handled: minor conflicts updated inline, major conflicts have sections marked "[RETIRED by CR-XXX]" with replacement content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Documents updated</name>
    <verification>Specification updated (both paths). Additionally: requirement-details.md updated if new_feature or high-level requirement change</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Next task type set</name>
    <verification>next_task_based_skill = x-ipe-task-based-feature-refinement or x-ipe-task-based-feature-breakdown</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockups updated for UI/UX CR</name>
    <verification>If CR involves UI/UX changes and existing mockups found: new mockup version created (not overriding original), specification Linked Mockups updated, CR document references mockup impact</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

| Pattern | When | Then |
|---------|------|------|
| Classification Decision | Classification unclear | Score against criteria, if score diff ≤2 ask human (manual/stop_for_question) or DAO (auto) |
| Conflict Resolution | Unexpected conflicts found | Present with impact, suggest mitigations, split CR if severe |
| Enhancement CR | See [references/patterns.md] | Match existing feature, classify modification |
| Multi-Feature CR | CR touches many features | One CR = one classification; split if needed |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip classification | Wrong workflow chosen | Always classify explicitly |
| Classify before conflicts | May miss scope issues | Phase 3 (conflicts) before Phase 4 (classify) |
| No classification confirmation | Risk wrong direction | Always confirm classification at Phase 4.2 (human in manual/stop_for_question; DAO in auto) |
| Skip conflict analysis | Break existing features | Always detect conflicts in Phase 3 |
| Override existing mockup | Lost design history | Create new version (v{N+1}), keep original |
| Leave conflicting docs unresolved | Stale docs mislead future work | Minor → update inline; major → mark retired |
| No version history | Lost change history | Update specification version |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples:
- Bulk import CR classification (NEW_FEATURE)
- UI enhancement CR classification (MODIFICATION)
- CR with dependency conflict (MODIFICATION with conflict analysis)
- Ambiguous request requiring clarification
- Bug report redirection (NOT_A_CR)
