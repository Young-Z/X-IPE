# Application RE — Single-Module Mixin

> Apply this mixin when the target codebase is a single-module project (one build target, one package).
> Merge these into the base playbook and collection templates when mixin_key: single-module.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| Single package.json | One `package.json` without `"workspaces"` | high |
| Single pyproject.toml | One `pyproject.toml` at root | high |
| Single build.gradle | One `build.gradle` without `settings.gradle` includes | high |
| Single Cargo.toml | One `Cargo.toml` without `[workspace]` | high |
| No sub-build files | No `*/package.json`, `*/pom.xml`, etc. in subdirectories | medium |

---

## Additional Sections

### Internal Layering Analysis

Add to Section 1 (Architecture Recovery):
- Identify internal layers (e.g., routes → controllers → services → repositories → models)
- Document layer boundaries and allowed dependency directions
- Identify cross-cutting concerns (logging, auth, validation)

### Package Structure Decomposition

Add to Section 5 (Code Structure):
- Deeper analysis of internal package/directory organization
- Map directory structure to architectural layers
- Document entry point tracing (main → app factory → router → handlers)

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Focus on internal layer decomposition rather than module boundaries
- Identify the application's layering pattern (MVC, hexagonal, clean architecture, etc.)
- Document dependency direction between layers
- Trace the primary request flow through layers
-->

### For Section 2 (Design Patterns)
<!-- ADDITIONAL PROMPTS:
- Focus on patterns within a single codebase (no cross-module patterns)
- Look for layering patterns: repository pattern, service pattern, middleware pattern
- Identify DI/IoC patterns used for wiring components
-->

### For Section 5 (Code Structure)
<!-- ADDITIONAL PROMPTS:
- Provide deeper naming convention analysis (since all files are in one project)
- Document internal package boundaries and conventions
- Identify "screaming architecture" — can you tell what the app does from directory names?
-->

### For Section 6 (Data Flow)
<!-- ADDITIONAL PROMPTS:
- Trace complete request flows from entry to response within the single module
- All data transformations happen within one codebase — document the full chain
- Identify sync vs. async boundaries within the application
-->
