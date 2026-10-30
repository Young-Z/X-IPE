# Feature Acceptance Test — Detailed Procedures

Domain-only under same lifecycle owner/readiness. Preserve original test types,
assertions and approved expectations; examples are illustrative, not new scope.
Read entry and integration for capability, revision, app and ownership gates.

## Test Type Classification Guide

| Type | Actual Boundary / Observable Check | Capability |
| --- | --- | --- |
| frontend-ui | Rendering, interaction, form, responsive/scoped visual state and browser console | Enabled available Chrome DevTools MCP, enabled UI skill if used |
| backend-api | Approved HTTP route/method/request/status/body/headers/errors/auth/side effects | Enabled matched stack/test runner; disclose in-process versus deployed |
| unit | Function/class/library public API/import/input/output/error contract | Enabled appropriate existing runner/test-only adapter |
| integration | Components/service/state/filesystem/CLI entry and cross-boundary contracts | Enabled appropriate runner or authorized browser where required |
| structured-review | Complete skill/prompt/docs/config contract against original AC and consumers | Actual cited review; required executable scenarios still execute |

An AC may need multiple types. CLI subprocess behavior is integration even when
parser unit tests exist; library public import/API checks remain executable.
Skill/non-code scope is not automatic ALL-review: helper/CLI/browser semantics
require suitable actual execution evidence. No default frontend-only assumption.
Use the same source/goal/AC/TC/assertion/revision/result case schema for all types.
Explicit reuse expectations cover every original clause for each required type;
same-type cases may split clauses, another type cannot hide an omitted assertion.
Different type-specific expectations use explicit partitions with unchanged AC
IDs and full merged report coverage, not a weaker acceptance contract.

## Per-Type Implementation Analysis Patterns

### Frontend-UI

1. Locate actual UI template/JS/component files from impl-files, relevant script
   load order/dependencies and current scoped mockups. Identify stable controls.
2. Prioritize data-testid → stable id → aria-label → robust unique selector;
   avoid generated IDs, div chains and fragile classes. Verify selector existence/
   uniqueness against actual page, not only source. Add event-based waits/dynamic
   state assertions, not blind sleeps.
3. Plan every original observable clause (including scoped states/accessibility/
   responsiveness/no-mutation) and console/load/runtime errors. Source/jsdom
   checks supplement actual browser, cannot prove the UI path or stakeholder gain.

### Backend-API

1. Inspect actual routes/method/schemas/content-type/auth/dependencies and approved
   response/status/error/side effects. Do not invent required 4xx/5xx branches.
2. Test relevant valid/error/boundary scenarios with authorized isolated data,
   API client (curl/httpx/fetch/framework) and real applicable application boundary.
3. Record exact request/response/headers/exit/result/setup and disclosure of
   mocked/in-process/deployed limits; retain original assertion clauses.

### Unit and Library Public API

1. Inspect real public signature/import/module, contract constraints and errors.
2. Execute valid/boundary/error and approved side-effect/non-mutation assertions
   through actual public interface; record inputs/result/runner/environment.
3. Mocks isolate unit dependencies only, do not claim end-to-end/API/browser proof.
   Keep library import/compatibility checks where acceptance requires them.

### Integration and CLI

1. Inspect services/entrypoint/flags/config/cwd/exit/stdout/stderr/filesystem setup.
2. Run actual CLI subprocess or component flow in disposable environment with
   source-derived data; inspect outputs and every specified side effect/invariant.
3. Capture before/after files/state, actual exit/streams and cleanup. In-process
   parser checks do not prove executable CLI behavior; direct API mocks do not
   prove network/UI boundaries when source requires actual interaction.

### Structured Skill/Prompt/Docs/Config

1. Read entire relevant package/resources and authoritative source/goal/ACs;
   cite exact content/sections/lines and actual consumer declarations/config.
2. Deterministic structure/link/schema checks are necessary where specified,
   but keyword count/section presence alone cannot prove behavioral semantics.
3. Execute applicable enabled validator/helper scenarios in temporary projects;
   inspect ownership/routing/config/current outputs/error/no-mutation semantics.
   Independent risk review cannot be replaced with self-review or DAO approval.

## Browser Prerequisites and MCP Patterns

Only frontend-ui needs actual reachable target and configured enabled browser.
Use dedicated --user-data-dir or isolated server; no attaching to user's unrelated
Chrome profile. No reinterpretation of a different tool as enabled Chrome MCP.
If capability unavailable, retain cases as Blocked, no source-only UI pass.

