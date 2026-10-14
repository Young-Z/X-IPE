# Evaluation Principles Reference

This document contains all evaluation principles and thresholds used by the x-ipe+feature+quality-board-management skill.

---

## Requirements Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Completeness | 100% | Every implemented feature must have documented requirements |
| Traceability | Required | Requirements should trace to features and code |
| Clarity | No ambiguity | Requirements should be specific and testable |
| Currency | < 30 days | Requirements updated within 30 days of code changes |

---

## Specification Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| API Documentation | Required | All public APIs must be documented |
| Behavior Specification | Required | Expected behaviors clearly defined |
| Edge Cases | Documented | Error handling and edge cases specified |
| Version Alignment | Match | Spec version should match implementation version |

---

## Test Coverage Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Line Coverage | ≥ 80% | Minimum line coverage for production code |
| Branch Coverage | ≥ 70% | Minimum branch/decision coverage |
| Critical Path Coverage | 100% | Core business logic must be fully tested |
| Error Handler Coverage | ≥ 90% | Exception and error paths tested |
| Test Isolation | Required | Tests should not depend on external services |
| Mock External APIs | Required | External API calls must be mocked in tests |

---

## Code Alignment Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| **File Size** | ≤ 800 lines | Single file should not exceed 800 lines |
| **Function Size** | ≤ 50 lines | Single function should not exceed 50 lines |
| **Class Size** | ≤ 500 lines | Single class should not exceed 500 lines |
| **Cyclomatic Complexity** | ≤ 10 | Function complexity should be manageable |
| **SRP** | 1 reason to change | Each module/class has one responsibility |
| **OCP** | Extensible | Open for extension, closed for modification |
| **LSP** | Substitutable | Subtypes must be substitutable for base types |
| **ISP** | Focused | Clients shouldn't depend on unused interfaces |
| **DIP** | Abstracted | Depend on abstractions, not concretions |
| **DRY** | No duplication | Avoid code duplication across modules |
| **KISS** | Simple solutions | Prefer simple over complex implementations |
| **YAGNI** | No unused code | Don't implement features until needed |
| **Modular Design** | Cohesive modules | Code organized into focused, reusable modules |
| **Naming Conventions** | Consistent | Follow language-specific naming conventions |
| **Import Organization** | Grouped | Imports organized by type (stdlib, external, internal) |

---

## Tracing Coverage Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Decorator Coverage | ≥ 90% | Public functions must have @x_ipe_tracing decorator |
| Sensitive Param Redaction | Required | password, token, secret, key params must use redact=[] |
| Logging Levels | Correct | API=INFO, Business logic=INFO, Utilities=DEBUG |

---

## Security Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Input Validation | Required | All user-facing endpoints must validate input |
| No Hardcoded Secrets | Required | No secrets, tokens, or credentials in code |
| Auth/Authz | Required | Protected routes must have proper authentication/authorization |
| Injection Prevention | Required | SQL injection and XSS prevention measures in place |
| Sensitive Data Handling | Required | Encryption/hashing for sensitive data |

---

## KISS Principle Assessment

| Check | Threshold | Description |
|-------|-----------|-------------|
| Avoid Over-Engineering | No unnecessary abstractions | Don't add layers without clear benefit |
| Straightforward Logic | Linear flow preferred | Avoid convoluted control flow |
| Minimal Dependencies | Only necessary imports | Don't import unused libraries |
| Clear Intent | Self-documenting code | Code should express intent without excessive comments |
| Simple Data Structures | Use built-in types | Avoid custom types when built-ins suffice |

---

## Modular Design Assessment

| Check | Threshold | Description |
|-------|-----------|-------------|
| **Module Cohesion** | High cohesion | Related functions grouped in same module |
| **Module Coupling** | Loose coupling | Modules minimize dependencies on each other |
| **Single Entry Point** | One public API | Each module has clear public interface |
| **Folder Structure** | Logical grouping | Files organized by feature or layer |
| **Reusability** | Portable modules | Modules can be reused in different contexts |
| **Testability** | Independently testable | Each module can be tested in isolation |

**Modular Design Patterns:**

| Pattern | When to Apply | Example |
|---------|---------------|---------|
| Feature Modules | Large files > 800 lines | Split `app.py` → `routes/api.py`, `routes/views.py` |
| Service Layer | Business logic mixed with routes | Extract to `services/` folder |
| Component Split | UI file > 500 lines | Split into sub-components |
| Utility Extraction | Repeated helper functions | Create `utils/` or `lib/` folder |

