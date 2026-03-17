---
name: x-ipe-tool-knowledge-extraction-user-manual
description: Provides playbook, collection template, acceptance criteria, and app-type mixins for user manual knowledge extraction. Loaded by x-ipe-task-based-application-knowledge-extractor during Phase 1. Triggers on category "user-manual".
categories:
  - "user-manual"
---

# Knowledge Extraction — User Manual

## Purpose

AI Agents follow this skill to provide user manual extraction artifacts:
1. Base playbook template defining user manual section layout
2. Collection template with per-section extraction prompts
3. Acceptance criteria for validating extracted content
4. App-type mixins (web/cli/mobile) for platform-specific overlays

---

## Important Notes

BLOCKING: This is a **tool skill** — it provides templates and validation only. The extraction process is driven by `x-ipe-task-based-application-knowledge-extractor`.
CRITICAL: All template files MUST exist at the paths declared in `get_artifacts` output. The extractor verifies existence before proceeding.

---

## About

This skill is a template provider for the Application Knowledge Extractor. When the extractor receives a `purpose: "user-manual"` request, it discovers this skill by globbing `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md` and matching `categories: ["user-manual"]` in the frontmatter.

**Key Concepts:**
- **Playbook Template** — Defines the standard user manual section layout (8 sections)
- **Collection Template** — Per-section extraction prompts guiding what to look for in source
- **Acceptance Criteria** — Validation rules per section (checklist format)
- **App-Type Mixin** — Platform-specific overlay adding sections/prompts for web, CLI, or mobile apps

---

## When to Use

```yaml
triggers:
  - "user-manual extraction"
  - "category: user-manual"
  - "extract user manual knowledge"

not_for:
  - "API reference extraction" → use x-ipe-tool-knowledge-extraction-api-reference (future)
  - "Direct README update" → use x-ipe-tool-readme-updator
```

---

## Input Parameters

```yaml
input:
  operation: "get_artifacts | get_collection_template | validate_section | get_mixin | pack_section | score_quality"
  category: "user-manual"
  section_id: "string | null"       # Required for validate_section, pack_section, score_quality
  content_path: "string | null"     # Path to extracted content file
  app_type: "web | cli | mobile | null"  # Required for get_mixin
  config:
    web_search_enabled: false
    max_files_per_section: 20
    max_iterations: 3
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />
  <field name="category" source="Always 'user-manual' for this skill" />

  <field name="section_id" source="Caller provides section identifier">
    <steps>
      1. Required for validate_section and pack_section operations
      2. Must match an H2 slug from playbook template (e.g., "1-overview", "2-installation-setup")
    </steps>
  </field>

  <field name="content_path" source="Caller provides path to extracted content in .x-ipe-checkpoint/">
    <steps>
      1. Path must exist and be readable
      2. Content must be UTF-8 markdown
    </steps>
  </field>

  <field name="app_type" source="Caller specifies target platform for get_mixin">
    <steps>
      1. Must be one of: web, cli, mobile
      2. IF null and operation is get_mixin → return error INVALID_APP_TYPE
    </steps>
  </field>

  <field name="config" source="Caller provides or uses defaults">
    <steps>
      1. web_search_enabled defaults to false
      2. max_files_per_section defaults to 20
      3. max_iterations defaults to 3
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Template files exist</name>
    <verification>All files in templates/ directory are present and readable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Valid operation requested</name>
    <verification>operation parameter matches one of the 6 defined operations</verification>
  </checkpoint>
  <checkpoint required="false">
    <name>Content file exists (for validate/pack)</name>
    <verification>IF operation is validate_section or pack_section THEN content_path file exists</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: get_artifacts

**When:** Extractor Step 1.3 loads this skill and needs paths to all templates.

```xml
<operation name="get_artifacts">
  <action>
    1. Return paths to all template files relative to skill root:
       - playbook_template: templates/playbook-template.md
       - collection_template: templates/collection-template.md
       - acceptance_criteria: templates/acceptance-criteria.md
    2. Return mixin paths:
       - app_type_mixins.web: templates/mixin-web.md
       - app_type_mixins.cli: templates/mixin-cli.md
       - app_type_mixins.mobile: templates/mixin-mobile.md
    3. Return config defaults:
       - web_search_enabled: false
       - max_files_per_section: 20
  </action>
  <output>
    artifact_paths object with playbook_template, collection_template,
    acceptance_criteria, and app_type_mixins map
  </output>
