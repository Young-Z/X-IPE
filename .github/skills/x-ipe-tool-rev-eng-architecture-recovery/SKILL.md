---
name: x-ipe-tool-rev-eng-architecture-recovery
version: "1.0"
description: Section 1 — Architecture Recovery for application reverse engineering (Phase 3-Deep). Extracts 4-level architecture view using Architecture DSL (conceptual/logical) and Mermaid (physical/data flow). Triggers on "architecture recovery", "module view", "component diagram".
section_id: 1
phase: "3-Deep"
categories: ["application-reverse-engineering"]
---

# Architecture Recovery — Section 1

## Purpose

AI Agents follow this skill to extract architecture knowledge from a target codebase:
1. Build a 4-level architecture view (Conceptual, Logical, Physical, Data Flow)
2. Use Architecture DSL for Levels 1–2 (invoke `x-ipe-tool-architecture-dsl`)
3. Use Mermaid class diagrams for Level 3, sequence diagrams for Level 4
4. Cross-reference with Phase 1 structure scan and Phase 2 test knowledge

---

## Important Notes

BLOCKING: This is a **tool skill** — it is invoked by `x-ipe-task-based-application-knowledge-extractor` during Phase 3-Deep extraction. Do not invoke standalone.
CRITICAL: Phase 1 scan output (Sections 5 + 7) and Phase 2 test knowledge (Section 8) MUST be available before this skill runs.
CRITICAL: Architecture DSL is REQUIRED for conceptual and/or logical levels. Use `x-ipe-tool-architecture-dsl` — do not hand-write DSL.
CRITICAL: Output MUST use subfolder structure with `index.md` linking subsections (LL-001, LL-002).

---

## When to Use

```yaml
triggers:
  - "architecture recovery"
  - "module view extraction"
  - "component diagram from source"
  - "section 1 extraction"
  - "4-level architecture"

not_for:
  - "Architecture DSL generation only" → use x-ipe-tool-architecture-dsl
  - "Code structure scan" → Phase 1 Section 5
  - "Data flow analysis only" → Section 6
```

---

## Input Parameters

```yaml
input:
  operation: "extract | validate | package"
  section_id: "1-architecture-recovery"
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
      1. Must contain Section 5 (code structure) and Section 7 (tech stack)
      2. Read module list and directory-to-purpose mapping from Section 5
      3. Read detected frameworks and languages from Section 7
    </steps>
  </field>
  <field name="phase2_output" source="Phase 2 test knowledge directory">
    <steps>
      1. Must contain Section 8 (test knowledge extraction)
      2. Read test-to-module mapping for cross-referencing
      3. Read mock/stub analysis for boundary identification
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

**When:** Orchestrator requests architecture extraction for Section 1.

```xml
<operation name="extract">
  <action>
    1. Read Phase 1 output:
       a. From Section 5: module list, directory-to-purpose mapping, layering patterns
       b. From Section 7: detected languages, frameworks, build tools
    2. Read Phase 2 output:
       a. From Section 8: test-to-module mapping, mock/stub boundaries
    3. Analyze module/package structure to identify logical components:
       a. Trace import/dependency chains for component relationships
       b. Identify entry points and request routing
       c. Classify components by responsibility: handlers, services, repositories, utilities, models
    4. Build Level 1 — Conceptual (Architecture DSL):
       a. Invoke x-ipe-tool-architecture-dsl with operation generate_landscape_view
       b. Define application boundaries, external systems, user types
       c. Output: 01-conceptual-landscape.md
    5. Build Level 2 — Logical (Architecture DSL):
       a. Invoke x-ipe-tool-architecture-dsl with operation generate_module_view
       b. Define layers, modules per layer, component responsibilities
       c. Each module MUST list: responsibility, source directory, key files
       d. Output: 02-logical-module-view.md
    6. Build Level 3 — Physical (Mermaid class diagrams):
       a. For key class hierarchies: generate Mermaid classDiagram
       b. Include inheritance, composition, interface implementations
       c. Output: 03-physical-classes.md
    7. Build Level 4 — Data Flow (Mermaid sequence diagrams):
       a. Trace critical request paths through the system
       b. Generate Mermaid sequenceDiagram for each flow
       c. Cross-reference with Phase 2 integration test flows
       d. Output: 04-data-flow-sequences.md
    8. Create index.md linking all 4 levels with summary table
  </action>
  <constraints>
    - BLOCKING: Architecture DSL MUST be used for Levels 1-2 via x-ipe-tool-architecture-dsl
    - CRITICAL: Every module must cite specific source files/directories
    - CRITICAL: Each subsection goes in its own file (LL-002)
    - CRITICAL: index.md must link all subsections (LL-001)
  </constraints>
  <output>
    extracted_content: path to output directory with index.md + 4 subsection files
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
       a. [REQ] At least 2 architecture levels documented → check subsection files exist
       b. [REQ] Module/component diagram present → check for Architecture DSL or Mermaid blocks
       c. [REQ] Architecture DSL used for conceptual/logical → verify @startuml blocks
       d. [REQ] Each module lists responsibility → scan for responsibility descriptions
       e. [REQ] Components reference source files → check for file path citations
       f. [OPT] Physical level class diagrams → check 03-physical-classes.md
       g. [OPT] Data flow sequence diagrams → check 04-data-flow-sequences.md
       h. [OPT] Phase 2 cross-reference → check for test knowledge citations
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
       section-01-architecture-recovery/
       ├── index.md                     # Architecture overview with links
       ├── 01-conceptual-landscape.md   # Architecture DSL landscape view
       ├── 02-logical-module-view.md    # Architecture DSL module view
       ├── 03-physical-classes.md       # Mermaid class diagrams
       ├── 04-data-flow-sequences.md    # Mermaid sequence diagrams
       ├── screenshots/                 # Diagram screenshots (if rendered)
    3. Ensure index.md has summary table and links to each subsection
    4. Verify all Architecture DSL blocks are valid
    5. Verify all Mermaid blocks have correct syntax
  </action>
  <constraints>
    - CRITICAL: index.md MUST link all subsections (LL-001)
    - CRITICAL: Each subsection in its own file (LL-002)
  </constraints>
  <output>
    package_path: path to section-01-architecture-recovery/ directory
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

**Profile:** Architecture Sections

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 0.20 | Ratio of [REQ] criteria satisfied |
| Structure | 0.10 | Proper heading hierarchy, diagrams, subfolder layout |
| Clarity | 0.15 | Clear explanations, concrete responsibility descriptions |
| **Accuracy** | **0.35** | Evidence-backed claims, verified file:line citations |
| Freshness | 0.10 | References current code state |
| Coverage | 0.10 | Breadth across modules and architecture levels |

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
    <name>Architecture DSL present</name>
    <verification>At least one Architecture DSL block exists in conceptual or logical level</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Source file citations present</name>
    <verification>Every module/component references specific source files or directories</verification>
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
| `NO_MODULES_DETECTED` | No logical modules found in codebase | Review Phase 1 output; codebase may be too small |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Validation rules with [REQ]/[OPT] markers |
| `templates/extraction-prompts.md` | Per-subsection extraction guidance |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
