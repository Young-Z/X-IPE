---
name: x-ipe-tool-knowledge-extraction-user-manual
version: "2.0"
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
  operation: "get_artifacts | get_collection_template | validate_section | get_mixin | pack_section | score_quality | test_walkthrough"
  category: "user-manual"
  section_id: "string | null"       # Required for validate_section, pack_section, score_quality
  content_path: "string | null"     # Path to extracted content file (e.g., .x-ipe-checkpoint/session-{ts}/content/section-{NN}-{slug}.md)
  app_type: "web | cli | mobile | null"  # Required for get_mixin
  app_url: "string | null"          # Optional URL for live walkthrough testing
  instruction_temperature: "strict | balanced | creative"  # Default: balanced
    # strict: Exact template adherence, verbatim labels, [PLACEHOLDER] markers, uniform phrasing.
    # balanced: Accuracy + natural flow. Representative examples. Moderate paraphrasing.
    # creative: High variability. Inventive scenarios. Exploration encouraged.
    # Used by: get_collection_template, validate_section, pack_section, score_quality, test_walkthrough
  config:                           # Passed through from extractor's config_overrides
    web_search_enabled: false       # Extractor default: true — extractor value overrides
    max_files_per_section: 20       # Shared default between extractor and tool skill
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
  <field name="app_url" source="Caller provides URL for live walkthrough testing">
    <steps>
      1. Optional — only used by test_walkthrough operation
      2. IF provided AND Chrome DevTools MCP available → live testing mode
      3. IF null → offline validation mode (structural checks only)
    </steps>
  </field>
  <field name="instruction_temperature" source="Provided by caller (extractor asks human). Default: balanced">
    <steps>
      1. Must be one of: strict, balanced, creative
      2. IF null or omitted → default to "balanced"
      3. Affects validate_section, pack_section, score_quality, get_collection_template, and test_walkthrough operations
    </steps>
  </field>
  <field name="config" source="Passed through from extractor's config_overrides. Caller provides or uses defaults.">
    <steps>
      1. web_search_enabled defaults to false (extractor default is true — extractor value takes precedence)
      2. max_files_per_section defaults to 20 (shared default with extractor)
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
    <verification>operation parameter matches one of the 7 defined operations</verification>
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
    5. Append instruction_temperature guidance to the returned prompts:
       - strict: "Write instructions exactly as found in source. Use verbatim labels and literal syntax. Mark placeholders with [PLACEHOLDER]. No paraphrasing."
       - balanced: "Write clear, natural instructions grounded in source. Light paraphrasing OK. Examples realistic."
       - creative: "Write engaging instructions. Inventive but plausible examples. Encourage exploration."
  </action>
  <constraints>
    - BLOCKING: Do NOT modify the base prompt content; append temperature guidance as a separate block
  </constraints>
  <output>Markdown content with extraction prompts in HTML comments plus temperature guidance</output>
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
    5. Apply instruction_temperature-aware evaluation thresholds:
       - **strict:** Require exact template adherence. Content with paraphrasing → FAIL on structure criteria. Missing [PLACEHOLDER] markers → FAIL.
       - **balanced:** Standard evaluation. Accept natural phrasing if factually correct.
       - **creative:** Relax structural criteria. Accept stylistic variation. Do NOT fail for exploratory tone or added context.
    6. IF any REQ criterion fails due to insufficient source material (not poor writing):
       a. Mark criterion as INCOMPLETE (distinct from FAIL)
       b. Add to `missing_info[]` with description of what content is needed
       c. The extractor should use `missing_info` to request more source material
    7. Return validation result with per-criterion status
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: ALL criteria must be evaluated — do not skip any
    - CRITICAL: Distinguish FAIL (content exists but is wrong) from INCOMPLETE (content is missing/thin)
    - CRITICAL: instruction_temperature affects evaluation strictness — content valid under "creative" may fail under "strict"
  </constraints>
  <output>
    validation_result: { section_id, passed: bool, criteria: [{id, status, feedback}], missing_info: [], instruction_temperature: string }
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
    <field name="section_id" type="string" required="true">Section identifier (e.g., "1-overview", "4-core-features")</field>
    <field name="content_path" type="string" required="true">Path to validated content file in .x-ipe-checkpoint/</field>
    <field name="split_mode" type="boolean" required="false" default="false">If true, output as standalone sub-markdown file with Instructions and Screenshots sections</field>
  </input>
  <action>
    1. Read the playbook template to get section heading and structure
    2. Read validated content at content_path
    3. **IF section_id is "4-core-features" or "5-common-workflow-scenarios":**
       a. Create subfolder: `04-core-features/` or `05-common-workflows/`
       b. Parse content to identify individual features/workflows (split on H3 headings or feature boundaries)
       c. For each feature/workflow item:
          - Create individual file: `feature{nn}-{slug}.md` or `workflow{nn}-{slug}.md`
          - Number sequentially starting at 01
          - Slug derived from feature/workflow name (lowercase, hyphens)
          - Structure: H1 heading with number and name → content sections per playbook template
       d. Create `_index.md` with table listing all items and cross-links
       e. Create `screenshots/` subfolder; move item-specific screenshots there
       f. Return list of created file paths
    4. ELSE IF split_mode is true:
       a. Create standalone sub-markdown file with naming convention: {nn}-{section-slug}.md
       b. Structure: H1 heading → ## Instructions → ## Content → ## Screenshots (optional)
       c. Instructions section explains what this section covers and how to use it
       d. Screenshots section includes references to images in screenshots/ subfolder
    5. ELSE (split_mode is false):
       a. Format content under proper H2 heading with consistent style
       b. Apply section numbering from playbook
       c. Ensure subsection headings use H3
       d. Wrap code examples in fenced code blocks
       e. Normalize list formatting
    6. Apply instruction_temperature to instructional content and examples:
       - **strict:** Exact source phrasing. Mark `[placeholder]` values. Uniform "Step N: [Action] [Element] → [Expected]" pattern.
       - **balanced:** Natural, grounded instructions. Realistic examples. Light paraphrasing OK.
       - **creative:** Engaging, descriptive. Inventive scenarios. Add "why" explanations and exploration tips.
    7. Return formatted section ready for assembly
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: Do not alter factual content — only apply formatting
    - CRITICAL: Sections 4 and 5 ALWAYS use subfolder output with per-item files, regardless of split_mode
    - CRITICAL: Feature files use `feature{nn}-{slug}.md` naming; workflow files use `workflow{nn}-{slug}.md`
    - CRITICAL: Each subfolder MUST have `_index.md` and `screenshots/` subfolder
    - CRITICAL: All screenshot images MUST be placed in the section's screenshots/ subfolder
  </constraints>
  <output>Formatted markdown section (inline, sub-file path, or subfolder path) ready for final assembly</output>