</operation>
```

### Operation: get_collection_template

**When:** Extractor Step 2.1 reads section-specific extraction prompts.

```xml
<operation name="get_collection_template">
  <action>
    1. Read templates/collection-template.md
    2. IF section_id provided → extract only that section's content
    3. ELSE → return full template with all 8 sections
    4. Each section contains HTML comments with EXTRACTION PROMPTS
  </action>
  <constraints>
    - BLOCKING: Do NOT modify prompt content; return as-is from template
  </constraints>
  <output>Markdown content with extraction prompts in HTML comments</output>
</operation>
```

### Operation: validate_section

**When:** Extractor Step 3.1 validates extracted content against acceptance criteria.

```xml
<operation name="validate_section">
  <action>
    1. Read templates/acceptance-criteria.md
    2. Extract criteria for the given section_id
    3. Read content at content_path
    4. Evaluate each criterion against the content:
       a. For each checkbox item, check if content satisfies the rule
       b. Mark as PASS or FAIL with brief feedback
    5. IF any REQ criterion fails due to insufficient source material (not poor writing):
       a. Mark criterion as INCOMPLETE (distinct from FAIL)
       b. Add to `missing_info[]` with description of what content is needed
       c. The extractor should use `missing_info` to request more source material
    6. Return validation result with per-criterion status
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: ALL criteria must be evaluated — do not skip any
    - CRITICAL: Distinguish FAIL (content exists but is wrong) from INCOMPLETE (content is missing/thin)
  </constraints>
  <output>
    validation_result: { section_id, passed: bool, criteria: [{id, status, feedback}], missing_info: [] }
  </output>
</operation>
```

### Operation: get_mixin

**When:** Extractor needs platform-specific extraction prompts.

```xml
<operation name="get_mixin">
  <action>
    1. Resolve mixin file from app_type:
       - web → templates/mixin-web.md
       - cli → templates/mixin-cli.md
       - mobile → templates/mixin-mobile.md
    2. Read and return the mixin template content
    3. Mixin contains additional sections and extraction prompts to merge with base template
  </action>
  <constraints>
    - BLOCKING: app_type is required and must be web, cli, or mobile
  </constraints>
  <output>Mixin markdown content with additional sections and prompts</output>
</operation>
```

### Operation: pack_section

**When:** Extractor packs validated content into final user manual format.

```xml
<operation name="pack_section">
  <input>
    <field name="section_id" type="string" required="true">Section identifier (e.g., "1-overview", "2-installation-setup")</field>
    <field name="content_path" type="string" required="true">Path to validated content file in .x-ipe-checkpoint/</field>
    <field name="split_mode" type="boolean" required="false" default="false">If true, output as standalone sub-markdown file with Instructions and Screenshots sections</field>
  </input>
  <action>
    1. Read the playbook template to get section heading and structure
    2. Read validated content at content_path
    3. IF split_mode is true:
       a. Create standalone sub-markdown file with naming convention: {nn}-{section-slug}.md
       b. Structure: H1 heading → ## Instructions → ## Content → ## Screenshots (optional)
       c. Instructions section explains what this section covers and how to use it
       d. Screenshots section includes references to images in references/ subfolder: references/{nn}-{section-slug}-{description}.png
    4. ELSE (split_mode is false):
       a. Format content under proper H2 heading with consistent style
       b. Apply section numbering from playbook
       c. Ensure subsection headings use H3
       d. Wrap code examples in fenced code blocks
       e. Normalize list formatting
    5. Return formatted section ready for assembly
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: Do not alter factual content — only apply formatting
    - CRITICAL: Follow naming convention for sub-files and images per Content Splitting Guidelines in playbook-template.md
    - CRITICAL: All screenshot images MUST be placed in references/ subfolder, never at output root
  </constraints>
  <output>Formatted markdown section (inline or sub-file path) ready for final assembly</output>
