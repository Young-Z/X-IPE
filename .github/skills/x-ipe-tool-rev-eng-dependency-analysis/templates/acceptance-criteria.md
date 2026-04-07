# Acceptance Criteria — Section 4: Dependency Analysis

## Required Criteria [REQ]

### REQ-4.1: Inter-Module Dependency Graph

- **Rule:** An inter-module dependency graph MUST be present
- **Method:** `file_exists` → `01-inter-module-deps.md`
- **Validation:** File contains at least one dependency table or adjacency list
- **Evidence:** Each edge cites source file:line of the import/require/include statement
- **Fail if:** No inter-module dependencies documented at all

### REQ-4.2: External Library List with Versions

- **Rule:** External library dependencies MUST be listed with resolved versions
- **Method:** `table_parse` → `02-external-library-deps.md`
- **Validation:** Table contains columns: Library Name, Version, Dependency Type, Purpose
- **Evidence:** Versions sourced from lock file (preferred) or manifest file
- **Fail if:** Libraries listed without version numbers

### REQ-4.3: Dependency Type Classification

- **Rule:** Every dependency MUST be classified by type
- **Method:** `section_parse` → all subsection files
- **Validation:** Each dependency has one of: `import`, `runtime`, `dev`, `optional`, `peer`, `type-only`, `dynamic`
- **Evidence:** Classification matches actual usage in source code
- **Fail if:** Dependency entries missing type classification

---

## Optional Criteria [OPT]

### OPT-4.4: Circular Dependencies Identified

- **Rule:** Circular dependency chains SHOULD be detected and documented
- **Method:** `file_exists` → `03-circular-dependencies.md`
- **Validation:** File contains either cycle documentation or explicit "No circular dependencies detected"
- **Evidence:** Each cycle lists participating modules and the specific import file:lines forming the cycle
- **Incomplete if:** File missing entirely

### OPT-4.5: Critical/Heavy Dependencies Highlighted

- **Rule:** Hub modules with high fan-in SHOULD be identified
- **Method:** `table_parse` → `04-critical-dependencies.md`
- **Validation:** Table contains: Module Name, Fan-In Count, Fan-Out Count, Dependents
- **Evidence:** Fan-in counts match actual import analysis
- **Incomplete if:** No hub analysis present

### OPT-4.6: Architecture DSL Dependency Visualization

- **Rule:** A dependency landscape visualization SHOULD use Architecture DSL
- **Method:** `section_parse` → `05-dependency-visualization.md`
- **Validation:** Contains at least one Architecture DSL block (via x-ipe-tool-architecture-dsl)
- **Evidence:** DSL block accurately represents the extracted dependency structure
- **Incomplete if:** Only Mermaid diagrams present without Architecture DSL

---

## Validation Summary

| ID | Criterion | Level | Method |
|----|-----------|-------|--------|
| REQ-4.1 | Inter-module dependency graph | Required | file_exists + table_parse |
| REQ-4.2 | External library list with versions | Required | table_parse |
| REQ-4.3 | Dependency type classified | Required | section_parse |
| OPT-4.4 | Circular dependencies identified | Optional | file_exists |
| OPT-4.5 | Critical hub modules highlighted | Optional | table_parse |
| OPT-4.6 | Architecture DSL visualization | Optional | section_parse |

---

## Status Definitions

- **PASS:** Criterion fully satisfied with evidence
- **FAIL:** Criterion attempted but content is incorrect or insufficient
- **INCOMPLETE:** Criterion not addressed (content missing)
