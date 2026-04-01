# Application Reverse Engineering — Acceptance Criteria

> Per-section validation rules used by `validate_section` and `score_quality` operations.
> `[REQ]` = Required — must pass for section validation.
> `[OPT]` = Optional — contributes to quality score but not required for validation.

---

### Section 1: Architecture Recovery

- [ ] `[REQ]` At least 2 architecture levels documented (conceptual + logical minimum)
- [ ] `[REQ]` Module/component diagram present (Architecture DSL or Mermaid)
- [ ] `[REQ]` Architecture DSL used for conceptual and/or logical levels
- [ ] `[REQ]` Each module lists its responsibility (1-2 sentences)
- [ ] `[REQ]` Components reference specific source files/directories
- [ ] `[OPT]` Physical level class diagrams for key hierarchies
- [ ] `[OPT]` Data flow sequence diagrams for critical paths
- [ ] `[OPT]` Cross-reference with Phase 2 test knowledge noted

---

### Section 2: Design Pattern Detection

- [ ] `[REQ]` Pattern inventory table present with columns: Pattern, Type, Confidence, Location
- [ ] `[REQ]` Each pattern has confidence level (🟢 High / 🟡 Medium / 🔴 Low)
- [ ] `[REQ]` Each pattern has file:line evidence citation
- [ ] `[REQ]` At least 3 patterns analyzed (or documented "no canonical patterns found")
- [ ] `[OPT]` Pattern interaction map showing how patterns compose
- [ ] `[OPT]` Test-derived pattern evidence (mocks/stubs revealing boundaries)

---

### Section 3: API Contract Extraction

- [ ] `[REQ]` API inventory table present with endpoint count
- [ ] `[REQ]` Each API documents parameters with types
- [ ] `[REQ]` Each API documents return type / response schema
- [ ] `[REQ]` APIs grouped by module or service boundary
- [ ] `[REQ]` Each API cites implementing file:line
- [ ] `[OPT]` Error responses / exceptions documented
- [ ] `[OPT]` API versioning patterns noted

---

### Section 4: Dependency Analysis

- [ ] `[REQ]` Inter-module dependency graph present (imports between internal modules)
- [ ] `[REQ]` External library list with versions and purposes
- [ ] `[REQ]` Dependency type classified (import, runtime, dev, optional)
- [ ] `[OPT]` Circular dependencies identified (or confirmed none)
- [ ] `[OPT]` Critical/heavy dependencies highlighted
- [ ] `[OPT]` Architecture DSL dependency visualization

---

### Section 5: Code Structure Analysis

- [ ] `[REQ]` Root directory tree present (2-3 levels deep)
- [ ] `[REQ]` Directory-to-purpose mapping table
- [ ] `[REQ]` Naming conventions documented with examples
- [ ] `[REQ]` Module boundary markers identified
- [ ] `[OPT]` File count per directory (hot spot analysis)
- [ ] `[OPT]` Layering pattern identified and described

---

### Section 6: Data Flow / Protocol Analysis

- [ ] `[REQ]` At least 1 end-to-end request flow documented
- [ ] `[REQ]` Each flow step cites file:line
- [ ] `[REQ]` Data shape documented at each transformation step
- [ ] `[REQ]` Mermaid sequence diagram for critical flows
- [ ] `[OPT]` Event-driven flows documented (if applicable)
- [ ] `[OPT]` Communication protocols identified (REST, gRPC, WebSocket, etc.)

---

### Section 7: Technology Stack Identification

- [ ] `[REQ]` Languages listed with version constraints
- [ ] `[REQ]` Frameworks listed with configuration evidence
- [ ] `[REQ]` Build tools identified
- [ ] `[REQ]` Evidence file cited for each technology
- [ ] `[OPT]` Runtime/infrastructure tools documented
- [ ] `[OPT]` Testing frameworks identified (feeds Section 8)

---

### Section 8: Source Code Tests

- [ ] `[REQ]` All tests follow AAA structure (Arrange/Act/Assert)
- [ ] `[REQ]` All tests pass when executed
- [ ] `[REQ]` Line coverage ≥ 80% (or gaps documented with rationale)
- [ ] `[REQ]` Test framework matches project's detected framework
- [ ] `[REQ]` Source code was never modified to fix failing tests
- [ ] `[REQ]` Test knowledge extraction mapping documented (test → module → behavior)
- [ ] `[OPT]` Edge case tests for error handling paths
- [ ] `[OPT]` Coverage visualization screenshot included
