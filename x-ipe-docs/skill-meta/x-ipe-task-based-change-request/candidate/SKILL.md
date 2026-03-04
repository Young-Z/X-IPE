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
  require_human_review: "yes"

  # Required inputs
  auto_proceed: false
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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Understand CR | Parse what, who, why, when of the change request | CR context documented |
| 2 | Review Existing | Read requirement-details.md and features.md | Related features identified |
| 3 | Classify CR | Apply classification criteria (modification vs new feature) | Classification determined |
| 4 | Conflict Analysis | Detect spec/design/dependency conflicts with existing features | Conflicts resolved or documented |
| 5 | Human Approval | Present classification, conflicts, and reasoning to human | Human approves |
| 6 | Execute Path | Update spec (modification) or requirements (new feature) | Documents updated |
| 7 | Document CR | Create CR-XXX.md in feature folder, update version history | CR documented |

BLOCKING: Step 4 must complete before Step 5 — do NOT present to human with unanalyzed conflicts.
BLOCKING: Step 5 must complete before Step 6. Do NOT proceed without explicit human approval of classification.

---

## Execution Procedure

```xml
<procedure name="change-request">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Understand the Change Request</name>
    <action>
      1. Identify WHAT change is being requested
      2. Identify WHO requested it and WHY
      3. Identify WHEN it is needed (priority/urgency)
      4. Document the CR context
      5. (Recommended) Use web search to research similar features, industry standards, best practices
    </action>
    <output>CR understanding summary</output>
  </step_1>

  <step_2>
    <name>Review Existing Requirements and Features</name>
    <action>
      0. Resolve extra_context_reference inputs:
         - FOR EACH ref in [eval-report, specification]:
           IF workflow mode AND extra_context_reference.{ref} is a file path:
             READ the file at that path
           ELIF extra_context_reference.{ref} is "auto-detect":
             Use existing discovery logic below
           ELIF extra_context_reference.{ref} is "N/A":
             Skip this context input
           ELSE (free-mode / absent):
             Use existing behavior
      1. READ x-ipe-docs/requirements/requirement-details.md
         - Understand overall project scope
         - Identify related high-level requirements
      2. READ x-ipe-docs/planning/features.md
         - List all existing features
         - Note feature statuses and dependencies
         - Identify potentially related features
      3. FOR EACH potentially related feature:
         IF x-ipe-docs/requirements/FEATURE-XXX/specification.md exists:
           READ specification (functionality, user stories, acceptance criteria, out-of-scope)
      4. IF CR involves UI/UX changes:
         a. CHECK x-ipe-docs/requirements/FEATURE-XXX/mockups/ for existing mockup files
         b. IF mockups exist: note them for reference in Step 6
         c. CHECK specification.md Linked Mockups section for mockup status (current/outdated)
    </action>
    <output>Related features list with relevance notes, existing mockups identified (if UI/UX CR)</output>
  </step_2>

  <step_3>
    <name>Classify the Change Request</name>
    <action>
      1. Create comparison matrix:
         | Aspect         | CR Requirement | Existing Feature(s) |
         |----------------|----------------|---------------------|
         | Users          | [who]          | [who]               |
         | Workflow       | [what flow]    | [what flow]         |
         | Data Model     | [data]         | [data]              |
         | UI Elements    | [screens]      | [screens]           |
         | API Endpoints  | [APIs]         | [APIs]              |
      2. Apply decision tree (see Classification Criteria below)
      3. Document classification decision with reasoning
    </action>
    <output>
      classification: modification | new_feature
      reasoning: explanation referencing specific criteria
      affected_features: [FEATURE-XXX, ...]  (if modification)
      proposed_new_feature: title             (if new feature)
    </output>
  </step_3>

  <step_4>
    <name>Conflict Analysis</name>
    <action>
      1. Spawn sub-agent (Conflict Detector) to analyze proposed CR changes against existing artifacts:
         - Read specifications and technical designs of related features (from Step 2)
         - Read implemented code for affected features (if code exists)
         - Identify specification conflicts: acceptance criteria, user stories, or out-of-scope items the CR would violate
         - Identify design conflicts: technical designs or architecture decisions the CR would break
         - Identify dependency conflicts: features that depend on the affected feature(s) and would be impacted
         - Identify pending CR conflicts: other open CRs that modify the same feature(s)
         - Output: list of conflicts with description, severity, and affected artifacts (empty if none)
      2. IF no conflicts found: proceed to Step 5
      3. IF conflicts found: classify each conflict as:
         - "expected": the CR's stated goal explicitly or implicitly requires this change
         - "unexpected": the change goes beyond the CR's scope or creates unintended side effects
         - Output: classified conflict list with mitigation suggestions for unexpected conflicts
      4. IF all conflicts are "expected": proceed to Step 5 (include in human approval)
      5. IF any conflicts are "unexpected":
         - Document unexpected conflicts with clear explanation of what would change
         - Suggest mitigations: scope adjustment, additional CRs for affected features, or design alternatives
         - Include all conflicts (expected + unexpected) in Step 5 presentation
    </action>
    <constraints>
      - BLOCKING: Do NOT proceed to Step 5 with unanalyzed conflicts
      - CRITICAL: Conflict Detector must examine actual project artifacts (specs, designs, code), not just the CR description
      - CRITICAL: For modification CRs, check ALL features that depend on the affected feature
    </constraints>
    <output>Conflict analysis report with classified conflicts and mitigations</output>
  </step_4>

  <step_5>
    <name>Human Approval</name>
    <action>
      1. Present to human:
         - CR summary and classification reasoning
         - Conflict analysis results (if any conflicts found)
         - For unexpected conflicts: explain what would change and proposed mitigations
         - Affected features and proposed approach
      2. Wait for explicit human approval
      3. IF human requests changes based on conflicts: return to Step 3 or Step 4 as appropriate
    </action>
    <constraints>
      - BLOCKING: Do NOT proceed without explicit human approval
    </constraints>
    <output>Human-approved classification and conflict resolution</output>
  </step_5>

  <step_6>
    <name>Execute Based on Classification</name>
    <action>
      1. IF classification = "modification":
         a. CREATE x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md using template (see templates/change-request.md)
         b. UPDATE specification.md: add Version History entry with CR reference (see references/version-history-template.md)
         c. Update affected sections, user stories, acceptance criteria
         d. CHECK if requirement-details.md needs update:
            IF cr_affects_high_level_requirements:
              UPDATE requirement-details.md (High-Level Requirements, Clarifications, Constraints)
              SET requirement_updated = true
            ELSE:
              SET requirement_updated = false
         e. IF CR involves UI/UX changes AND existing mockups found in Step 2:
            - Reference existing mockup(s) in CR document (Mockup Impact section)
            - IF CR changes are significant enough to warrant a new mockup:
              i. Load tools.json to check if x-ipe-tool-frontend-design is enabled
              ii. IF enabled: invoke design tool to create updated mockup
                  - Use existing mockup as reference baseline
                  - Apply CR changes to create new version
                  - Save as {mockup-name}-v{N+1}.{ext} (DO NOT override the original)
              iii. IF not enabled: describe mockup changes in CR document
            - Update specification.md Linked Mockups section:
              - Keep original mockup row (mark as "superseded by v{N+1}" if new version created)
              - Add new mockup row with status "current"
            - Update mockup-comparison ACs to reference the new mockup version
         f. SET next_task_based_skill = x-ipe-task-based-feature-refinement
      2. ELSE (classification = "new_feature"):
         a. UPDATE x-ipe-docs/requirements/requirement-details.md:
            Add new requirement to High-Level Requirements, document in Clarifications table, update Project Overview if scope changed
         b. SET next_task_based_skill = x-ipe-task-based-feature-breakdown
         c. NOTE: After feature breakdown creates FEATURE-XXX folder,
            CREATE x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md to link CR to new feature
    </action>
    <constraints>
      - CRITICAL: Never override or delete existing mockup files -- always create new versions
    </constraints>
    <output>Updated documents, next_task_based_skill set, updated mockups (if applicable)</output>
  </step_6>

  <step_7>
    <name>Document CR</name>
    <action>
      1. Create CR record at x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md
         Use template: templates/change-request.md
      2. CR files are stored INSIDE the affected feature folder (co-location for traceability)
      3. The specification Version History links to the CR document
    </action>
    <constraints>
      - CRITICAL: CR files go in feature folders, NOT a separate change-requests folder
      - For new features, CR is created after feature breakdown creates the folder
    </constraints>
    <output>CR-XXX.md created and linked</output>
  </step_7>

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
  require_human_review: yes
  auto_proceed: "{from input}"
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
    <verification>Conflicts checked against specs, designs, and dependencies; all unexpected conflicts resolved with human</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human approved classification and conflicts</name>
    <verification>Explicit human approval recorded before execution, including conflict resolution</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Version history updated</name>
    <verification>Specification Version History has CR entry (modification path only)</verification>
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

### Pattern: Classification Decision

**When:** CR classification is unclear
**Then:**
```
1. List facts about the CR
2. Score against classification criteria (see references/patterns.md for scoring table)
3. If score difference <= 2: ask human for decision
4. Document the decision rationale
```

### Pattern: Conflict Resolution

**When:** Unexpected conflicts found during conflict analysis
**Then:**
```
1. Present each unexpected conflict with clear impact description
2. Suggest mitigations: scope adjustment, additional CRs, design alternatives
3. If conflicts are severe: recommend splitting CR into smaller scoped changes
4. If user confirms changes are acceptable: classify as "expected" and proceed
5. If user wants to adjust: return to classification with updated scope
```

See [references/patterns.md](references/patterns.md) for detailed patterns: Enhancement CR, New Capability CR, Scope Expansion CR, Multi-Feature CR, Boundary Cases, CR Chain.

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip classification | Wrong workflow chosen | Always classify explicitly |
| Assume modification | May miss scope expansion | Use decision tree |
| No human approval | Risk of wrong direction | Always get approval at Step 5 |
| Skip conflict analysis | May break existing features silently | Always analyze conflicts before human approval |
| Skip documentation | Lost traceability | Create CR document |
| Modify multiple features at once | Hard to track | One CR = one classification |
| No version history update | Lost change history | Update specification version |
| Override existing mockup | Lost design history | Create new version (v{N+1}), keep original |
| Ignore mockups on UI/UX CR | Stale mockups misguide dev | Reference and update mockups for UI/UX CRs |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples:
- Bulk import CR classification (NEW_FEATURE)
- UI enhancement CR classification (MODIFICATION)
- CR with dependency conflict (MODIFICATION with conflict analysis)
- Ambiguous request requiring clarification
- Bug report redirection (NOT_A_CR)
