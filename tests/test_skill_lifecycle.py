"""Candidate contracts plus real installed helpers in temporary projects only.

Content checks are not a runtime simulation of autonomous agent decisions.
No tests write live boards, source, Git, or skills.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
NAME = "x-ipe-workflow-task-execution"
META = ROOT / "x-ipe-docs" / "skill-meta" / NAME
CANDIDATE = META / "candidate"
SKILLS = ROOT / ".github" / "skills"
BOARD = SKILLS / "x-ipe-tool-task-board-manager" / "scripts"
CREATOR = SKILLS / "x-ipe-meta-skill-creator" / "scripts"
APP = SKILLS / "x-ipe-tool-x-ipe-app-interactor" / "scripts"


def cli(script: Path, root: Path, *args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, "-B", str(script), *args], cwd=root,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode, json.loads(result.stdout or result.stderr)


def snapshot(folder: Path) -> dict[str, str]:
    return {
        file.relative_to(folder).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(folder.rglob("*")) if file.is_file()
    }


def block(text: str, heading: str) -> dict:
    section = text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
    return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", section, re.S).group(1))


def test_five_phase_procedure_and_single_owner():
    text = (CANDIDATE / "SKILL.md").read_text()
    xml = re.search(r'(<procedure name=".*?</procedure>)', text, re.S).group(1)
    procedure = ET.fromstring(xml)
    phases = [node for node in procedure if node.tag.startswith("phase_")]
    assert [node.findtext("name") for node in phases] == [
        "Orient", "Plan", "Execute", "Verify", "Record",
    ]
    assert all(len(node.findall("action")) == 1 and node.find("gate") is not None for node in phases)
    for required in ("One task owner", "No upfront speculative chain", "no recursive execution",
                     "already-entered direct child", "unresolved conflict blocks execution"):
        assert required in text
    assert "Create ALL chained tasks upfront" not in text
    assert text.count("\nname: x-ipe-workflow-task-execution\n") == 1


def test_common_contract_and_existing_output_fields():
    text = (CANDIDATE / "SKILL.md").read_text()
    common = (CANDIDATE / "references/lifecycle.md").read_text()
    live = (SKILLS / NAME / "SKILL.md").read_text()
    # Live documentation includes non-YAML union notation; compare its declared
    # two-space aggregate fields without repairing or rewriting production.
    live_output = live.split("## Output Result", 1)[1].split("\n## ", 1)[0]
    assert set(block(text, "Output Result")["output"]) == set(re.findall(r"(?m)^  (\w+):", live_output))
    child = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", common, re.S).group(1))["task_completion_output"]
    assert list(child)[0] == "category"
    assert set(child) == {"category", "status", "next_task_based_skill",
                          "process_preference", "task_output_links"}
    assert "optional: preserve only if declared by child" in common
    assert "Do not reject a child solely for omitting require_human_review" in common
    assert "completed/cancelled/skipped are terminal" in common
    assert "Tools/assistants retain operation_output" in common
    assert "Load this reference once per agent context" in common
    assert "references/lifecycle.md" in text
    model = yaml.safe_load((CANDIDATE / "templates/task-record.yaml").read_text())
    assert "interaction_mode" not in model
    assert model["execution"]["process_preference"]["interaction_mode"] == "interact-with-human"


@pytest.mark.parametrize("mode,decision,boundary", [
    ("interact-with-human", "Ask human and wait", "Human review and route confirmation"),
    ("dao-represent-human-to-interact", "DAO bounded answer/guidance", "DAO selects authorized route"),
    ("dao-represent-human-to-interact-for-questions-in-skill", "DAO bounded answer/guidance", "Human review and route confirmation"),
])
def test_exact_mode_contract(mode: str, decision: str, boundary: str):
    common = (CANDIDATE / "references/lifecycle.md").read_text()
    row = next(line for line in common.splitlines() if line.startswith(f"| {mode} |"))
    assert decision in row and boundary in row
    assert "Explicit task --interaction@MODE" in common
    assert "Re-read" in common and "Representative execution_strategy cannot silently overwrite" in common
    # Current app specification/UI semantics outrank an unsupported review claim.
    representative = (SKILLS / "x-ipe-assistant-user-representative-Engineer/SKILL.md").read_text()
    assert "instruction_units:" in representative and "execution_plan:" in representative
    assert "approval` is guidance, NOT human approval" in common
    js_tests = (ROOT / "tests/frontend-js/action-execution-modal-cr001.test.js").read_text()
    assert mode in js_tests
    if "questions-in-skill" in mode:
        # Preserve current externally-visible meaning; no unauthorized inversion.
        assert "DAO inner-skill only" in js_tests
        assert "not authorized by the current user" in " ".join(common.split())
        assert "Hybrid means DAO within skill, human completion/route confirmation" in common
        workflow = (CANDIDATE / "SKILL.md").read_text()
        assert "full DAO and hybrid use the representative" in workflow
        assert "hybrid uses DAO within skill, then waits for human" in workflow
        assert "completion/route confirmation" in workflow


def test_source_resolution_git_safety_and_small_path():
    text = (CANDIDATE / "references/lifecycle.md").read_text()
    for required in ("Explicit broken", "never mask", "legacy", "Multiple matches",
                     "symlink escape", "content hashes", "Default no commit",
                     "No git add -A", "Preexisting staged changes block",
                     "no implicit network", "No app workflow skips", "combined deliverable",
                     "any changed tested input invalidates"):
        assert required.lower() in text.lower()
    assert "Source artifact resolution" in text
    assert "timestamps alone" in (CANDIDATE / "SKILL.md").read_text()
    assert "candidate_ready is not publication/release" in text


def test_action_sources_and_distinct_tool_key():
    source = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"implementation:\s*\{[^\n]+skill: 'x-ipe-task-based-code-implementation'", source)
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["implement"]["actions"]["implementation"]
    assert action["deliverables"] == ["$output:impl-files", "$output-folder:impl-folder"]
    tools = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())
    assert "code_implementation" in tools["stages"]["implement"]
    assert "implementation" not in tools["stages"]["implement"]
    common = (CANDIDATE / "references/lifecycle.md").read_text()
    assert "Only `done` plus verified required artifacts" in common
    assert "shared.stage.actions.action" in common and "features[].stage.actions.action" in common


def test_known_deliverable_mismatches_are_recorded_not_waived():
    common = (CANDIDATE / "references/lifecycle.md").read_text()
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    closing = (SKILLS / "x-ipe-task-based-feature-closing/SKILL.md").read_text()
    acceptance = (SKILLS / "x-ipe-task-based-feature-acceptance-test/SKILL.md").read_text()
    implementation = (SKILLS / "x-ipe-task-based-code-implementation/SKILL.md").read_text()
    assert template["stages"]["validation"]["actions"]["feature_closing"]["deliverables"] == []
    integration = (SKILLS / "x-ipe-task-based-feature-closing/references/integration.md").read_text()
    assert "deliverables {}" in closing + integration
    assert 'deliverables: {"closing-report": "{path}"}' not in closing
    assert "task artifact" in closing + integration
    # Both consumers are promoted. Distinguish fixed current contracts from the
    # historical mismatch; never reintroduce a tag rejected by the real service.
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", acceptance, re.S).group(0))
    fields = {field.attrib["name"]: " ".join(field.itertext()) for field in init.findall("field")}
    assert "Selected impl-files is actual implementation-file input" in fields["implementation_files"]
    assert "nonempty file array" in fields["implementation_files"]
    assert "Never output directories or design as implementation" in fields["implementation_files"]
    assert "both parts" in fields["technical_design_link"]
    assert "Implementation context is not a design initializer" in fields["technical_design_link"]
    assert '    - "src/"' in implementation and '    - "tests/"' in implementation
    for finding in ("Current repaired contracts", "no extract tags", "eval-report",
                    "technical_design_link", "actual changed files separately",
                    "legacy test", "blocks that invocation"):
        assert finding in common


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "x-ipe-docs").mkdir()
    return tmp_path


def payload(**overrides) -> dict:
    return {"task_id": "TASK-123", "task_type": "Bug Fix", "description": "Fix approved defect",
            "role": "Quill", "status": "pending", "output_links": [], "next_task": "", **overrides}


def ensure(root: Path, task: dict) -> tuple[int, dict]:
    return cli(BOARD / "task_ensure.py", root, "--task", json.dumps(task))


def test_supplied_id_ensure_retry_no_duplicate_or_timestamp_change(project: Path):
    code, first = ensure(project, payload())
    assert code == 0 and first["data"]["created"] is True
    before = snapshot(project)
    code, second = ensure(project, payload(status="in_progress", output_links=["must-not-overwrite"]))
    assert code == 0 and second["data"]["created"] is False
    assert second["data"]["task"] == first["data"]["task"]
    assert snapshot(project) == before
    code, query = cli(BOARD / "task_query.py", project, "--range", "all", "--page-size", "1")
    assert code == 0 and query["data"]["total"] == 1


@pytest.mark.parametrize("field,value,error", [
    ("role", "Echo", "OWNERSHIP_CONFLICT"),
    ("role", "", "OWNERSHIP_REQUIRED"),
    ("description", "Different scope", "CONTEXT_CONFLICT"),
    ("task_type", "Code Refactor", "CONTEXT_CONFLICT"),
])
def test_resume_conflicts_preserve_all_bytes(project: Path, field: str, value: str, error: str):
    assert ensure(project, payload())[0] == 0
    before = snapshot(project)
    code, result = ensure(project, payload(**{field: value}))
    assert code == 1 and result["error"] == error
    assert snapshot(project) == before


@pytest.mark.parametrize("status", ["in_progress", "blocked", "deferred", "completed", "cancelled", "skipped"])
def test_resume_preserves_current_and_terminal_status(project: Path, status: str):
    code, first = ensure(project, payload(status=status, output_links=["evidence.md"]))
    assert code == 0
    before = snapshot(project)
    code, second = ensure(project, payload())
    assert code == 0 and second["data"]["task"] == first["data"]["task"]
    assert snapshot(project) == before


def test_create_then_ensure_allocated_id_and_complete_pagination(project: Path):
    data = payload()
    del data["task_id"]
    code, created = cli(BOARD / "task_create.py", project, "--task", json.dumps(data))
    assert code == 0
    current_id = created["data"]["task_id"]
    assert ensure(project, payload(task_id=current_id))[1]["data"]["created"] is False
    assert ensure(project, payload(task_id="TASK-900", role="Echo"))[0] == 0
    pages = [cli(BOARD / "task_query.py", project, "--range", "all", "--page-size", "1", "--page", str(page))[1]["data"]
             for page in (1, 2)]
    assert all(page["total_pages"] == 2 for page in pages)
    assert {task["role"] for page in pages for task in page["tasks"]} == {"Quill", "Echo"}


def test_duplicate_live_context_blocks_resume_without_repair(project: Path):
    code, first = ensure(project, payload())
    assert code == 0
    tasks = project / "x-ipe-docs/planning/tasks"
    (tasks / "tasks-2000-01-01.json").write_text(json.dumps({"_version": "1.0", "tasks": [first["data"]["task"]]}))
    before = snapshot(project)
    code, rejected = ensure(project, payload())
    assert code == 1 and rejected["error"] == "INCONSISTENT_BOARD"
    assert snapshot(project) == before


def validate(root: Path, candidate: Path) -> tuple[int, dict]:
    return cli(CREATOR / "validate_skill.py", root, "--project-root", str(root), "--candidate", str(candidate),
               "--name", NAME, "--type", "x-ipe-workflow-orchestration")


def test_installed_validator_readonly_complete_candidate_links():
    before = snapshot(CANDIDATE)
    code, receipt = validate(ROOT, CANDIDATE)
    assert code == 0 and receipt["ok"], receipt["errors"]
    assert not receipt["warnings"]
    assert receipt["body_lines"] <= 1000
    assert receipt["files"] == before and snapshot(CANDIDATE) == before


def test_candidate_revision_change_invalidates_review_hash(project: Path):
    candidate = project / "x-ipe-docs/skill-meta" / NAME / "candidate"
    shutil.copytree(CANDIDATE, candidate)
    # Copy only external resources referenced by this candidate into the sandbox.
    for relative in ("src/x_ipe/static/js/features/workflow-stage.js", "x-ipe-docs/config/workflow-template.json",
                     "x-ipe-docs/config/tools.json"):
        destination = project / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    code, original = validate(project, candidate)
    assert code == 0
    with (candidate / "references/lifecycle.md").open("a") as stream:
        stream.write("\nChanged tested revision.\n")
    code, changed = validate(project, candidate)
    assert code == 0 and changed["candidate_hash"] != original["candidate_hash"]
    for name in ("baseline.json", "managed.json"):
        (project / name).write_text("{}")
    before = snapshot(project)
    code, rejected = cli(CREATOR / "publish_skill.py", project,
                         "--project-root", str(project), "--name", NAME, "--candidate", str(candidate),
                         "--type", "x-ipe-workflow-orchestration", "--baseline", str(project / "baseline.json"),
                         "--managed", str(project / "managed.json"), "--candidate-hash", original["candidate_hash"])
    assert code != 0 and "fingerprint changed" in json.dumps(rejected)
    assert snapshot(project) == before and not (project / ".github/.skill-publication").exists()


def test_external_consumer_revision_requires_separate_evidence(project: Path):
    candidate = project / "x-ipe-docs/skill-meta" / NAME / "candidate"
    shutil.copytree(CANDIDATE, candidate)
    for relative in ("src/x_ipe/static/js/features/workflow-stage.js", "x-ipe-docs/config/workflow-template.json",
                     "x-ipe-docs/config/tools.json"):
        destination = project / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    code, before = validate(project, candidate)
    assert code == 0
    config = project / "x-ipe-docs/config/tools.json"
    old_digest = hashlib.sha256(config.read_bytes()).hexdigest()
    config.write_text(config.read_text() + "\n")
    code, after = validate(project, candidate)
    assert code == 0 and before["candidate_hash"] == after["candidate_hash"]
    assert hashlib.sha256(config.read_bytes()).hexdigest() != old_digest
    # The installed validator does not bind external consumer bytes. Candidate
    # policy explicitly requires separate consumer evidence, not a fabricated
    # claim that structural validation detects external semantic changes.
    common = (CANDIDATE / "references/lifecycle.md").read_text()
    assert "test and config SHA256 hashes" in common
    assert "any changed tested input invalidates affected receipts/review" in common


def workflow_project(project: Path) -> tuple[Path, dict]:
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    config = project / "x-ipe-docs/config"
    config.mkdir()
    (config / "workflow-template.json").write_text(json.dumps(template))
    stages = {stage: {"status": "in_progress", "actions": {
        action: {"status": "pending", "deliverables": {}} for action in definition["actions"]
    }} for stage, definition in template["stages"].items()}
    state = {"name": "test", "schema_version": "3.0", "current_stage": "implement",
             "shared": {stage: stages[stage] for stage in ("ideation", "requirement")},
             "features": [{"feature_id": "FEATURE-001", **{stage: stages[stage] for stage in ("implement", "validation", "feedback")}}]}
    folder = project / "x-ipe-docs/engineering-workflow"
    folder.mkdir()
    path = folder / "workflow-test.json"
    path.write_text(json.dumps(state))
    return path, state


def test_real_workflow_writer_and_keyed_per_feature_readback(project: Path):
    path, _ = workflow_project(project)
    source = project / "src"
    source.mkdir()
    (source / "changed.py").write_text("value = 1\n")
    deliverables = {"impl-files": ["src/changed.py"], "impl-folder": "src"}
    code, result = cli(APP / "workflow_update_action.py", project, "--workflow", "test", "--action", "implementation",
                       "--status", "done", "--feature-id", "FEATURE-001", "--deliverables", json.dumps(deliverables), "--format", "json")
    assert code == 0 and result["success"] is True
    stored = json.loads(path.read_text())["features"][0]["implement"]["actions"]["implementation"]
    assert stored["status"] == "done" and stored["deliverables"] == deliverables
    before = snapshot(project)
    code, result = cli(APP / "workflow_get_state.py", project, "--workflow", "test", "--format", "json")
    # Read helper returns raw state, not the write helper success envelope.
    assert code == 0 and result == json.loads(path.read_text()) and snapshot(project) == before


def test_writer_validation_is_not_lifecycle_completion_proof(project: Path):
    path, _ = workflow_project(project)
    # Actual writer allows incomplete done output: docs must impose the stronger gate.
    code, result = cli(APP / "workflow_update_action.py", project, "--workflow", "test", "--action", "implementation",
                       "--status", "done", "--feature-id", "FEATURE-001", "--deliverables", "{}")
    assert code == 0 and result["success"] is True
    stored = json.loads(path.read_text())["features"][0]["implement"]["actions"]["implementation"]
    assert stored["deliverables"] == {}
    common = (CANDIDATE / "references/lifecycle.md").read_text()
    assert "Empty/missing/wrong-feature outputs block" in common


def test_no_workflow_skips_or_mutations_on_invalid_tool_action(project: Path):
    workflow_project(project)
    before = snapshot(project)
    code, result = cli(APP / "workflow_update_action.py", project, "--workflow", "test", "--action", "code_implementation",
                       "--status", "done", "--feature-id", "FEATURE-001")
    assert code != 0 and result["success"] is False
    # Writer lock may be created; workflow bytes must remain unchanged.
    assert {key: snapshot(project)[key] for key in before} == before
    assert "No skipped writes" in (CANDIDATE / "SKILL.md").read_text()