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
   - FEATURE-001: Product Catalog Display
   - FEATURE-002: Product Search & Filter
   - FEATURE-003: Product Details Page
   - FEATURE-004: Inventory Management

   Shopping Cart:
   - FEATURE-005: Add to Cart
   - FEATURE-006: Cart Management (update qty, remove)
   - FEATURE-007: Cart Persistence

   Checkout & Payment:
   - FEATURE-008: Checkout Flow
   - FEATURE-009: Payment Integration
   - FEATURE-010: Order Confirmation

4. Define Dependencies:

   ```
   FEATURE-001 (Catalog) 
        ↓
   FEATURE-005 (Add to Cart) → FEATURE-006 (Cart Management)
        ↓                              ↓
   FEATURE-007 (Persistence) ←─────────┘
        ↓
   FEATURE-008 (Checkout) → FEATURE-009 (Payment)
        ↓
   FEATURE-010 (Confirmation)
   ```

5. Update features.md:

   | ID | Name | Status | Dependencies | Priority |
   |----|------|--------|--------------|----------|
   | FEATURE-001 | Product Catalog | Draft | None | P1 |
   | FEATURE-002 | Product Search | Draft | FEATURE-001 | P2 |
   | FEATURE-005 | Add to Cart | Draft | FEATURE-001 | P1 |
   | FEATURE-008 | Checkout Flow | Draft | FEATURE-007 | P1 |

6. Create Feature Folders:
   - x-ipe-docs/requirements/FEATURE-001/
   - x-ipe-docs/requirements/FEATURE-002/
   - ... (one folder per feature)

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
  - x-ipe-docs/requirements/FEATURE-001/
  - x-ipe-docs/requirements/FEATURE-002/
  - ... (10 feature folders)
```

---

## Example 2: API Integration Feature Breakdown

**Input:** "Integrate with third-party shipping providers"

```
1. Analyze Scope:
   - Single integration point, multiple providers
   - Need abstraction layer

2. Break Down:
   - FEATURE-020: Shipping Provider Interface
   - FEATURE-021: FedEx Integration
   - FEATURE-022: UPS Integration
   - FEATURE-023: USPS Integration
   - FEATURE-024: Rate Comparison UI

3. Define Dependencies:

   FEATURE-020 (Interface) ──┬──→ FEATURE-021 (FedEx)
                             ├──→ FEATURE-022 (UPS)
                             └──→ FEATURE-023 (USPS)
                                      ↓
                             FEATURE-024 (Rate UI)

4. Output:
   features_created: 5
   base_dependency: FEATURE-020
```

---

## Example 3: From Change Request (NEW_FEATURE)

**Input:** CR classified as NEW_FEATURE for bulk import

```
1. Receive from Change Request task:
   - CR: "Add bulk import to product management"
   - Classification: NEW_FEATURE

2. Break Down:
   - FEATURE-025: CSV Import Parser
   - FEATURE-026: Import Validation Pipeline
   - FEATURE-027: Import Error Handling
   - FEATURE-028: Import Progress UI

3. Link to Existing:
   - All depend on FEATURE-004 (Product Management - existing)

4. Update features.md with new entries

5. Output:
   source: Change Request
   features_created: 4
   linked_to_existing: FEATURE-004
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
