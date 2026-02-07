---
name: x-ipe-task-based-technical-design
description: Create technical design for a single feature. Queries feature board, reads specification, designs solution with KISS/YAGNI/DRY principles. Creates two-part design document. Triggers on requests like "design feature", "technical design", "architecture planning".
---

# Task-Based Skill: Technical Design

## Purpose

Create technical design for a single feature by:
1. Querying feature board for full Feature Data Model
2. Reading feature specification document
3. Researching best practices and existing patterns
4. Creating two-part technical design document
5. NO board status update (handled by category skill)

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

### Key Rules

- **Two-Part Document:** All technical designs use Part 1 (Agent-Facing Summary) + Part 2 (Implementation Guide). See [references/design-principles.md](references/design-principles.md) for structure details.
- **Single File:** Maintain ONE `technical-design.md` per feature. Do NOT create versioned files. Use Version History table inside the document.
- **Design Principles:** Follow KISS, YAGNI, DRY, and 800-line module threshold. See [references/design-principles.md](references/design-principles.md) for details.
- **Document Location:** Feature-specific at `x-ipe-docs/requirements/FEATURE-XXX/technical-design.md`; cross-feature at `x-ipe-docs/architecture/technical-designs/{component}.md`.
- **Templates:** See [references/design-templates.md](references/design-templates.md) for full document template, Part 1/Part 2 guidelines, dependency table format, mockup reference guidelines, and diagram examples.

### Mockup List Loading

When `mockup_list` input is needed, resolve in this order:
1. Previous Idea Mockup task's `task_output_links`
2. Human-provided explicit path
3. Feature specification's "Linked Mockups" section
4. Idea summary's "Mockups & Prototypes" section
5. Default: N/A

MANDATORY: When mockup_list is provided AND scope includes [Frontend] or [Full Stack], the agent MUST open, analyze, extract UI requirements, and reference mockups in Part 2.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Technical Design"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "Code Implementation"
  require_human_review: yes
  feature_phase: "Technical Design"

  # Required inputs
  auto_proceed: false
  mockup_list: "N/A"

  # Context (from previous task or project)
  feature_id: "{FEATURE-XXX}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Feature exists on feature board</name>
    <verification>Query feature board for feature_id; confirm entry exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is "Done Feature Refinement"</name>
    <verification>Check feature status field equals "Done Feature Refinement"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature specification document exists</name>
    <verification>Verify file exists at x-ipe-docs/requirements/FEATURE-XXX/specification.md</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Read Spec | Thoroughly read feature specification | Spec understood |
| 3 | Reference Arch | Check existing architecture patterns | Patterns identified |
| 4 | Research | Search for best practices and libraries | Research complete |
| 5 | Create Design | Write two-part technical design document | Design written |
| 6 | Complete | Verify DoD, output summary, request human review | Human review |

BLOCKING: Step 1 is BLOCKED if feature not on board or status not "Done Feature Refinement".
BLOCKING: Step 6 requires human approval before proceeding to Test Generation.

---

## Execution Procedure

