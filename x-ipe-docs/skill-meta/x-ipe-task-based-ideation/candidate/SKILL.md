---
name: x-ipe-task-based-ideation
description: Learn and refine user ideas through brainstorming. Use when user uploads idea files to Workplace. Analyzes content, asks clarifying questions, and produces structured idea summary. Triggers on "ideate", "brainstorm", "refine idea", "analyze my idea".
---

# Task-Based Skill: Ideation

## Purpose

Learn and refine user ideas through collaborative brainstorming by:
1. Analyzing uploaded idea files from Workplace
2. Generating an initial understanding summary
3. Asking clarifying questions to brainstorm with user
4. Creating a structured idea summary document with visual infographics
5. Preparing for Idea Mockup, Idea to Architecture, or Requirement Gathering

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
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-ideation"
  
  category: ideation-stage
  next_task_based_skill:
    - skill: "x-ipe-task-based-idea-mockup"
      condition: "Create visual mockup of the idea"
    - skill: "x-ipe-task-based-idea-to-architecture"
      condition: "Create architecture diagram for the idea"
    - skill: "x-ipe-task-based-share-idea"
      condition: "Share the refined idea with stakeholders"
    - skill: "x-ipe-task-based-requirement-gathering"
      condition: "Skip to requirements if idea is already clear"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  
  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name from workflow-{name}.json (NOT the idea folder name), default: N/A
    action: "refine_idea"  # hardcoded — this skill ALWAYS updates the refine_idea action
    extra_context_reference:  # optional, default: N/A for all refs
      raw-ideas: "path | N/A | auto-detect"
      uiux-reference: "path | N/A | auto-detect"
  idea_folder_path: "x-ipe-docs/ideas/{folder}"
  toolbox_meta_path: "x-ipe-docs/config/tools.json"
  extra_instructions: "{N/A | from config | from human}"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task/readiness; no duplicate registration" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})">
    NOTE: workflow.name is the {name} part from workflow-{name}.json filename — it is NOT the idea folder name.
    The idea folder name is auto-generated as wf-{NNN}-{sanitized-idea-name} under x-ipe-docs/ideas/.
  </field>
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />

  <field name="idea_folder_path">
    <steps>
      1. IF human specifies folder path → use provided path
      2. ELSE scan x-ipe-docs/ideas/ for most recent folder
    </steps>
  </field>

  <field name="extra_instructions">
    <steps>
      1. IF human provides explicit extra instructions → use human-provided value
      2. ELSE IF x-ipe-docs/config/tools.json exists → read stages.ideation.ideation._extra_instruction field
      3. ELSE → "N/A"
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
| 1 | Read Intent and Relevant Sources | Source-linked intent, constraints, configured capabilities and gaps |
| 2 | Clarify and Shape the Idea | Well-defined idea and explicit decisions or bounded blockers |
| 3 | Write the Refined Summary | Actual versioned idea summary and optional requested artifacts |
| 4 | Verify and Return | Original result, verified summary and one owner boundary |

## Execution Procedure

```xml
<procedure name="ideation">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Read Intent and Relevant Sources</name>
    <action>
      1. Resolve the explicit idea_folder_path and selected raw-ideas/uiux-reference first; otherwise use previous output or one unique matching idea folder. Ambiguous folders require one bounded selection, never pick newest unrelated work.
      2. Read relevant supplied idea files and existing decisions; extract problem, target users, goals, constraints, non-goals and material gaps. Reuse unchanged context, not a new full research pass.
      3. Read tools.json stages.ideation.ideation and applicable ideation tool flags; only literal true enables a capability. Missing config means no optional tool, not auto-create configuration. Discover descriptions now; load a tool skill only when selected.
    </action>
    <output>Source-linked intent, constraints, configured capabilities and gaps</output>
  </step_1>
  <step_2>
    <name>Clarify and Shape the Idea</name>
    <action>
      1. Reuse clear supplied answers. Ask only material unresolved questions, one at a time through the configured interaction policy; full DAO and hybrid use bounded representative guidance, human mode asks the human.
      2. In the same context check clarity, consistency, feasibility and scope. Incorporate useful corrections directly; no mandatory critic agent, separate critique report or repeated approval of already agreed facts.
      3. Research only an unresolved fact that affects the idea, using enabled research capabilities. Label uncited model knowledge; visuals are optional and used only when they clarify requested scope, not because a tool is enabled.
    </action>
    <output>Well-defined idea and explicit decisions or bounded blockers</output>
  </step_2>
  <step_3>
    <name>Write the Refined Summary</name>
    <action>
      1. Use templates/idea-summary.md, keeping user intent, key features, source-derived success criteria, constraints, decisions, references and source links. No invented KPIs or stakeholder observations.
      2. Write {idea_folder_path}/refined-idea/idea-summary-vN.md with the next numeric version. Preserve previous versions and unrelated files; never clear the output folder. Update only owned applicable sections for a small revision.
      3. Use project-root-relative links. Plain Markdown is sufficient; load selected visualization skill only if an enabled, useful visualization is actually needed.
    </action>
    <output>Actual versioned idea summary and optional requested artifacts</output>
  </step_3>
  <step_4>
    <name>Verify and Return</name>
    <action>
      1. Self-check the summary against actual source intent, material decisions, constraints and working links. Apply the shared risk policy rather than spawning a DoD checker.
      2. Return the original task_completion_output and actual paths/current_idea_folder. Workflow owner alone verifies refine_idea and writes keyed refined-idea/refined-ideas-folder deliverables with readback; free-mode no app write.
      3. Owner handles the existing mode-aware completion boundary once and suggests mockup, architecture, sharing or requirements only as needed. This skill does not execute those successors.
    </action>
    <output>Original result, verified summary and one owner boundary</output>
  </step_4>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: ideation-stage
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-idea-mockup"
      condition: "Create visual mockup of the idea"
    - skill: "x-ipe-task-based-idea-to-architecture"
      condition: "Create architecture diagram for the idea"
    - skill: "x-ipe-task-based-share-idea"
      condition: "Share the refined idea with stakeholders"
    - skill: "x-ipe-task-based-requirement-gathering"
      condition: "Skip to requirements if idea is already clear"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  task_output_links:
    - "x-ipe-docs/ideas/{folder}/refined-idea/idea-summary-vN.md"
    - "x-ipe-docs/ideas/{folder}/refined-idea/"
  # Dynamic attributes
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"   # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if workflow_update_action.py was run
  idea_id: "IDEA-XXX"
  idea_status: Refined
  idea_version: "vN"
  current_idea_folder: "x-ipe-docs/ideas/{folder}"
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

Reuse clear answers; ask only material gaps. Plain Markdown and one useful self-check are sufficient. Do not load all enabled tools, generate decorative artifacts, clear output folders, or create a critic/DoD agent for a small idea.

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-ideation/references/examples.md) for concrete execution examples:
- Business plan ideation with tools enabled
- Ideation without tools (all disabled)
- Missing config file handling
