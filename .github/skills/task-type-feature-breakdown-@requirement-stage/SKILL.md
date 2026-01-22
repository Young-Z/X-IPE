---
name: task-type-feature-breakdown-@requirement-stage
description: Break requirements into high-level features and create feature list in requirement-details.md. Calls feature-board-management to initialize feature tracking. Use when requirements are gathered and need to be split into discrete features. Triggers on requests like "break down features", "split into features", "create feature list".
---

# Task Type: Feature Breakdown

## Purpose

Break user requests into high-level features by:
1. Analyzing requirement documentation
2. Identifying feature boundaries
3. Creating feature list in requirement-details.md
4. Calling feature-board-management to create features on board

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Feature Breakdown |
| Category | requirement-stage |
| Next Task Type | Feature Refinement |
| Require Human Review | Yes |

---

## Skill Output

This skill MUST return these attributes to the Task Data Model:

```yaml
Output:
  status: completed | blocked
  next_task_type: task-type-feature-refinement-@feature-stage
  require_human_review: Yes
  task_output_links: [docs/requirements/requirement-details.md]
  
  # Dynamic attributes for requirement-stage
  requirement_id: REQ-XXX
  feature_ids: [FEATURE-001, FEATURE-002, FEATURE-003]
  feature_count: 3
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Requirement documentation exists (user request or requirement doc) | Yes |

---

## Execution Procedure

### Step 1: Analyze Requirements

**Action:** Review requirement information to identify features

```
IF docs/requirements/requirement-details.md exists:
  1. Read existing requirement summary
  2. Identify features from requirements
ELSE:
  1. Analyze user request
  2. Extract requirements
  3. Identify features from request
```

**Look for:**
- Verbs (actions the system must perform)
- Nouns (entities the system must manage)
- Boundaries (where one function ends and another begins)
- User goals and workflows

**Feature Identification Criteria:**

1.  **Prioritize MVP:** The first feature MUST be the "Minimum Runnable Feature". It should be small but sufficient to demonstrate the core value loop (even if imperfect).
2.  **Iterative Expansion:** Subsequent features should build upon the first one, adding complexity or breadth.
3.  **Single Responsibility:** Each feature does one thing well.
4.  **Independent:** Can be developed/tested in isolation (mostly).
5.  **Deliverable Value:** Provides value when completed.
6.  **Reasonable Size:** Fits within a development sprint.

| Consideration | Description |
|---------------|-------------|
| MVP Requirement | First feature = Runnable core loop |
| Complexity | Start simple, then add complexity |
| Dependencies | Minimize cross-feature dependencies |

---

### Step 2: Create/Update Requirement Summary

**Action:** Create or update `docs/requirements/requirement-details.md`

**File Structure:**
```markdown
# Requirement Summary

> Requirement ID: REQ-XXX  
> Created: MM-DD-YYYY  
> Last Updated: MM-DD-YYYY

## Overview
[Brief description of the requirement/epic, 2-3 paragraphs]

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-001 | User Authentication | v1.0 | JWT-based user authentication with login, logout, token refresh | None |
| FEATURE-002 | User Profile | v1.0 | User profile management and settings | FEATURE-001 |
| FEATURE-003 | Password Reset | v1.0 | Password reset functionality via email | FEATURE-001 |

---

## Feature Details

### FEATURE-001: User Authentication

**Version:** v1.0  
**Brief Description:** Implement JWT-based user authentication with login, logout, and token refresh capabilities

**Acceptance Criteria:**
- [ ] User can login with email/password
- [ ] User receives JWT token on successful login
- [ ] Token can be refreshed before expiration
- [ ] User can logout and invalidate token
- [ ] Invalid credentials return appropriate error

**Dependencies:**
- None

**Technical Considerations:**
- JWT token expiration: 1 hour
- Refresh token expiration: 7 days
- Password hashing: bcrypt with salt rounds = 10
- Rate limiting: Max 5 login attempts per minute

---

### FEATURE-002: User Profile
[Similar structure for each feature]

---

### FEATURE-003: Password Reset  
[Similar structure for each feature]

---
```

**Feature Details Template (for each feature):**
```markdown
### {FEATURE-ID}: {Feature Title}

**Version:** v{X.Y}  
**Brief Description:** [1-2 sentence description]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Dependencies:**
- {FEATURE-ID}: [Why needed]
- None (if no dependencies)

**Technical Considerations:**
- [Key technical decisions or constraints]
- [Performance requirements]
- [Security considerations]
```

**Rules:**
- Keep brief description under 50 words
- List 3-7 acceptance criteria per feature
- Note dependencies using Feature IDs
- Technical considerations are hints for design

---

### Step 3: Call Feature Board Management

**Action:** Create features on the feature board

```
CALL @feature-stage+feature-board-management skill:
  operation: create_or_update_features
  features:
    - feature_id: FEATURE-001
      title: User Authentication
      version: v1.0
      description: JWT-based user authentication with login, logout, token refresh
      dependencies: []
    - feature_id: FEATURE-002
      title: User Profile  
      version: v1.0
      description: User profile management and settings
      dependencies: [FEATURE-001]
    [... etc for all features]
