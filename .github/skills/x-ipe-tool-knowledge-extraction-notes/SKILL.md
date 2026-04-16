---
name: x-ipe-tool-knowledge-extraction-notes
description: General-purpose knowledge extractor that organizes content into structured markdown knowledge bases with hierarchy, embedded images, and linked overview. Use when extracting knowledge, creating structured notes, or organizing content into a knowledge base. Triggers on requests like "extract knowledge notes", "create knowledge base", "organize knowledge", "take key insights".
categories:
  - "notes"
---

> ⚠️ **DEPRECATED** — This skill is superseded by [`x-ipe-knowledge-constructor-notes`](.github/skills/x-ipe-knowledge-constructor-notes/SKILL.md).
> Introduced in FEATURE-059-C. This skill will be removed in a future release.
> **Do not use for new work.** Existing references should migrate to the replacement skill.

# Knowledge Extraction — Notes

## Purpose

AI Agents follow this skill to extract and organize knowledge into structured markdown files:
1. Initialize a knowledge folder with standardized structure
2. Extract key insights from source content into numbered markdown sections
3. Organize hierarchical content with sub-folders and sub-files
4. Embed images/screenshots with consistent naming
5. Generate an overview.md as a linked table of contents

---

## Important Notes

BLOCKING: All images MUST be stored in the `.images/` subfolder — never in the knowledge root or section folders.
CRITICAL: Section files MUST follow the `{NN}.{slug}.md` numbering convention. Sub-section files use `{NNMM}.{slug}.md` inside `{NN}.{slug}/` folders.
CRITICAL: `overview.md` MUST be regenerated after any structural change (add/remove/rename sections).
MANDATORY: Every markdown file (sections and overview.md) MUST end with a `## References` footer listing all original source URLs, file paths, or data sources used to produce that content. This applies regardless of template_type.

---

## About

A general-purpose knowledge extraction tool that produces self-contained markdown knowledge bases. Unlike specialized extractors (user-manual, reverse-engineering), this skill handles any content type — research notes, meeting insights, tutorial material, reference documentation, or free-form knowledge capture.

**Key Concepts:**
- **Knowledge Folder** — Root directory named after the knowledge topic, containing all related files
- **Section Numbering** — Two-digit prefix (01–99) for ordering; four-digit for sub-sections (0101–0199)
- **Overview** — `overview.md` at root acts as table of contents with links to all sections
- **Source Reference Tracking** — Every markdown file ends with a `## References` footer listing original URLs/data sources

---

## When to Use

```yaml
triggers:
  - "extract knowledge notes"
  - "create knowledge base"
  - "organize knowledge"
  - "knowledge extraction notes"
  - "take key insights"
  - "create structured notes"
  - "extract notes from content"

not_for:
  - "User manual extraction → use x-ipe-tool-knowledge-extraction-user-manual"
  - "Application reverse engineering → use x-ipe-tool-knowledge-extraction-application-reverse-engineering"
  - "README updates → use x-ipe-tool-readme-updator"
```

---

## Input Parameters

