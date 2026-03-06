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

BLOCKING: Learn `x-ipe-workflow-task-execution` and `x-ipe+all+task-board-management` skills before executing this skill. Learn `x-ipe-tool-frontend-design` skill if enabled in config.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

CRITICAL: Focus ONLY on UI/UX presentation -- ignore all tech stack mentions. See [references/mockup-guidelines.md](.github/skills/x-ipe-task-based-idea-mockup/references/mockup-guidelines.md) for detailed focus guidelines.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Idea Mockup"

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
  next_task_based_skill: "Requirement Gathering"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"

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
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="current_idea_folder" source="previous Ideation task output OR task board OR human input">
    <steps>
      1. IF previous task was "Ideation" → extract from task_output_links.current_idea_folder
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
  <checkpoint required="true">
    <name>Current Idea Folder Set</name>
    <verification>current_idea_folder is not N/A and folder exists on disk</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Idea Summary Exists</name>
    <verification>File {current_idea_folder}/idea-summary-vN.md exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tools Config Accessible</name>
    <verification>x-ipe-docs/config/tools.json is readable or manual mode accepted</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Mockup Tool Available</name>
    <verification>At least one mockup tool enabled in config OR human accepts manual mode</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 (Study Broadly) | 1.1 | Validate Folder | Verify Current Idea Folder exists | Folder validated |
| | 1.2 | Load Config | Read `x-ipe-docs/config/tools.json` mockup section | Config loaded |
| | 1.3 | Read Idea Summary | Load latest idea-summary-vN.md from folder | Summary loaded |
| | 1.4 | Research Design References | If needs lack detail, search online for design inspiration | References gathered |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Identify Mockup Needs | Extract UI/visual elements from idea | Needs identified |
| 3. 慎思之 (Think Carefully) | 3.1 | Load Brand Theme and Plan | Load theme, plan layout approach | Theme loaded |
| 4. 明辨之 (Discern Clearly) | — | SKIP | Single implementation approach; tool selection done in Phase 1 config | — |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Create Mockups | Invoke enabled mockup tools with creative, distinctive designs | Mockups created |
| | 5.2 | Save Artifacts | Store mockups in `{current_idea_folder}/mockups/` | Artifacts saved |
| | 5.3 | Update Summary | Add mockup links to idea summary | Summary updated |
| | 5.4 | Complete | Verify DoD, update workflow status | DoD verified |

BLOCKING: Step 1.1 halts if current_idea_folder is N/A -- ask human for folder path.
BLOCKING: Step 5.1 halts if no tools available AND human declines manual mode.


---

## Execution Procedure