</operation>
```

### Operation: score_quality

**When:** Extractor Phase 5 requests quality assessment for a section.

```xml
<operation name="score_quality">
  <action>
    1. Read content at content_path for the given section_id
    2. Load acceptance criteria for the section from templates/acceptance-criteria.md
    3. Evaluate content across 5 quality dimensions:
       a. **Completeness** (0.0–1.0): ratio of REQ criteria satisfied
       b. **Structure** (0.0–1.0): proper heading hierarchy, code blocks, lists
       c. **Clarity** (0.0–1.0): actionable instructions, concrete examples present
       d. **Followability** (0.0–1.0): can instructions be followed literally without guessing?
          - Each step has explicit action verb (click, type, press, wait, select)
          - Each step has expected outcome
          - No implicit knowledge between steps
          - Async operations have completion indicators
          - Different interaction patterns (modal vs CLI dispatch) are clearly distinguished
       e. **Freshness** (0.0–1.0): content references current versions, no stale info
    4. Apply section-aware weighting:
       - **Sections 4 (Core Features) and 5 (Common Workflow Scenarios):**
         Weighted mean: completeness 0.25, structure 0.10, clarity 0.30, followability 0.25, freshness 0.10
       - **Section 3 (Getting Started):**
         Weighted mean: completeness 0.25, structure 0.10, clarity 0.25, followability 0.30, freshness 0.10
         (followability weighted highest — getting started MUST be literally followable)
       - **All other sections:**
         Weighted mean: completeness 0.35, structure 0.20, clarity 0.25, followability 0.10, freshness 0.10
    5. Adjust scoring thresholds per instruction_temperature:
       - **strict:** Clarity/followability thresholds → 0.75. Penalize paraphrasing (-0.1 clarity) and missing placeholders (-0.1 structure).
       - **balanced:** Standard thresholds (0.6 default).
       - **creative:** Followability threshold -0.05. No penalty for stylistic variation. +0.05 clarity bonus for "why" explanations.
    6. Generate improvement_hints[] for any dimension below threshold (adjusted per temperature)
    7. **For sections 3, 4, and 5:** Apply critical-but-constructive feedback mode:
       a. Be MORE specific in improvement_hints (name exact missing subsections, features, or scenarios)
       b. Lower the "acceptable" threshold: score < 0.70 → generate hints (not just < 0.60)
       c. If instructions are vague or generic → explicitly call out "Instructions lack step-by-step detail"
       d. If no screenshots referenced → hint "No screenshot references found — add for UI features"
       e. If followability < 0.70 → hint "Steps cannot be followed literally — add explicit actions and expected outcomes"
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: Scoring is based on domain expertise — this skill defines what "quality" means for user manuals
    - CRITICAL: Sections 3, 4, and 5 receive stricter evaluation — they are the core value of the manual
  </constraints>
  <output>
    quality_result: { section_id, section_quality_score, dimensions: {completeness, structure, clarity, followability, freshness}, improvement_hints[], is_key_section: bool, instruction_temperature: string }
  </output>
