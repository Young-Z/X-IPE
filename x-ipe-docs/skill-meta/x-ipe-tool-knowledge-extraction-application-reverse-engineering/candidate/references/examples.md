# Usage Examples — Application Reverse Engineering Orchestrator (v2.0)

> Examples showing how the orchestrator dispatches to sub-skills and coordinates phased extraction.

---

## Example 1: Full Orchestration Flow (TypeScript Monorepo)

```yaml
# Scenario: Reverse engineering a TypeScript monorepo (11K files, 86K LOC)

# ── Step 1: Discover available sub-skills ──
Orchestrator: discover_sub_skills()
→ {
    sub_skills: [
      { name: "x-ipe-tool-rev-eng-code-structure-analysis", section_id: 5, phase: "1-Scan", has_extract: true },
      { name: "x-ipe-tool-rev-eng-technology-stack",        section_id: 7, phase: "1-Scan", has_extract: true },
      { name: "x-ipe-tool-rev-eng-test-analysis",           section_id: 8, phase: "2-Tests", has_extract: true },
      { name: "x-ipe-tool-rev-eng-architecture-recovery",   section_id: 1, phase: "3-Deep", has_extract: true },
      { name: "x-ipe-tool-rev-eng-design-pattern-detection",section_id: 2, phase: "3-Deep", has_extract: true },
      { name: "x-ipe-tool-rev-eng-api-contract-extraction", section_id: 3, phase: "3-Deep", has_extract: true },
      { name: "x-ipe-tool-rev-eng-dependency-analysis",     section_id: 4, phase: "3-Deep", has_extract: true },
      { name: "x-ipe-tool-rev-eng-data-flow-analysis",      section_id: 6, phase: "3-Deep", has_extract: true }
    ]
  }

# ── Step 2: Apply cross-cutting mixins ──
Orchestrator: get_mixin(mixin_key="monorepo")
→ { overlay: cross-package analysis prompts, per-package module view, workspace analysis }

Orchestrator: get_mixin(mixin_key="typescript")
→ { overlay: TypeScript-specific detection prompts, tsconfig analysis }

# ── Step 3: Execute orchestrate_phases (full 3-phase run) ──
Orchestrator: orchestrate_phases(
    repo_path="/workspace/openclaw",
    output_path=".intake/openclaw-rev-eng/"
)

# ── Phase 1: Scan (parallel dispatch) ──
# Dispatches sections 5 and 7 simultaneously:

  dispatch_section(section_id=5, repo_path="/workspace/openclaw",
    output_path=".intake/openclaw-rev-eng/section-05-code-structure-analysis/")
  → { section_path: ".intake/.../section-05-.../", quality_score: 0.89, success: true }

  dispatch_section(section_id=7, repo_path="/workspace/openclaw",
    output_path=".intake/openclaw-rev-eng/section-07-technology-stack/")
  → { section_path: ".intake/.../section-07-.../", quality_score: 0.92, success: true }

# phase1_results = {
#   "5": { path: "section-05-.../", quality: 0.89, modules: [...], directories: [...] },
#   "7": { path: "section-07-.../", quality: 0.92, technologies: [...], frameworks: [...] }
# }

# ── Phase 2: Tests (depends on Phase 1) ──
# Phase 1 scan results passed as context so test analysis knows project structure:

  dispatch_section(section_id=8, repo_path="/workspace/openclaw",
    output_path=".intake/openclaw-rev-eng/section-08-source-code-tests/",
    section_context={ phase1_results: { "5": ..., "7": ... } })
  → { section_path: ".intake/.../section-08-.../", quality_score: 0.85, success: true,
      metadata: { tests_collected: 3293, tests_executed: 421, coverage: 0.78 } }

# phase2_results = {
#   "8": { path: "section-08-.../", quality: 0.85, test_insights: {...}, coverage_map: {...} }
# }

# ── Phase 3: Deep Analysis (parallel, depends on Phase 1+2) ──
# All Phase 1+2 results passed as context:

  dispatch_section(section_id=1, ..., section_context={ phase1_results, phase2_results })
  → { quality_score: 0.93, success: true }   # Architecture Recovery

  dispatch_section(section_id=2, ..., section_context={ phase1_results, phase2_results })
  → { quality_score: 0.91, success: true }   # Design Pattern Detection

  dispatch_section(section_id=3, ..., section_context={ phase1_results, phase2_results })
  → { quality_score: 0.88, success: true }   # API Contract Extraction

  dispatch_section(section_id=4, ..., section_context={ phase1_results, phase2_results })
  → { quality_score: 0.90, success: true }   # Dependency Analysis

  dispatch_section(section_id=6, ..., section_context={ phase1_results, phase2_results })
  → { quality_score: 0.87, success: true }   # Data Flow Analysis

# ── Step 4: Post-extraction (orchestrator cross-section work) ──

Orchestrator: generate_index(output_path=".intake/openclaw-rev-eng/")
→ { index_path: ".intake/openclaw-rev-eng/index.md" }
# Generated index.md:
#   | # | Section                | Quality | Lines | Description                    |
#   |---|------------------------|---------|-------|--------------------------------|
#   | 1 | Architecture Recovery  | 0.93    | 1375  | 4-level architecture recovery  |
#   | 2 | Design Patterns        | 0.91    | 1528  | 42 patterns with evidence      |
#   | 5 | Code Structure         | 0.89    | 890   | Project layout + modules       |
#   ...
#   Reading Order: 5 → 7 → 1 → 6 → 2 → 3 → 4 → 8

Orchestrator: aggregate_quality()
→ {
    overall_score: 0.896,
    classification: "HIGH",
    section_scores: {
      "1": { score: 0.93, weight: 0.15, weighted: 0.1395 },
      "2": { score: 0.91, weight: 0.15, weighted: 0.1365 },
      "3": { score: 0.88, weight: 0.10, weighted: 0.0880 },
      "4": { score: 0.90, weight: 0.10, weighted: 0.0900 },
      "5": { score: 0.89, weight: 0.10, weighted: 0.0890 },
      "6": { score: 0.87, weight: 0.15, weighted: 0.1305 },
      "7": { score: 0.92, weight: 0.10, weighted: 0.0920 },
      "8": { score: 0.85, weight: 0.15, weighted: 0.1275 }
    },
    weakest_sections: []  # all above 0.70
  }

Orchestrator: validate_cross_references()
→ {
    total_references: 127,
    valid_references: 119,
    invalid_references: 8,
    consistency_score: 0.937,
    issues: [
      { source_section: 1, target_section: 5, claim: "analytics-engine module",
        issue: "Referenced in architecture but not found in code structure scan",
        severity: "warning" },
      { source_section: 4, target_section: 7, claim: "Redis 7.2",
        issue: "Dependency declares redis==6.2.0 but tech stack says 7.2",
        severity: "error" }
    ]
  }

# Final output:
# .intake/openclaw-rev-eng/
# ├── index.md                    ← Master TOC with quality scores
# ├── section-01-.../             ← 8 section subfolders from sub-skills
# ├── section-02-.../
# ├── ...
# ├── extraction_report.md        ← Timing, phases, quality summary
# └── cross-reference-validation.md ← 8 issues flagged
```

