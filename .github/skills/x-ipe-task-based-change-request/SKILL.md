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

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "change-request"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      eval-report: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: "x-ipe-task-based-feature-refinement | x-ipe-task-based-feature-breakdown"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"

  # Required inputs
  change_request_description: "{description of the requested change}"
  business_justification: "{why this change is needed}"

  # Optional inputs
  requestor: "{name/role}"
  priority: "medium"

  # Context (from project)
  requirement_details_path: "x-ipe-docs/requirements/requirement-details.md"
  features_path: "x-ipe-docs/planning/features.md"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="change_request_description" source="from human input" />
  <field name="business_justification" source="from human input" />
  <field name="extra_context_reference" source="from workflow context or N/A" />
  <field name="requirement_details_path" source="auto-detect from x-ipe-docs/requirements/ (default: x-ipe-docs/requirements/requirement-details.md)" />
  <field name="features_path" source="default x-ipe-docs/planning/features.md" />
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
    <verification>x-ipe-docs/planning/features.md exists</verification>
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
| 4. 明辨之 — Discern Clearly | 4.1 Classify CR Type, 4.2 Route Workflow | Classify modification vs new feature, get human approval | Classification approved |
| 5. 笃行之 — Practice Earnestly | 5.1 Execute & Document | Update documents, create CR record | CR documented |

BLOCKING: Phase 3 must complete before Phase 4 — do NOT classify without conflict analysis.
BLOCKING: Classification MUST be approved before Phase 5 execution (manual/stop_for_question: human approval; auto: DAO approval via x-ipe-dao-end-user-representative).

---

## Execution Procedure

```xml
<procedure name="change-request">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

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
        2. IF auto_proceed: use x-ipe-dao-end-user-representative to resolve challenges
        3. ELSE (manual/stop_for_question): present challenges to human, ask for confirmation
        4. Document challenge outcomes and confirmed scope
      </action>
      <output>Validated CR scope with challenge decisions</output>
    </step_2_1>

    <step_2_2>
      <name>Analyze Impact</name>
      <action>
        0. Resolve extra_context_reference inputs (eval-report, specification)
        1. READ requirement-details.md: understand project scope, identify related requirements
        2. READ features.md: list all features, note statuses, identify related features
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
        1. IF auto_proceed: log classification and conflicts via x-ipe-dao-end-user-representative, proceed
        2. ELSE (manual/stop_for_question):
           a. Present to human: CR summary, classification, conflict results, affected features
           b. Wait for explicit human approval
           c. IF human requests changes: return to step 4.1 or Phase 3
      </action>
      <constraints>
        - BLOCKING (manual/stop_for_question): Do NOT proceed without human approval
        - BLOCKING (auto): Do NOT proceed without DAO approval-like guidance from x-ipe-dao-end-user-representative
      </constraints>
      <output>Approved classification and conflict resolution</output>
    </step_4_2>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Execute & Document</name>
      <action>
        0. Resolve conflicting documents (from Phase 3 conflict analysis):
           - Applies regardless of resolution method (human approval or auto_proceed)
           - FOR EACH conflict with an existing document (spec, design, requirement):
             a. IF minor conflict (wording update, small AC adjustment, additive change):
                → Directly update the target document inline with CR changes
             b. IF major conflict (structural redesign, contradicting requirements, scope change):
                → Mark affected sections in target document with "[RETIRED by CR-XXX]" header
                → Add retirement note: reason, date, and reference to CR-XXX.md
                → Write replacement content in the appropriate location (new section or updated section)
        1. IF classification = "modification":
           a. CREATE CR-XXX.md using templates/change-request.md
           b. UPDATE specification.md: Version History + affected sections/ACs
           c. IF CR affects high-level requirements: update requirement-details.md
           d. IF UI/UX CR with existing mockups: create new mockup version (never override)
           e. SET next_task_based_skill = x-ipe-task-based-feature-refinement
        2. ELSE (classification = "new_feature"):
           a. UPDATE requirement-details.md: add new requirement
           b. SET next_task_based_skill = x-ipe-task-based-feature-breakdown
           c. NOTE: CR-XXX.md created after feature breakdown creates folder
        3. Create CR record at FEATURE-XXX/CR-XXX.md
        4. Verify all DoD checkpoints
        5. IF auto_proceed: skip human review
        6. ELSE (manual/stop_for_question): present output, wait for approval
      </action>
      <constraints>
        - CRITICAL: Never override existing mockup files — create new versions
        - CRITICAL: CR files go in feature folders (co-location)
        - CRITICAL: Conflicting documents MUST be handled — minor conflicts updated inline, major conflicts marked retired
      </constraints>
      <output>CR documented, conflicting docs resolved, next_task_based_skill set</output>
    </step_5_1>

  </phase_5>

</procedure>
```

### Classification Criteria

**Decision Tree:**

```yaml
classification_logic:
  step_1_check_existing:
    action: Search features.md for related functionality
    IF no_related_feature_exists:
      THEN: classification = "new_feature"
    IF related_feature_exists:
      THEN: proceed to step_2

  step_2_evaluate_scope:
    IF cr_changes_fundamental_scope:
      THEN: classification = "new_feature"
    ELSE:
      THEN: classification = "modification"
```

**Scope change indicators** (any of these means fundamental scope change):
- Introduces entirely new workflows
- Requires new data models
- Adds new user types or roles
- Creates new integration points
- Significantly changes the feature's purpose

**Modification indicators:**
- Works within current system boundaries
- Builds upon existing user stories
- No new API endpoints/screens required
- Same users, extended functionality

**New feature indicators:**
- Expands system boundaries
- Requires new user stories
- Needs new UI screens, API endpoints, or data models
- May require separate documentation/onboarding

**When to update requirement-details.md (modification path):**
- CR adds new high-level capability to existing feature
- CR changes project constraints
- CR affects multiple features
- CR changes user types or stakeholders
- CR modifies business rules at project level

---

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill: x-ipe-task-based-feature-refinement | x-ipe-task-based-feature-breakdown
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md"

  # Dynamic attributes
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
    <name>Human approved classification and conflicts</name>
    <verification>Approval recorded before execution (manual/stop_for_question: explicit human approval; auto: DAO approval-like guidance), including conflict resolution</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Version history updated</name>
    <verification>Specification Version History has CR entry (modification path only)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Conflicting documents resolved</name>
    <verification>All conflicting documents from Phase 3 handled: minor conflicts updated inline, major conflicts have sections marked "[RETIRED by CR-XXX]" with replacement content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Documents updated</name>
    <verification>Specification (modification) or requirement-details.md (new feature) updated</verification>
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
| No human approval | Risk wrong direction | Always get approval at Phase 4.2 (human in manual/stop_for_question; DAO in auto) |
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