</operation>
```

### Operation: test_walkthrough

**When:** After extraction and validation are complete, test if the manual can actually be followed.

```xml
<operation name="test_walkthrough">
  <action>
    1. Read the scenario/walkthrough from the manual at content_path
    2. Parse each numbered step into discrete actions
    3. For each step, classify the expected interaction:
       - CLICK: click a button/link (element name specified)
       - FILL: type into an input field (field name + value specified)
       - DISPATCH: send command to terminal (command + "press Enter" specified)
       - WAIT: wait for a state change (expected outcome specified)
       - VERIFY: check that UI state matches description
    4. Apply instruction_temperature-aware walkthrough strictness:
       - **strict:** Every step MUST have explicit element name, action verb, and expected outcome. ANY ambiguity → FAIL.
       - **balanced:** Standard walkthrough. Accept minor implicit knowledge if context is clear.
       - **creative:** Relax element naming. Accept descriptive references ("the main button") if unambiguous in context.
    5. IF app_url is provided AND Chrome DevTools MCP is available:
       a. Navigate to app_url
       b. For each step: take_snapshot → find matching element → perform action → take_snapshot → verify expected outcome
       c. Record step results: {step_number, action, expected, actual, passed: bool}
    6. IF app_url is NOT available (offline validation):
       a. For each step, verify:
          - Step specifies exact UI element or exact command
          - Step includes explicit user action verb (click, type, press Enter, wait)
          - Step includes expected outcome ("you should see...")
          - No implicit knowledge assumed between consecutive steps
       b. Record: {step_number, has_element: bool, has_action: bool, has_outcome: bool, has_gap: bool}
    7. Compute followability_score = steps_passed / steps_total
    8. Generate gap_report — for each failed step, classify the issue:
       - MISSING_ACTION: step doesn't specify what user should do (e.g., no "press Enter", no "click X")
       - MISSING_ELEMENT: step doesn't name the UI element or target
       - MISSING_OUTCOME: step doesn't describe expected result
       - WRONG_STATE: (live mode only) actual UI doesn't match description
       - IMPLICIT_KNOWLEDGE: step assumes knowledge not previously documented
  </action>
  <constraints>
    - CRITICAL: Steps must be followed LITERALLY — do not infer intent
    - CRITICAL: If a step says "generate CLI command" but doesn't say "press Enter to execute" → mark as FAIL with issue_type MISSING_ACTION
    - BLOCKING: content_path is required
    - CRITICAL: instruction_temperature adjusts evaluation strictness — "strict" is more rigorous than "creative"
  </constraints>
  <output>
    walkthrough_result: { scenario_id, steps_total, steps_passed, steps_failed, followability_score, gap_report: [{step, issue_type, issue, suggestion}], instruction_temperature: string }
  </output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "get_artifacts | get_collection_template | validate_section | get_mixin | pack_section | score_quality | test_walkthrough"
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
      instruction_temperature: "string"  # temperature used for evaluation thresholds
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
        followability: 0.0
        freshness: 0.0
      improvement_hints: ["string"]
      is_key_section: false  # true for sections 3, 4, and 5 (stricter evaluation)
      instruction_temperature: "string"  # temperature used for scoring thresholds
    # test_walkthrough
    walkthrough_result:
      scenario_id: "{id}"
      steps_total: 0
      steps_passed: 0
      steps_failed: 0
      followability_score: 0.0  # 0.0–1.0
      gap_report: [{ step: 0, issue: "string", suggestion: "string" }]
      instruction_temperature: "string"  # temperature used for walkthrough strictness
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
| `INVALID_OPERATION` | operation not one of the 7 defined | Check operation name matches exactly |
| `MISSING_SECTION_ID` | section_id null for validate/pack/score_quality | Provide section_id matching playbook template |
| `MISSING_CONTENT_PATH` | content_path null for validate/pack/score_quality/test_walkthrough | Provide path to extracted content file |
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
