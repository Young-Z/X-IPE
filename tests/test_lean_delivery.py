"""Reusable delivery preflight scenarios; no claim of live model evaluation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import re

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
NAME = "x-ipe-workflow-task-execution"
SCRIPT = ROOT / f"x-ipe-docs/skill-meta/{NAME}/candidate/scripts/delivery_preflight.py"
spec = importlib.util.spec_from_file_location("delivery_preflight_test", SCRIPT)
preflight = importlib.util.module_from_spec(spec)
exec(compile(SCRIPT.read_bytes(), str(SCRIPT), "exec"), preflight.__dict__)
PYTHON = "x-ipe-tool-implementation-python"
GENERAL = "x-ipe-tool-implementation-general"


@pytest.mark.parametrize(("section", "enabled"), [
    ({}, [GENERAL, PYTHON]),
    ({"_order": 2, "_extra_instruction": "do not execute during design"}, [GENERAL, PYTHON]),
    ({PYTHON: True}, [PYTHON]),
    ({PYTHON: True, GENERAL: False}, [PYTHON]),
    ({GENERAL: False}, []),
    ({PYTHON: False, GENERAL: False}, []),
    ({GENERAL: True}, [GENERAL]),
])
def test_actual_config_eligibility(section, enabled):
    result = preflight.eligible_tools(section, [PYTHON, GENERAL])
    assert result["enabled"] == enabled
    assert set(result["disabled"]) == {PYTHON, GENERAL} - set(enabled)


@pytest.mark.parametrize("section", [None, [], False, {"tool": "true"}, {"tool": 1}, {"tool": None}])
def test_bad_flags_are_errors_not_truthy_enablement(section):
    with pytest.raises(ValueError):
        preflight.eligible_tools(section, [PYTHON, GENERAL])


def create_project(tmp_path):
    for name in (PYTHON, GENERAL):
        entry = tmp_path / f".github/skills/{name}/SKILL.md"
        entry.parent.mkdir(parents=True)
        entry.write_text(f"---\nname: {name}\n---\n")
    config = tmp_path / "x-ipe-docs/config/tools.json"
    config.parent.mkdir(parents=True)
    return config


def configure(path, section):
    path.write_text(json.dumps({"stages": {"implement": {"code_implementation": section}}}))


def test_revisions_invalidate_cached_catalog_and_config(tmp_path):
    config = create_project(tmp_path)
    first = preflight.capabilities(tmp_path, "implement", "code_implementation")
    assert first["config_revision"] is None
    configure(config, {PYTHON: True, GENERAL: False})
    second = preflight.capabilities(tmp_path, "implement", "code_implementation")
    assert second["config_revision"] != first["config_revision"]
    assert second["enabled"] == [PYTHON]
    entry = tmp_path / f".github/skills/{PYTHON}/SKILL.md"
    entry.write_text(entry.read_text() + "New capability\n")
    third = preflight.capabilities(tmp_path, "implement", "code_implementation")
    assert third["catalog_revision"] != second["catalog_revision"]


@pytest.mark.parametrize("raw", ["{", "null", '{"stages": []}', '{"stages":{"implement":null}}'])
def test_malformed_config_never_uses_missing_file_default(tmp_path, raw):
    config = create_project(tmp_path)
    config.write_text(raw)
    with pytest.raises(ValueError):
        preflight.capabilities(tmp_path, "implement", "code_implementation")


def test_unknown_capability_is_not_executed():
    result = preflight.eligible_tools({"uninstalled-tool": True}, [PYTHON])
    assert result["enabled"] == []
    assert result["undiscovered"] == ["uninstalled-tool"]


def test_audit_reports_drift_without_mutation(tmp_path):
    create_project(tmp_path)
    canonical = tmp_path / ".github/copilot-instructions.md"
    canonical.write_text("One owner; approval stays human.\n")
    (tmp_path / "CLAUDE.md").write_text("Every child creates a task.\n")
    mirrored = tmp_path / f".claude/skills/{PYTHON}/SKILL.md"
    mirrored.parent.mkdir(parents=True)
    mirrored.write_text("old skill")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    result = preflight.audit(tmp_path, [PYTHON, GENERAL], [".claude/skills"])
    assert result["skills"][PYTHON]["mirrors"][".claude/skills"]["state"] == "different"
    assert result["skills"][GENERAL]["mirrors"][".claude/skills"]["state"] == "missing"
    assert result["instructions"]["CLAUDE.md"]["state"] == "different"
    assert "not semantic" in result["limits"]
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}


@pytest.mark.parametrize("relative", ["../secret", "/tmp/file", "a/../b", "a//b"])
def test_unsafe_inputs_are_rejected(tmp_path, relative):
    with pytest.raises(ValueError):
        preflight.file_bytes(tmp_path, relative)


def test_symlink_inputs_are_not_followed(tmp_path):
    target = tmp_path / "target"
    target.write_text("private")
    (tmp_path / "linked").symlink_to(target)
    with pytest.raises(ValueError, match="Symlink"):
        preflight.file_bytes(tmp_path, "linked")


def test_cli_json_success_and_explicit_failure(tmp_path):
    config = create_project(tmp_path)
    command = [sys.executable, "-B", str(SCRIPT), "--project-root", str(tmp_path),
               "capabilities", "--stage", "implement", "--action", "code_implementation"]
    configure(config, {PYTHON: True, GENERAL: False})
    success = subprocess.run(command, capture_output=True, text=True)
    assert success.returncode == 0
    assert json.loads(success.stdout)["result"]["enabled"] == [PYTHON]
    configure(config, {PYTHON: "false"})
    failure = subprocess.run(command, capture_output=True, text=True)
    assert failure.returncode == 1
    assert json.loads(failure.stderr)["ok"] is False
    assert not failure.stdout


@pytest.mark.parametrize("suffix", ["python", "typescript", "html5", "java", "mcp", "general"])
def test_tool_operations_preserve_contracts_and_use_affected_verification(suffix):
    name = f"x-ipe-tool-implementation-{suffix}"
    before = (ROOT / f".github/skills/{name}/SKILL.md").read_text()
    after = (ROOT / f"x-ipe-docs/skill-meta/{name}/candidate/SKILL.md").read_text()
    def output(text):
        body = text.split("## Output Result", 1)[1]
        return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", body, re.S)[1])
    assert output(before) == output(after)
    by_name = dict(re.findall(r'<operation name="([^"]+)">(.*?)</operation>', after, re.S))
    assert set(by_name) == {"implement", "fix", "refactor"}
    fix = by_name["fix"]
    refactor = by_name["refactor"]
    assert fix.index("MUST FAIL") < fix.index("IMPLEMENT minimal fix") < fix.index("MUST PASS")
    assert "affected regression selection" in fix
    assert "same preservation selection" in refactor
    assert "baseline tests failing" in refactor
    assert "RUN all tests" not in after and "RUN all existing tests" not in after
    assert "never claim an" in after and "unrun suite passed" in after
    assert "explicit authority" in refactor


def test_all_implementation_routes_share_disablement_contract():
    for suffix in ("technical-design", "code-implementation", "bug-fix",
                   "code-refactor", "human-playground"):
        candidate = ROOT / f"x-ipe-docs/skill-meta/x-ipe-task-based-{suffix}/candidate"
        text = "\n".join(path.read_text() for path in candidate.rglob("*.md"))
        assert "references/capability-routing.md" in text
        assert "Always force-enable general" not in text
        assert "opt-in); force-enable general" not in text
    implementation = (ROOT / "x-ipe-docs/skill-meta/x-ipe-task-based-code-implementation/candidate/SKILL.md").read_text()
    assert "never parallel" not in implementation
    assert "isolated data/environment/cleanup" in implementation


def test_typescript_refactor_uses_declared_test_path():
    candidate = ROOT / "x-ipe-docs/skill-meta/x-ipe-tool-implementation-typescript/candidate/SKILL.md"
    text = candidate.read_text()
    refactor = dict(re.findall(r'<operation name="([^"]+)">(.*?)</operation>', text, re.S))["refactor"]
    assert "npx vitest run {test_code_path}" in refactor
    assert "{test_file}" not in refactor
