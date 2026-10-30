# Acceptance Test Cases

> Feature / approved standalone scope: {actual identity and title}
> Status: Draft | Ready for Execution | Executed with gaps | Verified delivery
> Revision: {relevant hashes, not timestamp-only freshness}

## Overview

| Attribute | Value |
| --- | --- |
| Feature / Scope | {actual immutable feature or approved standalone identity} |
| Specification / Source | {project-root-relative links and source anchors} |
| Design / Implementation | {both design parts and actual files} |
| Target URL | {actual browser URL only for UI; otherwise N/A} |
| Config / Capability | {actual testing enablement/disabled diagnostics} |
| Planned Cases / Priority | {diagnostic count, P0/P1/P2; not goal} |

## Goal / Subgoal Frame

Copy approved source/story values, no invented goals/KPIs/observations. Legacy
explicit so-that inference labeled with exact anchor. Qualitative scenario suffices.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {stable source/story ID} | {source/parent anchor} | {actual stakeholder} | {approved outcome} | {selected means; all-required versus alternatives} | {source-derived scenario and gap} | {approved constraints} | {all scoped AC IDs} | {not measured or cited actual observation} |

## Full Acceptance / Evidence Map

Every scoped AC, original assertions, types and necessary branches retained.
Cross-type AC has all suitable TCs; selected alternatives are not extra scope.

| Source / Parent Goal | Story / Subgoal | AC ID | TC / Type | Original Assertions | Evidence / Revision | Delivery State | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {source/parent} | {stable story/subgoal} | {AC ID} | {TCs and original types} | {every approved expected clause} | {actual command/result/environment/hashes or not run} | {planned/invalidated/blocked/verified engineering delivery} | {not measured or cited stakeholder observation} |

## Prerequisites and Relevant Inputs

- Same current task/readiness/owner; approved source/acceptance/implementation scope.
- Actual specification/both design parts/source/package files and protected baseline.
- Applicable API/CLI/library/integration runners/data/setup; no universal browser,
  deployment/merge or manual data prerequisite.
- Frontend-ui only: configured enabled available isolated/dedicated actual browser,
  reachable URL, navigate → trigger path → console and every original assertion.
- Current testing config and required risk review; unavailable scope stays Blocked.

| Role | Actual Path / Boundary | SHA256 / Environment Revision | Dependent ACs / Rationale |
| --- | --- | --- | --- |
| source | {parent/intent source file} | {actual hash} | {source dependencies} |
| specification | {actual specification} | {actual hash} | {all scoped ACs} |
| code | {every relevant source/package file} | {actual hashes} | {behavioral dependencies} |
| config | {tools/workflow/runtime/declarations} | {actual hashes} | {capability/gates/behavior} |
| test | {tests/plan/fixture assertions} | {actual hashes} | {original assertions} |
| design/mockup/interface/environment | {applicable explicit files/live setup} | {hashes plus actual versions/boundary} | {why relevant or justified absence} |
| evidence | {captured log/snapshot/review/screenshots} | {actual hashes} | {TC/AC proof and limits} |

## Typed Test Cases

Instantiate only applicable groups, never omit scoped ACs:
Frontend-UI Tests (frontend-ui), Backend-API Tests (backend-api), Unit Tests (unit,
including library public API), Integration Tests (integration, including CLI
subprocess/filesystem), Structured-Review Tests (structured-review, skill/docs/config).
Executable skill helper scenarios still execute, not review-only keyword checks.

### TC-{stable ID}: {Title}

**Acceptance Criteria Reference:** {source/story/subgoal and AC anchors}
**Priority:** P0 | P1 | P2
**Test Type:** frontend-ui | backend-api | unit | integration | structured-review
**Assigned Tool / Runner:** {enabled actual capability/test-only adapter or Blocked}
**Preconditions:** {source-derived setup/auth/data, actual boundary}
**Original Assertions:** {all original clauses, including errors/no-mutation}

**Test Data:**

| Type | Field / Argument / Boundary | Value | Provenance / Expected Source |
| --- | --- | --- | --- |
| Input / Selection / API Payload / CLI Args / Library Params | {input} | {safe fixture} | {approved source} |
| Expected / Compare | {observable condition} | {approved value or before/after} | {original AC clause} |

**Test Steps:**

| Step | Action / Command / Review | Selector / Endpoint / Public API / Deliverable | Input / Setup | Expected Result |
| --- | --- | --- | --- | --- |
| 1 | {actual setup/call/subprocess/read} | {real type-appropriate boundary} | {safe data} | {original expectation} |
| 2 | {observe/assert; UI console where applicable} | {actual checkpoint} | {fixture} | {all remaining clauses} |
| 3 | {cleanup/no-mutation verification} | {safe before/after} | {data} | {specified invariant} |

