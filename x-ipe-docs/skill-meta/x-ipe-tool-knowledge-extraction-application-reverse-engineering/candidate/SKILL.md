---
name: x-ipe-tool-knowledge-extraction-application-reverse-engineering
version: "1.0"
description: Provides playbook, collection template, acceptance criteria, and two-dimension mixins (repo-type × language-type) for application reverse engineering knowledge extraction. Loaded by x-ipe-task-based-application-knowledge-extractor during Phase 1. Triggers on category "application-reverse-engineering".
categories:
  - "application-reverse-engineering"
---

# Knowledge Extraction — Application Reverse Engineering

## Purpose

AI Agents follow this skill to provide application reverse engineering extraction artifacts:
1. Base playbook template defining 8-section phased extraction layout
2. Collection template with per-section extraction prompts and source priority
3. Acceptance criteria for validating extracted content
4. Two-dimension mixins (repo-type × language-type) for codebase-specific overlays

---

## Important Notes

BLOCKING: This is a **tool skill** — it provides templates and validation only. The extraction process is driven by `x-ipe-task-based-application-knowledge-extractor`.
CRITICAL: All template files MUST exist at the paths declared in `get_artifacts` output. The extractor verifies existence before proceeding.
CRITICAL: **Mixin composition order matters.** Repo-type mixin is applied first (primary structural overlay). Language-type mixins are merged on top (additive). Only one repo-type, but multiple language-types may apply.

---

## About

This skill is a template provider for the Application Knowledge Extractor. When the extractor receives a `purpose: "application-reverse-engineering"` request, it discovers this skill by globbing `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md` and matching `categories: ["application-reverse-engineering"]` in the frontmatter.

**Key Concepts:**
- **Playbook Template** — Defines 8 extraction sections in 3 phases: Scan (5, 7), Tests (8), Deep (1, 2, 3, 4, 6)
- **Collection Template** — Per-section extraction prompts with HTML comments guiding source analysis
- **Acceptance Criteria** — Validation rules per section with `[REQ]`/`[OPT]` markers
- **Repo-Type Mixin** — Structural overlay for monorepo, multi-module, single-module, or microservices
- **Language-Type Mixin** — Additive overlay for Python, Java, JavaScript, TypeScript, or Go
- **Complexity Gate** — Minimum thresholds (≥10 files, ≥500 LOC, ≥3 dirs) before extraction proceeds
- **Quality Scoring** — 6-dimension weighted scoring with 3 section-specific weight profiles
- **Mixin Composition** — Repo-type applied first (primary, only one); language-type merged on top (additive, may be multiple)

---

## When to Use

```yaml
triggers:
  - "application reverse engineering extraction"
  - "category: application-reverse-engineering"
  - "reverse engineer source code"
  - "extract architecture from codebase"

not_for:
  - "User manual extraction" → use x-ipe-tool-knowledge-extraction-user-manual
  - "Direct README update" → use x-ipe-tool-readme-updator
```

---

## Input Parameters

