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

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Idea to Architecture"

  # Task type attributes
  category: "ideation-stage"
  next_task_based_skill: "Requirement Gathering"
  require_human_review: true

  # Required inputs
  auto_proceed: false
  current_idea_folder: "{path}"   # e.g., x-ipe-docs/ideas/mobile-app-idea
  extra_instructions: null        # Additional context for diagram creation

  # Context (from previous task or project)
  ideation_toolbox_meta: "x-ipe-docs/config/tools.json"
```

### Input Resolution Rules

**current_idea_folder:**
- Source: previous Ideation task output, task board, or human input
- IF null: list folders under `x-ipe-docs/ideas/` and ask human to select
- Validate: folder exists AND contains `idea-summary-vN.md`

**extra_instructions:**
- Priority: human-provided value > `stages.ideation.architecture._extra_instruction` from config > null
- When set: incorporate into component identification and diagram creation

**ideation_toolbox_meta** config section:
```json
{ "stages": { "ideation": { "architecture": { "mermaid": true, "excalidraw": false } } } }
```
- File exists: parse and use enabled tools (value = `true`)
- File missing: inform user, offer manual architecture description mode

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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Validate Folder | Verify current_idea_folder exists with idea summary | Folder validated |
| 2 | Load Config | Read architecture section from tools config | Config loaded |
| 3 | Read Idea Summary | Load latest idea-summary-vN.md | Summary parsed |
| 4 | Identify Needs | Extract system components, select diagram types | Needs identified |
| 5 | Create Diagrams | Generate diagrams using enabled tools | Diagrams created |
| 6 | Save Artifacts | Store in `{current_idea_folder}/architecture/` | Artifacts saved |
| 7 | Update Summary | Create new idea-summary version with diagram links | Summary updated |
| 8 | Complete | Request human review and approval | Human approves |

BLOCKING: Step 1 halts if current_idea_folder is null -- ask human for folder path.
BLOCKING: Step 5 halts if no tools available AND human declines manual mode.
BLOCKING: Step 8 requires human approval before proceeding.

---

## Execution Procedure

```xml
<procedure name="idea-to-architecture">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Validate Current Idea Folder</name>
    <action>
      1. IF current_idea_folder is null:
         - List folders under x-ipe-docs/ideas/
         - Ask human to select a folder
         - Set current_idea_folder = selected folder
      2. Verify folder exists on disk
      3. Verify idea-summary-vN.md exists in folder
    </action>
    <constraints>
      - BLOCKING: Stop if folder not found
      - BLOCKING: Stop if no idea summary -- run Ideation first
    </constraints>
    <output>Validated current_idea_folder path</output>
  </step_1>

  <step_2>
    <name>Load Architecture Tool Configuration</name>
    <action>
      1. Read x-ipe-docs/config/tools.json
      2. Extract stages.ideation.architecture section
      3. Identify enabled tools (value = true)
      4. Load extra_instructions (human value > config _extra_instruction > null)
    </action>
    <branch>
      IF: config file missing
      THEN: ask human "Proceed with manual architecture description?"
      ELSE: use enabled tools from config
    </branch>
    <output>List of enabled architecture tools, extra_instructions value</output>
  </step_2>

  <step_3>
    <name>Read Idea Summary</name>
    <action>
      1. Find latest idea-summary-vN.md (highest version number)
      2. Parse summary content
      3. Extract: overview, key features, technical mentions,
         integration requirements, data flow
    </action>
    <output>Parsed idea summary with architecture-relevant sections</output>
  </step_3>

  <step_4>
    <name>Identify Architecture Needs</name>
    <action>
      1. Analyze: multiple system components? --> System Architecture (C4)
      2. Analyze: data processing or flow? --> Data Flow Diagram
      3. Analyze: user interactions with multiple systems? --> Sequence Diagram
      4. Analyze: integrations or external services? --> Integration Architecture
      5. Prioritize diagram list by relevance
      6. Apply extra_instructions to component identification if set
    </action>
    <output>Prioritized list of diagrams to create</output>
  </step_4>

  <step_5>
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
      - BLOCKING: Stop if no tools AND human declines manual mode
    </constraints>
    <output>Generated diagram files</output>
  </step_5>

  <step_6>
    <name>Save Artifacts</name>
    <action>
      1. Create {current_idea_folder}/architecture/ directory if needed
      2. Save diagrams as {diagram-type}-v{version}.{ext}
         (e.g., system-architecture-v1.md)
      3. Record list of saved artifact paths
    </action>
    <output>List of saved artifact paths</output>
  </step_6>

  <step_7>
    <name>Update Idea Summary</name>
    <action>
      1. DO NOT modify existing idea-summary files
      2. Create new version: idea-summary-v{N+1}.md
      3. Add architecture diagram references table
      4. Use template from references/architecture-patterns.md
    </action>
    <output>New idea summary version with diagram links</output>
  </step_7>

  <step_8>
    <name>Complete</name>
    <action>
      1. Present diagrams to human for review
      2. Wait for human approval
      3. Compile output result
    </action>
    <success_criteria>
      - All diagrams created and saved
      - New idea summary version references all diagrams
      - Human has approved the architecture
    </success_criteria>
    <output>Completed task output</output>
  </step_8>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "ideation-stage"
  task_based_skill: "Idea to Architecture"
  status: "completed"
  auto_proceed: "{from input}"
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
  next_task_based_skill: "Requirement Gathering"
  require_human_review: true
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
    <name>Human approved</name>
    <verification>Human has reviewed and approved the architecture diagrams</verification>
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

See [references/architecture-patterns.md](references/architecture-patterns.md#architecture-patterns) for additional patterns (microservices, simple web app, data pipeline, no technical details).

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Creating diagrams before reading idea | May miss requirements | Always analyze idea first |
| Ignoring tools.json config | Inconsistent tool usage | Always check config |
| Too much detail in initial diagrams | Overwhelms review | Start high-level, add detail if requested |
| Skipping human review | May create wrong architecture | Always get approval |
| Using disabled tools | Violates config rules | Only use enabled tools |
| Including implementation details | Architecture is high-level | Focus on components and relationships |
| Creating only one diagram type | May miss important views | Consider multiple perspectives |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples:
- Architecture with mermaid tool enabled
- Architecture without tools (manual mode)
- Missing idea folder (blocked scenario)
- No idea summary (blocked scenario)
- Microservices architecture (complex system)
