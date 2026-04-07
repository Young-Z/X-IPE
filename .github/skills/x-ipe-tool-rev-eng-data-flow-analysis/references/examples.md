# Examples — Section 6: Data Flow / Protocol Analysis

## Example 1: Extract Data Flows from a FastAPI Application

```yaml
invocation:
  skill: x-ipe-tool-rev-eng-data-flow-analysis
  operation: extract
  input:
    repo_path: "/workspace/my-api"
    phase1_output: "/workspace/output/phase1"
    phase2_output: "/workspace/output/phase2"
    output_dir: "/workspace/output/section-06"
```

### Expected Output: 01-request-flows.md (excerpt)

```markdown
# Request Flows

## Flow 1: User Registration (POST /api/v1/users)

| Step | Name | Role | File:Line | Data In | Data Out | Sync/Async |
|------|------|------|-----------|---------|----------|------------|
| 1 | FastAPI router | Entry point | api/routes/users.py:24 | HTTP Request body | UserCreateDTO | async |
| 2 | Auth middleware | Middleware | api/middleware/auth.py:15 | Request headers | AuthContext | async |
| 3 | Pydantic validation | Validation | api/schemas/user.py:8 | raw JSON | UserCreateDTO | sync |
| 4 | UserController.create | Handler | api/controllers/user.py:31 | UserCreateDTO | UserResponse | async |
| 5 | UserService.create_user | Service | services/user.py:42 | UserCreateDTO | User | async |
| 6 | hash_password | Utility | utils/crypto.py:18 | plain text | hashed string | sync |
| 7 | UserRepository.insert | Repository | repos/user.py:27 | User entity | User (with id) | async |
| 8 | SQLAlchemy execute | Data access | repos/user.py:35 | SQL + params | Row | async |
| 9 | Response serialization | Response | api/controllers/user.py:38 | User | UserResponse JSON | sync |

### Mermaid Sequence Diagram

​```mermaid
sequenceDiagram
    participant Client
    participant Router as FastAPI Router
    participant Auth as Auth Middleware
    participant Ctrl as UserController
    participant Svc as UserService
    participant Repo as UserRepository
    participant DB as PostgreSQL

    Client->>Router: POST /api/v1/users {name, email, password}
    Router->>Auth: Check auth headers
    Auth-->>Router: AuthContext
    Router->>Ctrl: UserCreateDTO
    Ctrl->>Svc: create_user(dto)
    Svc->>Svc: hash_password(dto.password)
    Svc->>Repo: insert(User entity)
    Repo->>DB: INSERT INTO users...
    DB-->>Repo: Row with generated id
    Repo-->>Svc: User(id, name, email)
    Svc-->>Ctrl: User
    Ctrl-->>Client: 201 UserResponse JSON
​```
```

---

## Example 2: Event Propagation Documentation

### Expected Output: 02-event-propagation.md (excerpt)

```markdown
# Event Propagation

## Event: user.created

| Field | Value |
|-------|-------|
| Event name | `user.created` |
| Publisher | services/user.py:48 (`event_bus.publish("user.created", user)`) |
| Subscriber 1 | services/email.py:12 (`@subscribe("user.created")`) |
| Subscriber 2 | services/analytics.py:31 (`@subscribe("user.created")`) |
| Payload shape | `{ id: int, name: str, email: str, created_at: datetime }` |
| Delivery | at-least-once (Redis pub/sub with retry) |
| Ordering | best-effort |

## Event: order.completed

| Field | Value |
|-------|-------|
| Event name | `order.completed` |
| Publisher | services/order.py:92 (`event_bus.publish("order.completed", order)`) |
| Subscriber 1 | services/inventory.py:45 (`@subscribe("order.completed")`) |
| Subscriber 2 | services/notification.py:23 (`@subscribe("order.completed")`) |
| Payload shape | `{ order_id: int, user_id: int, items: List[OrderItem], total: Decimal }` |
| Delivery | at-least-once |
| Ordering | guaranteed per partition (Kafka) |
```

---

## Example 3: Data Transformation Chain

### Expected Output: 03-data-transformations.md (excerpt)

```markdown
# Data Transformation Chains

## Chain: User Registration Data Flow

### Step 1: HTTP Body → UserCreateDTO
| Input Shape | Output Shape | Location | Changes |
|-------------|-------------|----------|---------|
| `{ "name": "str", "email": "str", "password": "str" }` | `UserCreateDTO(name: str, email: str, password: str)` | api/schemas/user.py:8 | Validated, typed |

### Step 2: UserCreateDTO → User Entity
| Input Shape | Output Shape | Location | Changes |
|-------------|-------------|----------|---------|
| `UserCreateDTO(name, email, password)` | `User(id=None, name, email, hashed_password, created_at)` | services/user.py:45 | +hashed_password (password hashed), +created_at, -password |

### Step 3: User Entity → Database Row
| Input Shape | Output Shape | Location | Changes |
|-------------|-------------|----------|---------|
| `User(id=None, name, email, hashed_password, created_at)` | `Row(id=42, name, email, hashed_password, created_at)` | repos/user.py:30 | +id (auto-generated) |

### Step 4: User Entity → UserResponse
| Input Shape | Output Shape | Location | Changes |
|-------------|-------------|----------|---------|
| `User(id, name, email, hashed_password, created_at)` | `UserResponse(id, name, email, created_at)` | api/controllers/user.py:38 | -hashed_password (stripped for security) |
```

---

## Example 4: Validate Extracted Content

```yaml
invocation:
  skill: x-ipe-tool-rev-eng-data-flow-analysis
  operation: validate
  input:
    content_path: "/workspace/output/section-06"
    section_id: "6-data-flow-analysis"
```

### Expected Validation Output

```yaml
validation_result:
  section_id: "6-data-flow-analysis"
  passed: true
  criteria:
    - id: REQ-6.1
      status: PASS
      feedback: "1 complete end-to-end flow: User Registration (9 steps)"
    - id: REQ-6.2
      status: PASS
      feedback: "All 9 steps cite file:line references"
    - id: REQ-6.3
      status: PASS
      feedback: "4 transformation steps documented with input/output shapes"
    - id: REQ-6.4
      status: PASS
      feedback: "1 Mermaid sequenceDiagram present for User Registration flow"
    - id: OPT-6.5
      status: PASS
      feedback: "2 events documented: user.created, order.completed"
    - id: OPT-6.6
      status: PASS
      feedback: "3 protocols: HTTP/REST, Redis pub/sub, PostgreSQL"
  missing_info: []
```

---

## Example 5: Package Final Output

```yaml
invocation:
  skill: x-ipe-tool-rev-eng-data-flow-analysis
  operation: package
  input:
    content_path: "/workspace/output/section-06"
    output_dir: "/workspace/output/final/section-06-data-flow"
```

### Expected Directory Structure

```
section-06-data-flow/
├── index.md                      # Overview: 1 flow, 2 events, 4 transforms, 3 protocols, 2 boundaries
├── 01-request-flows.md           # User Registration flow (9 steps + sequence diagram)
├── 02-event-propagation.md       # user.created, order.completed events
├── 03-data-transformations.md    # 4-step transformation chain
├── 04-protocol-details.md        # HTTP/REST, Redis pub/sub, PostgreSQL
├── 05-async-sync-boundaries.md   # 2 boundaries: sync Flask → async aiohttp, sync → async DB
├── screenshots/
└── tests/
    ├── test_user_registration.py  # Validates POST /users end-to-end flow
    └── test_event_user_created.py # Validates user.created event propagation
```