</operation>
```

---

### Operation: score_quality

**When:** Extractor Phase 5 requests quality assessment for a section.

```xml
<operation name="score_quality">
  <action>
    1. Read content at content_path for the given section_id
    2. Load acceptance criteria for the section from templates/acceptance-criteria.md
    3. Evaluate content across 4 quality dimensions:
       a. **Completeness** (0.0–1.0): ratio of REQ criteria satisfied
       b. **Structure** (0.0–1.0): proper heading hierarchy, code blocks, lists
       c. **Clarity** (0.0–1.0): actionable instructions, concrete examples present
       d. **Freshness** (0.0–1.0): content references current versions, no stale info
    4. Apply section-aware weighting:
       - **Sections 4 (Core Features) and 5 (Common Workflow Scenarios):**
         Weighted mean: completeness 0.35, structure 0.15, clarity 0.40, freshness 0.10
         (clarity weighted highest — these sections MUST have actionable step-by-step instructions)
       - **All other sections:**
         Weighted mean: completeness 0.40, structure 0.20, clarity 0.30, freshness 0.10
    5. Generate improvement_hints[] for any dimension below 0.6
    6. **For sections 4 and 5 ONLY:** Apply critical-but-constructive feedback mode:
       a. Be MORE specific in improvement_hints (name exact missing subsections, features, or scenarios)
       b. Lower the "acceptable" threshold: score < 0.70 → generate hints (not just < 0.60)
       c. If instructions are vague or generic → explicitly call out "Instructions lack step-by-step detail"
       d. If no screenshots referenced → hint "No screenshot references found — add for UI features"
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: Scoring is based on domain expertise — this skill defines what "quality" means for user manuals
    - CRITICAL: Sections 4 and 5 receive stricter evaluation — they are the core value of the manual
  </constraints>
  <output>
    quality_result: { section_id, section_quality_score, dimensions: {completeness, structure, clarity, freshness}, improvement_hints[], is_key_section: bool }
  </output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "get_artifacts | get_collection_template | validate_section | get_mixin | pack_section | score_quality"
  result:
    # get_artifacts
    artifact_paths:
      playbook_template: "templates/playbook-template.md"
      collection_template: "templates/collection-template.md"
      acceptance_criteria: "templates/acceptance-criteria.md"
      app_type_mixins:
        web: "templates/mixin-web.md"
        cli: "templates/mixin-cli.md"
        mobile: "templates/mixin-mobile.md"
    config_defaults:
      web_search_enabled: false
      max_files_per_section: 20
    # validate_section
    validation_result:
      section_id: "{id}"
      passed: true | false
      criteria: [{ id: "string", status: "pass | fail | incomplete", feedback: "string" }]
      missing_info: ["string"]  # content gaps requiring more extraction
    # pack_section
    formatted_content: "string"
    # score_quality
    quality_result:
      section_id: "{id}"
      section_quality_score: 0.0  # 0.0–1.0
      dimensions:
        completeness: 0.0
        structure: 0.0
        clarity: 0.0
        freshness: 0.0
      improvement_hints: ["string"]
      is_key_section: false  # true for sections 4 and 5 (stricter evaluation)
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed</name>
    <verification>operation_output.success is true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Result matches operation</name>
    <verification>Returned result fields match the requested operation type</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Template files intact</name>
    <verification>No template files were modified during operation</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | operation not one of the 6 defined | Check operation name matches exactly |
| `MISSING_SECTION_ID` | section_id null for validate/pack/score_quality | Provide section_id matching playbook template |
| `MISSING_CONTENT_PATH` | content_path null for validate/pack/score_quality | Provide path to extracted content file |
| `CONTENT_NOT_FOUND` | content_path file does not exist | Verify file was written by extractor |
| `INVALID_APP_TYPE` | app_type not web/cli/mobile | Use one of: web, cli, mobile |
| `TEMPLATE_NOT_FOUND` | Template file missing from skill | Re-install skill or verify file paths |
| `SCORING_FAILED` | Unable to evaluate content quality | Verify content exists and is readable |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/playbook-template.md` | Base user manual section layout (8 sections) |
| `templates/collection-template.md` | Per-section extraction prompts |
| `templates/acceptance-criteria.md` | Per-section validation rules, also used for quality scoring |
| `templates/mixin-web.md` | Web app-specific sections and prompts |
| `templates/mixin-cli.md` | CLI app-specific sections and prompts |
| `templates/mixin-mobile.md` | Mobile app-specific sections and prompts |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
