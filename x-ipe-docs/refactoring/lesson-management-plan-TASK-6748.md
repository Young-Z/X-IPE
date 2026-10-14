# Selective, Time-Bounded Skill Lessons — Redesign Plan

Date: 2026-10-13 | Task: TASK-6748 | Assignee: Quill

**Planning only.** No production skills, candidates, existing lesson statuses, or historical lesson files were changed. Implementation remains subject to the user's approval of the broader refactoring work.

## 1. Decision

Refactor [lesson-learned](.github/skills/x-ipe-meta-lesson-learned/SKILL.md) from an append-only incident diary into a **small, time-bounded skill-improvement queue**.

- Capture only critical or demonstrably high-value reusable lessons, not every mistake or feedback item.
- Deduplicate by cause and corrective rule, not incident wording.
- Track adoption and verified application; reading is not application.
- Expire stale entries and remove them from routine context. Resolved lessons should become tests/instructions, not permanent repeated warnings.
- Do not conceal unresolved critical risks when forgetting the narrative: hand them off to an existing owned task/issue.
- Keep plain files and a small bundled helper, not a database, ontology, separate service, or scheduled agent workflow.

The numbers below are proposed defaults, not existing project behavior or empirically optimal thresholds.

## 2. Verified Gaps

| Current behavior | Evidence | Required change |
| --- | --- | --- |
| Broad capture trigger; no admission test | [Current description and scope](.github/skills/x-ipe-meta-lesson-learned/SKILL.md#L1-L42) cover issues, feedback, and edge cases. | Evaluate significance before creating a persistent lesson. |
| New entries are always raw | [Save procedure](.github/skills/x-ipe-meta-lesson-learned/SKILL.md#L202-L218). | Define selection, candidate adoption, verified application, retirement, and cleanup. |
| Status vocabularies disagree | [Actual template](x-ipe-docs/skill-meta/.templates/lesson-learned.md) uses raw/reviewed/incorporated; real records also use applied. | Normalize through migration; do not assume old applied text proves validated publication. |
| Documented template location is absent | The skill points to a different template path; the actual template is linked above. | Use one canonical template and align references. |
| Consultation is unbounded and read-oriented | [Creator consultation rule](.github/skills/x-ipe-meta-skill-creator/SKILL.md#L63), [production patterns](.github/skills/x-ipe-meta-skill-creator/references/12.%20reference-production-patterns.md#L7-L18). | Select a bounded set by relevance, severity, validity, and status; settle only selected lessons. |
| Large history already exists | Eight per-skill lesson files found; the [UIUX-reference file](x-ipe-docs/skill-meta/x-ipe-tool-uiux-reference/x-ipe-meta-lesson-learned.md) is 1,573 lines with 15 lesson headings. | Compact and migrate rather than keep loading incident histories. |
| Instruction variants point to a legacy filename | For example [English instructions](src/x_ipe/resources/copilot-instructions-en-no-dao.md#L159-L165). | Update canonical naming and support legacy lookup during migration. |

Repeated LL-001 IDs across skills are **not duplicates**: IDs are scoped by skill. Deduplication must inspect cause/rule, with identity `(skill_name, lesson_id)`.

## 3. Admission Gate — What Deserves a Lesson?

Create a new persistent lesson only when **all** of the following hold:

1. There is observed evidence or an explicit human correction establishing the problem; uncertainty is stated, not hidden.
2. The problem exposes a reusable gap in a skill's instructions, resources, checks, or recovery behavior—not just one task's incorrect implementation.
3. A concrete corrective rule and a verification method are known. An unresolved critical incident without established ground truth belongs in an owned issue/task first; do not invent a fix to satisfy the lesson schema.
4. No equivalent active lesson, existing authoritative rule, or tested safeguard already covers it. If a known rule was violated, improve its enforcement or discover the cause; do not copy the same warning again.
5. Impact qualifies as either:
   - **Critical:** data loss/corruption, confidentiality/security or authorization failure, destructive/unapproved action, or a materially invalid result that was incorrectly accepted as successful.
   - **High-value major:** a verified recurring failure, or a systemic contract gap likely to block ordinary future work, with a clear reusable correction. The major label alone is insufficient.

Do not auto-record cosmetic formatting, harmless one-off typos, preferences, speculative enhancements, ordinary debugging observations, or already-fixed local bugs with no skill-level gap. Fix them or use existing backlog/task notes.

Explicit user requests to retain a lesson are allowed as documented overrides, with purpose and finite expiry; do not silently promote them to critical. An explicit request not to retain an item must also be respected.

### Recurrence and consolidation

- Same root cause and same corrective rule: update the existing entry's bounded evidence and occurrence count.
- A real new occurrence can refresh validation/lifetime after checking the rule still applies. Reading, selecting, editing prose, or routine queries cannot refresh it.
- Cross-skill lessons have one primary owner and an applicability list. Link from consumers rather than replicate the full lesson under every skill.
- Keep at most two current evidence references in a lesson. Full logs belong to the original task/test artifacts.
- Reoccurrence after an applied fix is a regression: reopen the same lesson if still retained and reconfirm its cause. If already purged, create a new ID and cite the previous change/test if available.

## 4. Small Status Model

| Status | Meaning | What changes it |
| --- | --- | --- |
| active | Eligible, unexpired improvement waiting for a relevant update. | Verified admission or revalidation. |
| planned | Explicitly selected and incorporated into a named candidate update; not fixed yet. | Creator records lesson-to-change/test mapping and owning task/candidate. Merely opening or considering it is insufficient. |
| applied | Candidate was published, the intended safeguard exists, and the relevant verification passed. | Creator settles the selected lesson with production revision and test evidence after verified publication. |
| retired | Not eligible for routine use. | Expiry, invalidation, supersession, already-covered disposition, or explicit rejection, with a short reason. |

Transitions: active → planned → applied; active/planned → retired; planned → active on cancellation or failed publication after checking it remains valid. Applied → active only on verified recurrence. Superseded lessons include a replacement link rather than creating a separate status.

Reading has no global status. Considered-but-not-selected decisions belong in the current task/candidate validation record, not an expanding access log on every lesson. Do not require a minimum number of lessons read or applied.

### Creator failure/restart handling

- A candidate proposal never marks a lesson applied.
- Failed validation or merge leaves no false applied state; preserve/update planned ownership or release it to active.
- Publication receipts let a restarted creator settle the same lesson idempotently. Repeating settle must not create new records or change expiry repeatedly.
- Review planned entries after 14 days without owner progress. Release abandoned ownership, but do not steal an active task or reset the lesson's original expiry. A resumed task revalidates expired content before using it.

## 5. Time Span and Forgetting

### Proposed defaults

| Entry | Lifetime / handling |
| --- | --- |
| High-value major, active or planned | 90 days from admission or explicit evidence-backed revalidation. |
| Critical, active or planned | 180 days, with a review due after 90 days. No permanent immunity from expiry. |
| Applied | Excluded from normal selection immediately; retain compact application receipt for 30 days, then prune. The actual instruction/test remains authoritative. |
| Retired | Excluded immediately; retain compact reason/handoff for 30 days, then prune. |

Store explicit dates rather than calculate validity from generic last_updated. Use UTC timestamps and expire at `now >= expires_at`. Reading does not extend expiry; planned status does not pause the clock.

At expiry:

1. Immediately exclude the entry from normal lesson retrieval, even if physical pruning has not run.
2. Retire obsolete, fixed, low-value, or no-longer-applicable entries with a reason.
3. For a still-valid entry, renew only after actual source/version/behavior verification; record the new evidence and explicit date. No automatic sliding renewal.
4. For an unresolved critical risk, create or link an **existing-schema owned task/issue** before removing its only record. Its source of truth becomes that task, not a permanent lesson exception. If handoff fails, keep the excluded record and report the blocked cleanup; do not silently discard the risk or feed it back into every skill's context.

### What “forget” means

- Forget from active selection and default agent context immediately on expiry/application/retirement.
- Remove full entries from the working lesson file after the bounded grace period and validated handoff where needed.
- For tracked lessons, Git history is historical recovery; do not build a second ever-growing archive or summary index by default. Never rewrite history as part of this feature. For untracked/WIP records, do not prune until preservation/approval is established; report them as protected instead.
- Applied tests/instructions, linked risk tasks, and past publication records have their own lifecycles; lesson cleanup must not delete them.
- Review historical content only on an explicit investigation. Do not routinely retrieve it through creator, knowledge retrieval, or persistent-memory copies.

## 6. Bound Both Storage and Context

Proposed limits:

- **Eight pending entries per skill** (active + planned, including stale pending cleanup); prefer fewer. Aim for at most 20 nonblank lines per entry, with links rather than incident dumps.
- **At most five relevant lesson summaries per creator update across all consulted skills**, within an approximately 120-line summary budget. No full-file mandatory loading.
- Prioritize current applicability, criticality, verified recurrence, then freshness. Inspect overflow metadata so relevant critical risks are not silently hidden by a top-five cutoff. Raise a concise overflow notice and group compatible rules; fetch details only if needed.
- At capacity: merge duplicates, prune eligible terminal entries, retire entries disproved/obsolete after verification. Move unresolved critical overflow into an owned issue/task if it cannot fit. If capacity still cannot be respected safely, report the exception; never silently drop high-impact records or increase limits automatically.
- No rejected-event diary. A skipped capture returns a short disposition in the ordinary task output; it does not create a lesson about why no lesson was recorded.

Do not claim a strict total on-disk bound when unresolved/protected records prevent pruning. The enforceable bounds are admission and routine context, with explicit blocked-cleanup exceptions.

## 7. Minimal Record and Operations

Keep the existing per-skill Markdown location with a consistent compact YAML record. File metadata carries schema version and monotonic next_id so pruning never reuses IDs. No separate registry/database.

Required per-entry data: ID, severity plus admission reason, summary, evidence link(s), corrective rule, verification method, status, created_at, last_validated_at, expires_at. Optional only when relevant: occurrence count, applies_to, owner task/candidate, application revision/test receipt, retirement reason/replacement/risk-task link, terminal purge_after.

The helper should provide four small operations:

1. **capture:** validate admission evidence, deduplicate, enforce capacity, write one compact entry or return skipped/merged/blocked.
2. **select:** filter validity/applicability and bound summaries; return IDs and evidence. Read-only—no access log or expiry reset.
3. **settle:** record planned/applied/released/retired decisions with prerequisite evidence, scoped identity, and idempotency.
4. **prune:** preview expired/terminal changes and handoff/protection requirements; apply only authorized safe changes, preserving unrelated records.

Use atomic writes and file locking for concurrent updates; validate IDs/date/status, restrict writes to allowed lesson paths, and prevent lost updates with a revision check. A single bundled helper is sufficient initially. Keep qualitative admission decisions with the agent; the helper enforces schema and supplied decision evidence, not unsupported autonomous severity scoring.

Run maintenance when capturing/selecting for an approved skill update, not by spawning a periodic agent. Selection itself filters by time even without permission to mutate. Physical pruning requires the bounded maintenance permission and preservation checks; historical migration requires a reviewed dry-run first.

## 8. Skill-Level Change Plan

| Target | Change | Validation |
| --- | --- | --- |
| [Lesson skill](.github/skills/x-ipe-meta-lesson-learned/SKILL.md) | Admission gate; compact record; capture/select/settle/prune; dates/caps; critical handoff; avoid compulsory ground-truth interview or subagent for routine metadata. | Critical admission, ordinary skip, unknown ground truth routed to task, dedup, expiry, status evidence, maintenance authorization. |
| [Lesson examples](.github/skills/x-ipe-meta-lesson-learned/references/examples.md) | Replace diary-style examples with important failure, skipped trivial event, merged recurrence, applied safeguard, expiry/handoff, rollback/restart examples. | Examples execute against temporary records; expected dispositions match. |
| [Actual lesson template](x-ipe-docs/skill-meta/.templates/lesson-learned.md) | Compact versioned fields and status semantics; remove redundant summary counters. Package one canonical template with the skill and migrate existing template references. | Template resolves in clean installed project, not just this repo; parser round-trip and legacy migration. |
| [Creator](.github/skills/x-ipe-meta-skill-creator/SKILL.md) | Bounded select at planning; planned when adopted into candidate; applied only after verified publication; release/retire with reasons on failure/cancel; no read-all requirement. | Select→candidate→publish→settle, failed merge, restart, no irrelevant status changes. |
| [Production-patterns guide](.github/skills/x-ipe-meta-skill-creator/references/12.%20reference-production-patterns.md) | Relevant unexpired lesson lookup; explain reading versus applying; remove blanket consultation of full related histories. | Only current bounded records consumed; critical overflow surfaced. |
| [Project instructions](.github/copilot-instructions.md) and packaged EN/ZH/DAO variants | Invoke admission only for consequential reusable problems; one filename policy; no demand to record every feedback/mistake. | Variant parity and canonical/legacy discovery tests. |
| Existing per-skill lesson files | Reviewed migration only; dedup compact rules, verify already-fixed entries, assign real dates/expiry, establish next IDs, protect untracked/WIP. | Dry-run receipts; no age-only mass deletion; preserve linked risks and references. |

All live skill/resource changes must use the creator candidate→validation→publication process. The canonical template should move into the skill's candidate bundle during implementation; no direct live skill writes or implementation changes occur in this planning task.

## 9. Migration and Tests

### Integrate with the main refactoring phases

1. **P0:** inventory legacy formats/filenames/statuses and authoritative consumers. Review dates and actual corrective rules, not just severity labels. Existing applied/incorporated entries require checking the safeguard/evidence; reviewed does not imply applied.
2. **P1:** create the lesson-skill candidate and minimal helper/template/tests, then integrate creator select/settle. Keep a legacy reader during conversion. The 1,000-line ceiling is capacity; this skill should remain substantially shorter.
3. **P2:** align instruction variants and shared lifecycle maintenance permissions/ownership, avoiding duplicate tasks for every helper call.
4. **P4:** run approved migration/pruning in small batches with dry-run and recovery evidence. Old missing dates default to protected review-needed, not “fresh today” and not immediate deletion. Unknown status is not silently coerced to applied or expired.

### Acceptance scenarios

- One-off typo skipped; repeated harmless typo still does not qualify just by count.
- Verified critical permission violation captured; unsupported fix remains an incident task until ground truth exists.
- High-value blocking CLI contract captured once; recurrence merged without another entry.
- A rule already enforced by an effective test is not recorded again merely because the old narrative remains.
- Reading/selecting neither changes status nor refreshes expiry; adopting into a candidate marks planned with mapping.
- Successful verified publication marks applied with evidence; failed publication does not; replayed receipt is idempotent.
- Exact UTC expiry boundary; 90/180-day defaults; no sliding renewal from edits/reads; explicit revalidation can renew.
- Applied/retired summaries disappear from default retrieval immediately and are pruned only after grace/protection checks.
- Expired critical risk is handed off before purge; failed handoff blocks cleanup and remains visible as an exception.
- Eight pending entries: merge/retire/handoff behavior tested; no silent critical eviction.
- Top-five retrieval with relevant critical overflow notice; zero relevant lessons is valid.
- Multi-skill scoped IDs, monotonic IDs after pruning, shared-rule linkage, concurrent writes, malformed dates, and prohibited paths.
- Legacy raw/reviewed/incorporated/applied formats, missing dates, old filename fallback, installed-project template discovery, untracked/WIP protection.
- Pruning never removes production safeguards/tests, linked risks, task history, or unrelated changes.

## 10. Recommended Outcome

Treat lessons as temporary prompts to **improve a durable safeguard**. Once that safeguard is applied and verified, retire the reminder. Keep critical risk ownership outside expiring lesson memory when necessary.

This extension is ready to implement alongside creator modernization, not as a separate heavyweight knowledge-management subsystem. No new lesson was recorded merely for identifying this design gap; it is already represented by this approved-scope planning task.
