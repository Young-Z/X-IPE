---
name: x-ipe-tool-rev-eng-dependency-analysis
version: "1.0"
description: Section 4 — Dependency Analysis for application reverse engineering (Phase 3-Deep). Extracts inter-module dependency graphs, external library inventories, circular dependency chains, critical hub modules, and dependency visualizations. Triggers on "dependency analysis", "import graph", "library inventory".
section_id: 4
phase: "3-Deep"
categories: ["application-reverse-engineering"]
---

# Dependency Analysis — Section 4

## Purpose

AI Agents follow this skill to extract dependency knowledge from a target codebase:
1. Map inter-module dependencies (import/call graphs between internal modules)
2. Inventory external library dependencies with versions and purposes
3. Detect circular dependency chains
4. Identify critical hub modules that many others depend on
5. Produce Mermaid graphs and Architecture DSL dependency landscape

---

## Important Notes

BLOCKING: This is a **tool skill** — it is invoked by `x-ipe-task-based-application-knowledge-extractor` during Phase 3-Deep extraction. Do not invoke standalone.
CRITICAL: Phase 1 scan output (Sections 5 + 7) and Phase 2 test knowledge (Section 8) MUST be available before this skill runs.
CRITICAL: Every dependency claim MUST cite source file:line (import statement or lock file entry).
CRITICAL: Output MUST use subfolder structure with `index.md` linking subsections (LL-001, LL-002).

---

## When to Use

```yaml
triggers:
  - "dependency analysis"
  - "import graph extraction"
  - "library inventory"
  - "section 4 extraction"
  - "circular dependency detection"

not_for:
  - "Data flow analysis" → Section 6
  - "Architecture recovery" → Section 1
  - "Adding new dependencies" → not reverse engineering
```

---

## Input Parameters

```yaml
input:
  operation: "extract | validate | package"
  section_id: "4-dependency-analysis"
  content_path: "string | null"
  repo_path: "string"
  phase1_output: "string"       # Path to Phase 1 results (Sections 5, 7)
  phase2_output: "string"       # Path to Phase 2 results (Section 8)
  output_path: "string"         # Target output directory
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />
  <field name="repo_path" source="Caller provides path to target repository">
    <steps>
      1. Must be a valid directory containing source code
      2. Required for extract operation
    </steps>
  </field>
  <field name="phase1_output" source="Phase 1 scan output directory">
    <steps>
      1. Must contain Section 5 (code structure) for module boundaries
      2. Must contain Section 7 (tech stack) for package manager identification
      3. Read module list and directory-to-purpose mapping from Section 5
      4. Read detected languages and build tools from Section 7
    </steps>
  </field>
  <field name="phase2_output" source="Phase 2 test knowledge directory">
    <steps>
      1. Must contain Section 8 (test knowledge extraction)
      2. Read test imports — they reveal module coupling patterns
      3. Read mock/stub targets — they reveal dependency injection points
    </steps>
  </field>
  <field name="content_path" source="Path to extracted content">
    <steps>
      1. Required for validate, package operations
      2. Must be UTF-8 markdown
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Phase 1 output available</name>
    <verification>phase1_output directory exists with Section 5 and Section 7 content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Phase 2 output available</name>
    <verification>phase2_output directory exists with Section 8 test knowledge</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Repository accessible</name>
    <verification>repo_path is a valid directory with source code</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Valid operation requested</name>
    <verification>operation is one of: extract, validate, package</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: extract

**When:** Orchestrator requests dependency extraction for Section 4.

```xml
<operation name="extract">
  <action>
    1. Read Phase 1 output:
       a. From Section 5: module list, directory-to-purpose mapping, module boundaries
       b. From Section 7: languages, package managers, build tools
          - npm/yarn/pnpm → package.json + lock file
          - pip/poetry/uv → requirements.txt / pyproject.toml + lock file
          - Maven/Gradle → pom.xml / build.gradle + dependency tree
          - Go modules → go.mod / go.sum
          - Cargo → Cargo.toml / Cargo.lock
    2. Read Phase 2 output:
       a. From Section 8: test import patterns revealing coupling
       b. Mock/stub targets indicating dependency injection boundaries
    3. Extract inter-module dependencies (subsection 4.1):
       a. Trace import/require/include/use statements across all source files
       b. For each dependency: source module, target module, import type, file:line
       c. Classify type: direct import, re-export, dynamic import, type-only
       d. Build adjacency list: { source_module → [target_modules] }
       e. Output: 01-inter-module-deps.md
    4. Extract external library dependencies (subsection 4.2):
       a. Parse package manager manifest files (package.json, pyproject.toml, go.mod, etc.)
       b. Parse lock files for exact resolved versions
       c. For each library: name, version, declared version range, dependency type
          (runtime, dev, optional, peer), purpose (1 sentence)
       d. Cross-reference with actual imports to confirm usage
       e. Detect unused declared dependencies (declared but never imported)
       f. Output: 02-external-library-deps.md
    5. Detect circular dependencies (subsection 4.3):
       a. Run cycle detection on the inter-module adjacency list (DFS-based)
       b. For each cycle: list modules in chain, list specific import file:lines
       c. Assess severity: tight cycle (2 modules) vs long chain
       d. Output: 03-circular-dependencies.md
    6. Identify critical dependencies (subsection 4.4):
       a. Compute in-degree for each module (how many modules depend on it)
       b. Compute out-degree (how many modules it depends on)
       c. Rank by fan-in: top modules are hub/critical dependencies
       d. For each hub: module name, fan-in count, fan-out count, dependents list
       e. Flag modules with fan-in > 50% of total modules as critical
       f. Output: 04-critical-dependencies.md
    7. Create dependency visualizations (subsection 4.5):
       a. Generate Mermaid flowchart for inter-module dependency graph
       b. Generate Mermaid pie chart for dependency type distribution
       c. Invoke x-ipe-tool-architecture-dsl with operation generate_landscape_view
          to create Architecture DSL dependency landscape
       d. Output: 05-dependency-visualization.md
    8. Create index.md with dependency overview table:
       | Metric | Count |
       | Internal modules | N |
       | Inter-module edges | N |
       | External libraries | N |
       | Circular chains | N |
       | Critical hubs | N |
  </action>
  <constraints>
    - CRITICAL: Every dependency MUST cite source file:line (import statement)
    - CRITICAL: External libraries MUST include resolved version from lock file
    - CRITICAL: Each subsection goes in its own file (LL-002)
    - CRITICAL: index.md must link all subsections with summary metrics (LL-001)
    - BLOCKING: Architecture DSL MUST be used for dependency landscape via x-ipe-tool-architecture-dsl
  </constraints>
  <output>
    extracted_content: path to output directory with index.md + 5 subsection files
  </output>
