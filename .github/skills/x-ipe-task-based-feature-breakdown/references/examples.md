# Feature Breakdown - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: E-Commerce Platform Feature Breakdown

**Input:** User story or high-level requirement for an e-commerce platform

### Execution Flow

```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. Identify Major Capabilities:
   - Product Management
   - Shopping Cart
   - Checkout & Payment
   - User Accounts
   - Order Management

3. Break Down Each Capability:

   Product Management:
   - FEATURE-001-A: Product Catalog Display
   - FEATURE-001-B: Product Search & Filter
   - FEATURE-001-C: Product Details Page
   - FEATURE-001-D: Inventory Management

   Shopping Cart:
   - FEATURE-002-A: Add to Cart
   - FEATURE-002-B: Cart Management (update qty, remove)
   - FEATURE-002-C: Cart Persistence

   Checkout & Payment:
   - FEATURE-003-A: Checkout Flow
   - FEATURE-003-B: Payment Integration
   - FEATURE-003-C: Order Confirmation

4. Define Dependencies:

   ```
   FEATURE-001-A (Catalog) 
        ↓
   FEATURE-002-A (Add to Cart) → FEATURE-002-B (Cart Management)
        ↓                              ↓
   FEATURE-002-C (Persistence) ←─────────┘
        ↓
   FEATURE-003-A (Checkout) → FEATURE-003-B (Payment)
        ↓
   FEATURE-003-C (Confirmation)
   ```

5. Update features.md:

   | ID | Name | Status | Dependencies | Priority |
   |----|------|--------|--------------|----------|
   | FEATURE-001-A | Product Catalog | Draft | None | P1 |
   | FEATURE-001-B | Product Search | Draft | FEATURE-001-A | P2 |
   | FEATURE-002-A | Add to Cart | Draft | FEATURE-001-A | P1 |
   | FEATURE-003-A | Checkout Flow | Draft | FEATURE-002-C | P1 |

6. Create Feature Folders (under Epic):
   - x-ipe-docs/requirements/EPIC-001/FEATURE-001-A/
   - x-ipe-docs/requirements/EPIC-001/FEATURE-001-B/
   - ... (one folder per feature, under parent Epic)

7. Resume Task Flow from x-ipe-workflow-task-execution skill
```

### Output

```yaml
category: requirement-stage
next_task_based_skill: Feature Refinement
require_human_review: Yes

breakdown_summary: |
  Identified 10 features across 5 capability areas:
  - Product Management: 4 features
  - Shopping Cart: 3 features
  - Checkout & Payment: 3 features
  
dependencies_mapped: Yes
priority_assigned: Yes

task_output_links:
  - x-ipe-docs/planning/features.md
  - x-ipe-docs/requirements/EPIC-001/FEATURE-001-A/
  - x-ipe-docs/requirements/EPIC-001/FEATURE-001-B/
  - ... (10 feature folders across 3 Epics)
```

---

## Example 2: API Integration Feature Breakdown

**Input:** "Integrate with third-party shipping providers"

```
1. Analyze Scope:
   - Single integration point, multiple providers
   - Need abstraction layer

2. Break Down:
   - FEATURE-020-A: Shipping Provider Interface
   - FEATURE-020-B: FedEx Integration
   - FEATURE-020-C: UPS Integration
   - FEATURE-020-D: USPS Integration
   - FEATURE-020-E: Rate Comparison UI

3. Define Dependencies:

   FEATURE-020-A (Interface) ──┬──→ FEATURE-020-B (FedEx)
                             ├──→ FEATURE-020-C (UPS)
                             └──→ FEATURE-020-D (USPS)
                                      ↓
                             FEATURE-020-E (Rate UI)

4. Output:
   features_created: 5
   base_dependency: FEATURE-020-A
```

---

## Example 3: From Change Request (NEW_FEATURE)

**Input:** CR classified as NEW_FEATURE for bulk import

```
1. Receive from Change Request task:
   - CR: "Add bulk import to product management"
   - Classification: NEW_FEATURE

2. Break Down:
   - FEATURE-025-A: CSV Import Parser
   - FEATURE-025-B: Import Validation Pipeline
   - FEATURE-025-C: Import Error Handling
   - FEATURE-025-D: Import Progress UI

3. Link to Existing:
   - All depend on FEATURE-004-A (Product Management - existing)

4. Update features.md with new entries

5. Output:
   source: Change Request
   features_created: 4
   linked_to_existing: FEATURE-004-A
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
1. FEATURE-001 split into:
   - FEATURE-001-A: Product Listing (covers FR-001.1, FR-001.2, FR-001.3)
   - FEATURE-001-B: Product Search (covers FR-001.4, FR-001.5)
   - FEATURE-001-C: Product Filtering (covers FR-001.6, FR-001.7, FR-001.8)

2. Dedup Check — Coverage Table:

   | Parent FR/AC | Covered By | Status |
   |-------------|------------|--------|
   | FR-001.1 | FEATURE-001-A (FR-001-A.1) | ✅ Covered |
   | FR-001.2 | FEATURE-001-A (FR-001-A.2) | ✅ Covered |
   | FR-001.3 | FEATURE-001-A (FR-001-A.3) | ✅ Covered |
   | FR-001.4 | FEATURE-001-B (FR-001-B.1) | ✅ Covered |
   | FR-001.5 | FEATURE-001-B (FR-001-B.2) | ✅ Covered |
   | FR-001.6 | FEATURE-001-C (FR-001-C.1) | ✅ Covered |
   | FR-001.7 | FEATURE-001-C (FR-001-C.2) | ✅ Covered |
   | FR-001.8 | FEATURE-001-C (FR-001-C.3) | ✅ Covered |

3. Result: 100% coverage → Remove FEATURE-001 from:
   - requirement-details.md (parent section removed)
   - features.md (via feature-board-management: archive FEATURE-001)
   - Log: "Parent FEATURE-001 fully covered by A/B/C, removed"

4. Output:
   parent_features_removed: [FEATURE-001]
   dedup_gaps: []
```

### Partial Coverage Example

```
If FR-001.9 (Inventory Display) was NOT covered by any sub-feature:

   | FR-001.9 | — | ❌ Gap |

   Result: Keep FEATURE-001 with note:
   "Partially split — uncovered: FR-001.9 (Inventory Display)"
   Flag for human review.

   parent_features_removed: []
   dedup_gaps: [{feature: FEATURE-001, uncovered: [FR-001.9]}]
```
