# Feature Breakdown - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: E-Commerce Platform (Multi-Epic Breakdown)

**Input:** User story or high-level requirement for an e-commerce platform

### Step 2: Epic Assessment

```
Scope signals:
  - Estimated features: ~13 features across 5 capability areas
  - Domain diversity: 3 distinct domains (Product, Cart/Checkout, User)
  - Dependency clusters: Product features tightly coupled; Cart/Checkout tightly coupled

Decision: 3 Epics (one per domain)
  - EPIC-001: Product Management (catalog, search, details, inventory)
  - EPIC-002: Shopping & Checkout (cart, checkout, payment, confirmation)
  - EPIC-003: User Accounts (registration, profile, settings)

Epic-level dependencies:
  - EPIC-002 depends on EPIC-001 (cart needs product catalog)
  - EPIC-003 is independent (can develop in parallel)
```

### Step 4: Feature Identification (per Epic)

```
EPIC-001 — Product Management:
  - FEATURE-001-A: Product Catalog Display (MVP)
  - FEATURE-001-B: Product Search & Filter
  - FEATURE-001-C: Product Details Page
  - FEATURE-001-D: Inventory Management

EPIC-002 — Shopping & Checkout:
  - FEATURE-002-A: Add to Cart (MVP)
  - FEATURE-002-B: Cart Management
  - FEATURE-002-C: Checkout Flow
  - FEATURE-002-D: Payment Integration
  - FEATURE-002-E: Order Confirmation

EPIC-003 — User Accounts:
  - FEATURE-003-A: User Registration (MVP)
  - FEATURE-003-B: User Profile
  - FEATURE-003-C: User Settings

Folder structure:
  x-ipe-docs/requirements/EPIC-001/FEATURE-001-A/
  x-ipe-docs/requirements/EPIC-001/FEATURE-001-B/
  x-ipe-docs/requirements/EPIC-002/FEATURE-002-A/
  ...
```

### Output

```yaml
category: requirement-stage
epic_ids: [EPIC-001, EPIC-002, EPIC-003]
epic_count: 3
feature_ids: [FEATURE-001-A, FEATURE-001-B, ..., FEATURE-003-C]
feature_count: 12
```

---

## Example 2: API Integration (Single Epic)

**Input:** "Integrate with third-party shipping providers"

### Step 2: Epic Assessment

```
Scope signals:
  - Estimated features: 5 (interface + 3 providers + UI)
  - Domain diversity: 1 domain (shipping integration)
  - Dependency clusters: all depend on shared interface

Decision: Single Epic
  - EPIC-020: Shipping Integration
```

### Feature Breakdown

```
EPIC-020 — Shipping Integration:
  - FEATURE-020-A: Shipping Provider Interface (MVP)
  - FEATURE-020-B: FedEx Integration
  - FEATURE-020-C: UPS Integration
  - FEATURE-020-D: USPS Integration
  - FEATURE-020-E: Rate Comparison UI

Dependencies: All B/C/D depend on A; E depends on B/C/D

Output:
  epic_ids: [EPIC-020]
  epic_count: 1
  feature_count: 5
```

---

## Example 3: From Change Request (NEW_FEATURE)

**Input:** CR classified as NEW_FEATURE for bulk import

### Step 2: Epic Assessment

```
Scope signals:
  - Estimated features: 4 (parser, validation, errors, UI)
  - Domain diversity: 1 domain (import pipeline)
  - Links to existing EPIC-001 (Product Management)

Decision: Single Epic (EPIC-025 — Bulk Import)
```

### Feature Breakdown

```
EPIC-025 — Bulk Import:
  - FEATURE-025-A: CSV Import Parser (MVP)
  - FEATURE-025-B: Import Validation Pipeline
  - FEATURE-025-C: Import Error Handling
  - FEATURE-025-D: Import Progress UI

Cross-Epic dependency: All depend on FEATURE-001-D (Inventory — in EPIC-001)

Output:
  source: Change Request
  epic_ids: [EPIC-025]
  feature_count: 4
```