```

**Output:** Features created on docs/requirements/features.md with status "Planned"

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `docs/requirements/requirement-details.md` created/updated with feature list | Yes |
| 2 | All features have detailed sections in requirement-details.md | Yes |
| 3 | Feature board updated via feature-board-management skill | Yes |
| 4 | All features have status "Planned" on feature board | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Example Execution

**Request:** "Break down e-commerce checkout requirement into features"

**Step 1: Analyze**
```
Identified features:
1. Shopping Cart - Manage items before purchase
2. Payment Processing - Handle payment transactions
3. Order Confirmation - Confirm and track orders
```

**Step 2: Create requirement-details.md**
```markdown
# Requirement Summary

> Requirement ID: REQ-005  
> Created: 01-17-2026  
> Last Updated: 01-17-2026

## Overview

E-commerce checkout functionality allowing users to complete purchases. Includes shopping cart management, payment processing, and order confirmation with email notifications.

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-010 | Shopping Cart | v1.0 | Add, remove, update items in cart | None |
| FEATURE-011 | Payment Processing | v1.0 | Process credit card payments via Stripe | FEATURE-010 |
| FEATURE-012 | Order Confirmation | v1.0 | Generate order confirmation and send email | FEATURE-011 |

---

## Feature Details

### FEATURE-010: Shopping Cart

**Version:** v1.0  
**Brief Description:** Allow users to add, remove, and update quantity of items in shopping cart

**Acceptance Criteria:**
- [ ] User can add products to cart
- [ ] User can update quantity in cart
- [ ] User can remove items from cart
- [ ] Cart persists across sessions
- [ ] Cart shows subtotal and item count

**Dependencies:**
- None

**Technical Considerations:**
- Store cart in browser localStorage for guest users
- Sync to database for logged-in users
- Calculate subtotal client and server-side

---

[More features...]
```

**Step 3: Call Feature Board Management**
```yaml
operation: create_or_update_features
features:
  - feature_id: FEATURE-010
    title: Shopping Cart
    version: v1.0
    description: Add, remove, update items in cart
    dependencies: []
  - feature_id: FEATURE-011
    title: Payment Processing
    version: v1.0
    description: Process credit card payments via Stripe
    dependencies: [FEATURE-010]
  - feature_id: FEATURE-012
    title: Order Confirmation
    version: v1.0
    description: Generate order confirmation and send email
    dependencies: [FEATURE-011]
```

**Step 4: Return Output**
```yaml
status: completed
next_task_type: task-type-feature-refinement-@feature-stage
require_human_review: Yes
task_output_links: [docs/requirements/requirement-details.md]
requirement_id: REQ-005
feature_ids: [FEATURE-010, FEATURE-011, FEATURE-012]
feature_count: 3
```

---

## Feature Dependency Guidelines

### Common Dependency Patterns

**Sequential Dependencies:**
```
FEATURE-001: User Authentication (no deps)
FEATURE-002: User Profile (depends on FEATURE-001)
FEATURE-003: User Settings (depends on FEATURE-002)
```

**Parallel with Shared Dependency:**
```
FEATURE-001: Database Layer (no deps)
FEATURE-002: User Service (depends on FEATURE-001)
FEATURE-003: Product Service (depends on FEATURE-001)
```

**Multiple Dependencies:**
```
FEATURE-001: Authentication (no deps)
FEATURE-002: Authorization (no deps)
FEATURE-003: Admin Panel (depends on FEATURE-001, FEATURE-002)
```

### Dependency Rules

1. **No Circular Dependencies** - A cannot depend on B if B depends on A
2. **Foundation First** - Core/shared features have no dependencies
3. **Clear Reason** - Document why dependency exists
4. **Minimal Dependencies** - Only list direct dependencies

---

## Best Practices

### Feature Sizing

**Too Large (Split):**
- "Complete E-Commerce System" → Split into Cart, Payment, Shipping, etc.
- "User Management" → Split into Registration, Profile, Settings, etc.

**Good Size:**
- "Shopping Cart Management"
- "Payment Processing with Stripe"
- "Email Notification System"

**Too Small (Combine):**
- "Add to Cart Button" → Part of Shopping Cart feature
- "Validate Email Format" → Part of User Registration feature

### Feature Naming

**Good Names:**
- Specific: "JWT Authentication" not "Login"
- Action-oriented: "User Profile Management" not "User Profile"
- Technology-agnostic (usually): "Payment Processing" not "Stripe Integration"

**Bad Names:**
- Too vague: "User Stuff", "Main Feature"
- Too technical: "REST API Controller Layer"
- Too broad: "Everything Users Need"

### Version Numbering

- Start with v1.0 for new features
- Use v1.1, v1.2 for minor enhancements
- Use v2.0 for major redesigns
- Most breakdown features will be v1.0

---

## Integration with Feature Board Management

This skill **MUST** call the feature-board-management skill to create features on the board. This integration:

1. **Creates centralized tracking** - Single source of truth at docs/requirements/features.md
2. **Initializes status** - All features start with status "Planned"
3. **Enables queries** - Other skills can query feature board for Feature Data Model
4. **Supports lifecycle** - Board tracks features through all phases

**See:** `skills/@feature-stage+feature-board-management/SKILL.md` for operation details

---

## Notes

- No longer create individual docs/requirements/FEATURE-XXX/feature.md files
- All features consolidated in requirement-details.md
- Feature board (features.md) is the status tracking system
- Feature specifications created later during Feature Refinement task
- Keep feature descriptions concise (50 words max) in the table
- More details go in the feature details section