---

## Code Smell Detection

| Smell | Detection Rule | Severity |
|-------|----------------|----------|
| God Class | Class > 500 lines OR > 20 methods | High |
| Long Method | Function > 50 lines | Medium |
| Large File | File > 800 lines | Medium |
| Deep Nesting | > 4 levels of indentation | Medium |
| Too Many Parameters | Function > 5 parameters | Low |
| Magic Numbers | Hardcoded values without constants | Low |
| Dead Code | Unused functions/variables | Low |
| Duplicate Code | Similar code blocks > 10 lines | Medium |

---

## Score Calculation

### Dimension Score (1-10 Grid)

Each dimension (Requirements, Specification, Test, Code, Tracing, Security) is scored 1-10 based on:

1. **Principle Violations:** Count violations in that dimension
2. **Principle Importance:** Weight violations by importance (critical=3, high=2, medium=1, low=0.5)

```
dimension_score = 10 - SUM(violation_weight * importance_weight)
dimension_score = MAX(1, MIN(10, dimension_score))  # Clamp to 1-10
```

**Importance Weights by Principle:**

| Category | Principle | Importance | Weight |
|----------|-----------|------------|--------|
| Code | File Size >800 lines | Critical | 3 |
| Code | Function Size >50 lines | High | 2 |
| Code | SRP Violation | Critical | 3 |
| Code | OCP Violation | High | 2 |
| Code | LSP Violation | Medium | 1 |
| Code | ISP Violation | Medium | 1 |
| Code | DIP Violation | High | 2 |
| Code | DRY Violation | High | 2 |
| Code | KISS Violation | High | 2 |
| Code | Modular Design Violation | High | 2 |
| Test | Line Coverage <80% | High | 2 |
| Test | No Tests | Critical | 3 |
| Test | Critical Path Untested | Critical | 3 |
| Req | Undocumented Feature | Medium | 1 |
| Req | Unimplemented Requirement | High | 2 |
| Req | Deviated Implementation | High | 2 |
| Spec | Missing Specification | Medium | 1 |
| Spec | Outdated Specification | Medium | 1 |
| Tracing | Untraced Function | Medium | 1 |
| Tracing | Unredacted Sensitive Param | High | 2 |
| Security | Hardcoded Secret | Critical | 3 |
| Security | Missing Input Validation | High | 2 |
| Security | Missing Auth/Authz | Critical | 3 |

### Dimension Status from Score

| Score Range | Status | Icon |
|-------------|--------|------|
| 8-10 | ✅ aligned | Green |
| 6-7 | ⚠️ needs_attention | Yellow |
| 1-5 | ❌ critical | Red |
| N/A | 📋 planned | Gray |

### Feature Score (1-10)

```
feature_score = weighted_average(
  requirements_alignment: weight=0.20,
  specification_alignment: weight=0.20,
  test_coverage: weight=0.20,
  code_alignment: weight=0.20,
  tracing_coverage: weight=0.10,
  security: weight=0.10
)
```

**Note:** Features with "planned" status are excluded from scoring.

### Overall Score (1-10)

```
overall_score = average(all feature_scores WHERE status != "planned")
```

### Health Status

```
IF overall_score >= 8: healthy
ELSE IF overall_score >= 5: attention_needed
ELSE: critical
```

## Evidence and Applicability Boundaries

The original rubric above is retained. Apply each principle to inspected scope;
record numerator/denominator, command, revision and actual violations before
scoring. An empty violation list without evaluation is not a score of ten.
Coverage thresholds diagnose applicable production-code gaps, not a universal
release gate or forced infrastructure for skills/documents. Critical approved
AC/security failures and explicitly mandatory thresholds cannot be waived.

Retain original rounding/status ambiguity for fractional dimension scores as a
reported compatibility issue; do not silently invent a rounding policy. The
principles reference calls file-size severity Medium while its importance table
uses Critical and the template uses High: distinguish severity from scoring
importance, cite the applicable rubric, and disclose unresolved severity conflict.
Do not revise source acceptance or hide these original inconsistencies.

N/A in narrative means unavailable/not applicable with a reason unless inspected
future work supports planned status. Missing intent or current evidence blocks
the pertinent score/outcome claim; do not exclude unknown dimensions and inflate
an aggregate, add a scoring dimension, change model enums, or fabricate a metric.
Delivery and stakeholder outcome use document-local evidence, never these scores.
See [goal reporting](.github/skills/x-ipe+feature+quality-board-management/references/goal-reporting.md).
