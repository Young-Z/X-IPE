# Feature Breakdown Guidelines Reference

This document contains detailed guidelines, examples, and rules for feature breakdown. Referenced from SKILL.md.

---

## Epic Granularity Assessment

### When to Create Multiple Epics

Before breaking requirements into features, assess whether the scope warrants multiple Epics. Epics group related features into cohesive, domain-aligned containers.

### Scope Signal Evaluation

| Signal | Question | Measurement |
|--------|----------|-------------|
| Feature count | How many features will likely emerge? | Count distinct deliverables from requirements |
| Domain diversity | How many distinct functional domains? | Count capability areas that could be owned independently |
| Dependency clusters | Do features group with tight internal deps? | Identify clusters where features reference each other more than external features |
| Team boundaries | Would different expertise areas own different parts? | Count distinct skill sets needed (frontend, backend, data, infra) |

### Epic Grouping Decision Matrix

| Domains | Est. Features | Decision | Rationale |
|---------|---------------|----------|-----------|
| 1 | ≤7 | Single Epic | Small enough to manage as one unit |
| 1 | 8-15 | Single Epic, consider split | Split only if clear sub-domains emerge |
| 2-3 | ≤7 | Single Epic | Few features despite multiple domains |
| 2-3 | 8-15 | 2-3 Epics (one per domain) | Each domain has enough features to justify separate tracking |
| 2-3 | >15 | 2-3 Epics (one per domain) | Must split — too many features for one container |
| 4+ | Any | Multiple Epics | Each domain = one Epic; merge small domains if <3 features |

### Epic Naming Conventions

- **Domain-based:** "{Domain} {Capability}" — e.g., "Product Management", "Order Processing"
- **Clear scope:** Name should convey what the Epic contains
- **Avoid generic:** Do not use "Miscellaneous" or "Other" — assign features to real domains

### Epic-Level Dependencies

| Pattern | Description | Example |
|---------|-------------|---------|
| Foundation Epic | Core infrastructure that other Epics build on | "Data Layer" → "Product Management" → "Order Processing" |
| Parallel Epics | Independent domains that can be developed concurrently | "User Management" ∥ "Product Catalog" |
| Sequential Epics | One domain must complete before another starts | "Auth" → "User Profiles" → "Social Features" |

Rules:
1. **No circular Epic dependencies** — if Epic A depends on Epic B, B cannot depend on A
2. **Foundation Epics first** — Epics with no dependencies should be prioritized
3. **Minimize cross-Epic feature dependencies** — features within an Epic should primarily depend on other features in the same Epic

---

## Feature Sizing Guidelines

### Complexity Evaluation Heuristics

Before identifying features, evaluate the proposed feature's complexity using these heuristics:

**AC Count Thresholds:**

| AC Count | Action | Rationale |
|----------|--------|-----------|
| Under 10 | Likely single feature | Small enough to refine, design, implement in one pass |
| 10-20 | Evaluate | Split if ACs span multiple distinct capabilities or layers |
| Over 20 | MUST split | Too large for a single feature — split along natural boundaries |

**Scope Dimension Assessment:**

| Dimension | Question | Split Signal |
|-----------|----------|-------------|
| Technical layers | How many layers touched? (service, API, CLI, UI, config) | 3+ layers = consider split |
| AC groups | Are ACs organized into distinct groups? | Groups map to sub-features |
| New files | How many new files/modules estimated? | 5+ new files = consider split |
| User capabilities | How many distinct user-facing capabilities? | Each capability = potential feature |
| Dependency depth | Is there a clear foundation vs consumer pattern? | Foundation should be separate MVP |

**Natural Split Boundary Patterns:**

| Pattern | Description | Example |
|---------|-------------|---------|
| Foundation + Consumers | Core service used by multiple higher-level features | Registry (foundation) → Init, Translation, Migration (consumers) |
| Pipeline stages | Sequential processing stages | Parse → Validate → Transform → Deploy |
| Per-variant | Same pattern applied to different targets | Copilot adapter, OpenCode adapter, Claude adapter |
| Read vs Write | Query/display separated from mutation/creation | Config API (read) vs Config Migration (write) |

### Too Large (Split)

Examples of features that need splitting:
- "Complete E-Commerce System" → Split into Cart, Payment, Shipping, etc.
- "User Management" → Split into Registration, Profile, Settings, etc.
- "Full Admin Dashboard" → Split into User Admin, Content Admin, Analytics, etc.

### Good Size

Features appropriately scoped:
- "Shopping Cart Management"
- "Payment Processing with Stripe"
- "Email Notification System"
- "User Profile Management"
- "JWT Authentication"

