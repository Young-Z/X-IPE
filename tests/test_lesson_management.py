"""TASK-6749 candidate lifecycle tests. All queues/tasks/receipts use tmp_path."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
CANDIDATE = REPO / "x-ipe-docs/skill-meta/x-ipe-meta-lesson-learned/candidate"
SCRIPT = CANDIDATE / "scripts/lesson_ops.py"
spec = importlib.util.spec_from_file_location("candidate_lesson_ops", SCRIPT)
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)
SKILL = "x-ipe-tool-example"
NOW = "2026-01-01T00:00:00Z"
EXPIRES = "2026-04-01T00:00:00Z"


@pytest.fixture
def root(tmp_path):
    (tmp_path / ".github/skills" / SKILL).mkdir(parents=True)
    (tmp_path / ".github/skills" / SKILL / "SKILL.md").write_text("safeguard\n")
    (tmp_path / "x-ipe-docs/skill-meta" / SKILL / "candidate").mkdir(parents=True)
    return tmp_path


def proposal(n=0, critical=False):
    admission = {"kind": "critical" if critical else "high_value", "reason": "Reusable verified failure",
                 "reusable_gap": "Missing contract guard", "coverage_check": "No existing effective test",
                 "ground_truth": "Verified rejection before mutation"}
    admission.update({"impact": "Unapproved destructive action"} if critical else
                     {"basis": "systemic_contract_gap", "basis_evidence": "Ordinary CLI path blocked in test"})
    return {"severity": "critical" if critical else "major", "summary": f"Guard contract {n}",
            "cause": f"Missing precondition {n}", "corrective_rule": f"Reject before changing state {n}",
            "verification": "test_permission_guard", "evidence": [f"tests/failure-{n}.md"], "admission": admission}


def revision(root):
    return ops.load(root, SKILL)["revision"]


def capture(root, p=None, now=NOW, **kwargs):
    return ops.capture(root, SKILL, p or proposal(), now=now, expected_revision=revision(root), **kwargs)


def records(root):
    return ops.load(root, SKILL)["document"]["records"]


def task(root, lesson_id="LL-001", **changes):
    path = "x-ipe-docs/planning/tasks/tasks-2026-01-01.json"
    obj = {"task_id": "TASK-1", "task_type": "skill update", "description": "Own risk and correction",
           "role": "Quill", "status": "in_progress", "created_at": NOW, "last_updated": NOW,
           "output_links": [f"x-ipe-docs/skill-meta/{SKILL}/{ops.CANONICAL}#{lesson_id}"], "next_task": ""}
    obj.update(changes)
    write_json(root, path, {"_version": "1.0", "tasks": [obj]})
    return {"path": path, "task_id": "TASK-1", "owner": "Quill"}


def write_json(root, path, value):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value))


def settle(root, decision, now=NOW):
    return ops.settle(root, SKILL, "LL-001", decision, expected_revision=revision(root), now=now)


def plan(root):
    return settle(root, {"status": "planned", "owner": task(root),
                        "candidate": f"x-ipe-docs/skill-meta/{SKILL}/candidate",
                        "change": "Add precondition guard", "test": "test_permission_guard"})


def receipts(root):
    files = {"SKILL.md": ops.digest((root / ".github/skills" / SKILL / "SKILL.md").read_bytes())}
    fingerprint = ops.digest(json.dumps(files, sort_keys=True, separators=(",", ":")).encode())
    write_json(root, "evidence/publication.json", {"ok": True, "operation": "publish", "state": "published",
               "byte_parity": True, "name": SKILL, "files": files, "candidate_hash": fingerprint})
    write_json(root, "evidence/test.json", {"ok": True, "tests_passed": True, "skill_name": SKILL,
               "production_revision": fingerprint, "candidate_hash": fingerprint,
               "lesson_ids": ["LL-001"], "verification": "test_permission_guard"})
    return {"status": "applied", "task": "TASK-1", "production_revision": fingerprint,
            "publication_receipt": "evidence/publication.json", "test_receipt": "evidence/test.json"}


def approve(root):
    return {"kind": "explicit_user_approval", "revision": revision(root),
            "authorized_by": "User", "reason": "Approved removal of this exact temporary queue"}


def cli(root, operation, data=None, *flags):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run([sys.executable, "-B", str(SCRIPT), operation, "--project-root", str(root),
                             "--skill", SKILL, "--now", NOW, "--input", json.dumps(data or {}), *flags],
                            capture_output=True, text=True, env=env)
    return result.returncode, json.loads(result.stdout)


@pytest.mark.parametrize("critical,days,expiry", [(False, 90, EXPIRES), (True, 180, "2026-06-30T00:00:00Z")])
def test_admission_dates_and_roundtrip(root, critical, days, expiry):
    result = capture(root, proposal(critical=critical))
    assert result["disposition"] == "captured"
    entry = records(root)[0]
    assert entry["expires_at"] == expiry
    assert entry["status"] == "active" and entry["occurrences"] == 1
    assert ops.render(ops.load(root, SKILL)["document"]) == Path(ops.load(root, SKILL)["path"]).read_bytes()
    if critical:
        assert entry["review_due"] == EXPIRES


@pytest.mark.parametrize("field", ["retain", "covered"])
def test_skip_no_file_or_log(root, field):
    p = proposal()
    p[field] = field == "covered"
    assert capture(root, p)["disposition"] == "skipped"
    assert not Path(ops.load(root, SKILL)["path"]).exists()


def test_unknown_truth_incident_not_invented(root):
    p = proposal(critical=True)
    del p["admission"]["ground_truth"]
    assert capture(root, p)["disposition"] == "incident_handoff_required"
    assert not Path(ops.load(root, SKILL)["path"]).exists()


@pytest.mark.parametrize("field", ["reason", "reusable_gap", "coverage_check", "basis_evidence", "basis"])
def test_major_requires_qualitative_decision(root, field):
    p = proposal()
    del p["admission"][field]
    with pytest.raises(ValueError):
        capture(root, p)


@pytest.mark.parametrize("severity", ["minor", "enhancement"])
def test_harmless_recurrence_not_major_admission(root, severity):
    p = proposal()
    p["severity"] = severity
    p["admission"]["basis"] = "verified_recurrence"
    with pytest.raises(ValueError):
        capture(root, p, recurrence=True)


@pytest.mark.parametrize("days", [0, -1, 181, "14", True, None])
def test_override_finite_required(root, days):
    p = proposal()
    p["severity"] = "minor"
    p["admission"].update(kind="user_override", explicit_request="Please retain this", purpose="temporary review", ttl_days=days)
    with pytest.raises(ValueError):
        capture(root, p)


def test_override_preserves_severity(root):
    p = proposal()
    p["severity"] = "minor"
    p["admission"].update(kind="user_override", explicit_request="Retain for 14 days", purpose="time bounded preference", ttl_days=14)
    capture(root, p)
    assert records(root)[0]["severity"] == "minor"
    assert records(root)[0]["expires_at"] == "2026-01-15T00:00:00Z"


@pytest.mark.parametrize("evidence", [[], ["a", "b", "c"], ["a", "a"], ["x" * 501]])
def test_evidence_bound(root, evidence):
    p = proposal()
    p["evidence"] = evidence
    with pytest.raises(ValueError):
        capture(root, p)


def test_dedup_reads_and_no_new_evidence_do_not_refresh(root):
    capture(root)
    before = revision(root)
    assert capture(root, now="2026-02-01T00:00:00Z", recurrence=True)["disposition"] == "duplicate"
    p = proposal()
    p["evidence"] = ["tests/new.md"]
    assert capture(root, p)["disposition"] == "duplicate"
    assert ops.select(root, [SKILL], now=NOW)["summaries"]
    assert revision(root) == before


def test_recurring_evidence_bounded_and_refresh_explicit(root):
    capture(root)
    for i in range(3):
        p = proposal()
        p["evidence"] = [f"tests/new-{i}.md"]
        assert capture(root, p, now="2026-02-01T00:00:00Z", recurrence=True)["disposition"] == "merged"
    entry = records(root)[0]
    assert entry["id"] == "LL-001" and entry["occurrences"] == 4
    assert entry["evidence"] == ["tests/new-1.md", "tests/new-2.md"]
    assert entry["expires_at"] == "2026-05-02T00:00:00Z"


@pytest.mark.parametrize("now,selected", [("2026-03-31T23:59:59Z", True), (EXPIRES, False), ("2026-04-01T00:00:01Z", False)])
def test_exact_expiry_read_only(root, now, selected):
    capture(root)
    before = revision(root)
    assert bool(ops.select(root, [SKILL], now=now)["summaries"]) is selected
    assert revision(root) == before


def test_pending_cap_counts_stale_and_no_eviction(root):
    for i in range(8):
        capture(root, proposal(i))
    assert capture(root, proposal(9, critical=True), now=EXPIRES)["disposition"] == "blocked"
    assert len(records(root)) == 8
    p = proposal(0)
    p["evidence"] = ["tests/new.md"]
    assert capture(root, p, recurrence=True)["disposition"] == "merged"


def test_five_budget_overflow_and_applicability(root):
    for i in range(8):
        p = proposal(i, critical=True)
        p["applies_to"] = ["x-ipe-tool-consumer"]
        capture(root, p)
    result = ops.select(root, [SKILL, SKILL], relevant_to="x-ipe-tool-consumer", now=EXPIRES)
    assert len(result["summaries"]) == 5 and len(result["critical_overflow"]) == 3
    assert len(result["notices"]) == 8
    assert len(json.dumps(result["summaries"], indent=2).splitlines()) <= 120
    assert not ops.select(root, [SKILL], relevant_to="x-ipe-tool-other", now=NOW)["summaries"]


def test_scoped_ids_across_owners(root):
    other = "x-ipe-tool-other"
    (root / ".github/skills" / other).mkdir()
    capture(root)
    ops.capture(root, other, proposal(), expected_revision=ops.load(root, other)["revision"], now=NOW)
    result = ops.select(root, [SKILL, other], now=NOW)["summaries"]
    assert {r["id"] for r in result} == {"LL-001"}
    assert {r["skill"] for r in result} == {SKILL, other}


def test_planned_mapping_release_and_no_sliding_ttl(root):
    capture(root)
    plan(root)
    entry = records(root)[0]
    assert entry["plan"]["task"] == "TASK-1" and entry["expires_at"] == EXPIRES
    result = ops.select(root, [SKILL], now="2026-01-15T00:00:00Z")
    assert "owner progress" in result["notices"][0]["reason"]
    with pytest.raises(ValueError):
        settle(root, {"status": "active", "task": "TASK-2", "reason": "failed publish"})
    settle(root, {"status": "active", "task": "TASK-1", "reason": "failed publish"})
    assert records(root)[0]["expires_at"] == EXPIRES


@pytest.mark.parametrize("change", [{"role": "unassigned"}, {"status": "completed"}, {"output_links": "bad"}])
def test_plan_owned_task_schema_gate(root, change):
    capture(root)
    owner = task(root, **change)
    with pytest.raises(ValueError):
        settle(root, {"status": "planned", "owner": owner,
                      "candidate": f"x-ipe-docs/skill-meta/{SKILL}/candidate", "change": "guard", "test": "test"})
    assert records(root)[0]["status"] == "active"


def test_plan_unknown_task_and_candidate_block(root):
    capture(root)
    owner = task(root)
    owner["task_id"] = "TASK-unknown"
    with pytest.raises(ValueError):
        settle(root, {"status": "planned", "owner": owner, "candidate": "anything", "change": "guard", "test": "test"})


def test_application_and_replay_idempotent(root):
    capture(root)
    plan(root)
    decision = receipts(root)
    settle(root, decision)
    entry, before = deepcopy(records(root)[0]), revision(root)
    assert entry["purge_after"] == "2026-01-31T00:00:00Z"
    assert not ops.select(root, [SKILL], now=NOW)["summaries"]
    assert settle(root, decision, now="2026-01-10T00:00:00Z")["disposition"] == "unchanged"
    assert revision(root) == before and records(root)[0] == entry


@pytest.mark.parametrize("target,field,value", [("publication", "state", "dry_run"), ("publication", "byte_parity", False),
                                               ("test", "tests_passed", False), ("test", "lesson_ids", []),
                                               ("test", "verification", "unrelated"), ("test", "production_revision", "fake")])
def test_application_receipt_boundaries(root, target, field, value):
    capture(root)
    plan(root)
    decision = receipts(root)
    path = root / f"evidence/{target}.json"
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data))
    before = revision(root)
    with pytest.raises(ValueError):
        settle(root, decision)
    assert revision(root) == before and records(root)[0]["status"] == "planned"


@pytest.mark.parametrize("change", ["changed", "extra"])
def test_application_complete_bytes_not_arbitrary_receipt(root, change):
    capture(root)
    plan(root)
    decision = receipts(root)
    (root / ".github/skills" / SKILL / ("SKILL.md" if change == "changed" else "extra.md")).write_text("unexpected")
    with pytest.raises(ValueError):
        settle(root, decision)


def test_no_plan_no_apply_and_expiry_blocks_settlement(root):
    capture(root)
    decision = receipts(root)
    with pytest.raises(ValueError):
        settle(root, decision)
    plan(root)
    with pytest.raises(ValueError):
        settle(root, decision, now=EXPIRES)
    with pytest.raises(ValueError):
        settle(root, {"status": "active", "task": "TASK-1", "reason": "cancel"}, now=EXPIRES)


def test_applied_regression_reopens_identity(root):
    capture(root)
    plan(root)
    settle(root, receipts(root))
    p = proposal()
    p["evidence"] = ["tests/regression.md"]
    capture(root, p, recurrence=True, now="2026-01-02T00:00:00Z")
    assert records(root)[0]["status"] == "active" and records(root)[0]["id"] == "LL-001"
    assert "purge_after" not in records(root)[0]


def test_prune_dry_run_no_write_even_missing(root):
    before = set(root.rglob("*"))
    assert ops.prune(root, SKILL, now=NOW)["disposition"] == "dry_run"
    assert set(root.rglob("*")) == before
    capture(root)
    before = revision(root)
    preview = ops.prune(root, SKILL, now=EXPIRES)
    assert preview["actions"] == [{"id": "LL-001", "action": "retire"}]
    assert revision(root) == before


def test_retire_grace_purge_protection_and_monotonic_id(root):
    capture(root)
    settle(root, {"status": "retired", "reason": "superseded by verified test"})
    assert not ops.select(root, [SKILL], now=NOW)["summaries"]
    assert not ops.prune(root, SKILL, now="2026-01-30T23:59:59Z", preservation=approve(root))["actions"]
    result = ops.prune(root, SKILL, now="2026-01-31T00:00:00Z", apply=True, expected_revision=revision(root))
    assert result["blocked"] and len(records(root)) == 1
    result = ops.prune(root, SKILL, now="2026-01-31T00:00:00Z", apply=True,
                       expected_revision=revision(root), preservation=approve(root))
    assert result["actions"] == [{"id": "LL-001", "action": "purge"}]
    assert capture(root, proposal(2))["id"] == "LL-002"


def test_prune_cannot_bypass_untracked_with_boolean_or_stale_approval(root):
    capture(root)
    settle(root, {"status": "retired", "reason": "obsolete"})
    for preservation in ({"tracked": True}, {**approve(root), "revision": "0" * 64}):
        assert ops.prune(root, SKILL, now="2026-02-01T00:00:00Z", preservation=preservation)["blocked"]


@pytest.mark.parametrize("bad", [None, "TASK-1", {"path": "arbitrary", "task_id": "TASK-1", "owner": "Quill"}])
def test_expired_critical_handoff_not_arbitrary(root, bad):
    capture(root, proposal(critical=True))
    result = ops.prune(root, SKILL, now="2026-06-30T00:00:00Z", apply=True,
                       expected_revision=revision(root), handoffs={"LL-001": bad})
    assert result["blocked"] and records(root)[0]["status"] == "active"
    assert not ops.select(root, [SKILL], now="2026-06-30T00:00:00Z")["summaries"]


def test_critical_handoff_backlink_owner_and_recheck(root):
    capture(root, proposal(critical=True))
    handoff = task(root, output_links=[])
    assert ops.prune(root, SKILL, now="2026-06-30T00:00:00Z", handoffs={"LL-001": handoff})["blocked"]
    handoff = task(root)
    wrong = {**handoff, "owner": "Other"}
    assert ops.prune(root, SKILL, now="2026-06-30T00:00:00Z", handoffs={"LL-001": wrong})["blocked"]
    result = ops.prune(root, SKILL, now="2026-06-30T00:00:00Z", apply=True,
                       expected_revision=revision(root), handoffs={"LL-001": handoff})
    assert result["actions"][0]["action"] == "retire"
    task(root, status="completed")
    result = ops.prune(root, SKILL, now="2026-07-30T00:00:00Z", preservation=approve(root))
    assert result["blocked"] and not result["actions"]
    assert (root / ".github/skills" / SKILL / "SKILL.md").read_text() == "safeguard\n"


@pytest.mark.parametrize("status", ["raw", "reviewed", "incorporated", "applied", "mystery"])
def test_legacy_undated_reader_protected(root, status):
    path = root / "x-ipe-docs/skill-meta" / SKILL / ops.LEGACY
    path.write_text(f"---\nskill_name: {SKILL}\n---\n## LL-009 | undated | {status} | major\nOld narrative\n")
    before = path.read_bytes()
    result = ops.select(root, [SKILL], now=NOW)
    assert not result["summaries"] and result["protected"]
    assert ops.prune(root, SKILL, now=NOW)["blocked"]
    with pytest.raises(ValueError):
        capture(root)
    assert path.read_bytes() == before


def test_legacy_filename_valid_new_schema_and_ambiguous_files(root):
    capture(root)
    canonical = Path(ops.load(root, SKILL)["path"])
    old = canonical.with_name(ops.LEGACY)
    canonical.rename(old)
    assert ops.select(root, [SKILL], now=NOW)["summaries"]
    canonical.write_text(old.read_text())
    with pytest.raises(ValueError, match="Ambiguous"):
        ops.load(root, SKILL)


@pytest.mark.parametrize("field,value", [("status", "unknown"), ("created_at", None),
                                        ("expires_at", "2026-01-01"), ("id", "LL-bad")])
def test_malformed_records_protected_no_mutation(root, field, value):
    capture(root)
    snapshot = ops.load(root, SKILL)
    snapshot["document"]["records"][0][field] = value
    Path(snapshot["path"]).write_bytes(ops.render(snapshot["document"]))
    before = revision_bytes = Path(snapshot["path"]).read_bytes()
    assert ops.select(root, [SKILL], now=NOW)["protected"]
    with pytest.raises(ValueError):
        ops.prune(root, SKILL, apply=True, expected_revision=ops.digest(revision_bytes), now=NOW)
    assert Path(snapshot["path"]).read_bytes() == before


@pytest.mark.parametrize("now", ["2026-01-01", "2026-01-01T00:00:00", "2026-01-01T00:00:00+01:00", "nonsense"])
def test_utc_only(root, now):
    with pytest.raises(ValueError):
        capture(root, now=now)


def test_revision_required_conflict_and_same_snapshot_writers(root):
    initial = revision(root)
    with pytest.raises(ValueError):
        ops.capture(root, SKILL, proposal(), expected_revision=None, now=NOW)
    capture(root)
    with pytest.raises(ValueError, match="Revision conflict"):
        ops.capture(root, SKILL, proposal(1), expected_revision=initial, now=NOW)
    shared = revision(root)
    def writer(n):
        try:
            ops.capture(root, SKILL, proposal(n), expected_revision=shared, now=NOW)
            return True
        except (ValueError, BlockingIOError):
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(writer, [1, 2])) == 1
    assert len(records(root)) == 2


def test_lock_contention_and_noncooperating_revision(root):
    import fcntl
    capture(root)
    lock = Path(ops.load(root, SKILL)["path"]).parent / ".lesson-ops.lock"
    with lock.open("r+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            capture(root, proposal(1))
    snapshot = ops.load(root, SKILL)
    Path(snapshot["path"]).write_bytes(Path(snapshot["path"]).read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Revision conflict"):
        ops.commit(root, snapshot, snapshot["document"])
    assert list(lock.parent.glob(".lesson-*")) == [lock]


@pytest.mark.parametrize("skill", ["../escape", "/escape", "x-ipe-tool/escape", "wrong"])
def test_prohibited_skill_paths(root, skill):
    with pytest.raises(ValueError):
        ops.load(root, skill)


def test_symlink_and_hardlink_protection(root, tmp_path):
    capture(root)
    path = Path(ops.load(root, SKILL)["path"])
    saved = path.read_bytes()
    external = root / "external.md"
    external.write_bytes(saved)
    path.unlink()
    path.symlink_to(external)
    with pytest.raises(ValueError, match="Symlink"):
        ops.load(root, SKILL)
    path.unlink()
    os.link(external, path)
    with pytest.raises(ValueError, match="Hard link"):
        ops.load(root, SKILL)


def test_installed_template_resolves_without_repo_templates(root):
    template = yaml.safe_load((CANDIDATE / "templates/lesson-learned.md").read_text().split("---")[1].replace("{skill_name}", SKILL))
    template["records"] = []
    path = Path(ops.load(root, SKILL)["path"])
    path.write_bytes(ops.render(template))
    assert capture(root)["id"] == "LL-001"


def test_real_cli_capture_select_settle_prune(root):
    code, result = cli(root, "capture", proposal(), "--expected-revision", revision(root))
    assert code == 0 and result["disposition"] == "captured"
    code, result = cli(root, "select")
    assert code == 0 and len(result["summaries"]) == 1
    code, result = cli(root, "settle", {"id": "LL-001", "decision": {"status": "retired", "reason": "obsolete"}},
                       "--expected-revision", revision(root))
    assert code == 0 and result["disposition"] == "retired"
    before = revision(root)
    code, result = cli(root, "prune")
    assert code == 0 and result["disposition"] == "dry_run" and revision(root) == before
    code, result = cli(root, "capture", proposal(2), "--expected-revision", "0" * 64)
    assert code == 1 and result["ok"] is False


def test_real_cli_apply_and_failure_shapes(root):
    capture(root)
    # CLI --now supersedes the first supplied default instant.
    code, result = cli(root, "prune", {}, "--now", EXPIRES)
    assert code == 0 and result["actions"][0]["action"] == "retire"
    code, result = cli(root, "prune", {}, "--now", EXPIRES, "--apply", "--expected-revision", revision(root))
    assert code == 0 and records(root)[0]["status"] == "retired"
    code, result = cli(root, "prune", {"preservation": approve(root)}, "--now", "2026-05-01T00:00:00Z",
                       "--apply", "--expected-revision", revision(root))
    assert code == 0 and not records(root)
    code, result = cli(root, "select", {}, "--apply")
    assert code == 1 and result["ok"] is False


def test_atomic_replace_failure_preserves_queue(root, monkeypatch):
    capture(root)
    before = revision(root)
    def fail(*args):
        raise OSError("injected replacement failure")
    monkeypatch.setattr(ops.os, "replace", fail)
    with pytest.raises(OSError, match="injected"):
        capture(root, proposal(2))
    assert revision(root) == before and len(records(root)) == 1
    folder = Path(ops.load(root, SKILL)["path"]).parent
    assert list(folder.glob(".lesson-*")) == [folder / ".lesson-ops.lock"]


@pytest.mark.parametrize("mutation", ["next_id", "duplicate_id", "unrelated_prose"])
def test_corrupt_queue_preserved(root, mutation):
    capture(root)
    snapshot = ops.load(root, SKILL)
    if mutation == "next_id":
        snapshot["document"]["next_id"] = 1
    elif mutation == "duplicate_id":
        snapshot["document"]["records"].append(deepcopy(snapshot["document"]["records"][0]))
    raw = ops.render(snapshot["document"])
    if mutation == "unrelated_prose":
        raw += b"\nUnrelated handwritten notes\n"
    Path(snapshot["path"]).write_bytes(raw)
    assert ops.select(root, [SKILL], now=NOW)["protected"]
    assert Path(snapshot["path"]).read_bytes() == raw


def test_critical_retirement_and_planned_task_gate(root):
    capture(root, proposal(critical=True))
    plan(root)
    with pytest.raises(ValueError):
        settle(root, {"status": "retired", "reason": "reject", "task": "TASK-2", "handoff": task(root)})
    with pytest.raises(ValueError):
        settle(root, {"status": "retired", "reason": "reject", "task": "TASK-1", "handoff": "TASK-1"})
    settle(root, {"status": "retired", "reason": "superseded; risk task owns follow-up", "task": "TASK-1", "handoff": task(root)})
    assert records(root)[0]["status"] == "retired"


def test_applied_regression_at_pending_cap_blocks_without_eviction(root):
    capture(root)
    plan(root)
    settle(root, receipts(root))
    for i in range(1, 9):
        capture(root, proposal(i))
    p = proposal()
    p["evidence"] = ["tests/regression.md"]
    before = revision(root)
    assert capture(root, p, recurrence=True)["disposition"] == "blocked"
    assert revision(root) == before


def test_real_cli_planned_and_applied(root):
    capture(root)
    decision = {"status": "planned", "owner": task(root),
                "candidate": f"x-ipe-docs/skill-meta/{SKILL}/candidate", "change": "guard", "test": "test_permission_guard"}
    code, result = cli(root, "settle", {"id": "LL-001", "decision": decision}, "--expected-revision", revision(root))
    assert code == 0 and result["disposition"] == "planned"
    code, result = cli(root, "settle", {"id": "LL-001", "decision": receipts(root)}, "--expected-revision", revision(root))
    assert code == 0 and result["disposition"] == "applied"


def test_unknown_truth_without_invented_correction_routes_incident(root):
    p = {"severity": "critical", "summary": "Unapproved destructive action", "admission": {}}
    assert capture(root, p)["disposition"] == "incident_handoff_required"
    assert not Path(ops.load(root, SKILL)["path"]).exists()


def test_whitespace_dedup_does_not_consume_pending_capacity(root):
    p = proposal()
    p["cause"] = "  " + p["cause"] + "  "
    p["corrective_rule"] = "  " + p["corrective_rule"] + "  "
    capture(root, p)
    assert capture(root)["disposition"] == "duplicate"
    assert len(records(root)) == 1


def test_legacy_filename_critical_handoff_uses_actual_queue(root):
    capture(root, proposal(critical=True))
    canonical = Path(ops.load(root, SKILL)["path"])
    canonical.rename(canonical.with_name(ops.LEGACY))
    handoff = task(root, output_links=[f"x-ipe-docs/skill-meta/{SKILL}/{ops.LEGACY}#LL-001"])
    assert ops.prune(root, SKILL, now="2026-06-30T00:00:00Z", apply=True,
                     expected_revision=revision(root), handoffs={"LL-001": handoff})["actions"]
    assert records(root)[0]["status"] == "retired"


def test_applied_replay_after_later_production_revision_is_read_only(root):
    capture(root)
    plan(root)
    decision = receipts(root)
    settle(root, decision)
    before = revision(root)
    (root / ".github/skills" / SKILL / "SKILL.md").write_text("later independently published version\n")
    assert settle(root, decision, now="2026-01-10T00:00:00Z")["disposition"] == "unchanged"
    assert revision(root) == before
    with pytest.raises(ValueError):
        settle(root, {**decision, "task": "TASK-other"})


@pytest.mark.parametrize("terminal", ["applied", "retired"])
def test_terminal_time_cannot_be_rewound_by_recurrence_or_purge(root, terminal):
    capture(root)
    if terminal == "applied":
        plan(root)
        settle(root, receipts(root), now="2026-01-10T00:00:00Z")
        p = proposal()
        p["evidence"] = ["tests/new-regression.md"]
        with pytest.raises(ValueError):
            capture(root, p, recurrence=True, now="2026-01-05T00:00:00Z")
    else:
        settle(root, {"status": "retired", "reason": "obsolete"}, now="2026-01-10T00:00:00Z")
    before = revision(root)
    assert not ops.prune(root, SKILL, now="2026-02-08T23:59:59.999999Z", preservation=approve(root))["actions"]
    assert revision(root) == before


@pytest.mark.parametrize("mutation", ["duplicate_yaml", "overlong_ttl", "wrong_review", "terminal_before_validation", "bad_plan", "bad_evidence"])
def test_protected_schema_cannot_be_silently_rewritten(root, mutation):
    capture(root, proposal(critical=True))
    if mutation == "terminal_before_validation":
        plan(root)
        settle(root, receipts(root), now="2026-01-02T00:00:00Z")
    snapshot = ops.load(root, SKILL)
    entry = snapshot["document"]["records"][0]
    if mutation == "overlong_ttl":
        entry["expires_at"] = "2030-01-01T00:00:00Z"
    elif mutation == "wrong_review":
        entry["review_due"] = "2026-05-01T00:00:00Z"
    elif mutation == "terminal_before_validation":
        entry["terminal_at"] = "2025-12-31T00:00:00Z"
        entry["purge_after"] = "2026-01-30T00:00:00Z"
    elif mutation == "bad_plan":
        entry.update(status="planned", plan=None)
    elif mutation == "bad_evidence":
        entry["evidence"] = [{"unexpected": "mapping"}]
    raw = ops.render(snapshot["document"])
    if mutation == "duplicate_yaml":
        raw = raw.replace(b"occurrences: 1", b"occurrences: 999\noccurrences: 1")
    Path(snapshot["path"]).write_bytes(raw)
    result = ops.select(root, [SKILL], now=NOW)
    assert result["protected"] and not result["summaries"]
    with pytest.raises((ValueError, TypeError, yaml.YAMLError)):
        ops.prune(root, SKILL, now="2031-01-01T00:00:00Z", apply=True,
                  expected_revision=ops.digest(raw), preservation={"kind": "explicit_user_approval",
                  "revision": ops.digest(raw), "authorized_by": "User", "reason": "not permission to rewrite corruption"})
    assert Path(snapshot["path"]).read_bytes() == raw


def test_expired_critical_select_surfaces_cleanup_without_selecting_risk(root):
    capture(root, proposal(critical=True))
    before = revision(root)
    result = ops.select(root, [SKILL], now="2026-06-30T00:00:00Z")
    assert not result["summaries"]
    assert result["notices"] == [{"skill": SKILL, "id": "LL-001", "reason": "expired critical; owned handoff/cleanup review required"}]
    assert not ops.select(root, [SKILL], relevant_to="x-ipe-tool-other", now="2026-06-30T00:00:00Z")["notices"]
    assert revision(root) == before


def test_failed_merge_preserves_or_releases_owned_plan_without_application(root):
    capture(root)
    plan(root)
    before = revision(root)
    decision = receipts(root)
    pub = root / decision["publication_receipt"]
    data = json.loads(pub.read_text())
    data.update(state="rolled_back", byte_parity=False)
    pub.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        settle(root, decision)
    assert revision(root) == before and records(root)[0]["status"] == "planned"
    settle(root, {"status": "active", "task": "TASK-1", "reason": "merge rolled back"})
    assert records(root)[0]["expires_at"] == EXPIRES


def test_repeated_plan_is_unchanged_without_resetting_ownership_clock(root):
    capture(root)
    plan(root)
    before = revision(root)
    decision = {"status": "planned", "owner": task(root),
                "candidate": f"x-ipe-docs/skill-meta/{SKILL}/candidate",
                "change": "Add precondition guard", "test": "test_permission_guard"}
    assert settle(root, decision, now="2026-01-10T00:00:00Z")["disposition"] == "unchanged"
    assert revision(root) == before and records(root)[0]["planned_at"] == NOW