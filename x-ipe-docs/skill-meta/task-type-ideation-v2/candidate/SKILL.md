---
name: task-type-ideation-v2
description: Learn and refine user ideas through brainstorming. Use when user uploads idea files to Workplace. Analyzes content, asks clarifying questions, and produces structured idea summary. Triggers on "ideate", "brainstorm", "refine idea", "analyze my idea".
---

# Task Type: Ideation

## Purpose

Learn and refine user ideas through collaborative brainstorming by:
1. Analyzing uploaded idea files from Workplace
2. Generating an initial understanding summary
3. Asking clarifying questions to brainstorm with user
4. Creating a structured idea summary document with visual infographics
5. Preparing for Idea Mockup, Idea to Architecture, or Requirement Gathering

---

## Important Notes

BLOCKING: Learn `task-execution-guideline` skill before executing this skill.

BLOCKING: Learn `infographic-syntax-creator` skill for visual infographics in the idea summary.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_type: "Ideation"
  
  category: ideation-stage
  next_task_type: "Idea Mockup | Idea to Architecture"
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
| 1 | Load Toolbox | Read tools.json config | config loaded |
| 2 | Analyze Files | Read all files in idea folder | files analyzed |
| 3 | Initialize Tools | Set up enabled tools from config | tools ready |
| 4 | Generate Summary | Create understanding summary | summary shared |
| 5 | Brainstorm | Ask clarifying questions (3-5 at a time) | idea refined |
| 6 | Research | Search for common principles | research complete |
| 7 | Generate Draft | Create idea draft using enabled tools | draft created |
| 8 | Critique | Sub-agent provides constructive feedback | feedback received |
| 9 | Improve Summary | Incorporate feedback, deliver final | summary finalized |
| 10 | Rename Folder | Rename if "Draft Idea - xxx" | folder renamed |
| 11 | Complete | Request human review | human approves |

BLOCKING: Step 5 - Continue brainstorming until idea is well-defined.

BLOCKING: Step 11 - Human MUST approve idea summary before proceeding.

---

## Execution Procedure

```xml
<procedure name="ideation-v2">

  <step_1>
    <name>Load Ideation Toolbox Meta</name>
    <action>
      1. Check if x-ipe-docs/config/tools.json exists
      2. If exists: parse JSON, extract enabled tools from stages.ideation
      3. If NOT exists: create default config with all tools disabled
      4. Load Extra Instructions (human → config → N/A)
      5. Log active tool configuration
    </action>
    <branch>
      IF: file exists
      THEN: Parse and extract enabled tools
      ELSE: Create default config, inform user
    </branch>
    <output>tool_config, extra_instructions</output>
  </step_1>

  <step_2>
    <name>Analyze Idea Files</name>
    <action>
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
    <name>Initialize Tools</name>
    <action>
      1. For each enabled tool in config
      2. Check tool availability
      3. Log status (available/unavailable)
    </action>
    <branch>
      IF: config.stages.ideation.ideation["antv-infographic"] == true
      THEN: Verify infographic-syntax-creator skill available
      
      IF: config.stages.ideation.ideation["mermaid"] == true
      THEN: Verify mermaid capability available
      
      IF: config.stages.ideation.mockup["frontend-design"] == true
      THEN: Verify frontend-design skill available
    </branch>
    <output>tools_status</output>
  </step_3>

  <step_4>
    <name>Generate Understanding Summary</name>
    <action>
      1. Create summary of what you understand
      2. Include: Core Concept, Key Goals, Identified Components
      3. List Questions and Ambiguities
      4. List enabled tools from config
      5. Share summary with user for validation
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
      5. Invoke enabled tools when user describes visuals/flows
    </action>
    <constraints>
      - BLOCKING: Continue until idea is well-defined
      - CRITICAL: Batch questions (3-5), do not overwhelm
      - MANDATORY: Use enabled tools for visualization
    </constraints>
    <branch>
      IF: user describes UI layout AND frontend-design enabled
      THEN: Invoke frontend-design skill, create mockup
      
      IF: user describes flow AND mermaid enabled
      THEN: Generate mermaid diagram
      
      IF: user describes architecture AND tool-architecture-dsl enabled
      THEN: Invoke tool-architecture-dsl skill
    </branch>
    <output>brainstorming_notes, artifacts[]</output>
  </step_5>

  <step_6>
    <name>Research Common Principles</name>
    <action>
      1. Identify if topic is common/established
      2. Research: industry best practices, design patterns
      3. Document findings as "Common Principles"
      4. Note authoritative sources for references
    </action>
    <branch>
      IF: topic is common (auth, API, UI/UX, security)
      THEN: Research and document principles
      ELSE: Skip this step
    </branch>
    <output>common_principles[], references[]</output>
  </step_6>

  <step_7>
    <name>Generate Idea Draft</name>
    <action>
      1. Synthesize outputs from steps 4, 5, 6 (summary, brainstorming, research)
      2. Determine version number (auto-increment)
      3. Create draft using template from templates/idea-summary.md
      4. Apply enabled visualization tools
      5. Link to artifacts created during brainstorming
    </action>
    <constraints>
      - CRITICAL: Use visualization tools based on config
      - MANDATORY: Include all sections from template
    </constraints>
    <branch>
      IF: antv-infographic enabled
      THEN: Use infographic DSL for features/roadmaps
      
      IF: mermaid enabled
      THEN: Use mermaid for flowcharts/sequences
      
      IF: tool-architecture-dsl enabled
      THEN: Use architecture DSL for system diagrams
      
      IF: all disabled
      THEN: Use standard markdown (bullet lists, tables)
    </branch>
    <output>idea_draft</output>
  </step_7>

  <step_8>
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
        - Visualization: Are tools used effectively?
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
      2. Generate new name based on idea content
      3. Rename folder
      4. Update internal links
    </action>
    <branch>
      IF: folder matches draft pattern AND idea has clear identity
      THEN: Rename to "{Idea Name} - {timestamp}"
      ELSE: Skip rename
    </branch>
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

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: ideation-stage
  status: completed | blocked
  next_task_type: "Idea Mockup | Idea to Architecture"
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

MANDATORY: After completing this skill, return to `task-execution-guideline` to continue the task execution flow.

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

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples:
- Business plan ideation with tools enabled
- Ideation without tools (all disabled)
- Missing config file handling
- Draft folder rename scenario
