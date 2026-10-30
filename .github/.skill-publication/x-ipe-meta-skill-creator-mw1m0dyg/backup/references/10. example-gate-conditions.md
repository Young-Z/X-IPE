# Example: Gate Conditions

Demonstrates Gate Conditions patterns for complex branching logic as alternative to DoR/DoD.

## Quality Gate

```yaml
gate:
  name: "Quality Gate"
  conditions:
    logic: AND
    checks:
      - type: threshold
        condition: "test_coverage >= 80%"
      - type: completion
        condition: "all_tests_pass == true"
      - type: completion
        condition: "no_critical_issues == true"
  on_pass: "Proceed to deployment"
  on_fail: "Return to implementation with issues list"
```

## Approval Gate with Fallback

```yaml
gate:
  name: "Design Approval"
  conditions:
    logic: OR
    checks:
      - type: approval
        condition: "tech_lead_approved == true"
      - type: approval
        condition: "two_senior_devs_approved == true"
  on_pass: "Proceed to implementation"
  on_fail: "Request review from tech lead"
```

## Tiered Release Gate

```yaml
gate:
  name: "Release Readiness"
  conditions:
    logic: AND
    checks:
      - type: threshold
        condition: "test_coverage >= 90%"
      - type: completion
        condition: "security_scan_passed == true"
      - type: completion
        condition: "performance_baseline_met == true"
      - type: approval
        condition: "product_owner_signoff == true"
  on_pass: "Deploy to production"
  on_fail: "Block release, notify team lead"
```

## Conditional Skip Gate

```yaml
gate:
  name: "Documentation Gate"
  conditions:
    logic: OR
    checks:
      - type: completion
        condition: "docs_updated == true"
      - type: completion
        condition: "no_public_api_changes == true"
  on_pass: "Proceed to merge"
  on_fail: "Update documentation before merge"
```
