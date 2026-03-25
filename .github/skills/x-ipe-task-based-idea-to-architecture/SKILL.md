---
name: x-ipe-task-based-idea-to-architecture
description: Create architecture diagrams for refined ideas. Use after ideation when idea needs system architecture visualization. Generates architecture diagrams using tools from x-ipe-docs/config/tools.json (mermaid, excalidraw). Triggers on requests like "create architecture", "design system", "architecture diagram", "system design".
---

# Task-Based Skill: Idea to Architecture

## Purpose

Create architecture diagrams and system design visualizations for refined ideas by:
1. Reading the idea summary from ideation task
2. Loading architecture tools from `x-ipe-docs/config/tools.json` config
3. Creating architecture diagrams (system architecture, component diagrams, data flow)
4. Saving artifacts to the idea folder
5. Preparing for Requirement Gathering

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` and `x-ipe+all+task-board-management` skills before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

### High-Level Architecture Focus

CRITICAL: Architecture diagrams must focus on system-level design, not implementation specifics. Detailed design comes later during Technical Design.

| Focus On | Ignore |
|----------|--------|
| System components and their relationships | Implementation details (code structure) |
| Data flow between components | UI/UX design elements |
| Integration points and APIs | Visual styling and colors |
| Technology stack overview | Database schema details |
| Scalability considerations | Specific library choices |
| Security boundaries | Deployment scripts |

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-idea-to-architecture"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "ideation-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-requirement-gathering"
      condition: "Proceed to requirements after architecture"
    - skill: "x-ipe-task-based-idea-mockup"
      condition: "Create visual mockup if not done"
    - skill: "x-ipe-task-based-share-idea"
      condition: "Share the architecture with stakeholders"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  current_idea_folder: "{path}"   # e.g., x-ipe-docs/ideas/mobile-app-idea
  extra_instructions: null        # Additional context for diagram creation

  # Context (from previous task or project)
  ideation_toolbox_meta: "x-ipe-docs/config/tools.json"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="current_idea_folder" source="previous Ideation task output OR human input">
    <steps>
      1. IF previous task was "Ideation" → use previous task output's current_idea_folder field
      2. ELIF human provides path → use it
      3. IF null → list folders under x-ipe-docs/ideas/ and ask human to select
      4. Validate: folder exists AND contains idea-summary-vN.md
    </steps>
  </field>
  <field name="extra_instructions" source="human-provided > config > null">
    <steps>
      1. IF human provides extra_instructions → use human value
      2. ELIF tools.json stages.ideation.architecture._extra_instruction exists → use config value
      3. ELSE → set to null
      4. When set: incorporate into component identification and diagram creation
    </steps>
  </field>
  <field name="ideation_toolbox_meta" source="default: x-ipe-docs/config/tools.json">
    <steps>
      1. Default path: x-ipe-docs/config/tools.json
      2. Config section: stages.ideation.architecture (e.g., {"mermaid": true, "excalidraw": false})
      3. IF file exists → parse and use enabled tools (value = true)
      4. IF file missing → inform user, offer manual architecture description mode
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Idea folder is set</name>
    <verification>current_idea_folder is not null and folder exists on disk</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Idea summary exists</name>
    <verification>idea-summary-vN.md found in current_idea_folder</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tools config accessible</name>
    <verification>x-ipe-docs/config/tools.json is readable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Architecture tool available</name>
    <verification>At least one tool enabled in config OR human accepts manual mode</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 (Study Broadly) | 1.1 | Validate Folder | Verify current_idea_folder exists with idea summary | Folder validated |
| | 1.2 | Load Config | Read architecture section from tools config | Config loaded |
| | 1.3 | Read Idea Summary | Load latest idea-summary-vN.md | Summary parsed |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Identify Architecture Needs | Extract system components, analyze diagram requirements | Needs identified |
| 3. 慎思之 (Think Carefully) | — | SKIP | Architecture decisions are at idea level, not implementation | — |
| 4. 明辨之 (Discern Clearly) | 4.1 | Select Diagram Types | Choose diagram types and prioritize | Types selected |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Create Diagrams | Generate diagrams using enabled tools | Diagrams created |
| | 5.2 | Save Artifacts | Store in `{current_idea_folder}/architecture/` | Artifacts saved |
| | 5.3 | Update Summary | Create new idea-summary version with diagram links | Summary updated |
| | 5.4 | Complete | Verify DoD, output summary | Task complete |
| 继续执行 | 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: Step 1.1 halts if current_idea_folder is null -- ask human for folder path.
BLOCKING: Step 5.1 halts if no tools available AND human declines manual mode.
BLOCKING (manual/stop_for_question): Step 5.4 - present diagrams, ask if architecture captures the right components.

---

## Execution Procedure

```xml
<procedure name="idea-to-architecture">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Validate Current Idea Folder</name>
      <action>
        1. IF current_idea_folder is null:
           - List folders under x-ipe-docs/ideas/
           - Ask "Which idea folder for architecture?" with available options
           - Set current_idea_folder = selected folder

           Response source (based on interaction_mode):
           IF process_preference.interaction_mode == "dao-represent-human-to-interact":
             → Resolve via x-ipe-dao-end-user-representative
           ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
             → Ask human for selection
        2. Verify folder exists on disk
        3. Verify idea-summary-vN.md exists in folder
      </action>
      <constraints>
        - BLOCKING: Stop if folder not found
        - BLOCKING: Stop if no idea summary -- run Ideation first
      </constraints>
      <output>Validated current_idea_folder path</output>
    </step_1_1>

    <step_1_2>
      <name>Load Architecture Tool Configuration</name>
      <action>
        1. Read x-ipe-docs/config/tools.json
        2. Extract stages.ideation.architecture section
        3. Identify enabled tools (value = true)
        4. Load extra_instructions (human value > config _extra_instruction > null)
      </action>
      <output>List of enabled architecture tools, extra_instructions value</output>
    </step_1_2>

    <step_1_3>
      <name>Read Idea Summary</name>
      <action>
        1. Find latest idea-summary-vN.md (highest version number)
        2. Parse summary content
        3. Extract: overview, key features, technical mentions,
           integration requirements, data flow
      </action>
      <output>Parsed idea summary with architecture-relevant sections</output>
    </step_1_3>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Identify Architecture Needs</name>
      <action>
        1. Analyze: multiple system components? --> System Architecture (C4)
        2. Analyze: data processing or flow? --> Data Flow Diagram
        3. Analyze: user interactions with multiple systems? --> Sequence Diagram
        4. Analyze: integrations or external services? --> Integration Architecture
        5. Apply extra_instructions to component identification if set
      </action>
      <output>List of architecture needs with analysis rationale</output>
    </step_2_1>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <skip reason="Architecture decisions are at idea level, not implementation level. No trade-offs or risk assessment needed — diagram generation is straightforward given identified needs." />
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>Select Diagram Types</name>
      <action>
        1. Based on architecture needs from step 2.1, select diagram types to create
        2. Prioritize diagram list by relevance to the idea
        3. Match diagram types to available tools (mermaid, excalidraw, manual)
        4. Document selection rationale
      </action>
      <output>Prioritized list of diagrams to create with tool assignments</output>
    </step_4_1>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Create Architecture Diagrams</name>
      <action>
        1. For each prioritized diagram type:
           - IF mermaid enabled: generate C4/flowchart/sequence in markdown
           - IF excalidraw enabled: create .excalidraw diagram
           - IF no tools: create architecture-description.md
        2. Use templates from references/architecture-patterns.md
      </action>
      <constraints>
        - CRITICAL: Focus on system-level components, not implementation details
        - MANDATORY: All internal markdown links MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). Do NOT use relative paths like `../` or `./`.
        - BLOCKING: Stop if no tools AND human declines manual mode (auto: DAO decides whether to proceed with manual mode)
      </constraints>
      <output>Generated diagram files</output>
    </step_5_1>

    <step_5_2>
      <name>Save Artifacts</name>
      <action>
        1. Create {current_idea_folder}/architecture/ directory if needed
        2. Save diagrams as {diagram-type}-v{version}.{ext}
           (e.g., system-architecture-v1.md)
        3. Record list of saved artifact paths
      </action>
      <output>List of saved artifact paths</output>
    </step_5_2>

    <step_5_3>
      <name>Update Idea Summary</name>
      <action>
        1. DO NOT modify existing idea-summary files
        2. Create new version: idea-summary-v{N+1}.md
        3. Add architecture diagram references table
        4. Use template from references/architecture-patterns.md
      </action>
      <output>New idea summary version with diagram links</output>
    </step_5_3>

    <step_5_4>
      <name>Complete</name>
      <action>
        1. Verify all DoD checkpoints are met
        2. IF manual/stop_for_question:
              → Present diagrams to human
              → Ask if architecture captures the right components and relationships
              → IF human identifies issues → revise specific components
        3. Compile output result
      </action>
      <success_criteria>
        - All diagrams created and saved
        - New idea summary version references all diagrams
      </success_criteria>
      <output>Completed task output</output>
    </step_5_4>

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
  category: "ideation-stage"
  task_based_skill: "x-ipe-task-based-idea-to-architecture"
  status: "completed"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  idea_id: "IDEA-XXX"
  current_idea_folder: "{current_idea_folder}"
  architecture_tools_used:
    - "mermaid"
  diagrams_created:
    - type: "system-architecture"
      path: "{current_idea_folder}/architecture/system-architecture-v1.md"
    - type: "data-flow"
      path: "{current_idea_folder}/architecture/data-flow-v1.md"
  idea_summary_version: "v{N+1}"
  next_task_based_skill:
    - skill: "x-ipe-task-based-requirement-gathering"
      condition: "Proceed to requirements after architecture"
    - skill: "x-ipe-task-based-idea-mockup"
      condition: "Create visual mockup if not done"
    - skill: "x-ipe-task-based-share-idea"
      condition: "Share the architecture with stakeholders"
  task_output_links:
    - "{current_idea_folder}/architecture/system-architecture-v1.md"
    - "{current_idea_folder}/architecture/data-flow-v1.md"
    - "{current_idea_folder}/idea-summary-v{N+1}.md"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Idea folder validated</name>
    <verification>current_idea_folder exists and contains idea summary</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tools config parsed</name>
    <verification>x-ipe-docs/config/tools.json loaded and architecture section extracted</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Idea summary analyzed</name>
    <verification>Summary read and architecture needs identified</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Diagrams created</name>
    <verification>At least one diagram created using enabled tools or manual mode</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Artifacts saved</name>
    <verification>Files exist in {current_idea_folder}/architecture/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary updated</name>
    <verification>New idea-summary-v{N+1}.md created with diagram links</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Architecture diagrams complete</name>
    <verification>Architecture diagrams generated with all idea components represented</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Tool-Based Diagram Generation

