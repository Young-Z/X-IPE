---
name: x-ipe-tool-knowledge-extraction-application-reverse-engineering
version: "2.0"
description: >
  Orchestrator for application reverse engineering knowledge extraction.
  Dynamically discovers section-specific sub-skills, coordinates 3-phase
  execution (Scan → Tests → Deep), generates the master index, aggregates
  quality scores, and validates cross-references. Retains cross-cutting
  mixin templates (repo-type × language-type).
---

# Knowledge Extraction — Application Reverse Engineering (Orchestrator)

## Purpose

AI Agents follow this skill to orchestrate application reverse engineering extraction:
1. **Discover** section-specific sub-skills dynamically (glob pattern)
2. **Dispatch** extraction work to sub-skills in 3 phases with dependency passing
3. **Collect** results and generate master index.md (LL-001)
4. **Aggregate** quality scores across all sections
5. **Validate** cross-section consistency
6. Provide cross-cutting **mixin templates** (repo-type × language-type)

---

## Important Notes

BLOCKING: This is an **orchestrator skill** — it dispatches to sub-skills, not a monolithic template provider.
CRITICAL: Sub-skills are discovered dynamically via glob. Do NOT hardcode sub-skill names or paths.
CRITICAL: Phase dependencies are strict: Phase 2 receives Phase 1 output; Phase 3 receives Phase 1+2 output.
CRITICAL: Mixin composition order: repo-type first (primary), language-type merged on top (additive, may be multiple).

---

## About

This skill orchestrates the full application reverse engineering extraction by discovering
and dispatching to 8 section-specific sub-skills. The extractor (`x-ipe-task-based-application-knowledge-extractor`)
invokes this orchestrator, which coordinates the 3-phase execution.

**Key Concepts:**
- **Sub-Skill Discovery** — Glob `.github/skills/x-ipe-tool-rev-eng-*/SKILL.md`, parse frontmatter
- **3-Phase Execution** — Phase 1 (Scan: 5, 7) → Phase 2 (Tests: 8) → Phase 3 (Deep: 1, 2, 3, 4, 6)
- **Context Passing** — Phase 1 feeds Phase 2; Phase 1+2 feed Phase 3
- **Master Index** — TOC with quality scores, reading order (LL-001)
- **Quality Aggregation** — Weighted scores rolled up into overall score
- **Cross-Reference Validation** — Cross-section consistency checks
- **Mixin Templates** — Cross-cutting repo-type and language-type overlays

**Phases:** `P1 (∥ 5,7) → P2 (8, needs P1) → P3 (∥ 1,2,3,4,6, needs P1+P2)`

---

## When to Use

```yaml
triggers:
  - "application reverse engineering extraction"
  - "category: application-reverse-engineering"
  - "reverse engineer source code"
  - "extract architecture from codebase"
  - "orchestrate reverse engineering"

not_for:
  - "Single section extraction" → invoke sub-skill directly
  - "User manual extraction" → use x-ipe-tool-knowledge-extraction-user-manual
  - "Direct README update" → use x-ipe-tool-readme-updator
```

---

## Input Parameters

