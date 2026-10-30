---
name: x-ipe-task-based-idea-mockup
description: Create visual mockups and prototypes for refined ideas. Use after ideation when idea needs visual representation. Invokes x-ipe-tool-frontend-design skill or other mockup tools based on x-ipe-docs/config/tools.json config. Triggers on requests like "create mockup", "visualize idea", "prototype UI", "design mockup".
---

# Task-Based Skill: Idea Mockup

## Purpose

Create visual mockups and prototypes for refined ideas by:
1. Reading the idea summary from ideation task
2. Loading mockup tools from `x-ipe-docs/config/tools.json` config
3. Creating visual representations (UI mockups, wireframes, prototypes)
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
  task_based_skill: "x-ipe-task-based-idea-mockup"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    action: "design_mockup"  # workflow action name for status updates
    extra_context_reference:  # optional, default: N/A for all refs
      refined-idea: "path | N/A | auto-detect"
      uiux-reference: "path | N/A | auto-detect"

  # Task type attributes
  category: "ideation-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-requirement-gathering"
      condition: "Proceed to requirements after mockup"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  ideation_toolbox_meta: "{project_root}/x-ipe-docs/config/tools.json"
  current_idea_folder: "N/A"  # REQUIRED from context - path to current idea folder
  extra_instructions: "N/A"   # Additional context for mockup creation

  # Context (from previous task or project)
  # current_idea_folder sourced from: previous Ideation output, task board, or human input
  # extra_instructions sourced from: human input > config._extra_instruction > N/A
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task/readiness; no duplicate registration" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="current_idea_folder" source="previous Ideation task output OR task board OR human input">
    <steps>
      1. IF previous task was "Ideation" → use previous task output's current_idea_folder field
      2. ELIF task board has current_idea_folder in task data → use it
      3. ELIF human provides path → use it
      4. IF null → list folders under x-ipe-docs/ideas/ and ask human to select
    </steps>
  </field>
  <field name="extra_instructions" source="human-provided > config > N/A">
    <steps>
      1. IF human provides extra_instructions → use human value
      2. ELIF tools.json stages.ideation.mockup._extra_instruction exists → use config value
      3. ELSE → set to "N/A"
    </steps>
  </field>
  <field name="ideation_toolbox_meta" source="default: x-ipe-docs/config/tools.json">
    <steps>
      1. Default path: {project_root}/x-ipe-docs/config/tools.json
      2. IF file exists → use it
      3. ELSE → inform user, offer manual mode
    </steps>
  </field>
  <field name="extra_context_reference" source="workflow context OR auto-detect">
    <steps>
      1. IF workflow-mode → use workflow.extra_context_reference values
      2. FOR EACH ref in [refined-idea, uiux-reference]:
         IF ref is a file path → use it
         ELIF "auto-detect" → use existing discovery logic
         ELIF "N/A" → skip
      3. ELSE (free-mode) → use existing behavior
    </steps>
  </field>
