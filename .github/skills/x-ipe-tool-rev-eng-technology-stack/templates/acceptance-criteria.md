# Acceptance Criteria — Section 7: Technology Stack Identification

## Required (REQ)

| ID | Criterion | Subsection File | Validation Check |
|----|-----------|-----------------|------------------|
| AC-REQ-01 | Languages listed with version constraints | `7.1-languages.md` | File contains a table with at least one language row, each with Language, Version Constraint, and Evidence File columns |
| AC-REQ-02 | Frameworks listed with configuration evidence | `7.2-frameworks.md` | File contains a table with at least one framework row, each with Framework, Version, Evidence File, and Config Evidence columns |
| AC-REQ-03 | Build tools identified | `7.3-build-tools.md` | File contains a table with at least one build tool row with Tool, Category, and Config File columns |
| AC-REQ-04 | Evidence file cited for each technology | All subsection files | Every technology row across all files has a non-empty Evidence File cell referencing an actual file in the repo |

## Optional (OPT)

| ID | Criterion | Subsection File | Validation Check |
|----|-----------|-----------------|------------------|
| AC-OPT-01 | Runtime/infrastructure tools documented | `7.4-runtime-infrastructure.md` | File present with at least one entry for runtime version, container, or CI/CD tool |
| AC-OPT-02 | Testing frameworks identified | `7.5-testing-frameworks.md` | File present with at least one entry for test runner, assertion library, or coverage tool |

## Cross-Cutting

| ID | Criterion | Scope | Validation Check |
|----|-----------|-------|------------------|
| AC-XC-01 | index.md links all subsection files | `index.md` | Every subsection file (7.1–7.5) is linked in the TOC |
| AC-XC-02 | Quality score embedded | `index.md` | Frontmatter or header section contains a numeric quality score (0.0–1.0) |
| AC-XC-03 | Evidence is verifiable | All files | Every cited evidence file path can be resolved relative to repo root |
| AC-XC-04 | Version constraints are verbatim | All files | Version strings match source file content exactly (not paraphrased or guessed) |

## Quality Scoring Weights

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 0.30 | All REQ subsections present with required content |
| Structure | 0.20 | Consistent table formatting, proper markdown, valid links |
| Clarity | 0.20 | Technology categories are clear; evidence citations are specific |
| Accuracy | 0.15 | Versions match source files; frameworks correctly identified |
| Freshness | 0.10 | Lock file versions used where available; content reflects current state |
| Coverage | 0.05 | OPT criteria coverage (runtime/infra, testing frameworks) |
