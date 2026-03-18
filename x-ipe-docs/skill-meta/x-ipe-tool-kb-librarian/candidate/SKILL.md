---
name: x-ipe-tool-kb-librarian
description: Organize knowledge base intake files — analyze content, assign lifecycle/domain tags, generate YAML frontmatter, move to destination folders. Use when user triggers AI Librarian from KB UI or CLI. Triggers on requests like "organize knowledge base intake files with AI Librarian", "run AI Librarian", "organize intake".
---

# KB AI Librarian

## Purpose

AI Agents follow this skill to organize knowledge base intake files by:
1. Reading pending files from the `.intake/` folder
2. Analyzing content to determine the best destination folder and tags
3. Generating YAML frontmatter for markdown files
4. Moving files to their destination and updating intake status

---

## Important Notes

BLOCKING: Process ALL pending files in one batch. Do not prompt for file selection.

BLOCKING: Respect pre-assigned destinations from the UI. Only use AI folder selection for files without a destination.

CRITICAL: Non-markdown files (PDF, images, etc.) are moved and status-tracked but do NOT receive frontmatter injection.

CRITICAL: Existing frontmatter in markdown files MUST be preserved. Only merge missing fields — never overwrite existing values.

---

## About

The KB AI Librarian automates the organization of files dropped into the knowledge base intake folder. When a user clicks "✨ Run AI Librarian" in the KB Browse Modal or triggers the command via CLI, this skill processes all pending intake files: analyzing their content, assigning appropriate tags from the project's tag taxonomy, generating frontmatter metadata for markdown files, and moving them to the correct destination folder.

**Key Concepts:**
- **Intake Folder** — The `.intake/` directory under the KB root where new files are dropped for processing
- **Intake Status** — Tracked in `.intake-status.json`: `pending` → `processing` → `filed`
- **Tag Taxonomy** — Lifecycle tags (7) and domain tags (10) defined in `knowledgebase-config.json`
- **Frontmatter** — YAML metadata block at the top of markdown files (title, tags, author, created, auto_generated)
- **Destination Folder** — Target folder within the KB where a file should live, determined by UI assignment or AI analysis

---

## When to Use

```yaml
triggers:
  - "organize knowledge base intake files with AI Librarian"
  - "run AI Librarian"
  - "organize intake"
  - "process intake files"

not_for:
  - "Browsing KB files or managing intake UI — use KB Browse Modal frontend"
  - "Configuring KB settings — edit knowledgebase-config.json directly"
  - "Creating new KB articles from scratch — use KB editor"
```

---

## Input Parameters

