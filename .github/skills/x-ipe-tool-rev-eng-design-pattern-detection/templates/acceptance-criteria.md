# Design Pattern Detection — Acceptance Criteria

> Validation rules for Section 2 (Design Pattern Detection) used by `validate` operation.
> `[REQ]` = Required — must pass for section validation.
> `[OPT]` = Optional — contributes to quality score but not required for validation.

---

### Section 2: Design Pattern Detection

**Required Criteria:**

- [ ] `[REQ]` Pattern inventory table present with columns: Pattern, Type, Confidence, Location
- [ ] `[REQ]` Each pattern has confidence level (🟢 High / 🟡 Medium / 🔴 Low)
- [ ] `[REQ]` Each pattern has file:line evidence citation
- [ ] `[REQ]` At least 3 patterns analyzed (or documented "no canonical patterns found" with rationale)

**Optional Criteria:**

- [ ] `[OPT]` Pattern interaction map showing how patterns compose
- [ ] `[OPT]` Test-derived pattern evidence (mocks/stubs revealing boundaries)

---

### Per-Subsection Criteria

#### 2.1 Pattern Inventory (index.md)

- [ ] `[REQ]` Summary table with all detected patterns
- [ ] `[REQ]` Each row has: Pattern name, Type (Creational/Structural/Behavioral/Language-Specific), Confidence (🟢/🟡/🔴), Location (file:line), Role (1-line description)
- [ ] `[REQ]` Links to detailed subsection for each pattern category

#### 2.2 Creational Patterns

- [ ] `[REQ]` Factory pattern scanned: create_*, build_*, *Factory classes
- [ ] `[REQ]` Singleton pattern scanned: instance caching, module-level state
- [ ] `[REQ]` Builder pattern scanned: fluent chaining, step-by-step construction
- [ ] `[OPT]` Other creational patterns (Prototype, Abstract Factory) checked

#### 2.3 Structural Patterns

- [ ] `[REQ]` Adapter pattern scanned: wrapping external APIs, interface translation
- [ ] `[REQ]` Decorator pattern scanned: function decorators, middleware chains
- [ ] `[REQ]` Facade pattern scanned: simplified interfaces hiding subsystems
- [ ] `[OPT]` Other structural patterns (Proxy, Composite, Bridge) checked

#### 2.4 Behavioral Patterns

- [ ] `[REQ]` Observer pattern scanned: event emitters, pub/sub, callbacks
- [ ] `[REQ]` Strategy pattern scanned: pluggable algorithms, config-driven dispatch
- [ ] `[REQ]` Command pattern scanned: handler dispatch, action objects
- [ ] `[OPT]` Other behavioral patterns (State, Template Method, Chain of Responsibility) checked

#### 2.5 Language-Specific Patterns

- [ ] `[OPT]` Language-specific idioms documented (context managers, type guards, functional options)
- [ ] `[OPT]` Each idiom cites file:line evidence

#### 2.6 Pattern Interactions

- [ ] `[OPT]` Composed patterns identified (e.g., Factory + Strategy)
- [ ] `[OPT]` Pattern dependency chains mapped
