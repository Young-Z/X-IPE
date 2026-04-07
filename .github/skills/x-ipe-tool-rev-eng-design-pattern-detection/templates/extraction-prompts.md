# Design Pattern Detection — Extraction Prompts

> Per-subsection extraction guidance for Section 2 (Design Pattern Detection).
> HTML comments contain the actual prompts — the extractor reads these to guide analysis.

---

## 2.1 Pattern Inventory

<!-- EXTRACTION PROMPTS:
- After scanning all pattern categories, compile a summary inventory table:
  | Pattern | Type | Confidence | Location | Role |
  |---------|------|------------|----------|------|
  | Factory Method | Creational | 🟢 | src/services/factory.py:42 | Creates service instances based on config |
- Sort by confidence level (🟢 first, then 🟡, then 🔴)
- Link each pattern to its detailed subsection file
- If fewer than 3 patterns found, document "no canonical patterns found" with rationale

SOURCE PRIORITY:
1. Results from subsection scans (2.2–2.6)
2. Phase 2 test knowledge (patterns revealed by test structure)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: All subsection scans complete
- Output type: index.md with summary table
-->

---

## 2.2 Creational Patterns

<!-- EXTRACTION PROMPTS:
- Factory Pattern:
  a. Search for functions/methods named: create_*, build_*, make_*, new_*, *Factory
  b. Search for classes with "Factory" in name or factory method pattern
  c. Check DI containers / service registries that construct objects
  d. Confidence: 🟢 if explicit Factory class/function; 🟡 if constructor delegation; 🔴 if simple new/init
- Singleton Pattern:
  a. Search for module-level instances, cached singletons
  b. Python: module-level variables, __new__ override, @singleton decorator
  c. TypeScript/JS: module.exports of single instance, static getInstance()
  d. Go: sync.Once patterns, package-level var + init()
  e. Confidence: 🟢 if explicit singleton mechanism; 🟡 if module-level caching; 🔴 if just a global
- Builder Pattern:
  a. Search for fluent method chaining (methods returning `this`/`self`)
  b. Search for step-by-step object construction with .build() terminal
  c. Confidence: 🟢 if explicit Builder class; 🟡 if fluent API; 🔴 if just method chaining
- For each detected pattern:
  a. Cite file:line evidence
  b. Assign confidence level with rationale
  c. Describe the pattern's role in the system
  d. Note any deviations from canonical implementation

SOURCE PRIORITY:
1. Source code (class definitions, factory functions, constructors)
2. DI/IoC container configuration
3. Phase 2 test fixtures (test setup often reveals factory/builder usage)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (class/function structure) + Phase 2 (test fixtures)
- Output type: subfolder (01-creational-patterns.md)
-->

---

## 2.3 Structural Patterns

<!-- EXTRACTION PROMPTS:
- Adapter Pattern:
  a. Search for wrapper classes/functions around external APIs or libraries
  b. Look for interface translation: converting one API to another
  c. Common indicators: classes named *Adapter, *Wrapper, *Client, *Gateway
  d. Confidence: 🟢 if explicit adapter interface; 🟡 if wrapping with translation; 🔴 if simple delegation
- Decorator Pattern:
  a. Python: @decorator syntax, functools.wraps usage
  b. TypeScript/JS: Higher-order functions, middleware chains (express, koa)
  c. Go: Function wrappers, http.Handler chains
  d. Class decorators: additional behavior without modifying original
  e. Confidence: 🟢 if classic decorator pattern; 🟡 if middleware chain; 🔴 if simple wrapper
- Facade Pattern:
  a. Search for simplified interfaces that delegate to multiple subsystems
  b. Look for "service" classes that orchestrate multiple lower-level components
  c. Common indicators: methods that call 3+ other services/components
  d. Confidence: 🟢 if explicit facade class; 🟡 if service orchestration; 🔴 if just aggregation
- For each: cite file:line, assign confidence, describe role

SOURCE PRIORITY:
1. Source code (class hierarchies, wrapper functions)
2. Middleware registration/configuration
3. Phase 2 test mocks (mocked dependencies reveal adapter/facade boundaries)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (module boundaries) + Phase 2 (mock analysis)
- Output type: subfolder (02-structural-patterns.md)
-->

---

## 2.4 Behavioral Patterns

<!-- EXTRACTION PROMPTS:
- Observer Pattern:
  a. Search for event emitter/listener registrations
  b. Python: signals (Django), event hooks, callback lists
  c. TypeScript/JS: EventEmitter, addEventListener, on/off/emit, RxJS Observables
  d. Go: channel-based pub/sub, callback function fields
  e. Confidence: 🟢 if explicit event system; 🟡 if callback registration; 🔴 if just function passing
- Strategy Pattern:
  a. Search for pluggable algorithm implementations behind a common interface
  b. Look for configuration-driven dispatch (strategy selected by config/env)
  c. Common indicators: interface + multiple implementations, map of handlers
  d. Confidence: 🟢 if explicit strategy interface; 🟡 if config dispatch; 🔴 if just if/switch
- Command Pattern:
  a. Search for handler/command dispatch systems
  b. Look for action objects, command queues, undo/redo stacks
  c. Common indicators: execute() method, handler maps, dispatch functions
  d. Confidence: 🟢 if explicit command objects; 🟡 if handler dispatch; 🔴 if just function maps
- For each: cite file:line, assign confidence, describe role

SOURCE PRIORITY:
1. Source code (event systems, handler registrations, interface implementations)
2. Configuration files (strategy selection, handler mapping)
3. Phase 2 test knowledge (event test assertions, strategy swap tests)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (module structure) + Phase 2 (test patterns)
- Output type: subfolder (03-behavioral-patterns.md)
-->

---

## 2.5 Language-Specific Patterns

<!-- EXTRACTION PROMPTS:
- TypeScript-Specific:
  a. Discriminated unions (type narrowing via literal types)
  b. Type guards (is keyword, assertion functions)
  c. Module augmentation / declaration merging
  d. Branded types for type safety
- Python-Specific:
  a. Context managers (__enter__/__exit__, @contextmanager)
  b. Descriptors (__get__/__set__/__delete__)
  c. Metaclasses (type manipulation)
  d. Protocol classes (structural subtyping)
  e. Dataclass patterns
- Go-Specific:
  a. Functional options pattern (WithXxx functions)
  b. Interface embedding (composition over inheritance)
  c. Error wrapping (fmt.Errorf with %w)
  d. Table-driven tests
- For each: cite file:line evidence, describe the pattern's purpose

SOURCE PRIORITY:
1. Source code (idiomatic patterns specific to detected language from Phase 1 Section 7)
2. Type definition files (.d.ts, .pyi, interfaces)
3. Phase 2 test patterns (language idioms often visible in test code)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 Section 7 (detected languages)
- Output type: subfolder (04-language-specific-patterns.md)
-->

---

## 2.6 Pattern Interactions

<!-- EXTRACTION PROMPTS:
- Identify composed patterns:
  a. Factory + Strategy: factory creates strategy instances
  b. Observer + Mediator: events routed through central mediator
  c. Decorator + Chain of Responsibility: middleware stacks
  d. Builder + Factory: builder used inside factory methods
- Map pattern dependency chains: which patterns depend on others
- Document interaction points: where in the code patterns connect
- Create interaction summary (prose or diagram)

SOURCE PRIORITY:
1. Cross-referencing detected patterns from subsections 2.2-2.5
2. Source code (where pattern implementations reference each other)
3. Phase 2 integration tests (tests often exercise pattern compositions)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: All pattern subsections (2.2-2.5) complete
- Output type: subfolder (05-pattern-interactions.md)
-->
