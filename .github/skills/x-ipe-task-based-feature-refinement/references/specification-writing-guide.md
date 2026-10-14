# Feature Specification Writing Guide

This guide provides detailed templates, examples, and best practices for writing feature specifications.

## Delta-first refinement and ownership

Use current source/specification/mockup SHA256 and approved delta, not dates alone.
Reuse fresh breakdown findings and confirmed unchanged decisions. Missing coverage
needs a baseline; changes invalidate affected evidence. Ask only actual unresolved
questions, up to 3-5 per batch without padding; human asks the human within
skill; full DAO and hybrid use the common representative contract. No repeated interview.

Preserve stable US/FR/NFR/AC IDs, established EN/ZH language and unaffected bytes.
Append new IDs after reserved history; changed/retired criteria retain CR rationale
and old-to-new mapping. Do not relabel outdated tests/design as current. Every
source acceptance item is mapped to a specification AC or an approved deferral.
Use the existing full scaffold; do not drop NFRs/edge/scope sections for small work.
Material open questions and unconfirmed changed scope block completion.

Exactly one specification in its resolved feature folder. Legacy FEATURE-{nnn}
and new FEATURE-{nnn}-{X} are valid; board specification_link precedes validated
EPIC/FEATURE then legacy FEATURE fallback. Explicit broken/wrong-feature/escaping
or ambiguous links block. Do not copy a legacy spec to a second folder on CR.
Lifecycle owns task/category/feature status/link updates, Git and routing; this
guide adds no child registration, board-status mutation or successor execution.

---

## Specification Section Templates

### Goal / Subgoal Coverage

Use the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
in the existing specification, not a separate goal store. Map stakeholder desired
observable outcome to parent/source, story and leaf GWT ACs plus validation plan
and outcome gaps. Explain credible indirect enabling value and all-required versus
selected bounded alternatives; do not make every possible means a required goal.
Coherent scope, not fixed minimums or three-goal caps, bounds the map. Existing
FR/US/AC IDs suffice; optional doc-local G anchors never change board schema.

For new/changed scope coverage is mandatory; measurable if known, qualitative
scenario valid otherwise. Legacy goals inferred from explicit story so-that must
carry inferred label/source, never new confirmation. Missing/ambiguous intent
blocks the pertinent claim, not rewriting history or unrelated delivery evidence.
Keep means adaptable within constraints; scope/acceptance changes need authorized
CR/human intent. A parent delta invalidates affected evidence, not every test.
not measured outcome can coexist with verified engineering delivery; observed
stakeholder outcome needs real observation, not a fixture or planned test.

### Overview Section

Write 2-3 paragraphs covering:

1. **What** - What this feature does
2. **Why** - Why it's needed
3. **Who** - Who will use it

### User Stories Template

```markdown
As a [user type], I want to [action/goal], so that [benefit/value].
```

**Examples:**

- As a **customer**, I want to **save items to my cart**, so that **I can purchase them later**.
- As an **admin**, I want to **view all user orders**, so that **I can track sales and resolve issues**.
- As a **developer**, I want to **access API documentation**, so that **I can integrate with the service**.
- As a **support agent**, I want to **search customer tickets**, so that **I can quickly find and resolve issues**.

### Acceptance Criteria Template

Format: Table with Given/When/Then criterion and Test Type column, grouped by AC ID prefix:

```markdown
### AC-XXX-01: {AC Group Name}

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-XXX-01a | GIVEN user is on cart page WHEN user adds item THEN cart count increments by 1 | UI |
| AC-XXX-01b | GIVEN cart has items WHEN total is recalculated THEN displayed total matches the approved pricing rules | UI |
| AC-XXX-01c | GIVEN valid product payload WHEN POST /api/cart/items THEN 201 returned with item details | API |
| AC-XXX-01d | GIVEN quantity > 99 WHEN addToCart() is called THEN validation error is returned | Unit |
```

**AC Format:** Every criterion MUST use **Given/When/Then (GWT)** syntax:

- `GIVEN [precondition/context] WHEN [action/event] THEN [expected outcome]`
- Multi-clause: use AND to chain (e.g., `GIVEN ... AND ... WHEN ... THEN ... AND ...`)

**Test Type values:** UI, API, Unit, Integration

**Good Examples:**

