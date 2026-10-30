# Deterministic Validation and Safe Publication

Reusable validator/publisher contracts. Applicable foundation and real-template
tests supply evidence outside the bundle in skill metadata; no execution count or
release authorization is embedded here. A passing receipt is not permission.

Resolve helpers through `.github/skills/x-ipe-meta-skill-creator/scripts/` after
promotion, even when the target is another skill. A reviewed creator candidate
override is permitted only during an explicitly recorded bootstrap.

## APIs

The scripts accept explicit project roots and work in temporary test projects;
they do not read or mutate task boards, lessons, memory, or Git state.
PyYAML (already an X-IPE dependency) parses frontmatter; remaining imports are
standard library. Load scripts with their scripts directory on the import path.

### Validator

`validate(project_root, candidate, name, skill_type) -> dict` returns `ok`,
`errors`, `warnings`, `body_lines`, `files` (relative path → SHA256), and
`candidate_hash` (SHA256 of sorted compact JSON file map).
Paths are absolute; candidate must equal the same-named canonical
`x-ipe-docs/skill-meta/{name}/candidate` under the given project.

CLI flags: `--project-root`, `--candidate`, `--name`, `--type` (all required).
Output is one JSON receipt on stdout. Success exits 0, validation failures 1,
argument errors 2. No files are written, including receipt files.

Checks:
- Frontmatter mapping, nonempty description (≤1024 characters), name/subtype/folder identity.
- Exact existing `x-ipe-assistant-user-representative-Engineer` identity is accepted
  only as x-ipe-assistant; arbitrary uppercase names and wrong subtypes still fail.
- Logical SKILL.md body lines ≤1000, excluding both YAML delimiters and header;
  blank body lines included, LF/CRLF equivalent, final newline adds no phantom line.
- Purpose, Input Parameters/Initialization, DoR, procedure or operations, Output,
  DoD in contract order; corresponding blocks; DoR ≤5 and DoD ≤10 checkpoints.
- Task-based routing fields only for task-based skills; tools/knowledge retain
  Operations + `<operation>` and their own Output Result, not task outputs.
- Exact legacy category `x-ipe+feature+quality-board-management` validates with
  `--type x-ipe-task-category` and its existing Operations + `<operation>` contract.
  Its original `operation_output` is retained, not replaced by workflow output.
  This name is not accepted as a tool or any other subtype. Other category names,
  including lookalike suffixes and categories, still require Execution Procedure
  + `<procedure>`. Every remaining identity/path/resource/line/checkpoint check
  is unchanged. No process-local TYPES patch is supported or needed.
- Local inline/image/reference-style Markdown targets in every bundled Markdown
  file; URI-decoding, optional anchors, self production references mapped to
  candidate; root-relative external links checked against the actual project.
- Existing file-relative resource links supported; template placeholders produce
  warnings until instantiated. External HTTP/HTTPS/mailto are not fetched.
- All physical files, including hidden files, are checked for links, traversal,
  hard links and special nodes. No cache or resource ignore rules. The explicit
  creator-only excluded root `metadata` allows exactly `review-findings.md` and
  `test-cases.yaml`, cleanup remnants of review metadata; unknown files there fail.
  Receipts disclose their hashes as `excluded_files`; publishable `files` and
  `candidate_hash` omit them. Keep authoritative review records outside candidate.
  This exception never filters production inventories, backups or staged trees.

`tree_bytes(folder, root)` inventories all physical files without exclusion.
`candidate_bytes(folder, root, name)` returns only publishable candidate bytes
with the explicit cleanup boundary above. `manifest(byte_map)`,
`fingerprint(hash_map)` and `parse_skill(data)` are pure/read-only helpers.

## Publication

`publish(project_root, candidate, name, skill_type, baseline, managed,
expected_candidate_hash, reviewed_deletions=(), apply=False, hook=None) -> dict`.

CLI flags: validator identity/path flags plus `--baseline`, `--managed`,
`--candidate-hash`; repeat `--delete-reviewed` for each reviewed removed path.
The two manifest arguments are paths to JSON path→SHA256 maps, not entire
validator receipts. Use `--apply` only after authorization and review.
Without it the script does not create locks, staging, parents, or production files.