**When:** Architecture tools are enabled in config
**Then:**
```
1. Use enabled tools (mermaid/excalidraw) for diagram creation
2. Generate multiple diagram types based on idea complexity
3. Save all artifacts with versioned naming
```

### Pattern: Manual Architecture Description

**When:** No tools enabled and human accepts manual mode
**Then:**
```
1. Create architecture-description.md with component listing
2. Document relationships and data flow as text
3. Save to {current_idea_folder}/architecture/
```

See [references/architecture-patterns.md](.github/skills/x-ipe-task-based-idea-to-architecture/references/architecture-patterns.md#architecture-patterns) for additional patterns (microservices, simple web app, data pipeline, no technical details).

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Creating diagrams before reading idea | May miss requirements | Always analyze idea first |
| Ignoring tools.json config | Inconsistent tool usage | Always check config |
| Too much detail in initial diagrams | Overwhelms review | Start high-level, add detail if requested |
| Skipping DoD verification | May create wrong architecture | Always verify DoD checkpoints; ask specific questions in manual mode |
| Using disabled tools | Violates config rules | Only use enabled tools |
| Including implementation details | Architecture is high-level | Focus on components and relationships |
| Creating only one diagram type | May miss important views | Consider multiple perspectives |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-idea-to-architecture/references/examples.md) for concrete execution examples:
- Architecture with mermaid tool enabled
- Architecture without tools (manual mode)
- Missing idea folder (blocked scenario)
- No idea summary (blocked scenario)
- Microservices architecture (complex system)
