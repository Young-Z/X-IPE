"""Legacy category contract regression; all mutations use pytest temp roots.

No prefix monkeypatch, adapted validator, repository publication or board access.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/candidate/scripts"
NAME = "x-ipe+feature+quality-board-management"


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    loaded = []
    for name in ("validate_skill", "publish_skill"):
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        loaded.append(module)
    return loaded


def bundle(root, name=NAME, operations=True):
    candidate = root / "x-ipe-docs/skill-meta" / name / "candidate"
    candidate.mkdir(parents=True)
    action = ("## Operations\n<operation name='generate'><action>Inspect.</action></operation>"
              if operations else "## Execution Procedure\n<procedure name='complete' />")
    data = (
        f"---\nname: {name}\ndescription: Test category compatibility.\n---\n"
        "## Purpose\nInspect.\n## Input Parameters\n### Input Initialization\n"
        "<input_init />\n## Definition of Ready\n<definition_of_ready></definition_of_ready>\n"
        f"{action}\n## Output Result\n```yaml\noperation_output:\n  success: true\n```\n"
        "## Definition of Done\n<definition_of_done></definition_of_done>\n"
    )
    (candidate / "SKILL.md").write_text(data)
    return candidate


def test_exact_legacy_category_operations_pass_without_adaptation(tmp_path, api):
    candidate = bundle(tmp_path)
    receipt = api[0].validate(tmp_path, candidate, NAME, "x-ipe-task-category")
    assert receipt["ok"], receipt["errors"]
    assert not receipt["warnings"]
    assert receipt["files"] == api[0].manifest(api[0].tree_bytes(candidate, tmp_path))


@pytest.mark.parametrize("kind", ["x-ipe-tool", "x-ipe-meta", "x-ipe-task-based", "x-ipe-knowledge"])
def test_legacy_name_is_not_an_alias_for_another_type(tmp_path, api, kind):
    candidate = bundle(tmp_path)
    result = api[0].validate(tmp_path, candidate, NAME, kind)
    assert not result["ok"]
    assert result["errors"] == ["Invalid name or subtype identity"]


@pytest.mark.parametrize("name", [
    "x-ipe+feature+quality-board-management-copy", "x-ipe+all+quality-board-management",
    "x-ipe+feature+other", "x-ipe+feature-stage+release",
])
def test_no_generic_operations_exemption_for_category_names(tmp_path, api, name):
    candidate = bundle(tmp_path, name)
    result = api[0].validate(tmp_path, candidate, name, "x-ipe-task-category")
    assert not result["ok"]
    assert "Missing contract section: Execution Procedure" in result["errors"]
    assert "Missing contract block: <procedure" in result["errors"]


def test_ordinary_category_procedure_still_passes(tmp_path, api):
    name = "x-ipe+feature-stage+release"
    candidate = bundle(tmp_path, name, operations=False)
    assert api[0].validate(tmp_path, candidate, name, "x-ipe-task-category")["ok"]


@pytest.mark.parametrize("mutation,error", [
    (lambda text: text.replace("## Operations", "## Other"), "Missing contract section: Operations"),
    (lambda text: text.replace("<operation ", "<operation_fake "), "Missing contract block: <operation"),
    (lambda text: text.replace("<input_init />", "<input_fake />"), "Missing contract block: <input_init"),
    (lambda text: text.replace("description: Test category compatibility.", "description: ''"), "Frontmatter description"),
    (lambda text: text + "\n[missing](references/missing.md)\n", "Broken resource"),
    (lambda text: text + "\n" + "padding\n" * 1001, "maximum is 1000"),
])
def test_legacy_exception_retains_other_validation_gates(tmp_path, api, mutation, error):
    candidate = bundle(tmp_path)
    path = candidate / "SKILL.md"
    path.write_text(mutation(path.read_text()))
    result = api[0].validate(tmp_path, candidate, NAME, "x-ipe-task-category")
    assert not result["ok"]
    assert any(error in item for item in result["errors"])


def test_actual_reporter_candidate_api_cli_agree(api):
    candidate = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
    result = api[0].validate(ROOT, candidate, NAME, "x-ipe-task-category")
    command = [sys.executable, "-B", str(SCRIPTS / "validate_skill.py"),
               "--project-root", str(ROOT), "--candidate", str(candidate),
               "--name", NAME, "--type", "x-ipe-task-category"]
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    assert result == json.loads(run.stdout)
    assert result["ok"] and len(result["files"]) == 7
    assert result["body_lines"] == 259
    assert result["errors"] == result["warnings"] == []


def test_publisher_uses_category_validation_and_preserves_unmanaged(tmp_path, api):
    candidate = bundle(tmp_path)
    target = tmp_path / ".github/skills" / NAME
    target.mkdir(parents=True)
    old = (candidate / "SKILL.md").read_bytes().replace(b"Inspect.", b"Original.")
    (target / "SKILL.md").write_bytes(old)
    (target / "user-owned.txt").write_bytes(b"never adopt or delete")
    baseline = api[0].manifest(api[0].tree_bytes(target, tmp_path))
    managed = {"SKILL.md": baseline["SKILL.md"]}
    validated = api[0].validate(tmp_path, candidate, NAME, "x-ipe-task-category")
    assert validated["ok"], validated["errors"]
    options = dict(project_root=tmp_path, candidate=candidate, name=NAME,
                   skill_type="x-ipe-task-category", baseline=baseline, managed=managed,
                   expected_candidate_hash=validated["candidate_hash"])
    with pytest.raises(ValueError, match="dirty or unmanaged"):
        api[1].publish(**options)
    assert (target / "user-owned.txt").read_bytes() == b"never adopt or delete"
    (candidate / "user-owned.txt").write_bytes(b"never adopt or delete")
    options["expected_candidate_hash"] = api[0].validate(
        tmp_path, candidate, NAME, "x-ipe-task-category")["candidate_hash"]
    plan = api[1].publish(**options)
    assert plan["ok"], plan
    published = api[1].publish(**options, apply=True)
    assert published["ok"], published
    assert api[0].tree_bytes(target, tmp_path) == api[0].tree_bytes(candidate, tmp_path)


def yaml_block(text, heading):
    import re
    return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", text.split(heading, 1)[1], re.S)[1])


def test_reporter_original_model_and_operation_envelope_unchanged():
    live = ROOT / ".github/skills" / NAME
    candidate = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
    for heading in ("## Input Parameters", "## Output Result"):
        assert yaml_block((live / "SKILL.md").read_text(), heading) == yaml_block(
            (candidate / "SKILL.md").read_text(), heading)
    model = "references/quality-evaluation-data-model.yaml"
    assert (live / model).read_bytes() == (candidate / model).read_bytes()


def test_unmeasured_outcome_does_not_erase_known_engineering_scores():
    candidate = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
    text = (candidate / "references/goal-reporting.md").read_text()
    assert "Numeric rubric evaluation remains independent of these narrative states" in text
    assert "preserve unrelated established engineering evidence" in text
    assert "Missing\nevidence does not justify zero, ten, null" in text
    example = (candidate / "references/examples.md").read_text()
    result = yaml_block(example, "## 3. Missing evidence")["operation_output"]
    assert set(result) == {"success", "operation", "result", "errors"}
    assert result["success"] is False and result["result"] == {}
    assert result["errors"][0].startswith("EVALUATION_INCOMPLETE:")


def test_prior_creator_receipt_remains_valid_managed_provenance(api):
    receipt = yaml.safe_load((ROOT / "x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/promotion-receipt.yaml").read_text())
    assert receipt["ok"] and receipt["state"] == "published"
    assert api[0].fingerprint(receipt["published_files"]) == receipt["post_promotion"]["production_hash"]