# Usage Examples — Application Reverse Engineering

> Examples showing how the Knowledge Extractor interacts with this tool skill.

---

## Example 1: Full Extraction Flow

```yaml
# Step 1: Extractor loads this skill and gets artifact paths
Extractor: get_artifacts()
→ {
    artifact_paths: {
      playbook_template: "templates/playbook-template.md",
      collection_template: "templates/collection-template.md",
      acceptance_criteria: "templates/acceptance-criteria.md",
      repo_type_mixins: {
        monorepo: "templates/mixin-monorepo.md",
        multi_module: "templates/mixin-multi-module.md",
        single_module: "templates/mixin-single-module.md",
        microservices: "templates/mixin-microservices.md"
      },
      language_type_mixins: {
        python: "templates/mixin-python.md",
        java: "templates/mixin-java.md",
        javascript: "templates/mixin-javascript.md",
        typescript: "templates/mixin-typescript.md",
        go: "templates/mixin-go.md"
      },
      config_defaults: {
        max_files_per_section: 30,
        complexity_gate: { min_files: 10, min_loc: 500, min_dirs: 3 }
      }
    }
  }

# Step 2: Extractor detects repo-type and language → applies mixins
Extractor: get_mixin(mixin_key="monorepo")
→ { overlay content: cross-package analysis prompts, additional sections }

Extractor: get_mixin(mixin_key="typescript")
→ { overlay content: TypeScript-specific detection prompts }

Extractor: get_mixin(mixin_key="javascript")
→ { overlay content: JavaScript-specific detection prompts }

# Step 3: Per-section extraction cycle (Phase 1 first)
Extractor: get_collection_template(section_id="5-code-structure-analysis")
→ { extraction prompts for Code Structure section }

# ... extractor analyzes codebase using prompts ...

Extractor: validate_section(section_id="5-code-structure-analysis", content_path=".x-ipe-checkpoint/section-5.md")
→ { passed: true, criteria: [
    { id: "REQ-1", status: "pass", feedback: "Directory tree present" },
    { id: "REQ-2", status: "pass", feedback: "Directory mapping table found" },
    ...
  ], missing_info: [] }

Extractor: pack_section(section_id="5-code-structure-analysis", content_path=".x-ipe-checkpoint/section-5.md")
→ { formatted inline Markdown content }

Extractor: score_quality(section_id="5-code-structure-analysis", content_path=".x-ipe-checkpoint/section-5.md")
→ { section_quality_score: 0.87, dimensions: {
    completeness: 0.90, structure: 0.85, clarity: 0.80,
    accuracy: 0.90, freshness: 1.0, coverage: 0.75
  }, improvement_hints: [] }
```

---

## Example 2: Mixin Composition Order

```yaml
# Scenario: A Python monorepo (e.g., a data platform with multiple packages)

# Step 1: Apply repo-type mixin FIRST (primary overlay)
Extractor: get_mixin(mixin_key="monorepo")
→ Adds: cross-package dependency prompts, per-package module view, workspace analysis

# Step 2: Apply language-type mixin SECOND (additive overlay)
Extractor: get_mixin(mixin_key="python")
→ Adds: Python-specific pattern detection, pyproject.toml parsing, pytest fixtures

# Result: Base templates + monorepo structural analysis + Python-specific prompts
# The monorepo mixin defines HOW to analyze structure.
# The Python mixin adds WHAT to look for in Python code.
```

---

## Example 3: Handling Validation with Incomplete Content

```yaml
# Section 8 (Source Code Tests) — coverage below 80%
Extractor: validate_section(section_id="8-source-code-tests", content_path=".x-ipe-checkpoint/section-8.md")
→ { passed: false, criteria: [
    { id: "REQ-1", status: "pass", feedback: "AAA structure followed" },
    { id: "REQ-2", status: "pass", feedback: "All tests pass" },
    { id: "REQ-3", status: "incomplete", feedback: "Coverage at 62%, below 80% target" },
    { id: "REQ-4", status: "pass", feedback: "Framework matches (pytest)" },
    { id: "REQ-5", status: "pass", feedback: "Source code unmodified" },
    { id: "REQ-6", status: "pass", feedback: "Knowledge mapping documented" }
  ], missing_info: [
    "Coverage gap in modules: auth_service (45%), payment_handler (38%). Generate additional tests for these modules."
  ] }

# Extractor uses missing_info to request more test generation
# After iteration, re-validates until coverage ≥80% or max iterations reached
```

---

## Example 4: Test Walkthrough (Source-Code Verification)

```yaml
# After all 8 sections extracted, verify claims against actual code
Extractor: test_walkthrough(content_path=".x-ipe-checkpoint/all-sections.md", repo_path="/path/to/repo")
→ { 
    claims_total: 47,
    claims_verified: 43,
    claims_failed: 4,
    verification_score: 0.91,
    unverified_claims: [
      { claim_id: "arch-3", type: "module_exists", issue: "Module 'analytics_engine' not found at stated path", suggestion: "Check if module was renamed or moved" },
      { claim_id: "pattern-7", type: "pattern_detected", issue: "Observer pattern at utils/events.py:42 — file exists but no EventEmitter class found", suggestion: "Verify line numbers against current code version" },
      { claim_id: "dep-12", type: "dependency_link", issue: "Claimed auth → billing import not found", suggestion: "Check indirect dependency through shared module" },
      { claim_id: "stack-2", type: "tech_stack_item", issue: "Redis version 7.2 claimed but redis==6.2.0 in requirements.txt", suggestion: "Update version reference" }
    ]
  }
```

---

## Example 5: Quality Scoring with Section-Specific Weights

```yaml
# Architecture section uses accuracy-heavy weights
Extractor: score_quality(section_id="1-architecture-recovery", content_path="...")
→ { section_quality_score: 0.78, dimensions: {
    completeness: 0.85,  # weight 0.20
    structure: 0.90,     # weight 0.10
    clarity: 0.70,       # weight 0.15
    accuracy: 0.72,      # weight 0.35  ← dominant weight
    freshness: 0.95,     # weight 0.10
    coverage: 0.65       # weight 0.10
  }, improvement_hints: [
    "accuracy: 2 architecture claims lack file:line evidence",
    "coverage: Only 3 of 7 modules have detailed component breakdown"
  ] }

# Tests section uses coverage-heavy weights
Extractor: score_quality(section_id="8-source-code-tests", content_path="...")
→ { section_quality_score: 0.71, dimensions: {
    completeness: 0.80,  # weight 0.10
    structure: 0.85,     # weight 0.05
    clarity: 0.75,       # weight 0.10
    accuracy: 0.90,      # weight 0.15
    freshness: 1.00,     # weight 0.10
    coverage: 0.62       # weight 0.50  ← dominant weight, dragging score down
  }, improvement_hints: [
    "coverage: Line coverage at 62%, target is 80%. Uncovered modules: payment_handler, notification_service"
  ] }
```
