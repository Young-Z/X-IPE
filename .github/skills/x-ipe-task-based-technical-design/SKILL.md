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

**BLOCKING: Single Feature Only.** This skill operates on exactly ONE feature at a time. Do NOT batch or combine multiple features in a single execution. If multiple features need processing, run this skill separately for each feature.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

### Key Rules

- **Two-Part Document:** All technical designs use Part 1 (Agent-Facing Summary) + Part 2 (Implementation Guide). See [references/design-principles.md](.github/skills/x-ipe-task-based-technical-design/references/design-principles.md) for structure details.
- **Single File:** Maintain ONE `technical-design.md` per feature. Do NOT create versioned files. Use Version History table inside the document.
- **Design Principles:** Follow KISS, YAGNI, DRY, and 800-line module threshold. See [references/design-principles.md](.github/skills/x-ipe-task-based-technical-design/references/design-principles.md) for details.
- **Document Location:** Feature-specific at `x-ipe-docs/requirements/FEATURE-XXX/technical-design.md`; cross-feature at `x-ipe-docs/architecture/technical-designs/{component}.md`.
- **Templates:** See [references/design-templates.md](.github/skills/x-ipe-task-based-technical-design/references/design-templates.md) for full document template, Part 1/Part 2 guidelines, dependency table format, mockup reference guidelines, and diagram examples.

### Mockup List Loading

When `mockup_list` input is needed, resolve in this order:
1. Previous Idea Mockup task's `task_output_links`
2. Human-provided explicit path
3. Feature specification's "Linked Mockups" section
4. Idea summary's "Mockups & Prototypes" section
5. Default: N/A

MANDATORY: When mockup_list is provided AND scope includes [Frontend] or [Full Stack], the agent MUST open, analyze, extract UI requirements, and reference mockups in Part 2.

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-technical-design"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      specification: "path | N/A | auto-detect"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-implementation"
      condition: "Implement the designed feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  feature_phase: "Technical Design"

  # Required inputs
  mockup_list: "N/A"

  # Context (from previous task or project)
  feature_id: "{FEATURE-XXX}"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="feature_id" source="previous task | task board | human input">
    <steps>
      1. Check previous task (Feature Refinement) output for feature_id
      2. If not available, query task board for current feature context
      3. If still unresolved, ask human for feature_id
    </steps>
  </field>
  <field name="extra_context_reference.specification" source="workflow context | auto-detect">
    <steps>
      1. If workflow-mode: read from workflow context extra_context_reference.specification
      2. If free-mode or auto-detect: resolve from x-ipe-docs/requirements/{feature_id}/specification.md
      3. Default: N/A
    </steps>
  </field>
  <field name="mockup_list" source="previous task | human input | N/A">
    <steps>
      1. IF previous task was "Feature Refinement" → use previous task output's mockup_list field (or derive from linked_mockups)
      2. ELIF human provides explicit mockup links → use human-provided value
      3. ELSE → set to N/A
    </steps>
  </field>