```yaml
input:
  operation: "organize_intake"
  kb_root: "auto-detect | explicit path"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Always 'organize_intake' — single-operation skill">
    <validation>MUST equal 'organize_intake'</validation>
  </field>

  <field name="kb_root" source="Auto-detected from project structure">
    <steps>
      1. Look for x-ipe-docs/knowledge-base/ in the project root
      2. IF not found, check knowledgebase-config.json for configured root
      3. IF still not found, fail with KB_ROOT_NOT_FOUND
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>KB root folder exists</name>
    <verification>x-ipe-docs/knowledge-base/ directory exists in the project</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Intake folder exists</name>
    <verification>.intake/ subdirectory exists under KB root</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>KB config readable</name>
    <verification>knowledgebase-config.json exists and contains tag taxonomy (tags.lifecycle, tags.domain)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: organize_intake

**When:** User triggers AI Librarian to process pending intake files.

```xml
<operation name="organize_intake">
  <action>
    1. Read KB configuration:
       - Load knowledgebase-config.json from KB root
       - Extract tag taxonomy: tags.lifecycle[] and tags.domain[]
       - Extract folder structure for destination matching

    2. Get intake files:
       - Call GET /api/kb/intake (or read .intake/ directory + .intake-status.json directly)
       - Filter to files with status == "pending" (or no status entry = pending by default)
       - IF no pending files found → print "No pending files to process" and exit with success

    3. For each pending file, process sequentially:

       a. Set status to "processing":
          - Call PUT /api/kb/intake/status with {filename, status: "processing"}

       b. Read file content:
          - Read the full file content from .intake/{filename}

       c. Determine destination folder:
          - IF file has a pre-assigned destination in .intake-status.json → use it
          - ELSE analyze content to determine the best matching KB folder:
            * Scan existing KB folder structure (folder names and any README descriptions)
            * Match file content topics/keywords to folder purposes
            * Select the single best-matching folder
          - IF destination folder does not exist → create it

       d. Assign tags:
          - Analyze content against the tag taxonomy from knowledgebase-config.json
          - Select 1-2 lifecycle tags (e.g., "Design", "Implementation")
          - Select 1-3 domain tags (e.g., "API", "Security")
          - Use conservative tagging — only assign tags with clear evidence in content

       e. Handle file based on type:
          - IF markdown (.md) file:
            * Parse existing frontmatter (if any)
            * Generate frontmatter fields: title, tags (lifecycle + domain), author, created, auto_generated: true
            * MERGE with existing frontmatter — preserve existing values, only fill missing fields
            * Write updated content with merged frontmatter
          - IF non-markdown file:
            * Skip frontmatter generation entirely
            * File will be moved as-is

       f. Move file to destination:
          - Move file from .intake/{filename} to {destination_folder}/{filename}
          - Use KB service move capability (POST /api/kb/files/move or filesystem move)

       g. Update status to "filed":
          - Call PUT /api/kb/intake/status with {filename, status: "filed", destination: "{destination_path}"}

    4. Print terminal summary:
       - Format: "{N} files processed → {folder1}/ ({count1}), {folder2}/ ({count2})"
       - If any errors occurred: also print "{M} files failed: {error details}"
  </action>
  <constraints>
    - BLOCKING: Must set status to "processing" BEFORE analyzing each file
    - BLOCKING: Must respect pre-assigned destinations — do NOT override with AI suggestion
    - CRITICAL: Continue processing remaining files if one file fails
    - CRITICAL: Only generate frontmatter for markdown files
    - CRITICAL: Never overwrite existing frontmatter fields — merge only
  </constraints>
  <output>operation_output with files_processed, destinations, errors, summary</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    files_processed: 3
    destinations:
      - "docs/guides/"
      - "docs/references/"
    summary: "3 files processed → docs/guides/ (2), docs/references/ (1)"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All pending files processed</name>
    <verification>Every file with status "pending" was attempted (status changed from pending)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Markdown files have frontmatter</name>
    <verification>All processed .md files have YAML frontmatter with title, tags, author, created, auto_generated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Files moved to destinations</name>
    <verification>Processed files no longer in .intake/ — moved to destination folders</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Status updated to filed</name>
    <verification>.intake-status.json shows status="filed" with destination for each processed file</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Terminal summary printed</name>
    <verification>Summary line shows count of files processed and destination folders</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `KB_ROOT_NOT_FOUND` | No knowledge-base/ folder in project | Verify KB is initialized; check project structure |
| `INTAKE_FOLDER_NOT_FOUND` | No .intake/ directory under KB root | Create .intake/ folder or check KB config |
| `CONFIG_MISSING_TAGS` | knowledgebase-config.json missing tag taxonomy | Add tags.lifecycle and tags.domain arrays to config |
| `FILE_READ_ERROR` | Cannot read file from .intake/ | Check file permissions; skip file and continue |
| `MOVE_FAILED` | File move operation failed | Check destination path validity and permissions; retry once |
| `NO_PENDING_FILES` | All intake files already processed | Not an error — print message and exit with success |

---

## Templates

| File | Purpose |
|------|---------|
| _None_ | This skill produces no template files — it operates on existing files |

---

## Examples

See `.github/skills/x-ipe-tool-kb-librarian/references/examples.md` for usage examples.