```yaml
input:
  operation: "init_knowledge_folder | get_template | extract_section | embed_image | generate_overview | validate_structure"
  knowledge_name: "string"           # Root folder name (lowercase, hyphens, no spaces)
  output_dir: "string"              # Parent directory (default: current working directory)
  source_content: "string | null"   # Content to extract from (text, URL, file path)
  section_id: "string | null"       # Section number (e.g., "01", "0201")
  image_path: "string | null"       # Path to image file for embed_image
  source_urls: "string[] | null"     # Original page URLs or data source identifiers for reference tracking
  template_type: "general | tutorial | reference | research | meeting-notes"  # Default: general
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />

  <field name="knowledge_name">
    <steps>
      1. IF provided by caller → use directly
      2. MUST be lowercase, hyphens only, no spaces (e.g., "react-hooks-guide")
      3. IF contains invalid characters → sanitize by replacing spaces/underscores with hyphens, lowercasing
    </steps>
  </field>

  <field name="output_dir">
    <steps>
      1. IF provided → use as-is
      2. IF null → default to current working directory
      3. Verify directory exists and is writable
    </steps>
  </field>

  <field name="source_content">
    <steps>
      1. Required for extract_section operation
      2. Can be inline text, a file path, or a URL
      3. IF file path → read content from file
      4. IF URL → fetch and convert to text
    </steps>
  </field>

  <field name="section_id">
    <steps>
      1. Required for extract_section, embed_image operations
      2. Must match {NN} (two-digit, e.g., "01") or {NNMM} (four-digit, e.g., "0201") format
      3. IF invalid format → return error INVALID_SECTION_ID
    </steps>
  </field>

  <field name="image_path">
    <steps>
      1. Required for embed_image operation
      2. Must point to an existing file
      3. Must be a supported format: png, jpg, jpeg, gif, svg, webp
      4. IF not found or unsupported → return error INVALID_IMAGE
    </steps>
  </field>

  <field name="image_description">
    <steps>
      1. Used for embed_image operation to generate target filename
      2. Sanitize: lowercase, replace spaces with hyphens, strip special chars
      3. IF null → derive slug from original filename
    </steps>
  </field>

  <field name="source_urls">
    <steps>
      1. Collect all original page URLs, file paths, or data source identifiers used during extraction
      2. IF source_content is a URL → automatically include it
      3. IF source_content is a file → include the file path
      4. IF additional URLs were browsed/referenced during extraction → append them
      5. IF null → section References footer will note "Source not recorded"
    </steps>
  </field>

  <field name="template_type">
    <steps>
      1. IF provided → load corresponding template from templates/
      2. IF null → default to "general"
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Knowledge Name Valid</name>
    <verification>knowledge_name is lowercase, hyphens only, 1-64 chars</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output Directory Exists</name>
    <verification>output_dir exists and is writable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation Valid</name>
    <verification>operation matches one of the defined operations</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Initialize Knowledge Folder

**When:** Starting a new knowledge base from scratch.

```xml
<operation name="init_knowledge_folder">
  <action>
    1. Create root folder: {output_dir}/{knowledge_name}/
    2. Create hidden images folder: {output_dir}/{knowledge_name}/.images/
    3. Create initial overview.md with title and empty content table
    4. IF template_type provided → load template from templates/ and create placeholder sections
    5. Return folder path and created file list
  </action>
  <constraints>
    - BLOCKING: Folder must not already exist (prevents accidental overwrite)
    - BLOCKING: .images/ must be created as hidden directory
  </constraints>
  <output>knowledge_folder_path, created_files[]</output>
</operation>
```

### Operation: Get Template

**When:** Retrieving the section structure template for a given knowledge type.

```xml
<operation name="get_template">
  <action>
    1. Load template from templates/{template_type}-template.md
    2. Return template content with section layout and placeholder descriptions
  </action>
  <constraints>
    - IF template_type not found → fall back to "general" template
  </constraints>
  <output>template_content, section_list[]</output>
</operation>
```

### Operation: Extract Section

**When:** Extracting knowledge from source content into a specific section file.

```xml
<operation name="extract_section">
  <action>
    1. Analyze source_content for key insights relevant to section_id
    2. Determine if section has sub-topics requiring hierarchy
    3. IF flat section:
       - Create {NN}.{slug}.md in knowledge root
       - Write extracted content as structured markdown
    4. IF hierarchical section:
       - Create folder {NN}.{slug}/
       - Create sub-files {NNMM}.{sub-slug}.md for each sub-topic
    5. IF source contains relevant images/diagrams:
       - Save to .images/ with naming {NN}.{description-slug}.{ext}
       - Insert image references in markdown: ![description](.images/{NN}.{slug}.{ext})
    6. Append `## References` footer at the end of each created markdown file:
       - List all source_urls provided for this section
       - IF source_content was a URL → auto-include it
       - IF source_content was a file path → include it
       - Format as numbered markdown list with URL/path and access date
    7. Return created file paths and extraction summary
  </action>
  <constraints>
    - BLOCKING: section_id and source_content are required
    - BLOCKING: Images MUST go to .images/ folder, never alongside markdown files
    - CRITICAL: Markdown content should use relative paths for image references
    - MANDATORY: `## References` footer is required on every section file — never omit it
  </constraints>
  <output>created_files[], extraction_summary</output>
</operation>
```

### Operation: Embed Image

**When:** Adding a screenshot or diagram to the knowledge base.

```xml
<operation name="embed_image">
  <action>
    1. Validate image_path exists and is a supported format (png, jpg, jpeg, gif, svg, webp)
    2. Generate target filename: {section_id}.{image_description}.{ext}
    3. Copy image to {knowledge_folder}/.images/{target_filename}
    4. Return the markdown image reference string
  </action>
  <constraints>
    - BLOCKING: image_path must exist
    - BLOCKING: Target must be inside .images/ folder
  </constraints>
  <output>image_ref_markdown, target_path</output>
