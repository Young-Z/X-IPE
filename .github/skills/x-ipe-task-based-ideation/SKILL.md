---
name: x-ipe-task-based-ideation
description: Learn and refine user ideas through brainstorming. Use when user uploads idea files to Workplace. Analyzes content, asks clarifying questions, produces structured idea summary with visualizations. Triggers on "ideate", "brainstorm", "refine idea", "analyze my idea".
---

# Task-Based Skill: Ideation

## Purpose

Learn and refine user ideas through collaborative brainstorming by:
1. Analyzing uploaded idea files from Workplace
2. Generating an initial understanding summary
3. Asking clarifying questions to brainstorm with user
4. Creating a structured idea summary with config-driven visualizations
5. Refining via sub-agent critique before final delivery

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

BLOCKING: Learn `infographic-syntax-creator` skill for visual infographics in the idea summary.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "Ideation"

  category: ideation-stage
  next_task_based_skill: "Idea Mockup | Idea to Architecture"
  require_human_review: yes

  auto_proceed: false
  idea_folder_path: "x-ipe-docs/ideas/{folder}"
  toolbox_meta_path: "x-ipe-docs/config/tools.json"
  extra_instructions: "{N/A | from config | from human}"
```

### Extra Instructions Loading

```yaml
loading_logic:
  - step: 1
    condition: "human provides explicit Extra Instructions"
    action: "Use human-provided value"
  - step: 2
    condition: "x-ipe-docs/config/tools.json exists"
    action: "Read stages.ideation.ideation._extra_instruction field"
  - step: 3
    condition: "field not found or empty"
    action: "Set Extra Instructions = N/A"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Idea Files Uploaded</name>
    <verification>Files exist in x-ipe-docs/ideas/{folder}/files/</verification>
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
| 1 | Load Toolbox | Read tools.json config | config loaded |
| 2 | Analyze Files | Read all files in idea folder | files analyzed |
| 3 | Initialize Tools | Set up enabled tools from config | tools ready |
| 4 | Generate Summary | Create understanding summary | summary shared |
| 5 | Brainstorm | Ask clarifying questions (3-5 batches) | idea refined |
| 6 | Research | Search for common principles | research complete |
| 7 | Generate Draft | Create idea draft using enabled tools | draft created |
| 8 | Critique | Sub-agent provides constructive feedback | feedback received |
| 9 | Improve Summary | Incorporate feedback, finalize | summary finalized |
| 10 | Rename Folder | Rename if "Draft Idea - xxx" | folder renamed |
| 11 | Complete | Request human review | human approves |

BLOCKING: Step 5 - Continue brainstorming until idea is well-defined.

BLOCKING: Step 11 - Human MUST approve idea summary before proceeding.

---

## Execution Procedure

