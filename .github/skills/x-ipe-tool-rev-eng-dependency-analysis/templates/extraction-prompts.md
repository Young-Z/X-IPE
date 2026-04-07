# Extraction Prompts — Section 4: Dependency Analysis

> These prompts guide AI agents during the `extract` operation.
> Each subsection has targeted prompts for systematic extraction.

---

## 4.1 Inter-Module Dependencies

### Primary Prompt

```
Trace all import/require/include/use statements across source files in {repo_path}.
For each import that crosses a module boundary (as defined by Phase 1 Section 5 module list):

1. Record: source_module, source_file:line, target_module, import_type
2. Classify import type:
   - direct: standard import of module/package
   - re-export: module imports and re-exports from another
   - dynamic: runtime import (importlib, require(), dynamic import())
   - type-only: TypeScript "import type" or Python TYPE_CHECKING imports
3. Build an adjacency list: { source_module → [target_module, ...] }
4. Count total edges per module pair (multiple imports = 1 edge with count)

Source priority: import statements > call-site analysis > test import patterns
```

### Follow-up Prompt

```
For each module pair with dependencies, document:
- The primary purpose of the dependency (what does the source need from the target?)
- Whether it's a direct or transitive dependency
- Whether the dependency is abstracted through an interface
```

---

## 4.2 External Library Dependencies

### Primary Prompt

```
Parse package manager files in {repo_path} to extract external dependencies:

1. Identify package manager:
   - Node.js: package.json + (package-lock.json | yarn.lock | pnpm-lock.yaml)
   - Python: (requirements.txt | pyproject.toml | setup.py) + (poetry.lock | uv.lock)
   - Java: pom.xml | build.gradle(.kts) + dependency tree output
   - Go: go.mod + go.sum
   - Rust: Cargo.toml + Cargo.lock

2. For each library, record:
   | Field | Source |
   |-------|--------|
   | Name | manifest file |
   | Declared version | manifest file (version range) |
   | Resolved version | lock file (exact version) |
   | Type | runtime / dev / optional / peer |
   | Purpose | 1-sentence based on library name + usage in code |

3. Cross-reference with actual imports:
   - Library declared but never imported → flag as "potentially unused"
   - Library imported but not declared → flag as "transitive / undeclared"
```

---

## 4.3 Circular Dependencies

### Primary Prompt

```
Using the inter-module adjacency list from 4.1, detect circular dependency chains:

1. Run depth-first cycle detection on the module dependency graph
2. For each cycle found:
   - List modules in order: A → B → C → A
   - For each edge in the cycle, cite the specific import file:line
   - Classify severity:
     * Tight cycle (2 modules): HIGH — likely design issue
     * Medium cycle (3-4 modules): MEDIUM — may indicate layering violation
     * Long chain (5+ modules): LOW — often transitive and harder to fix
3. If no cycles found, explicitly state: "No circular dependencies detected"
4. Suggest potential resolution strategies for each cycle
```

---

## 4.4 Critical Dependencies

### Primary Prompt

```
Analyze the dependency graph from 4.1 to identify critical hub modules:

1. Compute for each module:
   - Fan-in (in-degree): how many other modules depend on this module
   - Fan-out (out-degree): how many modules this module depends on
   - Betweenness: does this module sit on many shortest paths?

2. Rank modules by fan-in (descending)
3. Flag as "critical" if fan-in > 50% of total module count
4. For each critical module, list:
   - Module name and source directory
   - Fan-in count and list of dependent modules
   - Fan-out count and list of dependencies
   - Risk assessment: what breaks if this module changes?
5. Identify "God modules" with both high fan-in AND high fan-out
```

---

## 4.5 Dependency Visualization

### Primary Prompt

```
Create visual representations of the dependency structure:

1. Mermaid flowchart (inter-module):
   - Nodes = modules (sized or colored by fan-in)
   - Edges = dependency direction
   - Highlight circular dependencies in red
   - Highlight critical hubs with bold borders

2. Mermaid pie chart (dependency type distribution):
   - Slices: runtime, dev, optional, peer, type-only

3. Architecture DSL (dependency landscape):
   - Invoke x-ipe-tool-architecture-dsl with generate_landscape_view
   - Layers represent dependency tiers (core → services → adapters → entry points)
   - Show which modules sit in each tier based on dependency direction
   - External systems as boundary elements
```

---

## Cross-Cutting Guidance

- **Source priority:** Lock files > manifest files > import analysis > test patterns
- **Always cite file:line** for every dependency claim
- **Phase 1 reference:** Use Section 5 module list as the authoritative module boundary definition
- **Phase 2 reference:** Use Section 8 test imports to discover hidden dependencies (test-only coupling)
- **Unused dependencies:** Always flag but don't remove — this is reverse engineering, not refactoring
