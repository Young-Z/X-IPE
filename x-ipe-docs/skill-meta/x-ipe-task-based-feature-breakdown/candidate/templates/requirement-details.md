# Requirement Summary — Feature Breakdown

> Requirement ID: {existing REQ-XXX or N/A; do not fabricate}  
> Epic context: {actual intake/existing EPIC IDs}  
> Created / Updated: {actual dates}

## Overview and Scoped Delta

{Reuse what/who/why, acceptance, in/out scope and authorized new/small/CR findings}

## Epic Assessment and Delivery Order

{Grouping rationale: domains, estimated feature count, dependency/team boundaries;
reuse intake Epic; additional authorized groups link to original intake}
{Runnable MVP per new Epic, ordered enhancements, approved deferrals with reasons}

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
| --- | --- | --- | --- | --- | --- |
| FEATURE-{nnn}-A | EPIC-{nnn} | {Runnable MVP} | v1.0 | {<=50 words} | {None or direct FEATURE IDs} |

## Feature Details

### {FEATURE-ID}: {Feature Title}

**Version:** {actual vX.Y}  
**Brief Description:** {<=50 words}  
**Scope / MVP:** {runnable value, in/out boundary and approved deferred scope}

**Goal / Subgoal Contribution:** {stakeholder observable outcome; parent stable requirement/source ID; credible enabling chain, not just artifact name}

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {stable US/FR ID or optional doc-local G} | {parent requirement ID and intent anchor; inferred label for legacy so-that} | {beneficiary} | {observable change} | {feature deliverable enables parent; all-required or selected bounded alternative} | {known measure or qualitative scenario; planned/actual distinction} | {limits} | {stable GWT AC IDs} | {not measured or actual observed stakeholder outcome} |

**Acceptance Criteria:**

- [ ] {Stable AC ID: GIVEN context WHEN event THEN observable result; mapped to source FR/goal; aim 3-7 without padding, never >20}

**Dependencies:**

- {Direct FEATURE-ID}: {reason; cross-Epic and legacy IDs preserved}
- {None if actually no dependency}
- {All-required selected prerequisites versus bounded alternatives and rationale; non-selected alternatives are not board edges or compulsory features}

**Technical Considerations:**

- {Constraint/integration/performance/security hints for later design}

**Mockup Links:**

- {Actual project-root-relative Markdown link or N/A; shared Epic mockups}

## Coverage and Split Decisions

| Source Requirement / Parent FR / AC | Covered By | Decision / Gap |
| --- | --- | --- |
| {actual stable source ID} | {Feature/child AC} | {covered or approved deferral} |

{For genuine split: partial parent retained with gaps; full authorized retirement
preserves history/redirects and verifies Retired board record before active removal}

## Context and Integration Evidence

{Source/parts/index/config/board/workflow SHA256 revisions, reused/refreshed facts,
actual feature create/query/update results, preserved existing status/spec/stages}
{Goal-to-AC validation plan and separate engineering delivery/outcome state; unknown
stakeholder observation remains not measured; CR invalidates affected evidence only}
{features-list = actual populated file; breakdown-folder = scalar containing folder;
actual action write/readback or truthful free-mode/blocked result; known limitations}

## Notes

Keep all feature details consolidated here; do not create individual feature.md or
specification files during breakdown. Specifications are refined downstream.
Status source of truth is x-ipe-docs/planning/features/features.json through the
board manager. Generated links are project-root-relative. Preserve EN/ZH prose,
all stable IDs and unrelated sections on CR. Parts index has overview only.
