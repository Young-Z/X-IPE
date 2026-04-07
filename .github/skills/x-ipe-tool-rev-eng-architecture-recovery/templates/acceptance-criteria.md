# Architecture Recovery — Acceptance Criteria

> Validation rules for Section 1 (Architecture Recovery) used by `validate` operation.
> `[REQ]` = Required — must pass for section validation.
> `[OPT]` = Optional — contributes to quality score but not required for validation.

---

### Section 1: Architecture Recovery

**Required Criteria:**

- [ ] `[REQ]` At least 2 architecture levels documented (conceptual + logical minimum)
- [ ] `[REQ]` Module/component diagram present (Architecture DSL or Mermaid)
- [ ] `[REQ]` Architecture DSL used for conceptual and/or logical levels (via x-ipe-tool-architecture-dsl)
- [ ] `[REQ]` Each module lists its responsibility (1-2 sentences)
- [ ] `[REQ]` Components reference specific source files/directories

**Optional Criteria:**

- [ ] `[OPT]` Physical level class diagrams for key hierarchies (Mermaid classDiagram)
- [ ] `[OPT]` Data flow sequence diagrams for critical paths (Mermaid sequenceDiagram)
- [ ] `[OPT]` Cross-reference with Phase 2 test knowledge noted (test imports, mock boundaries)

---

### Per-Subsection Criteria

#### 1.1 Conceptual Level — Application Landscape

- [ ] `[REQ]` Architecture DSL landscape view present (`@startuml landscape-view`)
- [ ] `[REQ]` External systems and user types identified
- [ ] `[OPT]` System boundaries clearly delineated

#### 1.2 Logical Level — Module/Component View

- [ ] `[REQ]` Architecture DSL module view present (`@startuml module-view`)
- [ ] `[REQ]` Layers defined with modules assigned to each layer
- [ ] `[REQ]` Module columns sum to 12 per layer (Architecture DSL grid rule)
- [ ] `[REQ]` Each module has responsibility description
- [ ] `[REQ]` Each module references source directory

#### 1.3 Physical Level — Class/File Structure

- [ ] `[OPT]` Mermaid classDiagram blocks for key class hierarchies
- [ ] `[OPT]` Inheritance, composition, and interface relationships shown
- [ ] `[OPT]` Key classes reference their source file paths

#### 1.4 Data Flow Level — Request/Response Paths

- [ ] `[OPT]` Mermaid sequenceDiagram for at least 1 critical path
- [ ] `[OPT]` Each flow step cites file:line
- [ ] `[OPT]` Cross-referenced with Phase 2 integration test flows