There is deliberately no arbitrary destination parameter: publication targets
only `.github/skills/{name}` under the validated root. Wrong-name candidate roots
and link/escaping targets fail. New skills use `{}` baseline and managed maps.

### Ownership and Freshness

Baseline is the full target snapshot from before task edits. Managed is a trusted
prior successful publication inventory or reviewed clean tracked source inventory.
Baseline equality is concurrency evidence, not ownership. Never fabricate managed
ownership by copying all current target hashes: that would hide dirty/unmanaged work.
The first migration must review this provenance and initial tracked candidate deltas.

- Exact baseline hashes must still match production.
- Exact candidate fingerprint must still match validation/review evidence.
- Dirty/unmanaged files may remain only with identical bytes; changes/removal fail.
- Managed files already deleted before work cannot be silently restored.
- Removed files must match the exact reviewed deletion list and trusted managed hashes.
- Dry-run includes added/changed/removed/protected lists and complete proposed file hashes.
- Same bytes may be retained without changing ownership; a receipt alone does not
  authorize a later publisher to adopt previously unmanaged work.

Permission, proportional review, lesson validity, and workflow/config semantics
remain agent decisions. Independent review is required only for the concrete
triggers in the [authoring policy](.github/skills/x-ipe-meta-skill-creator/references/single-loop-authoring.md),
not every executable, workflow, or public-contract edit.
The script enforces filesystem/manifests, not those
human decisions; a deterministic pass is never an automatic release approval.

### Transaction and Recovery

Application takes an exclusive per-name cooperative lock under
`.github/.skill-publication/`, then creates a transaction there (outside production).
It stages every candidate file, checks actual staged bytes, rechecks target and
candidate, journals the swap, renames old production to retained backup, installs
staged production, and compares all resulting bytes to candidate. It does not
recursively delete production or merge arbitrary trees. File permission bits are
copied to staging, but manifest/parity contracts concern file content bytes.

Ordinary exceptions and injected faults attempt rollback. Unexpected concurrent
target or backup edits block rollback rather than discarding them. Keep journal,
lock, and backup for inspection when recovery cannot complete. Backups and failed
trees are intentionally retained; cleanup requires a separately reviewed action.

`recover(project_root, name, transaction, apply=False) -> dict` inspects only a
same-named transaction under canonical staging. CLI recovery uses `--project-root`,
`--name`, `--recover` and optional `--apply`. Confirm the previous publisher is
stopped first; never steal an active lock. Applying recovery requires the matching
retained lock. Published/rolled-back receipts can be replayed without changing
production; a leftover matching lock after terminal journaling can be released.

Recovery validates recorded identity and baseline/proposed maps; it restores
only matching baseline backups, preserves installed content in a failed tree,
and verifies restored hashes/existence. It refuses unexpected bytes. A hard
process termination may leave production temporarily absent between the two
renames; this is recoverable publication, not a seamless live-directory exchange.
Power-loss durability and hostile writers require separately scoped evidence;
cooperative locks cannot eliminate races from tools that ignore the lock.

### Fault/Test Hook

`hook(event)` receives `staged`, `backed_up`, `installed`. Tests may raise,
interrupt, or modify a temporary target at these boundaries. No production tests.
Test baseline/new-skill, small delta, missing resource, 1000/1001 and newline
variants, invalid paths, unmanaged/deleted-file protection, exact removals,
candidate/target concurrency, exception rollback, journal recovery/replay,
retained backup safety, and CLI JSON/nonzero errors before promotion.

## Limits and Review Focus

Markdown resource scanning is a deliberately bounded parser, not a full CommonMark
engine. Nested-parenthesis targets and unusual reference syntax need test fixtures
or a documented supported-link convention. Anchors are optional and not checked.
Semantic schema compatibility, discovery quality, code behavior, workflow actions,
and config consumers require applicable scenario evidence; independent review
is conditional on concrete risk, explicit user review, or unresolved ambiguity/failures.
Empty directories are not file-manifest entries; do not store meaningful unmanaged
state solely in empty directories. No blanket application compatibility is claimed.