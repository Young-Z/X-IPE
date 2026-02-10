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

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Share Idea"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  require_human_review: true

  # Required inputs
  auto_proceed: false
  idea_folder: "x-ipe-docs/ideas/{folder}"
  toolbox_meta: "x-ipe-docs/config/tools.json"

  # Optional inputs
  extra_instructions: null
  # Source priority: 1) human input, 2) stages.ideation.sharing._extra_instruction in toolbox_meta, 3) null
  # When set, apply to content structure, format selection, document styling, and conversion.
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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Load Config | Read toolbox meta sharing section; detect conversion tools | Config loaded |
| 2 | Identify Source | Locate latest `idea-summary-vN.md` in idea folder | Source found |
| 3 | Confirm Format | Ask human for target format(s) from enabled options | Format(s) confirmed |
| 4 | Prepare Content | Restructure content for each target format | Content ready |
| 5 | Convert | Generate output files via pandoc, MCP, or manual fallback | Files generated |
| 6 | Verify & Complete | Confirm output files exist with size > 0; report to human | DoD validated |

BLOCKING: Step 3 requires human confirmation of target format(s).
BLOCKING: Step 6 fails if any output file is empty or missing.

---

## Execution Procedure

```xml
<procedure name="share-idea">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
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
      6. Log active formats, extra_instructions, and available tools
    </action>
    <constraints>
      - CRITICAL: Report available tools before proceeding
    </constraints>
    <output>Enabled formats list, available tools, extra_instructions</output>
    <reference>
      Supported formats and config key mapping:
      | Config Key                         | Extension | Best For           |
      |------------------------------------|----------|--------------------|
      | stages.ideation.sharing.pptx       | .pptx    | Presentations      |
      | stages.ideation.sharing.docx       | .docx    | Documents, reviews |
      | stages.ideation.sharing.pdf        | .pdf     | Read-only sharing  |
      | stages.ideation.sharing.html       | .html    | Web viewing        |
    </reference>
  </step_1>

  <step_2>
    <name>Identify Source File</name>
    <action>
      1. Navigate to {idea_folder}
      2. List available idea-summary-vN.md files
      3. Select the latest version OR human-specified version
      4. Read the source content
    </action>
    <output>Source file path and content</output>
  </step_2>

  <step_3>
    <name>Confirm Target Formats</name>
    <action>
      1. Present enabled formats to human (filter by config):
         - PowerPoint (.pptx) - For presentations
         - Word (.docx) - For document review
         - PDF (.pdf) - For read-only sharing
         - HTML (.html) - For web viewing
      2. Allow multiple selections
      3. Wait for human confirmation
    </action>
    <constraints>
      - BLOCKING: Do not proceed until human confirms format(s)
    </constraints>
    <output>List of confirmed target formats</output>
  </step_3>

  <step_4>
    <name>Prepare Content Structure</name>
    <action>
      1. If extra_instructions set: apply them to content structuring
      2. For PPTX: restructure into slide-sized chunks
         - Title slide (idea name + subtitle)
         - Overview, Problem, Solution as bullet points
         - Key Features, Success Criteria, Next Steps
         - Max 5-7 bullets per slide; add speaker notes
      3. For DOCX/PDF: use markdown content directly,
         preserve headers, tables, and formatting
      4. For HTML: use markdown content with web-friendly structure
    </action>
    <output>Format-specific content ready for conversion</output>
  </step_4>

  <step_5>
    <name>Execute Conversion</name>
    <action>
      1. Select conversion method based on detected tools:
         IF pandoc available:
           pandoc -t {format} -o "formal-{source_name}.{ext}" "{source_file}"
         ELSE IF MCP document tools available:
           Use mcp-documents/convert, mcp-office/create-presentation, or mcp-office/create-document
         ELSE (manual fallback):
           Inform human that automatic conversion is unavailable, provide structured content for manual copy-paste, suggest alternatives (Google Docs, CloudConvert). Mark task as partially complete.
      2. Generate each requested format sequentially
      3. Output naming: formal-{source_filename}.{extension}
         Example: idea-summary-v1.md -> formal-idea-summary-v1.pptx
    </action>
    <output>Generated document files in {idea_folder}</output>
  </step_5>

  <step_6>
    <name>Verify and Complete</name>
    <action>
      1. Check each output file exists in {idea_folder}
      2. Verify file size > 0 for each
      3. List generated files with paths and sizes to human
      4. Wait for human to confirm receipt
    </action>
    <success_criteria>
      - All requested files exist and are non-empty
      - Human confirms receipt
    </success_criteria>
    <output>Verified file list with paths</output>
  </step_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  task_based_skill: "Share Idea"
  next_task_based_skill: null
  require_human_review: true
  auto_proceed: "{from input auto_proceed}"
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
    <name>Human confirmed receipt</name>
    <verification>Human acknowledged generated files</verification>
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

**When:** Neither pandoc nor MCP tools are available
**Then:**
```
1. Inform human: "Document conversion tools not available"
2. Provide structured content in clipboard-friendly format
3. Suggest alternatives (Google Docs, CloudConvert, manual copy)
4. Mark task as partially complete
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

---

## Examples

**Scenario:** User wants to share `idea-summary-v1.md` as a PowerPoint

```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. Load Config:
   - tools.json: pptx=true, pdf=true, docx=false
   - pandoc detected at /usr/local/bin/pandoc

3. Identify Source:
   - Found: x-ipe-docs/ideas/mobile-app-idea/idea-summary-v1.md

4. Confirm Format:
   - Human selects: PowerPoint (.pptx)

5. Prepare Content:
   - Restructure for slides, create bullet points

6. Convert:
   - pandoc -t pptx -o "formal-idea-summary-v1.pptx" "idea-summary-v1.md"

7. Verify:
   - File created: formal-idea-summary-v1.pptx (245 KB)
   - Report: "Created formal-idea-summary-v1.pptx in x-ipe-docs/ideas/mobile-app-idea/"

8. Resume Task Flow from x-ipe-workflow-task-execution skill
```
