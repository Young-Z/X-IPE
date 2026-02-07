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

CRITICAL: Focus ONLY on UI/UX presentation -- ignore all tech stack mentions. See [references/mockup-guidelines.md](references/mockup-guidelines.md) for detailed focus guidelines.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Idea Mockup"

  # Task type attributes
  category: "ideation-stage"
  next_task_based_skill: "Requirement Gathering"
  require_human_review: "yes"

  # Required inputs
  auto_proceed: false
  ideation_toolbox_meta: "{project_root}/x-ipe-docs/config/tools.json"
  current_idea_folder: "N/A"  # REQUIRED from context - path to current idea folder
  extra_instructions: "N/A"   # Additional context for mockup creation

  # Context (from previous task or project)
  # current_idea_folder sourced from: previous Ideation output, task board, or human input
  # extra_instructions sourced from: human input > config._extra_instruction > N/A
```

MANDATORY: See [references/mockup-guidelines.md](references/mockup-guidelines.md) for Extra Instructions loading logic, Current Idea Folder validation, and tool configuration details.

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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Validate Folder | Verify Current Idea Folder exists | Folder validated |
| 2 | Load Config | Read `x-ipe-docs/config/tools.json` mockup section | Config loaded |
| 3 | Read Idea Summary | Load latest idea-summary-vN.md from folder | Summary loaded |
| 4 | Identify Mockup Needs | Extract UI/visual elements from idea | Needs identified |
| 5 | Create Mockups | Invoke enabled mockup tools | Mockups created |
| 6 | Save Artifacts | Store mockups in `{current_idea_folder}/mockups/` | Artifacts saved |
| 7 | Update Summary | Add mockup links to idea summary | Summary updated |
| 8 | Complete | Verify DoD, request human review | Human approves |

BLOCKING: Step 1 halts if current_idea_folder is N/A -- ask human for folder path.
BLOCKING: Step 5 halts if no tools available AND human declines manual mode.
BLOCKING: Step 8 requires human approval before proceeding.

---

## Execution Procedure

```xml
<procedure name="idea-mockup">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Validate Current Idea Folder</name>
    <action>
      1. IF current_idea_folder == N/A:
         - List available folders under x-ipe-docs/ideas/
         - Ask human: "Which idea folder should I create mockups for?"
         - Wait for selection, set current_idea_folder = selected folder
      2. Validate folder exists on disk
      3. Verify idea-summary-vN.md exists in folder
      4. Log: "Working with idea folder: {current_idea_folder}"
    </action>
    <constraints>
      - BLOCKING: If folder does not exist, stop with error
      - BLOCKING: If no idea-summary-vN.md found, stop: "Run Ideation task first"
    </constraints>
    <output>validated current_idea_folder path</output>
  </step_1>

  <step_2>
    <name>Load Mockup Tool Configuration</name>
    <action>
      1. Check if x-ipe-docs/config/tools.json exists
      2. IF exists: Parse JSON, extract stages.ideation.mockup section
      3. IF not exists: Ask "Proceed with manual mockup description? (Y/N)"
      4. Load Extra Instructions (human input > config._extra_instruction > N/A)
      5. Log active configuration
    </action>
    <branch>
      IF: config file exists
      THEN: extract enabled tools from stages.ideation.mockup
      ELSE: propose manual mode to human
    </branch>
    <output>list of enabled mockup tools, extra_instructions value</output>
  </step_2>

  <step_3>
    <name>Read Idea Summary</name>
    <action>
      1. Navigate to {current_idea_folder}/
      2. Find latest idea-summary-vN.md (highest version number)
      3. Parse summary content
      4. Extract: overview, key features, UI/UX mentions, user flow descriptions
    </action>
    <output>parsed idea summary with UI-relevant sections</output>
  </step_3>

  <step_4>
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
  </step_4>

  <step_5>
    <name>Create Mockups</name>
    <action>
      1. For each enabled tool, invoke with idea context (UI/UX content only)
      2. Generate mockup artifacts per identified needs
      3. IF no tools enabled and manual mode accepted: create markdown description
    </action>
    <constraints>
      - CRITICAL: Focus on UI/UX only -- ignore all tech stack mentions from idea files
      - BLOCKING: Halts if no tools available AND human declines manual mode
    </constraints>
    <output>generated mockup files/links</output>
  </step_5>

  <step_6>
    <name>Save Artifacts</name>
    <action>
      1. Create {current_idea_folder}/mockups/ directory if needed
      2. Save all mockup files with naming: {mockup-type}-v{version}.{ext}
      3. Record list of saved artifact paths
    </action>
    <output>list of saved artifact paths relative to current_idea_folder</output>
  </step_6>

  <step_7>
    <name>Update Idea Summary</name>
    <action>
      1. Create new version: {current_idea_folder}/idea-summary-v{N+1}.md
      2. Include all content from previous version
      3. Add "Mockups and Prototypes" section with artifact links
    </action>
    <constraints>
      - CRITICAL: Do NOT modify existing idea-summary files -- create new version only
    </constraints>
    <output>updated idea summary version path</output>
  </step_7>

  <step_8>
    <name>Complete</name>
    <action>
      1. Verify all DoD checkpoints pass
      2. Present mockups to human for review
      3. Wait for human approval
    </action>
    <constraints>
      - BLOCKING: Human MUST approve mockups before proceeding
    </constraints>
    <output>human approval status</output>
  </step_8>

