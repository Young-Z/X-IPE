# Feature Specification Writing Guide

This guide provides detailed templates, examples, and best practices for writing feature specifications.

---

## Specification Section Templates

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

Format: `- [ ] Criterion: [Specific, measurable condition]`

**Good Examples:**
- [ ] User can add up to 50 items to cart
- [ ] Cart total updates within 200ms of item addition
- [ ] Error message displays when stock is insufficient
- [ ] Session persists for 24 hours of inactivity

**Bad Examples (avoid):**
- [ ] Cart works correctly (too vague)
- [ ] System is fast (not measurable)
- [ ] User has good experience (subjective)

---

## Functional Requirements Template

### FR-N: [Requirement Name]

**Description:** [What the system must do]

**Details:**
- Input: [What data is provided]
- Process: [What happens]
- Output: [What result is produced]

**Example - FR-1: Add to Cart**

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

**Example:**
- Response time: < 200ms for cart operations
- Throughput: 1000 add-to-cart requests per second
- Concurrent users: 10,000 simultaneous sessions

### NFR-2: Security

- Authentication required: [Yes/No]
- Authorization level: [Role/permission required]
- Data encryption: [What data, how encrypted]

**Example:**
- Authentication required: Yes (JWT token)
- Authorization level: Registered customer or higher
- Data encryption: Credit card data encrypted with AES-256

### NFR-3: Scalability

- Expected growth: [User/data growth projections]
- Scaling strategy: [Horizontal/vertical]

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
|----------|------------|
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

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| Dashboard Main | HTML | [mockups/dashboard-v1.html](mockups/dashboard-v1.html) | Main dashboard layout |
| Settings Panel | HTML | [mockups/settings.html](mockups/settings.html) | User settings page |

> **Note:** UI/UX requirements below are derived from these mockups.
```

---

## Mockup-to-Specification Mapping

| Mockup Element | Specification Section |
|----------------|----------------------|
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

| Version | Date | Description |
|---------|------|-------------|
| v2.0 | 01-22-2026 | Major upgrade: xterm.js, session persistence, split-pane |
| v1.0 | 01-18-2026 | Initial specification |
```

**Rules:**
- Maintain ONE specification file per feature
- Add/update Version History table after the header
- Increment version in document header (v1.0 → v2.0)
- Update content in place with new version

---

## Specification Quality Checklist

- [ ] All acceptance criteria are testable
- [ ] User stories provide clear value
- [ ] Functional requirements are complete
- [ ] Non-functional requirements defined
- [ ] Dependencies clearly stated
- [ ] Edge cases identified
- [ ] Out of scope explicitly listed
- [ ] Mockups linked and analyzed (if applicable)
