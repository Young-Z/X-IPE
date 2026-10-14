"""Final integration evidence: actual helpers in disposable projects, not agents.

Never writes the real board, lessons, skills, instruction mirrors or Git state.
Candidate-only changes are deliberately distinct from installed publications.
"""
import importlib.util
import json
from pathlib import Path
import re
import sys

import pytest
import yaml

from tests.test_skill_creator_foundation import skill

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".github/skills"
META = ROOT / "x-ipe-docs/skill-meta"
CREATOR = META / "x-ipe-meta-skill-creator/candidate"
REP = "x-ipe-assistant-user-representative-Engineer"
NOW = "2026-10-14T00:00:00Z"


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.fixture
def installed(monkeypatch):
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    scripts = SKILLS / "x-ipe-meta-skill-creator/scripts"
    validator = module(scripts / "validate_skill.py", "installed_validator_6749")
    monkeypatch.setitem(sys.modules, "validate_skill", validator)
    return (validator, module(scripts / "publish_skill.py", "installed_publisher_6749"),
            module(SKILLS / "x-ipe-meta-lesson-learned/scripts/lesson_ops.py", "installed_lessons_6749"))


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def snippets():
    text = (CREATOR / "references/consumer-integration.md").read_text()
    blocks = re.findall(r"```python\n(.*?)\n```", text, re.S)
    assert len(blocks) == 4
    return blocks


def test_documented_selection_is_actual_installed_read_only_call(tmp_path, installed):
    _, _, ops = installed
    name = "x-ipe-tool-integration-test"
    (tmp_path / ".github/skills" / name).mkdir(parents=True)
    context = dict(ops=ops, root=tmp_path, owner_skills=[name], skill_name=name, now=NOW)
    before = snapshot(tmp_path)
    exec(snippets()[0], context)
    assert context["selection"] == dict(summaries=[], critical_overflow=[], protected=[], notices=[])
    assert snapshot(tmp_path) == before


def setup_lesson(root, ops):
    name = "x-ipe-tool-integration-test"
    target = root / ".github/skills" / name
    target.mkdir(parents=True)
    (target / "SKILL.md").write_bytes(skill(name=name, marker="baseline"))
    candidate = root / "x-ipe-docs/skill-meta" / name / "candidate"
    candidate.mkdir(parents=True)
    (candidate / "SKILL.md").write_bytes(skill(name=name, marker="new guard"))
    evidence = root / "evidence"
    evidence.mkdir()
    proposal = dict(severity="major", summary="Guard published evidence", cause="Missing receipt guard",
                    corrective_rule="Require exact publication and test evidence", verification="test_guard",
                    evidence=["tests/test_guard.py"], admission=dict(kind="high_value", reason="Verified reusable gap",
                    reusable_gap="Missing publication evidence guard", coverage_check="Existing tests lacked guard",
                    ground_truth="Actual publisher verifies byte parity", basis="systemic_contract_gap",
                    basis_evidence="Disposable integration regression"))
    ops.capture(root, name, proposal, expected_revision=ops.load(root, name)["revision"], now=NOW)
    # Real installed board CLI, not a fabricated new board schema.
    from tests.test_skill_lifecycle import cli, payload, BOARD
    task = payload(task_id="TASK-6749", description="Disposable creator integration", status="in_progress")
    code, result = cli(BOARD / "task_ensure.py", root, "--task", json.dumps(task))
    assert code == 0 and result["data"]["created"]
    board = root / "x-ipe-docs/planning/tasks" / result["data"]["file"]
    assert re.fullmatch(r"tasks-\d{4}-\d{2}-\d{2}\.json", board.name)
    assert board.is_file()
    owner = dict(path=board.relative_to(root).as_posix(), task_id="TASK-6749", owner=task["role"])
    return dict(ops=ops, root=root, primary_skill=name, skill_name=name, owner_skills=[name],
                lesson_id="LL-001", owner=owner, change="Add actual guard", verification="test_guard",
                task_id="TASK-6749", now=NOW), candidate, target, board


def test_documented_plan_real_publish_test_settle_and_replay(tmp_path, installed):
    v, publisher, ops = installed
    context, candidate, target, board = setup_lesson(tmp_path, ops)
    board_before = board.read_bytes()
    blocks = snippets()
    exec(blocks[0], context)
    assert context["selection"]["summaries"][0]["id"] == "LL-001"
    exec(blocks[1], context)
    assert context["planned"]["disposition"] == "planned"
    original_expiry = ops.load(tmp_path, context["primary_skill"])["document"]["records"][0]["expires_at"]
    checked = v.validate(tmp_path, candidate, context["primary_skill"], "x-ipe-tool")
    assert checked["ok"], checked["errors"]
    baseline = v.manifest(v.tree_bytes(target, tmp_path))
    receipt = publisher.publish(tmp_path, candidate, context["primary_skill"], "x-ipe-tool",
                                baseline, baseline, checked["candidate_hash"], apply=True)
    assert receipt["state"] == "published" and receipt["byte_parity"]
    # A real verification runs against the actual newly published bytes.
    actual = v.manifest(v.tree_bytes(target, tmp_path))
    assert actual == receipt["files"] == checked["files"]
    assert b"new guard" in (target / "SKILL.md").read_bytes()
    (tmp_path / "evidence/publication.json").write_text(json.dumps(receipt))
    test_receipt = dict(ok=True, tests_passed=True, skill_name=context["primary_skill"],
                        production_revision=receipt["candidate_hash"], candidate_hash=receipt["candidate_hash"],
                        lesson_ids=["LL-001"], verification="test_guard")
    (tmp_path / "evidence/test.json").write_text(json.dumps(test_receipt))
    context.update(production_revision=receipt["candidate_hash"], publication_receipt="evidence/publication.json",
                   test_receipt="evidence/test.json")
    exec(blocks[2], context)
    assert context["applied"]["disposition"] == "applied"
    first = ops.load(tmp_path, context["primary_skill"])
    assert first["document"]["records"][0]["expires_at"] == original_expiry
    exec(blocks[2], context)
    assert context["applied"]["disposition"] == "unchanged"
    assert ops.load(tmp_path, context["primary_skill"])["revision"] == first["revision"]
    assert board.read_bytes() == board_before


