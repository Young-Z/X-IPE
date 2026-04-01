# Application Reverse Engineering — Playbook Template

> This playbook defines the standard extraction layout for application reverse engineering.
> Sections are ordered by extraction phase, not by final document numbering.
> The extractor processes sections in phase order: Phase 1 → Phase 2 → Phase 3.

---

## Extraction Phases

| Phase | Sections | Purpose | Output Type |
|-------|----------|---------|-------------|
| 1-Scan | 5, 7 | Quick structural scan of codebase | Inline (Markdown tables) |
| 2-Tests | 8 | Collect/generate/run tests to build knowledge | Subfolder (executable files) |
| 3-Deep | 1, 2, 3, 4, 6 | Deep analysis using scan + test knowledge | Subfolder (Markdown + diagrams) |

---

## Phase 1 — Scan

### 5. Code Structure Analysis
<!-- PHASE: 1-Scan | OUTPUT: inline -->

Analyze the project's file and directory structure to understand organizational patterns.

**Subsections:**
- **5.1 Project Layout** — Root-level directory tree with purpose annotations
- **5.2 Directory Structure** — Table mapping each directory to its role and key files
- **5.3 Naming Conventions** — Patterns in file/class/function naming (e.g., `*_service.py`, `*Controller.java`)
- **5.4 Module Boundaries** — How the project separates concerns (packages, namespaces, directories)

**Output Format:** Markdown tables (directory → purpose, convention → examples)

---

### 7. Technology Stack Identification
<!-- PHASE: 1-Scan | OUTPUT: inline -->

Identify all technologies, frameworks, and tools used in the project.

**Subsections:**
- **7.1 Languages** — Programming languages with version constraints
- **7.2 Frameworks** — Application frameworks with configuration evidence
- **7.3 Build Tools** — Build systems, package managers, task runners
- **7.4 Runtime & Infrastructure** — Runtime versions, containers, CI/CD tools
- **7.5 Testing Frameworks** — Test runners, assertion libraries, coverage tools

**Output Format:** Markdown tables (technology → version → purpose → evidence file)

---

## Phase 2 — Tests

### 8. Source Code Tests
<!-- PHASE: 2-Tests | OUTPUT: subfolder | SPECIAL: executable files -->

Collect existing tests, generate missing tests, execute all tests, and extract test-derived knowledge that feeds Phase 3 analysis.

**Subsections:**
- **8.1 Test Collection** — Scan and catalog all existing test files
- **8.2 Test Framework Detection** — Identify test framework, assertion style, fixture patterns
- **8.3 AAA Test Generation** — Generate missing tests in Arrange/Act/Assert format
- **8.4 Test Execution** — Run all tests, record pass/fail results
- **8.5 Coverage Analysis** — Measure line coverage, identify gaps (target ≥80%)
- **8.6 Knowledge Extraction** — Map test insights to architecture sections

**Output Structure:**
```
section-08-source-code-tests/
├── _index.md              # Test suite overview, framework, summary
├── screenshots/           # Coverage report visualizations
├── tests/                 # Executable test files
│   ├── test_module_a.{ext}
│   └── ...
└── coverage-report.md     # Per-module coverage breakdown
```

**Ground Truth Rule:** Source code is NEVER modified to fix failing tests. Tests adapt to actual code behavior.

---

## Phase 3 — Deep Analysis

### 1. Architecture Recovery
<!-- PHASE: 3-Deep | OUTPUT: subfolder | DEPENDS: Phase 1 scan + Phase 2 test knowledge -->

Recover the system's architecture at multiple abstraction levels.

**Subsections:**
- **1.1 Conceptual Level** — Application landscape view (Architecture DSL)
- **1.2 Logical Level** — Module/component view with responsibilities (Architecture DSL)
- **1.3 Physical Level** — Class/file level structure (Mermaid class diagrams)
- **1.4 Data Flow Level** — Request/response paths through the system (Mermaid sequence diagrams)

**Output Structure:**
```
section-01-architecture-recovery/
├── _index.md              # Architecture overview summary
├── screenshots/           # Rendered diagrams
├── conceptual-landscape.md    # Architecture DSL landscape view
├── logical-module-view.md     # Architecture DSL module view
├── physical-classes.md        # Mermaid class diagrams
└── data-flow-sequences.md     # Mermaid sequence diagrams
```

**Tools:** Use `x-ipe-tool-architecture-dsl` for conceptual and logical levels.

---

### 2. Design Pattern Detection
<!-- PHASE: 3-Deep | OUTPUT: subfolder | DEPENDS: Phase 1 scan + Phase 2 test knowledge -->

Identify software design patterns used in the codebase with confidence scoring.

**Subsections:**
- **2.1 Pattern Inventory** — Table of all detected patterns with confidence levels
- **2.2 Per-Pattern Evidence** — Detailed analysis per pattern with file:line citations
- **2.3 Confidence Scoring** — 🟢 High (clear implementation), 🟡 Medium (partial match), 🔴 Low (possible)
- **2.4 Pattern Interactions** — How detected patterns compose/interact

**Output Structure:**
```
section-02-design-patterns/
├── _index.md              # Pattern inventory table
├── screenshots/           # Pattern diagrams
└── pattern-{name}.md      # Per-pattern evidence file
```

---

### 3. API Contract Extraction
<!-- PHASE: 3-Deep | OUTPUT: subfolder | DEPENDS: Phase 1 scan + Phase 2 test knowledge -->

Extract internal and external API contracts with request/response schemas.

**Subsections:**
- **3.1 Internal APIs** — Module-to-module function/class interfaces
- **3.2 External APIs** — HTTP endpoints, CLI commands, message handlers
- **3.3 Per-API-Group Files** — Grouped by module or service boundary
- **3.4 Schema Documentation** — Request/response types, validation rules

**Output Structure:**
```
section-03-api-contracts/
├── _index.md              # API overview with endpoint count
├── screenshots/           # API flow diagrams
└── api-{group-name}.md    # Per-group contract files
```

---

### 4. Dependency Analysis
<!-- PHASE: 3-Deep | OUTPUT: subfolder | DEPENDS: Phase 1 scan + Phase 2 test knowledge -->

Map inter-module and external library dependencies.

**Subsections:**
- **4.1 Inter-Module Dependencies** — Which modules depend on which (import/call graph)
- **4.2 External Library Dependencies** — Third-party libraries with versions and purposes
- **4.3 Per-Module Dependency Files** — Detailed dependency breakdown per module
- **4.4 Dependency Visualization** — Mermaid + Architecture DSL dependency graphs

**Output Structure:**
```
section-04-dependency-analysis/
├── _index.md              # Dependency overview with counts
├── screenshots/           # Dependency graphs
└── deps-{module-name}.md  # Per-module dependency files
```

**Tools:** Use `x-ipe-tool-architecture-dsl` for dependency landscape view.

---

### 6. Data Flow / Protocol Analysis
<!-- PHASE: 3-Deep | OUTPUT: subfolder | DEPENDS: Phase 1 scan + Phase 2 test knowledge -->

Trace how data moves through the system from entry to exit.

**Subsections:**
- **6.1 Request Flows** — End-to-end request processing paths
- **6.2 Event Propagation** — Event-driven communication patterns
- **6.3 Data Transformation Chains** — How data is transformed between layers
- **6.4 Protocol Details** — Communication protocols (HTTP, gRPC, WebSocket, message queues)

**Output Structure:**
```
section-06-data-flow/
├── _index.md              # Data flow overview
├── screenshots/           # Flow diagrams
└── flow-{name}.md         # Per-flow trace files
```
