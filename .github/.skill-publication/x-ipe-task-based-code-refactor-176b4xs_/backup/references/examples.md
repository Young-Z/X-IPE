# Refactor examples — authored contracts, not production changes

Examples are fixtures, not actual approval, autonomous skill/tool execution or
stakeholder observation. The dedicated test separately executes the miniature
price refactor in a disposable directory. No application source is modified.

## 1. Local: one shared decision, same public price contract

Authored source US-PRICE-01 / AC-PRICE-01: retail and wholesale return the same
clamped doubled price; invalid input retains TypeError. Maintainer enabling goal
is fewer places to accidentally diverge, not a fabricated stakeholder percentage.

| Goal / Subgoal | Parent / Source | Stakeholder | Contribution / Selection | Baseline | Success Evidence | Preservation / AC / Type | Trade-off | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q-DUP-01 | US-PRICE-01; fixture contract | maintainer; indirect contribution to price consistency | all-required same outputs/errors and reduced duplicated decision; alternatives extraction versus keeping duplication; extraction selected | two identical price decisions in inspected disposable source | one shared decision after extraction; same six preservation checks at both revisions | unchanged public functions/results/errors; AC-PRICE-01; Unit | extra internal call and indirection; no performance gain claimed | not measured |

Arrange negative/zero/integer/fractional input and invalid None; Act original
public retail/wholesale; Assert original results and TypeError. Baseline tests
are green, not manufactured red. Extract private _price, keep both public wrappers.
Actual disposable fixture runs six checks before/after with unchanged test hashes;
counts two repeated decisions before, one after. No score or coverage percentage
is measured. Trade-off is an extra internal call; benchmark would be needed for
performance claims. Goal is verified fixture engineering only, not stakeholder gain.

Analysis adapter records inspected source, public/error boundaries and named gap.
Targeted sync would update only existing affected design/reference links; no new
requirements, blanket 80% or project-wide alignment. This fixture does not claim
actual analysis/sync tool invocation. Source/AC frame is authored, not app authority.
Designated quality_score_before/after strings say not measured; do not synthesize
1–10 totals. Unmeasured coverage returns before: null, after: null, status: null
with not measured explained in the report, not a false maintained status. A strict
legacy consumer rejecting null is a pertinent integration gap, not forced scoring.

## 2. Broad: split a large API module without losing public exports

Retain the original large users API split use case: inspected CRUD/auth/password/
bulk/util responsibilities might justify separate modules. Size alone is not
success; name easier independent maintenance as a qualitative goal with exact
component responsibilities and caller checks. Five extracted files is an option,
not a required goal count or automatic plan.

Inspect actual imported public names, callers, data/error/resource behavior and
existing tracing/redaction before extraction. Authorize each phase separately
within the approved broad scope; preserve original imports through re-exports.
An ImportError at api.users.reset_password after moving it is a regression: repair
re-export/import structure, NOT replace the caller assertion with a new private
module path. Same contract tests remain. Named trade-off: more module boundaries
and import edges, balanced against cohesion demonstrated by responsibility map.

Broad verification includes relevant integration/full suite, applicable build/lint
and same-scope measured coverage when justified. Existing docs/Change Log record
new structure; requirements/ACs remain authoritative. Numeric quality requires
real comparable method/results; historical invented 4.6→8.6 or 47-test totals are
not evidence. No automatic commit or human approval claimed in an example.

## 3. Rollback: missing dependency causes a behavior regression

Original rollback use case: move helper without its dependency; changed results
cause preserved assertions to fail. Stop, inspect actual failure and bound cause.
Restore only owned phase bytes after checking no concurrent change, using edit
tools; never checkout an earlier Git revision or discard dirty foreign work.
Revise to move the dependency coherently and rerun unchanged assertions. New
regressions block completion; no legitimate behavior-change test rewrite shortcut.
Changed expected behavior is a separately authorized actual-human CR boundary.

## 4. Study-only and legacy source gaps

Assessment request selects study-only: read sources, inspect dependencies and
record analysis report/recommendations. Missing documents stay not_found/gaps,
not created from code to claim alignment. No source/test/doc mutation except the
approved analysis deliverable; no global prerequisites or achieved refactor claim.
An explicit legacy so-that supplies inferred parent intent with anchor only;
missing intent blocks pertinent outcome claims, not unrelated delivery checks.

Current workflow code_refactor is mandatory. Study-only is not app done, nor
permission to mark it skipped. Return report and exact context to owner; actual
completion still needs required tech-design/specification, predecessor checks,
accepted deliverable and readback under the unchanged integration. Report writer
success without those conditions is insufficient.

## 5. Skill package and mixed-stack routing

A skill target routes through creator candidate/metadata/validator/review and
separate authorized publication, same task/readiness. It is not arbitrary
production edits through a generic implementation tool. Mixed Python/UI changes
route enabled matching tools sequentially with original AAA preservation checks;
explicit disabled tools are not force-enabled. No inline production fallback.
Python's explicit optional refactor feature_context exception permits tool-local
synthetic REFACTOR-task only; never allocate an actual feature or invent design.
Other tools' own contracts decide readiness, not assumed Python compatibility.
