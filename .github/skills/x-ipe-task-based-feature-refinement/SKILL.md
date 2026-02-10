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

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Feature Refinement"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "Technical Design"
  require_human_review: yes
  feature_phase: "Feature Refinement"

  # Required inputs
  auto_proceed: false
  mockup_list: "N/A"  # Path to mockup file(s) from previous Idea Mockup task or context

  # Context (from previous task or project)
  feature_id: "{FEATURE-XXX}"
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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Gather Context | Read requirement-details.md, check dependencies, analyze mockups | Context understood |
| 3 | Process Mockups | Auto-detect mockups from idea folder if not in feature folder | Mockups processed |
| 4 | Create Spec | Create/update `specification.md` with all sections | Specification written |
| 5 | Complete | Verify DoD, output summary, request human review | Human review |

BLOCKING: Step 1 fails if feature not on board or status not "Planned".
BLOCKING: Step 3 MUST scan for mockups if feature folder has no `mockups/` directory.
BLOCKING: Human MUST approve specification before Technical Design proceeds.

---

## Execution Procedure

```xml
<procedure name="feature-refinement">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Query Feature Board</name>
    <action>
      1. CALL x-ipe+feature+feature-board-management skill:
         operation: query_feature, feature_id: {feature_id from task_data}
      2. RECEIVE Feature Data Model (feature_id, title, version, status, description, dependencies, timestamps)
      3. Use data to understand context, check dependencies, get description, determine if specification exists
    </action>
    <constraints>
      - BLOCKING: Feature must exist on board with status "Planned"
    </constraints>
    <output>Feature Data Model loaded</output>
  </step_1>

  <step_2>
    <name>Gather Context</name>
    <action>
      1. IF x-ipe-docs/requirements/requirement-details.md exists:
         READ for overall context, related features, business goals
      2. IF feature has dependencies:
         FOR EACH dependency -- check if specification exists, read integration points
      3. IF feature has architecture implications:
         CHECK x-ipe-docs/architecture/ for relevant designs
      4. Web search (recommended): domain rules, compliance (GDPR, PCI-DSS, HIPAA),
         UX best practices, common pitfalls, accessibility (WCAG)
      5. IF mockup_list is provided:
         Analyze mockup file(s), extract UI/UX requirements,
         document in "UI/UX Requirements" section with acceptance criteria,
         identify gaps (missing interactions, loading/empty/error states)
    </action>
    <output>Full context gathered including mockup analysis</output>
  </step_2>

  <step_3>
    <name>Process Mockups</name>
    <action>
      MANDATORY: Auto-detect and copy mockups if not in feature folder.

      1. CHECK x-ipe-docs/requirements/{FEATURE-ID}/mockups/
         IF exists AND contains files -- skip to Step 4
      2. IF mockups NOT in feature folder:
         a. Check requirement-details.md for idea folder reference
         b. IF idea folder exists -- scan x-ipe-docs/ideas/{idea-folder}/mockups/
         c. IF mockups found:
            - Create x-ipe-docs/requirements/{FEATURE-ID}/mockups/
            - Copy ALL mockup files from idea folder
            - Update mockup_list with copied paths
      3. IF mockup_list provided AND not yet copied:
         - Create mockups folder, copy each mockup, update paths
      4. IF no mockups found -- log and proceed
    </action>
    <constraints>
      - CRITICAL: Only copy if mockups NOT already in feature folder (avoid duplicates)
      - Preserve original filenames when copying
      - Create mockups folder only if mockups found
    </constraints>
    <output>Mockups in feature folder (or confirmed absent)</output>
  </step_3>

  <step_4>
    <name>Create/Update Feature Specification</name>
    <action>
      1. Create or update: x-ipe-docs/requirements/FEATURE-XXX/specification.md
      2. Follow specification template structure from references/specification-template.md
      3. Include all sections: Version History, Linked Mockups (if applicable),
         Overview, User Stories, Acceptance Criteria, Functional Requirements,
         Non-Functional Requirements, UI/UX Requirements, Dependencies,
         Business Rules, Edge Cases, Out of Scope, Technical Considerations, Open Questions
      4. IF mockups exist in FEATURE-XXX/mockups/:
         a. Assess mockup freshness -- compare mockup content against current feature scope:
            - IF mockup aligns with current feature scope: mark as "current" in Linked Mockups table
            - IF mockup is outdated (feature scope changed significantly since mockup was created): mark as "outdated -- use as directional reference only"
         b. For each current (non-outdated) mockup, add acceptance criteria that reference mockup comparison:
            - AC: "UI layout MUST match the approved mockup ({mockup-filename}) for [component/screen]"
            - AC: "Visual styling (colors, spacing, typography) MUST be consistent with mockup ({mockup-filename})"
            - AC: "Interactive elements shown in mockup ({mockup-filename}) MUST be present and functional"
         c. For outdated mockups, do NOT add mockup-comparison ACs -- instead note in UI/UX Requirements:
            "Mockup {filename} is outdated; use as directional reference only. Implementation should follow the updated requirements in this specification."
    </action>
    <constraints>
      - MANDATORY: Single file with version history (no versioned filenames)
      - CRITICAL: Focus on WHAT not HOW in Technical Considerations
      - CRITICAL: Only add mockup-comparison ACs for current mockups, never for outdated ones
      - See references/specification-template.md for full structure
      - See references/specification-writing-guide.md for detailed guidance
    </constraints>
    <success_criteria>
      - All specification sections completed
      - Acceptance criteria are testable and measurable
      - Dependencies documented
      - Edge cases identified
      - If current mockups exist, ACs reference mockup comparison
    </success_criteria>
    <output>specification.md created/updated</output>
  </step_4>

  <step_5>
    <name>Complete</name>
    <action>
      1. Verify all DoD checkpoints
      2. Output task completion summary
      3. Request human review
    </action>
    <output>Task completion output with specification path</output>
  </step_5>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "x-ipe-task-based-technical-design"
  require_human_review: yes
  auto_proceed: "{from input auto_proceed}"
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
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Mockup-Driven Refinement

**When:** Mockup List is provided from Idea Mockup task
**Then:**
```
1. Open and thoroughly analyze mockup file(s)
2. Assess mockup freshness against current feature scope:
   - Current: scope unchanged since mockup creation → add mockup-comparison ACs
   - Outdated: scope changed significantly → mark outdated, use as directional reference only