```yaml
input:
  operation: "get_artifacts | get_collection_template | validate_section | get_mixin | pack_section | score_quality | test_walkthrough"
  category: "application-reverse-engineering"
  section_id: "string | null"          # e.g., "1-architecture-recovery", "5-code-structure-analysis"
  content_path: "string | null"        # Path to extracted content file
  mixin_key: "string | null"           # e.g., "monorepo", "python" — used by get_mixin
  repo_path: "string | null"           # Path to target repo — used by test_walkthrough
  config:
    max_files_per_section: 30
    complexity_gate:
      min_files: 10
      min_loc: 500
      min_dirs: 3
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />
  <field name="category" source="Always 'application-reverse-engineering' for this skill" />

  <field name="section_id" source="Caller provides section identifier">
    <steps>
      1. Required for validate_section, pack_section, and score_quality operations
      2. Must match an H2 slug from playbook template (e.g., "1-architecture-recovery", "8-source-code-tests")
    </steps>
  </field>

  <field name="content_path" source="Caller provides path to extracted content in .x-ipe-checkpoint/">
    <steps>
      1. Path must exist and be readable
      2. Content must be UTF-8 markdown
    </steps>
  </field>

  <field name="mixin_key" source="Caller specifies mixin identifier for get_mixin">
    <steps>
      1. Must be one of: monorepo, multi-module, single-module, microservices (repo-type)
         OR: python, java, javascript, typescript, go (language-type)
      2. IF null and operation is get_mixin → return error INVALID_MIXIN_KEY
    </steps>
  </field>

  <field name="repo_path" source="Caller provides path to target repository">
    <steps>
      1. Optional — only used by test_walkthrough operation
      2. IF provided → source-code verification mode (glob, grep, import tracing)
      3. IF null → offline structural validation only
    </steps>
  </field>

  <field name="config" source="Caller provides or uses defaults">
    <steps>
      1. max_files_per_section defaults to 30
      2. complexity_gate defaults to { min_files: 10, min_loc: 500, min_dirs: 3 }
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
    <name>Content file exists (for validate/pack/score)</name>
    <verification>IF operation is validate_section, pack_section, or score_quality THEN content_path file exists</verification>
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
    2. Return repo-type mixin paths:
       - repo_type_mixins.monorepo: templates/mixin-monorepo.md
       - repo_type_mixins.multi_module: templates/mixin-multi-module.md
       - repo_type_mixins.single_module: templates/mixin-single-module.md
       - repo_type_mixins.microservices: templates/mixin-microservices.md
    3. Return language-type mixin paths:
       - language_type_mixins.python: templates/mixin-python.md
       - language_type_mixins.java: templates/mixin-java.md
       - language_type_mixins.javascript: templates/mixin-javascript.md
       - language_type_mixins.typescript: templates/mixin-typescript.md
       - language_type_mixins.go: templates/mixin-go.md
    4. Return config defaults:
       - max_files_per_section: 30
       - complexity_gate: { min_files: 10, min_loc: 500, min_dirs: 3 }
  </action>
  <output>
    artifact_paths object with playbook_template, collection_template,
    acceptance_criteria, repo_type_mixins map, language_type_mixins map, config_defaults
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
    4. Each section contains HTML comments with EXTRACTION PROMPTS, SOURCE PRIORITY, and PHASE CONTEXT
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
       a. For each checklist item, check if content satisfies the rule
       b. Mark as PASS, FAIL, or INCOMPLETE with brief feedback
    5. IF any REQ criterion fails due to insufficient source material (not poor writing):
       a. Mark criterion as INCOMPLETE (distinct from FAIL)
       b. Add to missing_info[] with description of what content is needed
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

**When:** Extractor needs codebase-specific extraction prompts (repo-type or language-type).

```xml
<operation name="get_mixin">
  <action>
    1. Resolve mixin file from mixin_key:
       Repo-type: monorepo → templates/mixin-monorepo.md
                  multi-module → templates/mixin-multi-module.md
                  single-module → templates/mixin-single-module.md
                  microservices → templates/mixin-microservices.md
       Language-type: python → templates/mixin-python.md
                      java → templates/mixin-java.md
                      javascript → templates/mixin-javascript.md
                      typescript → templates/mixin-typescript.md
                      go → templates/mixin-go.md
    2. Read and return the mixin template content
    3. Mixin contains detection signals, additional sections, and section overlay prompts
  </action>
  <constraints>
    - BLOCKING: mixin_key is required and must be one of the 9 valid keys
  </constraints>
  <output>Mixin markdown content with detection signals and overlay prompts</output>
</operation>
```

### Operation: pack_section

**When:** Extractor packs validated content into final output format.

```xml
<operation name="pack_section">
  <action>
    1. Read the playbook template to get section heading, phase, and output type
    2. Read validated content at content_path
    3. IF output type is "subfolder" (sections 1, 2, 3, 4, 6, 8):
       a. Create subfolder: section-{nn}-{section-slug}/
       b. Parse content to identify logical units (split on H3 headings)
       c. Create individual files per logical unit
       d. Create _index.md with summary table
       e. Create screenshots/ subfolder for diagrams
       f. Return list of created file paths
    4. IF output type is "inline" (sections 5, 7):
       a. Format content under proper H2 heading with Markdown tables
       b. Apply section numbering from playbook
       c. Normalize list and code block formatting
    5. Return formatted section ready for assembly
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: Do not alter factual content — only apply formatting
    - CRITICAL: Sections with subfolder output MUST have _index.md and screenshots/
    - CRITICAL: Section 8 additionally has tests/ subfolder for executable test files
  </constraints>
  <output>Formatted markdown section (inline or subfolder path) ready for final assembly</output>
</operation>
```

### Operation: score_quality

**When:** Extractor requests quality assessment for a section.

```xml
<operation name="score_quality">
  <action>
    1. Read content at content_path for the given section_id
    2. Load acceptance criteria for the section from templates/acceptance-criteria.md
    3. Evaluate content across 6 quality dimensions:
       a. Completeness (0.0–1.0): ratio of [REQ] criteria satisfied
       b. Structure (0.0–1.0): proper heading hierarchy, diagrams, tables
       c. Clarity (0.0–1.0): clear explanations, concrete examples
       d. Accuracy (0.0–1.0): evidence-backed claims, verified against code
       e. Freshness (0.0–1.0): references current versions, no stale info
       f. Coverage (0.0–1.0): breadth of code-evidence across modules
    4. Apply section-aware weighting (see Weight Tables below)
    5. Generate improvement_hints[] for any dimension below 0.6
  </action>
  <constraints>
    - BLOCKING: section_id and content_path are required
    - CRITICAL: This skill defines what "quality" means for reverse engineering output
  </constraints>
  <output>
    quality_result: { section_id, section_quality_score, dimensions: {completeness, structure, clarity, accuracy, freshness, coverage}, improvement_hints[] }
  </output>
