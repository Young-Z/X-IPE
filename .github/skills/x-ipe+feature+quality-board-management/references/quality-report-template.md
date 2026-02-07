# Project Quality Evaluation Report

> **Project Version:** {project_version}
> **Evaluated Date:** {evaluated_date}
> **Evaluated By:** {generated_by}
> **Scope:** {scope}

---

## Contents

- [Executive Summary](#executive-summary)
- [Feature-by-Feature Evaluation](#feature-by-feature-evaluation)
- [Violation Details by Feature](#violation-details-by-feature)
- [Files Approaching Threshold](#files-approaching-threshold)
- [Priority Gaps Summary](#priority-gaps-summary)
- [Recommendations](#recommendations)
- [Appendix: Detailed Metrics](#appendix-detailed-metrics)
- [Evaluation Principles](#evaluation-principles)
- [Status Legend](#status-legend)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Score** | {overall_score}/10 |
| **Health Status** | {health_status} |
| **Features Evaluated** | {feature_count} |
| **High Priority Gaps** | {high_priority_count} |
| **Medium Priority Gaps** | {medium_priority_count} |
| **Low Priority Gaps** | {low_priority_count} |

### Health Indicators

| Perspective | Status | Score |
|-------------|--------|-------|
| Requirements Alignment | {req_status} | {req_score}/10 |
| Specification Alignment | {spec_status} | {spec_score}/10 |
| Test Coverage | {test_status} | {test_score}/10 |
| Code Alignment | {code_status} | {code_score}/10 |

### Key Findings

- {key_finding_1}
- {key_finding_2}
- {key_finding_3}

---

## Feature-by-Feature Evaluation

### Overview Table

| Feature ID | Feature Name | Score | Status | Req | Spec | Test | Code | Tracing | Security | Gaps |
|------------|--------------|-------|--------|-----|------|------|------|---------|----------|------|
| {feature_id} | {feature_name} | {score}/10 | {status_icon} | {req_score}/10 | {spec_score}/10 | {test_score}/10 | {code_score}/10 | {tracing_score}/10 | {security_score}/10 | {gap_count} |

**Score-to-Status Mapping:**
- 8-10: ✅ aligned (green)
- 6-7: ⚠️ needs_attention (yellow)
- 1-5: ❌ critical (red)
- N/A: 📋 planned (gray)

---

## Violation Details by Feature

> This section lists specific violations per feature, organized by evaluation category.

### {feature_id}: {feature_name}

#### Requirements Violations

| Violation | Severity | Details |
|-----------|----------|---------|
| {violation_type} | {severity} | {details} |

*No violations* (if none)

#### Specification Violations

| Violation | Severity | Details |
|-----------|----------|---------|
| {violation_type} | {severity} | {details} |

*No violations* (if none)

#### Test Coverage Violations

| Violation | Severity | Details |
|-----------|----------|---------|
| {violation_type} | {severity} | {details} |

*No violations* (if none)

#### Code Alignment Violations

| Violation | Severity | Details |
|-----------|----------|---------|
| {violation_type} | {severity} | {details} |

*No violations* (if none)

#### Tracing Coverage Violations

| Violation | Severity | Details |
|-----------|----------|---------|
| {violation_type} | {severity} | {details} |

*No violations* (if none)

#### Security Violations

| Violation | Severity | Details |
|-----------|----------|---------|
| {violation_type} | {severity} | {details} |

*No violations* (if none)

---

<!-- Repeat "### {feature_id}" section for each feature with violations -->

---

## Files Approaching Threshold

> These files should be monitored - consider refactoring before they exceed limits.

| File | Lines | Threshold | Buffer | Feature |
|------|-------|-----------|--------|---------|
| {file_path} | {lines} | {threshold} | {buffer} lines | {feature_id} |

---

## Priority Gaps Summary

### 🔴 High Priority

| # | Feature | Category | Description |
|---|---------|----------|-------------|
| {n} | {feature_id} | {category} | {description} |

### 🟡 Medium Priority

| # | Feature | Category | Description |
|---|---------|----------|-------------|
| {n} | {feature_id} | {category} | {description} |

### 🟢 Low Priority

| # | Feature | Category | Description |
|---|---------|----------|-------------|
| {n} | {feature_id} | {category} | {description} |

---

## Recommendations

| Priority | Category | Action | Affected Features |
|----------|----------|--------|-------------------|
| {n} | {category} | {action} | {feature_list} |

---

## Appendix: Detailed Metrics

### Coverage by Feature

| Feature | Requirements | Specification | Test Coverage | Code Alignment | Tracing | Security | Overall |
|---------|--------------|---------------|---------------|----------------|---------|----------|---------|
| {feature_id} | {req_score}/10 | {spec_score}/10 | {test_score}/10 | {code_score}/10 | {tracing_score}/10 | {security_score}/10 | {overall}/10 |

**Score-to-Status Mapping:**
- 8-10: ✅ aligned
- 6-7: ⚠️ needs_attention
- 1-5: ❌ critical

### Gap Distribution by Feature

| Feature | Requirements | Specification | Test Coverage | Code Alignment | Total Gaps |
|---------|--------------|---------------|---------------|----------------|------------|
| {feature_id} | {req_gaps} | {spec_gaps} | {test_gaps} | {code_gaps} | {total} |

---

## Evaluation Principles

> This section defines the principles and thresholds used in this evaluation.

### Requirements Evaluation

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Completeness | 100% | Every implemented feature must have documented requirements |
| Traceability | Required | Requirements should trace to features and code |
| Clarity | No ambiguity | Requirements should be specific and testable |
| Currency | < 30 days | Requirements updated within 30 days of code changes |

### Specification Evaluation

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| API Documentation | Required | All public APIs must be documented |
| Behavior Specification | Required | Expected behaviors clearly defined |
| Edge Cases | Documented | Error handling and edge cases specified |
| Version Alignment | Match | Spec version should match implementation version |

### Test Coverage Evaluation

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Line Coverage | ≥ 80% | Minimum line coverage for production code |
| Branch Coverage | ≥ 70% | Minimum branch/decision coverage |
| Critical Path Coverage | 100% | Core business logic must be fully tested |
| Error Handler Coverage | ≥ 90% | Exception and error paths tested |
| Test Isolation | Required | Tests should not depend on external services |
| Mock External APIs | Required | External API calls must be mocked in tests |

### Code Alignment Evaluation

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| **File Size** | ≤ 800 lines | Single file should not exceed 800 lines |
| **Function Size** | ≤ 50 lines | Single function should not exceed 50 lines |
| **Class Size** | ≤ 500 lines | Single class should not exceed 500 lines |
| **Cyclomatic Complexity** | ≤ 10 | Function complexity should be manageable |

### SOLID Principles

| Principle | Description |
|-----------|-------------|
| **SRP** | Single Responsibility - each module/class has one reason to change |
| **OCP** | Open/Closed - open for extension, closed for modification |
| **LSP** | Liskov Substitution - subtypes must be substitutable for base types |
| **ISP** | Interface Segregation - clients shouldn't depend on unused interfaces |
| **DIP** | Dependency Inversion - depend on abstractions, not concretions |

### KISS Principle

| Check | Description |
|-------|-------------|
| Avoid Over-Engineering | Don't add abstraction layers without clear benefit |
| Straightforward Logic | Prefer linear control flow over convoluted paths |
| Minimal Dependencies | Only import necessary libraries |
| Clear Intent | Code should be self-documenting |
| Simple Data Structures | Use built-in types when they suffice |

### Modular Design Principle

| Check | Description |
|-------|-------------|
| **Module Cohesion** | Related functions grouped in same module |
| **Module Coupling** | Modules minimize dependencies on each other |
| **Single Entry Point** | Each module has clear public interface |
| **Folder Structure** | Files organized by feature or layer |
| **Reusability** | Modules can be reused in different contexts |
| **Testability** | Each module can be tested in isolation |

### Code Smell Detection Rules

| Smell | Detection Rule | Severity |
|-------|----------------|----------|
| God Class | Class > 500 lines OR > 20 methods | High |
| Long Method | Function > 50 lines | Medium |
| Large File | File > 800 lines | High |
| Deep Nesting | > 4 levels of indentation | Medium |
| Too Many Parameters | Function > 5 parameters | Low |
| Duplicate Code | Similar code blocks > 10 lines | Medium |

### Tracing Coverage Evaluation

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Decorator Coverage | ≥ 90% | Public functions must have @x_ipe_tracing decorator |
| Sensitive Param Redaction | Required | password, token, secret, key params must use redact=[] |
| Logging Levels | Correct | API=INFO, Business logic=INFO, Utilities=DEBUG |

### Security Evaluation

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Input Validation | Required | All user-facing endpoints must validate input |
| No Hardcoded Secrets | Required | No secrets, tokens, or credentials in code |
| Auth/Authz | Required | Protected routes must have proper authentication/authorization |
| Injection Prevention | Required | SQL injection and XSS prevention measures in place |
| Sensitive Data Handling | Required | Encryption/hashing for sensitive data |

---

## Status Legend

| Score Range | Status | Description |
|-------------|--------|-------------|
| 8-10 | ✅ aligned | Fully aligned, meets quality standards |
| 6-7 | ⚠️ needs_attention | Minor gaps exist, should be addressed |
| 1-5 | ❌ critical | Major issues requiring immediate action |
| N/A | 📋 planned | Future feature - not yet implemented |

### Dimension Score Calculation

Each dimension (Requirements, Specification, Test, Code, Tracing, Security) is scored 1-10 based on:

```
dimension_score = 10 - SUM(violation_count × importance_weight)
```

**Importance Weights:**
- Critical violations: ×3 (e.g., no tests, hardcoded secrets)
- High violations: ×2 (e.g., missing coverage, SRP violations)
- Medium violations: ×1 (e.g., outdated specs, missing docs)
- Low violations: ×0.5 (e.g., minor style issues)

## Health Status Definitions

| Status | Score Range | Description |
|--------|-------------|-------------|
| 🟢 healthy | 8-10 | Project in good shape |
| 🟡 attention_needed | 5-7 | Some areas need work |
| 🔴 critical | 1-4 | Immediate action required |

**Note:** Features with "planned" status are excluded from score calculation.

---

*Report generated by x-ipe+feature+quality-board-management skill*
