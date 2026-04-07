# Acceptance Criteria — Section 5: Code Structure Analysis

## Required (REQ)

| ID | Criterion | Subsection File | Validation Check |
|----|-----------|-----------------|------------------|
| AC-REQ-01 | Root directory tree present (2-3 levels deep) | `5.1-project-layout.md` | File contains an indented tree structure with at least 2 nesting levels and purpose annotations |
| AC-REQ-02 | Directory-to-purpose mapping table | `5.2-directory-structure.md` | File contains a markdown table with columns: Directory, Role, Key Files (minimum 2 data rows) |
| AC-REQ-03 | Naming conventions documented with examples | `5.3-naming-conventions.md` | File contains at least one naming pattern (file, class, or function) with a concrete code example from the repo |
| AC-REQ-04 | Module boundary markers identified | `5.4-module-boundaries.md` | File lists at least one boundary marker file (e.g., `__init__.py`, `index.ts`) found in the repo |

## Optional (OPT)

| ID | Criterion | Subsection File | Validation Check |
|----|-----------|-----------------|------------------|
| AC-OPT-01 | File count per directory (hot spot analysis) | `5.2-directory-structure.md` or separate section | Table or list showing directories sorted by file count descending |
| AC-OPT-02 | Layering pattern identified and described | `5.4-module-boundaries.md` | Named pattern (e.g., "MVC", "Clean Architecture") with directory-to-layer mapping |

## Cross-Cutting

| ID | Criterion | Scope | Validation Check |
|----|-----------|-------|------------------|
| AC-XC-01 | index.md links all subsection files | `index.md` | Every subsection file (5.1–5.4) is linked in the TOC |
| AC-XC-02 | Quality score embedded | `index.md` | Frontmatter or header section contains a numeric quality score (0.0–1.0) |
| AC-XC-03 | All claims cite evidence | All files | No structural claim exists without referencing the source file or command output |

## Quality Scoring Weights

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 0.30 | All REQ subsections present with required content |
| Structure | 0.20 | Consistent formatting, proper table structure, valid markdown |
| Clarity | 0.20 | Purpose annotations are understandable; naming examples are clear |
| Accuracy | 0.15 | Tree matches actual repo; naming patterns match actual files |
| Freshness | 0.10 | Content reflects current state of repo (not stale) |
| Coverage | 0.05 | OPT criteria coverage (hot spots, layering pattern) |
