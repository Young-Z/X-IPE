# Queue Schema and Helper Contract

One Markdown file per primary skill:
`x-ipe-docs/skill-meta/{skill}/x-ipe-meta-lesson-learned.md`.
Legacy `lesson-learned.md` is accepted when canonical is absent; two files block.
Old prose/raw/reviewed/incorporated/undated formats are read-only protected,
not silently normalized. Reviewed historical migration is separate work.

The bundled template is an empty queue; substitute its skill name. Helper
capture can initialize it without external project templates. YAML frontmatter
has exactly schema=1, skill_name, next_id. Each `## LL-NNN` heading encloses
one fenced YAML mapping. next_id increases monotonically even after purge.
No redundant counters, last_access, generic last_updated or separate index.
Duplicate/non-string YAML keys and invalid chronology are protected, not silently
rewritten. Expiry equals last_validated_at plus the admitted TTL; critical review
equals validation plus 90 days. Terminal time cannot precede validation.

Required record fields: id, severity, summary, cause, corrective_rule,
verification, admission, evidence, status, occurrences, created_at,
last_validated_at, expires_at. All textual values are bounded single-line text;
summary ≤240 characters; two evidence references ≤500 characters each.
Other required text ≤1000 characters. Links refer to existing task/test evidence
whose qualitative relevance the agent verifies; helper does not score impact.

Admission requires kind, reason, reusable_gap, coverage_check, ground_truth.
`critical` also needs impact and critical severity. `high_value` needs major
severity, basis (`verified_recurrence` or `systemic_contract_gap`) and
basis_evidence. `user_override` needs explicit_request, purpose, integer
ttl_days 1-180; no invented critical promotion. Optional applies_to lists
consumer skill names. Normal lifetime is critical 180 / major 90 days.

Planned adds plan (task, owner, candidate, change, test), planned_at.
Applied adds application (production revision, publication/test receipt paths
and hashes, idempotency ID). Retired adds retirement_reason and optional
handoff. Both add terminal_at and purge_after exactly 30 days later.
Critical adds review_due at 90 days. Compact YAML can exceed 20 physical lines
when ownership/receipts are necessary; prefer short linked values over logs.

## APIs

Load the bundled script through importlib or its script path. All APIs receive
explicit approved roots, never discover CWD or global state:

- `load(root, skill)` → path, revision, document or protected legacy disposition.
- `capture(root, skill, proposal, expected_revision=..., now=None, recurrence=False)`.
- `select(root, skills, relevant_to=None, now=None)` across owners: five summaries,
  critical_overflow IDs, protected records, critical/planned review notices.
    Expired relevant critical identities surface cleanup notices, never summaries.
- `settle(root, skill, lesson_id, decision, expected_revision=..., now=None)`.
- `prune(root, skill, now=None, apply=False, expected_revision=None,
  preservation=None, handoffs=None)` → actions/blocked and revision.

Keywords after positional arguments are keyword-only. `now` is explicit UTC
ISO timestamp (Z or +00:00), never a date or naive local time. Mutating calls
require the snapshot SHA256 even for a new file (SHA256 of empty bytes).
Expected revision mismatch fails; caller rereads and reviews, not blind retry.
Exceptions indicate invalid schema/evidence/path/conflict; CLI returns JSON
`ok=false` exit 1. Argument parsing errors exit 2. Blocked operation dispositions
are valid JSON results, not claimed successful admission/application.

## CLI

Invoke the installed Python interpreter with bundled scripts/lesson_ops.py,
operation (`capture|select|settle|prune`), `--project-root`, repeatable `--skill`,
optional `--now`, `--expected-revision`, `--input` JSON object, and prune-only
`--apply`. No stdout receipt is written automatically. Writes allow one owner.
Input: capture accepts proposal directly or `{proposal, recurrence}`; select
accepts `{relevant_to}`; settle `{id, decision}`; prune `{preservation, handoffs}`.

## Evidence Gates

Planned decision: status=planned, owner={path, task_id, owner}, candidate,
change, test. Candidate must be the existing canonical owner-skill candidate.
Task path must be `x-ipe-docs/planning/tasks/tasks-YYYY-MM-DD.json`, containing
exactly one matching task with existing task schema. Owner must equal its role,
not unassigned/unknown/none; status must be pending/in_progress/blocked/deferred.
Helper reads but never creates or modifies tasks. External issue providers are
not verified in this minimal helper; use existing-schema owned tasks instead.

Applied decision: status=applied, task, production_revision,
publication_receipt, test_receipt. Receipt files must be existing project-relative
JSON. Creator publication receipt needs ok=true, operation=publish,
state=published, byte_parity=true, matching name, complete files hash manifest
including SKILL.md. Helper checks manifested production bytes. The agent must
verify trusted provenance: JSON alone cannot cryptographically prove a test ran.
Test receipt needs ok=true, tests_passed=true, skill_name, production_revision,
lesson_ids containing scoped lesson ID, verification matching the planned test,
and candidate_hash matching publication receipt. Publication fingerprint is the
production_revision (not an arbitrary Git-string declaration).
Receipt hashes make replay idempotent; expiry/terminal dates do not reset.
An already applied identical receipt with matching task verifies artifact hashes
without requiring old production bytes still be installed. Changed receipts or
wrong ownership block; first application always verifies current production.
Repeating the same valid owned plan is unchanged; replacement mappings require
explicit release first. Recurrence/settlement cannot rewind plan/terminal time.

Release decision: status=active, matching task, reason; preserves original TTL.
Retire decision: status=retired, reason, matching task if planned. Critical also
requires handoff={path, task_id, owner}. Canonical lesson backlink including
`#LL-NNN` must exist in task output_links (use the actual legacy filename when
that queue is loaded). Conservative gate does not infer a
critical issue resolved from an arbitrary reason string. Applied→active is only
through evidence-backed recurrence capture; retired re-admission blocks.

## Maintenance and Safety Limits

Prune never invokes Git. Therefore every physical purge defaults to untracked/
WIP protection. To authorize removal supply preservation={kind:
explicit_user_approval, revision: snapshot SHA256, authorized_by, reason}.
Approval is explicit metadata supplied by the agent from the user, not inferred.
Critical unresolved retirement/purge verifies a live open owned task and scoped
backlink at operation time. Without it expired entries remain excluded but kept.
First approved expiry maintenance sets retired and starts 30 days; a second
operation after grace can purge. IDs never reset. Dry-run creates no locks or
parents and changes no bytes. Apply locks and checks revision, preserving other
entries. No blanket on-disk cap is promised when protected cleanup blocks.

POSIX flock is nonblocking on a stable per-skill lock file; atomic temporary
write uses fsync and os.replace, rechecks revision. Lock file remains for stable
inode cooperation. No guarantee against hostile writers ignoring the lock;
power-loss directory durability, remote filesystems and Windows need review.
Admission/dedup require agent semantic evaluation. Explicit revalidation without
a new occurrence is conservatively unsupported; use reviewed evidence-backed
recurrence or report blocked. No automatic abandoned-plan release is performed.

## Consumer Integration Boundary

Creator select/planned/settle execution, packaged instruction variants and old
global-template consumers need separate integration and end-to-end evidence.
This package provides explicit APIs, not an automatically wired learning loop.
Historical lessons remain protected; no conversion or migration is implied.
