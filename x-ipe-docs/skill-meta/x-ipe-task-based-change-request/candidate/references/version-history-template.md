# Specification version history for approved CR deltas

Maintain ONE specification per actual feature, with its existing Version History.
Do not create versioned specification files or erase old rows; unchanged resume
adds no row/version. Preserve prior EN/ZH prose and stable reserved US/FR/AC IDs.
Minor approved additive delta may increment minor; structural redesign may
increment major. Versioning is justified by actual impact, not all CRs blindly minor.

```markdown
## Version History

| Version | Date | Description | Change Request |
| --- | --- | --- | --- |
| {approved new version} | {actual date} | {bounded actual delta} | {actual root-relative owning CR link} |
| {existing version} | {existing date} | {unchanged existing description} | {existing link or N/A} |
```

Both classification paths update any affected existing specification/history;
no-related-feature free-mode records N/A until authorized breakdown/refinement.
Never fabricate a new specification/feature ID or defer all CR records until a
recursive successor runs. Use current feature board specification_link then
unique EPIC/FEATURE or validated legacy folder; anchor retained for source lookup.

Major conflicting sections preserve original text under [RETIRED by CR-XXX]
with reason, date, source CR and replacement location/content. Maintain old-to-new
ID links; never reuse deleted IDs. Update affected requirement/design/goal/AC/type
context before implementation; invalidate affected evidence without erasing past
results or unrelated evidence. Approval precedes inline or retirement mutations.
