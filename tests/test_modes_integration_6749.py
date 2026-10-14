"""Current candidate contract + actual mode persistence; no agent-pilot claim.

Production and historical publication assertions remain in the original suites.
These checks do not declare revised candidates published or approve own edits.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from tests.test_skill_pipeline_refactor import output_contract

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "x-ipe-docs/skill-meta"
SUFFIXES = (
    "requirement-gathering", "feature-breakdown", "feature-refinement",
    "technical-design", "code-implementation", "feature-acceptance-test",
    "feature-closing", "change-request", "bug-fix", "code-refactor",
)
MODES = (
    "interact-with-human", "dao-represent-human-to-interact",
    "dao-represent-human-to-interact-for-questions-in-skill",
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("suffix", SUFFIXES)
def test_every_adopting_candidate_exact_modes_authority_and_original_output(suffix):
    name = "x-ipe-task-based-" + suffix
    candidate = META / name / "candidate"
    live = ROOT / ".github/skills" / name
    text = (candidate / "SKILL.md").read_text()
    normalized = " ".join(text.lower().split())
    assert all(mode in text for mode in MODES)
    assert "full dao and hybrid" in normalized
    assert "human and hybrid require human" in normalized or (
        "human and hybrid must confirm" in normalized)
    assert "completion/route" in normalized
    assert "every mode" in normalized
    assert "message_context" in text and "instruction_units" in text
    assert "execution_plan" in text
    assert output_contract(candidate / "SKILL.md") == output_contract(live / "SKILL.md")
    for path in candidate.rglob("*.md"):
        body = " ".join(path.read_text().lower().split())
        for inverted in (
            "human and hybrid ask", "human/hybrid ask", "human/hybrid human",
            "hybrid dao-only routing", "hybrid dao routing", "hybrid human within skill",
            "hybrid routes via lifecycle without an extra route confirmation",
            "hybrid has human domain decisions", "only in full dao",
        ):
            assert inverted not in body, (path, inverted)


@pytest.mark.parametrize("mode", MODES)
def test_real_service_roundtrip_matches_enum_sources_and_rejects_unknown(tmp_path, mode):
    from x_ipe.services.workflow_manager_service import WorkflowManagerService
    for relative in ("x-ipe-docs/config/workflow-template.json",
                     "src/x_ipe/resources/config/workflow-template.json"):
        template = json.loads((ROOT / relative).read_text())
        assert template["global"]["process_preference"]["interaction_mode"] == MODES[0]
        assert template["stages"]["validation"]["actions"]["code_refactor"]["optional"] is False
    service = WorkflowManagerService(str(tmp_path))
    assert service.create_workflow("review-modes")["success"]
    before = service.get_workflow("review-modes")
    result = service.update_settings("review-modes", {"process_preference": {"interaction_mode": mode}})
    assert result["success"] and result["data"]["process_preference"]["interaction_mode"] == mode
    restarted = WorkflowManagerService(str(tmp_path))
    after = restarted.get_workflow("review-modes")
    assert after["global"]["process_preference"]["interaction_mode"] == mode
    assert after["shared"] == before["shared"] and after["features"] == before["features"]
    rejected = restarted.update_settings("review-modes", {"process_preference": {"interaction_mode": "hybrid"}})
    assert not rejected["success"] and rejected["error"] == "INVALID_VALUE"
    assert restarted.get_workflow("review-modes") == after


def test_goal_contract_bytes_unchanged_and_template_inputs_outputs_preserved():
    name = "x-ipe-workflow-task-execution"
    relative = "references/goal-contract.md"
    assert (META / name / "candidate" / relative).read_bytes() == (
        ROOT / ".github/skills" / name / relative).read_bytes()
    name = "x-ipe-meta-skill-creator"
    old = (ROOT / ".github/skills" / name / "templates/x-ipe-task-based.md").read_text()
    new = (META / name / "candidate/templates/x-ipe-task-based.md").read_text()
    for start, end in (("## Input Parameters", "### Input Initialization"),
                       ("## Output Result", "## Definition of Done")):
        assert old.split(start, 1)[1].split(end, 1)[0] == new.split(start, 1)[1].split(end, 1)[0]


def test_all_candidates_real_validator_api_equals_cli():
    script = META / "x-ipe-meta-skill-creator/candidate/scripts/validate_skill.py"
    validator = load(script, "modes_validator_6749")
    identities = [("x-ipe-workflow-task-execution", "x-ipe-workflow-orchestration"),
                  ("x-ipe-meta-skill-creator", "x-ipe-meta"),
                  ("x-ipe-assistant-user-representative-Engineer", "x-ipe-assistant")]
    identities += [("x-ipe-task-based-" + suffix, "x-ipe-task-based") for suffix in SUFFIXES]
    for name, kind in identities:
        candidate = META / name / "candidate"
        api = validator.validate(ROOT, candidate, name, kind)
        assert api["ok"], api["errors"]
        process = subprocess.run([sys.executable, "-B", str(script), "--project-root", str(ROOT),
                                  "--candidate", str(candidate), "--name", name, "--type", kind],
                                 capture_output=True, text=True, check=False)
        assert process.returncode == 0, process.stdout + process.stderr
        assert json.loads(process.stdout) == api


def test_publisher_blockers_are_actual_read_only_failures(monkeypatch):
    scripts = META / "x-ipe-meta-skill-creator/candidate/scripts"
    validator = load(scripts / "validate_skill.py", "validate_skill")
    monkeypatch.setitem(sys.modules, "validate_skill", validator)
    publisher = load(scripts / "publish_skill.py", "modes_publisher_6749")
    name = "x-ipe-meta-skill-creator"
    meta = META / name
    live = ROOT / ".github/skills" / name
    before = validator.tree_bytes(live, ROOT)
    historical = yaml.safe_load((meta / "publication-receipt-legacy-category-TASK-6749.yaml").read_text())
    assert historical["published_manifest"]["full_manifest"] == "validation-legacy-category-TASK-6749.json files"
    managed = json.loads((meta / "validation-legacy-category-TASK-6749.json").read_text())["files"]
    assert {key: managed[key] for key in historical["published_manifest"]["replacements"]} == historical["published_manifest"]["replacements"]
    published = json.loads((meta / "publication-receipt-TASK-6749-R2.json").read_text())
    assert published["operation"] == "authorized_editor_promotion"
    assert published["baseline"]["managed_hash"] == validator.fingerprint(managed)
    assert all(managed[key] == digest for key, digest in published["baseline"]["replaced_file_hashes"].items())
    # Old managed hashes are historical, not the now-published creator revision.
    assert validator.manifest(before) == published["files"] | published["preserved_unmanaged"]
    assert validator.fingerprint(published["files"]) == published["candidate_hash"]
    assert validator.fingerprint(validator.manifest(before)) == published["post_promotion"]["production_physical_hash"]
    removed = sorted(before.keys() - validator.candidate_bytes(meta / "candidate", ROOT, name).keys())
    assert removed == ["scripts/__pycache__/publish_skill.cpython-312.pyc",
                       "scripts/__pycache__/validate_skill.cpython-312.pyc"]
    receipt = validator.validate(ROOT, meta / "candidate", name, "x-ipe-meta")
    with pytest.raises(ValueError, match="dirty or unmanaged"):
        publisher.publish(ROOT, meta / "candidate", name, "x-ipe-meta", validator.manifest(before),
                          managed, receipt["candidate_hash"], apply=False)
    assert validator.tree_bytes(live, ROOT) == before
    with pytest.raises(ValueError, match="Invalid canonical name"):
        publisher.paths(ROOT, "x-ipe-assistant-user-representative-Engineer")
