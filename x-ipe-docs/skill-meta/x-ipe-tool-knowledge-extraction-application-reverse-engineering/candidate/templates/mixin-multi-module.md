# Application RE — Multi-Module Mixin

> Apply this mixin when the target codebase uses a multi-module build system (Maven modules, Gradle subprojects, Cargo workspaces).
> Merge these into the base playbook and collection templates when mixin_key: multi-module.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| Maven modules | `pom.xml` with `<modules>` section | high |
| Gradle subprojects | `settings.gradle` with `include` directives | high |
| Cargo workspace | `Cargo.toml` with `[workspace]` section | high |
| Go workspace | `go.work` file | high |
| SBT multi-project | `build.sbt` with `project` definitions | medium |
| Multiple build files | `*/build.gradle` or `*/pom.xml` in subdirectories | medium |

---

## Additional Sections

### Module Boundary Analysis

Add to Section 1 (Architecture Recovery):
- Document each module's purpose and public API
- Identify parent-child module relationships
- Map module dependency hierarchy (which modules depend on which)

### Inter-Module API Contracts

Add to Section 3 (API Contracts):
- Document interfaces/classes exported by each module
- Identify shared data models across modules
- Note module-level access control (public vs. internal packages)

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Create module dependency tree from build file declarations
- For each module: document public API surface and internal implementation
- Identify common/shared modules vs. application modules
- Document module initialization and wiring order
-->

### For Section 3 (API Contracts)
<!-- ADDITIONAL PROMPTS:
- Extract inter-module interfaces (Java interfaces, Go interfaces, Rust traits)
- Document which module implements which shared interfaces
- Identify data transfer objects (DTOs) shared across module boundaries
-->

### For Section 4 (Dependency Analysis)
<!-- ADDITIONAL PROMPTS:
- Build module-level dependency graph from build file declarations
- Distinguish compile-time vs. runtime module dependencies
- Identify modules with most dependents (high-impact modules)
- Check for circular module dependencies
-->

### For Section 5 (Code Structure)
<!-- ADDITIONAL PROMPTS:
- Document per-module directory structure
- Identify consistent vs. inconsistent module layouts
- Note module naming conventions
-->

### For Section 8 (Source Code Tests)
<!-- ADDITIONAL PROMPTS:
- Identify per-module test configurations
- Note integration tests that cross module boundaries
- Check for shared test fixtures in common/test modules
-->