</operation>
```

### Operation: Generate Overview

**When:** Creating or updating the overview.md table of contents after structural changes.

```xml
<operation name="generate_overview">
  <action>
    1. Scan knowledge folder for all .md files (excluding overview.md)
    2. Build ordered list based on numeric prefixes
    3. For hierarchical sections, indent sub-files under parent
    4. Extract title from each file (first H1 or filename)
    5. Generate overview.md with:
       - Knowledge base title (from knowledge_name)
       - Brief description (if available)
       - Linked table of contents with relative paths
       - Section count summary
    6. Append consolidated `## References` footer to overview.md:
       - Scan all section files for their `## References` sections
       - Deduplicate and merge all source URLs/paths into a single list
       - Format as numbered list, grouped by section origin
    7. Write to {knowledge_folder}/overview.md
  </action>
  <constraints>
    - BLOCKING: Must scan recursively for sub-folders
    - CRITICAL: Links must use relative paths from overview.md location
  </constraints>
  <output>overview_path, section_count, toc_structure</output>
</operation>
```

### Operation: Validate Structure

**When:** Verifying the knowledge folder integrity.

```xml
<operation name="validate_structure">
  <action>
    1. Verify overview.md exists and is not empty
    2. Verify .images/ folder exists
    3. Verify all section files follow {NN}.{slug}.md naming
    4. Verify all sub-section files follow {NNMM}.{slug}.md naming inside {NN}.{slug}/ folders
    5. Verify all image references in markdown files point to existing files in .images/
    6. Verify all links in overview.md point to existing files
    7. Verify every section markdown file and overview.md has a `## References` footer
    8. Report any broken links, naming violations, missing references, or missing files
  </action>
  <constraints>
    - CRITICAL: Return detailed report, not just pass/fail
  </constraints>
  <output>validation_report{valid, issues[], warnings[]}</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "{operation_name}"
  result:
    knowledge_folder: "{path}"
    files_created: []
    files_modified: []
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation Completed</name>
    <verification>operation_output.success == true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Folder Structure Valid</name>
    <verification>Knowledge folder contains overview.md and .images/ directory</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Naming Convention Followed</name>
    <verification>All files follow {NN}.{slug}.md pattern; sub-files follow {NNMM}.{slug}.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Images Properly Stored</name>
    <verification>All images in .images/ folder; no images outside this folder</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Overview Links Valid</name>
    <verification>All links in overview.md resolve to existing files</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>References Footer Present</name>
    <verification>Every section markdown file and overview.md has a ## References footer listing source URLs/data sources</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_NAME` | knowledge_name contains spaces or special chars | Sanitize: lowercase, replace spaces/underscores with hyphens |
| `FOLDER_EXISTS` | Knowledge folder already exists at target path | Use existing folder or choose different name |
| `MISSING_SOURCE` | source_content is null for extract_section | Provide source content to extract from |
| `INVALID_IMAGE` | image_path doesn't exist or unsupported format | Verify path and use png/jpg/gif/svg/webp |
| `BROKEN_LINK` | overview.md references non-existent file | Run generate_overview to regenerate |
| `INVALID_SECTION_ID` | section_id doesn't match {NN} or {NNMM} pattern | Use two-digit (01-99) or four-digit (0101-0199) format |

---

## Anti-Patterns

- **Images outside `.images/`** — Never place screenshots alongside markdown files. Always store in `.images/` and reference via relative path.
- **Skipping overview regeneration** — After adding/removing/renaming sections, always run `generate_overview`. Stale overview.md causes confusion.
- **Non-numeric prefixes** — Section files must start with `{NN}.` (e.g., `01.`). Using names without numeric prefix breaks ordering and overview generation.
- **Deep nesting** — Only one level of hierarchy is supported (`{NN}.{slug}/{NNMM}.{slug}.md`). Do not nest sub-folders inside sub-folders.
- **Manual overview editing** — Do not hand-edit overview.md links. Always regenerate with `generate_overview` to ensure consistency.
- **Omitting references** — Never skip the `## References` footer. Even if source is inline text, note "Direct input" as the source.

---

## Templates

| File | Purpose |
|------|---------|
| `templates/general-template.md` | Default knowledge structure template |
| `templates/overview-template.md` | Template for overview.md generation |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-knowledge-extraction-notes/references/examples.md) for usage examples.
