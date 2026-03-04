---
name: x-ipe-task-based-ideation-v2
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

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

CRITICAL: Only use tools that are explicitly enabled (`true`) in `x-ipe-docs/config/tools.json` under `stages.ideation`. Only `true` counts as enabled -- `false`, absent, or any other value means DISABLED. The tools.json config is the single source of truth for which tools are allowed.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

---

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "Ideation"
  
  category: ideation-stage
  next_task_based_skill: "Idea Mockup | Idea to Architecture"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  
  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    action: "refine_idea"  # hardcoded — this skill ALWAYS updates the refine_idea action
    extra_context_reference:  # optional, default: N/A for all refs
      raw-idea: "path | N/A | auto-detect"
      uiux-reference: "path | N/A | auto-detect"
  idea_folder_path: "x-ipe-docs/ideas/{folder}"
  toolbox_meta_path: "x-ipe-docs/config/tools.json"
  extra_instructions: "{N/A | from config | from human}"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />

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
  <checkpoint required="true">
    <name>Idea Files Uploaded</name>
    <verification>Files exist in x-ipe-docs/ideas/{folder}/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human Available</name>
    <verification>Human available for brainstorming session</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Idea Folder Path Provided</name>
    <verification>Path to idea folder specified</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Load Toolbox | Read tools.json config, output enabled tool list | config loaded |
| 2 | Analyze Files | Read all files in idea folder | files analyzed |
| 3 | Generate Summary | Create understanding summary | summary shared |
| 4 | Brainstorm | Ask clarifying questions (3-5 at a time) | idea refined |
| 5 | Research | Search for common principles | research complete |
| 6 | Generate Draft | Create idea draft, prefer enabled tools from step 1 | draft created |
| 7 | Critique | Sub-agent provides constructive feedback | feedback received |
| 8 | Improve Summary | Incorporate feedback, prefer enabled tools from step 1 | summary finalized |
| 9 | Complete | Request human review | human approves |

BLOCKING: Step 4 - Continue brainstorming until idea is well-defined.

BLOCKING: Step 10 - Human MUST approve idea summary before proceeding.

---

## Execution Procedure

