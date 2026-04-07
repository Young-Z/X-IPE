---
name: x-ipe-tool-rev-eng-technology-stack
version: "1.0.0"
description: >
  Extract technology stack identification (Section 7) from a source repository during
  Phase 1-Scan of application reverse engineering. Produces a subfolder with subsection
  files covering languages, frameworks, build tools, runtime/infrastructure, and testing
  frameworks. Triggers: extract technology stack, identify dependencies, parse package
  manager files, detect frameworks, list build tools.
section_id: 7
phase: "1-Scan"
categories:
  - knowledge-extraction
  - reverse-engineering
  - technology-detection
---

# x-ipe-tool-rev-eng-technology-stack

## Purpose

1. Extract technology stack information from a source repository into documented subsection files
2. Validate extracted content against section-specific acceptance criteria with evidence citations

## Important Notes

- BLOCKING: Output MUST be a subfolder `07-technology-stack/` with individual subsection files — NEVER a single flat file (LL-002)
- BLOCKING: Output MUST include `index.md` linking all subsection files with TOC and quality scores (LL-001)
- CRITICAL: Every technology entry MUST cite the evidence file that proves its presence (e.g., `package.json`, `pyproject.toml`)

## About

**Key Concepts:**

- **Section 7**: Technology Stack Identification — one of 8 sections in the application reverse engineering extraction workflow
- **Phase 1-Scan**: First extraction phase; runs in parallel with Section 5, no dependencies
- **Subsection Files**: Individual markdown files per subsection (7.1–7.5), NOT concatenated into one file
- **Evidence-Based**: Every technology claim must reference the file that proves it
- **Source Priority**: Package manager files > Config files > Import statements > CI/CD configuration
- **Quality Weights**: Completeness=0.30, Structure=0.20, Clarity=0.20, Accuracy=0.15, Freshness=0.10, Coverage=0.05

## When to Use

```yaml
triggers:
  - "extract technology stack"
  - "identify dependencies"
  - "parse package manager files"
  - "detect frameworks"
  - "list build tools"
  - "section 7 extraction"

not_for:
  - "x-ipe-tool-rev-eng-code-structure-analysis: Project layout and module boundaries (Section 5)"
  - "x-ipe-tool-knowledge-extraction-application-reverse-engineering: Full multi-section orchestration"
```

## Input Parameters

```yaml
required:
  - name: operation
    type: string
    description: "Operation to perform"
    validation: "One of: extract, validate, package"
  - name: repo_path
    type: string
    description: "Absolute path to source repository root"
  - name: output_path
    type: string
    description: "Absolute path to output directory"
  - name: section_context
    type: object
    description: "Context from parent orchestrator"
    properties:
      section_number: 7
      section_name: "Technology Stack Identification"
      phase: "1-Scan"
      repo_type: "string (single-module | multi-module | monorepo | microservices)"

optional:
  - name: config
    type: object
    description: "Overrides for detection heuristics, lock file parsing, framework patterns"
  - name: mixin_overlays
    type: array
    description: "Repo-type and language-type mixin identifiers to apply"
```

## Input Initialization

<input_init>

1. Verify `repo_path` exists and is a directory
2. Verify `repo_path` contains at least one file
3. Create `output_path/07-technology-stack/` if it does not exist
4. Detect primary package manager files at repo root:
   - Python: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `Pipfile`
   - Node.js: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - Java: `pom.xml`, `build.gradle`, `build.gradle.kts`
   - Go: `go.mod`, `go.sum`
   - Rust: `Cargo.toml`, `Cargo.lock`
5. Set `detected_ecosystems` list from found package manager files
6. IF `mixin_overlays` provided THEN load language-specific detection heuristics

</input_init>

## Definition of Ready

<definition_of_ready>

1. `repo_path` exists, is a directory, and contains at least one file
2. `output_path` is writable
3. `section_context` includes `section_number`, `phase`, and `repo_type`
4. At least one package manager file or source file exists for analysis
5. Parent orchestrator has assigned this section for extraction

</definition_of_ready>

## Operations

<operation name="extract">
  <action>
    1. Scan repo root and first 2 levels for all package manager and config files
    2. Parse each detected package manager file to extract dependency lists with version constraints
    3. IF lock files exist THEN extract pinned versions alongside declared constraints
    4. Identify programming languages from file extensions, shebang lines, and language-specific configs
    5. Write `7.1-languages.md` with table: Language, Version Constraint, Evidence File, Lock Version
    6. Detect frameworks by analyzing:
       - Package dependencies (e.g., `django` in requirements, `express` in package.json)
       - Framework config files (e.g., `next.config.js`, `angular.json`, `settings.py`)
       - Import patterns in source files (sample 10-20 representative files)
    7. Write `7.2-frameworks.md` with table: Framework, Version, Evidence File, Config Evidence
    8. Identify build tools from config files: `Makefile`, `webpack.config.*`, `tsconfig.json`, `Dockerfile`, `docker-compose.yml`, `Taskfile.yml`, `.goreleaser.yml`
    9. Identify package managers and task runners from lock files and scripts
    10. Write `7.3-build-tools.md` with table: Tool, Category (build/package/task), Config File, Purpose
    11. Detect runtime and infrastructure from: `Dockerfile`, `.python-version`, `.nvmrc`, `.node-version`, `.tool-versions`, `runtime.txt`, CI/CD configs
    12. Scan `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml` for CI/CD tools
    13. Write `7.4-runtime-infrastructure.md` with table: Tool, Category (runtime/container/ci-cd), Version, Evidence File
    14. Detect testing frameworks from: test config files, test dependencies in package manifests, test directory structure
    15. Write `7.5-testing-frameworks.md` with table: Tool, Category (runner/assertion/coverage/mock), Version, Evidence File
    16. Write `index.md` linking subsections 7.1–7.5 with summary and reading order
  </action>
  <constraints>
    - BLOCKING: Each subsection MUST be a separate file in the subfolder
    - CRITICAL: Every technology entry MUST have a non-empty Evidence File column
    - CRITICAL: Version constraints must be extracted verbatim from source files, not guessed
    - When lock file and manifest disagree, report both values
  </constraints>
  <output>
    operation_output:
      success: true | false
      files_created: ["index.md", "7.1-languages.md", "7.2-frameworks.md", "7.3-build-tools.md", "7.4-runtime-infrastructure.md", "7.5-testing-frameworks.md"]
      detected_ecosystems: ["list of detected package ecosystems"]
      warnings: ["list of non-fatal issues"]
      errors: ["list of fatal issues if success=false"]
  </output>