</procedure>
```

MANDATORY: See [references/mockup-guidelines.md](references/mockup-guidelines.md) for tool mapping table, mockup type priorities, tool invocation formats, directory structure, naming conventions, and summary update template.

---

## Output Result

```yaml
task_completion_output:
  category: "ideation-stage"
  status: completed | blocked
  next_task_based_skill: "Requirement Gathering"
  require_human_review: "yes"
  task_output_links:
    - "{current_idea_folder}/mockups/{mockup-type}-v1.html"
    - "{current_idea_folder}/idea-summary-v{N+1}.md"
  # Dynamic attributes
  current_idea_folder: "{current_idea_folder}"
  mockup_tools_used:
    - "x-ipe-tool-frontend-design"
  mockup_list:
    - "{current_idea_folder}/mockups/dashboard-v1.html"
    - "{current_idea_folder}/mockups/user-form-v1.html"
  idea_summary_version: "v{N+1}"
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
    <name>Mockups Created</name>
    <verification>Mockups created using enabled tools or manual description</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Artifacts Saved</name>
    <verification>All mockups saved to {current_idea_folder}/mockups/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary Updated</name>
    <verification>New idea-summary-v{N+1}.md created with mockup links</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human Approved</name>
    <verification>Human has reviewed and approved mockups</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Dashboard-Heavy Idea

**When:** Idea focuses on data visualization and dashboards
**Then:**
```
1. Prioritize dashboard mockup
2. Include chart placeholders and filter/control areas
3. Consider responsive layout
4. Use x-ipe-tool-frontend-design skill with dashboard template
```

### Pattern: Form-Heavy Idea

**When:** Idea involves data input or user registration
**Then:**
```
1. Prioritize form mockups with validation states
2. Show error/success messages
3. Consider multi-step flows and mobile view
```

### Pattern: No UI Description

**When:** Idea summary lacks UI details
**Then:**
```
1. Ask clarifying questions about UI needs
2. Suggest common patterns based on idea type
3. Create minimal viable mockup, request feedback before expanding
```

### Pattern: Multiple User Roles

**When:** Idea mentions different user types
**Then:**
```
1. Create separate mockups per role (e.g., admin-dashboard-v1.html)
2. Document role-specific features and permission variations
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Creating mockup before reading idea | May miss requirements | Always analyze idea first |
| Ignoring tools.json config | Inconsistent tool usage | Always check config |
| Overwriting existing mockups | Loses previous versions | Use version numbering |
| Skipping human review | May create wrong visuals | Always get approval |
| Using disabled tools | Violates config rules | Only use enabled tools |
| Creating too many mockups at once | Overwhelms review | Start with 1-3 key mockups |
| Including tech stack in mockups | Mockups are for UI/UX only | Focus on visual presentation |
| Labeling with framework names | Confuses design with implementation | Use descriptive UI labels |

---

## Examples

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Mockup with frontend-design tool enabled
- Mockup without tools (manual mode)
- Missing idea folder (blocked scenario)
- No idea summary (blocked scenario)