```xml
<procedure name="idea-mockup">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Validate Current Idea Folder</name>
      <action>
        1. IF current_idea_folder == N/A:
           - List available folders under x-ipe-docs/ideas/
           - IF process_preference.auto_proceed == "auto":
              → CALL x-ipe-dao-end-user-representative with:
                  message_context:
                    source: "ai"
                    calling_skill: "idea-mockup"
                    task_id: "{task_id}"
                    feature_id: "N/A"
                    workflow_name: "N/A"
                    downstream_context: "Selecting which idea folder to generate mockups for"
                    messages:
                      - content: "Which idea folder for mockups? Options: {available folders}"
                        preferred_dispositions: ["answer", "clarification"]
                  human_shadow: false
              → IF disposition is "answer" or "approval" or "instruction": use returned decision
              → IF disposition is "clarification" or "reframe" or "critique": refine question and re-ask
              → IF disposition is "pass_through": escalate to human
           - ELSE (manual/stop_for_question):
             → Ask human: "Which idea folder should I create mockups for?"
             → Wait for selection
           - Set current_idea_folder = selected folder
        2. Validate folder exists on disk
        3. Verify idea-summary-vN.md exists in folder
        4. Log: "Working with idea folder: {current_idea_folder}"
      </action>
      <constraints>
        - BLOCKING: If folder does not exist, stop with error
        - BLOCKING: If no idea-summary-vN.md found, stop: "Run Ideation task first"
      </constraints>
      <output>validated current_idea_folder path</output>
    </step_1_1>

    <step_1_2>
      <name>Load Mockup Tool Configuration</name>
      <action>
        1. Check if x-ipe-docs/config/tools.json exists
        2. IF exists: Parse JSON, extract stages.ideation.mockup section
        3. IF not exists: Ask "Proceed with manual mockup description? (Y/N)"
        4. Load Extra Instructions (human input > config._extra_instruction > N/A)
        5. Log active configuration
      </action>
      <output>list of enabled mockup tools, extra_instructions value</output>
    </step_1_2>

    <step_1_3>
      <name>Read Idea Summary</name>
      <action>
        0. Resolve extra_context_reference inputs:
           - FOR EACH ref in [refined-idea, uiux-reference]:
             IF workflow mode AND extra_context_reference.{ref} is a file path:
               READ the file at that path
             ELIF extra_context_reference.{ref} is "auto-detect":
               Use existing discovery logic below
             ELIF extra_context_reference.{ref} is "N/A":
               Skip this context input
             ELSE (free-mode / absent):
               Use existing behavior
        1. Navigate to {current_idea_folder}/
        2. Find latest idea-summary-vN.md (highest version number)
        3. Parse summary content
        4. Extract: overview, key features, UI/UX mentions, user flow descriptions
      </action>
      <output>parsed idea summary with UI-relevant sections</output>
    </step_1_3>

    <step_1_4>
      <name>Research Design References</name>
      <action>
        1. Evaluate whether mockup needs provide enough detail to design a high-quality UI/UX
        2. IF needs are vague, generic, or lack visual specificity (e.g., "a dashboard", "a form" without layout/interaction details):
           a. Use the mockup needs as search queries to find real-world design references online
           b. Search for: "{mockup type} UI design", "{domain} dashboard examples", "{feature} UX patterns"
           c. Analyze found references for: layout patterns, component arrangements, interaction models, visual hierarchy
           d. Enrich the mockup needs with specific design details gleaned from references
           e. Document which references inspired which design decisions
        3. IF needs are already detailed and specific enough: skip to next step
      </action>
      <success_criteria>
        - Mockup needs now include concrete layout, component, and interaction details
        - Design references documented (if searched)
      </success_criteria>
      <output>enriched mockup needs with design reference insights (if applicable)</output>
    </step_1_4>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Identify Mockup Needs</name>
      <action>
        1. Analyze summary for screens/pages needed
        2. Identify interactive elements and workflows
        3. Determine primary user-facing components
        4. Prioritize mockups by importance
      </action>
      <success_criteria>
        - At least one mockup need identified
        - Needs prioritized (high/medium/low)
      </success_criteria>
      <output>prioritized list of mockups to create</output>
    </step_2_1>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">

    <step_3_1>
      <name>Load Brand Theme and Plan Layout</name>
      <action>
        1. Check x-ipe-docs/config/tools.json for `selected-theme` section
        2. IF `selected-theme` exists AND `theme-folder-path` is set:
           a. Read the design system file at {theme-folder-path}/design-system.md
           b. Extract: color palette, typography, spacing, component styles, semantic tokens
           c. These theme tokens MUST be applied when creating mockups in Phase 5
           d. Log: "Brand theme loaded: {theme-name}"
        3. IF `selected-theme` is not set or theme folder does not exist:
           a. Log: "No brand theme configured -- using tool defaults"
           b. Proceed without theme constraints
        4. Plan layout approach based on mockup needs and theme constraints
      </action>
      <output>brand theme tokens (colors, typography, spacing) or null, layout_plan</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <skip reason="Single implementation approach; mockup tool selection already determined in Phase 1 config loading. No alternative approaches to evaluate." />
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Create Mockups</name>
      <action>
        1. For each enabled tool, invoke with idea context (UI/UX content only)
        2. Generate mockup artifacts per identified needs (enriched with design references from step 1.4)
        3. IF brand theme loaded in step 3.1: apply theme colors, typography, and spacing to all mockups
        4. IF no tools enabled and manual mode accepted: create markdown description
      </action>
      <constraints>
        - CRITICAL: Focus on UI/UX only -- ignore all tech stack mentions from idea files
        - CRITICAL: Be creative and distinctive -- avoid generic, cookie-cutter layouts. Push for unique visual compositions, unexpected but intuitive interactions, and bold design choices that make the mockup memorable. Surprise the reviewer with thoughtful design details they did not ask for but will love.
        - BLOCKING: Halts if no tools available AND human declines manual mode
      </constraints>
      <output>generated mockup files/links</output>
    </step_5_1>

    <step_5_2>
      <name>Save Artifacts</name>
      <action>
        1. Create {current_idea_folder}/mockups/ directory if needed
        2. Save all mockup files with naming: {mockup-type}-v{version}.{ext}
        3. Record list of saved artifact paths
      </action>
      <output>list of saved artifact paths relative to current_idea_folder</output>
    </step_5_2>

    <step_5_3>
      <name>Update Idea Summary</name>
      <action>
        1. Open the existing {current_idea_folder}/idea-summary-vN.md (latest version)
        2. Add or update "Mockups and Prototypes" section with artifact links
        3. Do NOT create a new versioned file -- edit in-place
      </action>
      <constraints>
        - CRITICAL: Update the existing idea-summary file in-place -- do NOT create a new version
      </constraints>
      <output>updated idea summary path</output>
    </step_5_3>

    <step_5_4>
      <name>Complete</name>
      <action>
        1. IF execution_mode == "workflow-mode":
           a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
              - workflow_name: {from context}
              - action: {workflow.action}
              - status: "done"
              - deliverables: {"mockup-html": "{path to mockup HTML file}", "mockups-folder": "{path to mockups/ folder}"}
           b. Log: "Workflow action status updated to done"
        2. Verify all DoD checkpoints pass
        3. Present mockups summary to human
      </action>
      <output>workflow_action_updated</output>
    </step_5_4>

  </phase_5>

</procedure>
```