```yaml
input:
  operation: "discover_sub_skills | dispatch_section | orchestrate_phases | get_mixin | generate_index | aggregate_quality | validate_cross_references"
  category: "application-reverse-engineering"
  section_id: "integer | null"                # 1–8, for dispatch_section
  repo_path: "string"                         # Target repository (required for orchestrate/dispatch)
  output_path: "string"                       # .intake/{extraction_id}/ (required for orchestrate/generate/validate)
  mixin_key: "string | null"                  # e.g., "monorepo", "python" (required for get_mixin)
  section_context:                            # Built during phase execution
    phase1_output: "map | null"              # Section 5 + 7 output paths
    phase2_output: "map | null"              # Section 8 output path
  config:
    max_files_per_section: 30
    complexity_gate: { min_files: 10, min_loc: 500, min_dirs: 3 }
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Valid operation requested</name>
    <verification>operation matches one of the 7 defined operations</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Sub-skills discoverable</name>
    <verification>Glob .github/skills/x-ipe-tool-rev-eng-*/SKILL.md returns ≥1 result</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Mixin templates exist</name>
    <verification>All mixin files in templates/ are present and readable</verification>
  </checkpoint>
  <checkpoint required="false">
    <name>Repo path valid (for extraction operations)</name>
    <verification>IF orchestrate_phases or dispatch_section THEN repo_path is a directory</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: discover_sub_skills

**When:** First step — discover available sub-skills before dispatching.

```xml
<operation name="discover_sub_skills">
  <action>
    1. Glob: .github/skills/x-ipe-tool-rev-eng-*/SKILL.md
    2. For each matched file:
       a. Parse YAML frontmatter (name, description, section_id, phase)
       b. Verify the skill has an `extract` operation defined
       c. Record: { name, section_id, phase, path, description }
    3. Sort by phase (1-Scan, 2-Tests, 3-Deep), then by section_id
    4. Validate all 3 phases have at least one sub-skill
    5. Return the discovered sub-skill registry
  </action>
  <constraints>
    - BLOCKING: Do NOT hardcode sub-skill names — always discover via glob
    - CRITICAL: Missing sub-skills are warnings, not errors (partial extraction is valid)
  </constraints>
  <output>
    sub_skills: [{ name, section_id, phase, path, description, has_extract: bool }]
  </output>
</operation>
```

### Operation: dispatch_section

**When:** Orchestrator needs to invoke a specific sub-skill for one section.

```xml
<operation name="dispatch_section">
  <action>
    1. Look up section_id in the discovered sub-skill registry
    2. IF no sub-skill found for section_id → return SECTION_NOT_FOUND error
    3. Build invocation context:
       a. repo_path: path to target repository
       b. output_path: {output_path}/section-{nn}-{slug}/
       c. phase1_output: paths from Phase 1 results (if available)
       d. phase2_output: paths from Phase 2 results (if available)
       e. config: complexity_gate, max_files_per_section
    4. Invoke the sub-skill's `extract` operation with the built context
    5. Collect sub-skill output: { section_path, quality_score, metadata }
    6. Return the dispatch result
  </action>
  <constraints>
    - BLOCKING: section_id is required
    - CRITICAL: Phase context MUST be passed — Phase 2 sub-skill needs phase1_output,
      Phase 3 sub-skills need phase1_output + phase2_output
    - CRITICAL: Create output subfolder before invoking sub-skill
  </constraints>
  <output>
    dispatch_result: { section_id, sub_skill_name, section_path, quality_score, success: bool, errors: [] }
  </output>
</operation>
```

### Operation: orchestrate_phases

**When:** Full extraction requested — execute all 3 phases in order.

```xml
<operation name="orchestrate_phases">
  <action>
    1. Run discover_sub_skills to build the registry
    2. Create output directory: {output_path}/
    3. **Phase 1 — Scan (parallel):**
       a. Dispatch sections 5 and 7 in parallel
       b. Collect results: phase1_output = { "5": result_5, "7": result_7 }
       c. IF any Phase 1 section fails → log warning, continue with available results
    4. **Phase 2 — Tests (depends on Phase 1):**
       a. Dispatch section 8 with phase1_output
       b. Collect result: phase2_output = { "8": result_8 }
       c. IF Phase 2 fails → log warning, continue (Phase 3 runs without test context)
    5. **Phase 3 — Deep Analysis (parallel, depends on Phase 1+2):**
       a. Dispatch sections 1, 2, 3, 4, 6 in parallel with phase1_output + phase2_output
       c. Collect results: phase3_results = { "1": result_1, ... "6": result_6 }
    6. Run generate_index with all section results
    7. Run aggregate_quality across all sections
    8. Run validate_cross_references across all sections
    9. Generate extraction_report.md with timing, phase results, quality summary
    10. Return orchestration result
  </action>
  <constraints>
    - BLOCKING: repo_path and output_path are required
    - CRITICAL: Phase ordering is STRICT — Phase 2 MUST wait for Phase 1; Phase 3 MUST wait for Phase 1+2
    - CRITICAL: Within a phase, sections run in parallel (no inter-section dependencies)
    - Partial success is valid: failed sections are logged but don't block others
  </constraints>
  <output>
    orchestration_result: {
      phases: { phase1: { sections, status }, phase2: { sections, status }, phase3: { sections, status } },
      overall_quality: float,
      index_path: string,
      report_path: string,
      cross_ref_path: string,
      errors: []
    }
  </output>
