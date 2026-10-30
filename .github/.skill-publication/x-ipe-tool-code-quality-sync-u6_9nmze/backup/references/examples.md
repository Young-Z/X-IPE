# Quality sync examples — illustrative contracts, not observed production outcomes

## 1. Local API descriptive drift against approved goals

Approved FR-USER-01 / US-USER-01 / AC-USER-01 says password reset requires a valid
token; the approved functional API is already implemented and characterized in
src/api/users.py with src/models/user.py and src/services/auth.py as inspected
dependencies, not added write permission. An old design describes a class.
Authorized local sync corrects only the stale design description/links and adds
targeted happy/error/edge preservation tests. No invented five-second SLA, token
lifetime or complexity requirements. Technical Design Change Log records actual
date/hashes. Undocumented bulk import stays an observed note until approved, not
automatic acceptance. All numbers below are illustrative, not measurements.

| Goal / Parent / Source | Baseline / Target | Docs Considered | Preservation / Type | Evidence / Limits | Disposition |
| --- | --- | --- | --- | --- | --- |
| Q-USER-01; US-USER-01; FR-USER-01#AC-USER-01 | approved token boundary unchanged; stale class description | requirements; specification; technical design | AC-USER-01; Unit; same results/errors at base and target | source/test/doc/config hashes and actual date required; outcome not measured | descriptive drift only; no changed requirement |

Example instantiated handoff: original result keys, exact scope/suggestion/goals/
target_structure/principles, doc count from changed design, tests counted from
actual tests, line_coverage=null and overall_quality_score=null when unmeasured.
Local optional coverage does not block independently evidenced preservation.

## 2. Bug is not documentation drift

Approved token boundary: expiry == now is expired. Code accepts equality; a test
that accepts equality can pass while violating AC-USER-01. Keep requirement/AC
unchanged, add the authorized expected-rejection characterization and retain its
actual failure evidence. alignment_state=divergent, BUG_FOUND and readiness=false.
Do not rewrite requirement to equality-valid, automatically skip/xfail the test,
fix source, or add repair to pass-through refactor scope. User-requested grace
period changes approved behavior and requires actual human CR authority instead.

## 3. Missing requirements, features or technical design

No approved goal documents exist for a legacy user module. Record not_found and
unavailable alignment, not zero score, measured zero coverage or aligned after
creating files. A caller-authorized draft may describe observed user CRUD,
authentication and notifications but is explicitly observational, not approved
requirements/ACs. Reuse an explicit legacy story so-that only as inferred anchored
intent. Missing pertinent intent blocks that goal/coverage claim, not unrelated
established delivery. success can mean completed assessment with readiness=false.

## 4. Broad scoped preservation, not global repair

Approved cross-module payment API refactor has stable imports/results/errors/data
and redaction. Run planned relevant integration/full suite; map every critical
changed path and affected caller at base and target. Suppose actual comparable
coverage is 62% then 84%: record those values only with method/scope/denominator/
dates/hashes. 84% does not waive an untested security boundary; 62% alone is not
an arbitrary block if critical evidence and applicable policy permit proceeding.
Broad default line80 is a guideline; mandatory thresholds require an applicable
authoritative source. Unrelated suite failure stays reported, not silently repaired.
No synthetic score 10 from adding tests or docs. Preserve existing tracing/redaction.

## 5. Skill/document study with unavailable metrics

Caller selects study-only, skill/document targets and one read-only report. Inspect
entry/resource/output contracts with the installed validator and relevant disposable
fixtures if authorized. No source/doc/test mutation or production promotion;
line_coverage=null, overall_quality_score=null, coverage not_applicable with reason.
No forced newinfra, compile, tracing or coverage framework. Base/target missing
fingerprints mean preservation unavailable, not automatically maintained. Passing
fixtures establish their engineering observations, not autonomous tool execution,
caller compatibility or observed stakeholder outcome. Readiness=false for study;
success=true only when the authorized assessment/report actually exists.

## 6. Evidence invalidation and honest boundaries

After a targeted design or assertion change, recompute relevant hashes and rerun
affected checks; do not reuse earlier green. Required critical checker unavailable
has exit=null; attempted failure has actual nonzero exit. Keep historical metrics
with provenance and optional legacy current_percentage numeric alias even when
its scope differs from current line_coverage. Explain divergence/unavailability,
retain code_alignment exact input and unaffected evidence. A strict downstream
consumer rejecting null returns a compatibility gap, not coerced score or success.

