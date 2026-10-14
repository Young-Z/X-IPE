---
name: x-ipe-meta-lesson-learned
description: Maintain selective, time-bounded skill lessons with evidence-backed admission, adoption, application and safe cleanup. Use when a consequential reusable skill gap is verified or an explicit finite retention request is made. Triggers on requests like "capture lesson", "record issue", "this skill failed", "improve this skill". Ordinary mistakes are skipped; unresolved incidents go to owned tasks.
---

# Lesson Learned

## Purpose

Maintain a small temporary skill-improvement queue by:
1. Admitting only consequential, reusable, verified corrections.
2. Selecting relevant summaries without refreshing their lifetime.
3. Distinguishing candidate adoption from verified production application.
4. Forgetting reminders safely once durable safeguards or risk owners exist.

## About

This meta skill operates on other skills' improvement records, not a general
incident diary. Durable instructions and tests supersede temporary reminders.
No database, global registry, growing archive, scheduled agent or access log.

### Key Concepts

- **Ground truth:** verified correct behavior, never a fabricated proposed fix.
- **Identity:** `(primary skill, LL-NNN)`; IDs are not global.
- **Admission:** agent-supplied qualitative reason, gap and supporting evidence.
- **Application:** published safeguard plus relevant passing production tests.
- **Handoff:** an existing open task with actual owner and scoped lesson backlink.

### Scope

```yaml
operates_on:
  - per-skill Markdown lesson queues
  - bounded selection and evidence-backed lifecycle decisions
does_not_handle:
  - editing or publishing skills (use x-ipe-meta-skill-creator)
  - creating tasks, incidents or external issues inside the helper
  - historical migration, Git operations, memory copies or periodic maintenance
```

## Important Notes

BLOCKING: Unknown ground truth is an incident/task handoff, not a lesson.
Never invent the corrective rule or validation evidence to complete a schema.

CRITICAL: Severity alone does not admit a major lesson. Require verified
recurrence or a systemic contract gap likely to block ordinary future work.
Skip cosmetic/harmless one-offs, speculative enhancements and local fixed bugs
without a reusable skill gap. Repeated harmless typos still do not qualify.

MANDATORY: Check existing authoritative rules/tests and equivalent lessons.
If a known rule was violated, identify enforcement/cause rather than duplicate
the warning. Respect explicit no-retention requests without a rejected diary.

BLOCKING: Writes use explicit roots and expected SHA256 revision under a
cooperative lock. Physical purge requires explicit apply and preservation.
Do not bypass protected legacy, undated, unknown-status or WIP records.

MANDATORY: Creator select/settle calls and packaged instruction alignment are
separate consumer-integration work. Installing this helper does not establish
automatic adoption/application; lifecycle owners invoke it explicitly until
that integration is verified. Historical lesson conversion is not included.

## Input Parameters

