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

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

Load `x-ipe-workflow-task-execution` and its
[common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Reuse the supplied task/readiness; direct entry calls Orient/Plan once without
recursively dispatching this skill. One owner handles task/feature/app writes,
Git and the next boundary. Return full output; do not register or execute a
successor. Within-skill questions follow the three existing interaction modes;
clear inputs need no question or DAO call. Explicit human approvals still bind.

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
  <field name="task_id" source="existing lifecycle task/readiness; no duplicate registration" />
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
  <checkpoint required="true"><name>Scope and owner</name><verification>Approved current task/readiness, idea identity and permitted artifact paths are known.</verification></checkpoint>
  <checkpoint required="true"><name>Source</name><verification>Selected idea sources resolve safely; broken explicit links or conflicting identities are not hidden.</verification></checkpoint>
  <checkpoint required="true"><name>Capabilities</name><verification>Applicable configuration and required capabilities are known; unavailable work is explicit.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Work | Evidence |
| --- | --- | --- |
| 1 | Read the Idea and Bound the Diagram | Source-backed high-level architecture needs |
| 2 | Generate the Useful Views | Selected diagrams and new linked summary version |
| 3 | Verify and Return | Original architecture result with bounded evidence |

## Execution Procedure

```xml
<procedure name="idea-to-architecture">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Read the Idea and Bound the Diagram</name>
    <action>
      1. Resolve current_idea_folder from explicit input or previous output; load highest numeric summary in refined-idea/ or legacy folder. Broken explicit links and ambiguous identity block, never select another idea by date.
      2. Read only relevant system components, relationships, integrations, data flows, constraints and trust boundaries. Stay high-level: no unrequested detailed schema, deployment scripts or UI styling.
      3. Inspect tools.json stages.ideation.architecture, literal true capabilities and _extra_instruction. Load only selected diagram expertise; configured availability is not a requirement to generate every diagram type.
    </action>
    <output>Source-backed high-level architecture needs</output>
  </step_1>
  <step_2>
    <name>Generate the Useful Views</name>
    <action>
      1. Choose only views needed to explain the idea: system/module, data flow, sequence or integration. One sufficient diagram is valid; additional perspectives require a concrete gap, not a quota.
      2. Resolve material uncertainty through the shared mode policy. Use enabled diagram capability in the same loop; if none is available, use an explicitly agreed architecture-description.md and label it as text.
      3. Save versioned diagrams under {current_idea_folder}/architecture/. Preserve existing summaries; create idea-summary-v{N+1}.md from the resolved summary with diagram links and decisions, all project-root-relative.
    </action>
    <output>Selected diagrams and new linked summary version</output>
  </step_2>
  <step_3>
    <name>Verify and Return</name>
    <action>
      1. Self-check relevant components, relationships, data/trust boundaries, source consistency and selected DSL validity or rendered view where supported. No mandatory fresh-agent review or alternate diagram merely to satisfy process.
      2. Return the original output fields and actual diagrams_created/current_idea_folder/version. There is no architecture app action in current ACTION_MAP: do not invent workflow action/status/deliverable tags.
      3. Return to the existing owner for task recording and one authorized boundary. Recommend requirements, optional mockup or sharing without executing them.
    </action>
    <output>Original architecture result with bounded evidence</output>
  </step_3>
</procedure>
```

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

```xml
<definition_of_done>
  <checkpoint required="true"><name>Requested outcome</name><verification>Actual artifacts preserve source intent and meet the requested domain scope; unresolved required gaps remain blocked.</verification></checkpoint>
  <checkpoint required="true"><name>Verified evidence</name><verification>Applicable checks ran or current suitable evidence was reused; no fabricated pass, score or observed stakeholder benefit.</verification></checkpoint>
  <checkpoint required="true"><name>Original handoff</name><verification>Original output fields, real paths and conditional suggestions return to the same owner; no duplicate lifecycle or unauthorized app/Git work.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

Use the smallest set of views that explains the system. One adequate diagram is valid. Preserve high-level components/data/trust boundaries; do not add implementation detail or a diagram quota.

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-idea-to-architecture/references/examples.md) for concrete execution examples:
- Architecture with mermaid tool enabled
- Architecture without tools (manual mode)
- Missing idea folder (blocked scenario)
- No idea summary (blocked scenario)
- Microservices architecture (complex system)