| AC ID | Criterion (Given/When/Then) | Test Type |
| --- | --- | --- |
| AC-001-01a | GIVEN user is on cart page WHEN user clicks "Add to Cart" 50 times THEN all 50 items are in cart | UI |
| AC-001-01b | GIVEN item is added to cart WHEN cart total renders THEN the displayed total includes the item price | UI |
| AC-001-02a | GIVEN valid item payload WHEN POST /api/cart/items THEN 201 returned with item details | API |
| AC-001-02b | GIVEN item is out of stock WHEN POST /api/cart/items THEN 409 returned with error message | API |
| AC-001-03a | GIVEN price is 10.005 WHEN calculateTotal() runs THEN result rounds to 10.01 | Unit |
| AC-001-04a | GIVEN cart has 3 items WHEN service AND DB restart THEN cart still has 3 items after recovery | Integration |

**Bad Examples (avoid):**

- Cart works correctly (too vague, no GWT)
- System is fast (not measurable, no GWT)
- User has good experience (subjective, no GWT)
- User can add items to cart (missing GIVEN/WHEN/THEN structure)
- Missing Test Type column (downstream testing cannot route)
- Using "Manual" as Test Type (all ACs must be automatable)

---

## Functional Requirements Template

### FR-N: [Requirement Name]

**Description:** [What the system must do]

**Details:**

- Input: [What data is provided]
- Process: [What happens]
- Output: [What result is produced]

### Example - FR-1: Add to Cart

**Description:** System must allow users to add products to their shopping cart.

**Details:**

- Input: Product ID, quantity (1-99)
- Process: Validate stock availability, add to cart, recalculate total
- Output: Updated cart with new item, total price displayed

---

## Non-Functional Requirements Templates

### NFR-1: Performance

- Response time: [X seconds/milliseconds]
- Throughput: [X requests per second]
- Concurrent users: [X users]

**Example:** Use a sourced performance target only when known and justified;
otherwise record the measurement gap. Do not infer arbitrary latency, throughput
or concurrency thresholds from this template. Observable qualitative scenarios
are valid acceptance evidence; a material performance ambiguity remains a question.

### NFR-2: Security

- Authentication required: [Yes/No]
- Authorization level: [Role/permission required]
- Data encryption: [What data, how encrypted]

**Example:**

- Authentication required: Yes, authenticated customer identity
- Authorization level: Registered customer or higher
- Data protection: payment data protected per approved compliance requirements;
  do not invent implementation algorithms or regulatory thresholds

### NFR-3: Scalability

- Expected growth: [User/data growth projections]
- Required capacity/availability: [Measured requirement, not chosen architecture]

---

## UI/UX Requirements Template

**Wireframes/Mockups:** [Link or embed]

**User Flows:**

1. User navigates to [page/screen]
2. User performs [action]
3. System displays [result]

**UI Elements:**

- Button: [Label, action]
- Form fields: [List with validation rules]
- Error messages: [List with conditions]

**Example User Flow - Checkout:**

1. User navigates to cart page
2. User clicks "Proceed to Checkout"
3. System validates cart items in stock
4. System displays shipping address form
5. User enters address and clicks "Continue"
6. System displays payment options

---

## Business Rules Template

### BR-N: [Rule Name]

**Rule:** [Clear statement of business rule]

**Examples:**

- Only authenticated users can add items to cart
- Prices must be positive numbers
- Discounts cannot exceed 90%
- Free shipping applies to orders over $50
- Refunds must be processed within 14 days

---

## Edge Cases & Constraints Template

### Edge Case N: [Scenario]

**Scenario:** [Describe unusual or boundary condition]  
**Expected Behavior:** [How system should respond]

**Common Edge Cases to Consider:**

| Category | Edge Cases |
| --- | --- |
| User Session | Session expires during operation, multiple tabs open |
| Data | Empty state, maximum limit reached, invalid format |
| Network | Connection lost, slow response, timeout |
| Concurrency | Simultaneous edits, race conditions |
| Boundary | Min/max values, empty inputs, special characters |

**Example:**

- User session expires during checkout → Redirect to login, preserve cart
- Database connection lost → Show error, queue for retry
- Invalid input format → Return validation error with details

---

## Out of Scope Template

Format: `- [What is NOT included and why/when planned]`

**Examples:**

- Social media login (only email/password for v1.0)
- Multi-factor authentication (planned for v2.0)
- Mobile app support (web only for v1.0)
- International shipping (domestic only for launch)

---

## Dependencies Section Templates

### Internal Dependencies

Format: `- **FEATURE-XXX:** [Why needed, what it provides]`

**Example:**

- **FEATURE-001:** User authentication - provides user identity for cart association
- **FEATURE-003:** Product catalog - provides product data for cart items

### External Dependencies

Format: `- **Name:** [Purpose, version if known]`

**Example:**

- **Stripe SDK v3.2:** Payment processing
- **SendGrid API:** Email notifications
- **Redis 7.0:** Session storage

---

## Linked Mockups Section Template

