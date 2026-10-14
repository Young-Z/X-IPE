# Analysis examples — authored fixtures

Contracts, not executed agent decisions, human approval or observed stakeholder
outcome. Dedicated tests separately inspect disposable actual imports/byte hashes
and serialize authored reports/outputs. No production source changes.

## 1. API module: correct known dependencies

Study mixed CRUD/auth responsibilities for safer independent maintenance; preserve
public exports/errors/data/redaction. An 800-line file alone is no split criterion.
Authored directed edges, not claims about this repository:

| Source | Target | Reason |
| --- | --- | --- |
| src/api/users.py | src/models/user.py | imported model |
| src/api/users.py | src/services/auth.py | called auth service |
| src/api/users.py | src/utils/validation.py | imported validation |
| src/routes/v1.py | src/api/users.py | inverse public caller |
| tests/test_users.py | src/api/users.py | preservation tests |
| src/services/auth.py | src/models/session.py | imported session model |
| src/services/profile.py | src/models/user.py | inverse model consumer |

Pass 1 adds direct imports and relevant inverse callers/tests; pass 2 session and
profile under shared-model risk; pass 3 no new paths, stable known closure. Correct
src/models/user.py paths consistently retained; independent siblings excluded with
reasons. No all-hidden-dependencies claim. Outside-root required consumers stay
unresolved for owner, not ignored. Requirements/Features/Tech Spec separate; test
coverage command/method/denominator if measured else null/not_measured; tracing
configuration/redaction/applicability. Invented 62% or total 6 is not evidence.
Each boundary suggestion cites responsibility/caller sources, checks and extra
import-edge trade-off. Recommendations only, not achieved improvement or app done.

## 2. No documentation: legacy/payment.js

Missing documents (requirements/spec/design) are not_found, not behavior failure.
Unavailable coverage tool: null/not_measured, not zero coverage. No tests found is
a verified test gap, not measured zero. Missing baseline: exists=false/score=null.
Inspect public behavior/risk; explicit legacy so-that anchors inferred intent only
if actually present. Suggest bounded characterization for actual risky payment/
error branches. No create-all-docs, coverage80 or global compile prerequisite.
Executed failing check is failed with command/exit/output/hash, unlike unavailable.
Read-only analysis may succeed; later mutation needs pertinent preservation evidence.
No spec/source repair or tool-level approval question.

## 3. Qualitative goal: fewer divergent price decisions

Fixture US-PRICE-01/AC-PRICE-01: same retail/wholesale results/TypeError, no authorized
performance change. Maintainer safe-change confidence is the enabling quality goal;
extraction is one means, retaining duplication is an alternative with divergence cost.

| Suggestion | Gap / Source | Goal / Parent | Baseline | Success Evidence | Preservation | Trade-off | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S-01 extract shared price decision | G-01; price.py repeated expression; fixture revision | Q-DUP-01; US-PRICE-01; maintainer safe-change confidence | two repeated decisions; public results/errors unchanged | one shared decision; same public contract checks planned | AC-PRICE-01; Unit; keep exports/results/TypeError | extra internal call; no performance claim | not measured |

all-required: same outputs/errors and fewer repeated decision points; alternatives:
selected extraction versus retaining duplication. Planned checks are not achieved
results. No numeric rubric measured: scores null, report not measured. Size-only
restructuring and invented parent are invalid. Stakeholder outcome not observed.

## 4. Cycle, cap and unavailable boundary

Real disposable a.py imports b.py, b.py imports a.py, caller.py imports a.py; first
pass adds b.py/caller.py, second no new paths. Verified cycle terminates with visited;
unrelated.py excluded. Tests read actual fixture AST/edges and unchanged bytes;
not a general resolver or autonomous skill execution.

Pending frontier after pass 10 hits cap: incomplete, not guessed cycle. Record
frontier/exclusions/risk. Unsatisfied required full analysis returns success=false/
partial result; authorized bounded study can succeed with limits. Never claim full
closure when dynamic dependencies remain unresolved.

## 5. skills/documents and selective consultation

Schema/scenario/public-instruction checks, not runtime compilation. Disabled tracing
without applicable infrastructure: not_applicable; existing redaction preserved.
Missing creator validator unavailable/not_measured, actual failed validation failed.
Metadata-first matching: Python-only scope consults allowed Python excerpts, not
enabled Java/TS/HTML packages. MCP may need protocol and language guidance. Explicit
false general stays disabled. Missing/empty config enables legacy discovery only,
not full loading or source execution. Consultation is not enforcement evidence.
Comparable numeric rubric absent: null, no synthetic weighted score.
