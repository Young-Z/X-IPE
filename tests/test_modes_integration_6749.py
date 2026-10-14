"""Current candidate contract + actual mode persistence; no agent-pilot claim.

Production and historical publication assertions remain in the original suites.
These checks do not declare revised candidates published or approve own edits.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from tests.test_skill_pipeline_refactor import output_contract
from tests.publication_recovery_6749 import resource_inventory
from tests.skill_validation_harness_6749 import load_source, validation_project

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
    return load_source(path, name)


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
        with validation_project(validator, ROOT, candidate, name) as (project, copied):
            api = validator.validate(project, copied, name, kind)
            assert api["ok"], api["errors"]
            process = subprocess.run([sys.executable, str(script), "--project-root", str(project),
                                      "--candidate", str(copied), "--name", name, "--type", kind],
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
    assert resource_inventory(live) == published["files"]
    assert validator.fingerprint(published["files"]) == published["candidate_hash"]
    # Preserve the historical physical receipt, but do not mistake regenerated
    # interpreter caches for immutable published content. This call must still
    # leave every current physical byte (including caches) untouched.
    assert validator.fingerprint(published["files"] | published["preserved_unmanaged"]) == published["post_promotion"]["production_physical_hash"]
    with validation_project(validator, ROOT, meta / "candidate", name) as (project, candidate):
        target = project / ".github/skills" / name
        # Generate genuine caches under normal interpreter defaults, only in
        # the disposable live tree. They are not managed publication resources.
        process = subprocess.run([sys.executable, "-c",
                                  "import sys; sys.path.insert(0, sys.argv[1]); import publish_skill",
                                  str(target / "scripts")], capture_output=True, text=True,
                                 env={key: value for key, value in os.environ.items()
                                      if key != "PYTHONDONTWRITEBYTECODE"})
        assert process.returncode == 0, process.stdout + process.stderr
        physical = validator.tree_bytes(target, project)
        expected_caches = {Path(importlib.util.cache_from_source(str(target / "scripts" / filename)))
                           .relative_to(target).as_posix()
                           for filename in ("publish_skill.py", "validate_skill.py")}
        assert expected_caches <= physical.keys()
        assert resource_inventory(target) == published["files"]
        removed = physical.keys() - validator.candidate_bytes(candidate, project, name).keys()
        assert removed == expected_caches
        receipt = validator.validate(project, candidate, name, "x-ipe-meta")
        assert receipt["ok"], receipt["errors"]
        for apply in (False, True):
            with pytest.raises(ValueError, match="dirty or unmanaged"):
                publisher.publish(project, candidate, name, "x-ipe-meta", validator.manifest(physical),
                                  managed, receipt["candidate_hash"], apply=apply)
            assert validator.tree_bytes(target, project) == physical
    assert validator.tree_bytes(live, ROOT) == before
    with pytest.raises(ValueError, match="Invalid canonical name"):
        publisher.paths(ROOT, "x-ipe-assistant-user-representative-Engineer")