MANDATORY: See [references/mockup-guidelines.md](.github/skills/x-ipe-task-based-idea-mockup/references/mockup-guidelines.md) for tool mapping table, mockup type priorities, tool invocation formats, directory structure, naming conventions, and summary update template.

---

## Output Result

```yaml
task_completion_output:
  category: "ideation-stage"
  status: completed | blocked
  next_task_based_skill: "Requirement Gathering"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"     # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  task_output_links:
    - "{current_idea_folder}/mockups/{mockup-type}-v1.html"
    - "{current_idea_folder}/idea-summary-vN.md"
  # Dynamic attributes
  current_idea_folder: "{current_idea_folder}"
  mockup_tools_used:
    - "x-ipe-tool-frontend-design"
  mockup_list:
    - "{current_idea_folder}/mockups/dashboard-v1.html"
    - "{current_idea_folder}/mockups/user-form-v1.html"
  idea_summary_version: "vN"
```

MANDATORY: The `mockup_list` is passed through the chain: Idea Mockup -> Requirement Gathering -> Feature Breakdown -> Feature Refinement -> Technical Design.

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Folder Validated</name>
    <verification>current_idea_folder exists and contains idea-summary-vN.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Config Loaded</name>
    <verification>x-ipe-docs/config/tools.json loaded and mockup section parsed (or manual mode accepted)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary Analyzed</name>
    <verification>Idea summary read and UI-relevant elements extracted</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Needs Identified</name>
    <verification>Mockup needs identified and prioritized</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Design References Researched</name>
    <verification>If needs lacked detail, online design references were searched and insights incorporated; otherwise explicitly skipped with justification</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Brand Theme Applied</name>
    <verification>If selected-theme configured in tools.json, theme tokens read and applied to mockups; otherwise no theme configured</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Mockups Created</name>
    <verification>Mockups created using enabled tools or manual description</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Artifacts Saved</name>
    <verification>All mockups saved to {current_idea_folder}/mockups/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary Updated</name>
    <verification>Existing idea-summary-vN.md updated in-place with mockup links</verification>
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