</operation>
```

### Operation: get_mixin

**When:** Extractor needs codebase-specific overlays (repo-type or language-type).

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
    3. Mixin contains detection signals, additional prompts, and section overlays
  </action>
  <constraints>
    - BLOCKING: mixin_key is required and must be one of the 9 valid keys
    - CRITICAL: Composition order — repo-type first (primary), language-type additive
  </constraints>
  <output>Mixin markdown content with detection signals and overlay prompts</output>
</operation>
```

### Operation: generate_index

**When:** After all phases complete — create the master index.md (LL-001).

```xml
<operation name="generate_index">
  <action>
    1. Scan output_path for section-{nn}-{slug}/ subdirectories
    2. For each section subfolder:
       a. Read its index.md for description
       b. Count total lines across all .md files
       c. Retrieve quality score from sub-skill results
    3. Build master index.md at {output_path}/index.md with:
       - App name and overview
       - Section table: number, name (linked), quality score, line count, description
       - Reading order: 5 → 7 → 1 → 6 → 2 → 3 → 4 → 8
       - Extraction metadata: overall quality, phases completed, source path
    4. Return path to generated index
  </action>
  <constraints>
    - BLOCKING: output_path must contain at least one section subfolder
    - CRITICAL: Quality scores must come from actual sub-skill results
  </constraints>
  <output>index_path: string</output>
</operation>
```

### Operation: aggregate_quality

**When:** After all phases complete — compute overall quality score.

```xml
<operation name="aggregate_quality">
  <action>
    1. Collect quality_score from each sub-skill's dispatch result
    2. Apply section-group weighting:
       - Architecture sections (1, 2, 6): weight 0.15 each = 0.45 total
       - Tests section (8): weight 0.15
       - Other sections (3, 4, 5, 7): weight 0.10 each = 0.40 total
    3. Compute weighted_overall = Σ(section_score × section_weight)
    4. Classify:
       - ≥ 0.85 → HIGH
       - ≥ 0.65 → ACCEPTABLE
       - < 0.65 → LOW
    5. Identify weakest sections (below 0.70) with improvement hints
    6. Return aggregated result
  </action>
  <constraints>
    - CRITICAL: Missing sections get score 0.0 (they drag the average down)
    - CRITICAL: Use sub-skill-reported scores — do NOT re-evaluate content
  </constraints>
  <output>
    aggregate_result: {
      overall_score: float,
      classification: "HIGH | ACCEPTABLE | LOW",
      section_scores: { section_id: { score, weight, weighted } },
      weakest_sections: [{ section_id, score, hints: [] }]
    }
  </output>
</operation>
```

### Operation: validate_cross_references

**When:** After all phases complete — check cross-section consistency.

```xml
<operation name="validate_cross_references">
  <action>
    1. Read all section index.md files from output_path
    2. Build reference maps:
       a. modules_declared: from section 5 (Code Structure) — list of modules/directories
       b. tech_declared: from section 7 (Tech Stack) — technologies and versions
       c. tests_declared: from section 8 (Tests) — test files and coverage data
       d. arch_claims: from section 1 (Architecture) — module references, layers
       e. pattern_claims: from section 2 (Design Patterns) — file:line citations
       f. api_claims: from section 3 (API Contracts) — endpoint/module references
       g. dep_claims: from section 4 (Dependencies) — import/call graphs
       h. flow_claims: from section 6 (Data Flow) — module path references
    3. Cross-validate:
       a. Architecture claims reference modules found in code structure (1 ↔ 5)
       b. Design patterns cite files that exist in code structure (2 ↔ 5)
       c. API contracts reference modules from code structure (3 ↔ 5)
       d. Dependencies match imports found in code structure (4 ↔ 5)
       e. Data flows reference modules from code structure (6 ↔ 5)
       f. Deep sections cite test evidence where available (1,2,3,4,6 ↔ 8)
       g. Tech stack versions match dependency declarations (7 ↔ 4)
    4. Generate cross-reference-validation.md at {output_path}/
    5. Return validation summary
  </action>
  <constraints>
    - Missing sections are skipped (validation runs on available sections)
    - CRITICAL: Flag inconsistencies but do NOT auto-correct content
  </constraints>
  <output>
    cross_ref_result: {
      total_references: int,
      valid_references: int,
      invalid_references: int,
      consistency_score: float,
      issues: [{ source_section, target_section, claim, issue, severity }]
    }
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
    sub_skills:              # discover_sub_skills
    dispatch_result:         # dispatch_section
    orchestration_result:    # orchestrate_phases (includes index + quality + cross-refs)
    mixin_content:           # get_mixin
    index_path:              # generate_index
    aggregate_result:        # aggregate_quality
    cross_ref_result:        # validate_cross_references
  errors: []
```

