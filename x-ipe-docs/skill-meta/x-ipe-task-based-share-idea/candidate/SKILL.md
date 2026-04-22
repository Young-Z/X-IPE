---
name: x-ipe-task-based-share-idea
description: Convert refined idea summaries to shareable document formats (PPTX, DOCX, PDF). Use when user wants to share or present an idea. Uses MCP document conversion tools or pandoc. Triggers on requests like "share idea", "convert to ppt", "make presentation", "export idea".
---

# Task-Based Skill: Share Idea

## Purpose

Convert refined idea summaries to human-readable shareable formats by:
1. Loading sharing tool configuration and detecting available converters
2. Locating the source idea summary file
3. Confirming target format(s) with human
4. Restructuring content and generating formatted documents
5. Naming output as `formal-{source_name}.{extension}`

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` and `x-ipe+all+task-board-management` skills before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-assistant-user-representative-Engineer` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-share-idea"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null  # terminal skill
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  idea_folder: "x-ipe-docs/ideas/{folder}"
  toolbox_meta: "x-ipe-docs/config/tools.json"

  # Optional inputs
  extra_instructions: null
  # Source priority: 1) human input, 2) stages.ideation.sharing._extra_instruction in toolbox_meta, 3) null
  # When set, apply to content structure, format selection, document styling, and conversion.
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="idea_folder" source="previous task output | human input | auto-detect">
    <steps>
      1. IF previous task output has current_idea_folder → use it (map to idea_folder)
      2. ELIF human provides explicit folder path → use it
      3. ELSE → scan x-ipe-docs/ideas/ for most recent folder (by modification time)
      4. Confirm resolved folder with human before proceeding
    </steps>
  </field>
  <field name="toolbox_meta" source="default: x-ipe-docs/config/tools.json" />
  <field name="extra_instructions" source="human input | config | null">
    <steps>
      1. If human provides explicit extra instructions, use them
      2. Else if stages.ideation.sharing._extra_instruction exists in toolbox_meta config, use that
      3. Otherwise, set to null
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Refined idea summary exists</name>
    <verification>idea-summary-vN.md present in {idea_folder}</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Idea folder path provided</name>
    <verification>{idea_folder} is a valid directory</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Toolbox meta config exists</name>
    <verification>x-ipe-docs/config/tools.json exists and contains stages.ideation.sharing</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 (Study Broadly) | 1.1 | Load Config | Read toolbox meta sharing section; detect conversion tools and tool skills | Config loaded |
| | 1.2 | Identify Source | Locate latest `idea-summary-vN.md` in idea folder | Source found |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Confirm Format | Ask human for target format(s) from enabled options | Format(s) confirmed |
| 3. 慎思之 (Think Carefully) | — | SKIP | No trade-offs; conversion is mechanical once format confirmed | — |
| 4. 明辨之 (Discern Clearly) | — | SKIP | Format already confirmed in Phase 2; no alternatives to evaluate | — |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Prepare Content | Restructure content for each target format | Content ready |
| | 5.2 | Convert | Generate output files via tool skills, pandoc, MCP, or manual fallback | Files generated |
| | 5.3 | Verify & Complete | Confirm output files exist with size > 0; report to human | DoD validated |
| 继续执行 | 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: Step 2.1 requires confirmation of target format(s) (manual/stop_for_question: human confirms; auto: DAO confirms via x-ipe-assistant-user-representative-Engineer).
BLOCKING: Step 5.3 fails if any output file is empty or missing.

---

## Execution Procedure