```yaml
input:
  operation: capture | select | settle | prune
  project_root: "absolute approved project, including temporary test projects"
  skill_name: "existing primary owner skill; select can consult multiple owners"
  task_id: "existing lifecycle task; do not create duplicate operation tasks"
  proposal: "agent-evaluated admission, evidence and reusable correction"
  expected_revision: "SHA256 from load or prune preview, required for writes"
  now: "optional explicit UTC instant for deterministic tests"
  decision: "owned plan/application/release/retirement evidence"
  apply: false
  preservation: "revision-bound explicit user approval for physical purge"
  process_preference:
    interaction_mode: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="existing task intent; capture is not automatic for every issue" />
  <field name="project_root">
    <steps>Resolve the approved root; reject traversal, symlinks, hard links and special nodes.</steps>
  </field>
  <field name="skill_name">
    <steps>Verify target skill exists. Resolve canonical per-skill file, accepting legacy lesson-learned.md only when canonical is absent. Ambiguous dual files block.</steps>
  </field>
  <field name="proposal">
    <steps>Obtain observed evidence/correction, reusable gap, coverage check, cause, corrective rule, verification and qualitative reason. Unknown truth routes to incident ownership.</steps>
  </field>
  <field name="expected_revision">
    <steps>Read load snapshot or maintenance preview; reread on conflict, never retry blindly with a new revision.</steps>
  </field>
  <field name="decision">
    <steps>Resolve real owner/candidate mappings or existing publication/test artifacts, not arbitrary success strings.</steps>
  </field>
  <field name="preservation">
    <steps>Resolve explicit user approval tied to the exact file revision; otherwise retain untracked/WIP records.</steps>
  </field>
  <field name="process_preference" source="lifecycle policy; route only genuinely unresolved questions" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Scope known</name><verification>Existing task, operation, allowed root and owner skills are explicit.</verification></checkpoint>
  <checkpoint required="true"><name>Evidence honest</name><verification>Admission or settlement facts are supplied; unknown truth is stated.</verification></checkpoint>
  <checkpoint required="true"><name>Mutation authorized</name><verification>Expected revision and maintenance/preservation permission are known when needed.</verification></checkpoint>
  <checkpoint required="true"><name>Resources loaded</name><verification>Bundled schema and API reference are available; legacy is read-only.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Action | Gate |
|------|--------|------|
| 1 | Evaluate admission or lifecycle evidence | Reusable verified correction or honest blocked disposition |
| 2 | Resolve compact queue and relevant summaries | Protected records not treated as fresh/expired |
| 3 | Execute the authorized operation | Revision, ownership, receipts and preservation enforced |
| 4 | Return bounded disposition | Exact evidence and exceptions; no false application |

## Execution Procedure

```xml
<procedure name="x-ipe-meta-lesson-learned">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Evaluate Intent and Evidence</name>
    <action>
      1. IF ordinary/no reusable gap/already covered/no-retention THEN skip without persisting a rejection log.
      2. IF correct behavior is unknown THEN route incident to an existing owned task; report handoff required until an owner exists.
      3. Admit critical failures only with explicit impact (loss/corruption, confidentiality/security/authorization, destructive action or invalid accepted success).
      4. Admit high-value major only with verified-recurrence or systemic-contract-gap basis and supporting evidence.
      5. IF user explicitly requests retention THEN record exact request, purpose and finite TTL (1-180 days); preserve honest severity.
    </action>
    <output>Admission decision or short skipped/incident disposition</output>
  </step_1>
  <step_2>
    <name>Resolve Queue and Select</name>
    <action>
      1. Load the per-skill snapshot; unknown schema/status/dates and old prose remain protected for reviewed migration.
      2. Select unexpired active/planned records by applicability, criticality, recurrence and freshness; zero relevant entries is valid.
      3. Return at most five summaries across owners within approximately 120 lines; surface relevant critical overflow identities.
      4. Reads, selections and prose edits do not change status, timestamps or expiry; no access log.
      5. Surface critical review due at 90 days, expired critical cleanup identities and planned owner-progress review after 14 days; never steal ownership or automatically renew.
    </action>
    <output>Bounded summaries, scoped IDs, revision and protected/overflow notices</output>
  </step_2>
  <step_3>
    <name>Execute Authorized Operation</name>
    <action>
      1. Use the bundled helper APIs/CLI with explicit project root. One primary owner stores shared rules; applicability links consumers.
      2. Capture deduplicates normalized cause plus corrective rule; retain at most two evidence links. A verified new occurrence with distinct evidence can refresh validity and increment occurrence count.
      3. Without new evidence, a duplicate is unchanged. Applied regression reopens the retained identity after confirming the cause; retired re-admission blocks for review.
      4. Enforce eight pending active/planned entries, including stale pending cleanup. At capacity consolidate or approved maintenance; unresolved critical overflow goes to owned tasks, never silent eviction.
      5. Set planned only when a real open task owns an existing named candidate and concrete lesson-to-change/test mapping. Planning never pauses expiry.
      6. Set applied only after matching planned ownership, verified publication manifest/byte parity and a scoped passing production test receipt. Replay identical owned receipt is unchanged even after later production updates; it does not reapply or reset the terminal clock.
      7. Failed publication leaves planned or explicitly releases to valid active with owner task and reason. Release preserves original expiry; expired content needs evidence-backed revalidation.
      8. Retirement excludes immediately and records reason. Conservative helper requires verified critical handoff even for explicit rejection/supersession; record replacement in reason.
      9. Prune previews only by default. Expired pending records retire with 30-day grace. Unresolved critical cleanup needs existing-schema open owned task plus scoped backlink; failed handoff retains the excluded record.
      10. Apply physical purge only after grace, fresh revision and explicit revision-bound preservation approval. Never remove unrelated files, safeguards, linked tasks or history.
    </action>
    <output>Operation receipt with actions, revision, protected records and blocked cleanup</output>
  </step_3>
  <step_4>
    <name>Verify and Report</name>
    <action>
      1. Validate changed queue and bounded output; surface every protected exception rather than claiming a strict disk bound.
      2. Critical active/planned TTL is 180 days, review due 90; major TTL 90. UTC expiry is now greater than or equal to expires_at.
      3. Applied/retired disappear from normal selection immediately; retain compact receipt/reason 30 days, then approved purge.
      4. Keep old undated/unknown status records neither fresh today nor automatically expired. No migration or global database in this operation.
      5. Return honest result to lifecycle owner; no board/Git/memory changes from helper. Meaningful policy changes require independent review through creator.
    </action>
    <output>Exact disposition and unresolved issues</output>
  </step_4>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill: null
  process_preference:
    interaction_mode: "resolved lifecycle mode"
  require_human_review: "yes for policy changes or unresolved permission"
  task_output_links: ["per-skill Markdown or existing incident task"]
  disposition: captured | merged | duplicate | skipped | incident_handoff_required | planned | applied | active | retired | unchanged | dry_run | blocked
  lesson_identity: "primary skill + LL-NNN when present"
  revision: "SHA256 snapshot when available"
  unresolved_issues: []
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Admission justified</name><verification>Qualitative gap, truth and evidence supplied; ordinary events skipped.</verification></checkpoint>
  <checkpoint required="true"><name>Bounded records</name><verification>Scoped monotonic IDs, two evidence links, eight pending limit and explicit dates.</verification></checkpoint>
  <checkpoint required="true"><name>Selection read-only</name><verification>Five summaries, expiry filter and critical overflow; no timestamp refresh.</verification></checkpoint>
  <checkpoint required="true"><name>Lifecycle truthful</name><verification>Ownership and publication/test receipts gate changes; replay does not reset retention.</verification></checkpoint>
  <checkpoint required="true"><name>Cleanup safe</name><verification>Dry-run first, critical handoff, grace and preservation; exceptions remain visible.</verification></checkpoint>
  <checkpoint required="true"><name>Evidence exact</name><verification>Operation result reports revisions and gaps without invented ground truth or migration.</verification></checkpoint>
</definition_of_done>
```

## Templates

- [Canonical queue template](.github/skills/x-ipe-meta-lesson-learned/templates/lesson-learned.md)
- [API and schema](.github/skills/x-ipe-meta-lesson-learned/references/lifecycle.md)
- [Helper](.github/skills/x-ipe-meta-lesson-learned/scripts/lesson_ops.py)

## Examples

See [examples](.github/skills/x-ipe-meta-lesson-learned/references/examples.md).