```markdown
## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Dashboard Main | HTML | [x-ipe-docs/requirements/{EPIC-ID}/mockups/dashboard-v1.html](x-ipe-docs/requirements/{EPIC-ID}/mockups/dashboard-v1.html) | Main dashboard layout | current | 03-11-2026 |
| Settings Panel | HTML | [x-ipe-docs/requirements/{EPIC-ID}/mockups/settings.html](x-ipe-docs/requirements/{EPIC-ID}/mockups/settings.html) | User settings page | current | 03-11-2026 |

> **Path Convention:** Use full project-root-relative paths for mockup links (e.g., `x-ipe-docs/requirements/EPIC-XXX/mockups/file.html`).
> This enables the link preview feature (IDEA-033) — clicking opens an in-app DeliverableViewer modal.
> Do NOT use relative paths like `../mockups/` or `../../mockups/`.
>
> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.
>
> **Conflict Resolution:** Compare content, approved scope and SHA256 revisions.
> Record the actual conflict decision under current mode policy. A newer date
> alone never authorizes a scope change or spec/mockup precedence.
```

**Status values:** `current` (actively used for ACs) or `outdated` (directional only)

**Linked Date:** MM-DD-YYYY when first linked or changed, preserved on unchanged
resume. Provenance only, not semantic precedence. Scope-filter existing feature
copies and shared Epic/linked idea sources; copy only missing authorized files
when actually needed and never overwrite foreign bytes. Current in-scope elements
must map to stories, UI requirements and comparison ACs (UI type); unmatched
in-scope current elements block. Outdated mockups are directional only and must
not create comparison ACs. Preserve valid shared project-root-relative links.

---

## Mockup-to-Specification Mapping

| Mockup Element | Specification Section |
| --- | --- |
| Layout/Components | UI/UX Requirements → UI Elements |
| Forms/Inputs | Functional Requirements + Validation Rules |
| Buttons/Actions | User Stories + Acceptance Criteria |
| Navigation | User Flows |
| Error States | Edge Cases & Constraints |
| Data Display | Functional Requirements → Output |
| Loading States | Edge Cases → Empty/Loading |
| Responsive Hints | NFR → Accessibility |

---

## Mockup Analysis Checklist

When analyzing mockups, extract:

- [ ] Layout structure and component hierarchy
- [ ] User interaction patterns (clicks, hovers, inputs)
- [ ] Visual design elements (colors, spacing, typography)
- [ ] Form fields, validation rules, error states
- [ ] Navigation flows and page transitions
- [ ] Responsive behavior hints
- [ ] Loading states
- [ ] Empty states
- [ ] Error states

---

## Version History Format

```markdown
## Version History

| Version | Date | Description | Change Request |
| --- | --- | --- | --- |
| v2.0 | 01-22-2026 | Approved major redesign | {actual CR link} |
| v1.0 | 01-18-2026 | Initial specification | N/A |
```

**Rules:**

- Maintain ONE specification file per feature
- Add/update Version History table after the header
- Use approved minor v1.1/v1.2 for additive CR or major v2.0 for redesign
- Preserve older history/CR records; unchanged resume does not bump version
- Update affected sections in place with stable language and IDs

## Acceptance traceability and completeness

The scaffold's traceability table maps Source Requirement/FR/NFR → User Story →
AC ID → current scoped mockup element/status → primary validation plan and actual
CR/coverage/deferral decision. Keep exact source IDs, not invented REQ identities.
GWT tables have unique stable AC IDs and exactly one UI/API/Unit/Integration Test
Type, never Manual. Preserve Chinese prose with GIVEN/WHEN/THEN tokens; do not
translate stable criteria merely to standardize the document. Assertions must be
specific, measurable and automatable; unresolved thresholds need a question.

Keep full stories, functional input/process/output, measurable NFRs, UI flows,
internal/external dependencies, business rules, boundary/error/loading/empty
behavior, out-of-scope exclusions with reasons and WHAT-not-HOW considerations.
N/A requires rationale. Human/hybrid completeness and completion/route confirmation
is revision-bound; explicit human approval binds in every mode and DAO cannot
invent human authority. Real workflow outputs are specification
and scalar feature-docs-folder; verify both actual artifacts and readback, not
merely writer exit. The lifecycle verifies the returned board-link handoff.

---

## Specification Quality Checklist

- [ ] All acceptance criteria are testable
- [ ] All acceptance criteria have a Test Type assigned (UI/API/Unit/Integration)
- [ ] User stories provide clear value
- [ ] Functional requirements are complete
- [ ] Non-functional requirements defined
- [ ] Dependencies clearly stated
- [ ] Edge cases identified
- [ ] Out of scope explicitly listed
- [ ] Mockups linked and analyzed (if applicable)