```xml
<procedure name="ideation-v2">

  <step_1>
    <name>Load Ideation Toolbox Meta</name>
    <action>
      1. Check if x-ipe-docs/config/tools.json exists
      2. If exists: parse JSON, extract tools from stages.ideation
      3. If NOT exists: create default config with all tools disabled
      4. Resolve extra_instructions (see Input Initialization)
      5. Build and output the enabled tool list -- only tools with value `true` count as enabled; `false`, absent, or any other value means DISABLED
      6. BLOCKING: For each enabled tool that has a corresponding skill at .github/skills/{tool-name}/SKILL.md, LOAD that skill now. This ensures correct syntax and grammar are available before any content generation.
      7. Output format:
         ```
         Enabled tools: [list of enabled tool names]
         Disabled tools: [list of disabled tool names]
         Loaded tool skills: [list of skills loaded in step 6]
         ```
    </action>
    <output>tool_config, enabled_tool_list, extra_instructions</output>
  </step_1>

  <step_2>
    <name>Analyze Idea Files</name>
    <action>
      0. Resolve extra_context_reference inputs:
         - FOR EACH ref in [raw-idea, uiux-reference]:
           IF workflow mode AND extra_context_reference.{ref} is a file path:
             READ the file at that path
           ELIF extra_context_reference.{ref} is "auto-detect":
             Use existing discovery logic below
           ELIF extra_context_reference.{ref} is "N/A":
             Skip this context input
           ELSE (free-mode / absent):
             Use existing behavior
      1. Navigate to x-ipe-docs/ideas/{folder}/files/
      2. Read each file (text, markdown, code, etc.)
      3. Identify key themes, concepts, and goals
      4. Note any gaps or ambiguities
    </action>
    <constraints>
      - BLOCKING: All files must be analyzed before proceeding
    </constraints>
    <output>initial_analysis</output>
  </step_2>

  <step_3>
    <name>Generate Understanding Summary</name>
    <action>
      1. Create summary of what you understand
      2. Include: Core Concept, Key Goals, Identified Components
      3. List Questions and Ambiguities
      4. List enabled tools from step 1
      5. Share summary with user for validation
    </action>
    <output>understanding_summary</output>
  </step_3>

  <step_4>
    <name>Brainstorming Session</name>
    <action>
      1. Ask questions in batches (3-5 at a time)
      2. Wait for human response before proceeding
      3. Build on previous answers
      4. Challenge assumptions constructively
      5. IF extra_instructions is provided and non-empty:
         - Incorporate extra_instructions as additional context/guidance for the refinement
         - Treat as user preference that supplements (not replaces) the idea content
      6. When the user describes something visual (UI layouts, flows, system structure), proactively generate visual artifacts to enrich the brainstorming -- select the most appropriate enabled tool from step 1's tool list for the content type
    </action>
    <constraints>
      - BLOCKING: Continue until idea is well-defined
      - CRITICAL: Batch questions (3-5), do not overwhelm
      - MANDATORY: Only use tools that appear in the enabled tool list from step 1
    </constraints>
    <output>brainstorming_notes, artifacts[]</output>
  </step_4>

  <step_5>
    <name>Research Common Principles</name>
    <action>
      1. Identify if topic is common/established (auth, API, UI/UX, security)
      2. IF topic is common: research industry best practices, design patterns, document findings as "Common Principles", note authoritative sources
         ELSE: skip this step
    </action>
    <output>common_principles[], references[]</output>
  </step_5>

  <step_6>
    <name>Generate Idea Draft</name>
    <action>
      1. Synthesize outputs from steps 3, 4, 5 (summary, brainstorming, research)
      2. Determine version number (auto-increment)
      3. Output path: {idea_folder}/refined-idea/idea-summary-vN.md
         a. Create {idea_folder}/refined-idea/ folder if it does not exist
         b. IF folder already exists and contains previous output: clear it (overwrite mode)
         c. Write all refined output files to {idea_folder}/refined-idea/
      4. Create draft using template from templates/idea-summary.md
      5. RECOMMENDED: Use enabled tools from step 1's tool list to create rich visual content (diagrams, infographics, architecture views) -- select the most appropriate tool for each content type
      6. If no tools are enabled: use standard markdown (bullet lists, tables)
      7. Link to artifacts created during brainstorming
    </action>
    <constraints>
      - CRITICAL: Only use tools that appear in the enabled tool list from step 1 -- if a tool is not in the enabled list, do NOT use it
      - MANDATORY: Include all sections from template
      - MANDATORY: All internal markdown links MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). Do NOT use relative paths like `../` or `./`.
      - RECOMMENDED: Prefer enabled tools over plain markdown for richer idea presentation
    </constraints>
    <output>idea_draft</output>
  </step_6>

  <step_7>
    <name>Critique and Feedback</name>
    <action>
      1. Invoke sub-agent to review the idea draft
      2. Sub-agent evaluates against quality criteria
      3. Sub-agent provides constructive feedback
    </action>
    <sub_agent>
      role: idea-critic
      goal: Provide constructive feedback on idea draft
      model_hint: sonnet
      evaluation_criteria:
        - Clarity: Is the problem statement clear?
        - Completeness: Are all key sections filled?
        - Consistency: Do sections align with each other?
        - Feasibility: Are goals realistic?
        - Visualization: Are enabled tools used effectively?
      feedback_format:
        - Strengths: What works well
        - Improvements: Specific actionable suggestions
        - Questions: Clarifications needed
    </sub_agent>
    <constraints>
      - CRITICAL: Feedback must be constructive, not just critical
      - MANDATORY: Include specific improvement suggestions
    </constraints>
    <output>critique_feedback</output>
  </step_7>

  <step_8>
    <name>Improve and Deliver Summary</name>
    <action>
      1. Review critique feedback from step 7
      2. Address each improvement suggestion
      3. Resolve any questions raised
      4. RECOMMENDED: Use enabled tools from step 1's tool list to enhance or add visual content where feedback suggests improvements -- select the most appropriate tool for each content type
      5. IF feedback requires minor-to-moderate changes:
         → Update the existing draft in-place
         IF feedback requires extensive rewrite (majority of sections affected):
         → Rewrite the file from scratch (same path)
      6. Finalize at {idea_folder}/refined-idea/idea-summary-vN.md
    </action>
    <constraints>
      - MANDATORY: Update the existing draft file in-place — do NOT create a new versioned file for critique improvements
      - CRITICAL: All feedback items must be addressed
      - CRITICAL: Only use tools that appear in the enabled tool list from step 1
    </constraints>
    <output>idea_summary_path</output>
  </step_8>

  <step_9>
    <name>Complete and Request Review</name>
    <action>
      1. IF execution_mode == "workflow-mode":
         a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
            - workflow_name: {from context}
            - action: "refine_idea"  ← HARDCODED: always use "refine_idea", NEVER "compose_idea" or any other action
            - status: "done"
            - deliverables: {"refined-idea": "{path to idea-summary file}", "refined-ideas-folder": "{path to refined-idea/ folder}"}
         b. Log: "Workflow action status updated to done"
      2. Present final idea summary to human
      3. Ask human to choose next task
      4. Wait for approval
    </action>
    <constraints>
      - BLOCKING: Human MUST approve before proceeding
    </constraints>
    <output>human_approval, next_task_choice, workflow_action_updated</output>
  </step_9>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: ideation-stage
  status: completed | blocked
  next_task_based_skill: "Idea Mockup | Idea to Architecture"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  task_output_links:
    - "x-ipe-docs/ideas/{folder}/refined-idea/idea-summary-vN.md"
    - "x-ipe-docs/ideas/{folder}/refined-idea/"
  # Dynamic attributes
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"   # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  idea_id: "IDEA-XXX"
  idea_status: Refined
  idea_version: "vN"
  idea_folder: "{original folder name}"
```

