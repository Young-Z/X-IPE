---
name: x-ipe-task-based-change-request
description: Process change requests by analyzing impact on existing requirements and features. Determines if CR modifies existing feature (-> refinement) or requires new feature (-> requirement update + feature breakdown). Triggers on "change request", "CR", "modify feature", "update requirement".
---

# Task-Based Skill: Change Request

## Purpose

Process change requests (CRs) systematically by:
1. Analyzing the change request against existing requirements and features
2. Classifying the CR as modification to existing feature or new feature
3. Routing to appropriate workflow (Feature Refinement or Requirement Update + Feature Breakdown)
4. Maintaining traceability and documentation

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
| 4 | Human Approval | Present classification and reasoning to human | Human approves |
| 5 | Execute Path | Update spec (modification) or requirements (new feature) | Documents updated |
| 6 | Document CR | Create CR-XXX.md in feature folder, update version history | CR documented |

BLOCKING: Step 4 must complete before Step 5. Do NOT proceed without explicit human approval of classification.

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
    </action>
    <output>Related features list with relevance notes</output>
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
    <name>Human Approval</name>
    <action>
      1. Present CR summary, classification, reasoning, affected features, proposed approach
      2. Wait for explicit human approval
    </action>
    <constraints>
      - BLOCKING: Do NOT proceed without explicit human approval
    </constraints>
    <output>Human-approved classification</output>
  </step_4>

  <step_5>
    <name>Execute Based on Classification</name>
    <branch>
      IF: classification = "modification"
      THEN:
        1. CREATE x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md using template (see templates/change-request.md)
        2. UPDATE specification.md: add Version History entry with CR reference (see references/version-history-template.md)
        3. Update affected sections, user stories, acceptance criteria
        4. CHECK if requirement-details.md needs update:
           IF cr_affects_high_level_requirements:
             UPDATE requirement-details.md (High-Level Requirements, Clarifications, Constraints)
             SET requirement_updated = true
           ELSE:
             SET requirement_updated = false
        5. SET next_task_based_skill = x-ipe-task-based-feature-refinement

      ELSE (classification = "new_feature"):
        1. UPDATE x-ipe-docs/requirements/requirement-details.md
           - Add new requirement to High-Level Requirements
           - Document in Clarifications table
           - Update Project Overview if scope changed
        2. SET next_task_based_skill = x-ipe-task-based-feature-breakdown
        3. NOTE: After feature breakdown creates FEATURE-XXX folder,
           CREATE x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md to link CR to new feature
    </branch>
    <output>Updated documents, next_task_based_skill set</output>
  </step_5>

  <step_6>
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
  </step_6>

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
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md"

  # Dynamic attributes
  cr_id: "CR-XXX"
  cr_classification: modification | new_feature
  affected_features: ["FEATURE-XXX"]    # For modifications
  new_feature_ids: ["FEATURE-XXX"]      # For new features
  requirement_updated: true | false
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
    <name>Human approved classification</name>
    <verification>Explicit human approval recorded before execution</verification>
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

See [references/patterns.md](references/patterns.md) for detailed patterns: Enhancement CR, New Capability CR, Scope Expansion CR, Multi-Feature CR, Boundary Cases, CR Chain.

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip classification | Wrong workflow chosen | Always classify explicitly |
| Assume modification | May miss scope expansion | Use decision tree |
| No human approval | Risk of wrong direction | Always get approval at Step 4 |
| Skip documentation | Lost traceability | Create CR document |
| Modify multiple features at once | Hard to track | One CR = one classification |
| No version history update | Lost change history | Update specification version |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples:
- Bulk import CR classification (NEW_FEATURE)
- UI enhancement CR classification (MODIFICATION)
- Ambiguous request requiring clarification
- Bug report redirection (NOT_A_CR)
