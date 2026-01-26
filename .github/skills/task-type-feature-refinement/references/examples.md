# Feature Refinement - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: User Authentication Specification

**Context:**
- Feature: FEATURE-001 (User Authentication)
- From Feature Breakdown: Basic entry in features.md
- Task: Create detailed specification

### Execution Flow

```
1. Execute Task Flow from task-execution-guideline skill

2. Read Feature Entry:
   - ID: FEATURE-001
   - Name: User Authentication
   - Status: Draft
   - Dependencies: None

3. Gather Requirements (Brainstorming with Human):
   - Q: "What authentication methods are needed?"
   - A: "Email/password for now, OAuth later"
   
   - Q: "Password requirements?"
   - A: "Min 8 chars, 1 uppercase, 1 number"
   
   - Q: "Session duration?"
   - A: "24 hours, with refresh"

4. Document User Stories:
   - US-001: As a user, I can register with email and password
   - US-002: As a user, I can log in with my credentials
   - US-003: As a user, I can reset my forgotten password
   - US-004: As a user, I stay logged in for 24 hours

5. Define Acceptance Criteria:

   US-001 (Registration):
   - [ ] Email must be valid format
   - [ ] Password meets complexity requirements
   - [ ] Duplicate email shows error
   - [ ] Success sends verification email

   US-002 (Login):
   - [ ] Valid credentials return JWT token
   - [ ] Invalid credentials return 401
   - [ ] Account locked after 5 failed attempts
   - [ ] Token contains user ID and expiry

6. Create Specification:
   x-ipe-docs/requirements/FEATURE-001/specification.md

7. Update features.md:
   - Status: Draft → Specified

8. Resume Task Flow from task-execution-guideline skill
```

### Output

```yaml
category: feature-stage
next_task_type: Technical Design
require_human_review: Yes

specification_summary: |
  FEATURE-001 User Authentication:
  - 4 user stories defined
  - 16 acceptance criteria
  - Password policy documented
  - Session management defined

user_stories: 4
acceptance_criteria: 16

task_output_links:
  - x-ipe-docs/requirements/FEATURE-001/specification.md
  - x-ipe-docs/planning/features.md (status updated)
```

---

## Example 2: Enhancement Refinement (from Change Request)

**Context:** CR classified as ENHANCEMENT

```
1. Receive from Change Request:
   - Feature: FEATURE-005 (User Settings)
   - Enhancement: "Add auto-save functionality"

2. Read Existing Specification:
   - Current: Manual save with button
   - Current user stories: 3

3. Add Enhancement to Specification:

   New User Story:
   - US-010: As a user, my settings save automatically

   New Acceptance Criteria:
   - [ ] Changes auto-save after 2 second debounce
   - [ ] Save indicator shows "Saving..." during save
   - [ ] Save indicator shows "Saved" on success
   - [ ] Error toast on save failure
   - [ ] Unsaved changes prompt on navigation

4. Update Specification:
   - Add new section: "Auto-Save Behavior"
   - Add US-010 and criteria

5. Output:
   action: updated_existing
   user_stories_added: 1
   acceptance_criteria_added: 5
```

---

## Example 3: Missing Feature Entry (Blocked)

**Scenario:** Feature not in features.md

```
1. Look up FEATURE-099 in features.md
   → NOT FOUND

2. BLOCKED:
   "FEATURE-099 not found in x-ipe-docs/planning/features.md
    
    Feature Refinement requires an existing feature entry.
    This feature may need to go through Feature Breakdown first."

3. Options:
   A) Run Feature Breakdown to create the feature
   B) Manually add entry to features.md

4. Wait for human decision
```

---

## Example 4: Complex Feature with Sub-Features

**Context:** Large feature needs decomposition during refinement

```
1. Read Feature Entry:
   - FEATURE-015: Shopping Cart

2. During Refinement, identify complexity:
   - Cart state management
   - Price calculations
   - Inventory checking
   - Persistence
   - Guest vs logged-in handling

3. Recommend Split:
   "FEATURE-015 is too complex for single specification.
    
    Recommend splitting into:
    - FEATURE-015A: Cart State Management
    - FEATURE-015B: Cart Pricing
    - FEATURE-015C: Cart Persistence
    
    Shall I proceed with the split?"

4. If human approves split:
   → Return to Feature Breakdown with recommendation
   → Create sub-features
   → Then refine each separately

5. If human declines:
   → Proceed with single large specification
   → Mark as "Complex" in features.md
```

---

## Example 5: Specification with Edge Cases

**Context:** Payment feature requiring thorough edge case coverage

```
1. Core User Stories:
   - US-020: Process credit card payment

2. Edge Case Discovery (prompt human):
   - "What happens if card is declined?"
   - "What about expired cards?"
   - "Network timeout during processing?"
   - "Duplicate submission prevention?"

3. Document Edge Cases:

   Error Handling:
   - [ ] Declined card shows reason code
   - [ ] Expired card prompts for update
   - [ ] Network timeout retries 3 times
   - [ ] Idempotency key prevents duplicates

   Validation:
   - [ ] Card number Luhn check
   - [ ] CVV format validation
   - [ ] Expiry date future check

4. Output:
   user_stories: 1
   happy_path_criteria: 5
   error_handling_criteria: 4
   validation_criteria: 3
   total_acceptance_criteria: 12
```