@pytest.mark.parametrize("defect", ["missing-receipt", "editor-receipt", "wrong-owner"])
def test_documented_settlement_failure_preserves_plan_then_release(tmp_path, installed, defect):
    _, _, ops = installed
    context, _, _, board = setup_lesson(tmp_path, ops)
    blocks = snippets()
    exec(blocks[1], context)
    queue_before = ops.load(tmp_path, context["primary_skill"])["revision"]
    board_before = board.read_bytes()
    context.update(production_revision="not-a-published-fingerprint", publication_receipt="evidence/missing.json",
                   test_receipt="evidence/missing-test.json")
    if defect == "editor-receipt":
        (tmp_path / "evidence/editor.json").write_text(json.dumps(dict(operation="editor-promotion", byte_parity=True)))
        (tmp_path / "evidence/test.json").write_text("{}")
        context.update(publication_receipt="evidence/editor.json", test_receipt="evidence/test.json")
    elif defect == "wrong-owner":
        context["task_id"] = "TASK-999"
    with pytest.raises((ValueError, FileNotFoundError)):
        exec(blocks[2], context)
    assert ops.load(tmp_path, context["primary_skill"])["revision"] == queue_before
    context.update(task_id="TASK-6749", reason="Publication unavailable; release explicitly")
    exec(blocks[3], context)
    assert context["released"]["disposition"] == "active"
    assert board.read_bytes() == board_before


def test_candidate_validator_exact_existing_assistant_identity_only(tmp_path, installed):
    current = module(CREATOR / "scripts/validate_skill.py", "candidate_validator_6749")
    assert current.validate(ROOT, META / REP / "candidate", REP, "x-ipe-assistant")["ok"]
    # Installed creator was actually promoted; preserve exact-identity controls.
    published = json.loads((META / "x-ipe-meta-skill-creator/publication-receipt-TASK-6749-R2.json").read_text())
    actual = installed[0].manifest(installed[0].tree_bytes(SKILLS / "x-ipe-meta-skill-creator", ROOT))
    assert actual == published["files"] | published["preserved_unmanaged"]
    assert installed[0].fingerprint(published["files"]) == published["candidate_hash"]
    assert installed[0].validate(ROOT, META / REP / "candidate", REP, "x-ipe-assistant") == current.validate(ROOT, META / REP / "candidate", REP, "x-ipe-assistant")
    for index, (name, kind) in enumerate([(REP, "x-ipe-tool"), (REP + "-copy", "x-ipe-assistant"),
                       (REP.replace("Engineer", "ENGINEER"), "x-ipe-assistant"),
                       ("x-ipe-assistant-Arbitrary", "x-ipe-assistant")]):
        root = tmp_path / str(index)  # Keep distinct on case-insensitive macOS volumes.
        candidate = root / "x-ipe-docs/skill-meta" / name / "candidate"
        candidate.mkdir(parents=True)
        (candidate / "SKILL.md").write_bytes(skill(name=name, skill_type=kind))
        assert not current.validate(root, candidate, name, kind)["ok"]
        assert not installed[0].validate(root, candidate, name, kind)["ok"]
    receipt = current.validate(ROOT, CREATOR, "x-ipe-meta-skill-creator", "x-ipe-meta")
    assert receipt["ok"], receipt["errors"]


def test_representative_candidate_keeps_actual_input_output_and_phases():
    live = (SKILLS / REP / "SKILL.md").read_text()
    candidate = (META / REP / "candidate/SKILL.md").read_text()
    for heading in ("Input Parameters", "Output Result"):
        def contract(text):
            section = text.split("## " + heading + "\n", 1)[1].split("\n## ", 1)[0]
            return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", section, re.S)[1])
        assert contract(live) == contract(candidate)
    assert re.findall(r'<phase_\d name="([^"]+)"', live) == re.findall(r'<phase_\d name="([^"]+)"', candidate)
    assert "fallback_required = true ONLY if human_shadow AND confidence < threshold" in candidate
    assert "Append ONE entry covering ALL units" in candidate
    boundary = (META / REP / "candidate/references/decision-boundaries.md").read_text()
    for clause in ("not measured", "approval as guidance only", "Preserve existing story/GWT AC IDs", "actual external behavior"):
        assert clause.lower() in " ".join((candidate + boundary).lower().split())


def test_task_template_goal_adoption_preserves_output_and_owner_boundary():
    old = (SKILLS / "x-ipe-meta-skill-creator/templates/x-ipe-task-based.md").read_text()
    new = (CREATOR / "templates/x-ipe-task-based.md").read_text()
    assert old.split("## Input Parameters", 1)[1].split("### Input Initialization", 1)[0] == new.split("## Input Parameters", 1)[1].split("### Input Initialization", 1)[0]
    # Exact declared output stays intact, including dynamic attributes/placeholders.
    assert old.split("## Output Result", 1)[1].split("## Definition of Done", 1)[0] == new.split("## Output Result", 1)[1].split("## Definition of Done", 1)[0]
    for obsolete in ('type: "routing"', "<phase_6", "<name>Execute Next Action</name>"):
        assert obsolete not in new
    for required in ("goal-contract.md", "Orient/Plan once", "One lifecycle owner", "not measured",
                     "all-required", "Given/When/Then", "No new board/output/action fields"):
        assert required in new