```xml
<procedure name="share-idea">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Load Config and Detect Tools</name>
      <action>
        1. Check if x-ipe-docs/config/tools.json exists
        2. If exists: parse JSON, extract stages.ideation.sharing section,
           identify enabled formats (value = true)
        3. If missing or sharing section empty: default to all formats available
        4. Load extra_instructions:
           a. IF human provided explicit value: use it
           b. ELSE IF _extra_instruction field in sharing config: use config value
           c. ELSE: set to null
        5. Detect available conversion tools:
           - pandoc (which pandoc)
           - MCP document tools (check available MCP servers)
           - python-pptx / python-docx (pip show)
        6. Detect available format-specific tool skills:
           - IF DOCX enabled: check .github/skills/docx/SKILL.md exists → load as docx_tool_skill
           - IF PPTX enabled: check .github/skills/pptx/SKILL.md exists → load as pptx_tool_skill
        7. Log active formats, extra_instructions, available tools, and loaded tool skills
      </action>
      <constraints>
        - CRITICAL: Report available tools before proceeding
      </constraints>
      <output>Enabled formats list, available tools, loaded tool skills, extra_instructions</output>
      <reference>
        Supported formats and config key mapping:
        | Config Key                         | Extension | Best For           |
        |------------------------------------|----------|--------------------|
        | stages.ideation.sharing.pptx       | .pptx    | Presentations      |
        | stages.ideation.sharing.docx       | .docx    | Documents, reviews |
        | stages.ideation.sharing.pdf        | .pdf     | Read-only sharing  |
        | stages.ideation.sharing.html       | .html    | Web viewing        |
      </reference>
    </step_1_1>

    <step_1_2>
      <name>Identify Source File</name>
      <action>
        1. Navigate to {idea_folder}
        2. List available idea-summary-vN.md files
        3. Select the latest version OR human-specified version
        4. Read the source content
      </action>
      <output>Source file path and content</output>
    </step_1_2>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Confirm Target Formats</name>
      <action>
        1. Present enabled formats (filter by config):
           - PowerPoint (.pptx) - For presentations
           - Word (.docx) - For document review
           - PDF (.pdf) - For read-only sharing
           - HTML (.html) - For web viewing
        2. Allow multiple selections
        3. Wait for format confirmation

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Resolve via x-ipe-assistant-user-representative-Engineer (default: pptx if unresolvable)
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human to confirm format(s)
      </action>
      <constraints>
        - BLOCKING (manual/stop_for_question): Do not proceed until human confirms format(s)
        - BLOCKING (auto): Format confirmed by x-ipe-assistant-user-representative-Engineer (default: pptx if unresolvable)
      </constraints>
      <output>List of confirmed target formats</output>
    </step_2_1>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <skip reason="No trade-offs or risk assessment needed. Conversion is mechanical once the source file and target formats are confirmed." />
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <skip reason="Format already confirmed in Phase 2. No alternative approaches to evaluate — conversion tool selection is automatic based on availability." />
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Prepare Content Structure</name>
      <action>
        1. If extra_instructions set: apply them to content structuring
        2. For PPTX: restructure into slide-sized chunks
           - Title slide (idea name + subtitle)
           - Overview, Problem, Solution as bullet points
           - Key Features, Success Criteria, Next Steps
           - Max 5-7 bullets per slide; add speaker notes
           - IF pptx_tool_skill loaded: follow its content and design guidance
        3. For DOCX:
           - IF docx_tool_skill loaded: follow its Core Rules for document structure
             (use named styles over direct formatting, proper heading hierarchy,
              Word numbering definitions for lists, explicit page layout)
           - Structure content with Heading 1/2/3 hierarchy matching idea summary sections
           - Preserve tables, lists, and emphasis formatting
        4. For PDF: use markdown content directly, preserve headers, tables, formatting
        5. For HTML: use markdown content with web-friendly structure
      </action>
      <output>Format-specific content ready for conversion</output>
    </step_5_1>

    <step_5_2>
      <name>Execute Conversion</name>
      <action>
        1. For each requested format, select conversion method (priority order):
           a. Format-specific tool skill (highest priority):
              - DOCX: IF docx_tool_skill loaded → invoke `docx` skill for document generation
              - PPTX: IF pptx_tool_skill loaded → invoke `pptx` skill for presentation generation
           b. pandoc (IF available AND no tool skill for this format):
              pandoc -t {format} -o "formal-{source_name}.{ext}" "{source_file}"
           c. MCP document tools (IF available AND no higher-priority tool):
              Use mcp-documents/convert, mcp-office/create-presentation, or mcp-office/create-document
           d. Manual fallback (no tools available for this format):
              Inform human that automatic conversion is unavailable, provide structured content for manual copy-paste, suggest alternatives (Google Docs, CloudConvert). Mark format as partially complete.
        2. Generate each requested format sequentially
        3. Output naming: formal-{source_filename}.{extension}
           Example: idea-summary-v1.md -> formal-idea-summary-v1.docx
      </action>
      <output>Generated document files in {idea_folder}</output>
    </step_5_2>

    <step_5_3>
      <name>Verify and Complete</name>
      <action>
        1. Check each output file exists in {idea_folder}
        2. Verify file size > 0 for each
        3. List generated files with paths and sizes
        4. Present file list with paths and sizes

        Completion gate (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Auto-proceed after verification
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human to confirm receipt
      </action>
      <success_criteria>
        - All requested files exist and are non-empty
      </success_criteria>
      <output>Verified file list with paths</output>
    </step_5_3>

  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-assistant-user-representative-Engineer with:
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
  category: "standalone"
  status: completed | blocked
  task_based_skill: "x-ipe-task-based-share-idea"
  next_task_based_skill: null  # terminal skill
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  idea_folder: "x-ipe-docs/ideas/{folder}"
  source_file: "idea-summary-vN.md"
  shared_formats:
    - pptx
    - docx
  task_output_links:
    - "x-ipe-docs/ideas/{folder}/formal-idea-summary-vN.pptx"
    - "x-ipe-docs/ideas/{folder}/formal-idea-summary-vN.docx"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Source idea summary identified</name>
    <verification>Source file path logged and content read</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target formats confirmed with human</name>
    <verification>Human explicitly selected format(s)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Documents generated successfully</name>
    <verification>Each requested format file exists with size > 0</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output files named correctly</name>
    <verification>Files follow formal-{source_name}.{ext} convention</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Files saved in idea folder</name>
    <verification>Files exist in {idea_folder} directory</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Receipt confirmed (human or auto)</name>
    <verification>Generated files acknowledged (manual/stop_for_question: human confirms; auto: auto-acknowledged)</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Single Format Export

**When:** Human requests one specific format
**Then:**
```
1. Confirm the format
2. Generate single output file
3. Provide file path
```

### Pattern: Multi-Format Export

**When:** Human requests multiple formats
**Then:**
```
1. List all requested formats
2. Generate each format sequentially
3. Report success/failure for each
4. Provide summary of all created files
```

### Pattern: No Conversion Tools Available

**When:** Neither tool skills, pandoc, nor MCP tools are available for a format
**Then:**
```
1. Inform human: "Document conversion tools not available"
2. Provide structured content in clipboard-friendly format
3. Suggest alternatives (Google Docs, CloudConvert, manual copy)
4. Mark task as partially complete
```

### Pattern: Tool-Skill-Routed Conversion

**When:** A format-specific tool skill is available (e.g., `docx` for .docx, `pptx` for .pptx)
**Then:**
```
1. Load the tool skill from .github/skills/{skill-name}/SKILL.md
2. Follow the tool skill's rules and guidelines for document creation
3. Generate the output file following the tool skill's best practices
4. Verify output with the tool skill's quality checks (e.g., round-trip compatibility)
```

### Pattern: Presentation-Optimized Content

**When:** Human specifically wants a presentation
**Then:**
```
1. Restructure content into slide-sized chunks
2. Convert paragraphs to bullet points
3. Extract key phrases for slide titles
4. Limit content per slide (5-7 bullets max)
5. Add speaker notes with full context
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Converting without confirmation | May create unwanted formats | Always confirm format with human |
| Overwriting existing files | Loses previous versions | Use versioned naming |
| Ignoring conversion errors | Human doesn't know it failed | Report errors clearly |
| Skipping verification | May generate empty files | Always verify output size > 0 |
| Ignoring tool skill when available | Misses format-specific quality rules | Always prefer tool skill over generic pandoc |

---

## Examples

**Scenario 1:** User shares `idea-summary-v1.md` as PowerPoint (pptx tool skill available)

```
1. Load Config: tools.json pptx=true; pptx tool skill loaded
2. Source: x-ipe-docs/ideas/mobile-app-idea/idea-summary-v1.md
3. Human confirms: PowerPoint (.pptx)
4. Prepare: Restructure for slides following pptx skill guidance
5. Convert: Invoke pptx tool skill → formal-idea-summary-v1.pptx (245 KB)
6. Verify: File exists, size > 0, report to human
```

**Scenario 2:** User shares `idea-summary-v2.md` as Word document (docx tool skill available)

```
1. Load Config: tools.json docx=true; docx tool skill loaded
2. Source: x-ipe-docs/ideas/ai-assistant/idea-summary-v2.md
3. Human confirms: Word (.docx)
4. Prepare: Structure with heading hierarchy, named styles, Word numbering (per docx skill Core Rules)
5. Convert: Invoke docx tool skill → formal-idea-summary-v2.docx (128 KB)
6. Verify: File exists, size > 0, report to human
```