</input_init>
```

> **Note on `program_type` and `tech_stack`:** These fields are **determined during Step 5** (not provided as input). The agent identifies them from the design decisions and includes them in the Output Result for downstream skills.

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

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Query Feature Board, 1.2 Read Specification | Load feature data, read specification | Full context gathered |
| 2. 审问之 — Inquire Thoroughly | 2.1 Reference Architecture, 2.2 Research Best Practices | Check existing patterns, research libraries and best practices | Research complete |
| 3. 慎思之 — Think Carefully | 3.1 Create Technical Design Document | Write two-part technical design document | Design written |
| 4. 明辨之 — Discern Clearly | 4.1 Self-Critique Design | AI validates design against spec; escalates ONLY specific unresolvable conflicts | Design validated |
| 5. 笃行之 — Practice Earnestly | 5.1 Complete | Verify DoD, update workflow, output summary | Task complete |
| 继续执行 | 6.1 | Decide Next Action | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Execution started |

BLOCKING: Phase 1 fails if feature not on board or status not "Done Feature Refinement".
BLOCKING (manual/stop_for_question): Phase 4 - present design, ask if architecture decisions are correct before Code Implementation.
BLOCKING (auto): Proceed automatically after DoD verification.

---

## Execution Procedure

```xml
<procedure name="technical-design">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">
    <step_1_1>
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
    </step_1_1>

    <step_1_2>
      <name>Read Specification</name>
      <action>
        0. Resolve extra_context_reference inputs:
           - FOR ref specification:
             IF workflow mode AND extra_context_reference.specification is a file path:
               READ the file at that path (use instead of specification_link)
             ELIF extra_context_reference.specification is "auto-detect":
               Use existing discovery logic below
             ELIF extra_context_reference.specification is "N/A":
               Skip this context input
             ELSE (free-mode / absent):
               Use existing behavior
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
    </step_1_2>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <step_2_1>
      <name>Reference Architecture</name>
      <action>
        1. READ x-ipe-docs/architecture/ for existing patterns
        2. IDENTIFY reusable components, established conventions, integration requirements
        3. AVOID reinventing existing solutions
      </action>
      <output>List of applicable patterns and reusable components</output>
    </step_2_1>

    <step_2_2>
      <name>Research Best Practices</name>
      <action>
        1. CONSULT TOOL SKILLS (config-filtered):
           a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/ for available tools
           b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.implement.technical_design
              - IF section missing/empty → config_active = false (all discovered tools enabled)
              - ELSE → config_active = true (opt-in filtering); force-enable general
           c. FILTER: IF config_active → only ENABLED tools participate
           d. FOR EACH enabled tool: read "Built-In Practices" and "Operations" sections
           e. DOCUMENT as "Tool Capability Summary" (informational only — not binding)
        2. SEARCH official documentation, libraries, reference implementations, API docs
        3. IF mockup_list provided AND scope includes [Frontend] or [Full Stack]:
           OPEN and analyze all mockup files. EXTRACT layout, components, spacing, colors, interactions. The mockup is source of truth for visual design.
        4. DOCUMENT findings for design decisions (include tool capability summary)
      </action>
      <constraints>
        - Tool consultation is INFORMATIONAL ONLY — do not invoke tools for code execution
        - Part 2 format MUST remain independent of tool availability (FR-048.1.5)
      </constraints>
      <output>Research findings including tool capability summary and mockup constraints if applicable</output>
    </step_2_2>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <step_3_1>
      <name>Create Technical Design Document</name>
      <action>
        1. WRITE two-part technical design at x-ipe-docs/requirements/FEATURE-XXX/technical-design.md
        2. ADAPT structure based on implementation type (API, CLI, frontend, backend)
        3. USE templates from references/design-templates.md
        4. IF mockup_list provided AND scope includes [Frontend] or [Full Stack]:
           Open mockup files, extract UI component requirements, design frontend components based on mockup layout, reference mockup in Part 2
           ELSE: Focus on service architecture, data models, APIs
        5. INCLUDE Design Change Log section at end of document
        6. IDENTIFY and record program_type and tech_stack:
           - program_type: classify using known types (non-exhaustive, extend as needed):
             - "frontend": Browser-only (HTML/CSS/JS, no server logic)
             - "backend": Server-only (API, services, data processing)
             - "fullstack": Both server routes AND browser UI (JS/CSS)
             - "cli": Command-line tool
             - "library": Reusable package/module
             - "skills": Agent skill definitions (SKILL.md, prompt engineering)
             - "mcp": MCP server tools/endpoints
             - Other types may emerge as tech evolves — use descriptive lowercase names
           - tech_stack: list all technologies used (e.g. ["Python/Flask", "JavaScript/Vanilla", "HTML/CSS", "pytest"])
           - These are passed to downstream skills (Test Generation, Code Implementation) to determine test types
        7. LEVERAGE tool capability summary from Step 2.2:
           - Reference tool built-in practices instead of duplicating (e.g., "Python tool enforces PEP 8")
           - Focus Part 2 on what tools NEED: module boundaries, API contracts, data models
           - Note: Part 2 format remains independent of tool availability
      </action>
      <constraints>
        - MANDATORY: Part 1 must have component table with Tags for semantic search
        - MANDATORY: Part 1 must have usage example
        - MANDATORY: File links in generated markdown MUST use project-root-relative paths so the UI can intercept them and open a preview modal. **Avoid** relative paths (`../`, `./`, `../../`) and absolute filesystem paths (`/Users/...`). **Correct:** `[spec](x-ipe-docs/requirements/EPIC-001/specification.md)`, `[skill](.github/skills/x-ipe-task-based-bug-fix/SKILL.md)`. **Wrong:** `[spec](../specification.md)`, `[spec](./specification.md)`.
        - CRITICAL: Follow KISS/YAGNI/DRY principles
      </constraints>
      <output>Complete two-part technical design document</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <step_4_1>
      <name>Self-Critique Design</name>
      <action>
        1. AI self-critique — validate the design against objective criteria:
           a. Every specification acceptance criterion maps to a component or flow
           b. No contradictions between chosen patterns (e.g., stateless API + server-side sessions)
           c. Technology choices are compatible (versions, licenses, runtime)
           d. No over-engineering: each component has a clear reason from the spec
        2. Collect unresolved_questions[] — ONLY items AI genuinely cannot decide:
           - Trade-offs needing user preference (e.g., "Redis vs Memcached?")
           - Business-domain constraints AI lacks context for
           - Conflicting requirements needing human prioritization
        3. IF unresolved_questions is EMPTY → design is validated, proceed
        4. IF unresolved_questions is NON-EMPTY:
           IF process_preference.interaction_mode == "dao-represent-human-to-interact":
             → Invoke x-ipe-dao-end-user-representative with specific questions list
           ELSE:
             → Present ONLY the specific questions to human (not "review the whole design")
           → Incorporate answers, revise affected sections
      </action>
      <constraints>
        - MUST NOT ask broad "is this correct?" — only ask specific, bounded questions
        - IF self-critique passes with zero questions → skip human/DAO entirely
      </constraints>
      <output>Design validated (self-critique passed or specific questions resolved)</output>
    </step_4_1>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1>
      <name>Complete</name>
      <action>
        1. VERIFY all DoD checkpoints are met
        2. IF execution_mode == "workflow-mode":
           a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
              - workflow_name: {from context}
              - action: {workflow.action}
              - status: "done"
              - feature_id: {feature_id}
              - deliverables: {"tech-design": "{path to technical-design.md}", "feature-docs-folder": "{path to FEATURE-XXX/ folder}"}
           b. Log: "Workflow action status updated to done"
        3. OUTPUT task completion summary
      </action>
      <success_criteria>
        - All required DoD checkpoints pass
        - Design document created at correct location
        - feature_phase set to "Technical Design"
      </success_criteria>
      <output>Task completion output with design document link, workflow_action_updated</output>
    </step_5_1>

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
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-implementation"
      condition: "Implement the designed feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"   # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
  # Dynamic attributes
  mockup_list: {from input mockup_list, pass to next task if applicable}
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Technical Design"
  # Tech context (determined in Step 5, passed to downstream skills)
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."  # non-exhaustive
  tech_stack: ["Python/Flask", "JavaScript/Vanilla", "HTML/CSS"]  # example
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
  <checkpoint required="if-applicable">
    <name>Workflow Action Updated</name>
    <verification>If execution_mode == "workflow-mode", called the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with status "done" and deliverables keyed dict</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| API-Based | REST/GraphQL endpoints | Focus Part 2 on API spec, request/response schemas, auth, sequence diagrams |
| Background Service | Background process | Fault tolerance, retry/backoff, monitoring points, state diagrams |
| UI-Heavy | Primarily frontend | Component architecture, state management, mockup references (mockup = source of truth) |

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

See [references/examples.md](.github/skills/x-ipe-task-based-technical-design/references/examples.md) for detailed execution examples.
