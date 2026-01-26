# Technical Design - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: User Authentication Technical Design

**Context:**
- Feature: FEATURE-001 (User Authentication)
- Specification: `x-ipe-docs/requirements/FEATURE-001/specification.md`

### Execution Flow

```
1. Execute Task Flow from task-execution-guideline skill

2. Read Specification:
   - User Story: "As a user, I can log in with email and password"
   - Acceptance Criteria:
     - Valid credentials return JWT token
     - Invalid credentials return 401
     - Token expires after 24 hours
     - Password must be hashed

3. Design Components:

   High-Level Architecture:
   ```
   [Client] → [AuthController] → [AuthService] → [UserRepository] → [Database]
                    ↓
              [TokenService]
   ```

4. Define Component Table:

   | Component | Type | Responsibility | Dependencies |
   |-----------|------|----------------|--------------|
   | AuthController | Controller | Handle HTTP requests | AuthService |
   | AuthService | Service | Business logic | UserRepository, TokenService |
   | TokenService | Service | JWT operations | jwt library |
   | UserRepository | Repository | Database operations | ORM |

5. Define Interface Contracts:

   AuthService:
   ```python
   class AuthService:
       def authenticate(email: str, password: str) -> Token
       def verify_token(token: str) -> User
       def refresh_token(token: str) -> Token
   ```

6. Document Data Flows:
   - Login Flow: Request → Validate → Hash Check → Generate Token → Response
   - Token Refresh: Request → Verify Old → Generate New → Response

7. Create technical-design.md at:
   x-ipe-docs/requirements/FEATURE-001/technical-design.md

8. Resume Task Flow from task-execution-guideline skill
```

### Output

```yaml
category: feature-stage
next_task_type: Test Generation
require_human_review: Yes

design_summary: |
  Authentication system with 4 components:
  - AuthController: REST endpoints
  - AuthService: Core auth logic
  - TokenService: JWT handling
  - UserRepository: User persistence

components_defined: 4
interfaces_defined: 3
data_flows_documented: 2

task_output_links:
  - x-ipe-docs/requirements/FEATURE-001/technical-design.md
```

---

## Example 2: Complex Feature with Multiple Modules

**Context:** E-Commerce Cart Feature

```
1. Read Specification for FEATURE-015

2. Identify Module Boundaries:
   - Cart Module: Cart state management
   - Product Module: Product data (existing)
   - Pricing Module: Price calculation, discounts
   - Inventory Module: Stock checking

3. Design Inter-Module Communication:

   ```
   [CartService] ──→ [ProductService] (read product info)
        │
        ├──→ [PricingService] (calculate totals)
        │
        └──→ [InventoryService] (check stock)
   ```

4. Define API Contracts:
   - Internal: Service-to-service interfaces
   - External: REST API for frontend

5. Address Cross-Cutting Concerns:
   - Caching: Product info cached 5 min
   - Transactions: Cart updates atomic
   - Error Handling: Graceful degradation

6. Document Dependencies:
   - FEATURE-015 depends on FEATURE-010 (Products)
   - FEATURE-015 depends on FEATURE-012 (Inventory)

7. Output:
   components_defined: 4
   modules_affected: 3
   dependencies: [FEATURE-010, FEATURE-012]
```

---

## Example 3: Missing Specification (Blocked)

**Scenario:** No specification file exists

```
1. Check for Specification:
   - Expected: x-ipe-docs/requirements/FEATURE-007/specification.md
   - Result: FILE NOT FOUND

2. BLOCKED - Cannot proceed:
   "No specification found for FEATURE-007.
    
    Technical design requires specification to define:
    - User stories to implement
    - Acceptance criteria to satisfy
    - Functional requirements
    
    Required: Complete Feature Refinement first"

3. Status: blocked
   Reason: Missing specification
   Required: x-ipe-docs/requirements/FEATURE-007/specification.md
```

---

## Example 4: Design Update (Change Request)

**Scenario:** Existing design needs modification per CR

```
1. Read Change Request:
   - Add rate limiting to AuthService

2. Read Existing Design:
   - x-ipe-docs/requirements/FEATURE-001/technical-design.md exists
   - Current components: AuthController, AuthService, etc.

3. Update Design:
   - Add RateLimiter component
   - Update AuthService interface to include rate checking
   - Add rate limit configuration section

4. Add Design Change Log Entry:

   | Date | Type | Description |
   |------|------|-------------|
   | 01-25-2026 | Enhancement | Added RateLimiter component for login attempts |

5. Output:
   design_action: updated
   components_added: [RateLimiter]
   components_modified: [AuthService]
```
