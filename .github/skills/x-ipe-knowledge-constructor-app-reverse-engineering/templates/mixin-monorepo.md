# Application RE — Monorepo Mixin

> Apply this mixin when the target codebase is structured as a monorepo with multiple packages/projects.
> Merge these overlays into the base playbook when repo_type: monorepo.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| Lerna config | `lerna.json` | high |
| pnpm workspaces | `pnpm-workspace.yaml` | high |
| Nx config | `nx.json` | high |
| Turborepo | `turbo.json` | high |
| Yarn workspaces | `package.json` with `"workspaces"` field | high |
| Multiple package.json | `packages/*/package.json` or `apps/*/package.json` | medium |
| Bazel workspace | `WORKSPACE` or `WORKSPACE.bazel` | medium |

---

## Additional Sections

### Cross-Package Dependency Map

Add to Section 5 (Dependency Analysis):
- Map inter-package dependencies (which packages import from which)
- Identify shared packages (used by ≥3 other packages)
- Document package publish order / build order
- Detect version alignment strategy (fixed, independent, grouped)

### Per-Package Module View

Add to Section 1 (Architecture Recovery):
- Create Architecture DSL module view per package
- Document package boundary contracts (exported APIs)
- Identify shared utilities packages vs. application packages

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Create a top-level landscape view showing all packages and their relationships
- For each package: create a module view showing internal structure
- Document package boundary: what is exported vs. internal
- Identify cross-cutting concerns (shared configs, common utilities)
-->

### For Section 2 (API Contract Extraction)
<!-- ADDITIONAL PROMPTS:
- Document inter-package API contracts (package A exports used by package B)
- Identify shared type definitions across packages
- Note any API versioning between packages
-->

### For Section 5 (Dependency Analysis)
<!-- ADDITIONAL PROMPTS:
- Build cross-package dependency graph (package-level, not file-level)
- Identify circular package dependencies
- Document shared dependency versions across packages
- Analyze workspace hoisting strategy and its implications
-->

### For Section 6 (Infrastructure Analysis)
<!-- ADDITIONAL PROMPTS:
- Document workspace root structure vs. per-package structure
- Identify shared configuration files (tsconfig, eslint, prettier)
- Note build orchestration pattern (parallel, topological, pipeline)
-->

### For Section 8 (Testing Strategy)
<!-- ADDITIONAL PROMPTS:
- Identify per-package test configurations
- Note shared test utilities or fixtures across packages
- Check for integration tests that span package boundaries
-->
