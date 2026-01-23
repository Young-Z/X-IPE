---
name: task-type-share-idea
description: Convert refined idea summaries to shareable document formats (PPTX, DOCX, PDF). Use when user wants to share or present an idea. Uses MCP document conversion tools or pandoc. Triggers on requests like "share idea", "convert to ppt", "make presentation", "export idea".
---

# Task Type: Share Idea

## Purpose

Convert refined idea summaries to human-readable shareable formats by:
1. Selecting the source idea summary file
2. Choosing target format(s) (PPTX, DOCX, PDF, etc.)
3. Using document conversion tools (MCP or pandoc)
4. Generating formatted documents in the idea folder
5. Naming output as `formal-{source_name}.{extension}`

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| Task Type | Share Idea |
| Category | ideation-stage |
| Standalone | No |
| Next Task | Requirement Gathering (optional) |
| Auto-advance | No |
| Human Review | Yes |

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Refined idea summary exists (`idea-summary-vN.md`) | Yes |
| 2 | Target format(s) specified by human | Yes |
| 3 | Idea folder path provided | Yes |

---

## Execution Flow

Execute Share Idea by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Identify Source | Locate latest `idea-summary-vN.md` file | Source file found |
| 2 | Confirm Format | Ask human for target format(s) | Format(s) confirmed |
| 3 | Prepare Content | Restructure content for target format | Content ready |
| 4 | Convert | Use pandoc/MCP to generate output files | Files generated |
| 5 | Verify | Confirm output files exist and have content | Files verified |
| 6 | Complete | Report files to human | Human confirms receipt |

**⛔ BLOCKING RULES:**
- Step 2: BLOCKED until human confirms target format(s)
- Step 5: BLOCKED if output files are empty or missing

---

## Supported Output Formats

| Format | Extension | Tool | Best For |
|--------|-----------|------|----------|
| PowerPoint | .pptx | pandoc / MCP | Presentations |
| Word | .docx | pandoc / MCP | Documents, reviews |
| PDF | .pdf | pandoc / MCP | Read-only sharing |
| HTML | .html | pandoc / MCP | Web viewing |

---

## Execution Procedure

### Step 1: Identify Source File

**Action:** Locate the refined idea summary to convert

```
1. Navigate to docs/ideas/{folder}/
2. List available idea-summary-vN.md files
3. Select the latest version OR human-specified version
4. Read the source content
```

**Output:** Source file path and content

### Step 2: Confirm Target Format(s)

**Action:** Ask human for desired output format(s)

**Question Template:**
```
Which format(s) would you like to generate?

Available options:
- [ ] PowerPoint (.pptx) - For presentations
- [ ] Word (.docx) - For document review
- [ ] PDF (.pdf) - For read-only sharing
- [ ] HTML (.html) - For web viewing

You can select multiple formats.
```

**Output:** List of target formats

### Step 3: Prepare Content Structure

**Action:** Organize content for conversion

**For PowerPoint (PPTX):**
```markdown
# Title Slide
- Title: {Idea Name}
- Subtitle: Idea Summary

# Overview
- {Overview content as bullet points}

# Problem Statement
- {Problem as bullet points}

# Proposed Solution
- {Solution as bullet points}

# Key Features
- Feature 1: Description
- Feature 2: Description
- ...

# Success Criteria
- Criterion 1
- Criterion 2

# Next Steps
- {Call to action}
```

**For Word (DOCX):**
- Use the markdown content directly
- Preserve headers, tables, and formatting

### Step 4: Execute Conversion

**Action:** Use available conversion tool

**Option A: Using Pandoc (if available)**
```bash
# Convert to PPTX
pandoc -t pptx -o "formal-{source_name}.pptx" "{source_file}"

# Convert to DOCX
pandoc -t docx -o "formal-{source_name}.docx" "{source_file}"

# Convert to PDF
pandoc -t pdf -o "formal-{source_name}.pdf" "{source_file}"
```

**Option B: Using MCP Document Tools (if available)**
```
Use MCP server tools for document generation:
- mcp-documents/convert
- mcp-office/create-presentation
- mcp-office/create-document
```

**Option C: Manual Generation**
If no conversion tools available:
1. Inform human that automatic conversion is not available
2. Provide structured content for manual copy-paste
3. Suggest online conversion tools

**Output File Naming:**
```
formal-{source_filename}.{extension}

Examples:
- idea-summary-v1.md → formal-idea-summary-v1.pptx
- idea-summary-v2.md → formal-idea-summary-v2.docx
```

### Step 5: Verify Output

**Action:** Confirm files were created

```
1. Check each output file exists
2. Verify file size > 0
3. List generated files to human
```

**Output:** List of created files with paths

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Source idea summary identified | Yes |
| 2 | Target format(s) confirmed with human | Yes |
| 3 | Document(s) generated successfully | Yes |
| 4 | Output files named correctly (`formal-{source}.{ext}`) | Yes |
| 5 | Files saved in idea folder | Yes |
| 6 | Human confirmed receipt of files | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Task Completion Output

Upon completion, return:
```yaml
task_type: Share Idea
idea_folder: docs/ideas/{folder}
source_file: idea-summary-vN.md
shared_formats:
  - pptx
  - docx
require_human_review: true
task_output_links:
  - docs/ideas/{folder}/formal-idea-summary-vN.pptx
  - docs/ideas/{folder}/formal-idea-summary-vN.docx
```

---

## Patterns

### Pattern: Single Format Export

**When:** Human requests one specific format
**Then:**
```
1. Confirm the format
2. Generate single output file
3. Provide download link/path
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
3. Suggest alternatives:
   - Online converters (Google Docs, CloudConvert)
   - Manual copy to PowerPoint/Word
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

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Converting without confirmation | May create unwanted formats | Always confirm format with human |
| Overwriting existing files | Loses previous versions | Use versioned naming |
| Ignoring conversion errors | Human doesn't know it failed | Report errors clearly |
| Skipping verification | May generate empty files | Always verify output |

---

## Example

**Scenario:** User wants to share `idea-summary-v1.md` as a PowerPoint

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Identify Source:
   - Found: docs/ideas/mobile-app-idea/idea-summary-v1.md
   
3. Confirm Format:
   Human selects: PowerPoint (.pptx)
   
4. Prepare Content:
   - Restructure for slides
   - Create bullet points
   
5. Execute Conversion:
   pandoc -t pptx -o "formal-idea-summary-v1.pptx" "idea-summary-v1.md"
   
6. Verify:
   - File created: formal-idea-summary-v1.pptx (245 KB)
   
7. Report:
   "Created formal-idea-summary-v1.pptx in docs/ideas/mobile-app-idea/"

8. Resume Task Flow from task-execution-guideline skill
```

---

## Tool Detection

At task start, detect available conversion tools:

```python
# Check for pandoc
which pandoc  # or: pandoc --version

# Check for MCP document tools
# Look for MCP servers with document capabilities

# Check for python-pptx (Python library)
pip show python-pptx

# Check for python-docx (Python library)
pip show python-docx
```

Report available tools to human before proceeding.
