"""Downstream authored artifacts/scaffolds and actual temporary CLI contracts.

No autonomous designer, consultation execution, stakeholder observation or
production publication is simulated. Reuse upstream tables/fixtures/helpers.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml

from tests.publication_recovery_6749 import current_publication, recovered_publication, resource_inventory
from tests.skill_validation_harness_6749 import load_source, validate_resources

from tests.test_goal_oriented_skills import (
    GOAL_COLUMNS, REFINEMENT, render_table_from_scaffold, rows, validator,
)
from tests.test_skill_pipeline_refactor import (
    breakdown_project, helper_project, refinement_project, run_board, run_helper,
    write_refinement,
)


ROOT = Path(__file__).resolve().parents[1]
NAME = "x-ipe-task-based-technical-design"
META = ROOT / "x-ipe-docs/skill-meta" / NAME
CANDIDATE = META / "candidate"
COVERAGE = ("Source / Parent Goal", "Story / Subgoal", "AC ID", "Component / Flow",
            "Interface / Data / Algorithm", "Planned Validation", "Delivery State", "Outcome State")


def example(kind="new"):
    text = (CANDIDATE / "references/examples.md").read_text()
    return text.split("## 2.", 1)[0] if kind == "new" else text.split("## 2.", 1)[1].split("## 3.", 1)[0]


def check_design(text, upstream, *, delta=False):
    goals = rows(text, GOAL_COLUMNS)
    parents = rows(upstream, GOAL_COLUMNS)
    coverage = rows(text, COVERAGE)
    assert [g["Goal ID"] for g in goals] == [g["Goal ID"] for g in parents]
    expected = {a.strip() for g in parents for a in g["AC Links"].split(",")}
    assert len(coverage) == len(expected) == len({r["AC ID"] for r in coverage})
    assert {r["AC ID"] for r in coverage} == expected
    for goal, parent in zip(goals, parents):
        for column in ("Parent / Source", "Desired Observable Outcome", "Constraints / Non-goals", "AC Links"):
            assert goal[column] == parent[column]
        assert goal["Outcome State"] == "not measured"
    for row in coverage:
        assert all(row.values())
        assert row["Story / Subgoal"] == goals[0]["Goal ID"]
        assert "FR-061-01" in row["Source / Parent Goal"]
        assert "planned UI" in row["Planned Validation"]
        assert row["Component / Flow"] == "BadgeView + StateSelector"
        assert row["Outcome State"] == "not measured"
        assert row["Delivery State"] == ("invalidated by goal delta" if delta and row["AC ID"] == "AC-061-A-01" else "planned")
    return coverage


@pytest.mark.parametrize("kind", ["new", "delta"])
def test_design_authoritative_parent_ac_means_and_outcome(kind):
    text = (REFINEMENT / "references/examples.md").read_text()
    upstream = text.split("## 2.", 1)[0] if kind == "new" else text.split("## 7.", 1)[1]
    check_design(example(kind), upstream, delta=kind == "delta")
    if kind == "new":
        choices = rows(example(), ("Means", "Selection", "Goal / AC / Constraint Rationale"))
        assert [r["Means"] for r in choices if r["Selection"] == "selected"] == ["BadgeView", "StateSelector"]
        assert choices[-1]["Selection"] == "rejected"


@pytest.mark.parametrize("defect", ["orphan", "missing", "false-outcome", "false-delivery", "source", "empty-contract", "invented-goal"])
def test_design_negative_artifact_claims(defect):
    text = example()
    if defect == "orphan":
        text = text.replace("| AC-061-A-02 | BadgeView", "| AC-UNKNOWN | BadgeView")
    elif defect == "missing":
        text = "\n".join(l for l in text.splitlines() if not l.startswith("| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02"))
    elif defect == "false-outcome":
        text = text.replace("| not measured |", "| observed stakeholder outcome |", 1)
    elif defect == "false-delivery":
        text = text.replace("| planned | not measured |", "| verified engineering delivery | not measured |", 1)
    elif defect == "source":
        text = text.replace("FR-061-01; explicit badge request", "fabricated source", 1)
    elif defect == "empty-contract":
        text = text.replace("selectLabel absent-state branch; no state mutation", "", 1)
    else:
        text = text.replace("| US-061-A-01 | FR-061-01", "| BadgeView-goal | FR-061-01", 1)
    upstream = (REFINEMENT / "references/examples.md").read_text().split("## 2.", 1)[0]
    with pytest.raises(AssertionError):
        check_design(text, upstream)


def test_design_scaffold_renders_existing_tables_in_one_artifact(tmp_path):
    scaffold = (CANDIDATE / "references/design-templates.md").read_text()
    rendered = render_table_from_scaffold(scaffold, GOAL_COLUMNS, rows(example(), GOAL_COLUMNS))
    rendered = render_table_from_scaffold(rendered, COVERAGE, rows(example(), COVERAGE))
    target = tmp_path / "technical-design.md"
    target.write_text(rendered)
    upstream = (REFINEMENT / "references/examples.md").read_text().split("## 2.", 1)[0]
    check_design(target.read_text(), upstream)
    assert list(tmp_path.iterdir()) == [target]
    for section in ("Part 1: Agent-Facing Summary", "Part 2: Implementation Guide",
                    "Key Components Implemented", "Dependencies", "Usage Example",
                    "Algorithms and State Transitions", "Test Plan", "Security, Tracing and Observability",
                    "Mockup-to-Component Mapping", "Design Change Log", "Version History"):
        assert section in rendered
    assert "classDiagram" in rendered and "sequenceDiagram" in rendered
    assert not re.search(r"\]\((?:\.\.?/|/Users/)", rendered)


def test_design_delta_preserves_unaffected_mapping_bytes_and_ids():
    before, after = rows(example(), COVERAGE), rows(example("delta"), COVERAGE)
    assert [r["AC ID"] for r in before] == [r["AC ID"] for r in after]
    assert before[1] == after[1] and before[0] != after[0]
    assert "parent delta" in after[0]["Source / Parent Goal"]
    assert "invalidated" in after[0]["Planned Validation"]


def test_design_both_parts_are_authoritative_not_supplementary():
    scaffold = (CANDIDATE / "references/design-templates.md").read_text()
    assert "Part 2 is supplementary" not in scaffold
    assert "Read both parts before implementation" in scaffold


def output(path):
    text = path.read_text().split("## Output Result", 1)[1]
    return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", text, re.S)[1])


def test_design_validator_inventory_output_and_single_lifecycle():
    v = validator()
    baseline = json.loads((META / "baseline-goal-TASK-6749.json").read_text())
    published = META / "publication-receipt-goal-TASK-6749.json"
    if published.exists():
        publication = json.loads(published.read_text())
        assert publication["baseline"] == baseline
        assert publication["byte_parity"] is True
        current = current_publication(NAME)
        assert recovered_publication(NAME)["baseline_hash"] == v.fingerprint(publication["files"])
        assert v.tree_bytes(ROOT / ".github/skills" / NAME, ROOT) == v.tree_bytes(CANDIDATE, ROOT)
    else:
        assert v.manifest(v.tree_bytes(ROOT / ".github/skills" / NAME, ROOT)) == baseline
    receipt = v.validate(ROOT, CANDIDATE, NAME, "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    assert set(receipt["files"]) == set(baseline) | {"references/integration.md"}
    assert output(CANDIDATE / "SKILL.md") == output(ROOT / ".github/skills" / NAME / "SKILL.md")
    entry = (CANDIDATE / "SKILL.md").read_text()
    procedure = ET.fromstring(re.search(r"<procedure.*?</procedure>", entry, re.S)[0])
    assert len(procedure.findall(".//action")) == 5
    for obsolete in ("task_create.py", "task_update.py", "phase_0", "phase_6", 'type: "routing"', "Execute Next Action"):
        assert obsolete not in entry
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", entry, re.S)[0])
    assert {f.attrib["name"] for f in init.findall("field")} >= {"task_id", "workflow.action", "workflow.extra_context_reference", "mockup_list", "feature_id"}


def test_real_design_action_config_and_matching_declarations():
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    stage = template["stages"]["implement"]
    action = stage["actions"]["technical_design"]
    assert stage["type"] == "per_feature" and action["optional"] is False
    assert action["deliverables"] == ["$output:tech-design", "$output-folder:feature-docs-folder"]
    assert action["action_context"]["specification"]["required"] is True
    js = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"technical_design:.*skill: '" + NAME + "'", js)
    config = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())["stages"]["implement"]["technical_design"]
    assert "informational" in config["_extra_instruction"] and "Do not invoke" in config["_extra_instruction"]
    tool = "x-ipe-tool-implementation-html5"
    assert config[tool] is True
    declared = (ROOT / ".github/skills" / tool / "SKILL.md").read_text()
    assert "tech_stack contains HTML5, CSS3, JavaScript" in declared
    assert "vanilla" in declared and "## Operations" in declared
    entry = (CANDIDATE / "SKILL.md").read_text()
    for clause in ("metadata-only", "no force-enable general", "semantically", "INFORMATIONAL ONLY", "not filename suffix", "not mandatory execution", "no-op resume", "sensitive parameter/log redaction"):
        assert clause in entry


@pytest.fixture
def design_project(refinement_project):
    project, state_path, record, prior = refinement_project
    assert write_refinement(project, record, prior)[0].returncode == 0
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Refined"}')[0].returncode == 0
    folder = prior["feature-docs-folder"]
    target = project / folder / "technical-design.md"
    target.write_text(example())  # authored artifact, not autonomous design execution
    state = json.loads(state_path.read_text())
    state["features"][0]["implement"]["actions"]["technical_design"]["context"] = {"specification": prior["specification"]}
    state_path.write_text(json.dumps(state))
    return project, state_path, record, {"tech-design": f"{folder}/technical-design.md", "feature-docs-folder": folder}


def write_design(project, record, links):
    return run_helper(project, "workflow_update_action.py", "--workflow", "pilot", "--action", "technical_design", "--status", "done", "--feature-id", record["feature_id"], "--deliverables", json.dumps(links))


def test_design_actual_helpers_tags_status_link_and_readonly_resume(design_project):
    project, state_path, record, links = design_project
    result, payload = write_design(project, record, links)
    assert result.returncode == 0 and payload["success"]
    _, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    action = state["features"][0]["implement"]["actions"]["technical_design"]
    assert action["status"] == "done" and action["deliverables"] == links
    assert action["context"]["specification"] == record["specification_link"]
    assert (project / links["tech-design"]).is_file() and (project / links["feature-docs-folder"]).is_dir()
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Designed"}')[0].returncode == 0
    board = project / "x-ipe-docs/planning/features/features.json"
    frozen = state_path.read_bytes(), board.read_bytes()
    _, read = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert read["data"]["feature"]["status"] == "Designed"
    assert "technical_design_link" not in read["data"]["feature"]
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    assert frozen == (state_path.read_bytes(), board.read_bytes())
    assert not (project / "x-ipe-docs/planning/tasks").exists()


@pytest.mark.parametrize("defect", ["folder-array", "extra-tag", "missing-feature", "locked"])
def test_design_actual_helper_failures_preserve_state(design_project, defect):
    project, state_path, record, links = design_project
    if defect == "folder-array":
        links["feature-docs-folder"] = [links["feature-docs-folder"]]
    elif defect == "extra-tag":
        links["goal"] = "invented"
    elif defect == "missing-feature":
        record["feature_id"] = "FEATURE-999-A"
    else:
        state = json.loads(state_path.read_text())
        state["shared"]["requirement"]["actions"]["feature_breakdown"]["status"] = "pending"
        state["features"][0]["implement"]["status"] = "locked"
        state_path.write_text(json.dumps(state))
    frozen = state_path.read_bytes()
    result, payload = write_design(project, record, links)
    assert result.returncode != 0 and not payload["success"]
    assert state_path.read_bytes() == frozen


def test_design_permissive_writer_not_domain_completion(design_project):
    project, state_path, record, _ = design_project
    state = json.loads(state_path.read_text())
    actions = state["features"][0]["implement"]["actions"]
    actions["feature_refinement"]["status"] = "pending"
    actions["technical_design"]["context"] = {}
    state_path.write_text(json.dumps(state))
    result, payload = write_design(project, record, {"tech-design": "missing.md"})
    assert result.returncode == 0 and payload["success"]  # helper gap, not semantic gate
    assert not (project / "missing.md").exists()
    integration = (CANDIDATE / "references/integration.md").read_text()
    assert "writer success alone is insufficient" in integration
    assert "matching feature_refinement action `done`" in integration


def test_design_advanced_cr_preserves_identity_status_history(design_project):
    project, _, record, links = design_project
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Completed"}')[0].returncode == 0
    _, before = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"version":"v1.1"}')[0].returncode == 0
    _, after = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    for key in ("feature_id", "epic_id", "created_at", "status", "dependencies", "specification_link"):
        assert before["data"]["feature"][key] == after["data"]["feature"][key]


def test_design_link_is_not_a_board_schema_field(design_project):
    project, _, record, links = design_project
    board = project / "x-ipe-docs/planning/features/features.json"
    frozen = board.read_bytes()
    result, _ = run_board(project, "feature_update.py", "--feature-id", record["feature_id"],
                          "--updates", json.dumps({"technical_design_link": links["tech-design"]}))
    assert result.returncode != 0 and "UNKNOWN_FIELD" in result.stderr
    assert board.read_bytes() == frozen


IMPL_NAME = "x-ipe-task-based-code-implementation"
IMPL_META = ROOT / "x-ipe-docs/skill-meta" / IMPL_NAME
IMPL = IMPL_META / "candidate"
IMPL_COVERAGE = ("Source / Parent Goal", "Story / Subgoal", "AC ID", "Selected Means",
                 "Test / Assert", "Delivery State", "Outcome State")


def implementation_example(kind="new"):
    text = (IMPL / "references/examples.md").read_text()
    return text.split("## 2.", 1)[0] if kind == "new" else text.split("## 2.", 1)[1].split("## 3.", 1)[0]


def check_implementation(text, upstream):
    goals, parent = rows(text, GOAL_COLUMNS), rows(upstream, GOAL_COLUMNS)
    assert goals == parent  # no invented stakeholder goals or changed approved acceptance
    mapping = rows(text, IMPL_COVERAGE)
    expected = {a.strip() for g in parent for a in g["AC Links"].split(",")}
    assert len(mapping) == len(expected) == len({r["AC ID"] for r in mapping})
    assert {r["AC ID"] for r in mapping} == expected
    for row in mapping:
        assert all(row.values())
        assert row["Story / Subgoal"] == goals[0]["Goal ID"]
        assert "FR-061-01" in row["Source / Parent Goal"]
        assert row["Selected Means"] == "BadgeView + StateSelector"
        assert row["Delivery State"] in ("planned", "invalidated by goal delta")
        assert row["Outcome State"] == "not measured"
        assert "UI" in row["Test / Assert"] and "assert" in row["Test / Assert"]
        assert "mutation" in row["Test / Assert"]
        if row["AC ID"] == "AC-061-A-02":
            assert row["Test / Assert"] == "UI assert approved unavailable label; no controls/mutation"
    return mapping


@pytest.mark.parametrize("kind", ["new", "delta"])
def test_implementation_authoritative_goal_ac_tests_not_activity_counts(kind):
    check_implementation(implementation_example(kind), example(kind))
    text = implementation_example(kind)
    assert "all-required" in text and "no invented" in text
    if kind == "new":
        assert "Rejected dashboard rewrite is not a backlog mandate" in text


@pytest.mark.parametrize("defect", ["missing", "orphan", "duplicate", "source", "assert", "weaken-original", "goal", "false-outcome", "false-delivery"])
def test_implementation_negative_authored_claims(defect):
    text = implementation_example()
    if defect == "missing":
        text = "\n".join(l for l in text.splitlines() if not l.startswith("| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02"))
    elif defect == "orphan":
        text = text.replace("| AC-061-A-02 | BadgeView", "| AC-UNKNOWN | BadgeView")
    elif defect == "duplicate":
        line = next(l for l in text.splitlines() if l.startswith("| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02"))
        text = text.replace(line, line + "\n" + line, 1)
    elif defect == "source":
        text = text.replace("FR-061-01; explicit badge request", "fabricated source", 1)
    elif defect == "assert":
        text = text.replace("UI assert approved current label; no mutation", "", 1)
    elif defect == "weaken-original":
        text = text.replace("UI assert approved unavailable label; no controls/mutation", "UI assert approved unavailable label", 1)
    elif defect == "goal":
        text = text.replace("| US-061-A-01 | FR-061-01", "| BadgeView-goal | FR-061-01", 1)
    elif defect == "false-outcome":
        text = text.replace("| not measured |", "| observed stakeholder outcome |", 1)
    else:
        text = text.replace("| planned | not measured |", "| verified engineering delivery | not measured |", 1)
    with pytest.raises(AssertionError):
        check_implementation(text, example())


def test_implementation_scaffold_and_affected_only_delta(tmp_path):
    text = (IMPL / "references/implementation-guidelines.md").read_text()
    rendered = render_table_from_scaffold(text, GOAL_COLUMNS, rows(implementation_example(), GOAL_COLUMNS))
    rendered = render_table_from_scaffold(rendered, IMPL_COVERAGE, rows(implementation_example(), IMPL_COVERAGE))
    target = tmp_path / "technical-design.md"
    target.write_text(rendered)
    check_implementation(target.read_text(), example())
    before = rows(implementation_example(), IMPL_COVERAGE)
    after = rows(implementation_example("delta"), IMPL_COVERAGE)
    assert before[1] == after[1] and before[0] != after[0]
    assert [r["AC ID"] for r in before] == [r["AC ID"] for r in after]
    assert after[0]["Delivery State"] == "invalidated by goal delta"


def test_implementation_complete_inventory_original_output_and_single_owner():
    v = validator()
    baseline = json.loads((IMPL_META / "baseline-goal-TASK-6749.json").read_text())
    publication_path = IMPL_META / "publication-receipt-goal-TASK-6749.json"
    if publication_path.exists():
        publication = json.loads(publication_path.read_text())
        assert publication["baseline"] == baseline
        assert publication["byte_parity"] is True
        current = current_publication(IMPL_NAME)
        assert recovered_publication(IMPL_NAME)["baseline_hash"] == v.fingerprint(publication["files"])
        assert v.tree_bytes(ROOT / ".github/skills" / IMPL_NAME, ROOT) == v.tree_bytes(IMPL, ROOT)
        assert publication["candidate_hash"] == v.fingerprint(publication["files"])
    else:
        assert v.manifest(v.tree_bytes(ROOT / ".github/skills" / IMPL_NAME, ROOT)) == baseline
    receipt = v.validate(ROOT, IMPL, IMPL_NAME, "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    assert set(receipt["files"]) == set(baseline) | {"references/integration.md"}
    original = output(ROOT / ".github/skills" / IMPL_NAME / "SKILL.md")
    proposed = output(IMPL / "SKILL.md")
    assert proposed == original
    assert list(proposed["task_completion_output"]) == list(original["task_completion_output"])
    assert proposed["task_completion_output"]["task_output_links"] == ["src/", "tests/"]
    entry = (IMPL / "SKILL.md").read_text()
    assert entry.count("## Purpose") == 1 and entry.count("## Output Result") == 1
    procedure = ET.fromstring(re.search(r"<procedure.*?</procedure>", entry, re.S)[0])
    assert len(procedure.findall(".//action")) == 6
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", entry, re.S)[0])
    assert {f.attrib["name"] for f in init.findall("field")} >= {
        "task_id", "workflow.action", "workflow.extra_context_reference", "feature_id",
        "specification_link", "technical_design_link", "mockup_link", "program_type", "tech_stack",
        "git_strategy", "git_main_branch",
    }
    resources = "\n".join(p.read_text() for p in IMPL.rglob("*.md"))
    for obsolete in ("task_create.py", "task_update.py", "phase_0", "phase_6", 'type: "routing"',
                     "Execute Next Action", "stages.implement.implementation", "Linked Date >=",
                     "TDD Gate | N/A", "tracing-creator", "9-step process", "Rounds 2-4"):
        assert obsolete not in resources


def test_implementation_actual_config_semantic_routing_specials_tdd_tracing():
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["implement"]["actions"]["implementation"]
    assert action["optional"] is False
    assert action["deliverables"] == ["$output:impl-files", "$output-folder:impl-folder"]
    assert {k for k, v in action["action_context"].items() if v["required"]} == {"specification", "tech-design"}
    js = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"implementation:.*skill: '" + IMPL_NAME + "'", js)
    config = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())["stages"]["implement"]
    assert "code_implementation" in config and "implementation" not in config
    assert config["code_implementation"]["x-ipe-tool-implementation-html5"] is True
    entry = (IMPL / "SKILL.md").read_text()
    for clause in ("stages.implement.code_implementation", "metadata-only", "undeclared", "No force-enable general",
                   "sequentially", "semantically", "before scenario generation and semantic routing",
                   "original Assert clauses", "fail before", "regression", "every scoped AC",
                   "relevant inputs", "existing tracing infrastructure", "no mandatory setup",
                   "impl-files", "file array", "scalar directory", "read-only resume", "not measured",
                   "Human and hybrid require human completion/route confirmation", "no chasing activity counts"):
        assert clause in entry
    assert entry.index("<name>Special Delegation Gate</name>") < entry.index("<name>Generate AAA Scenarios</name>")
    assert entry.index("x-ipe-meta-skill-creator", entry.index("<procedure")) < entry.index("<name>Generate AAA Scenarios</name>")


@pytest.fixture
def implementation_project(design_project):
    project, state_path, record, prior = design_project
    assert write_design(project, record, prior)[0].returncode == 0
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Designed"}')[0].returncode == 0
    paths = ["src/status/badge.js", "src/status/select-label.js", "tests/status/badge.test.js"]
    for path in paths:
        target = project / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("// authored implementation-path fixture; no runtime claim\n")
    state = json.loads(state_path.read_text())
    state["features"][0]["implement"]["actions"]["implementation"]["context"] = {
        "specification": record["specification_link"], "tech-design": prior["tech-design"],
    }
    state_path.write_text(json.dumps(state))
    return project, state_path, record, {"impl-files": paths, "impl-folder": "src/status"}


def write_implementation(project, record, links):
    return run_helper(project, "workflow_update_action.py", "--workflow", "pilot", "--action", "implementation",
                      "--feature-id", record["feature_id"], "--status", "done", "--deliverables", json.dumps(links), "--format", "json")


def test_implementation_actual_file_array_folder_schema4_and_readonly_resume(implementation_project):
    project, state_path, record, links = implementation_project
    before = json.loads(state_path.read_text())
    result, payload = write_implementation(project, record, links)
    assert result.returncode == 0 and payload["success"]
    read_result, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot", "--format", "json")
    assert read_result.returncode == 0 and state["schema_version"] == "4.0"
    action = state["features"][0]["implement"]["actions"]["implementation"]
    assert action["status"] == "done" and action["deliverables"] == links
    assert action["context"] == before["features"][0]["implement"]["actions"]["implementation"]["context"]
    assert state["features"][0]["implement"]["actions"]["technical_design"] == before["features"][0]["implement"]["actions"]["technical_design"]
    assert all((project / path).is_file() for path in links["impl-files"])
    assert (project / links["impl-folder"]).is_dir()
    assert (project / "tests").is_dir()  # impl-files can include files outside the browsing impl-folder
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Implemented"}')[0].returncode == 0
    board = project / "x-ipe-docs/planning/features/features.json"
    frozen = state_path.read_bytes(), board.read_bytes()
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    _, feature = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert feature["data"]["feature"]["status"] == "Implemented"
    assert frozen == (state_path.read_bytes(), board.read_bytes())
    assert not (project / "x-ipe-docs/planning/tasks").exists()


@pytest.mark.parametrize("defect", ["folder-array", "extra-tag", "empty-element", "nonstring-element", "missing-feature", "locked"])
def test_implementation_actual_helper_rejections_preserve_bytes(implementation_project, defect):
    project, state_path, record, links = implementation_project
    if defect == "folder-array":
        links["impl-folder"] = [links["impl-folder"]]
    elif defect == "extra-tag":
        links["goal"] = "invented"
    elif defect == "empty-element":
        links["impl-files"].append("")
    elif defect == "nonstring-element":
        links["impl-files"].append(7)
    elif defect == "missing-feature":
        record["feature_id"] = "FEATURE-999-A"
    else:
        state = json.loads(state_path.read_text())
        state["shared"]["requirement"]["actions"]["feature_breakdown"]["status"] = "pending"
        state["features"][0]["implement"]["status"] = "locked"
        state_path.write_text(json.dumps(state))
    frozen = state_path.read_bytes()
    result, payload = write_implementation(project, record, links)
    assert result.returncode != 0 and not payload["success"]
    assert state_path.read_bytes() == frozen


@pytest.mark.parametrize("links", [
    {"impl-files": [], "impl-folder": "src/status"},
    {"impl-files": ["missing.js"], "impl-folder": "missing-folder"},
    {"impl-files": ["src/", "tests/"], "impl-folder": "src/status"},
    {"impl-files": ["src/status/badge.js"]},
])
def test_implementation_permissive_writer_not_completion(implementation_project, links):
    project, state_path, record, _ = implementation_project
    state = json.loads(state_path.read_text())
    actions = state["features"][0]["implement"]["actions"]
    actions["technical_design"]["status"] = "pending"
    actions["implementation"]["context"] = {}
    state_path.write_text(json.dumps(state))
    result, payload = write_implementation(project, record, links)
    assert result.returncode == 0 and payload["success"]  # characterize actual helper; NOT domain acceptance
    integration = (IMPL / "references/integration.md").read_text()
    for clause in ("writer success alone is insufficient", "nonempty file array", "technical_design action `done`",
                   "src/ and tests/ are directories", "empty arrays", "outside the browsing directory"):
        assert clause in integration


def test_implementation_revision_evidence_invalidates_only_relevant_inputs(tmp_path):
    relevant = [tmp_path / name for name in ("spec.md", "technical-design.md", "badge.js", "badge.test.js", "tools.json", "mockup.html")]
    for path in relevant:
        path.write_text("approved fixture revision\n")
    snapshot = lambda: {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in relevant}
    evidence = snapshot()
    (tmp_path / "unrelated.md").write_text("unrelated dirty documentation\n")
    assert snapshot() == evidence
    for path in relevant:
        original = path.read_bytes()
        path.write_bytes(original + b"authorized relevant delta\n")
        assert snapshot() != evidence
        path.write_bytes(original)
    assert snapshot() == evidence
    guidelines = (IMPL / "references/implementation-guidelines.md").read_text()
    assert "relevant inputs" in guidelines and "timestamps alone" in guidelines


def test_implementation_advanced_cr_status_and_identity_preserved(implementation_project):
    project, state_path, record, links = implementation_project
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Completed"}')[0].returncode == 0
    _, before = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert write_implementation(project, record, links)[0].returncode == 0
    _, after = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert before["data"]["feature"] == after["data"]["feature"]


@pytest.mark.parametrize("meta", [META, IMPL_META])
def test_downstream_metadata_current_state_and_yaml_closure(meta):
    text = (meta / "skill-meta.md").read_text()
    blocks = re.findall(r"```yaml\n(.*?)\n```", text, re.S)
    assert len(blocks) == 1
    parsed = yaml.safe_load(blocks[0])
    assert parsed["skill_name"] == meta.name
    assert parsed["task_id"] == "TASK-6749"
    assert "version_history" in parsed
    assert parsed["inputs"]["required"][2]["name"] == "process_preference.interaction_mode"
    if meta == META or (meta / "publication-receipt-goal-TASK-6749.json").exists():
        assert parsed["publication_state"] == "published" and parsed["version_history"]
    else:
        assert parsed["publication_state"] == "candidate_ready" and parsed["version_history"] == []
        assert parsed["independent_review"] == "pending_main_reviewer"


def test_implementation_actual_tool_io_and_red_adapter_not_live_migration():
    html5 = (ROOT / ".github/skills/x-ipe-tool-implementation-html5/SKILL.md").read_text()
    assert "<field name=\"feature_context.mockup_link\"" in html5
    operation = html5.split("### Operation: implement", 1)[1]
    assert operation.index("3. IMPLEMENT") < operation.index("4. WRITE tests")
    guidelines = (IMPL / "references/implementation-guidelines.md").read_text()
    block = re.search(r"```yaml\n(tool_skill_input:.*?)\n```", guidelines, re.S)[1]
    # The @backend example is illustrative text, not itself valid standalone YAML.
    assert "    mockup_link:" in block and "\n  mockup_link:" not in block
    assert "orchestrator supplies/runs relevant" in guidelines
    assert "before invoking them" in guidelines and "async" in guidelines


ACCEPT_NAME = "x-ipe-task-based-feature-acceptance-test"
ACCEPT_META = ROOT / "x-ipe-docs/skill-meta" / ACCEPT_NAME
ACCEPT = ACCEPT_META / "candidate"
ACCEPT_COVERAGE = ("Source / Parent Goal", "Story / Subgoal", "AC ID", "TC / Type",
                   "Original Assertions", "Evidence / Revision", "Delivery State", "Outcome State")


def acceptance_example():
    return (ACCEPT / "references/examples.md").read_text().split("## 2.", 1)[0]


def check_acceptance(text):
    assert rows(text, GOAL_COLUMNS) == rows(implementation_example(), GOAL_COLUMNS)
    mapping = rows(text, ACCEPT_COVERAGE)
    assert len(mapping) == 2
    assert {r["AC ID"] for r in mapping} == {"AC-061-A-01", "AC-061-A-02"}
    for row in mapping:
        assert all(row.values())
        assert row["Source / Parent Goal"] == "FR-061-01; explicit badge request"
        assert row["Story / Subgoal"] == "US-061-A-01"
        assert "frontend-ui" in row["TC / Type"]
        assert "no controls/mutation" in row["Original Assertions"]
        assert row["Evidence / Revision"] == "not executed; relevant input hashes required"
        assert row["Delivery State"] == "planned"
        assert row["Outcome State"] == "not measured"
    return mapping


def test_acceptance_authored_goal_ac_and_complete_scaffold(tmp_path):
    check_acceptance(acceptance_example())
    scaffold = (ACCEPT / "templates/acceptance-test-cases.md").read_text()
    rendered = render_table_from_scaffold(scaffold, GOAL_COLUMNS, rows(acceptance_example(), GOAL_COLUMNS))
    rendered = render_table_from_scaffold(rendered, ACCEPT_COVERAGE, rows(acceptance_example(), ACCEPT_COVERAGE))
    report = tmp_path / "acceptance-test-cases.md"
    report.write_text(rendered)
    check_acceptance(report.read_text())
    for clause in ("frontend-ui", "backend-api", "unit", "integration", "structured-review",
                   "CLI", "library", "Blocked", "not measured", "acceptance_evidence",
                   "Original Assertions", "Environment", "Relevant Inputs", "Refactor"):
        assert clause in scaffold
    assert "Chrome DevTools MCP is available" not in scaffold  # not universal prerequisite


@pytest.mark.parametrize("defect", ["missing", "orphan", "source", "assertion", "false-delivery", "false-outcome"])
def test_acceptance_negative_authored_claims(defect):
    text = acceptance_example()
    if defect == "missing":
        text = "\n".join(l for l in text.splitlines() if not l.startswith("| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02"))
    elif defect == "orphan":
        text = text.replace("| AC-061-A-02 | TC", "| AC-UNKNOWN | TC")
    elif defect == "source":
        text = text.replace("FR-061-01; explicit badge request", "invented source", 1)
    elif defect == "assertion":
        text = text.replace("no controls/mutation", "label only")
    elif defect == "false-delivery":
        text = text.replace("| planned |", "| verified engineering delivery |", 1)
    else:
        text = text.replace("| not measured |", "| observed stakeholder outcome |", 1)
    with pytest.raises(AssertionError):
        check_acceptance(text)


def test_acceptance_all_resources_config_action_outputs_and_owner():
    entry = (ACCEPT / "SKILL.md").read_text()
    resources = "\n".join(p.read_text() for p in ACCEPT.rglob("*.md"))
    receipt = validate_resources(validator(), ROOT, ACCEPT, ACCEPT_NAME, "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    baseline = json.loads((ACCEPT_META / "baseline-goal-TASK-6749.json").read_text())
    published = ACCEPT_META / "publication-receipt-goal-TASK-6749.json"
    if published.exists():
        publication = json.loads(published.read_text())
        assert publication["baseline"] == baseline and publication["byte_parity"] is True
        current = current_publication(ACCEPT_NAME)
        assert current["files"] == receipt["files"]
        assert current["candidate_hash"] == receipt["candidate_hash"]
        assert recovered_publication(ACCEPT_NAME)["baseline_hash"] == publication["candidate_hash"]
        assert resource_inventory(ROOT / ".github/skills" / ACCEPT_NAME) == resource_inventory(ACCEPT)
    else:
        assert validator().manifest(validator().tree_bytes(ROOT / ".github/skills" / ACCEPT_NAME, ROOT)) == baseline
    assert set(receipt["files"]) == set(baseline) | {"references/integration.md", "scripts/verify_evidence.py"}
    original = output(ROOT / ".github/skills" / ACCEPT_NAME / "SKILL.md")["task_completion_output"]
    proposed = output(ACCEPT / "SKILL.md")["task_completion_output"]
    assert list(original) == list(proposed)
    for key, value in original.items():
        if key != "process_preference":
            assert proposed[key] == value
    assert proposed["process_preference"] == {"interaction_mode": "{from input process_preference.interaction_mode}"}
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", entry, re.S)[0])
    fields = {f.attrib["name"]: "".join(f.itertext()) + f.attrib.get("source", "") for f in init.findall("field")}
    assert "implementation_files" in fields and "impl-files" in fields["implementation_files"]
    assert "impl-files" not in fields["technical_design_link"]
    for clause in ("stages.validation.acceptance_test", "only literal true", "no force-enable",
                   "Orient/Plan", "without recursively dispatching", "actual browser",
                   "all scoped ACs", "original assertions", "not measured", "not goal achievement",
                   "acceptance_testing", "test-report", "test-folder", "conditional", "mandatory",
                   "agent-authored skip", "one owner", "CLI", "library"):
        assert clause in resources
    for obsolete in ("task_create.py", "task_update.py", "phase_0", "phase_6", 'type: "routing"',
                     "Execute Next Action", "Linked Date >=", "stages.quality.testing", "all tools enabled by default"):
        assert obsolete not in resources
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["validation"]["actions"]["acceptance_testing"]
    assert action["deliverables"] == ["$output:test-report", "$output-folder:test-folder"]
    assert {k for k, v in action["action_context"].items() if v["required"]} == {"specification", "impl-files"}
    assert template["stages"]["validation"]["actions"]["code_refactor"]["optional"] is True
    js = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"acceptance_testing:.*skill: '" + ACCEPT_NAME + "'", js)


def evidence_verifier():
    path = ACCEPT / "scripts/verify_evidence.py"
    return load_source(path, "acceptance_evidence_verifier")


@pytest.fixture
def acceptance_evidence(tmp_path):
    paths = {"source": ["source.md"], "specification": ["specification.md"],
             "code": ["src/cli.py"], "config": ["tools.json"], "test": ["tests/test_cli.py"],
             "evidence": ["results.txt"]}
    expected = {"feature_id": "FEATURE-061-A", "inputs": paths,
                "acs": {"AC-CLI": {"types": ["integration"],
                                    "assertions": ["exit 1", "stderr error", "no file mutation"]}}}
    for role, files in paths.items():
        for path in files:
            p = tmp_path / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(role + " approved fixture bytes\n")
    record = {"feature_id": expected["feature_id"],
              "inputs": [{"role": role, "path": path, "sha256": hashlib.sha256((tmp_path / path).read_bytes()).hexdigest()}
                         for role, files in paths.items() for path in files],
              "cases": [{"tc_id": "TC-CLI", "ac_ids": ["AC-CLI"], "test_type": "integration", "status": "Pass",
                         "assertions": expected["acs"]["AC-CLI"]["assertions"], "command_or_review": "fixture-only CLI check",
                         "result": "fixture exit 1 and error; no mutation", "environment": "temporary project; not a stakeholder",
                         "evidence_paths": ["results.txt"]}]}
    report = tmp_path / "acceptance-test-cases.md"
    report.write_text("# Acceptance report\n\n```yaml\n" + yaml.safe_dump({"acceptance_evidence": record}, sort_keys=False) + "```\n")
    return tmp_path, report, expected, record


def test_acceptance_actual_evidence_cli_readonly_and_full_coverage(acceptance_evidence):
    root, report, expected, record = acceptance_evidence
    module = evidence_verifier()
    assert module.verify(root, report, expected)["reusable"] is True
    manifest = root / "expected.json"
    manifest.write_text(json.dumps(expected))
    frozen = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    result = subprocess.run([sys.executable, "-B", str(ACCEPT / "scripts/verify_evidence.py"),
                             "--project-root", str(root), "--report", str(report), "--expected", str(manifest)],
                            text=True, capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    assert result.returncode == 0 and json.loads(result.stdout)["reusable"] is True
    assert frozen == {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert "semantic" in json.loads(result.stdout)["limits"]


@pytest.mark.parametrize("role", ["source", "specification", "code", "config", "test", "evidence"])
def test_acceptance_reuse_rehashes_each_explicit_relevant_role(acceptance_evidence, role):
    root, report, expected, record = acceptance_evidence
    (root / "unrelated.md").write_text("unrelated dirty document")
    module = evidence_verifier()
    assert module.verify(root, report, expected)["reusable"] is True
    path = root / expected["inputs"][role][0]
    path.write_bytes(path.read_bytes() + b"changed relevant bytes\n")
    result = module.verify(root, report, expected)
    assert result["reusable"] is False and result["errors"]


@pytest.mark.parametrize("defect", ["omit-source", "omit-specification", "omit-code", "omit-config", "omit-test",
                                  "wrong-feature", "missing-ac", "orphan-ac", "wrong-type", "weaken-assertion",
                                  "blocked", "partial", "no-command", "no-result", "no-environment", "no-evidence",
                                  "traversal", "symlink", "extra-input"])
def test_acceptance_reuse_rejects_false_or_incomplete_evidence(acceptance_evidence, defect):
    root, report, expected, original = acceptance_evidence
    record = copy.deepcopy(original)
    case = record["cases"][0]
    if defect.startswith("omit-"):
        record["inputs"] = [r for r in record["inputs"] if r["role"] != defect[5:]]
    elif defect == "wrong-feature": record["feature_id"] = "FEATURE-999-A"
    elif defect == "missing-ac": record["cases"] = []
    elif defect == "orphan-ac": case["ac_ids"] = ["UNKNOWN"]
    elif defect == "wrong-type": case["test_type"] = "structured-review"
    elif defect == "weaken-assertion": case["assertions"].remove("no file mutation")
    elif defect in ("blocked", "partial"): case["status"] = defect.title()
    elif defect == "no-command": case["command_or_review"] = ""
    elif defect == "no-result": case["result"] = ""
    elif defect == "no-environment": case["environment"] = ""
    elif defect == "no-evidence": case["evidence_paths"] = []
    elif defect == "traversal": record["inputs"][0]["path"] = "../outside.md"
    elif defect == "symlink":
        path = root / expected["inputs"]["source"][0]
        path.unlink()
        path.symlink_to(root / "specification.md")
    else: record["inputs"].append({"role": "source", "path": "unknown.md", "sha256": "0" * 64})
    report.write_text("# Acceptance\n```yaml\n" + yaml.safe_dump({"acceptance_evidence": record}) + "```\n")
    result = evidence_verifier().verify(root, report, expected)
    assert result["reusable"] is False and result["errors"]


@pytest.fixture
def acceptance_project(implementation_project):
    project, state_path, record, prior = implementation_project
    assert write_implementation(project, record, prior)[0].returncode == 0
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Implemented"}')[0].returncode == 0
    folder = str(Path(record["specification_link"]).parent)
    report = project / folder / "acceptance-test-cases.md"
    report.write_text(acceptance_example())  # authored path fixture, not executed badge acceptance
    state = json.loads(state_path.read_text())
    state["features"][0]["validation"]["actions"]["acceptance_testing"]["context"] = {
        "specification": record["specification_link"], "impl-files": prior["impl-files"],
    }
    state_path.write_text(json.dumps(state))
    return project, state_path, record, {"test-report": f"{folder}/acceptance-test-cases.md", "test-folder": "tests/status"}


def write_acceptance(project, record, links):
    return run_helper(project, "workflow_update_action.py", "--workflow", "pilot", "--action", "acceptance_testing",
                      "--feature-id", record["feature_id"], "--status", "done", "--deliverables", json.dumps(links), "--format", "json")


def test_acceptance_actual_helper_tags_context_conditional_refactor_and_readonly_resume(acceptance_project):
    project, state_path, record, links = acceptance_project
    before = json.loads(state_path.read_text())
    result, payload = write_acceptance(project, record, links)
    assert result.returncode == 0 and payload["success"]
    _, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    action = state["features"][0]["validation"]["actions"]["acceptance_testing"]
    assert action["status"] == "done" and action["deliverables"] == links
    assert action["context"] == before["features"][0]["validation"]["actions"]["acceptance_testing"]["context"]
    assert action["next_actions_suggested"] == ["feature_closing", "code_refactor"]
    assert state["features"][0]["validation"]["actions"]["code_refactor"]["status"] == "skipped"
    assert state["features"][0]["validation"]["actions"]["feature_closing"]["status"] == "pending"
    assert (project / links["test-report"]).is_file() and (project / links["test-folder"]).is_dir()
    # Owner/category transition is separate; helper writes do not prove report results.
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Tested"}')[0].returncode == 0
    board = project / "x-ipe-docs/planning/features/features.json"
    frozen = state_path.read_bytes(), board.read_bytes()
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    _, feature = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert feature["data"]["feature"]["status"] == "Tested"
    assert frozen == (state_path.read_bytes(), board.read_bytes())
    assert not (project / "x-ipe-docs/planning/tasks").exists()


@pytest.mark.parametrize("defect", ["folder-array", "extra-tag", "missing-feature", "locked"])
def test_acceptance_actual_helper_rejections_preserve_state(acceptance_project, defect):
    project, state_path, record, links = acceptance_project
    if defect == "folder-array": links["test-folder"] = [links["test-folder"]]
    elif defect == "extra-tag": links["goal-evidence"] = "invented"
    elif defect == "missing-feature": record["feature_id"] = "FEATURE-999-A"
    else:
        state = json.loads(state_path.read_text())
        state["features"][0]["implement"]["actions"]["implementation"]["status"] = "pending"
        state["features"][0]["validation"]["status"] = "locked"
        state_path.write_text(json.dumps(state))
    frozen = state_path.read_bytes()
    result, payload = write_acceptance(project, record, links)
    assert result.returncode != 0 and not payload["success"]
    assert state_path.read_bytes() == frozen


def test_acceptance_permissive_writer_never_proves_acceptance_or_closing(acceptance_project):
    project, state_path, record, _ = acceptance_project
    state = json.loads(state_path.read_text())
    state["features"][0]["validation"]["status"] = "in_progress"
    state["features"][0]["validation"]["actions"]["acceptance_testing"]["context"] = {}
    state["features"][0]["implement"]["actions"]["implementation"]["status"] = "pending"
    state_path.write_text(json.dumps(state))
    result, payload = write_acceptance(project, record, {"test-report": "missing.md"})
    assert result.returncode == 0 and payload["success"]  # gap, not a domain pass
    integration = (ACCEPT / "references/integration.md").read_text()
    assert "writer success alone is insufficient" in integration
    assert "No need means closing" in integration and "mandatory" in integration
    assert "not goal achievement" in (ACCEPT / "SKILL.md").read_text()


def test_acceptance_advanced_completed_status_preserved(acceptance_project):
    project, state_path, record, links = acceptance_project
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Completed"}')[0].returncode == 0
    _, before = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert write_acceptance(project, record, links)[0].returncode == 0
    _, after = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert before["data"]["feature"] == after["data"]["feature"]


@pytest.mark.parametrize("role", ["source", "specification", "code", "config", "test", "evidence"])
def test_acceptance_reuse_expected_inventory_cannot_omit_required_role(acceptance_evidence, role):
    root, report, expected, record = acceptance_evidence
    incomplete = copy.deepcopy(expected)
    del incomplete["inputs"][role]
    assert evidence_verifier().verify(root, report, incomplete)["reusable"] is False


@pytest.mark.parametrize("defect", ["additional-relevant-input", "additional-ac", "additional-type", "empty-acs", "duplicate-input", "duplicate-tc", "malformed-yaml"])
def test_acceptance_reuse_full_current_scope_and_unique_records(acceptance_evidence, defect):
    root, report, expected, record = acceptance_evidence
    expected = copy.deepcopy(expected)
    record = copy.deepcopy(record)
    if defect == "additional-relevant-input":
        (root / "parent-delta.md").write_text("authorized current parent delta")
        expected["inputs"]["source"].append("parent-delta.md")
    elif defect == "additional-ac":
        expected["acs"]["AC-SECOND"] = {"types": ["unit"], "assertions": ["public API error"]}
    elif defect == "additional-type": expected["acs"]["AC-CLI"]["types"].append("unit")
    elif defect == "empty-acs": expected["acs"] = {}
    elif defect == "duplicate-input": record["inputs"].append(record["inputs"][0])
    elif defect == "duplicate-tc": record["cases"].append(record["cases"][0])
    else:
        report.write_text("```yaml\nacceptance_evidence: [\n```\n")
        assert evidence_verifier().verify(root, report, expected)["reusable"] is False
        return
    report.write_text("# Acceptance\n```yaml\n" + yaml.safe_dump({"acceptance_evidence": record}) + "```\n")
    assert evidence_verifier().verify(root, report, expected)["reusable"] is False


def test_acceptance_evidence_cli_nonzero_on_stale_input_without_writes(acceptance_evidence):
    root, report, expected, record = acceptance_evidence
    manifest = root / "expected.json"
    manifest.write_text(json.dumps(expected))
    (root / "tools.json").write_text("changed tool authorization")
    frozen = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    result = subprocess.run([sys.executable, "-B", str(ACCEPT / "scripts/verify_evidence.py"),
                             "--project-root", str(root), "--report", str(report), "--expected", str(manifest)],
                            text=True, capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    assert result.returncode == 1 and json.loads(result.stdout)["reusable"] is False
    assert "tools.json" in json.loads(result.stdout)["errors"][0]
    assert frozen == {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_acceptance_actual_closing_helper_allows_optional_refactor_untouched(acceptance_project):
    project, state_path, record, links = acceptance_project
    assert write_acceptance(project, record, links)[0].returncode == 0
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                                 "--action", "feature_closing", "--feature-id", record["feature_id"], "--status", "done")
    assert result.returncode == 0 and payload["success"]  # Still not semantic proof of acceptance.
    _, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    assert state["features"][0]["validation"]["actions"]["code_refactor"]["status"] == "skipped"
    integration = (ACCEPT / "references/integration.md").read_text()
    assert "code_refactor optional" in integration
    assert "implementation" in integration and "evidence remain required" in integration


def test_acceptance_actual_feedback_gate_remains_locked_without_refactor(acceptance_project):
    project, state_path, record, links = acceptance_project
    assert write_acceptance(project, record, links)[0].returncode == 0
    frozen = state_path.read_bytes()
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                                 "--action", "human_playground", "--feature-id", record["feature_id"], "--status", "done")
    assert result.returncode != 0 and payload["error"] == "STAGE_LOCKED"
    assert state_path.read_bytes() == frozen


def test_acceptance_metadata_candidate_only_and_complete_contract():
    text = (ACCEPT_META / "skill-meta.md").read_text()
    blocks = re.findall(r"```yaml\n(.*?)\n```", text, re.S)
    assert len(blocks) == 1
    meta = yaml.safe_load(blocks[0])
    current = validate_resources(validator(), ROOT, ACCEPT, ACCEPT_NAME, "x-ipe-task-based")
    assert current_publication(ACCEPT_NAME)["files"] == current["files"]
    receipt = json.loads((ACCEPT_META / "validation-receipt-goal-TASK-6749.json").read_text())
    assert meta["skill_name"] == ACCEPT_NAME and meta["task_id"] == "TASK-6749"
    assert meta["candidate_hash"] == receipt["candidate_hash"]
    publication_path = ACCEPT_META / "publication-receipt-goal-TASK-6749.json"
    if publication_path.exists():
        publication = json.loads(publication_path.read_text())
        assert meta["publication_state"] == "published"
        assert meta["independent_review"] == "completed_main_reviewer"
        assert meta["version_history"] and publication["byte_parity"] is True
        assert publication["candidate_hash"] == receipt["candidate_hash"]
        assert publication["files"] == receipt["files"]
        assert publication["baseline"] == json.loads((ACCEPT_META / "baseline-goal-TASK-6749.json").read_text())
        assert resource_inventory(ACCEPT) == resource_inventory(ROOT / ".github/skills" / ACCEPT_NAME)
    else:
        assert meta["publication_state"] == "candidate_ready"
        assert meta["independent_review"] == "pending_main_reviewer"
        assert meta["version_history"] == []
        assert not list(ACCEPT_META.glob("publication-receipt*"))
    assert meta["inputs"]["required"][2]["name"] == "process_preference.interaction_mode"
    for name in ("triggers", "not_for", "workflow", "inputs", "outputs", "acceptance_criteria", "dependencies", "test_scenarios", "evaluation"):
        assert meta[name]
    assert not list(ACCEPT_META.glob("promotion-receipt*"))


@pytest.mark.parametrize("test_type", ["frontend-ui", "backend-api", "unit", "integration", "structured-review"])
def test_acceptance_same_evidence_schema_for_every_original_type(acceptance_evidence, test_type):
    """Execute the consistency API, not the fictional feature's typed boundary."""
    root, report, expected, record = acceptance_evidence
    expected["acs"]["AC-CLI"]["types"] = [test_type]
    record["cases"][0]["test_type"] = test_type
    report.write_text("```yaml\n" + yaml.safe_dump({"acceptance_evidence": record}) + "```\n")
    frozen = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    result = evidence_verifier().verify(root, report, expected)
    assert result["reusable"] is True, result["errors"]
    assert set(result) == {"reusable", "errors", "limits"}
    assert frozen == {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("test_type", ["frontend-ui", "backend-api", "unit", "integration", "structured-review"])
def test_acceptance_cross_type_assertion_borrowing_rejected(acceptance_evidence, test_type):
    root, report, expected, record = acceptance_evidence
    other_type = "unit" if test_type != "unit" else "integration"
    expected["acs"]["AC-CLI"]["types"] = [test_type, other_type]
    first = record["cases"][0]
    second = copy.deepcopy(first)
    first["test_type"] = test_type
    first["assertions"] = ["exit 1"]
    second.update(tc_id="TC-SECOND", test_type=other_type)
    record["cases"].append(second)
    report.write_text("```yaml\n" + yaml.safe_dump({"acceptance_evidence": record}) + "```\n")
    result = evidence_verifier().verify(root, report, expected)
    assert result["reusable"] is False, "Another test type must not supply missing original clauses"


def test_acceptance_same_type_split_cases_preserve_all_clauses(acceptance_evidence):
    root, report, expected, record = acceptance_evidence
    first = record["cases"][0]
    second = copy.deepcopy(first)
    first["assertions"] = ["exit 1"]
    second.update(tc_id="TC-SECOND", assertions=["stderr error", "no file mutation"])
    record["cases"].append(second)
    report.write_text("```yaml\n" + yaml.safe_dump({"acceptance_evidence": record}) + "```\n")
    assert evidence_verifier().verify(root, report, expected)["reusable"] is True


ALL_TYPE_ASSERTIONS = {
    "TC-062-UI": ("AC-062-UI", "frontend-ui", "snapshot label; no controls/mutation; console free of runtime errors"),
    "TC-062-API": ("AC-062-API", "backend-api", "GET status 200; approved body; no storage mutation"),
    "TC-062-LIB": ("AC-062-LIB", "unit", "public import and return; documented invalid-input error; no argument mutation"),
    "TC-062-CLI": ("AC-062-CLI", "integration", "actual executable exit/stdout; invalid input exit 1/stderr; no file mutation"),
    "TC-062-FLOW": ("AC-062-FLOW", "integration", "real component handoff yields same snapshot; isolated setup/cleanup; no state mutation"),
    "TC-062-REVIEW": ("AC-062-SKILL", "structured-review", "complete resources; original output and same-owner lifecycle; actual app tags and contexts"),
    "TC-062-HELPER": ("AC-062-SKILL", "integration", "actual validator/helper exits and results; required error rejection; no source mutation"),
}


def all_type_acceptance_example():
    return (ACCEPT / "references/examples.md").read_text().split("## 8.", 1)[1]


def check_all_type_acceptance(text):
    goals = rows(text, GOAL_COLUMNS)
    assert len(goals) == 1 and goals[0]["Goal ID"] == "US-062-01"
    assert goals[0]["Parent / Source"] == "FR-062-01; authored diagnostic request"
    assert goals[0]["Outcome State"] == "not measured"
    mapping = rows(text, ACCEPT_COVERAGE)
    assert len(mapping) == len(ALL_TYPE_ASSERTIONS)
    expected_acs = {contract[0] for contract in ALL_TYPE_ASSERTIONS.values()}
    assert {ac.strip() for ac in goals[0]["AC Links"].split(",")} == expected_acs
    observed = set()
    for row in mapping:
        tc, kind = row["TC / Type"].split(" / ")
        assert tc not in observed
        observed.add(tc)
        assert (row["AC ID"], kind, row["Original Assertions"]) == ALL_TYPE_ASSERTIONS[tc]
        assert row["Source / Parent Goal"] == goals[0]["Parent / Source"]
        assert row["Story / Subgoal"] == goals[0]["Goal ID"]
        assert row["Evidence / Revision"] == "not executed; relevant input hashes required"
        assert row["Delivery State"] == "planned" and row["Outcome State"] == "not measured"
    assert observed == set(ALL_TYPE_ASSERTIONS)


def test_acceptance_all_type_source_ac_assertions_render_same_report_schema(tmp_path):
    text = all_type_acceptance_example()
    check_all_type_acceptance(text)
    scaffold = (ACCEPT / "templates/acceptance-test-cases.md").read_text()
    rendered = render_table_from_scaffold(scaffold, GOAL_COLUMNS, rows(text, GOAL_COLUMNS))
    rendered = render_table_from_scaffold(rendered, ACCEPT_COVERAGE, rows(text, ACCEPT_COVERAGE))
    target = tmp_path / "acceptance-test-cases.md"
    target.write_text(rendered)
    check_all_type_acceptance(target.read_text())
    assert list(tmp_path.iterdir()) == [target]


@pytest.mark.parametrize("tc", list(ALL_TYPE_ASSERTIONS))
def test_acceptance_all_type_omitted_original_clause_rejected(tc):
    text = all_type_acceptance_example()
    original = ALL_TYPE_ASSERTIONS[tc][2]
    weakened = original.rsplit("; ", 1)[0]
    with pytest.raises(AssertionError):
        check_all_type_acceptance(text.replace(original, weakened, 1))


CLOSE_NAME = "x-ipe-task-based-feature-closing"
CLOSE_META = ROOT / "x-ipe-docs/skill-meta" / CLOSE_NAME
CLOSE = CLOSE_META / "candidate"


def closing_example():
    return (CLOSE / "references/examples.md").read_text().split("## 2.", 1)[0]


def check_closing_plan(text):
    # A plan may not be relabeled as delivered/observed/approved on closing.
    assert rows(text, GOAL_COLUMNS) == rows(acceptance_example(), GOAL_COLUMNS)
    assert rows(text, ACCEPT_COVERAGE) == rows(acceptance_example(), ACCEPT_COVERAGE)
    assert "Outcome gap: no operator observation" in text
    assert "Release: not requested; no commit/push/PR" in text


def test_closing_complete_inventory_output_schema_and_lifecycle():
    v = validator()
    baseline = json.loads((CLOSE_META / "baseline-goal-TASK-6749.json").read_text())
    published = json.loads((CLOSE_META / "publication-receipt-goal-TASK-6749.json").read_text())
    assert published["baseline"] == baseline
    receipt = v.validate(ROOT, CLOSE, CLOSE_NAME, "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    current = current_publication(CLOSE_NAME)
    assert current["files"] == receipt["files"] == v.manifest(v.tree_bytes(ROOT / ".github/skills" / CLOSE_NAME, ROOT))
    assert current["candidate_hash"] == receipt["candidate_hash"]
    assert recovered_publication(CLOSE_NAME)["baseline_hash"] == published["candidate_hash"]
    assert published["byte_parity"] is True and published["removed"] == []
    assert set(receipt["files"]) == set(baseline) | {"references/integration.md", "templates/closing-report.md"}
    for path in ("references/templates/pr-template.md", "references/templates/changelog-template.md"):
        assert (CLOSE / path).read_bytes() == (ROOT / ".github/skills" / CLOSE_NAME / path).read_bytes()
    original, proposed = output(ROOT / ".github/skills" / CLOSE_NAME / "SKILL.md"), output(CLOSE / "SKILL.md")
    assert original == proposed
    assert list(original["task_completion_output"]) == list(proposed["task_completion_output"])
    entry = (CLOSE / "SKILL.md").read_text()
    ET.fromstring(re.search(r"<procedure.*?</procedure>", entry, re.S)[0])
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", entry, re.S)[0])
    assert {f.attrib["name"] for f in init.findall("field")} >= {
        "task_id", "workflow.action", "workflow.extra_context_reference", "feature_id",
        "specification_path", "test_results", "git_strategy", "git_main_branch",
        "git_dev_branch", "optional_tools.readme_updator",
    }
    for obsolete in ("task_create.py", "task_update.py", "phase_0", "phase_6", 'type: "routing"',
                     "Execute Next Action", "git checkout", "git push origin", "Stage all feature changes",
                     "<name>Refactoring Analysis</name>", "All implementation code committed"):
        assert obsolete not in entry


def test_closing_goal_evidence_scaffold_and_honest_plan(tmp_path):
    text = closing_example()
    check_closing_plan(text)
    scaffold = (CLOSE / "templates/closing-report.md").read_text()
    rendered = render_table_from_scaffold(scaffold, GOAL_COLUMNS, rows(text, GOAL_COLUMNS))
    rendered = render_table_from_scaffold(rendered, ACCEPT_COVERAGE, rows(text, ACCEPT_COVERAGE))
    report = tmp_path / "closing-report.md"
    report.write_text(rendered + "\nOutcome gap: no operator observation\nRelease: not requested; no commit/push/PR\n")
    check_closing_plan(report.read_text())
    assert list(tmp_path.iterdir()) == [report]
    for section in ("Evidence Reuse", "Review", "Documentation Delta", "Outcome Gaps", "Release", "Workflow", "Quality"):
        assert section in scaffold


@pytest.mark.parametrize("defect", ["missing", "source", "assertion", "type", "false-delivery", "false-outcome", "invented-approval"])
def test_closing_negative_authored_evidence_claims(defect):
    text = closing_example()
    if defect == "missing":
        text = "\n".join(l for l in text.splitlines() if not l.startswith("| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02"))
    elif defect == "source": text = text.replace("FR-061-01; explicit badge request", "fabricated source", 1)
    elif defect == "assertion": text = text.replace("no controls/mutation", "label only", 1)
    elif defect == "type": text = text.replace("TC-061-01 / frontend-ui", "TC-061-01 / structured-review", 1)
    elif defect == "false-delivery": text = text.replace("| planned |", "| verified engineering delivery |", 1)
    elif defect == "false-outcome": text = text.replace("| not measured |", "| observed stakeholder outcome |", 1)
    else: text = text.replace("Outcome gap: no operator observation", "Stakeholder approved; outcome achieved", 1)
    with pytest.raises(AssertionError):
        check_closing_plan(text)


def test_closing_policy_gates_not_optional_semantic_acceptance():
    entry = (CLOSE / "SKILL.md").read_text()
    resources = "\n".join(p.read_text() for p in CLOSE.rglob("*.md") if "references/templates" not in str(p))
    for clause in ("Orient/Plan", "without recursively dispatching", "one owner", "all scoped ACs",
                   "original assertions", "Given/When/Then", "not measured", "actual stakeholder",
                   "no invented", "Implemented or Tested", "Completed", "same relevant hashes",
                   "not run twice", "independent review", "approved CR", "mislead", "no implementation",
                   "no compulsory refactoring analysis", "no automatic commit", "broad staging",
                   "human and hybrid", "message_context", "instruction_units", "execution_plan",
                   "feature_closing", "deliverables {}", "task artifact", "optional closing-report"):
            assert clause.casefold() in resources.casefold(), clause
    assert "x-ipe-tool-refactoring-analysis" not in entry
    assert "overall_quality_score < 7" not in resources


def write_closing(project, record, deliverables):
    return run_helper(project, "workflow_update_action.py", "--workflow", "pilot", "--action", "feature_closing",
                      "--feature-id", record["feature_id"], "--status", "done", "--deliverables", json.dumps(deliverables), "--format", "json")


@pytest.fixture
def closing_project(acceptance_project):
    project, state_path, record, links = acceptance_project
    assert write_acceptance(project, record, links)[0].returncode == 0
    report = project / Path(record["specification_link"]).parent / "closing-report.md"
    report.write_text(closing_example())  # authored path fixture, not semantic feature closing
    state = json.loads(state_path.read_text())
    state["features"][0]["validation"]["actions"]["feature_closing"]["context"] = {"specification": record["specification_link"]}
    state_path.write_text(json.dumps(state))
    return project, state_path, record, report


@pytest.mark.parametrize("status", ["Implemented", "Tested", "Completed"])
def test_closing_actual_empty_tags_done_readback_and_status_preservation(closing_project, status):
    project, state_path, record, report = closing_project
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", json.dumps({"status": status}))[0].returncode == 0
    result, payload = write_closing(project, record, {})
    assert result.returncode == 0 and payload["success"]
    _, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    action = state["features"][0]["validation"]["actions"]["feature_closing"]
    assert action["status"] == "done" and action["deliverables"] == {}
    assert action["context"] == {"specification": record["specification_link"]}
    assert "closing-report" not in action["deliverables"] and report.is_file()
    # This is deliberately the real writer's permissiveness, not domain closing:
    assert state["features"][0]["validation"]["actions"]["code_refactor"]["status"] == "skipped"
    _, feature = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert feature["data"]["feature"]["status"] == status  # writer does NOT complete board
    assert run_board(project, "feature_update.py", "--feature-id", record["feature_id"], "--updates", '{"status":"Completed"}')[0].returncode == 0
    board = project / "x-ipe-docs/planning/features/features.json"
    frozen = state_path.read_bytes(), board.read_bytes()
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    _, completed = run_board(project, "feature_query.py", "--feature-id", record["feature_id"])
    assert completed["data"]["feature"]["status"] == "Completed"
    assert frozen == (state_path.read_bytes(), board.read_bytes())
    assert not (project / "x-ipe-docs/planning/tasks").exists()


def test_closing_actual_runtime_service_and_template_agree_on_empty_tags(closing_project):
    from src.x_ipe.services.workflow_manager_service import WorkflowManagerService
    project, state_path, record, report = closing_project
    template = json.loads((project / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["validation"]["actions"]["feature_closing"]
    assert action["deliverables"] == [] and action["optional"] is False
    assert action["action_context"]["specification"]["required"] is True
    assert action["action_context"]["refactor-report"]["required"] is False
    service = WorkflowManagerService(str(project))
    frozen = state_path.read_bytes()
    assert service.validate_action_deliverables("feature_closing", {}) is True
    assert service.validate_action_deliverables("feature_closing", {"closing-report": str(report.relative_to(project))}) is False
    assert state_path.read_bytes() == frozen
    js = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"feature_closing:.*skill: '" + CLOSE_NAME + "'", js)


@pytest.mark.parametrize("defect", ["bogus-tag", "wrong-feature", "locked"])
def test_closing_actual_rejection_preserves_workflow(closing_project, defect):
    project, state_path, record, report = closing_project
    links = {}
    if defect == "bogus-tag": links = {"closing-report": str(report.relative_to(project))}
    elif defect == "wrong-feature": record["feature_id"] = "FEATURE-999-A"
    else:
        state = json.loads(state_path.read_text())
        state["features"][0]["validation"]["status"] = "locked"
        state["features"][0]["implement"]["actions"]["implementation"]["status"] = "pending"
        state_path.write_text(json.dumps(state))
    frozen = state_path.read_bytes()
    result, payload = write_closing(project, record, links)
    assert result.returncode != 0 and not payload["success"]
    assert payload["error"] == {"bogus-tag": "INVALID_DELIVERABLES", "wrong-feature": "FEATURE_NOT_FOUND", "locked": "STAGE_LOCKED"}[defect]
    assert state_path.read_bytes() == frozen


def test_closing_change_request_optional_report_absent_is_compatible(closing_project):
    project, state_path, record, _ = closing_project
    template = json.loads((project / "x-ipe-docs/config/workflow-template.json").read_text())
    context = template["stages"]["feedback"]["actions"]["change_request"]["action_context"]
    assert context["closing-report"]["required"] is False
    assert context["specification"]["required"] is True
    state = json.loads(state_path.read_text())
    # Explicitly open temporary stage to characterize context compatibility only;
    # NOT fabricated refactor completion or unlocking a production workflow.
    state["features"][0]["feedback"]["status"] = "in_progress"
    state_path.write_text(json.dumps(state))
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot", "--action", "change_request",
                                 "--feature-id", record["feature_id"], "--status", "in_progress", "--context", json.dumps({"specification": record["specification_link"]}))
    assert result.returncode == 0 and payload["success"]
    _, read = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    action = read["features"][0]["feedback"]["actions"]["change_request"]
    assert action["context"] == {"specification": record["specification_link"]}
    assert "closing-report" not in action["context"]


def test_closing_reuses_current_consistency_and_invalidates_changed_code(acceptance_evidence):
    root, report, expected, record = acceptance_evidence
    frozen = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert evidence_verifier().verify(root, report, expected)["reusable"] is True
    assert frozen == {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    (root / expected["inputs"]["code"][0]).write_text("authorized relevant implementation delta")
    assert evidence_verifier().verify(root, report, expected)["reusable"] is False
    # Existing helper consistency reused, no duplicate closing helper/schema.
    assert not (CLOSE / "scripts/verify_evidence.py").exists()


def test_closing_metadata_receipt_and_verified_promotion():
    text = (CLOSE_META / "skill-meta.md").read_text()
    blocks = re.findall(r"```yaml\n(.*?)\n```", text, re.S)
    assert len(blocks) == 1
    meta = yaml.safe_load(blocks[0])
    current = validator().validate(ROOT, CLOSE, CLOSE_NAME, "x-ipe-task-based")
    assert current_publication(CLOSE_NAME)["files"] == current["files"]
    receipt = json.loads((CLOSE_META / "validation-receipt-goal-TASK-6749.json").read_text())
    assert meta["task_id"] == "TASK-6749" and meta["publication_state"] == "published"
    assert meta["independent_review"] == "completed_main_reviewer"
    history = meta["version_history"][-1]
    assert history["task_id"] == "TASK-6749" and history["candidate_hash"] == receipt["candidate_hash"]
    assert (CLOSE_META / history["review"]).is_file()
    published = json.loads((CLOSE_META / history["publication"]).read_text())
    assert published["publication_state"] == "published" and published["byte_parity"] is True
    assert published["files"] == receipt["files"] and published["candidate_hash"] == receipt["candidate_hash"]
    assert meta["candidate_hash"] == receipt["candidate_hash"]
    assert json.loads((CLOSE_META / "validation-receipt-goal-TASK-6749.json").read_text()) == receipt
    for key in ("triggers", "not_for", "workflow", "inputs", "outputs", "acceptance_criteria", "dependencies", "test_scenarios", "evaluation"):
        assert meta[key]
    assert published["operation"] == "editor-promotion"  # Not a transactional publisher receipt.


def all_type_closing_example():
    return (CLOSE / "references/examples.md").read_text().split("## 8.", 1)[1]


def test_closing_all_original_types_render_without_claiming_execution(tmp_path):
    text = all_type_closing_example()
    check_all_type_acceptance(text)
    upstream = all_type_acceptance_example()
    assert rows(text, GOAL_COLUMNS) == rows(upstream, GOAL_COLUMNS)
    assert rows(text, ACCEPT_COVERAGE) == rows(upstream, ACCEPT_COVERAGE)
    scaffold = (CLOSE / "templates/closing-report.md").read_text()
    rendered = render_table_from_scaffold(scaffold, GOAL_COLUMNS, rows(text, GOAL_COLUMNS))
    rendered = render_table_from_scaffold(rendered, ACCEPT_COVERAGE, rows(text, ACCEPT_COVERAGE))
    report = tmp_path / "closing-report.md"
    report.write_text(rendered)
    check_all_type_acceptance(report.read_text())
    assert list(tmp_path.iterdir()) == [report]
    assert "blocked for delivery" in text
    assert "actual suitable current evidence" in text
    assert "Outcome remains not measured" in text


@pytest.mark.parametrize("tc", list(ALL_TYPE_ASSERTIONS))
def test_closing_all_type_original_clauses_cannot_be_dropped(tc):
    text = all_type_closing_example()
    original = ALL_TYPE_ASSERTIONS[tc][2]
    with pytest.raises(AssertionError):
        check_all_type_acceptance(text.replace(original, original.rsplit("; ", 1)[0], 1))


def test_closing_original_input_paths_docs_and_release_gates_retained():
    entry = (CLOSE / "SKILL.md").read_text()
    live = (ROOT / ".github/skills" / CLOSE_NAME / "SKILL.md").read_text()
    proposed = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", entry, re.S)[1])["input"]
    original = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", live, re.S)[1])["input"]
    assert list(proposed) == list(original)
    assert proposed["workflow"]["extra_context_reference"] == original["workflow"]["extra_context_reference"]
    for key in ("task_id", "task_based_skill", "category", "next_task_based_skill",
                "process_preference", "feature_phase", "feature_id", "feature_title",
                "feature_version", "git_strategy", "git_main_branch", "git_dev_branch",
                "specification_path", "optional_tools"):
        assert proposed[key] == original[key]
    for clause in ("README/API/changelog", "spec explanatory material/design/test documentation",
                   "protected dirty docs/history", "approved CR and fresh downstream validation",
                   "Default no commit/push/PR", "Required release without authority blocks",
                   "Main-branch-only no new branch/PR", "explicit required human approval",
                   "No new workflow_action/goal/outcome/release keys"):
        assert clause.casefold() in entry.casefold(), clause
    for path in ("references/templates/pr-template.md", "references/templates/changelog-template.md"):
        assert f".github/skills/{CLOSE_NAME}/{path}" in entry


def test_closing_publication_records_bind_current_receipt_and_preserve_readiness_history():
    meta_text = (CLOSE_META / "skill-meta.md").read_text()
    meta = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", meta_text, re.S)[1])
    cases = yaml.safe_load((CLOSE_META / "test-cases.yaml").read_text())
    handoff = " ".join((CLOSE_META / "review-handoff-TASK-6749.md").read_text().split())
    receipt = json.loads((CLOSE_META / "validation-receipt-goal-TASK-6749.json").read_text())
    assert cases["task_id"] == meta["task_id"] == "TASK-6749"
    assert cases["candidate_hash"] == meta["candidate_hash"] == receipt["candidate_hash"]
    assert cases["publication_state"] == meta["publication_state"] == "published"
    assert cases["independent_review"] == meta["independent_review"] == "completed_main_reviewer"
    publication = json.loads((CLOSE_META / cases["publication"]["receipt"]).read_text())
    review = (CLOSE_META / cases["publication"]["review"]).read_text()
    assert publication["candidate_hash"] == receipt["candidate_hash"]
    assert publication["files"] == receipt["files"]
    assert receipt["candidate_hash"] in review
    must = {ac["id"] for ac in meta["acceptance_criteria"]["must"]}
    covered = {ac for case in cases["cases"] for ac in case["covers"]}
    assert must <= covered
    assert receipt["candidate_hash"] in handoff
    for limit in ("not autonomous feature closing", "not stakeholder observation",
                  "No promotion", "pending independent review", "mandatory code_refactor"):
        assert limit in handoff