</input_init>
```

MANDATORY: See [references/mockup-guidelines.md](.github/skills/x-ipe-task-based-idea-mockup/references/mockup-guidelines.md) for Extra Instructions loading logic, Current Idea Folder validation, and tool configuration details.

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
| 1 | Resolve Scope and Capabilities | Resolved summary, UI scope, selected tool and theme |
| 2 | Design and Create | Requested mockups and updated original summary |
| 3 | Verify and Return | Verified artifacts or honest limited output; original owner handoff |

## Execution Procedure

```xml
<procedure name="idea-mockup">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Resolve Scope and Capabilities</name>
    <action>
      1. Resolve selected refined-idea/uiux-reference and current_idea_folder from explicit input or prior output. Find the highest numeric idea-summary-vN.md in refined-idea/ or the legacy idea folder; multiple conflicting sources require bounded clarification.
      2. Read only the summary and UI-relevant context. Inspect tools.json stages.ideation.mockup and _extra_instruction; only true enables a tool. Load only the best matched permitted mockup skill, not every enabled tool.
      3. Inspect selected-theme only when configured. Apply its design-system tokens; broken explicit theme paths are reported rather than silently ignored. If no enabled tool is available, offer a clearly labeled manual description, never claim it is an HTML mockup.
    </action>
    <output>Resolved summary, UI scope, selected tool and theme</output>
  </step_1>
  <step_2>
    <name>Design and Create</name>
    <action>
      1. Choose the smallest useful set of requested screens/states/interactions. Clarify only consequential gaps through the shared interaction policy; do not require new inspiration research for a sufficiently specified design.
      2. Use the selected frontend-design capability in the same agent loop for distinctive accessible layouts. Preserve configured colors/type/spacing, relevant responsive and error/empty states, and UI/UX focus; technology mentions do not force implementation decisions.
      3. Save {current_idea_folder}/mockups/{mockup-type}-v{version}.{ext}; preserve unrelated artifacts. Update the resolved existing idea summary in place with actual project-root-relative mockup links, no unnecessary summary version.
    </action>
    <output>Requested mockups and updated original summary</output>
  </step_2>
  <step_3>
    <name>Verify and Return</name>
    <action>
      1. For actual HTML/browser mockups inspect the rendered requested screens/interactions and runtime errors using an enabled browser capability. Check only applicable states, links and theme fidelity; do not spawn another agent or invent visual scores.
      2. Unavailable required visual checks remain explicit blockers; a manual description is not rendered UI proof. Reuse current evidence rather than rerendering unchanged views at each downstream skill.
      3. Return original output, actual mockup_list and summary/version. Workflow owner alone writes design_mockup with mockup-html and mockups-folder after actual HTML checks/readback. Manual-only output cannot satisfy the HTML action tag. Free-mode has no app write; owner handles one boundary.
    </action>
    <output>Verified artifacts or honest limited output; original owner handoff</output>
  </step_3>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: "ideation-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-requirement-gathering"
      condition: "Proceed to requirements after mockup"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"     # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if workflow_update_action.py was run
  task_output_links:
    - "{current_idea_folder}/mockups/{mockup-type}-v1.html"
    - "{current_idea_folder}/idea-summary-vN.md"
  # Dynamic attributes
  current_idea_folder: "{current_idea_folder}"
  mockup_tools_used:
    - "x-ipe-tool-frontend-design"
  mockup_list:
    - mockup_name: "Dashboard mockup"
      mockup_link: "{current_idea_folder}/mockups/dashboard-v1.html"
    - mockup_name: "User form mockup"
      mockup_link: "{current_idea_folder}/mockups/user-form-v1.html"
  idea_summary_version: "vN"
```

MANDATORY: The `mockup_list` is passed through the chain: Idea Mockup -> Requirement Gathering -> Feature Breakdown -> Feature Refinement -> Technical Design.

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

| Pattern | When | Then |
|---------|------|------|
| Dashboard-Heavy | Data visualization focus | Prioritize dashboard mockup, chart placeholders, responsive layout |
| Form-Heavy | Data input or registration | Form mockups with validation, error/success, multi-step flows |
| No UI Description | Summary lacks UI details | Ask clarifying questions, suggest patterns, create minimal mockup |
| Multiple Roles | Different user types | Separate mockups per role, document role-specific features |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Mockup before reading idea | May miss requirements | Always analyze idea first |
| Ignoring tools.json config | Inconsistent tool usage | Always check config |
| Using disabled tools | Violates config rules | Only use enabled tools |
| Too many mockups at once | Overwhelms review | Start with 1-3 key mockups |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-idea-mockup/references/examples.md) for detailed execution examples including:
- Mockup with frontend-design tool enabled
- Mockup without tools (manual mode)
- Missing idea folder (blocked scenario)
- No idea summary (blocked scenario)