---

## Example 4: Granularity Guidelines

**When breaking down features, ensure appropriate granularity:**

### Too Coarse ❌
```
FEATURE-001: E-Commerce Platform
  - Scope: Everything
  - Problem: Impossible to estimate, test, or deliver incrementally
```

### Too Fine ❌
```
FEATURE-001: Add "Add to Cart" Button
FEATURE-002: Add Cart Icon in Header
FEATURE-003: Show Item Count in Cart Icon
  - Problem: Too many dependencies, overhead exceeds value
```

### Just Right ✓
```
FEATURE-005: Add to Cart Functionality
  - Includes: Button, API call, cart update, UI feedback
  - Deliverable: User can add products to cart
  - Testable: Clear acceptance criteria
  - Estimable: 3-5 story points
```

### Sizing Guidelines

| Size | Story Points | Characteristics |
|------|--------------|-----------------|
| Small | 1-2 | Single component, few tests |
| Medium | 3-5 | 2-3 components, clear scope |
| Large | 8-13 | Multiple components, consider splitting |
| Too Large | 13+ | MUST split into smaller features |

---

## Example 5: Parent Feature Deduplication After Split

**Input:** FEATURE-001 (Product Catalog) has 25 ACs and must be split.

### Execution Flow

```
1. FEATURE-001 split into (within EPIC-001):
   - FEATURE-001-A: Product Listing (covers FR-001.1, FR-001.2, FR-001.3)
   - FEATURE-001-B: Product Search (covers FR-001.4, FR-001.5)
   - FEATURE-001-C: Product Filtering (covers FR-001.6, FR-001.7, FR-001.8)

2. Dedup Check — Coverage Table:

   | Parent FR/AC | Covered By | Status |
   |-------------|------------|--------|
   | FR-001.1 | FEATURE-001-A | Covered |
   | FR-001.2 | FEATURE-001-A | Covered |
   | FR-001.3 | FEATURE-001-A | Covered |
   | FR-001.4 | FEATURE-001-B | Covered |
   | FR-001.5 | FEATURE-001-B | Covered |
   | FR-001.6 | FEATURE-001-C | Covered |
   | FR-001.7 | FEATURE-001-C | Covered |
   | FR-001.8 | FEATURE-001-C | Covered |

3. Result: 100% coverage → Remove parent FEATURE-001 from board
   Log: "Parent FEATURE-001 fully covered by A/B/C, removed"

4. Output:
   parent_features_removed: [FEATURE-001]
   dedup_gaps: []
```

### Partial Coverage Example

```
If FR-001.9 (Inventory Display) was NOT covered by any sub-feature:

   | FR-001.9 | — | Gap |

   Result: Keep parent FEATURE-001 with note:
   "Partially split — uncovered: FR-001.9 (Inventory Display)"
   Flag for human review.

   parent_features_removed: []
   dedup_gaps: [{feature: FEATURE-001, uncovered: [FR-001.9]}]
```

---

## Example 6: Epic Grouping Decision — Borderline Case

**Input:** "Build a project management tool with task tracking, team chat, and file storage"

### Step 2: Epic Assessment

```
Scope signals:
  - Estimated features: ~12 (4 per domain)
  - Domain diversity: 3 clearly distinct domains
  - Dependency clusters:
    - Task tracking: standalone core
    - Team chat: references tasks for linking
    - File storage: referenced by tasks and chat
  - Team boundaries: chat needs real-time expertise; file storage needs infra

Decision: 3 Epics
  - EPIC-030: Task Management (foundation — no deps)
  - EPIC-031: File Storage (depends on EPIC-030 for task attachments)
  - EPIC-032: Team Chat (depends on EPIC-030 for task linking, EPIC-031 for file sharing)

Rationale: 3 domains × ~4 features each = 12 features total.
  Each domain is independently testable and could be developed by separate teams.
  File Storage is a shared service used by both Tasks and Chat.
```
