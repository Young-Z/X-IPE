---
name: x-ipe-tool-rev-eng-design-pattern-detection
version: "1.0"
description: Section 2 — Design Pattern Detection for application reverse engineering (Phase 3-Deep). Detects GoF and language-specific patterns with confidence scoring and file:line citations. Triggers on "design pattern detection", "pattern inventory", "pattern scan".
section_id: 2
phase: "3-Deep"
categories: ["application-reverse-engineering"]
---

# Design Pattern Detection — Section 2

## Purpose

AI Agents follow this skill to detect and document design patterns in a target codebase:
1. Scan for Creational, Structural, and Behavioral patterns (GoF)
2. Identify language-specific patterns (TypeScript, Python, Go idioms)
3. Assign confidence levels (🟢/🟡/🔴) with file:line evidence citations
4. Map pattern interactions and compositions

---

## Important Notes

BLOCKING: This is a **tool skill** — it is invoked by `x-ipe-task-based-application-knowledge-extractor` during Phase 3-Deep extraction. Do not invoke standalone.
CRITICAL: Phase 1 scan output (Section 5) and Phase 2 test knowledge (Section 8) MUST be available before this skill runs.
CRITICAL: Every detected pattern MUST cite file:line evidence. Patterns without citations are rejected.
CRITICAL: Output MUST use subfolder structure with `index.md` linking subsections (LL-001, LL-002).

---

## When to Use

```yaml
triggers:
  - "design pattern detection"
  - "pattern inventory"
  - "pattern scan in codebase"
  - "section 2 extraction"
  - "detect factory singleton observer"

not_for:
  - "Architecture module view" → Section 1
  - "API contract extraction" → Section 3
  - "New pattern implementation" → not reverse engineering
```

---

## Input Parameters

```yaml
input:
  operation: "extract | validate | package"
  section_id: "2-design-pattern-detection"
  content_path: "string | null"
  repo_path: "string"
  phase1_output: "string"       # Path to Phase 1 results (Section 5)
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
      1. Must contain Section 5 (code structure) for class/function scanning
      2. Read naming conventions and module boundaries
    </steps>
  </field>
  <field name="phase2_output" source="Phase 2 test knowledge directory">
    <steps>
      1. Must contain Section 8 (test knowledge extraction)
      2. Read mock/stub analysis — mocks reveal integration boundaries indicating patterns
      3. Read test fixture patterns for DI/Factory detection
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
    <verification>phase1_output directory exists with Section 5 content</verification>
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

**When:** Orchestrator requests pattern detection for Section 2.

```xml
<operation name="extract">
  <action>
    1. Read Phase 1 output:
       a. From Section 5: module list, class/file structure, naming conventions
    2. Read Phase 2 output:
       a. From Section 8: mock/stub analysis, test fixture patterns, DI usage in tests
    3. Scan for Creational Patterns:
       a. Factory: search for create_*, build_*, *Factory classes, factory functions
       b. Singleton: module-level state, instance caching, __new__ overrides
       c. Builder: fluent method chaining, step-by-step object construction
       d. For each: cite file:line, assign confidence, describe role
       e. Output: 01-creational-patterns.md
    4. Scan for Structural Patterns:
       a. Adapter: wrappers around external APIs, interface translation
       b. Decorator: function decorators, middleware chains, wrapper classes
       c. Facade: simplified interfaces hiding complex subsystems
       d. For each: cite file:line, assign confidence, describe role
       e. Output: 02-structural-patterns.md
    5. Scan for Behavioral Patterns:
       a. Observer: event emitters, pub/sub, callback registrations
       b. Strategy: pluggable algorithms, interface implementations, config-driven dispatch
       c. Command: handler dispatch, action objects, undo/redo stacks
       d. For each: cite file:line, assign confidence, describe role
       e. Output: 03-behavioral-patterns.md
    6. Scan for Language-Specific Patterns:
       a. TypeScript: discriminated unions, type guards, module augmentation
       b. Python: context managers, descriptors, metaclasses, decorators
       c. Go: functional options, interface embedding, error wrapping
       d. Output: 04-language-specific-patterns.md
    7. Analyze Pattern Interactions:
       a. Identify composed patterns (e.g., Factory + Strategy, Observer + Mediator)
       b. Map pattern dependency chains
       c. Output: 05-pattern-interactions.md
    8. Create index.md with pattern inventory table:
       | Pattern | Type | Confidence | Location | Role |
  </action>
  <constraints>
    - CRITICAL: Every pattern MUST have file:line evidence citation
    - CRITICAL: Confidence MUST be assigned: 🟢 (canonical), 🟡 (partial), 🔴 (ambiguous)
    - CRITICAL: Each subsection in its own file (LL-002)
    - BLOCKING: Minimum 3 patterns analyzed or document "no canonical patterns found"
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
       a. [REQ] Pattern inventory table present → check index.md for table
       b. [REQ] Confidence levels present → check for 🟢/🟡/🔴 markers
       c. [REQ] File:line citations present → check for path:line format
       d. [REQ] At least 3 patterns → count unique patterns in inventory
       e. [OPT] Pattern interaction map → check 05-pattern-interactions.md
       f. [OPT] Test-derived evidence → check for Phase 2 cross-references
    4. Mark each as PASS, FAIL, or INCOMPLETE
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
       section-02-design-patterns/
       ├── index.md                        # Pattern inventory table
       ├── 01-creational-patterns.md
       ├── 02-structural-patterns.md
       ├── 03-behavioral-patterns.md
       ├── 04-language-specific-patterns.md
       ├── 05-pattern-interactions.md
       ├── screenshots/
    3. Ensure index.md has inventory table with links to subsections
    4. Verify all file:line citations are present
    5. Verify confidence levels are assigned to every pattern
  </action>
  <constraints>
    - CRITICAL: index.md MUST contain pattern inventory table (LL-001)
    - CRITICAL: Each pattern category in its own file (LL-002)
  </constraints>
  <output>
    package_path: path to section-02-design-patterns/ directory
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
| Structure | 0.10 | Proper inventory table, subsection layout |
| Clarity | 0.15 | Clear pattern descriptions, role explanations |
| **Accuracy** | **0.35** | Correct pattern identification, valid file:line citations |
| Freshness | 0.10 | References current code state |
| Coverage | 0.10 | Breadth across pattern categories |

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
    <name>Pattern inventory table present</name>
    <verification>index.md contains table with Pattern, Type, Confidence, Location columns</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Evidence citations present</name>
    <verification>Every detected pattern has file:line citation</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `PHASE1_NOT_AVAILABLE` | Phase 1 output missing | Run Phase 1 scan first |
| `PHASE2_NOT_AVAILABLE` | Phase 2 test knowledge missing | Run Phase 2 test extraction first |
| `INVALID_OPERATION` | Operation not one of the 3 defined | Use: extract, validate, package |
| `CONTENT_NOT_FOUND` | content_path file does not exist | Verify extraction completed |
| `NO_PATTERNS_DETECTED` | No patterns found in codebase | Document "no canonical patterns found" with rationale |
| `MISSING_EVIDENCE` | Pattern lacks file:line citation | Re-scan source code for evidence |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Validation rules with [REQ]/[OPT] markers |
| `templates/extraction-prompts.md` | Per-subsection extraction guidance |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
