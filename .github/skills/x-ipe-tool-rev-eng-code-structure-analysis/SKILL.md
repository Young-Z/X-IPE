---
name: x-ipe-tool-rev-eng-code-structure-analysis
version: "1.0.0"
description: >
  Extract code structure analysis (Section 5) from a source repository during Phase 1-Scan
  of application reverse engineering. Produces a subfolder with subsection files covering
  project layout, directory structure, naming conventions, and module boundaries.
  Triggers: extract code structure, analyze project layout, map directory structure,
  identify naming conventions, detect module boundaries.
section_id: 5
phase: "1-Scan"
categories:
  - knowledge-extraction
  - reverse-engineering
  - code-analysis
---

# x-ipe-tool-rev-eng-code-structure-analysis

## Purpose

1. Extract structural information from a source repository into documented subsection files
2. Validate extracted content against section-specific acceptance criteria

## Important Notes

- BLOCKING: Output MUST be a subfolder `05-code-structure-analysis/` with individual subsection files — NEVER a single flat file (LL-002)
- BLOCKING: Output MUST include `index.md` linking all subsection files with TOC and quality scores (LL-001)
- CRITICAL: Every claim in output must cite the source file or command that produced the evidence

## About

**Key Concepts:**

- **Section 5**: Code Structure Analysis — one of 8 sections in the application reverse engineering extraction workflow
- **Phase 1-Scan**: First extraction phase; no dependencies on other sections
- **Subsection Files**: Individual markdown files per subsection (5.1–5.4), NOT concatenated into one file
- **Source Priority**: Directory tree output > README.md/CONTRIBUTING.md > Build configs > Entry points
- **Quality Weights**: Completeness=0.30, Structure=0.20, Clarity=0.20, Accuracy=0.15, Freshness=0.10, Coverage=0.05

## When to Use

```yaml
triggers:
  - "extract code structure"
  - "analyze project layout"
  - "map directory structure"
  - "identify naming conventions"
  - "detect module boundaries"
  - "section 5 extraction"

not_for:
  - "x-ipe-tool-rev-eng-technology-stack: Technology/dependency identification (Section 7)"
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
      section_number: 5
      section_name: "Code Structure Analysis"
      phase: "1-Scan"
      repo_type: "string (single-module | multi-module | monorepo | microservices)"

optional:
  - name: config
    type: object
    description: "Overrides for tree depth (default: 3), hot-spot threshold (default: 20)"
  - name: mixin_overlays
    type: array
    description: "Repo-type and language-type mixin identifiers to apply"
```

## Input Initialization

<input_init>

1. Verify `repo_path` exists and is a directory
2. Verify `repo_path` contains at least one source file (not an empty directory)
3. Create `output_path/05-code-structure-analysis/` if it does not exist
4. Set `tree_depth` from `config.tree_depth` or default to 3
5. Set `hotspot_threshold` from `config.hotspot_threshold` or default to 20
6. IF `mixin_overlays` provided THEN load mixin-specific adjustments (e.g., monorepo may need per-package trees)

</input_init>

## Definition of Ready

<definition_of_ready>

1. `repo_path` exists, is a directory, and contains at least one file
2. `output_path` is writable
3. `section_context` includes `section_number`, `phase`, and `repo_type`
4. Shell commands `find` and `tree` (or equivalent) are available
5. Parent orchestrator has assigned this section for extraction

</definition_of_ready>

## Operations