```text
Check actual profile/configuration → navigate actual URL → snapshot actual page
→ find unique selector → trigger relevant feature interaction → wait for state
→ assert all original expected clauses → inspect browser console/load errors
→ capture failure screenshot/snapshot/console → cleanup safe fixture state
```

Enabled UI skill execute_ui_tests receives real TCs/URL/current mockup, failure
screenshots and actual screenshot directory. Enabled direct MCP is alternative
when that skill is disabled, not when Chrome MCP itself is disabled/unavailable.
Screenshot-on-failure and console/runtime diagnostics keep evidence hash-bound.
Actual semantic visual assertions suffice; no invented match_score required.

## API, Unit and CLI Command Patterns

Illustrative patterns only; endpoints/status/arguments/assertions must be from
current spec. Existing runner inside enabled matched capability is preferable
to inventing a test-only operation. A bounded adapter may generate only approved
tests, never normal implement/fix/refactor source mutations during acceptance.

```python
# Illustrative: actual feature contract supplies these approved values.
def test_article_contract(client):
    response = client.post("/api/kb/articles", json={"title": "Test", "content": "body"})
    assert response.status_code == 201
    assert response.json()["title"] == "Test"

def test_cli_contract(command, tmp_path):
    import subprocess
    before = sorted(p.name for p in tmp_path.iterdir())
    result = subprocess.run(command, cwd=tmp_path, text=True, capture_output=True)
    assert result.returncode == 1
    assert "error" in result.stderr
    assert sorted(p.name for p in tmp_path.iterdir()) == before
```

For actual no-mutation acceptance compare relevant contents/hashes, not only
names. Execute existing pytest/vitest/JUnit or inspected library test framework;
retain all original assertions. Missing runner/tool/config is Blocked, not skip.

## Test Data Collection

| Data Kind | Source | Boundary |
| --- | --- | --- |
| Input / Selection | Existing safe project fixture or authorized generated data | No secret/production mutation |
| Expected | Approved source/AC original assertions | Never invented target or inferred API status |
| Compare | Actual before/after state/files/observable result | Match approved invariants |
| API Payload / CLI Args / Library Params | Inspected source/schema and approved contract | Exact runner/cwd/auth/setup |

Ask only real gaps by current mode: human asks human; full DAO and hybrid use bounded guidance.
No ceremonial manual data question for known valid fixtures. Synthetic data or
review approval does not observe stakeholder outcome. Keep provenance in report.

## Reflection Checklist

- Every scoped AC/story/subgoal/source covered with all original assertions/types?
- Preconditions/steps/data/observable results valid from actual interfaces?
- All-required branches versus selected alternatives preserved within constraints?
- Type-specific boundary actual, selectors/waits/console appropriate, API schema/
  auth/error, CLI exit/streams/files, library public import/error, integration
  state/setup/cleanup, structured contracts plus required scenarios?
- Relevant source/spec/code/config/tests and applicable design/mockup/environment/
  evidence dependencies explicit and hash-bound, full reuse coverage validated?
- Failed/partial/blocked/unavailable cases retained, no weakened/skipped checks?
- Actual delivery separate from not measured/cited stakeholder observation?
- Independent review satisfied for risk, current mandatory app gates respected?

## Result Reporting and Freshness

Report all planned cases as Not Run/Pass/Fail/Blocked/Partial, actual expected-
versus-actual, commands/exits/review/environment, artifacts/hashes and limits.
Group per original type; CLI/library fit existing integration/unit groups, no
new mandatory output keys. Pass rate is passed/all planned including blockers/
not-run/partial, zero cases N/A. Counts are diagnostic, never goal achievement.
Only current all-AC suitable pass plus required review supports verified delivery;
stakeholder impact not observed explicitly remains not measured. Automation,
fixtures, source review and DAO/human approval cannot prove stakeholder benefit.

Rehash explicit dependencies before handoff. Failed/stale/incomplete reuse is
affected rerun/blocker, not success by timestamp/receipt. Dependency-independent
unaffected mappings/IDs/history stay intact; parent/intent/means deltas need
authorized scope and invalidate affected dependent evidence. Do not overwrite
preexisting dirty docs or historical results to disguise a failed check.

## Failure, Resume and Routing

Preserve independent passing evidence after failures; report bounded diagnosis/
recommended action to owner without editing implementation or expectations.
Unsupported tool operation or unavailable browser blocks pertinent execution.
No-op resume verifies current hashes/action/readback read-only, no replay writes.
Owner alone handles verified test-report/test-folder acceptance_testing write,
appropriate Tested transition and original conditional suggestions. Current app
code_refactor remains mandatory; no quality need creates a routing blocker, not
compulsory code change or fake skip/done/report. Later config migration is separate.
