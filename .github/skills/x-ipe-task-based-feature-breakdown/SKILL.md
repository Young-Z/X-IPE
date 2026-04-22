---
name: x-ipe-task-based-feature-breakdown
description: Break requirements into Epics and features. Assesses scope to determine Epic grouping, then breaks each Epic into features with MVP-first criteria. Calls feature-board-management to initialize tracking. Use when requirements need to be split into discrete features. Triggers on requests like "break down features", "split into features", "create feature list", "organize epics".
---

# Task-Based Skill: Feature Breakdown

## Purpose

Break user requests into Epics and features by:
1. Analyzing requirement documentation (or current active part)
2. Assessing scope to determine Epic-level grouping
3. Identifying feature boundaries within each Epic using MVP-first criteria
4. Creating feature list in requirement-details.md (or current active part)
5. Calling feature-board-management to create features on board

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST run the workflow update script via bash: `python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py` with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the script exits with code 0 before marking the task complete.

MANDATORY: This skill MUST call feature-board-management to create features on the board. Never edit features.json manually.

MANDATORY: Every feature MUST have a feature ID in the format `FEATURE-{nnn}-{X}` (e.g., FEATURE-035-A, FEATURE-035-B) where `{nnn}` matches the parent Epic number. Features are created as sub-folders under the parent `EPIC-{nnn}/` folder.