---

## Example 2: Partial Extraction with Missing Sub-Skill

```yaml
# Scenario: Python single-module API service.
# The x-ipe-tool-rev-eng-data-flow-analysis sub-skill is not installed.

# ── Step 1: Discover — one sub-skill missing ──
Orchestrator: discover_sub_skills()
→ {
    sub_skills: [
      { name: "x-ipe-tool-rev-eng-code-structure-analysis", section_id: 5, phase: "1-Scan" },
      { name: "x-ipe-tool-rev-eng-technology-stack",        section_id: 7, phase: "1-Scan" },
      { name: "x-ipe-tool-rev-eng-test-analysis",           section_id: 8, phase: "2-Tests" },
      { name: "x-ipe-tool-rev-eng-architecture-recovery",   section_id: 1, phase: "3-Deep" },
      { name: "x-ipe-tool-rev-eng-design-pattern-detection",section_id: 2, phase: "3-Deep" },
      { name: "x-ipe-tool-rev-eng-api-contract-extraction", section_id: 3, phase: "3-Deep" },
      { name: "x-ipe-tool-rev-eng-dependency-analysis",     section_id: 4, phase: "3-Deep" }
      # NOTE: section 6 (data-flow-analysis) NOT discovered
    ]
  }

# ── Step 2: Mixins ──
Orchestrator: get_mixin(mixin_key="single-module")
→ { overlay: single-module structural analysis }

Orchestrator: get_mixin(mixin_key="python")
→ { overlay: Python-specific detection, pyproject.toml parsing, pytest fixtures }

# ── Step 3: Orchestrate — partial run ──
Orchestrator: orchestrate_phases(
    repo_path="/workspace/my-api",
    output_path=".intake/my-api-rev-eng/"
)

# Phase 1: sections 5, 7 → both succeed
# Phase 2: section 8 → succeeds (with phase1 context)
# Phase 3: sections 1, 2, 3, 4 → succeed; section 6 → SKIPPED (no sub-skill)

# ── Step 4: Quality reflects missing section ──
Orchestrator: aggregate_quality()
→ {
    overall_score: 0.761,
    classification: "ACCEPTABLE",
    section_scores: {
      "1": { score: 0.88, weight: 0.15, weighted: 0.132 },
      "2": { score: 0.85, weight: 0.15, weighted: 0.128 },
      "3": { score: 0.82, weight: 0.10, weighted: 0.082 },
      "4": { score: 0.84, weight: 0.10, weighted: 0.084 },
      "5": { score: 0.90, weight: 0.10, weighted: 0.090 },
      "6": { score: 0.00, weight: 0.15, weighted: 0.000 },  # ← missing, drags score
      "7": { score: 0.91, weight: 0.10, weighted: 0.091 },
      "8": { score: 0.79, weight: 0.15, weighted: 0.119 }
    },
    weakest_sections: [
      { section_id: 6, score: 0.0,
        hints: ["Sub-skill x-ipe-tool-rev-eng-data-flow-analysis not installed. Install to complete extraction."] }
    ]
  }

# ── Cross-references still run on available sections ──
Orchestrator: validate_cross_references()
→ {
    total_references: 89,
    valid_references: 84,
    invalid_references: 5,
    consistency_score: 0.944,
    issues: [
      { source_section: 1, target_section: 6,
        claim: "Data flow references in architecture",
        issue: "Section 6 missing — cannot validate data flow claims",
        severity: "info" }
    ]
  }

# Final output (7 of 8 sections):
# .intake/my-api-rev-eng/
# ├── index.md                           ← Notes section 6 as missing
# ├── section-01-architecture-recovery/
# ├── section-02-design-patterns/
# ├── section-03-api-contracts/
# ├── section-04-dependency-analysis/
# ├── section-05-code-structure-analysis/
# ├── section-07-technology-stack/
# ├── section-08-source-code-tests/
# │   └── tests/                         ← Executable pytest files
# ├── extraction_report.md
# └── cross-reference-validation.md
# (no section-06-data-flow/ — sub-skill not available)
```