### Too Small (Combine)

Features that should be combined:
- "Add to Cart Button" → Part of Shopping Cart feature
- "Validate Email Format" → Part of User Registration feature
- "Display Error Message" → Part of Form Validation feature

---

## Feature ID Assignment Rules

### ID Format

```
Epic: EPIC-{NNN}
Feature: FEATURE-{NNN}-{X}
```

Where NNN is a zero-padded 3-digit number matching the parent Epic (001, 002, etc.)
and X is an uppercase letter suffix (A, B, C, ...).

Rules:
1. Feature {NNN} ALWAYS matches parent Epic {NNN}
2. Suffix assigned alphabetically: first feature = A, second = B
3. Scan x-ipe-docs/requirements/ for highest existing EPIC-{NNN} to determine next number
4. NEVER use `EPIC-{NNN}` as a Feature ID — they are separate concepts

### Assignment Rules

1. **Sequential Assignment** - IDs assigned in order of creation
2. **No Gaps** - Do not skip numbers
3. **No Reuse** - Deleted features keep their IDs
4. **Part-Specific Ranges** - When using parts, each part covers a range

### Continuation Numbering

When adding features to an existing set:
```
1. Query feature board for highest existing FEATURE-XXX
2. Start new features at next number
3. Example: If FEATURE-011 exists, next is FEATURE-012
```

---

## Priority Matrix

### Priority Levels

| Priority | Description | Typical Features |
|----------|-------------|------------------|
| P0 (Critical) | MVP must-have | Core loop, auth, primary workflow |
| P1 (High) | Important for launch | Secondary workflows, error handling |
| P2 (Medium) | Nice to have | Convenience features, polish |
| P3 (Low) | Future consideration | Advanced features, optimizations |

---

## Feature Naming Conventions

### Good Names

- **Specific:** "JWT Authentication" not "Login"
- **Action-oriented:** "User Profile Management" not "User Profile"
- **Technology-agnostic (usually):** "Payment Processing" not "Stripe Integration"
- **Clear scope:** "Order History Display" not "Orders"

### Bad Names

- **Too vague:** "User Stuff", "Main Feature"
- **Too technical:** "REST API Controller Layer"
- **Too broad:** "Everything Users Need"
- **Ambiguous:** "Processing", "Handler", "Manager"

---

## Feature Dependency Patterns

### Sequential Dependencies

```
FEATURE-001: User Authentication (no deps)
    └── FEATURE-002: User Profile (depends on FEATURE-001)
            └── FEATURE-003: User Settings (depends on FEATURE-002)
```

### Parallel with Shared Dependency

```
                    ┌── FEATURE-002: User Service (depends on FEATURE-001)
FEATURE-001: Database Layer ──┤
                    └── FEATURE-003: Product Service (depends on FEATURE-001)
```

### Dependency Rules

1. **No Circular Dependencies** - A cannot depend on B if B depends on A
2. **Foundation First** - Core/shared features have no dependencies
3. **Clear Reason** - Document why dependency exists
4. **Minimal Dependencies** - Only list direct dependencies, not transitive
5. **DAG Structure** - Dependency graph must be a Directed Acyclic Graph

---

## Mockup Processing Details

### Auto-Detection Procedure

```
1. IF mockup_list is NOT provided or empty:
   a. Check if requirement came from an Idea (look for idea folder reference)
   b. IF idea folder exists:
      - Scan: x-ipe-docs/ideas/{idea-folder}/mockups/
      - IF mockups found → Auto-populate mockup_list from found files

2. IF mockup_list is STILL empty after auto-detection:
   - Log: "No mockups found - skipping mockup processing"
   - Proceed to next step
```

### Mockup Rules

- If mockup_list is N/A or empty, skip mockup processing
- Use relative paths from the document location
- Preserve original file extension when copying
- Create mockups folder only if mockup_list has items

---

## Part File Management

### When Parts Exist

| Action | Target |
|--------|--------|
| Read requirements | Current active part (highest number) |
| Write Feature List | Current active part |
| Update Index | requirement-details-index.md |

---

## Integration with Feature Board Management

This skill **MUST** call the feature-board-management skill to create features on the board.

### Call Format

```
CALL x-ipe+feature+feature-board-management skill:
  operation: create_or_update_features
  features:
    - feature_id: FEATURE-001-A
      epic_id: EPIC-001
      title: User Authentication
      version: v1.0
      description: JWT-based user authentication
      dependencies: []
    - feature_id: FEATURE-001-B
      epic_id: EPIC-001
      title: User Profile
      version: v1.0
      description: User profile management
      dependencies: [FEATURE-001-A]
```
