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
  <field name="task_id" source="existing lifecycle task/readiness; no duplicate registration" />
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
  <checkpoint required="true"><name>Scope and owner</name><verification>Approved current task/readiness, idea identity and permitted artifact paths are known.</verification></checkpoint>
  <checkpoint required="true"><name>Source</name><verification>Selected idea sources resolve safely; broken explicit links or conflicting identities are not hidden.</verification></checkpoint>
  <checkpoint required="true"><name>Capabilities</name><verification>Applicable configuration and required capabilities are known; unavailable work is explicit.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Work | Evidence |
| --- | --- | --- |
| 1 | Resolve Source and Requested Format | Actual source, authorized format(s), selected available converters |
| 2 | Prepare and Convert | Actual requested documents or explicit conversion gaps |
| 3 | Verify and Return | Original terminal result with actual conversion evidence |

## Execution Procedure

```xml
<procedure name="share-idea">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Resolve Source and Requested Format</name>
    <action>
      1. Resolve idea_folder/source from explicit user input or previous output; highest numeric summary may be in refined-idea/ or legacy folder. Ambiguous identity requires selection, not newest-folder fallback.
      2. Read tools.json stages.ideation.sharing and _extra_instruction. Respect explicit disabled formats; an absent sharing section permits discovery of installed converters but does not prove availability or enable disabled tools.
      3. Reuse a format already named by the user; otherwise ask one bounded format question through existing mode policy. Load only the selected docx/pptx/pdf or other format skill now, not every installed converter. No silent default to PPTX if unresolved.
    </action>
    <output>Actual source, authorized format(s), selected available converters</output>
  </step_1>
  <step_2>
    <name>Prepare and Convert</name>
    <action>
      1. Restructure only as required by requested format: concise slides and notes for PPTX, named styles/heading/list/table preservation for DOCX, preserved content and links for PDF/HTML. Follow selected format skill in the same loop.
      2. Generate each requested formal-{source_filename}.{extension} in {idea_folder}, using selected format skill, then available authorized pandoc/MCP if appropriate. Do not send private content to third-party conversion services.
      3. Preserve actual source intent and artifacts; no new success criteria. If conversion is unavailable return the blocked/partial format and useful structured content, not a nonexistent generated file.
    </action>
    <output>Actual requested documents or explicit conversion gaps</output>
  </step_2>
  <step_3>
    <name>Verify and Return</name>
    <action>
      1. Verify every claimed document exists, is nonempty and opens/parses using its format capability; inspect content/layout relevant to the change. File size alone cannot prove a valid document.
      2. Return original shared_formats/source/task_output_links with actual artifacts only and blocked status for missing required formats. No mandatory review agent, redundant receipt confirmation, new board task or publishing merely because the skill is named Share Idea.
      3. Sharing conversion has no app action mapping; owner records the result once, handles the existing completion boundary and stops because next_task_based_skill is null.
    </action>
    <output>Original terminal result with actual conversion evidence</output>
  </step_3>
</procedure>
```

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

```xml
<definition_of_done>
  <checkpoint required="true"><name>Requested outcome</name><verification>Actual artifacts preserve source intent and meet the requested domain scope; unresolved required gaps remain blocked.</verification></checkpoint>
  <checkpoint required="true"><name>Verified evidence</name><verification>Applicable checks ran or current suitable evidence was reused; no fabricated pass, score or observed stakeholder benefit.</verification></checkpoint>
  <checkpoint required="true"><name>Original handoff</name><verification>Original output fields, real paths and conditional suggestions return to the same owner; no duplicate lifecycle or unauthorized app/Git work.</verification></checkpoint>
</definition_of_done>
```

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