```xml
<procedure name="technical-design">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Query Feature Board</name>
    <action>
      1. CALL x-ipe+feature+feature-board-management skill:
         operation: query_feature
         feature_id: {feature_id from task_data}
      2. RECEIVE Feature Data Model:
         feature_id, title, version, status, specification_link
    </action>
    <constraints>
      - BLOCKING: Feature must exist on board with status "Done Feature Refinement"
    </constraints>
    <output>Feature Data Model with specification_link</output>
  </step_1>

  <step_2>
    <name>Read Specification</name>
    <action>
      1. READ {specification_link} from Feature Data Model
      2. UNDERSTAND:
         - User stories and acceptance criteria
         - Business rules and constraints
         - Edge cases documented
         - Dependencies on other features
    </action>
    <constraints>
      - CRITICAL: Do NOT proceed to design until spec is fully understood
    </constraints>
    <output>Comprehensive understanding of feature requirements</output>
  </step_2>

  <step_3>
    <name>Reference Architecture</name>
    <action>
      1. READ x-ipe-docs/architecture/ for existing patterns
      2. IDENTIFY reusable components, established conventions, integration requirements
      3. AVOID reinventing existing solutions
    </action>
    <output>List of applicable patterns and reusable components</output>
  </step_3>

  <step_4>
    <name>Research Best Practices</name>
    <action>
      1. SEARCH for official documentation
      2. LOOK for existing libraries (don't reinvent the wheel)
      3. CHECK reference implementations
      4. REVIEW API documentation for planned libraries
      5. DOCUMENT findings for design decisions
    </action>
    <output>Research findings informing design decisions</output>
  </step_4>

  <step_5>
    <name>Create Technical Design Document</name>
    <action>
      1. WRITE two-part technical design at x-ipe-docs/requirements/FEATURE-XXX/technical-design.md
      2. ADAPT structure based on implementation type (API, CLI, frontend, backend)
      3. USE templates from references/design-templates.md
      4. INCLUDE Design Change Log section at end of document
    </action>
    <branch>
      IF: mockup_list provided AND scope includes [Frontend] or [Full Stack]
      THEN: Open mockup files, extract UI component requirements, design frontend components based on mockup layout, reference mockup in Part 2
      ELSE: Focus on service architecture, data models, APIs
    </branch>
    <constraints>
      - MANDATORY: Part 1 must have component table with Tags for semantic search
      - MANDATORY: Part 1 must have usage example
      - CRITICAL: Follow KISS/YAGNI/DRY principles
    </constraints>
    <output>Complete two-part technical design document</output>
  </step_5>

  <step_6>
    <name>Complete</name>
    <action>
      1. VERIFY all DoD checkpoints
      2. OUTPUT task completion summary
      3. REQUEST human review
    </action>
    <success_criteria>
      - All required DoD checkpoints pass
      - Design document created at correct location
      - feature_phase set to "Technical Design"
    </success_criteria>
    <output>Task completion output with design document link</output>
  </step_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "Code Implementation"
  require_human_review: yes
  auto_proceed: {from input auto_proceed}
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
  # Dynamic attributes
  mockup_list: {from input mockup_list, pass to next task if applicable}
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Technical Design"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Technical design document created</name>
    <verification>File exists at x-ipe-docs/requirements/FEATURE-XXX/technical-design.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Part 1 has component table with tags</name>
    <verification>Verify "Key Components Implemented" table exists with Tags column</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Part 1 has usage example</name>
    <verification>Verify "Usage Example" section exists with code snippet</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Part 2 has workflow diagrams (Mermaid)</name>
    <verification>Check for mermaid code blocks in Part 2</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Part 2 has class diagram (Mermaid)</name>
    <verification>Check for classDiagram mermaid block in Part 2</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Part 2 adapted to implementation type</name>
    <verification>Verify Part 2 sections match implementation type (API/CLI/frontend/backend)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>KISS/YAGNI/DRY principles followed</name>
    <verification>Review design for over-engineering, speculative features, or unnecessary duplication</verification>
  </checkpoint>
  <checkpoint required="if_applicable">
    <name>Mockup List analyzed (if provided AND frontend scope)</name>
    <verification>If mockup_list != N/A and scope is Frontend/Full Stack, verify mockup was referenced</verification>
  </checkpoint>
  <checkpoint required="if_applicable">
    <name>UI components derived from mockup (if frontend scope)</name>
    <verification>If frontend scope with mockup, verify component breakdown references mockup</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: API-Based Feature

**When:** Feature exposes REST/GraphQL endpoints
**Then:**
```
1. Focus Part 2 on API specification
2. Include request/response schemas
3. Document authentication requirements
4. Add sequence diagrams for complex flows
```

### Pattern: Background Service

**When:** Feature runs as background process
**Then:**
```
1. Design for fault tolerance
2. Include retry/backoff strategies
3. Document monitoring points
4. Add state diagrams for lifecycle
```

### Pattern: UI-Heavy Feature

**When:** Feature is primarily frontend
**Then:**
```
1. Focus on component architecture
2. Document state management
3. Include wireframes or mockup references
4. Describe user interaction flows
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Over-engineering | Wasted effort | Apply KISS principle |
| Future-proofing | YAGNI violation | Design for current needs |
| No research | Reinventing wheels | Research existing solutions |
| Monolithic design | Hard to change | Design modular components |
| Missing workflows | Hard to understand | Always include Mermaid diagrams |
| No tags | Hard for AI to find | Always add searchable tags |

---

## Examples

See [references/examples.md](references/examples.md) for detailed execution examples including:
- User authentication technical design
- Complex feature with multiple modules
- Missing specification (blocked)
- Design update from change request
