---
name: x-ipe-task-based-feature-breakdown
description: Break requirements into high-level features and create feature list in requirement-details.md (or current active part). Calls feature-board-management to initialize feature tracking. Use when requirements are gathered and need to be split into discrete features. Triggers on requests like "break down features", "split into features", "create feature list".
---

# Task-Based Skill: Feature Breakdown

## Purpose

Break user requests into high-level features by:
1. Analyzing requirement documentation (or current active part)
2. Identifying feature boundaries using MVP-first criteria
3. Creating feature list in requirement-details.md (or current active part)
4. Calling feature-board-management to create features on board

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

MANDATORY: This skill MUST call feature-board-management to create features on the board. Never edit features.md manually.

MANDATORY: Every feature MUST have a feature ID in the format `FEATURE-{nnn}-{X}` (e.g., FEATURE-035-A, FEATURE-035-B) where `{nnn}` matches the parent Epic number. Features are created as sub-folders under the parent `EPIC-{nnn}/` folder.

> **Transition Note:** During migration, both old (`FEATURE-{nnn}/`) and new (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`) folder structures may coexist. Skills must handle both formats when scanning existing files.

See [references/breakdown-guidelines.md](references/breakdown-guidelines.md) for:
- Feature dependency patterns (sequential, parallel, multiple) and rules (no cycles, foundation first)
- Feature sizing guidelines, naming conventions, version numbering rules
- Mockup processing procedures and examples
- Feature board integration details and call format
- Full file structure templates (single file and part files)

Additional notes:
- All features are consolidated in requirement-details.md (no individual feature.md files)
- Feature board (features.md) is the status tracking system
- Feature specifications are created later during Feature Refinement
- Keep feature descriptions concise (50 words max) in the table; more details go in the feature details section

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Feature Breakdown"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    action: "feature_breakdown"  # workflow action name for status updates
    extra_context_reference:  # optional, default: N/A for all refs
      requirement-doc: "path | N/A | auto-detect"

  # Task type attributes
  category: "requirement-stage"
  next_task_based_skill: "Feature Refinement"
  require_human_review: yes

  # Required inputs
  auto_proceed: false
  mockup_list: "N/A"  # List of mockups from previous task or context

  # Context (from previous task or project)
  requirement_doc: "x-ipe-docs/requirements/requirement-details.md"  # or requirement-details-part-X.md
```

### Mockup List Structure

```yaml
mockup_list:
  - mockup_name: "Description of what function the mockup is for"
    mockup_path: "URL or path to the mockup"
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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Analyze | Read requirement-details.md (or current active part) or user request | Requirements understood |
| 2 | Evaluate Complexity | Count ACs, assess scope dimensions, apply sizing heuristics, identify split boundaries | Split decision made |
| 3 | Identify Features | Extract features using MVP-first criteria (informed by complexity evaluation) | Features identified |
| 4 | Process Mockups | Auto-detect mockups from idea folder, copy to feature folders | Mockups processed |
| 5 | Create Summary | Create/update requirement-details file with feature list | Summary written |
| 6 | Update Board | Call feature-board-management to create features | Board updated |
| 7 | Update Index | If parts exist, update requirement-details-index.md | Index updated |
| 8 | Dedup Check | Verify parent features fully covered by sub-features, remove duplicates | Dedup verified |
| 9 | Complete | Verify DoD, output summary, request human review | Human review |

BLOCKING: If parts exist, work with the CURRENT ACTIVE PART (highest part number).
BLOCKING: Features with more than 20 ACs MUST be split into sub-features.
BLOCKING: First feature MUST be "Minimum Runnable Feature" (MVP).
BLOCKING: MUST scan idea folder for mockups before skipping (auto-detection required).
BLOCKING: Feature List goes into the PART FILE, not the index.
BLOCKING: MUST use feature-board-management skill (not manual file editing).
BLOCKING: Human MUST approve feature list before refinement proceeds.

---

## Execution Procedure

```xml
<procedure name="feature-breakdown">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Analyze Requirements</name>
    <action>
      0. Resolve extra_context_reference inputs:
         - FOR ref requirement-doc:
           IF workflow mode AND extra_context_reference.requirement-doc is a file path:
             READ the file at that path (skip auto-detection in sub-step 1)
           ELIF extra_context_reference.requirement-doc is "auto-detect":
             Use existing discovery logic below
           ELIF extra_context_reference.requirement-doc is "N/A":
             Skip this context input
           ELSE (free-mode / absent):
             Use existing behavior
      1. Determine which file to read:
         a. Check if x-ipe-docs/requirements/requirement-details-part-X.md files exist
         b. IF parts exist -- read the CURRENT ACTIVE PART (highest part number)
         c. ELSE IF x-ipe-docs/requirements/requirement-details.md exists -- read it
         d. ELSE -- analyze user request directly
      2. Read the determined file:
         - Understand existing requirement summary
         - Identify features from requirements
      3. Look for: verbs (actions), nouns (entities), boundaries (function edges), user goals
    </action>
    <constraints>
      - BLOCKING: If parts exist, MUST use current active part (highest number)
    </constraints>
    <output>Requirements understood, feature candidates identified</output>
  </step_1>

  <step_2>
    <name>Evaluate Complexity</name>
    <action>
      Before identifying features, evaluate the proposed feature's complexity to determine
      whether splitting is needed and where natural boundaries exist.

      1. Count acceptance criteria (ACs):
         - Total AC count across all groups
         - AC count per logical group (if grouped)
      2. Assess scope dimensions:
         - How many distinct technical layers? (service, API, CLI, UI, config)
         - How many distinct user-facing capabilities?
         - How many new files/modules estimated?
      3. Apply sizing heuristics (see references/breakdown-guidelines.md):
         - Under 10 ACs: likely single feature (no split needed)
         - 10-20 ACs: evaluate — split if multiple distinct capabilities
         - Over 20 ACs: MUST split into sub-features
      4. Identify natural split boundaries:
         - AC groups that map to independent deliverables
         - Technical layers that can be developed/tested in isolation
         - Dependency chains (foundation vs consumers)
      5. Determine split strategy:
         - IF no split needed: proceed with single feature to Step 3
         - IF split needed: identify sub-feature candidates with clear boundaries
    </action>
    <constraints>
      - BLOCKING: Features with more than 20 ACs MUST be split
      - CRITICAL: Split boundaries must align with testable, deliverable units
      - CRITICAL: Each sub-feature must be independently valuable when completed
    </constraints>
    <output>Complexity assessment with split decision and boundary candidates</output>
  </step_2>

  <step_3>
    <name>Identify Features</name>
    <action>
      Apply feature identification criteria:
      1. Assign Feature IDs as FEATURE-{nnn}-{A|B|C...} where {nnn} matches parent Epic number.
         First feature gets suffix A, second gets B, etc.
      2. Prioritize MVP: first feature MUST be the "Minimum Runnable Feature"
         - Small but sufficient to demonstrate the core value loop
      2. Iterative Expansion: subsequent features build upon the first
      3. Single Responsibility: each feature does one thing well
      4. Independent: can be developed/tested in isolation (mostly)
      5. Deliverable Value: provides value when completed
      6. Reasonable Size: fits within a development sprint
    </action>
    <constraints>
      - BLOCKING: First feature MUST be MVP (runnable core loop)
      - CRITICAL: Minimize cross-feature dependencies
      - Limit to 5-7 features maximum
    </constraints>
    <output>Feature list with IDs, titles, descriptions, dependencies</output>
  </step_3>

  <step_4>
    <name>Process Mockups</name>
    <action>
      MANDATORY: Auto-detect mockups if not provided.

      1. IF mockup_list empty -- scan EPIC-{nnn}/mockups/ (shared Epic-level mockups)
      2. IF still empty -- scan x-ipe-docs/ideas/{idea-folder}/mockups/
      3. IF still empty -- skip to Step 5
      4. Mockups remain at EPIC-{nnn}/mockups/ (shared) — do NOT create per-feature mockup folders
      5. Features reference mockups via ../mockups/ relative path
      6. Link in requirement-details.md

      See: references/breakdown-guidelines.md for detailed procedures.
    </action>
    <constraints>
      - CRITICAL: Only copy if mockups NOT already in feature folder (avoid duplicates)
      - Preserve original filenames when copying
    </constraints>
    <output>Mockups in feature folders (or confirmed absent)</output>
  </step_4>

  <step_5>
    <name>Create/Update Requirement Summary</name>
    <action>
      1. Determine target file:
         - IF parts exist -- update CURRENT ACTIVE PART (highest part number)
         - ELSE -- update x-ipe-docs/requirements/requirement-details.md
      2. Add Feature List table:

         | Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
         |------------|---------|---------------|---------|-------------------|-------------------|
         | FEATURE-001-A | EPIC-001 | ... | v1.0 | ... | None |
         | FEATURE-001-B | EPIC-001 | ... | v1.0 | ... | FEATURE-001-A |

         ⛔ **Feature ID column MUST only contain `FEATURE-{nnn}-{X}` values — NEVER `EPIC-{nnn}`.** Epic IDs go in the Epic ID column only.

      3. Add detailed sections for each feature

      See: references/breakdown-guidelines.md for file structure templates.
    </action>
    <constraints>
      - BLOCKING: Feature List goes into the PART FILE, NOT the index
      - Each part file has its OWN Feature List section
    </constraints>
    <output>Requirement-details file updated with feature list and details</output>
  </step_5>

  <step_6>
    <name>Update Feature Board</name>
    <action>
      CALL x-ipe+feature+feature-board-management skill:
        operation: create_or_update_features
        features:
          - feature_id: FEATURE-001-A
            epic_id: EPIC-001
            title: "{title}"
            version: v1.0
            description: "{description}"
            dependencies: []
          [... for all features]
    </action>
    <constraints>
      - BLOCKING: MUST use feature-board-management skill (not manual file editing)
    </constraints>
    <output>Features created on x-ipe-docs/planning/features.md with status "Planned"</output>
  </step_6>

  <step_7>
    <name>Update Index</name>
    <action>
      Only execute if requirement-details-part-X.md files exist:
      1. Open x-ipe-docs/requirements/requirement-details-index.md
      2. Update "Parts Overview" table with new feature range
      3. Update "Lines" column with approximate line count

      See: references/breakdown-guidelines.md for index file structure.
    </action>

    <output>Index updated (or skipped if no parts)</output>
  </step_7>

  <step_8>
    <name>Parent Feature Deduplication Check</name>
    <action>
      1. IF no feature was split into sub-features (no parent-child relationship created):
         - Skip this step entirely
      2. For each parent feature that was split (e.g., FEATURE-001 → FEATURE-001-A, B, C):
         a. List the parent's FRs/ACs from requirement-details
         b. List the union of all sub-features' FRs/ACs
         c. Compare coverage:
            - For each parent FR/AC, check if it is covered by at least one sub-feature
         d. Produce a coverage table:
            | Parent FR/AC | Covered By | Status |
            |-------------|------------|--------|
            | FR-001.1 | FEATURE-001-A (FR-001-A.1) | ✅ Covered |
            | FR-001.2 | FEATURE-001-B (FR-001-B.3) | ✅ Covered |
            | FR-001.5 | — | ❌ Gap |
      3. IF 100% coverage (all parent FRs/ACs covered by sub-features):
         - Remove parent feature from requirement-details file (keep sub-features only)
         - CALL feature-board-management to archive/remove parent feature from board
         - Log: "Parent {FEATURE-XXX} fully covered by sub-features, removed to avoid duplication"
      4. IF partial coverage (some parent FRs/ACs not covered):
         - Keep parent feature in requirement-details
         - Add note to parent: "Partially split — uncovered items: {list}"
         - Flag gap for human review in Step 9
    </action>
    <constraints>
      - BLOCKING: MUST use feature-board-management skill to remove parent (not manual editing)
      - CRITICAL: Only remove parent when 100% coverage confirmed
      - CRITICAL: Coverage comparison must be FR/AC level, not just title matching
    </constraints>
    <output>Dedup result: parents removed or gaps flagged</output>
  </step_8>

  <step_9>
    <name>Complete</name>
    <action>
      1. IF execution_mode == "workflow-mode":
         a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
            - workflow_name: {from context}
            - action: {workflow.action}
            - status: "done"
            - deliverables: {"features-list": "{path to features list file}", "breakdown-folder": "{path to breakdown/ folder}"}
            - features: [list of feature objects from Step 6, each with id, name, depends_on]
              Example: [{"id": "FEATURE-001-A", "name": "Login Page", "depends_on": []},
                        {"id": "FEATURE-001-B", "name": "Dashboard", "depends_on": ["FEATURE-001-A"]}]
         b. Log: "Workflow action status updated to done with features"
         NOTE: The tool automatically populates per-feature workflow structures and
               sets next_actions_suggested to features with no dependencies.
               No separate add_features API call is needed.
      2. Verify all DoD checkpoints
      3. Output task completion summary
      4. Request human review
    </action>
    <output>Task completion output, workflow_action_updated</output>
  </step_9>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "requirement-stage"
  status: completed | blocked
  next_task_based_skill: "x-ipe-task-based-feature-refinement"
  require_human_review: yes
  auto_proceed: "{from input auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"      # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  task_output_links:
    - "x-ipe-docs/requirements/requirement-details.md"  # or requirement-details-part-X.md
  mockup_list: "{inherited from input or N/A}"
  # Dynamic attributes
  requirement_id: "REQ-XXX"
  feature_ids: ["FEATURE-001-A", "FEATURE-001-B", "FEATURE-001-C"]
  feature_count: 3
  epic_id: "EPIC-{nnn}"  # Parent Epic
  requirement_details_part: null | 1 | 2  # current active part number (null if no parts)
  parent_features_removed: []  # list of parent FEATURE-XXX IDs removed due to full sub-feature coverage
  dedup_gaps: []  # list of partially covered parents with uncovered FRs
  linked_mockups:
    - mockup_name: "Description of mockup function"
      mockup_path: "x-ipe-docs/requirements/EPIC-XXX/mockups/mockup-name.html"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
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
    <verification>Check features.md shows status "Planned" for all new features</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Index updated (if parts exist)</name>
    <verification>requirement-details-index.md updated with new feature range</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockups copied to feature folders</name>
    <verification>Mockup files exist in x-ipe-docs/requirements/EPIC-{nnn}/mockups/ (shared at Epic level)</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Linked Mockups section updated</name>
    <verification>Linked Mockups table populated in requirement-details</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Parent feature deduplication verified</name>
    <verification>If features were split, parent coverage checked — fully covered parents removed, partial coverage gaps flagged</verification>
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

### Pattern: Clear Requirements

**When:** Well-documented requirements exist
**Then:**
```
1. Read requirement-details.md thoroughly
2. Identify natural feature boundaries
3. Apply MVP-first principle
4. Document dependencies between features
```

### Pattern: Vague Requirements

**When:** Requirements are ambiguous or incomplete
**Then:**
```
1. Ask clarifying questions to human
2. Document assumptions made
3. Start with minimal feature set
4. Flag areas needing more detail
```

### Pattern: Large Scope

**When:** Requirement covers many features
**Then:**
```
1. Group by domain/functionality
2. Identify MVP core (first feature)
3. Create feature hierarchy
4. Limit initial breakdown to 5-7 features
```

### Pattern: Feature Split with Parent Dedup

**When:** A parent feature is split into sub-features (e.g., FEATURE-001 → A, B, C)
**Then:**
```
1. After splitting, compare parent FRs against union of sub-feature FRs
2. If 100% covered → remove parent from board and requirement-details
3. If partial → keep parent, flag uncovered FRs for human review
4. Use feature-board-management for all board changes
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Too many features | Overwhelming, hard to track | Limit to 5-7 features max |
| Features too granular | Micromanagement | Combine related functions |
| MVP not first | Critical path unclear | Always start with runnable MVP |
| Circular dependencies | Impossible to implement | Ensure DAG structure |
| Manual board updates | Inconsistent state | Use feature-board-management skill |
| Vague feature titles | Unclear scope | Use specific, action-oriented names |
| Keeping duplicate parent | Redundant tracking, confusing | Remove parent if fully covered by sub-features |

---

## Examples

See [references/examples.md](references/examples.md) for detailed execution examples including:
- E-commerce platform feature breakdown
- API integration feature breakdown
- Change request (NEW_FEATURE) breakdown
- Granularity and sizing guidelines