3. Extract all visible UI elements and interactions
4. Create UI/UX Requirements section with:
   - Component inventory from mockup
   - User interaction flows
   - Form validation rules
   - Error/empty/loading states
5. Add "Linked Mockups" section at top of specification (with status column)
6. For current mockups: add ACs like "UI layout MUST match mockup ({filename})"
7. Cross-reference acceptance criteria to mockup elements
8. Note any functionality implied by mockup not in requirements
```

### Pattern: Well-Defined Feature

**When:** Feature has clear scope from breakdown
**Then:**
```
1. Query feature board for context
2. Read requirement-details.md
3. Create specification with standard sections
4. Request human review
```

### Pattern: Feature with Dependencies

**When:** Feature depends on other features
**Then:**
```
1. Read dependent feature specifications first
2. Identify integration points
3. Document assumptions about dependencies
4. Note blocking vs non-blocking dependencies
```

### Pattern: Complex Domain

**When:** Feature involves unfamiliar domain rules
**Then:**
```
1. Research domain best practices (web search)
2. Document compliance requirements
3. Include domain glossary in specification
4. Ask human for domain-specific clarifications
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip board query | Missing context | Always query feature board first |
| Vague acceptance criteria | Untestable | Make criteria specific and measurable |
| Technical implementation details | Wrong focus | Focus on WHAT, not HOW |
| Ignore dependencies | Integration failures | Document all dependencies |
| Multiple specification files | Version confusion | Single file with version history |
| Skip web research | Reinvent wheel | Research domain best practices |
| Ignore mockup when provided | Missing UI requirements | Always analyze mockup_list |
| Skip mockup-to-spec mapping | Incomplete specification | Extract all UI elements from mockup |
| Compare against outdated mockup | Wrong ACs, blocks progress | Check mockup freshness; only add comparison ACs for current mockups |

---

## Examples

See [references/examples.md](references/examples.md) for detailed execution examples including:
- User authentication specification
- Enhancement refinement from change request
- Missing feature entry (blocked)
- Complex feature requiring split
- Specification with thorough edge case coverage
