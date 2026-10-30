"""Single-loop policy contracts and real workflow transitions in disposable projects.

Text checks catch instruction regressions; they do not measure model behavior,
token consumption, or latency.
"""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pytest
import yaml

from x_ipe.services.workflow_manager_service import WorkflowManagerService, _default_config


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".github"
if not SOURCE.exists():
    SOURCE = ROOT / ".github_to_be_refactor"
CORE = (
    "ideation", "idea-mockup", "idea-to-architecture", "share-idea",
    "requirement-gathering", "feature-breakdown", "feature-refinement",
    "technical-design", "code-implementation", "feature-acceptance-test",
    "code-refactor", "feature-closing",
)


def candidate(name):
    return ROOT / "x-ipe-docs/skill-meta" / name / "candidate"


def output(path):
    section = path.read_text().split("## Output Result", 1)[1]
    return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", section, re.S)[1])


@pytest.mark.parametrize("suffix", CORE)
def test_core_skills_share_loop_and_preserve_outputs(suffix):
    name = "x-ipe-task-based-" + suffix
    text = (candidate(name) / "SKILL.md").read_text()
    assert "references/agent-loop.md" in text
    for obsolete in (
        "schedule_dod_checks_with_sub_agent_before_starting",
        "Use a sub-agent to validate DoD",
        'type: "routing"', "Invoke sub-agent",
        "<phase_0", "<phase_6", "task_create.py", "task_update.py",
    ):
        assert obsolete not in text, (name, obsolete)
    original = output(SOURCE / "skills" / name / "SKILL.md")
    proposed = output(candidate(name) / "SKILL.md")
    assert original.keys() == proposed.keys()
    before = original["task_completion_output"]
    after = proposed["task_completion_output"]
    assert before.keys() == after.keys()
    for key in ("category", "process_preference", "next_task_based_skill"):
        assert before[key] == after[key]
    procedure = re.search(r"<procedure\b.*?</procedure>", text, re.S)
    assert procedure
    xml = ET.fromstring(procedure[0])
    for step in (node for node in xml.iter() if re.fullmatch(r"step_\d+(?:_\d+)?", node.tag)):
        assert len(step.findall("action")) == 1


def test_shared_policy_has_ten_migration_scenarios():
    policy = (candidate("x-ipe-workflow-task-execution") / "references/agent-loop.md").read_text()
    for scenario in (
        "Small feature", "Independent research", "Context degradation",
        "Permission boundary", "Clear requirements", "Changed acceptance",
        "Unchanged acceptance", "Low-risk documentation", "High-risk change",
        "No refactoring need",
    ):
        assert scenario in policy
    assert "not measured" in policy
    assert "same agent" in policy


@pytest.mark.parametrize("path", [
    "x-ipe-docs/config/workflow-template.json",
    "src/x_ipe/resources/config/workflow-template.json",
])
def test_template_refactoring_is_optional_but_acceptance_is_not(path):
    template = json.loads((ROOT / path).read_text())
    actions = template["stages"]["validation"]["actions"]
    assert actions["code_refactor"]["optional"] is True
    assert actions["acceptance_testing"]["optional"] is False
    assert actions["feature_closing"]["optional"] is False
    assert actions["acceptance_testing"]["next_actions_suggested"] == ["feature_closing", "code_refactor"]


def test_fallback_matches_optional_refactoring_policy():
    stages, _, _, suggestions = _default_config()
    assert stages["validation"]["mandatory_actions"] == ["acceptance_testing", "feature_closing"]
    assert stages["validation"]["optional_actions"] == ["code_refactor"]
    assert suggestions["acceptance_testing"] == ["feature_closing", "code_refactor"]


@pytest.fixture
def ready_feature(tmp_path):
    service = WorkflowManagerService(str(tmp_path))
    name, feature = "single-loop", "FEATURE-100-A"
    assert service.create_workflow(name)["success"]
    for action in ("compose_idea", "requirement_gathering", "feature_breakdown"):
        assert service.update_action_status(name, action, "done")["success"]
    assert service.add_features(name, [{"id": feature, "name": "Small feature", "depends_on": []}])["success"]
    for action in ("feature_refinement", "technical_design", "implementation"):
        assert service.update_action_status(name, action, "done", feature_id=feature)["success"]
    return service, name, feature


def test_real_workflow_closes_without_refactor_or_fake_skip(ready_feature):
    service, name, feature = ready_feature
    assert service.update_action_status(name, "acceptance_testing", "done", feature_id=feature)["success"]
    assert service.update_action_status(name, "feature_closing", "done", feature_id=feature)["success"]
    state = service.get_workflow(name)
    lane = next(item for item in state["features"] if item["feature_id"] == feature)
    # The service initializes optional actions as skipped, without an agent write.
    assert lane["validation"]["actions"]["code_refactor"]["status"] == "skipped"
    assert lane["validation"]["actions"]["code_refactor"]["optional"] is True
    assert service._is_feature_stage_done(state, feature, "validation")
    assert service._is_feature_stage_ready_to_unlock(state, lane, "feedback")
    assert service.get_next_action(name).get("action") != "code_refactor"


def test_missing_acceptance_still_blocks_validation_completion(ready_feature):
    service, name, feature = ready_feature
    service.update_action_status(name, "feature_closing", "done", feature_id=feature)
    state = service.get_workflow(name)
    lane = next(item for item in state["features"] if item["feature_id"] == feature)
    assert lane["validation"]["status"] != "completed"
    assert lane["feedback"]["status"] == "locked"


@pytest.mark.parametrize("status", ["pending", "in_progress", "done"])
def test_existing_workflow_adopts_optional_flag_without_rewriting_history(ready_feature, tmp_path, status):
    service, name, feature = ready_feature
    path = tmp_path / "x-ipe-docs/engineering-workflow" / f"workflow-{name}.json"
    state = json.loads(path.read_text())
    action = state["features"][0]["validation"]["actions"]["code_refactor"]
    action.pop("optional", None)
    action["status"] = status
    path.write_text(json.dumps(state))
    refreshed = service.get_workflow(name)
    actual = refreshed["features"][0]["validation"]["actions"]["code_refactor"]
    assert actual["optional"] is True
    assert actual["status"] == status