> **Transition Note:** During migration, both old (`FEATURE-{nnn}/`) and new (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`) folder structures may coexist. Skills must handle both formats when scanning existing files.

See [references/breakdown-guidelines.md](.github/skills/x-ipe-task-based-feature-breakdown/references/breakdown-guidelines.md) for:
- Epic granularity heuristics and grouping decision matrix
- Feature dependency patterns (sequential, parallel, multiple) and rules
- Feature sizing guidelines, naming conventions, version numbering rules
- Mockup processing procedures and examples
- Feature board integration details and call format

Additional notes:
- All features are consolidated in requirement-details.md (no individual feature.md files)
- Feature board (features.json) is the status tracking system
- Feature specifications are created later during Feature Refinement
- Keep feature descriptions concise (50 words max) in the table

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-assistant-user-representative-Engineer` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-breakdown"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    action: "feature_breakdown"  # workflow action name for status updates
    extra_context_reference:  # optional, default: N/A for all refs
      requirement-doc: "path | N/A | auto-detect"

  # Task type attributes
  category: "requirement-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Refine the first unstarted feature. Each feature goes through the complete pipeline (refinement → design → implementation → testing → closing) one at a time before starting the next."
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  mockup_list: "N/A"  # List of mockups from previous task or context

  # Context (from previous task or project)
  requirement_doc: "x-ipe-docs/requirements/requirement-details.md"  # or requirement-details-part-X.md
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe-tool-task-board-manager (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="extra_context_reference.requirement-doc" source="workflow context OR auto-detect">
    <steps>
      1. IF workflow-mode AND workflow.extra_context_reference.requirement-doc is a file path → use it
      2. ELIF "auto-detect" → scan x-ipe-docs/requirements/ for requirement-details*.md
      3. ELIF "N/A" → skip
      4. ELSE (free-mode) → use existing discovery logic
    </steps>
  </field>
  <field name="mockup_list" source="previous task (Idea Mockup) output links OR human input OR N/A">
    <steps>
      1. IF previous task was "Idea Mockup" → use previous task output's mockup_list field (array of {mockup_name, mockup_link})
      2. ELIF previous task was "Requirement Gathering" → inherit from its mockup_list output
      3. ELIF human provides explicit mockup paths → use human-provided value
      4. ELSE → set to "N/A"
    </steps>
  </field>
  <field name="requirement_doc" source="auto-detect from x-ipe-docs/requirements/">
    <steps>
      1. Check if x-ipe-docs/requirements/requirement-details-part-X.md files exist
      2. IF parts exist → use current active part (highest part number)
      3. ELIF x-ipe-docs/requirements/requirement-details.md exists → use it
      4. ELSE → analyze user request directly
    </steps>
  </field>
</input_init>
```

### Mockup List Structure

```yaml
mockup_list:
  - mockup_name: "Description of what function the mockup is for"
    mockup_link: "URL or path to the mockup"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Requirement documentation exists</name>
    <verification>User request or requirement-details.md (or current active part) is available</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Analyze Requirements, 1.2 Assess Epic Scope | Read requirements, evaluate scope and Epic grouping | Requirements and Epic structure understood |
| 2. 审问之 — Inquire Thoroughly | 2.1 Scope Challenge | Challenge scope assumptions, question feature necessity | Scope validated |
| 3. 慎思之 — Think Carefully | 3.1 Evaluate Complexity, 3.2 Identify Features | Count ACs, assess dimensions, identify feature boundaries | Features identified |
| 4. 明辨之 — Discern Clearly | 4.1 MVP Prioritization Decision | Decide MVP order, validate dependency DAG | MVP and order decided |
| 5. 笃行之 — Practice Earnestly | 5.1 Process Mockups, 5.2 Create Summary, 5.3 Update Board, 5.4 Complete | Execute all deliverables | All artifacts created |
| 继续执行 | 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: If parts exist, work with the CURRENT ACTIVE PART (highest part number).
BLOCKING: Features with more than 20 ACs MUST be split into sub-features.
BLOCKING: First feature in each Epic MUST be "Minimum Runnable Feature" (MVP).
BLOCKING: MUST use feature-board-management skill (not manual file editing).
BLOCKING (manual/stop_for_question): Human MUST confirm feature list is complete before refinement.
BLOCKING (auto): Proceed after DoD verification; resolve open questions via x-ipe-assistant-user-representative-Engineer if needed.

---

## Execution Procedure

```xml
<procedure name="feature-breakdown">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_0 name="Board — Register Task">
    <step_0_1>
      <name>Create Task on Board</name>
      <action>
        Call `x-ipe-tool-task-board-manager` → `task_create.py`:
        - task_type: "Feature Breakdown"
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
      <name>Analyze Requirements</name>
      <action>
        0. Resolve extra_context_reference inputs:
           - FOR ref requirement-doc:
             IF workflow mode AND extra_context_reference.requirement-doc is a file path:
               READ the file at that path
             ELIF "auto-detect": Use existing discovery logic
             ELIF "N/A": Skip
             ELSE (free-mode): Use existing behavior
        1. Determine file: check for requirement-details-part-X.md (use highest), else requirement-details.md, else user request
        2. Read and understand requirement summary
        3. Identify: verbs (actions), nouns (entities), boundaries, user goals, domain clusters
      </action>
      <constraints>
        - BLOCKING: If parts exist, MUST use current active part (highest number)
      </constraints>
      <output>Requirements understood, capability areas and domain clusters identified</output>
    </step_1_1>

    <step_1_2>
      <name>Assess Epic Scope</name>
      <action>
        1. Evaluate scope signals: estimated feature count, domain diversity, dependency clusters
        2. Apply Epic grouping matrix (see references/breakdown-guidelines.md):
           - 1 domain, ≤7 features → Single Epic
           - 2-3 domains, 8-15 features → 2-3 Epics
           - 4+ domains OR >15 features → Multiple Epics
        3. IF single Epic: assign EPIC-{nnn}, create folder
        4. IF multiple Epics: define boundaries, name each, assign sequential IDs, create folders
        5. Document Epic assessment decision with rationale
      </action>
      <constraints>
        - BLOCKING: Epic structure must be decided BEFORE feature identification
      </constraints>
      <output>Epic structure with IDs, names, domains, dependencies</output>
    </step_1_2>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Scope Challenge</name>
      <action>
        1. For each identified domain/capability area, challenge assumptions:
           - Is this capability truly needed for the MVP?
           - Can this be deferred to a later version?
           - Does this overlap with existing features in the system?
        2. Present scope challenges and ask for confirmation
        3. Document scope decisions and rationale

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Resolve via x-ipe-assistant-user-representative-Engineer
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human for confirmation
      </action>
      <constraints>
        - CRITICAL: Challenge scope BEFORE breaking down into features
      </constraints>
      <output>Validated scope with challenge decisions documented</output>
    </step_2_1>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">

    <step_3_1>
      <name>Evaluate Complexity</name>
      <action>
        1. Count ACs per Epic (total and per logical group)
        2. Assess scope dimensions: technical layers, user-facing capabilities, new files
        3. Apply sizing heuristics (see references/breakdown-guidelines.md):
           - <10 ACs: likely single feature
           - 10-20 ACs: evaluate split if multiple capabilities
           - >20 ACs: MUST split
        4. Identify natural split boundaries within each Epic
      </action>
      <constraints>
        - BLOCKING: Features with more than 20 ACs MUST be split
      </constraints>
      <output>Per-Epic complexity assessment with split decisions</output>
    </step_3_1>

    <step_3_2>
      <name>Identify Features</name>
      <action>
        1. Assign Feature IDs: FEATURE-{nnn}-{A|B|C...} where {nnn} matches Epic number
        2. Apply feature criteria: Single Responsibility, Independent, Deliverable Value, Reasonable Size
        3. First feature = MVP (Minimum Runnable Feature)
        4. Subsequent features build upon first
      </action>
      <constraints>
        - BLOCKING: First feature per Epic MUST be MVP
        - Limit to 5-7 features per Epic maximum
      </constraints>
      <output>Feature list with IDs, titles, descriptions, dependencies per Epic</output>
    </step_3_2>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>MVP Prioritization Decision</name>
      <action>
        1. Review feature list across all Epics
        2. Validate MVP selection: does first feature provide minimum runnable value?
        3. Validate dependency DAG: no circular dependencies, clear implementation order
        4. Present prioritized list for confirmation
        5. Finalize feature order and dependency graph

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Confirm via x-ipe-assistant-user-representative-Engineer
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human for confirmation
      </action>
      <output>Confirmed feature prioritization with validated dependency DAG</output>
    </step_4_1>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Process Mockups</name>
      <action>
        1. IF mockup_list empty: scan EPIC-{nnn}/mockups/ then x-ipe-docs/ideas/{idea-folder}/mockups/
        2. IF still empty: skip
        3. Mockups stay at EPIC-{nnn}/mockups/ (shared), features reference via ../mockups/
      </action>
      <constraints>
        - CRITICAL: Only copy if NOT already in feature folder
      </constraints>
      <output>Mockups in Epic folders (or confirmed absent)</output>
    </step_5_1>

    <step_5_2>
      <name>Create Summary & Update Board</name>
      <action>
        1. Determine target file (current active part or requirement-details.md)
        2. Add Feature List table:
           | Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
        3. Add detailed sections for each feature
        4. CALL x-ipe-tool-task-board-manager skill to create all features
        5. IF parts exist: update requirement-details-index.md
        6. IF features were split: run parent dedup check (100% coverage → remove parent)
      </action>
      <constraints>
        - BLOCKING: Feature List goes into PART FILE, NOT index
        - BLOCKING: MUST use feature-board-management skill
        - MANDATORY: File links in generated markdown MUST use project-root-relative paths so the UI can intercept them and open a preview modal. **Avoid** relative paths (`../`, `./`, `../../`) and absolute filesystem paths (`/Users/...`). **Correct:** `[spec](x-ipe-docs/requirements/EPIC-001/specification.md)`, `[skill](.github/skills/x-ipe-task-based-bug-fix/SKILL.md)`. **Wrong:** `[spec](../specification.md)`, `[spec](./specification.md)`.
      </constraints>
      <output>Requirement-details updated, features on board with status "Planned"</output>
    </step_5_2>

    <step_5_3>
      <name>Complete & Verify</name>
      <action>
        1. IF workflow-mode: run `python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py` with status "done", features list
        2. Verify all DoD checkpoints
        3. IF manual/stop_for_question: present feature breakdown, ask if any features are missing or miscategorized
      </action>
      <output>Task completion output, workflow_action_updated</output>
    </step_5_3>

    <step_5_4>
      <name>Update Task on Board</name>
      <action>
        Call `x-ipe-tool-task-board-manager` → `task_update.py`:
        - task_id: from Phase 0 / Step 0
        - status: "done"
        - output_links: list of deliverables produced in this skill execution
      </action>
      <output>Task marked done on board</output>
    </step_5_4>

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
          → Present feature-by-feature pipeline hint to human:
            "✅ Feature breakdown complete — {N} features created ({list of feature IDs}).
             📋 Each feature goes through the complete pipeline one at a time:
                refinement → design → implementation → testing → closing
             Next step: Feature Refinement — let's start with {first_feature_id} ({title})
             and refine its specification. Want me to proceed?"
          → Wait for human instruction
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
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Refine the first unstarted feature. Each feature goes through the complete pipeline (refinement → design → implementation → testing → closing) one at a time before starting the next."
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false
  task_output_links:
    - "x-ipe-docs/requirements/requirement-details.md"
  mockup_list: "{inherited from input or N/A}"
  # Dynamic attributes
  requirement_id: "REQ-XXX"
  epic_ids: ["EPIC-001", "EPIC-002"]
  epic_count: 2
  feature_ids: ["FEATURE-001-A", "FEATURE-001-B", "FEATURE-002-A"]
  feature_count: 3
  requirement_details_part: null | 1 | 2
  parent_features_removed: []
  dedup_gaps: []
  linked_mockups:
    - mockup_name: "Description of mockup function"
      mockup_link: "x-ipe-docs/requirements/EPIC-XXX/mockups/mockup-name.html"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Epic structure assessed and documented</name>
    <verification>Epic grouping decision made with rationale; EPIC-{nnn}/ folders created</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Requirement-details file updated with Feature List</name>
    <verification>Feature List table exists in requirement-details.md (or current part)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All features have detailed sections</name>
    <verification>Each feature has a detail section in requirement-details (or part)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature board updated via skill</name>
    <verification>feature-board-management skill was called to create features</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All features have status Planned</name>
    <verification>Check features.json shows status "Planned" for all new features</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Index updated (if parts exist)</name>
    <verification>requirement-details-index.md updated with new feature range</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockups copied to Epic folders</name>
    <verification>Mockup files exist in x-ipe-docs/requirements/EPIC-{nnn}/mockups/</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Parent feature deduplication verified</name>
    <verification>If features were split, parent coverage checked — fully covered parents removed</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Workflow Action Status Updated</name>
    <verification>If execution_mode == "workflow-mode", ran `workflow_update_action.py` script with status "done"</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

See [references/patterns.md](.github/skills/x-ipe-task-based-feature-breakdown/references/patterns.md) for detailed patterns including:
- Clear Requirements, Vague Requirements, Large Scope patterns
- Epic Grouping pattern (single vs multi-Epic decision)
- Feature Split with Parent Dedup pattern

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skipping Epic assessment | Features lack cohesion, poor organization | Always assess Epic granularity first |
| All features in one Epic | Monolithic, hard to manage large scope | Split by domain when >7 features |
| Too many features per Epic | Overwhelming, hard to track | Limit to 5-7 features per Epic |
| Features too granular | Micromanagement | Combine related functions |
| MVP not first | Critical path unclear | First feature per Epic = MVP |
| Circular dependencies | Impossible to implement | Ensure DAG structure |
| Manual board updates | Inconsistent state | Use feature-board-management skill |
| Keeping duplicate parent | Redundant tracking | Remove parent if fully covered |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-feature-breakdown/references/examples.md) for detailed examples including:
- Multi-Epic and single-Epic breakdown scenarios
- Epic grouping decisions, change requests, and parent feature deduplication