```xml
<procedure name="ideation">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Load Ideation Toolbox Meta</name>
    <action>
      1. Check if x-ipe-docs/config/tools.json exists
      2. If exists: parse JSON, extract enabled tools from stages.ideation
      3. If NOT exists: create default config with all tools disabled
      4. Load Extra Instructions (human → config → N/A)
      5. Log active tool configuration
    </action>
    <output>tool_config, extra_instructions</output>
  </step_1>

  <step_2>
    <name>Analyze Idea Files</name>
    <action>
      1. Navigate to x-ipe-docs/ideas/{folder}/files/
      2. Read each file (text, markdown, code, images, etc.)
      3. Identify key themes, concepts, and goals
      4. Note gaps or ambiguities
    </action>
    <constraints>
      - BLOCKING: All files must be analyzed before proceeding
    </constraints>
    <output>initial_analysis</output>
  </step_2>

  <step_3>
    <name>Initialize Tools</name>
    <action>
      1. For each enabled tool in config, check availability:
         IF antv-infographic enabled: verify infographic-syntax-creator skill available
         IF mermaid enabled: verify mermaid capability available
         IF frontend-design enabled: verify frontend-design skill available
         IF x-ipe-tool-architecture-dsl enabled: verify skill available
      2. Log status (available/unavailable) for each tool
    </action>
    <output>tools_status</output>
  </step_3>

  <step_4>
    <name>Generate Understanding Summary</name>
    <action>
      1. Create summary: Core Concept, Key Goals, Identified Components
      2. List Questions and Ambiguities
      3. List enabled tools from config
      4. Share summary with user for validation
    </action>
    <output>understanding_summary</output>
  </step_4>

  <step_5>
    <name>Brainstorming Session</name>
    <action>
      1. Ask questions in batches (3-5 at a time)
      2. Wait for human response before proceeding
      3. Build on previous answers
      4. Challenge assumptions constructively
      5. Invoke enabled tools when user describes visuals/flows:
         IF user describes UI layout AND frontend-design enabled: invoke frontend-design skill, create mockup
         IF user describes flow AND mermaid enabled: generate mermaid diagram
         IF user describes architecture AND x-ipe-tool-architecture-dsl enabled: invoke skill
    </action>
    <constraints>
      - BLOCKING: Continue until idea is well-defined
      - CRITICAL: Batch questions (3-5), do not overwhelm
      - MANDATORY: Use enabled tools for visualization during brainstorming
    </constraints>
    <output>brainstorming_notes, artifacts[]</output>
  </step_5>

  <step_6>
    <name>Research Common Principles</name>
    <action>
      1. Identify if topic is common/established (auth, API, UI/UX, security, data)
      2. IF topic is common: research industry best practices, design patterns, document findings as "Common Principles", note authoritative sources
         ELSE: skip this step
    </action>
    <output>common_principles[], references[]</output>
  </step_6>

  <step_7>
    <name>Generate Idea Draft</name>
    <action>
      1. Synthesize outputs from steps 4, 5, 6
      2. Determine version number (auto-increment from existing files)
      3. Create draft using template from templates/idea-summary.md
      4. Apply enabled visualization tools per config:
         IF antv-infographic enabled: use infographic DSL for features/roadmaps
         IF mermaid enabled: use mermaid for flowcharts/sequences
         IF x-ipe-tool-architecture-dsl enabled: use architecture DSL for system diagrams
         IF all disabled: use standard markdown (bullet lists, tables)
      5. Link to artifacts created during brainstorming
    </action>
    <constraints>
      - CRITICAL: Use visualization tools based on config
      - MANDATORY: Include all sections from template
    </constraints>
    <output>idea_draft</output>
  </step_7>

  <step_8>
    <name>Critique and Feedback</name>
    <action>
      1. Invoke sub-agent (idea-critic) to review the idea draft
      2. Sub-agent evaluates: clarity, completeness, consistency, feasibility, visualization
      3. Sub-agent provides: strengths, improvements, questions
    </action>
    <constraints>
      - CRITICAL: Feedback must be constructive, not just critical
      - MANDATORY: Include specific improvement suggestions
    </constraints>
    <output>critique_feedback</output>
  </step_8>

  <step_9>
    <name>Improve and Deliver Summary</name>
    <action>
      1. Review critique feedback from step 8
      2. Address each improvement suggestion
      3. Resolve any questions raised
      4. Finalize idea-summary-vN.md
      5. Save to x-ipe-docs/ideas/{folder}/idea-summary-vN.md
    </action>
    <constraints>
      - MANDATORY: Create NEW versioned file, do not update existing
      - CRITICAL: All feedback items must be addressed
    </constraints>
    <output>idea_summary_path</output>
  </step_9>

  <step_10>
    <name>Rename Folder</name>
    <action>
      1. Check if folder matches "Draft Idea - MMDDYYYY HHMMSS"
      2. IF folder matches draft pattern AND idea has clear identity:
         a. Generate new name based on idea content (2-5 words, Title Case)
         b. Rename folder to "{Idea Name} - {timestamp}"
         c. Update internal links
         ELSE: skip rename
    </action>
    <output>folder_renamed, new_folder_name</output>
  </step_10>

  <step_11>
    <name>Complete and Request Review</name>
    <action>
      1. Present final idea summary to human
      2. Ask human to choose next task
      3. Wait for approval
    </action>
    <constraints>
      - BLOCKING: Human MUST approve before proceeding
    </constraints>
    <output>human_approval, next_task_choice</output>
  </step_11>

  <sub-agent-planning>
    <sub_agent_1>
      <sub_agent_definition>
        <role>idea-critic</role>
        <prompt>Review idea draft for clarity, completeness, consistency, feasibility, and visualization quality. Provide strengths, improvements, and questions.</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_8</workflow_step_reference>
    </sub_agent_1>
  </sub-agent-planning>

</procedure>
```

See [references/tool-usage-guide.md](references/tool-usage-guide.md) for tool mapping and invocation rules.

See [references/folder-naming-guide.md](references/folder-naming-guide.md) for rename logic.

---

## Output Result

```yaml
task_completion_output:
  category: ideation-stage
  status: completed | blocked
  next_task_based_skill: "Idea Mockup | Idea to Architecture"
  require_human_review: yes
  task_output_links:
    - "x-ipe-docs/ideas/{folder}/idea-summary-vN.md"
    - "x-ipe-docs/ideas/{folder}/mockups/mockup-vN.html"
  idea_id: "IDEA-XXX"
  idea_status: Refined
  idea_version: "vN"
  idea_folder: "{renamed folder name or original}"
  folder_renamed: true | false
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
    <verification>x-ipe-docs/config/tools.json loaded and parsed</verification>
    <step_output>tool_config, extra_instructions</step_output>
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
    <verification>Idea draft generated using enabled tools</verification>
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
    <verification>x-ipe-docs/ideas/{folder}/idea-summary-vN.md exists</verification>
    <step_output>idea_summary_path</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Human Approved</name>
    <verification>Human has reviewed and approved idea summary</verification>
    <step_output>human_approval, next_task_choice</step_output>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Tools Initialized</name>
    <verification>Enabled tools checked and status logged</verification>
    <step_output>tools_status</step_output>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Folder Renamed</name>
    <verification>Draft folder renamed if applicable</verification>
    <step_output>folder_renamed, new_folder_name</step_output>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Principles Researched</name>
    <verification>Common principles researched if topic is established</verification>
    <step_output>common_principles[], references[]</step_output>
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
| Ignoring tools.json | Misses capabilities | Always check config |
| Using tools when disabled | Unexpected behavior | Respect config settings |
| Skipping critique step | Lower quality output | Always run sub-agent critique |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples:
- Business plan ideation with tools enabled
- Ideation without tools (all disabled)
- Missing config file handling
- Draft folder rename scenario
- Brainstorming question batches
- Tool-enhanced brainstorming flow
- Draft → Critique → Improve flow