<operation name="extract">
  <action>
    1. Run `tree -L {tree_depth} -d --charset=ascii {repo_path}` to capture directory tree
    2. IF tree command unavailable THEN use `find {repo_path} -maxdepth {tree_depth} -type d` and format as indented tree
    3. For each top-level directory, read README.md or doc comments to determine purpose annotation
    4. Write `5.1-project-layout.md` with annotated directory tree
    5. Run `find {repo_path} -type f | sed 's|.*/||' | sort | head -200` to sample filenames
    6. Build directory-to-purpose mapping table: columns = Directory, Role, Key Files, File Count
    7. Write `5.2-directory-structure.md` with the mapping table
    8. Analyze sampled filenames for naming patterns (snake_case, camelCase, PascalCase, kebab-case)
    9. Scan class definitions and function signatures in 5-10 representative files for naming conventions
    10. Write `5.3-naming-conventions.md` with patterns and concrete examples from the repo
    11. Search for module boundary markers: `__init__.py`, `index.ts`, `index.js`, `package.json`, `go.mod`, `Cargo.toml`, `build.gradle`
    12. Identify layering patterns by checking for directory names matching known patterns (controller/service/repository, handler/usecase/entity, cmd/internal/pkg)
    13. Write `5.4-module-boundaries.md` with boundary markers and layering analysis
    14. Write `index.md` linking subsections 5.1–5.4 with summary and reading order
  </action>
  <constraints>
    - BLOCKING: Each subsection MUST be a separate file in the subfolder
    - CRITICAL: Annotate tree nodes with purpose — do not output a raw tree
    - CRITICAL: Naming convention examples must come from actual repo files, not generic examples
    - Tree depth limited to config value (default 3) to avoid noise
  </constraints>
  <output>
    operation_output:
      success: true | false
      files_created: ["index.md", "5.1-project-layout.md", "5.2-directory-structure.md", "5.3-naming-conventions.md", "5.4-module-boundaries.md"]
      warnings: ["list of non-fatal issues"]
      errors: ["list of fatal issues if success=false"]
  </output>
</operation>

<operation name="validate">
  <action>
    1. Load acceptance criteria from `templates/acceptance-criteria.md`
    2. For each REQ criterion, check the corresponding subsection file:
       - AC-REQ-01: `5.1-project-layout.md` contains directory tree at least 2 levels deep
       - AC-REQ-02: `5.2-directory-structure.md` contains a markdown table with Directory/Role/Key Files columns
       - AC-REQ-03: `5.3-naming-conventions.md` contains at least one naming pattern with a code example
       - AC-REQ-04: `5.4-module-boundaries.md` lists at least one boundary marker file found
    3. For each OPT criterion, check and record pass/skip:
       - AC-OPT-01: File count per directory present
       - AC-OPT-02: Layering pattern identified
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
    1. Verify all subsection files exist: 5.1 through 5.4
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
      package_path: "{output_path}/05-code-structure-analysis/"
      files: ["index.md", "5.1-project-layout.md", "5.2-directory-structure.md", "5.3-naming-conventions.md", "5.4-module-boundaries.md"]
      quality_score: 0.0-1.0
  </output>
</operation>

## Output Result

```yaml
operation_output:
  success: boolean
  operation: string
  section: "05-code-structure-analysis"
  result: object    # operation-specific result data
  warnings: array   # non-fatal issues
  errors: array     # fatal issues (only when success=false)
```

**Subfolder structure produced by full extract→package pipeline:**

```
05-code-structure-analysis/
├── index.md                       # TOC, quality score, reading order
├── 5.1-project-layout.md          # Annotated directory tree
├── 5.2-directory-structure.md     # Directory-to-purpose mapping table
├── 5.3-naming-conventions.md      # File/class/function naming patterns
├── 5.4-module-boundaries.md       # Boundary markers and layering
```

## Definition of Done

<definition_of_done>

1. Subfolder `05-code-structure-analysis/` exists at `output_path`
2. `index.md` present with TOC linking all subsection files
3. `5.1-project-layout.md` contains annotated directory tree (2-3 levels)
4. `5.2-directory-structure.md` contains directory-to-purpose mapping table
5. `5.3-naming-conventions.md` contains naming patterns with repo-specific examples
6. `5.4-module-boundaries.md` contains boundary markers found in repo
7. All REQ acceptance criteria pass validation
8. Quality score computed and embedded in index.md
10. No orphan files — every file in subfolder is linked from index.md

</definition_of_done>

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| EMPTY_REPO | `repo_path` contains no files | Return failure with descriptive message |
| TREE_CMD_UNAVAILABLE | `tree` command not found | Fall back to `find` + manual formatting |
| PERMISSION_DENIED | Cannot read repo files | Return failure, list inaccessible paths |
| WRITE_FAILED | Cannot write to `output_path` | Return failure with filesystem error |
| INVALID_OPERATION | Unrecognized operation name | Return failure listing valid operations |
| MISSING_SUBSECTION | Subsection file missing during validate/package | Return failure listing missing files |

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Section 5 acceptance criteria with REQ/OPT markers |
| `templates/extraction-prompts.md` | Extraction prompts for each subsection |

## Examples

See `references/examples.md` for complete usage examples including:
- Example 1: Extracting code structure from a Python Django project
- Example 2: Extracting code structure from a TypeScript monorepo
