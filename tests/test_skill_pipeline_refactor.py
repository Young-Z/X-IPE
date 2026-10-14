"""Lean skill pipeline contracts; no production writes or agent-behavior claims.

Requirement tests inspect the candidate (not an unpromoted production entry).
Installed workflow CLIs run only with a temporary project as cwd. Negative
helper behavior is characterized honestly, not patched into a pretend gate.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
NAME = "x-ipe-task-based-requirement-gathering"
META = ROOT / "x-ipe-docs" / "skill-meta" / NAME
CANDIDATE = META / "candidate"
PRODUCTION = ROOT / ".github" / "skills" / NAME
CREATOR = ROOT / ".github" / "skills" / "x-ipe-meta-skill-creator" / "scripts"
APP = ROOT / ".github" / "skills" / "x-ipe-tool-x-ipe-app-interactor" / "scripts"
MODES = (
    "interact-with-human",
    "dao-represent-human-to-interact",
    "dao-represent-human-to-interact-for-questions-in-skill",
)


def load_validator():
    spec = importlib.util.spec_from_file_location("pipeline_validator", CREATOR / "validate_skill.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def output_contract(path):
    text = path.read_text(encoding="utf-8").split("## Output Result", 1)[1]
    match = re.search(r"```yaml\n(.*?)\n```", text, re.S)
    assert match is not None
    return yaml.safe_load(match[1])["task_completion_output"]


def run_helper(project, script, *args):
    result = subprocess.run(
        [sys.executable, "-B", str(APP / script), *args],
        cwd=project, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True, capture_output=True, check=False,
    )
    assert result.stdout.strip(), result.stderr
    return result, json.loads(result.stdout)


@pytest.fixture
def entry():
    return (CANDIDATE / "SKILL.md").read_text(encoding="utf-8")


@pytest.fixture
def helper_project(tmp_path):
    config = tmp_path / "x-ipe-docs" / "config"
    config.mkdir(parents=True)
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    (config / "workflow-template.json").write_text(json.dumps(template), encoding="utf-8")
    requirements = tmp_path / "x-ipe-docs" / "requirements"
    (requirements / "EPIC-061" / "mockups").mkdir(parents=True)
    (requirements / "requirement-details.md").write_text(
        "# Requirement Summary\n\n## EPIC-061: Status badge\n\nRead-only badge for operators.\n",
        encoding="utf-8",
    )
    ideas = tmp_path / "x-ipe-docs" / "ideas"
    ideas.mkdir()
    (ideas / "refined-idea.md").write_text("# Status badge\nApproved read-only scope.\n", encoding="utf-8")
    state = {
        "schema_version": "3.0", "name": "pilot", "current_stage": "requirement",
        "global": {"process_preference": {"interaction_mode": MODES[0]}},
        "shared": {
            "ideation": {
                "status": "completed",
                "actions": {name: {"status": "done", "deliverables": {}}
                            for name in template["stages"]["ideation"]["actions"]},
            },
            "requirement": {
                "status": "in_progress",
                "actions": {
                    "requirement_gathering": {"status": "in_progress", "deliverables": {},
                                              "context": {"refined-idea": "x-ipe-docs/ideas/refined-idea.md"}},
                    "feature_breakdown": {"status": "pending", "deliverables": {}},
                },
            },
        },
        "features": [],
    }
    workflow = tmp_path / "x-ipe-docs" / "engineering-workflow"
    workflow.mkdir()
    state_path = workflow / "workflow-pilot.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    return tmp_path, state_path


def test_requirement_candidate_deterministic_validation():
    receipt = load_validator().validate(ROOT, CANDIDATE, NAME, "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    assert 200 <= receipt["body_lines"] <= 300
    assert set(receipt["files"]) == {
        "SKILL.md", "references/examples.md", "references/file-splitting.md",
        "references/requirement-details-template.md", "templates/requirement-details.md",
        "references/context-review.md",
    }


def test_requirement_output_schema_preserved():
    original = output_contract(PRODUCTION / "SKILL.md")
    proposed = output_contract(CANDIDATE / "SKILL.md")
    assert list(proposed) == list(original)
    for field in ("category", "status", "next_task_based_skill", "process_preference",
                  "execution_mode", "workflow", "workflow_action", "epic_id"):
        assert proposed[field] == original[field]
    assert proposed["next_task_based_skill"][0]["skill"] == "x-ipe-task-based-feature-breakdown"


def test_requirement_single_lifecycle_and_no_child_mutations(entry):
    assert entry.count(
        ".github/skills/x-ipe-workflow-task-execution/references/lifecycle.md"
    ) == 1
    assert "Orient/Plan" in entry and "without recursively dispatching" in entry
    for obsolete in ("task_create.py", "task_update.py", "phase_0", "phase_6",
                     'type: "routing"', "git add", "Execute Next Action",
                     "schedule_dod_checks_with_sub_agent_before_starting"):
        assert obsolete not in entry


@pytest.mark.parametrize("field", [
    "task_id", "task_based_skill", "execution_mode", "workflow.name", "workflow.action",
    "process_preference.interaction_mode", "workflow.extra_context_reference", "epic_id",
    "mockup_list", "document_language", "requirement_context",
])
def test_requirement_nontrivial_inputs_initialized(entry, field):
    block = re.search(r"<input_init>.*?</input_init>", entry, re.S)
    assert block is not None
    init = ET.fromstring(block[0])
    assert field in {item.attrib["name"] for item in init.findall("field")}


@pytest.mark.parametrize("mode", MODES)
def test_requirement_modes_and_authority_preserved(entry, mode):
    assert mode in entry
    assert "human asks the human within skill and waits" in entry
    assert "full DAO and hybrid receive bounded representative guidance" in entry
    assert "guidance cannot supply missing human authority" in entry
    assert "Human and hybrid require human requirements review and completion/route confirmation" in entry


def test_requirement_delta_freshness_risk_and_contracts(entry):
    review = (CANDIDATE / "references/context-review.md").read_text()
    for clause in ("Small compatible", "Standard new", "CR intake", "SHA256",
                   "Removed parts/index targets", "compare the current delta against ALL",
                   "no baseline exists", "timestamp", "independent review"):
        assert clause in review
    for clause in ("3-5 per batch", "Unresolved material ambiguity blocks", "EN/ZH",
                   "security, public API, data/destructive", "metadata-only configuration",
                   "FEATURE-{nnn}-{X}", "legacy FEATURE-{nnn}", "[RETIRED by EPIC-{nnn}]",
                   "Preserve unrelated FRs/ACs", "avoid duplicate markers on resume"):
        assert clause in entry


def test_requirement_resources_do_not_reintroduce_orchestration():
    resources = "\n".join(path.read_text() for path in CANDIDATE.rglob("*.md")
                          if path.name != "SKILL.md")
    for obsolete in ('type: "routing"', "task_create.py", "task_update.py",
                     "Execute Next Action", "always ask human", "part-6 has 473 lines → create"):
        assert obsolete not in resources
    assert "does NOT justify workflow_action_updated true" in resources
    assert "Neither simulates an" in resources


@pytest.mark.parametrize("heading", [
    "Project Overview", "User Request", "Clarifications", "High-Level Requirements",
    "Acceptance Criteria", "Scope", "Constraints", "Feasibility and Risks", "Related Features",
    "Impact Updates", "Open Questions", "Linked Mockups", "Context and Verification Evidence",
    "Outcome / Goal Frame", "Requirement Mapping",
])
def test_requirement_canonical_template_domain_fields(heading):
    template = (CANDIDATE / "references/requirement-details-template.md").read_text()
    assert f"### {heading}" in template
    compat = (CANDIDATE / "templates/requirement-details.md").read_text()
    assert "references/requirement-details-template.md" in compat


def test_requirement_split_boundary_and_links_are_consistent(entry):
    split = (CANDIDATE / "references/file-splitting.md").read_text()
    assert "473 and 500" in split and "501 requires a split" in split
    assert "highest\n   integer X, not lexicographic order" in split
    assert "repair links affected by first rename" in entry
    assert "inbound links affected by the first rename" in split
    assert "Never put\nan EPIC ID in a Feature ID column" in entry
    for target in load_validator().markdown_targets(split):
        assert target.startswith("x-ipe-docs/requirements/")


def test_requirement_app_and_prompt_consumers():
    config = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    stage = config["stages"]["requirement"]
    action = stage["actions"]["requirement_gathering"]
    assert stage["type"] == "shared" and action["optional"] is False
    assert action["deliverables"] == ["$output:requirement-doc", "$output-folder:requirements-folder"]
    assert action["action_context"]["refined-idea"]["required"] is True
    assert action["action_context"]["mockup-html"]["required"] is False
    script = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"requirement_gathering:.*skill: '" + NAME + "'", script)
    prompts = json.loads((ROOT / "x-ipe-docs/config/copilot-prompt.json").read_text())
    gathering = next(item for item in prompts["workflow-prompts"]
                     if item["action"] == "requirement_gathering")
    assert {item["language"] for item in gathering["prompt-details"]} == {"en", "zh"}
    assert all("$output:refined-idea$" in item["command"] for item in gathering["prompt-details"])
    tools = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())
    assert "gathering" in tools["stages"]["requirement"]
    assert not [key for key, enabled in tools["stages"]["requirement"]["gathering"].items()
                if not key.startswith("_") and enabled is True]


@pytest.mark.parametrize("active", ["requirement-details.md", "requirement-details-part-2.md"])
def test_requirement_real_helper_write_and_readback(helper_project, active):
    project, state_path = helper_project
    folder = project / "x-ipe-docs/requirements"
    if active != "requirement-details.md":
        (folder / "requirement-details.md").rename(folder / active)
    links = {"requirement-doc": f"x-ipe-docs/requirements/{active}",
             "requirements-folder": "x-ipe-docs/requirements"}
    before = json.loads(state_path.read_text())
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                                 "--action", "requirement_gathering", "--status", "done",
                                 "--deliverables", json.dumps(links), "--format", "json")
    assert result.returncode == 0 and payload["success"] is True
    read, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot", "--format", "json")
    assert read.returncode == 0
    action = state["shared"]["requirement"]["actions"]["requirement_gathering"]
    assert action["status"] == "done" and action["deliverables"] == links
    assert (project / links["requirement-doc"]).is_file()
    assert (project / links["requirements-folder"]).is_dir()
    assert state["shared"]["ideation"] == before["shared"]["ideation"]
    assert state["shared"]["requirement"]["actions"]["feature_breakdown"]["status"] == "pending"
    assert state["features"] == []
    unchanged = state_path.read_bytes()
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    assert state_path.read_bytes() == unchanged  # resume evidence is read-only, not a replay


@pytest.mark.parametrize("bad_links", [
    {"requirement-doc": "x-ipe-docs/requirements/requirement-details.md", "extra": "not-a-tag"},
    {"requirement-doc": "x-ipe-docs/requirements/requirement-details.md", "requirements-folder": ["x-ipe-docs/requirements"]},
])
def test_requirement_helper_rejects_extra_tags_and_folder_arrays(helper_project, bad_links):
    project, state_path = helper_project
    before = state_path.read_bytes()
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                                 "--action", "requirement_gathering", "--status", "done",
                                 "--deliverables", json.dumps(bad_links))
    assert result.returncode != 0 and payload["error"] == "INVALID_DELIVERABLES"
    assert state_path.read_bytes() == before


def test_requirement_helper_missing_tags_are_not_domain_success(helper_project, entry):
    project, state_path = helper_project
    links = {"requirement-doc": "x-ipe-docs/requirements/does-not-exist.md"}
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                                 "--action", "requirement_gathering", "--status", "done",
                                 "--deliverables", json.dumps(links))
    assert result.returncode == 0 and payload["success"] is True  # characterized existing gap
    action = json.loads(state_path.read_text())["shared"]["requirement"]["actions"]["requirement_gathering"]
    assert "requirements-folder" not in action["deliverables"]
    assert not (project / links["requirement-doc"]).exists()
    assert "Writer success alone is insufficient" in entry
    assert "missing or invalid artifacts" in entry


@pytest.mark.parametrize("failure", ["missing-workflow", "missing-action", "locked-prerequisite"])
def test_requirement_helper_error_keeps_state(helper_project, failure):
    project, state_path = helper_project
    state = json.loads(state_path.read_text())
    if failure == "missing-action":
        del state["shared"]["requirement"]["actions"]["requirement_gathering"]
    elif failure == "locked-prerequisite":
        state["shared"]["requirement"]["status"] = "locked"
        state["shared"]["ideation"]["status"] = "in_progress"
        for action in state["shared"]["ideation"]["actions"].values():
            action["status"] = "pending"
    state_path.write_text(json.dumps(state))
    before = state_path.read_bytes()
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow",
                                 "missing" if failure == "missing-workflow" else "pilot",
                                 "--action", "requirement_gathering", "--status", "done")
    assert result.returncode != 0
    assert payload["error"] == {
        "missing-workflow": "FILE_NOT_FOUND", "missing-action": "ACTION_NOT_FOUND",
        "locked-prerequisite": "STAGE_LOCKED",
    }[failure]
    assert state_path.read_bytes() == before


def test_requirement_candidate_resources_superset_of_production():
    live = {p.relative_to(PRODUCTION) for p in PRODUCTION.rglob("*") if p.is_file()}
    proposed = {p.relative_to(CANDIDATE) for p in CANDIDATE.rglob("*") if p.is_file()}
    assert live <= proposed


BREAKDOWN_NAME = "x-ipe-task-based-feature-breakdown"
BREAKDOWN_META = ROOT / "x-ipe-docs/skill-meta" / BREAKDOWN_NAME
BREAKDOWN = BREAKDOWN_META / "candidate"
BREAKDOWN_LIVE = ROOT / ".github/skills" / BREAKDOWN_NAME
BOARD = ROOT / ".github/skills/x-ipe-tool-task-board-manager/scripts"


def run_board(project, script, *args):
    result = subprocess.run(
        [sys.executable, "-B", str(BOARD / script), *args], cwd=project,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True, capture_output=True, check=False,
    )
    return result, json.loads(result.stdout if result.returncode == 0 else result.stderr)


def feature_record(feature_id="FEATURE-061-A", epic_id="EPIC-061", **updates):
    record = {"feature_id": feature_id, "epic_id": epic_id, "title": "Status Badge",
              "version": "v1.0", "status": "Planned", "description": "Runnable badge",
              "dependencies": []}
    return {**record, **updates}


@pytest.fixture
def breakdown_entry():
    return (BREAKDOWN / "SKILL.md").read_text()


@pytest.fixture
def breakdown_project(helper_project):
    project, state_path = helper_project
    state = json.loads(state_path.read_text())
    state["shared"]["requirement"]["actions"]["requirement_gathering"].update({
        "status": "done", "deliverables": {
            "requirement-doc": "x-ipe-docs/requirements/requirement-details.md",
            "requirements-folder": "x-ipe-docs/requirements"}})
    state_path.write_text(json.dumps(state))
    document = project / "x-ipe-docs/requirements/requirement-details.md"
    document.write_text(document.read_text() +
                        "\n## Feature List\n\n| Feature ID | Epic ID | Title |\n"
                        "| --- | --- | --- |\n| FEATURE-061-A | EPIC-061 | Status Badge |\n"
                        "\n### FEATURE-061-A: Status Badge\n"
                        "MVP: operators can read current status.\nAC: badge reflects state.\n")
    (project / "x-ipe-docs/requirements/EPIC-061/FEATURE-061-A").mkdir()
    return project, state_path


def breakdown_links(active="requirement-details.md"):
    return {"features-list": f"x-ipe-docs/requirements/{active}",
            "breakdown-folder": "x-ipe-docs/requirements"}


def write_breakdown(project, features, links=None):
    args = ["--workflow", "pilot", "--action", "feature_breakdown", "--status", "done",
            "--features", json.dumps(features)]
    if links is not None:
        args += ["--deliverables", json.dumps(links)]
    return run_helper(project, "workflow_update_action.py", *args)


def test_breakdown_deterministic_complete_and_production_preserved():
    validator = load_validator()
    receipt = validator.validate(ROOT, BREAKDOWN, BREAKDOWN_NAME, "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    assert 200 <= receipt["body_lines"] <= 300
    baseline = json.loads((BREAKDOWN_META / "baseline.json").read_text())
    live = validator.manifest(validator.tree_bytes(BREAKDOWN_LIVE, ROOT))
    promotion_path = BREAKDOWN_META / "promotion-receipt-TASK-6749.json"
    if promotion_path.exists():
        promotion = json.loads(promotion_path.read_text())
        assert promotion["publication_state"] == "published"
        published = json.loads((BREAKDOWN_META / "validation-receipt-promotion-TASK-6749.json").read_text())
        assert validator.fingerprint(published["files"]) == promotion["production_hash"]
        assert published["files"] == json.loads((BREAKDOWN_META / "baseline-goal-TASK-6749.json").read_text())
        assert validator.fingerprint(baseline) == promotion["baseline_hash"]
    else:
        assert live == baseline
    assert set(receipt["files"]) == set(baseline) | {"references/integration.md"}
    # A fresh candidate delta is not the already-published revision. Keep the
    # old publication checks above; verify fresh live preservation separately.
    fresh = json.loads((BREAKDOWN_META / "baseline-goal-TASK-6749.json").read_text())
    from tests.test_goal_oriented_skills import assert_reviewed_live
    assert_reviewed_live(BREAKDOWN_NAME, live, fresh)
    retained = (BREAKDOWN / "templates/specification.md").read_text()
    original = (BREAKDOWN_LIVE / "templates/specification.md").read_text()
    for section in re.findall(r"^## (.+)$", original, re.M):
        assert f"## {section}\n" in retained
    assert "Criterion (Given/When/Then)" in retained


def test_breakdown_original_output_contract_preserved():
    old = output_contract(BREAKDOWN_LIVE / "SKILL.md")
    new = output_contract(BREAKDOWN / "SKILL.md")
    assert list(new) == list(old)
    for key in ("category", "status", "next_task_based_skill", "process_preference",
                "execution_mode", "workflow", "workflow_action", "requirement_details_part",
                "parent_features_removed", "dedup_gaps", "linked_mockups"):
        assert new[key] == old[key]


@pytest.mark.parametrize("field", [
    "task_id", "task_based_skill", "execution_mode", "workflow.name", "workflow.action",
    "process_preference.interaction_mode", "workflow.extra_context_reference.requirement-doc",
    "requirement_doc", "mockup_list", "breakdown_context", "epic_context", "document_language",
])
def test_breakdown_input_initialization(breakdown_entry, field):
    block = re.search(r"<input_init>.*?</input_init>", breakdown_entry, re.S)
    assert block is not None
    assert field in {item.attrib["name"] for item in ET.fromstring(block[0]).findall("field")}


def test_breakdown_single_owner_all_modes_and_no_stale_resources(breakdown_entry):
    text = "\n".join(p.read_text() for p in BREAKDOWN.rglob("*.md")
                     if p.name != "specification.md")
    for mode in MODES:
        assert mode in breakdown_entry
    assert "human asks the human within skill and waits" in breakdown_entry
    assert "full DAO and hybrid receive bounded guidance" in breakdown_entry
    assert "without recursively dispatching" in breakdown_entry
    assert breakdown_entry.count("x-ipe-workflow-task-execution/references/lifecycle.md") == 1
    for obsolete in ('type: "routing"', "phase_0", "phase_6", "Execute Next Action",
                     "x-ipe+feature+feature-board-management", "x-ipe+all+task-board-management",
                     "status \"Draft\"", "requirements/features.md"):
        assert obsolete not in text
    # Forbidden link examples in prose are safeguards, not generated relative links.
    for path in BREAKDOWN.rglob("*.md"):
        for target in load_validator().markdown_targets(path.read_text()):
            assert not target.startswith(("../", "./", "/")), (path, target)
    for task_mutation in ("task_create.py", "task_update.py", "task_ensure.py", "git add"):
        assert task_mutation not in breakdown_entry


def test_breakdown_domain_delta_mvp_identity_dependencies(breakdown_entry):
    guidelines = (BREAKDOWN / "references/breakdown-guidelines.md").read_text()
    for clause in ("SHA256", "team boundaries", "8-15", "More than 20", "3-7",
                   "<=50 words", "FEATURE-{nnn}", "FEATURE-{nnn}-{X}", "EPIC-{nnn}",
                   "historic gaps", "v1.1/v1.2", "direct", "cross-Epic", "DAG",
                   "partial", "Retired", "history", "project-root-relative"):
        assert clause.lower() in guidelines.lower()
    for clause in ("Single-feature lightweight", "Incremental CR", "vertical runnable",
                   "stable IDs", "specifications", "owning requirement part", "EN/ZH",
                   "explicit", "blocked", "independent review"):
        assert clause in breakdown_entry


def test_breakdown_confirmation_and_truthful_conditional_gates(breakdown_entry):
    assert "human and hybrid require human completion/route confirmation" in breakdown_entry
    assert "this exact list/revision" in breakdown_entry
    assert "material edits invalidate it" in breakdown_entry
    assert "Return unresolved confirmation as blocked" in breakdown_entry
    assert "Free-mode makes no app write and returns workflow_action_updated false" in breakdown_entry
    assert "not helper success or skipped flags" in breakdown_entry
    patterns = (BREAKDOWN / "references/patterns.md").read_text()
    assert "Retired via feature_update.py" in patterns
    assert "do not\ndelete a board record" in patterns
    assert "never truncate the overall list to seven" in patterns
    assert "remove parent from board" not in patterns


def test_breakdown_templates_are_consolidated_truthful_artifacts():
    table = (BREAKDOWN / "templates/features.md").read_text()
    assert "Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency" in table
    assert "<=50 words" in table and "NOT the JSON" in table
    detail = (BREAKDOWN / "templates/requirement-details.md").read_text()
    for heading in ("Epic Assessment", "Feature List", "Feature Details", "Coverage",
                    "Context and Integration Evidence"):
        assert heading in detail
    for clause in ("features-list", "breakdown-folder", "Planned", "Retired",
                   "id/name/depends_on", "APPENDS", "MISSING_FEATURES", "writer exit alone",
                   "data.pagination", "data.feature", "Corrupt"):
        assert clause in (BREAKDOWN / "references/integration.md").read_text()


def test_breakdown_actual_action_and_prompt_contract():
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["requirement"]["actions"]["feature_breakdown"]
    bundled_template = json.loads((ROOT / "src/x_ipe/resources/config/workflow-template.json").read_text())
    assert action == bundled_template["stages"]["requirement"]["actions"]["feature_breakdown"]
    assert template["stages"]["requirement"]["type"] == "shared"
    assert action["optional"] is False
    assert action["action_context"]["requirement-doc"]["required"] is True
    assert action["deliverables"] == ["$output:features-list", "$output-folder:breakdown-folder"]
    script = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"feature_breakdown:.*skill: '" + BREAKDOWN_NAME + "'", script)
    prompts = json.loads((ROOT / "x-ipe-docs/config/copilot-prompt.json").read_text())
    prompt = next(p for p in prompts["workflow-prompts"] if p["action"] == "feature_breakdown")
    bundled_prompts = json.loads((ROOT / "src/x_ipe/resources/config/copilot-prompt.json").read_text())
    assert prompt == next(p for p in bundled_prompts["workflow-prompts"]
                          if p["action"] == "feature_breakdown")
    assert {p["language"] for p in prompt["prompt-details"]} == {"en", "zh"}
    assert all("$output:requirement-doc$" in p["command"] for p in prompt["prompt-details"])


@pytest.mark.parametrize("active", ["requirement-details.md", "requirement-details-part-2.md"])
def test_breakdown_single_feature_real_cli_and_action(breakdown_project, active):
    project, state_path = breakdown_project
    folder = project / "x-ipe-docs/requirements"
    if active != "requirement-details.md":
        (folder / "requirement-details.md").rename(folder / active)
    feature = feature_record()
    create, payload = run_board(project, "feature_create.py", "--feature", json.dumps(feature))
    assert create.returncode == 0 and payload["data"]["feature_id"] == feature["feature_id"]
    query, board = run_board(project, "feature_query.py", "--feature-id", feature["feature_id"])
    assert query.returncode == 0
    assert all(board["data"]["feature"][key] == value for key, value in feature.items())
    before = json.loads(state_path.read_text())
    features = [{"id": feature["feature_id"], "name": feature["title"], "depends_on": []}]
    result, payload = write_breakdown(project, features, breakdown_links(active))
    assert result.returncode == 0 and payload["success"]
    read, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    assert read.returncode == 0
    action = state["shared"]["requirement"]["actions"]["feature_breakdown"]
    assert action["status"] == "done" and action["deliverables"] == breakdown_links(active)
    assert state["shared"]["requirement"]["actions"]["requirement_gathering"] == (
        before["shared"]["requirement"]["actions"]["requirement_gathering"])
    assert state["shared"]["ideation"] == before["shared"]["ideation"]
    assert [f["feature_id"] for f in state["features"]] == [feature["feature_id"]]
    assert state["features"][0]["implement"]["actions"]["feature_refinement"]["status"] == "pending"
    assert (project / breakdown_links(active)["features-list"]).is_file()
    assert (project / breakdown_links(active)["breakdown-folder"]).is_dir()
    assert not list(folder.rglob("specification.md"))
    board_path = project / "x-ipe-docs/planning/features/features.json"
    unchanged = (state_path.read_bytes(), board_path.read_bytes())
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    run_board(project, "feature_query.py", "--feature-id", feature["feature_id"])
    assert unchanged == (state_path.read_bytes(), board_path.read_bytes())
    assert not (project / "x-ipe-docs/planning/tasks").exists()


def test_breakdown_new_delta_preserves_existing_workflow_stages(breakdown_project):
    project, state_path = breakdown_project
    existing = {"id": "FEATURE-005", "name": "Legacy Terminal", "depends_on": []}
    assert write_breakdown(project, [existing], breakdown_links())[0].returncode == 0
    state = json.loads(state_path.read_text())
    state["features"][0]["implement"]["actions"]["implementation"]["status"] = "done"
    state_path.write_text(json.dumps(state))
    stable = json.loads(state_path.read_text())["features"][0]
    new = {"id": "FEATURE-061-B", "name": "Status History", "depends_on": ["FEATURE-005"]}
    assert write_breakdown(project, [new], breakdown_links())[0].returncode == 0
    after = json.loads(state_path.read_text())
    assert after["features"][0] == stable
    assert [f["feature_id"] for f in after["features"]] == ["FEATURE-005", "FEATURE-061-B"]
    assert after["features"][1]["depends_on"] == ["FEATURE-005"]
    assert after["shared"]["requirement"]["actions"]["feature_breakdown"]["features_created"] == [new]


def test_breakdown_replay_is_characterized_not_claimed_idempotent(breakdown_project, breakdown_entry):
    project, state_path = breakdown_project
    features = [{"id": "FEATURE-061-A", "name": "Badge", "depends_on": []}]
    assert write_breakdown(project, features, breakdown_links())[0].returncode == 0
    assert write_breakdown(project, features, breakdown_links())[0].returncode == 0
    assert [f["feature_id"] for f in json.loads(state_path.read_text())["features"]] == [
        "FEATURE-061-A", "FEATURE-061-A"]
    assert "never resend existing entries" in breakdown_entry


@pytest.mark.parametrize("features", [None, []])
def test_breakdown_initial_empty_features_is_blocked(breakdown_project, features):
    project, state_path = breakdown_project
    before = state_path.read_bytes()
    result, payload = write_breakdown(project, features, breakdown_links())
    assert result.returncode != 0 and payload["error"] == "MISSING_FEATURES"
    assert state_path.read_bytes() == before


@pytest.mark.parametrize("links", [
    {"features-list": "x.md", "extra": "unknown"},
    {"features-list": "x.md", "breakdown-folder": ["x-ipe-docs/requirements"]},
])
def test_breakdown_invalid_deliverable_contract_preserves_state(breakdown_project, links):
    project, state_path = breakdown_project
    before = state_path.read_bytes()
    result, payload = write_breakdown(project, [{"id": "FEATURE-061-A", "name": "Badge"}], links)
    assert result.returncode != 0 and payload["error"] == "INVALID_DELIVERABLES"
    assert state_path.read_bytes() == before


def test_breakdown_writer_semantic_gaps_require_domain_guard(breakdown_project, breakdown_entry):
    project, state_path = breakdown_project
    state = json.loads(state_path.read_text())
    state["shared"]["requirement"]["actions"]["requirement_gathering"]["status"] = "pending"
    state_path.write_text(json.dumps(state))
    result, payload = write_breakdown(project, [{"id": "FEATURE-061-A", "name": "Badge"}],
                                      {"features-list": "missing.md"})
    assert result.returncode == 0 and payload["success"]  # installed semantic gap, not domain success
    after = json.loads(state_path.read_text())
    assert after["shared"]["requirement"]["actions"]["requirement_gathering"]["status"] == "pending"
    assert not (project / "missing.md").exists()
    assert "BOTH features-list" in breakdown_entry and "writer success alone is insufficient" in breakdown_entry


def test_breakdown_existing_cr_board_identity_status_and_retirement(breakdown_project):
    project, _ = breakdown_project
    old = feature_record("FEATURE-005", "EPIC-005", status="Completed",
                         specification_link="x-ipe-docs/requirements/FEATURE-005/specification.md")
    assert run_board(project, "feature_create.py", "--feature", json.dumps(old))[0].returncode == 0
    _, prior = run_board(project, "feature_query.py", "--feature-id", old["feature_id"])
    delta = {"description": "Approved CR note", "version": "v1.1"}
    result, _ = run_board(project, "feature_update.py", "--feature-id", old["feature_id"],
                          "--updates", json.dumps(delta))
    assert result.returncode == 0
    _, after = run_board(project, "feature_query.py", "--feature-id", old["feature_id"])
    for key in ("feature_id", "epic_id", "created_at", "status", "specification_link", "dependencies"):
        assert after["data"]["feature"][key] == prior["data"]["feature"][key]
    assert after["data"]["feature"]["description"] == delta["description"]
    assert run_board(project, "feature_update.py", "--feature-id", old["feature_id"],
                     "--updates", '{"status":"Retired"}')[0].returncode == 0
    _, retired = run_board(project, "feature_query.py", "--feature-id", old["feature_id"])
    assert retired["data"]["feature"]["status"] == "Retired"  # record remains, not archive/delete


@pytest.mark.parametrize("invalid", [{"status": "Draft"}, {"priority": "P0"}, {"dependencies": "FEATURE-005"}])
def test_breakdown_board_creation_contract_rejects_invalid_fields(breakdown_project, invalid):
    project, _ = breakdown_project
    result, payload = run_board(project, "feature_create.py", "--feature", json.dumps(feature_record(**invalid)))
    assert result.returncode != 0 and payload["success"] is False
    assert not (project / "x-ipe-docs/planning/features/features.json").exists()


def test_breakdown_board_duplicate_and_immutable_epic_preserve_history(breakdown_project):
    project, _ = breakdown_project
    feature = feature_record()
    assert run_board(project, "feature_create.py", "--feature", json.dumps(feature))[0].returncode == 0
    store = project / "x-ipe-docs/planning/features/features.json"
    before = store.read_bytes()
    result, payload = run_board(project, "feature_create.py", "--feature", json.dumps(feature))
    assert result.returncode != 0 and payload["error"] == "DUPLICATE_ERROR"
    assert store.read_bytes() == before
    result, payload = run_board(project, "feature_update.py", "--feature-id", feature["feature_id"],
                                "--updates", '{"epic_id":"EPIC-099"}')
    assert result.returncode != 0 and payload["error"] == "IMMUTABLE_FIELD"
    assert store.read_bytes() == before


def test_breakdown_http_read_consumer_uses_real_cli_store(breakdown_project):
    from flask import Flask
    from x_ipe.routes.feature_board_routes import feature_board_bp

    project, _ = breakdown_project
    assert run_board(project, "feature_create.py", "--feature", json.dumps(feature_record()))[0].returncode == 0
    app = Flask(__name__)
    app.config.update(TESTING=True, PROJECT_ROOT=str(project))
    app.register_blueprint(feature_board_bp)
    with app.test_client() as client:
        response = client.get("/api/features/get/FEATURE-061-A")
        assert response.status_code == 200
        assert response.json["data"]["feature"]["feature_id"] == "FEATURE-061-A"
        assert "feature_id" not in response.json["data"]
        listing = client.get("/api/features/list?epic_id=EPIC-061&page_size=1")
        assert listing.json["data"]["pagination"]["total"] == 1
        assert listing.json["data"]["features"][0]["status"] == "Planned"


def test_breakdown_existing_only_pending_action_cannot_replay(breakdown_project):
    project, state_path = breakdown_project
    features = [{"id": "FEATURE-061-A", "name": "Badge", "depends_on": []}]
    assert write_breakdown(project, features, breakdown_links())[0].returncode == 0
    state = json.loads(state_path.read_text())
    state["shared"]["requirement"]["actions"]["feature_breakdown"]["status"] = "pending"
    state["features"][0]["implement"]["actions"]["implementation"]["status"] = "done"
    state_path.write_text(json.dumps(state))
    before = state_path.read_bytes()
    result, payload = write_breakdown(project, [], breakdown_links())
    assert result.returncode != 0 and payload["error"] == "MISSING_FEATURES"
    assert state_path.read_bytes() == before


@pytest.mark.parametrize("prerequisite", ["pending", "skipped", "failed", "in_progress"])
def test_breakdown_incomplete_prerequisites_not_helper_success(breakdown_project, prerequisite):
    project, state_path = breakdown_project
    state = json.loads(state_path.read_text())
    state["shared"]["requirement"]["actions"]["requirement_gathering"]["status"] = prerequisite
    state_path.write_text(json.dumps(state))
    result, payload = write_breakdown(project, [{"id": "FEATURE-061-A", "name": "Badge"}],
                                      breakdown_links())
    assert result.returncode == 0 and payload["success"]  # real helper gap, NOT domain completion
    after = json.loads(state_path.read_text())
    assert after["shared"]["requirement"]["actions"]["requirement_gathering"]["status"] == prerequisite


@pytest.mark.parametrize("failure", ["missing-workflow", "missing-action", "locked-stage"])
def test_breakdown_helper_failures_preserve_state(breakdown_project, failure):
    project, state_path = breakdown_project
    state = json.loads(state_path.read_text())
    if failure == "missing-action":
        del state["shared"]["requirement"]["actions"]["feature_breakdown"]
    elif failure == "locked-stage":
        state["shared"]["requirement"]["status"] = "locked"
        state["shared"]["ideation"]["status"] = "in_progress"
        for action in state["shared"]["ideation"]["actions"].values():
            action["status"] = "pending"
    state_path.write_text(json.dumps(state))
    before = state_path.read_bytes()
    result, payload = run_helper(
        project, "workflow_update_action.py", "--workflow",
        "missing" if failure == "missing-workflow" else "pilot",
        "--action", "feature_breakdown", "--status", "done",
        "--deliverables", json.dumps(breakdown_links()),
        "--features", '[{"id":"FEATURE-061-A","name":"Badge"}]',
    )
    assert result.returncode != 0
    assert payload["error"] == {"missing-workflow": "FILE_NOT_FOUND",
                                "missing-action": "ACTION_NOT_FOUND",
                                "locked-stage": "STAGE_LOCKED"}[failure]
    assert state_path.read_bytes() == before


def test_breakdown_board_all_pages_include_retired_reservations(breakdown_project):
    project, _ = breakdown_project
    expected = {"FEATURE-061-A", "FEATURE-061-C"}
    for suffix, status in [("A", "Planned"), ("C", "Retired")]:
        record = feature_record(f"FEATURE-061-{suffix}", status=status)
        assert run_board(project, "feature_create.py", "--feature", json.dumps(record))[0].returncode == 0
    store = project / "x-ipe-docs/planning/features/features.json"
    before = store.read_bytes()
    observed = set()
    for page in (1, 2):
        result, payload = run_board(project, "feature_query.py", "--epic-id", "EPIC-061",
                                    "--page", str(page), "--page-size", "1")
        assert result.returncode == 0
        assert payload["data"]["total_pages"] == 2
        assert "pagination" not in payload["data"]
        observed.update(f["feature_id"] for f in payload["data"]["features"])
    assert observed == expected and store.read_bytes() == before


def test_breakdown_corrupt_inventory_guard_is_required(breakdown_project):
    project, _ = breakdown_project
    store = project / "x-ipe-docs/planning/features/features.json"
    store.parent.mkdir(parents=True)
    store.write_text('{"features": [broken historical bytes')
    corrupt = store.read_bytes()
    result, payload = run_board(project, "feature_query.py")
    assert result.returncode == 0 and payload["data"]["features"] == []
    assert store.read_bytes() == corrupt  # empty query does NOT establish genuine absence
    result, _ = run_board(project, "feature_create.py", "--feature", json.dumps(feature_record()))
    assert result.returncode == 0 and store.read_bytes() != corrupt  # unsafe gap in installed helper
    assert "Corrupt/unreadable/ambiguous" in (BREAKDOWN / "references/integration.md").read_text()


def xml_block(text, tag):
    match = re.search(rf"<{tag}(?:\s[^>]*)?>.*?</{tag}>", text, re.S)
    assert match is not None, tag
    return ET.fromstring(match[0])


def assert_domain_structure(package):
    """Parse real sections/XML/YAML; do not infer agent execution from prose."""
    text = (package / "SKILL.md").read_text()
    headings = ["Purpose", "Important Notes", "Input Parameters", "Definition of Ready",
                "Execution Flow", "Execution Procedure", "Output Result", "Definition of Done",
                "Patterns & Anti-Patterns", "Examples"]
    positions = [text.index(f"## {heading}\n") for heading in headings]
    assert positions == sorted(positions)
    assert 1 <= len(xml_block(text, "definition_of_ready").findall("checkpoint")) <= 5
    assert 1 <= len(xml_block(text, "definition_of_done").findall("checkpoint")) <= 10
    procedure = xml_block(text, "procedure")
    steps = [node for node in procedure if node.tag.startswith("step_")]
    assert len(steps) == 4
    assert [node.tag for node in steps] == [f"step_{n}" for n in range(1, 5)]
    assert all(node.findtext("name") and node.findtext("action") and node.findtext("output")
               for node in steps)
    assert not any(node.tag.startswith("phase_") for node in procedure.iter())
    assert set(output_contract(package / "SKILL.md")["process_preference"]) == {"interaction_mode"}
    return text


def test_breakdown_parsed_structure_and_actual_table_schema():
    assert_domain_structure(BREAKDOWN)
    for resource in ("templates/features.md", "templates/requirement-details.md"):
        rows = [line for line in (BREAKDOWN / resource).read_text().splitlines()
                if line.startswith("| ")]
        cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
        assert cells[0] == ["Feature ID", "Epic ID", "Feature Title", "Version",
                            "Brief Description", "Feature Dependency"]
        assert len(cells[2]) == 6 and cells[2][0] == "FEATURE-{nnn}-A"
        assert cells[2][1] == "EPIC-{nnn}" and cells[2][3] == "v1.0"


def test_breakdown_structure_guard_detects_duplicate_lifecycle(tmp_path):
    entry = (BREAKDOWN / "SKILL.md").read_text()
    (tmp_path / "SKILL.md").write_text(entry.replace(
        '<step_1>', '<phase_0><action>Create Task</action></phase_0><step_1>', 1))
    with pytest.raises(AssertionError):
        assert_domain_structure(tmp_path)


REFINEMENT_NAME = "x-ipe-task-based-feature-refinement"
REFINEMENT_META = ROOT / "x-ipe-docs/skill-meta" / REFINEMENT_NAME
REFINEMENT = REFINEMENT_META / "candidate"
REFINEMENT_LIVE = ROOT / ".github/skills" / REFINEMENT_NAME
SPEC_SECTIONS = (
    "Version History", "Linked Mockups", "Overview", "User Stories", "Acceptance Criteria",
    "Functional Requirements", "Non-Functional Requirements", "UI/UX Requirements",
    "Dependencies", "Business Rules", "Edge Cases & Constraints", "Out of Scope",
    "Technical Considerations", "Open Questions", "Acceptance Traceability",
    "Context and Verification Evidence",
    "Goal / Subgoal Coverage",
)


def table_rows(text, header):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == header)
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def assert_acceptance_tables(text):
    header = "| AC ID | Criterion (Given/When/Then) | Test Type |"
    rows = table_rows(text, header)
    assert rows and all(len(row) == 3 for row in rows)
    ids = [row[0] for row in rows]
    assert len(ids) == len(set(ids))
    for _, criterion, test_type in rows:
        assert re.search(r"\bGIVEN\b.+\bWHEN\b.+\bTHEN\b.+", criterion, re.S)
        assert test_type in {"UI", "API", "Unit", "Integration"}


def test_refinement_complete_validator_structure_and_protected_live():
    validator = load_validator()
    receipt = validator.validate(ROOT, REFINEMENT, REFINEMENT_NAME, "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    assert receipt["body_lines"] <= 300
    baseline = json.loads((REFINEMENT_META / "baseline.json").read_text())
    from tests.test_goal_oriented_skills import assert_reviewed_live
    assert_reviewed_live(REFINEMENT_NAME,
                        validator.manifest(validator.tree_bytes(REFINEMENT_LIVE, ROOT)), baseline)
    assert set(receipt["files"]) == set(baseline) | {"references/integration.md"}
    assert_domain_structure(REFINEMENT)
    assert not list(REFINEMENT.rglob("*.json")) and not list(REFINEMENT.rglob("*.yaml"))


def test_refinement_exact_original_output_contract():
    assert output_contract(REFINEMENT / "SKILL.md") == output_contract(REFINEMENT_LIVE / "SKILL.md")
    assert list(output_contract(REFINEMENT / "SKILL.md")) == list(
        output_contract(REFINEMENT_LIVE / "SKILL.md"))
    example = (REFINEMENT / "references/examples.md").read_text()
    block = re.search(r"```yaml\n(.*?)\n```", example, re.S)
    actual = yaml.safe_load(block[1])["task_completion_output"]
    assert list(actual) == list(output_contract(REFINEMENT / "SKILL.md"))
    assert actual["workflow_action"] == "feature_refinement" and actual["workflow_action_updated"] is False


def test_refinement_initialized_fields_single_owner_and_all_resources():
    entry = assert_domain_structure(REFINEMENT)
    fields = {node.attrib["name"] for node in xml_block(entry, "input_init").findall("field")}
    assert fields == {"task_id", "task_based_skill", "execution_mode", "workflow.name",
                      "workflow.action", "process_preference.interaction_mode", "feature_phase",
                      "feature_id", "workflow.extra_context_reference", "feature_docs_folder",
                      "mockup_list", "refinement_context", "document_language"}
    for mode in MODES:
        assert mode in entry
    assert entry.count("x-ipe-workflow-task-execution/references/lifecycle.md") == 1
    package = "\n".join(p.read_text() for p in REFINEMENT.rglob("*.md"))
    for obsolete in ("task_create.py", "task_update.py", "task_ensure.py", 'type: "routing"',
                     "phase_0", "phase_6", "Execute Next Action", "git add", "features.md",
                     "Draft → Specified", "newer artifact takes precedence", "x-ipe+feature+"):
        assert obsolete not in package
    for path in REFINEMENT.rglob("*.md"):
        assert all(not target.startswith(("../", "./", "/"))
                   for target in load_validator().markdown_targets(path.read_text()))
    procedure = xml_block(entry, "procedure")
    assert "Human asks the human within skill and waits" in procedure.find("step_2/action").text
    assert "full DAO and hybrid use bounded common" in procedure.find("step_2/action").text
    assert "Human and hybrid must confirm specification completeness" in procedure.find("step_2/action").text
    assert "without replay" in procedure.find("step_4/action").text


def test_refinement_full_scaffold_and_traceability_schema():
    scaffold = (REFINEMENT / "references/specification-template.md").read_text()
    headings = re.findall(r"^## (.+)$", scaffold, re.M)
    for section in SPEC_SECTIONS:
        assert section in headings
    assert headings.index("User Stories") < headings.index("Acceptance Criteria")
    assert headings.index("Out of Scope") < headings.index("Acceptance Traceability")
    assert "| Version | Date | Description | Change Request |" in scaffold
    mockups = table_rows(scaffold, "| Mockup | Type | Path | Description | Status | Linked Date |")
    assert len(mockups[0]) == 6 and mockups[0][-2:] == ["current", "MM-DD-YYYY"]
    trace = table_rows(scaffold, "| Source Requirement / FR / NFR | User Story | AC ID | Mockup Element / Status | Primary Validation | Coverage / CR Decision |")
    assert len(trace[0]) == 6
    entry = (REFINEMENT / "SKILL.md").read_text()
    for invariant in ("stable US/FR/AC IDs", "unaffected section bytes", "EN/ZH",
                      "never reuse deleted IDs", "Outdated mockups are directional only",
                      "Uncovered current in-scope elements block", "MM-DD-YYYY",
                      "specification_link", "legacy", "advanced", "SHA256",
                      "BOTH specification", "feature-docs-folder", "Writer success alone is insufficient"):
        assert invariant in entry


@pytest.mark.parametrize("defect", ["duplicate", "manual", "not-gwt"])
def test_refinement_acceptance_invariant_rejects_real_table_defects(defect):
    text = (REFINEMENT / "references/examples.md").read_text()
    assert_acceptance_tables(text)
    if defect == "duplicate":
        text = text.replace("AC-061-A-02", "AC-061-A-01")
    elif defect == "manual":
        text = text.replace("| UI |", "| Manual |", 1)
    else:
        text = text.replace("GIVEN operator views", "operator views", 1)
    with pytest.raises(AssertionError):
        assert_acceptance_tables(text)


@pytest.fixture(params=["new", "legacy"])
def refinement_project(breakdown_project, request):
    project, state_path = breakdown_project
    feature_id = "FEATURE-061-A" if request.param == "new" else "FEATURE-005"
    folder = ("x-ipe-docs/requirements/EPIC-061/FEATURE-061-A" if request.param == "new"
              else "x-ipe-docs/requirements/FEATURE-005")
    target = project / folder
    target.mkdir(parents=True, exist_ok=True)
    spec = target / "specification.md"
    # A concrete authored fixture, NOT execution of an LLM/refinement generator.
    text = "# Status Badge\n\n> Feature ID: " + feature_id + "\n"
    for section in SPEC_SECTIONS:
        text += f"\n## {section}\n"
        if section == "Acceptance Criteria":
            source = (REFINEMENT / "references/examples.md").read_text()
            text += source[source.index("| AC ID |"):source.index("\n\nHuman/hybrid")]
        else:
            text += "Approved read-only badge scope or explicit N/A rationale.\n"
    spec.write_text(text)
    assert_acceptance_tables(text)
    record = feature_record(feature_id, "EPIC-061" if request.param == "new" else "EPIC-005",
                            specification_link=f"{folder}/specification.md")
    assert run_board(project, "feature_create.py", "--feature", json.dumps(record))[0].returncode == 0
    assert write_breakdown(project, [{"id": feature_id, "name": record["title"], "depends_on": []}],
                           breakdown_links())[0].returncode == 0
    state = json.loads(state_path.read_text())
    state["features"][0]["implement"]["actions"]["feature_refinement"]["context"] = {
        "requirement-doc": breakdown_links()["features-list"], "features-list": breakdown_links()["features-list"]}
    state_path.write_text(json.dumps(state))
    return project, state_path, record, {"specification": f"{folder}/specification.md",
                                        "feature-docs-folder": folder}


def write_refinement(project, record, links, *extra):
    return run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                      "--action", "feature_refinement", "--status", "done",
                      "--feature-id", record["feature_id"], "--deliverables", json.dumps(links), *extra)


def test_refinement_actual_writer_readback_paths_context_and_lifecycle_handoff(refinement_project):
    project, state_path, record, links = refinement_project
    before = json.loads(state_path.read_text())
    result, payload = write_refinement(project, record, links)
    assert result.returncode == 0 and payload["success"]
    _, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    assert len(state["features"]) == 1
    action = state["features"][0]["implement"]["actions"]["feature_refinement"]
    assert action["status"] == "done" and action["deliverables"] == links
    assert action["context"] == before["features"][0]["implement"]["actions"]["feature_refinement"]["context"]
    assert state["shared"]["requirement"]["actions"] == before["shared"]["requirement"]["actions"]
    for name, data in before["features"][0]["implement"]["actions"].items():
        if name != "feature_refinement":
            assert state["features"][0]["implement"]["actions"][name] == data
    assert (project / links["specification"]).is_file() and (project / links["feature-docs-folder"]).is_dir()
    # Exercise the supported owner/category handoff, not a child status write.
    updates = {"specification_link": links["specification"], "status": "Refined"}
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"],
                     "--updates", json.dumps(updates))[0].returncode == 0
    board_path = project / "x-ipe-docs/planning/features/features.json"
    frozen = (state_path.read_bytes(), board_path.read_bytes())
    _, query = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert query["data"]["feature"]["specification_link"] == links["specification"]
    assert query["data"]["feature"]["status"] == "Refined"
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    assert frozen == (state_path.read_bytes(), board_path.read_bytes())
    assert not (project / "x-ipe-docs/planning/tasks").exists()


@pytest.mark.parametrize("defect", ["folder-array", "extra-tag", "missing-feature", "locked"])
def test_refinement_real_helper_errors_preserve_state(refinement_project, defect):
    project, state_path, record, links = refinement_project
    if defect == "folder-array":
        links["feature-docs-folder"] = [links["feature-docs-folder"]]
    elif defect == "extra-tag":
        links["spec-path"] = links["specification"]
    elif defect == "missing-feature":
        record["feature_id"] = "FEATURE-999-A"
    else:
        state = json.loads(state_path.read_text())
        state["shared"]["requirement"]["actions"]["feature_breakdown"]["status"] = "pending"
        state_path.write_text(json.dumps(state))
    frozen = state_path.read_bytes()
    result, payload = write_refinement(project, record, links)
    assert result.returncode != 0
    assert payload["error"] == {"folder-array": "INVALID_DELIVERABLES", "extra-tag": "INVALID_DELIVERABLES",
                                "missing-feature": "FEATURE_NOT_FOUND", "locked": "STAGE_LOCKED"}[defect]
    assert state_path.read_bytes() == frozen


def test_refinement_actual_advanced_cr_link_update_preserves_state(refinement_project):
    project, _, record, links = refinement_project
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"],
                     "--updates", '{"status":"Completed"}')[0].returncode == 0
    _, before = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    changes = {"version": "v1.1", "specification_link": links["specification"]}
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"],
                     "--updates", json.dumps(changes))[0].returncode == 0
    _, after = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    for key in ("feature_id", "epic_id", "created_at", "status", "dependencies", "specification_link"):
        assert after["data"]["feature"][key] == before["data"]["feature"][key]
    assert after["data"]["feature"]["version"] == "v1.1"


def test_refinement_helper_semantic_gaps_not_domain_success(refinement_project):
    project, state_path, record, _ = refinement_project
    state = json.loads(state_path.read_text())
    state["shared"]["requirement"]["actions"]["feature_breakdown"]["status"] = "skipped"
    state["features"][0]["implement"]["actions"]["feature_refinement"]["context"] = {}
    state_path.write_text(json.dumps(state))
    links = {"specification": "missing.md"}
    result, payload = write_refinement(project, record, links)
    assert result.returncode == 0 and payload["success"]  # real gap, NOT domain completion
    action = json.loads(state_path.read_text())["features"][0]["implement"]["actions"]["feature_refinement"]
    assert action["context"] == {} and "feature-docs-folder" not in action["deliverables"]
    assert not (project / links["specification"]).exists()


def test_refinement_actual_action_prompt_and_artifact_contract():
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["implement"]["actions"]["feature_refinement"]
    assert template["stages"]["implement"]["type"] == "per_feature" and action["optional"] is False
    assert set(action["action_context"]) == {"requirement-doc", "features-list"}
    assert all(item["required"] for item in action["action_context"].values())
    assert action["deliverables"] == ["$output:specification", "$output-folder:feature-docs-folder"]
    script = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"feature_refinement:.*skill: '" + REFINEMENT_NAME + "'", script)
    prompts = json.loads((ROOT / "x-ipe-docs/config/copilot-prompt.json").read_text())
    prompt = next(p for p in prompts["workflow-prompts"] if p["action"] == "feature_refinement")
    assert {p["language"] for p in prompt["prompt-details"]} == {"en", "zh"}
    assert all("$feature-id$" in p["command"] and "$output:requirement-doc$" in p["command"]
               for p in prompt["prompt-details"])