</operation>
```

### Operation: validate

**When:** After extraction, validate content against acceptance criteria.

```xml
<operation name="validate">
  <action>
    1. Load acceptance criteria from templates/acceptance-criteria.md
    2. Read extracted content at content_path
    3. Evaluate each criterion:
       a. [REQ] Inter-module dependency graph present → check 01-inter-module-deps.md exists
          and contains adjacency list or table
       b. [REQ] External library list with versions → check 02-external-library-deps.md
          contains table with name, version, type columns
       c. [REQ] Dependency type classified → verify each dependency has type label
          (import, runtime, dev, optional)
       d. [OPT] Circular dependencies identified → check 03-circular-dependencies.md
          for cycle documentation or explicit "none detected"
       e. [OPT] Critical hub modules highlighted → check 04-critical-dependencies.md
          for fan-in ranking
       f. [OPT] Architecture DSL visualization → check 05-dependency-visualization.md
          for Architecture DSL block
    4. Mark each as PASS, FAIL, or INCOMPLETE
    5. Distinguish FAIL (wrong content) from INCOMPLETE (missing content)
  </action>
  <output>
    validation_result: { section_id, passed, criteria: [{id, status, feedback}], missing_info[] }
  </output>
</operation>
```



### Operation: package

**When:** Format validated content into final subfolder output.

```xml
<operation name="package">
  <action>
    1. Read validated content at content_path
    2. Create output subfolder structure:
       section-04-dependency-analysis/
       ├── index.md                     # Dependency overview with counts
       ├── 01-inter-module-deps.md      # Import/call graphs between modules
       ├── 02-external-library-deps.md  # Third-party libraries
       ├── 03-circular-dependencies.md  # Circular dependency chains
       ├── 04-critical-dependencies.md  # Hub modules analysis
       ├── 05-dependency-visualization.md # Mermaid + Architecture DSL
       ├── screenshots/
    3. Ensure index.md has summary metrics table and links to each subsection
    4. Verify all file:line citations are present for import statements
    5. Verify external libraries include resolved versions
    6. Verify Mermaid blocks have correct syntax
    7. Verify Architecture DSL blocks are valid (if present)
  </action>
  <constraints>
    - CRITICAL: index.md MUST link all subsections with summary metrics (LL-001)
    - CRITICAL: Each subsection in its own file (LL-002)
  </constraints>
  <output>
    package_path: path to section-04-dependency-analysis/ directory
  </output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "extract | validate | package"
  result:
    extracted_content:   # extract — path to output directory
    validation_result:   # validate — { section_id, passed, criteria[], missing_info[] }
    package_path:        # package — path to final subfolder
  errors: []
```

---

## Quality Scoring

**Profile:** Other Sections

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Completeness** | **0.30** | Ratio of [REQ] criteria satisfied, dependency coverage |
| Structure | 0.20 | Proper grouping, metrics table, subsection layout |
| Clarity | 0.20 | Clear dependency descriptions, readable graphs |
| Accuracy | 0.15 | Correct import citations, valid version numbers |
| Freshness | 0.10 | References current lock file versions |
| Coverage | 0.05 | Breadth across modules and dependency types |

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>operation_output.success is true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Subfolder structure correct</name>
    <verification>Output has index.md + subsection files + screenshots/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All REQ criteria pass</name>
    <verification>validate operation returns passed: true for all [REQ] items</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Inter-module graph present</name>
    <verification>01-inter-module-deps.md contains dependency adjacency list or table</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>External libraries documented</name>
    <verification>02-external-library-deps.md contains library table with versions and types</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Dependency types classified</name>
    <verification>Every dependency entry has a type label (import, runtime, dev, optional)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Source file citations present</name>
    <verification>Every dependency claim cites file:line of the import statement</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `PHASE1_NOT_AVAILABLE` | Phase 1 output missing or incomplete | Run Phase 1 scan first |
| `PHASE2_NOT_AVAILABLE` | Phase 2 test knowledge missing | Run Phase 2 test extraction first |
| `ARCH_DSL_FAILED` | Architecture DSL generation failed | Check x-ipe-tool-architecture-dsl availability |
| `INVALID_OPERATION` | Operation not one of the 3 defined | Use: extract, validate, package |
| `CONTENT_NOT_FOUND` | content_path file does not exist | Verify extraction completed |
| `NO_LOCK_FILE` | Package manager lock file not found | Document versions from manifest only; note lower confidence |
| `NO_MODULES_DETECTED` | No distinct modules found | Review Phase 1 output; codebase may be single-module |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Validation rules with [REQ]/[OPT] markers |
| `templates/extraction-prompts.md` | Per-subsection extraction guidance |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