</operation>
```

#### Quality Scoring Weight Tables

**Architecture Sections** (1-Architecture Recovery, 2-Design Patterns, 6-Data Flow):

| Dimension | Weight |
|-----------|--------|
| Completeness | 0.20 |
| Structure | 0.10 |
| Clarity | 0.15 |
| **Accuracy** | **0.35** |
| Freshness | 0.10 |
| Coverage | 0.10 |

**Tests Section** (8-Source Code Tests):

| Dimension | Weight |
|-----------|--------|
| Completeness | 0.10 |
| Structure | 0.05 |
| Clarity | 0.10 |
| Accuracy | 0.15 |
| Freshness | 0.10 |
| **Coverage** | **0.50** |

**Other Sections** (3-API Contracts, 4-Dependencies, 5-Code Structure, 7-Tech Stack):

| Dimension | Weight |
|-----------|--------|
| **Completeness** | **0.30** |
| Structure | 0.20 |
| Clarity | 0.20 |
| Accuracy | 0.15 |
| Freshness | 0.10 |
| Coverage | 0.05 |

### Operation: test_walkthrough

**When:** After extraction complete, verify extracted claims against the actual codebase.

```xml
<operation name="test_walkthrough">
  <action>
    1. Read extracted knowledge from content_path (all 8 sections)
    2. Parse verifiable claims and classify each:
       - module_exists: glob for module path, check import references
       - pattern_detected: locate cited file:line, confirm structural match
       - api_contract: find function/class, check signature matches
       - dependency_link: trace import chain, confirm A imports/calls B
       - tech_stack_item: check config files, confirm version matches
    3. IF repo_path is provided (source-code verification mode):
       a. For each claim: navigate to repo_path, perform verification method
       b. Cross-check with Phase 2 test knowledge (test imports, mocks, assertions)
       c. Record: {claim_id, type, expected, actual, verified: bool}
    4. IF repo_path is NOT available (offline validation):
       a. For each claim: verify it cites specific file paths or code references
       b. Check evidence is concrete (file:line, not vague descriptions)
       c. Record: {claim_id, has_evidence: bool, evidence_quality: high|medium|low}
    5. Compute verification_score = claims_verified / claims_total
    6. Generate unverified_claims[] for each failed claim
  </action>
  <constraints>
    - CRITICAL: Claims must be verified against actual code — do not trust descriptions alone
    - BLOCKING: content_path is required
  </constraints>
  <output>
    walkthrough_result: { claims_total, claims_verified, claims_failed, verification_score, unverified_claims: [{claim_id, type, issue, suggestion}] }
  </output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "{one of the 7 operations}"
  result:
    artifact_paths:          # get_artifacts — includes playbook, collection, AC, repo_type_mixins (4), language_type_mixins (5), config_defaults
    validation_result:       # validate_section — { section_id, passed, criteria: [{id, status, feedback}], missing_info[] }
    formatted_content:       # pack_section — formatted markdown or subfolder path
    quality_result:          # score_quality — { section_id, section_quality_score, dimensions: {6 dims}, improvement_hints[] }
    walkthrough_result:      # test_walkthrough — { claims_total, claims_verified, verification_score, unverified_claims[] }
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
| `MISSING_SECTION_ID` | section_id null for validate/pack/score | Provide section_id matching playbook template |
| `MISSING_CONTENT_PATH` | content_path null for validate/pack/score/walkthrough | Provide path to extracted content file |
| `CONTENT_NOT_FOUND` | content_path file does not exist | Verify file was written by extractor |
| `INVALID_MIXIN_KEY` | mixin_key not one of the 9 valid keys | Use one of: monorepo, multi-module, single-module, microservices, python, java, javascript, typescript, go |
| `TEMPLATE_NOT_FOUND` | Template file missing from skill | Re-install skill or verify file paths |
| `BELOW_COMPLEXITY_GATE` | Codebase below min thresholds | Skip reverse engineering; document rationale |
| `SCORING_FAILED` | Unable to evaluate content quality | Verify content exists and is readable |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/playbook-template.md` | 8-section phased playbook (Scan → Tests → Deep) |
| `templates/collection-template.md` | Per-section extraction prompts with source priority |
| `templates/acceptance-criteria.md` | Per-section validation rules with [REQ]/[OPT] markers |
| `templates/mixin-monorepo.md` | Repo-type: monorepo structural overlay |
| `templates/mixin-multi-module.md` | Repo-type: multi-module structural overlay |
| `templates/mixin-single-module.md` | Repo-type: single-module structural overlay |
| `templates/mixin-microservices.md` | Repo-type: microservices structural overlay |
| `templates/mixin-python.md` | Language-type: Python analysis overlay |
| `templates/mixin-java.md` | Language-type: Java analysis overlay |
| `templates/mixin-javascript.md` | Language-type: JavaScript analysis overlay |
| `templates/mixin-typescript.md` | Language-type: TypeScript analysis overlay |
| `templates/mixin-go.md` | Language-type: Go analysis overlay |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-knowledge-extraction-application-reverse-engineering/references/examples.md) for usage examples.