**Expected Outcome:** {engineering AC behavior, not stakeholder achievement}
**Status:** Not Run | Pass | Fail | Blocked | Partial
**Actual Execution / Reuse:** {actual command/review/exits/expected-versus-actual or gap}
**Environment:** {actual setup/version/boundary; mocked/in-process/deployed/browser limits}
**Evidence / Inputs:** {project-root-relative artifacts and precise dependency hashes}
**Reuse Disposition:** {fresh or independently checked explicit current inputs/full relevant ACs}
**Observation Gap:** {not measured unless cited actual stakeholder/context observation at revision}

## Test Execution Summary

| Test Case | ACs / Subgoal | Title | Type | Priority | Status | Evidence / Gap |
| --- | --- | --- | --- | --- | --- | --- |
| {TC} | {all assigned ACs} | {title} | {original type} | {P0/P1/P2} | {actual status} | {current proof or blocker} |

## Execution Results

**Execution Date / Reviewer:** {actual provenance, not freshness by timestamp}
**Environment:** {actual versions/setup and safe boundary}

| Type | Total Planned | Passed | Failed | Blocked | Partial / Not Run |
| --- | --- | --- | --- | --- | --- |
| frontend-ui | {count} | {count} | {count} | {count} | {count} |
| backend-api | {count} | {count} | {count} | {count} | {count} |
| unit | {library/function count} | {count} | {count} | {count} | {count} |
| integration | {CLI/flow count} | {count} | {count} | {count} | {count} |
| structured-review | {skill/docs/config count} | {count} | {count} | {count} | {count} |
| TOTAL | {all planned} | {count} | {count} | {count} | {count} |

Pass Rate = passed / ALL planned including blocked/not-run/partial; zero cases N/A,
not 100%. Counts/rate diagnostic, not goal achievement or stakeholder impact.

### Failures / Blockers / Review Limits

| TC / AC | Expected versus Actual / Missing Evidence | Evidence | Recommended Bounded Action |
| --- | --- | --- | --- |
| {case/AC} | {real failure/blocker} | {current log/screenshot/review} | {owner decision, no unauthorized code fix} |

### Engineering Delivery versus Stakeholder Outcome

| Goal / Subgoal | Delivery Evidence / State | Outcome Scenario / Observation | Outcome State / Gap |
| --- | --- | --- | --- |
| {source ID} | {fresh all-AC suitable checks or unsupported claim} | {approved qualitative scenario; actual citation only if observed} | {not measured or cited observed stakeholder outcome with limits} |

### Refactor / Closing Recommendation and App Gates

Refactor need: {inspected issue and preservation need or no evidenced need; conditional}.
Original conditional successors retained, no compulsory code churn. Current app
code_refactor is optional: no-need delivery routes directly to closing.
Honor explicit project customizations. No fake skip/done/report. Acceptance delivery/
action evidence separate from route availability. Owner alone writes/verifies
acceptance_testing with actual test-report/test-folder and specification/impl-files,
done implementation and matching readback once. Free-mode no app mutation.

## Optional Deterministic Reuse Record in This Report

Actual record only, never execute scaffold as proof. Expected manifest independently
resolved from current source/spec/ACs/dependencies, not copied from this claim.

```yaml
acceptance_evidence:
  feature_id: "{actual feature or approved standalone identity}"
  inputs:
    - role: source
      path: "{actual source file}"
      sha256: "{actual SHA256}"
    # Include ALL explicit specification/code/config/test/evidence inputs plus
    # applicable design/mockup/environment/interface artifacts, not only source.
  cases:
    - tc_id: "{actual TC}"
      ac_ids: ["{all assigned AC IDs}"]
      test_type: "{original type}"
      status: "{actual Pass/Fail/Blocked/Partial/Not Run}"
      assertions: ["{all original clauses}"]
      command_or_review: "{actual command or precise review scope}"
      result: "{actual exit/result/expected-versus-actual}"
      environment: "{actual boundary/setup/version and limits}"
      evidence_paths: ["{actual hashed evidence artifacts}"]
```

Helper verifies exact explicit current inputs and all relevant AC/types/assertions.
The same case schema applies to every original type. Each expected AC/type pair
covers its complete original assertion list; same-type cases may split clauses,
but no cross-type assertion borrowing. Type-specific reuse partitions preserve
original AC IDs and full merged coverage, never reduce accepted scope.
Independent semantic/type-specific execution provenance and current environment
review required. Fixtures/DAO/approval/automation do not observe stakeholder impact.