### Next Task Selection

After ideation completes, ask human to choose:

```yaml
next_task_options:
  - option: "Idea Mockup"
    best_for: "Ideas with strong UI focus"
  - option: "Idea to Architecture"
    best_for: "Ideas requiring system design, integrations"
  - option: "Skip to Requirement Gathering"
    best_for: "Simple ideas or when mockups/architecture not needed"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

CRITICAL: Every step output in Execution Procedure MUST have a corresponding DoD checkpoint.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Config Loaded</name>
    <verification>x-ipe-docs/config/tools.json loaded, enabled tool list output</verification>
    <step_output>tool_config, enabled_tool_list, extra_instructions</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Files Analyzed</name>
    <verification>All files in idea folder analyzed</verification>
    <step_output>initial_analysis</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Understanding Summary Shared</name>
    <verification>Initial understanding summary shared with user</verification>
    <step_output>understanding_summary</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Brainstorming Complete</name>
    <verification>Idea is well-defined with clear goals</verification>
    <step_output>brainstorming_notes, artifacts[]</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Draft Created</name>
    <verification>Idea draft generated, enabled tools from step 1 used where appropriate</verification>
    <step_output>idea_draft</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Critique Received</name>
    <verification>Sub-agent provided constructive feedback</verification>
    <step_output>critique_feedback</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Feedback Addressed</name>
    <verification>All critique items addressed in final summary</verification>
    <step_output>N/A (validation step)</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary Created</name>
    <verification>x-ipe-docs/ideas/{folder}/refined-idea/idea-summary-vN.md exists</verification>
    <step_output>idea_summary_path</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Human Approved</name>
    <verification>Human has reviewed and approved idea summary</verification>
    <step_output>human_approval, next_task_choice</step_output>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Principles Researched</name>
    <verification>Common principles researched if topic is established</verification>
    <step_output>common_principles[], references[]</step_output>
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

### Pattern: Raw Notes Upload

**When:** User uploads unstructured notes or braindump
**Then:**
```
1. Extract key themes from notes
2. Organize into logical categories
3. Ask clarifying questions about each category
4. Help structure into coherent idea
```

### Pattern: Technical Specification Upload

**When:** User uploads detailed technical spec
**Then:**
```
1. Validate technical feasibility
2. Ask about business goals (why this spec?)
3. Identify missing user context
4. Connect technical details to user value
```

### Pattern: Multiple Conflicting Ideas

**When:** Uploaded files contain conflicting approaches
**Then:**
```
1. Surface the conflicts clearly
2. Ask user to prioritize or choose
3. Help evaluate trade-offs
4. Document decision rationale
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Summarizing without questions | Misses refinement | Engage in brainstorming |
| Too many questions at once | Overwhelms user | Batch 3-5 questions |
| Accepting at face value | May miss issues | Challenge constructively |
| Skipping to requirements | Idea not refined | Complete ideation first |
| Ignoring tools.json | Uses wrong tools | Always check enabled tool list from step 1 |
| Using disabled tools | Violates config | Only use tools in the enabled list |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-ideation-v2/references/examples.md) for concrete execution examples:
- Business plan ideation with tools enabled
- Ideation without tools (all disabled)
- Missing config file handling