</operation>

<operation name="validate">
  <action>
    1. Load acceptance criteria from `templates/acceptance-criteria.md`
    2. For each REQ criterion, check the corresponding subsection file:
       - AC-REQ-01: `7.1-languages.md` contains at least one language with version constraint
       - AC-REQ-02: `7.2-frameworks.md` contains at least one framework with config evidence
       - AC-REQ-03: `7.3-build-tools.md` contains at least one build tool entry
       - AC-REQ-04: Every technology row across all files has a non-empty Evidence File cell
    3. For each OPT criterion, check and record pass/skip:
       - AC-OPT-01: `7.4-runtime-infrastructure.md` present with entries
       - AC-OPT-02: `7.5-testing-frameworks.md` present with entries
    4. Calculate quality score using weights: Completeness=0.30, Structure=0.20, Clarity=0.20, Accuracy=0.15, Freshness=0.10, Coverage=0.05
    5. IF any REQ criterion fails THEN set success=false and list failures
  </action>
  <constraints>
    - BLOCKING: All REQ criteria must pass for success=true
    - Quality score must be between 0.0 and 1.0
  </constraints>
  <output>
    operation_output:
      success: true | false
      criteria_results: [{id, status: pass|fail|skip, detail}]
      quality_score: 0.0-1.0
      errors: ["list of failed REQ criteria"]
  </output>
</operation>



<operation name="package">
  <action>
    1. Verify all subsection files exist: 7.1 through 7.5
    2. Verify `index.md` exists and links all subsection files
    3. IF validate operation was run THEN embed quality score in `index.md` frontmatter
    4. Ensure `index.md` contains: TOC with links, section summary, quality score, reading order
    5. Verify no orphan files exist in the subfolder (all files linked from index.md)
    6. Return final package manifest
  </action>
  <constraints>
    - BLOCKING: index.md MUST link every subsection file (LL-001)
    - BLOCKING: Output must be subfolder structure, not flat files (LL-002)
  </constraints>
  <output>
    operation_output:
      success: true | false
      package_path: "{output_path}/07-technology-stack/"
      files: ["index.md", "7.1-languages.md", "7.2-frameworks.md", "7.3-build-tools.md", "7.4-runtime-infrastructure.md", "7.5-testing-frameworks.md"]
      quality_score: 0.0-1.0
  </output>
</operation>

## Output Result

```yaml
operation_output:
  success: boolean
  operation: string
  section: "07-technology-stack"
  result: object    # operation-specific result data
  warnings: array   # non-fatal issues
  errors: array     # fatal issues (only when success=false)
```

**Subfolder structure produced by full extract→package pipeline:**

```
07-technology-stack/
├── index.md                           # TOC, quality score, reading order
├── 7.1-languages.md                   # Languages with version constraints
├── 7.2-frameworks.md                  # Frameworks with config evidence
├── 7.3-build-tools.md                 # Build systems, package managers, task runners
├── 7.4-runtime-infrastructure.md      # Runtime versions, containers, CI/CD
├── 7.5-testing-frameworks.md          # Test runners, assertion libs, coverage
```

## Definition of Done

<definition_of_done>

1. Subfolder `07-technology-stack/` exists at `output_path`
2. `index.md` present with TOC linking all subsection files
3. `7.1-languages.md` contains languages with version constraints
4. `7.2-frameworks.md` contains frameworks with configuration evidence
5. `7.3-build-tools.md` contains build tools with config file references
6. Every technology entry cites an evidence file
7. All REQ acceptance criteria pass validation
8. Quality score computed and embedded in index.md
10. No orphan files — every file in subfolder is linked from index.md

</definition_of_done>

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| EMPTY_REPO | `repo_path` contains no files | Return failure with descriptive message |
| NO_PACKAGE_FILES | No package manager files detected | Fall back to import statement analysis and file extension detection |
| PARSE_FAILED | Package manager file has invalid syntax | Log warning, skip file, continue with others |
| PERMISSION_DENIED | Cannot read repo files | Return failure, list inaccessible paths |
| WRITE_FAILED | Cannot write to `output_path` | Return failure with filesystem error |
| INVALID_OPERATION | Unrecognized operation name | Return failure listing valid operations |
| MISSING_SUBSECTION | Subsection file missing during validate/package | Return failure listing missing files |

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Section 7 acceptance criteria with REQ/OPT markers |
| `templates/extraction-prompts.md` | Extraction prompts for each subsection |

## Examples

See `references/examples.md` for complete usage examples including:
- Example 1: Extracting technology stack from a Node.js Express project
- Example 2: Extracting technology stack from a Python multi-module project