---

## Output Structure

```
.intake/{extraction_id}/
├── index.md                           # Master TOC (LL-001) — generated by orchestrator
├── section-01-architecture-recovery/  # From x-ipe-tool-rev-eng-architecture-recovery
│   ├── index.md
│   └── ...
├── section-02-design-patterns/        # From x-ipe-tool-rev-eng-design-pattern-detection
│   └── ...
├── section-03-api-contracts/          # From x-ipe-tool-rev-eng-api-contract-extraction
│   └── ...
├── section-04-dependency-analysis/    # From x-ipe-tool-rev-eng-dependency-analysis
│   └── ...
├── section-05-code-structure-analysis/ # From x-ipe-tool-rev-eng-code-structure-analysis
│   └── ...
├── section-06-data-flow/              # From x-ipe-tool-rev-eng-data-flow-analysis
│   └── ...
├── section-07-technology-stack/       # From x-ipe-tool-rev-eng-technology-stack
│   └── ...
├── section-08-source-code-tests/      # From x-ipe-tool-rev-eng-test-analysis
│   ├── tests/                         # Executable test files
│   └── ...
├── extraction_report.md               # Generated by orchestrator
└── cross-reference-validation.md      # Generated by orchestrator
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
    <name>Sub-skills discovered dynamically</name>
    <verification>No hardcoded sub-skill list — glob pattern used</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Phase dependencies enforced</name>
    <verification>Phase 2 received Phase 1 output; Phase 3 received Phase 1+2 output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Master index generated (LL-001)</name>
    <verification>index.md exists at output_path with TOC, quality scores, reading order</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Quality aggregated across sections</name>
    <verification>Overall score computed with section-group weighting</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Cross-references validated</name>
    <verification>cross-reference-validation.md exists with consistency results</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | operation not one of the 7 defined | Check operation name matches exactly |
| `NO_SUB_SKILLS_FOUND` | Glob returned zero results | Verify sub-skill folders exist under `.github/skills/x-ipe-tool-rev-eng-*/` |
| `SECTION_NOT_FOUND` | section_id doesn't match any discovered sub-skill | Run discover_sub_skills first; check section_id is 1–8 |
| `MISSING_REPO_PATH` | repo_path null for orchestrate/dispatch | Provide path to target repository |
| `MISSING_OUTPUT_PATH` | output_path null for orchestrate/generate/validate | Provide .intake/{extraction_id}/ path |
| `INVALID_MIXIN_KEY` | mixin_key not one of the 9 valid keys | Use one of: monorepo, multi-module, single-module, microservices, python, java, javascript, typescript, go |
| `PHASE_DEPENDENCY_VIOLATED` | Phase 2/3 invoked without prior phase results | Run phases in order or supply section_context |
| `SUB_SKILL_EXTRACT_FAILED` | Sub-skill returned error | Check sub-skill logs; partial extraction continues |
| `BELOW_COMPLEXITY_GATE` | Codebase below min thresholds | Skip reverse engineering; document rationale |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/playbook-template.md` | Phase order reference (Scan → Tests → Deep) |
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

See [references/examples.md](references/examples.md) for orchestration flow examples.
