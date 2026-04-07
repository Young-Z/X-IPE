# Usage Examples — Design Pattern Detection

> Examples showing how the orchestrator interacts with this tool skill.

---

## Example 1: Full Pattern Detection Flow

```yaml
# Step 1: Extract patterns from codebase
Orchestrator: extract(
  repo_path="/path/to/repo",
  phase1_output=".x-ipe-checkpoint/phase1/",
  phase2_output=".x-ipe-checkpoint/phase2/",
  output_dir=".x-ipe-checkpoint/section-02/"
)
→ {
    success: true,
    extracted_content: ".x-ipe-checkpoint/section-02/",
    # Created files:
    #   index.md (inventory table)
    #   01-creational-patterns.md
    #   02-structural-patterns.md
    #   03-behavioral-patterns.md
    #   04-language-specific-patterns.md
    #   05-pattern-interactions.md
  }

# Step 2: Validate detected patterns
Orchestrator: validate(
  content_path=".x-ipe-checkpoint/section-02/",
  section_id="2-design-pattern-detection"
)
→ {
    passed: true,
    criteria: [
      { id: "REQ-1", status: "pass", feedback: "Inventory table with 7 patterns" },
      { id: "REQ-2", status: "pass", feedback: "All patterns have confidence levels" },
      { id: "REQ-3", status: "pass", feedback: "All patterns cite file:line" },
      { id: "REQ-4", status: "pass", feedback: "7 patterns > 3 minimum" }
    ],
    missing_info: []
  }

# Step 3: Collect and execute pattern-relevant tests
Orchestrator: collect_tests(
  repo_path="/path/to/repo",
  phase2_output=".x-ipe-checkpoint/phase2/"
)
→ {
    collected_tests: [
      { path: "tests/test_service_factory.py", claim: "Factory pattern in service creation" },
      { path: "tests/test_event_handler.py", claim: "Observer pattern in event system" },
      { path: "tests/test_middleware.py", claim: "Decorator pattern in middleware chain" }
    ]
  }

Orchestrator: execute_tests(repo_path="/path/to/repo")
→ {
    tests_run: 3, tests_passed: 3, tests_failed: 0,
    claim_mapping: [
      { test: "test_service_factory.py", claim: "Factory pattern", result: "confirmed" },
      { test: "test_event_handler.py", claim: "Observer pattern", result: "confirmed" },
      { test: "test_middleware.py", claim: "Decorator pattern", result: "confirmed" }
    ]
  }

# Step 4: Package into final output
Orchestrator: package(
  content_path=".x-ipe-checkpoint/section-02/",
  output_dir="output/section-02-design-patterns/"
)
→ { package_path: "output/section-02-design-patterns/" }
```

---

## Example 2: Pattern Inventory Table

```markdown
# Pattern Inventory — Example Output in index.md

| Pattern | Type | Confidence | Location | Role |
|---------|------|------------|----------|------|
| Factory Method | Creational | 🟢 | `src/services/factory.py:42` | Creates service instances based on config |
| Singleton | Creational | 🟡 | `src/config/settings.py:15` | Module-level config caching |
| Adapter | Structural | 🟢 | `src/adapters/redis_client.py:8` | Wraps Redis library with domain interface |
| Decorator | Structural | 🟢 | `src/middleware/auth.py:23` | Authentication middleware decorator |
| Facade | Structural | 🟡 | `src/services/payment.py:31` | Orchestrates payment + billing + notify |
| Observer | Behavioral | 🟢 | `src/events/emitter.py:12` | Event-driven notification system |
| Strategy | Behavioral | 🔴 | `src/handlers/dispatch.py:55` | Handler dispatch by type (possible strategy) |
```

---

## Example 3: Confidence Level Assignment

```yaml
# 🟢 High Confidence — Clear canonical implementation
Pattern: Factory Method
Location: src/services/factory.py:42
Evidence: |
  class ServiceFactory:
      _registry: dict[str, type[BaseService]] = {}

      @classmethod
      def register(cls, name: str, service_cls: type[BaseService]):
          cls._registry[name] = service_cls

      @classmethod
      def create(cls, name: str, **kwargs) -> BaseService:
          return cls._registry[name](**kwargs)
Rationale: Explicit Factory class with registry pattern, clear create() method

# 🟡 Medium Confidence — Partial/informal match
Pattern: Singleton
Location: src/config/settings.py:15
Evidence: |
  _settings = None
  def get_settings():
      global _settings
      if _settings is None:
          _settings = Settings()
      return _settings
Rationale: Module-level caching achieves singleton behavior but no explicit Singleton class

# 🔴 Low Confidence — Possible but ambiguous
Pattern: Strategy
Location: src/handlers/dispatch.py:55
Evidence: |
  HANDLERS = {
      "email": handle_email,
      "sms": handle_sms,
      "push": handle_push,
  }
  def dispatch(notification_type, payload):
      return HANDLERS[notification_type](payload)
Rationale: Dictionary dispatch is strategy-like but may just be a lookup table
```

---

## Example 4: Test-Derived Pattern Evidence

```yaml
# Phase 2 test knowledge reveals patterns through mock usage
# From Section 8 test analysis:

Test: test_payment_service.py
Mocks: [external_payment_gateway, email_service, audit_logger]
→ Pattern Evidence:
  - Facade: PaymentService mocks 3 dependencies → orchestration facade
  - Adapter: external_payment_gateway mock → adapter boundary

Test: test_notification.py
Setup: "patches EventEmitter.emit with mock"
→ Pattern Evidence:
  - Observer: EventEmitter being mocked → event system exists
```

---

## Example 5: No Patterns Found Scenario

```yaml
# Small utility library with no canonical patterns
Orchestrator: extract(...)
→ {
    # index.md contains:
    # "No canonical design patterns detected. This codebase consists of
    #  standalone utility functions without class hierarchies or behavioral
    #  patterns. 15 source files scanned across 3 modules."
    #
    # Subsection files created but marked "None detected"
  }

Orchestrator: validate(...)
→ {
    passed: true,  # REQ-4 allows "no canonical patterns found" with rationale
    criteria: [
      { id: "REQ-1", status: "pass", feedback: "Inventory table present (empty with rationale)" },
      { id: "REQ-4", status: "pass", feedback: "'No canonical patterns found' documented with rationale" }
    ]
  }
```
