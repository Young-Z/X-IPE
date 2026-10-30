"""CR authored-contract coverage and installed helpers in disposable projects.

Not an autonomous CR classifier, human approval, stakeholder observation or
production mutation. Negative authored fixtures reject unsupported claims.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml

from tests.publication_recovery_6749 import current_publication, recovered_publication

from tests.test_goal_oriented_skills import rows, render_table_from_scaffold, validator
from tests.test_skill_pipeline_refactor import helper_project, output_contract, run_helper


ROOT = Path(__file__).resolve().parents[1]
NAME = "x-ipe-task-based-change-request"
META = ROOT / "x-ipe-docs/skill-meta" / NAME
CANDIDATE = META / "candidate"
LIVE = ROOT / ".github/skills" / NAME
DELTA = ("Goal / Subgoal", "Parent / Source", "Stakeholder", "Before Outcome",
         "Proposed Outcome", "Contribution / Selection", "Success Evidence",
         "Constraints / Non-goals", "Story / AC Links", "Delta Kind", "Authority",
         "Affected Evidence", "Outcome State")
MATRIX = ("Aspect", "CR Requirement", "Existing Feature(s)", "Evidence / Boundary Decision")
CONFLICT = ("#", "Type", "Affected Feature", "Severity", "Classification",
            "Description", "Source / Revision", "Resolution / Authority")
# Frozen declaration verified against original production before promotion.
# Keep post-publication live/candidate schema checks non-tautological.
ORIGINAL_CR_OUTPUT = {
    "category": "standalone", "status": "completed | blocked",
    "next_task_based_skill": [
        {"skill": "x-ipe-task-based-feature-refinement", "condition": "When CR modifies an existing feature"},
        {"skill": "x-ipe-task-based-feature-breakdown", "condition": "When CR requires a new feature"}],
    "process_preference": {"interaction_mode": "{from input process_preference.interaction_mode}"},
    "execution_mode": "{from input}", "workflow": {"name": "{from input}"},
    "task_output_links": ["x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md"],
    "feature_id": "{FEATURE-XXX}", "cr_id": "CR-XXX",
    "cr_classification": "modification | new_feature", "affected_features": ["FEATURE-XXX"],
    "new_feature_ids": ["FEATURE-XXX"], "requirement_updated": "true | false",
    "mockup_updated": "true | false", "updated_mockup_paths": [], "conflicts_found": [],
    "conflicts_resolution": "none | all_expected | mitigated",
    "conflicting_docs_updated": [], "conflicting_docs_retired": [],
}


def section(number):
    text = (CANDIDATE / "references/examples.md").read_text()
    return text.split(f"## {number}.", 1)[1].split("\n## ", 1)[0]


def check_means_example(text):
    """Check authored consistency; the agent's decision is not executed here."""
    delta = rows(text, DELTA)
    assert len(delta) == 2
    primary, unchanged = delta
    assert primary["Goal / Subgoal"] == "US-005-01"
    assert primary["Parent / Source"] == "FR-005-01; approved preferences scope"
    assert primary["Stakeholder"] == "account owner"
    assert primary["Before Outcome"] == primary["Proposed Outcome"] == "preferences persist across reload"
    assert primary["Delta Kind"] == "selected means only"
    assert primary["Authority"] == "human-approved CR-002 scope; fixture only"
    assert primary["Story / AC Links"] == "US-005-01; AC-005-01"
    assert "all-required" in primary["Contribution / Selection"]
    assert "reload" in primary["Success Evidence"]
    assert "no sharing" in primary["Constraints / Non-goals"]
    assert primary["Affected Evidence"] == "AC-005-01 design/test/outcome evidence invalidated; rerun planned UI reload check"
    assert primary["Outcome State"] == "not measured"
    assert unchanged["Delta Kind"] == "unchanged"
    assert unchanged["Affected Evidence"] == "retain original AC-005-02 source and evidence bytes"
    assert unchanged["Outcome State"] == "not measured"
    matrix = rows(text, MATRIX)
    assert [r["Aspect"] for r in matrix] == ["Users", "Workflow", "Data Model", "UI Elements", "API Endpoints"]
    assert all(all(r.values()) for r in matrix)
    conflicts = rows(text, CONFLICT)
    assert len(conflicts) == 1
    assert conflicts[0]["Type"] == "specification"
    assert conflicts[0]["Classification"] == "expected"
    assert "specification.md#AC-005-01" in conflicts[0]["Source / Revision"]
    acs = rows(text, ("AC ID", "Criterion (Given/When/Then)", "Test Type"))
    assert [r["AC ID"] for r in acs] == ["AC-005-01", "AC-005-02"]
    assert all(all(word in r["Criterion (Given/When/Then)"] for word in ("GIVEN", "WHEN", "THEN")) for r in acs)
    assert all(r["Test Type"] == "UI" for r in acs)
    assert "cr_classification: modification" in text
    assert "verified engineering delivery" not in text
    return delta


def test_complete_candidate_exact_original_output_and_baselines():
    v = validator()
    baseline = json.loads((META / "baseline-goal-TASK-6749.json").read_text())
    publication = json.loads((META / "publication-receipt-goal-TASK-6749.json").read_text())
    assert publication["baseline_hash"] == v.fingerprint(baseline)
    current = current_publication(NAME, v.manifest(v.tree_bytes(LIVE, ROOT)))
    assert recovered_publication(NAME)["baseline_hash"] == publication["candidate_hash"]
    receipt = v.validate(ROOT, CANDIDATE, NAME, "x-ipe-task-based")
    assert receipt["ok"] and not receipt["warnings"], receipt
    assert receipt["files"] == current["files"] and publication["byte_parity"]
    assert set(receipt["files"]) == set(baseline) | {"references/integration.md"}
    original, proposed = output_contract(LIVE / "SKILL.md"), output_contract(CANDIDATE / "SKILL.md")
    assert original == proposed == ORIGINAL_CR_OUTPUT
    assert list(original) == list(proposed) == list(ORIGINAL_CR_OUTPUT)
    text = (CANDIDATE / "SKILL.md").read_text()
    procedure = ET.fromstring(re.search(r"<procedure.*?</procedure>", text, re.S)[0])
    assert len(procedure.findall(".//action")) == 5
    package = "\n".join(p.read_text() for p in CANDIDATE.rglob("*.md"))
    for forbidden in ("task_create.py", "task_update.py", "phase_0", "phase_6", 'type: "routing"',
                      "Execute Next Action", "git add", "features.md", "ENHANCEMENT", "NOT_A_CR"):
        assert forbidden not in package


@pytest.mark.parametrize("mode", ["interact-with-human", "dao-represent-human-to-interact",
                                 "dao-represent-human-to-interact-for-questions-in-skill"])
def test_modes_actual_human_gate_and_no_repeated_confirmation(mode):
    text = (CANDIDATE / "SKILL.md").read_text()
    assert mode in text
    for clause in ("Human asks the human within skill and waits", "full DAO and hybrid answer actual bounded questions", "one consolidated decision",
                   "large-scope changes require actual human approval", "before any target document mutation",
                   "Reuse exact-revision approval", "DAO guidance is not human permission",
                   "No board, Git, successor execution or recursive lifecycle"):
        assert clause in text


def test_source_init_and_current_workflow_tags_config():
    text = (CANDIDATE / "SKILL.md").read_text()
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", text, re.S)[0])
    assert {f.attrib["name"] for f in init.findall("field")} >= {
        "task_id", "task_based_skill", "workflow.action", "workflow.extra_context_reference",
        "features_path", "requirement_details_path", "change_request_description", "business_justification",
        "requestor", "priority", "category", "next_task_based_skill"}
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["feedback"]["actions"]["change_request"]
    assert template["stages"]["feedback"]["type"] == "per_feature"
    assert action["action_context"]["specification"]["required"] is True
    assert action["action_context"]["closing-report"]["required"] is False
    assert action["deliverables"] == ["$output:cr-doc", "$output-folder:cr-folder"]
    config = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())
    assert config["stages"]["feedback"]["change_request"] == {}
    js = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"change_request:.*skill: '" + NAME + "'", js)
    integration = " ".join((CANDIDATE / "references/integration.md").read_text().split()).lower()
    for clause in ("closing-report is optional", "writer success alone is insufficient",
                   "explicit broken link blocks", "epic", "symlink", "empty routing configuration",
                   "all mandatory predecessor actions", "no related feature", "blocked"):
        assert clause in integration


def test_authored_means_delta_and_template_expressiveness(tmp_path):
    text = section(1)
    check_means_example(text)
    scaffold = (CANDIDATE / "templates/change-request.md").read_text()
    rendered = scaffold
    for columns in (DELTA, MATRIX, CONFLICT, ("AC ID", "Criterion (Given/When/Then)", "Test Type")):
        rendered = render_table_from_scaffold(rendered, columns, rows(text, columns))
    target = tmp_path / "CR-002.md"
    target.write_text(rendered + "\ncr_classification: modification\n")
    check_means_example(target.read_text())
    assert list(tmp_path.iterdir()) == [target]
    for heading in ("Request Details", "Description", "Business Justification", "Impact Analysis",
                    "Comparison Matrix", "Conflict Analysis", "Affected Components", "Dependencies",
                    "Proposed Approach", "Mockup Impact", "Approval", "Execution", "Links", "Change History"):
        assert heading in scaffold


@pytest.mark.parametrize("old,new", [
    ("preferences persist across reload | preferences persist across reload", "preferences persist across reload | share preferences with coworkers"),
    ("FR-005-01; approved preferences scope", "invented authority"),
    ("US-005-01; AC-005-01", "US-005-01; AC-UNKNOWN"),
    ("selected means only", "new goal automatically means new feature"),
    ("human-approved CR-002 scope; fixture only", "DAO approval replaces human"),
    ("not measured", "observed stakeholder outcome"),
    ("AC-005-01 design/test/outcome evidence invalidated; rerun planned UI reload check", "retain obsolete passing result"),
    ("retain original AC-005-02 source and evidence bytes", "invalidate all unrelated evidence"),
    ("| UI |", "| Manual |"),
    ("GIVEN saved preferences", "saved preferences"),
    ("| API Endpoints |", "| Integration |"),
    ("specification.md#AC-005-01", "description-only guess"),
    ("cr_classification: modification", "cr_classification: new_feature"),
])
def test_negative_authored_goal_scope_approval_evidence_contracts(old, new):
    text = section(1)
    assert old in text
    with pytest.raises((AssertionError, ValueError)):
        check_means_example(text.replace(old, new, 1))


@pytest.mark.parametrize("number,clauses", [
    (2, ("Bulk import", "new_feature", "new stakeholder outcome", "not automatically", "new_feature_ids: []")),
    (3, ("profile.permissions.roles[]", "unexpected", "source", "mitigated", "[RETIRED by CR-003]", "reason, date")),
    (4, ("better error handling", "inferred", "so-that", "pertinent", "blocked")),
    (5, ("Safari", "bug-fix", "blocked", "not fabricate")),
    (6, ("all-required", "alternatives", "AC-005-03", "not automatically", "modification")),
])
def test_original_use_cases_and_new_subgoal_boundary(number, clauses):
    text = " ".join(section(number).split())
    assert all(c in text for c in clauses)


@pytest.fixture(params=["epic", "legacy"])
def cr_project(helper_project, request):
    project, state_path = helper_project
    feature = "FEATURE-005-A" if request.param == "epic" else "FEATURE-005"
    folder = ("x-ipe-docs/requirements/EPIC-005/" + feature if request.param == "epic"
              else "x-ipe-docs/requirements/" + feature)
    target = project / folder
    target.mkdir(parents=True)
    (target / "specification.md").write_text(f"# Preferences\nFeature ID: {feature}\n" + section(1))
    (target / "CR-002.md").write_text(section(1))
    state = json.loads(state_path.read_text())
    template = json.loads((project / "x-ipe-docs/config/workflow-template.json").read_text())
    state["shared"]["requirement"]["status"] = "completed"
    for data in state["shared"]["requirement"]["actions"].values():
        data["status"] = "done"
    record = {"feature_id": feature, "name": "Preferences"}
    for stage in ("implement", "validation", "feedback"):
        record[stage] = {"status": "in_progress", "actions": {
            name: {"status": "done" if stage != "feedback" else "pending", "deliverables": {}}
            for name in template["stages"][stage]["actions"]}}
    record["feedback"]["actions"]["change_request"]["context"] = {"specification": folder + "/specification.md"}
    state["features"] = [record]
    state["current_stage"] = "feedback"
    state_path.write_text(json.dumps(state))
    return project, state_path, feature, {"cr-doc": folder + "/CR-002.md", "cr-folder": folder}


def write_cr(project, feature, links):
    return run_helper(project, "workflow_update_action.py", "--workflow", "pilot", "--action",
                      "change_request", "--status", "done", "--feature-id", feature,
                      "--deliverables", json.dumps(links))


def test_real_helper_exact_tags_readback_optional_report_no_tasks(cr_project):
    project, state_path, feature, links = cr_project
    result, payload = write_cr(project, feature, links)
    assert result.returncode == 0 and payload["success"]
    _, state = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    action = state["features"][0]["feedback"]["actions"]["change_request"]
    assert action["status"] == "done" and action["deliverables"] == links
    assert action["context"] == {"specification": links["cr-folder"] + "/specification.md"}
    assert (project / links["cr-doc"]).is_file() and (project / links["cr-folder"]).is_dir()
    before = state_path.read_bytes()
    run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    assert state_path.read_bytes() == before
    assert not (project / "x-ipe-docs/planning/tasks").exists()


@pytest.mark.parametrize("defect", ["folder-array", "invented-tag", "wrong-feature", "locked"])
def test_real_helper_failure_without_state_mutation(cr_project, defect):
    project, state_path, feature, links = cr_project
    if defect == "folder-array":
        links["cr-folder"] = [links["cr-folder"]]
    elif defect == "invented-tag":
        links["goal-delta"] = links["cr-doc"]
    elif defect == "wrong-feature":
        feature = "FEATURE-999"
    else:
        state = json.loads(state_path.read_text())
        state["features"][0]["feedback"]["status"] = "locked"
        state["features"][0]["validation"]["actions"]["feature_closing"]["status"] = "pending"
        state_path.write_text(json.dumps(state))
    before = state_path.read_bytes()
    result, payload = write_cr(project, feature, links)
    assert result.returncode != 0 and not payload["success"]
    assert state_path.read_bytes() == before


def test_permissive_writer_is_not_cr_semantic_readiness(cr_project):
    project, state_path, feature, _ = cr_project
    state = json.loads(state_path.read_text())
    state["features"][0]["feedback"]["actions"]["change_request"]["context"] = {}
    state_path.write_text(json.dumps(state))
    result, payload = write_cr(project, feature, {"cr-doc": "missing.md"})
    assert result.returncode == 0 and payload["success"]
    assert not (project / "missing.md").exists()
    assert "writer success alone is insufficient" in " ".join(
        (CANDIDATE / "references/integration.md").read_text().split()).lower()


def test_readiness_metadata_receipt_exact_promotion_and_must_coverage():
    meta = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", (META / "skill-meta.md").read_text(), re.S)[1])
    cases = yaml.safe_load((META / "test-cases.yaml").read_text())
    receipt = json.loads((META / "validation-receipt-goal-TASK-6749.json").read_text())
    current = validator().validate(ROOT, CANDIDATE, NAME, "x-ipe-task-based")
    assert current_publication(NAME)["files"] == current["files"]
    assert validator().fingerprint(receipt["files"]) == receipt["candidate_hash"]
    assert meta["task_id"] == cases["task_id"] == "TASK-6749"
    assert meta["publication_state"] == cases["publication_state"] == "published"
    assert meta["independent_review"] == cases["independent_review"] == "passed_inherited_candidate_review"
    assert meta["candidate_hash"] == cases["candidate_hash"] == receipt["candidate_hash"]
    assert meta["version"] == "2.0.0" and meta["planned_version"] == "2.0.0"
    publication = json.loads((META / "publication-receipt-goal-TASK-6749.json").read_text())
    assert publication["candidate_hash"] == receipt["candidate_hash"]
    assert publication["publication_state"] == "published"
    must = {c["id"] for c in meta["acceptance_criteria"]["must"]}
    assert must <= {ac for case in cases["cases"] for ac in case["covers"]}
    assert cases["preservation"]["existing_assertions_weakened"] is False
    historical = (META / "skill-meta.md").read_text().split(
        "## Historical metadata (verbatim prework snapshot; superseded fields)\n\n```text\n", 1)[1].rsplit("```", 1)[0]
    assert hashlib.sha256(historical.encode()).hexdigest() == "697a68566911ac8eaf912d5233df8e3e332eae18d5a5d00138240d549d58f0fb"


BUG_NAME = "x-ipe-task-based-bug-fix"
BUG_META = ROOT / "x-ipe-docs/skill-meta" / BUG_NAME
BUG = BUG_META / "candidate"
# Frozen original declaration: live/candidate equality alone could accept drift.
ORIGINAL_BUG_OUTPUT = {
    "category": "standalone", "status": "completed | blocked",
    "next_task_based_skill": None,
    "process_preference": {"interaction_mode": "{from input process_preference.interaction_mode}"},
    "execution_mode": "{from input}", "workflow": {"name": "{from input}"},
    "task_output_links": ["{path to fixed source file}", "{path to test file}"],
    "bug_severity": "Critical | High | Medium | Low",
    "root_cause": "{brief description of root cause}", "conflicts_found": [],
}
RESTORE = ("Goal / Subgoal", "Parent / Source", "Stakeholder", "Intended Behavior",
           "Contribution / Selection", "Constraints / Non-goals", "Story / AC / Type",
           "Failing Scenario", "Fixed / Regression Evidence", "Outcome State")


def test_bug_complete_package_original_legacy_output_and_domain_gates():
    receipt = validator().validate(ROOT, BUG, BUG_NAME, "x-ipe-task-based")
    assert receipt["ok"] and not receipt["warnings"], receipt
    assert set(receipt["files"]) == {"SKILL.md", "references/examples.md",
                                     "references/integration.md", "templates/bug-report.md"}
    live = ROOT / ".github/skills" / BUG_NAME
    original = output_contract(live / "SKILL.md")
    proposed = output_contract(BUG / "SKILL.md")
    assert original == proposed == ORIGINAL_BUG_OUTPUT
    assert list(original) == list(proposed) == list(ORIGINAL_BUG_OUTPUT)
    text = (BUG / "SKILL.md").read_text()
    procedure = ET.fromstring(re.search(r"<procedure.*?</procedure>", text, re.S)[0])
    assert [node.tag for node in procedure if node.tag.startswith("step_")] == [f"step_{i}" for i in range(1, 9)]
    package = " ".join("\n".join(p.read_text() for p in BUG.rglob("*.md")).split())
    for forbidden in ("task_create.py", "task_update.py", "phase_9", 'type: "routing"',
                      "Execute Next Action", "test was committed before", "git bisect"):
        assert forbidden not in package
    for clause in ("restore documented intended behavior", "all-required", "alternatives",
                   "no arbitrary success metrics", "inferred", "pertinent", "not measured",
                   "original reproduction", "root cause", "callers/dependents", "side effects",
                   "before implementation", "new regressions block", "independent review",
                   "operation: fix", "mini AAA", "tracing_enabled", "no forced tracing"):
        assert clause in package


@pytest.mark.parametrize("mode", ["interact-with-human", "dao-represent-human-to-interact",
                                 "dao-represent-human-to-interact-for-questions-in-skill"])
def test_bug_authority_and_owner_contract_separate_from_execution(mode):
    text = " ".join((BUG / "SKILL.md").read_text().split())
    assert mode in text
    for clause in ("human asks the human within skill and waits", "full DAO and hybrid use common", "DAO guidance is not human permission",
                   "scope/goal/acceptance/constraint changes require actual human authority",
                   "No board, Git, app writes or successor execution", "same task/readiness",
                   "test MUST fail for the reported behavior", "unchanged test MUST pass"):
        assert clause in text


def check_restore_example(text):
    record, = rows(text, RESTORE)
    assert record["Goal / Subgoal"] == "US-AUTH-01"
    assert record["Parent / Source"] == "FR-AUTH-01; specification#AC-AUTH-01"
    assert record["Stakeholder"] == "account owner"
    assert record["Intended Behavior"] == "only unexpired tokens authorize access; equality is expired"
    assert "all-required" in record["Contribution / Selection"]
    assert "no grace period" in record["Constraints / Non-goals"]
    assert record["Story / AC / Type"] == "US-AUTH-01; AC-AUTH-01; Unit"
    assert record["Failing Scenario"] == "expiry == now incorrectly accepted; expected rejected"
    assert "fixture only" in record["Fixed / Regression Evidence"]
    assert record["Outcome State"] == "not measured"
    return record


def test_bug_template_rendering_is_authored_contract_not_actual_fix(tmp_path):
    text = (BUG / "references/examples.md").read_text()
    check_restore_example(text)
    scaffold = (BUG / "templates/bug-report.md").read_text()
    rendered = render_table_from_scaffold(scaffold, RESTORE, rows(text, RESTORE))
    target = tmp_path / "bug-report.md"
    target.write_text(rendered)
    check_restore_example(target.read_text())
    for heading in ("Reported Behavior", "Reproduction", "Root Cause", "Scope and Conflicts",
                    "Fix and Design Impact", "Mini AAA", "Verification", "Original Output"):
        assert heading in scaffold


@pytest.mark.parametrize("old,new", [
    ("equality is expired", "equality is valid"),
    ("specification#AC-AUTH-01", "invented acceptance"),
    ("no grace period", "add grace period without approval"),
    ("AC-AUTH-01; Unit", "AC-AUTH-01; Manual"),
    ("not measured", "observed stakeholder outcome"),
])
def test_bug_negative_authored_goal_constraints_not_behavior_claim(old, new):
    text = (BUG / "references/examples.md").read_text()
    assert old in text
    with pytest.raises(AssertionError):
        check_restore_example(text.replace(old, new))


def test_actual_disposable_reproduction_red_green_and_regression_not_app_fix(tmp_path):
    """Execute a real miniature fixture, not this repo's token/auth implementation."""
    source = tmp_path / "token_fixture.py"
    test = tmp_path / "test_token_fixture.py"
    broken = "def valid(expiry, now):\n    return expiry >= now\n"
    fixed = "def valid(expiry, now):\n    return expiry > now\n"
    source.write_text(broken)
    test.write_text(
        "from token_fixture import valid\n\n"
        "def test_expiry_boundary():\n"
        "    # Arrange: contract says equality is expired.\n"
        "    expiry = now = 10\n"
        "    # Act\n"
        "    result = valid(expiry, now)\n"
        "    # Assert\n"
        "    assert result is False\n\n"
        "def test_unexpired_preserved():\n    assert valid(11, 10) is True\n\n"
        "def test_expired_preserved():\n    assert valid(9, 10) is False\n"
    )
    test_hash = hashlib.sha256(test.read_bytes()).hexdigest()
    broken_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

    def original_action():
        return subprocess.run(
            [sys.executable, "-B", "-c", "from token_fixture import valid; print(valid(10, 10))"],
            cwd=tmp_path, env=environment, capture_output=True, text=True, check=False,
        )

    def execute():
        return subprocess.run([sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider",
                               str(test), "-q", "--tb=short"], cwd=tmp_path,
                              env=environment,
                              capture_output=True, text=True, check=False)
    reproduced = original_action()
    assert reproduced.returncode == 0 and reproduced.stdout.strip() == "True", reproduced.stderr
    red = execute()
    assert red.returncode == 1, red.stdout + red.stderr
    assert "test_expiry_boundary" in red.stdout and "1 failed, 2 passed" in red.stdout
    assert "assert True is False" in red.stdout  # behavioral failure, not setup/import failure
    assert source.read_text() == broken
    assert hashlib.sha256(source.read_bytes()).hexdigest() == broken_hash
    assert hashlib.sha256(test.read_bytes()).hexdigest() == test_hash
    source.write_text(fixed)  # Only this disposable fixture; never application source.
    fixed_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    assert fixed_hash != broken_hash
    green = execute()
    assert green.returncode == 0 and "3 passed" in green.stdout, green.stdout + green.stderr
    restored = original_action()
    assert restored.returncode == 0 and restored.stdout.strip() == "False", restored.stderr
    assert hashlib.sha256(source.read_bytes()).hexdigest() == fixed_hash
    assert hashlib.sha256(test.read_bytes()).hexdigest() == test_hash
    assert sorted(p.name for p in tmp_path.iterdir()) == ["test_token_fixture.py", "token_fixture.py"]


def test_real_helper_rejects_invented_bug_fix_action_without_mutation(helper_project):
    project, state_path = helper_project
    before = state_path.read_bytes()
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                                 "--action", "bug_fix", "--status", "done")
    assert result.returncode != 0 and not payload["success"]
    assert state_path.read_bytes() == before
    assert not (project / "x-ipe-docs/planning/tasks").exists()


def test_bug_real_mapping_tool_route_and_no_fabricated_state():
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    assert all("bug_fix" not in stage["actions"] for stage in template["stages"].values())
    js = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert BUG_NAME not in js
    tools = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())
    route = tools["stages"]["feedback"]["bug_fix"]
    assert route["x-ipe-tool-ui-testing-via-chrome-mcp"] is True
    assert route["x-ipe-tool-implementation-python"] is True
    assert "mini AAA" in route["_extra_instruction"] and tools["tracing_enabled"] is False
    reference = " ".join((BUG / "references/integration.md").read_text().split())
    for clause in ("not an app action", "workflow-mode returns blocked", "authorized free-mode",
                   "operation_output", "one assertion per Assert clause", "not browser evidence",
                   "synthetic", "no feature allocation", "disabled", "unavailable"):
        assert clause in reference


def test_bug_reviewed_metadata_receipt_exact_promotion():
    meta_text = (BUG_META / "skill-meta.md").read_text()
    meta = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", meta_text, re.S)[1])
    cases = yaml.safe_load((BUG_META / "test-cases.yaml").read_text())
    current = validator().validate(ROOT, BUG, BUG_NAME, "x-ipe-task-based")
    recovered = current_publication(BUG_NAME)
    historical = json.loads((BUG_META / "validation-receipt-goal-TASK-6749.json").read_text())
    assert meta["candidate_hash"] == cases["candidate_hash"] == historical["candidate_hash"]
    assert meta["task_id"] == cases["task_id"] == "TASK-6749"
    assert meta["publication_state"] == cases["publication_state"] == "published"
    assert meta["independent_review"] == cases["independent_review"] == "passed_inherited_candidate_review"
    assert meta["inputs"]["optional"][-1]["type"] == "null"
    assert meta["version"] == meta["planned_version"] == "2.0.0"
    baseline = json.loads((BUG_META / "baseline-goal-TASK-6749.json").read_text())
    publication = json.loads((BUG_META / "publication-receipt-goal-TASK-6749.json").read_text())
    assert publication["baseline_hash"] == validator().fingerprint(baseline)
    assert publication["publication_state"] == "published" and publication["byte_parity"]
    assert publication["method"] == "authorized_edit_tools"
    assert historical["files"] == publication["files"]
    assert recovered_publication(BUG_NAME)["baseline_hash"] == publication["candidate_hash"]
    assert validator().manifest(validator().tree_bytes(ROOT / ".github/skills" / BUG_NAME, ROOT)) == current["files"] == recovered["files"]
    historical = meta_text.split("## Historical metadata (verbatim prework snapshot)\n\n```text\n", 1)[1].rsplit("```", 1)[0]
    assert hashlib.sha256(historical.encode()).hexdigest() == "9cd7d3037abbd1bb44a8654b2ebd0ea4a7acaf7b3fe31f53e9a07227862c7611"
    assert {c["id"] for c in meta["acceptance_criteria"]["must"]} <= {ac for c in cases["cases"] for ac in c["covers"]}


REFACTOR_NAME = "x-ipe-task-based-code-refactor"
REFACTOR_META = ROOT / "x-ipe-docs/skill-meta" / REFACTOR_NAME
REFACTOR = REFACTOR_META / "candidate"
QUALITY = ("Goal / Subgoal", "Parent / Source", "Stakeholder", "Contribution / Selection",
           "Baseline", "Success Evidence", "Preservation / AC / Type", "Trade-off", "Outcome State")

ORIGINAL_REFACTOR_OUTPUT = {
    "category": "feature-stage | standalone", "status": "completed | blocked",
    "next_task_based_skill": [
        {"skill": "x-ipe-task-based-feature-acceptance-test", "condition": "Re-verify after refactoring"},
        {"skill": "x-ipe-task-based-feature-closing", "condition": "Close feature if refactoring is the final step"}],
    "process_preference": {"interaction_mode": "{from input process_preference.interaction_mode}"},
    "execution_mode": "{from input}", "workflow": {"name": "{from input}"},
    "task_output_links": ["x-ipe-docs/refactoring/analysis-{context}.md",
                          "x-ipe-docs/refactoring/validation-{context}.md", "{paths to refactored files}"],
    "feature_id": "{from input refactoring_scope.feature_id or N/A}",
    "refactoring_summary": {
        "files_modified": "<count>", "files_created": "<count>", "files_deleted": "<count>",
        "principles_applied": [{"principle": "<name>", "application_count": "<count>", "areas": "<list>"}],
        "goals_achieved": [{"goal": "<name>", "status": "achieved | partial | skipped", "notes": "<details>"}]},
    "code_quality_evaluated": {
        "quality_score_before": "<1-10>", "quality_score_after": "<1-10>",
        "test_coverage": {"before": "<percentage>", "after": "<percentage>",
                          "status": "maintained | improved | degraded"},
        "references_updated": {"requirements": "<count>", "specifications": "<count>", "technical_designs": "<count>"}},
}


def test_refactor_complete_resources_frozen_original_output_and_publication_state():
    receipt = validator().validate(ROOT, REFACTOR, REFACTOR_NAME, "x-ipe-task-based")
    assert receipt["ok"] and not receipt["warnings"], receipt
    assert set(receipt["files"]) == {"SKILL.md", "references/examples.md",
        "references/refactoring-techniques.md", "references/integration.md", "templates/refactor-report.md"}
    old = ORIGINAL_REFACTOR_OUTPUT
    new = output_contract(REFACTOR / "SKILL.md")
    expected = json.loads(json.dumps(old))
    expected["code_quality_evaluated"]["quality_score_before"] = "<1-10 | not measured>"
    expected["code_quality_evaluated"]["quality_score_after"] = "<1-10 | not measured>"
    expected["code_quality_evaluated"]["test_coverage"] = {
        "before": "<percentage string | null>", "after": "<percentage string | null>",
        "status": "maintained | improved | degraded | null"}
    assert new == expected and list(new) == list(old)
    assert list(new["code_quality_evaluated"]) == list(old["code_quality_evaluated"])
    baseline = json.loads((REFACTOR_META / "baseline-goal-TASK-6749.json").read_text())
    live = validator().manifest(validator().tree_bytes(ROOT / ".github/skills" / REFACTOR_NAME, ROOT))
    publication_path = REFACTOR_META / "publication-receipt-goal-TASK-6749.json"
    if publication_path.exists():
        publication = json.loads(publication_path.read_text())
        assert publication["publication_state"] == "published" and publication["byte_parity"]
        assert publication["baseline_hash"] == validator().fingerprint(baseline)
        current = current_publication(REFACTOR_NAME, live)
        assert recovered_publication(REFACTOR_NAME)["baseline_hash"] == publication["candidate_hash"]
        assert current["candidate_hash"] == receipt["candidate_hash"]
        assert live == receipt["files"] == current["files"]
        assert publication["added"] == ["references/integration.md", "templates/refactor-report.md"]
        assert publication["changed"] == sorted(baseline) and publication["removed"] == []
        assert output_contract(ROOT / ".github/skills" / REFACTOR_NAME / "SKILL.md") == expected
    else:
        assert live == baseline
        assert output_contract(ROOT / ".github/skills" / REFACTOR_NAME / "SKILL.md") == old
    text = (REFACTOR / "SKILL.md").read_text()
    procedure = ET.fromstring(re.search(r"<procedure.*?</procedure>", text, re.S)[0])
    assert len(procedure.findall(".//action")) == 5
    package = "\n".join(p.read_text() for p in REFACTOR.rglob("*.md"))
    for forbidden in ("task_create.py", "task_update.py", 'type: "routing"', "phase_6",
                      "git commit -m", "git checkout HEAD", "force-enable general", "Output:\n"):
        assert forbidden not in package


@pytest.mark.parametrize("mode", ["interact-with-human", "dao-represent-human-to-interact",
                                 "dao-represent-human-to-interact-for-questions-in-skill"])
def test_refactor_goal_preservation_modes_and_single_lifecycle(mode):
    text = " ".join((REFACTOR / "SKILL.md").read_text().split())
    assert mode in text
    for clause in ("same task/readiness", "No board, Git, app writes or successor execution",
                   "human asks the human within skill and waits", "full DAO and hybrid use common", "actual human CR authority",
                   "externally-visible behavior", "named measurable or qualitative quality improvement",
                   "all-required", "alternatives", "inferred", "pertinent", "no arbitrary scores",
                   "baseline", "trade-off", "not measured", "dirty", "default no commit"):
        assert clause in text


@pytest.mark.parametrize("mode,clauses", [
    ("study-only", ("no source/test/doc mutation", "analysis report", "not implementation")),
    ("local", ("targeted risk-based tests", "affected documentation", "no blanket 80%")),
    ("broad", ("integration/full suite", "measured coverage", "authorized scope")),
])
def test_refactor_scope_modes_and_legacy_tool_adapter_honesty(mode, clauses):
    text = " ".join((REFACTOR / "references/integration.md").read_text().split()).lower()
    assert mode in text
    assert all(c in text for c in clauses)
    for clause in ("full_analysis", "full_sync", "operation_output", "not a successful tool invocation",
                   "numeric", "schema", "no synthetic metric", "no whole-project retrofit",
                   "not_found", "do not skip failing tests", "before behavior change"):
        assert clause in text


def check_quality_example(text):
    record, = rows(text, QUALITY)
    assert record["Goal / Subgoal"] == "Q-DUP-01"
    assert record["Parent / Source"] == "US-PRICE-01; fixture contract"
    assert record["Stakeholder"] == "maintainer; indirect contribution to price consistency"
    assert "all-required" in record["Contribution / Selection"]
    assert record["Baseline"] == "two identical price decisions in inspected disposable source"
    assert "one shared decision" in record["Success Evidence"]
    assert record["Preservation / AC / Type"] == "unchanged public functions/results/errors; AC-PRICE-01; Unit"
    assert "extra internal call" in record["Trade-off"]
    assert record["Outcome State"] == "not measured"


def test_refactor_authored_quality_baseline_scaffold_and_plain_output_reference(tmp_path):
    text = (REFACTOR / "references/examples.md").read_text()
    check_quality_example(text)
    scaffold = (REFACTOR / "templates/refactor-report.md").read_text()
    target = tmp_path / "refactor-report.md"
    target.write_text(render_table_from_scaffold(scaffold, QUALITY, rows(text, QUALITY)))
    check_quality_example(target.read_text())
    reference = (REFACTOR / "references/refactoring-techniques.md").read_text()
    assert "## Output guidance" in reference
    assert "not measured" in reference
    assert "task_completion_output:" not in reference  # no contradictory executable schema
    for heading in ("Scope and Authority", "Analysis and Sync", "Preservation Baseline",
                    "Plan and Trade-offs", "Execution", "Before / After Evidence", "Original Output"):
        assert heading in scaffold


@pytest.mark.parametrize("old,new", [
    ("two identical price decisions in inspected disposable source", "uninspected invented baseline"),
    ("one shared decision", "score automatically increased"),
    ("unchanged public functions/results/errors; AC-PRICE-01; Unit", "new API; AC-PRICE-01; Manual"),
    ("extra internal call", "no trade-off measured or inspected"),
    ("not measured", "observed stakeholder outcome"),
])
def test_refactor_negative_authored_quality_claims(old, new):
    text = (REFACTOR / "references/examples.md").read_text()
    assert old in text
    with pytest.raises(AssertionError):
        check_quality_example(text.replace(old, new))


def test_refactor_real_config_optional_app_action_and_conditional_report():
    template = json.loads((ROOT / "x-ipe-docs/config/workflow-template.json").read_text())
    action = template["stages"]["validation"]["actions"]["code_refactor"]
    assert action["optional"] is True
    assert action["deliverables"] == ["$output:refactor-report"]
    assert action["action_context"]["tech-design"]["required"] is True
    assert action["action_context"]["specification"]["required"] is True
    assert action["action_context"]["test-report"]["required"] is False
    js = (ROOT / "src/x_ipe/static/js/features/workflow-stage.js").read_text()
    assert re.search(r"code_refactor:.*skill: '" + REFACTOR_NAME + "'", js)
    config = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())
    route = config["stages"]["validation"]["code_refactor"]
    assert route["x-ipe-tool-implementation-python"] is True
    assert "checkpoints" in route["_extra_instruction"]
    text = " ".join((REFACTOR / "references/integration.md").read_text().split()).lower()
    for clause in ("stages.validation.code_refactor", "explicit false", "no inline production fallback",
                   "x-ipe-meta-skill-creator", "candidate", "not arbitrary production edits",
                   "refactor-report", "explicit customized mandatory action", "writer success alone is insufficient",
                   "no fake done", "enabled", "operation: refactor", "synthetic", "tracing_enabled"):
        assert clause in text


def test_actual_disposable_refactor_baseline_after_same_behavior_named_improvement(tmp_path):
    """Real structural fixture refactor; no application modification or skill execution."""
    source = tmp_path / "price_fixture.py"
    test = tmp_path / "test_price_fixture.py"
    source.write_text("def retail(x):\n    return max(0, x) * 2\n\ndef wholesale(x):\n    return max(0, x) * 2\n")
    test.write_text("import pytest\nfrom price_fixture import retail, wholesale\n\n"
                    "@pytest.mark.parametrize('x', [-3, 0, 2, 2.5])\n"
                    "def test_public_results(x):\n    assert retail(x) == wholesale(x) == max(0, x) * 2\n\n"
                    "@pytest.mark.parametrize('fn', [retail, wholesale])\n"
                    "def test_error_contract(fn):\n    with pytest.raises(TypeError):\n        fn(None)\n")
    assertion_hash = hashlib.sha256(test.read_bytes()).hexdigest()
    before = hashlib.sha256(source.read_bytes()).hexdigest()

    def execute():
        return subprocess.run([sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider",
                               str(test), "-q", "--tb=short"], cwd=tmp_path,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True)

    baseline = execute()
    assert baseline.returncode == 0 and "6 passed" in baseline.stdout
    assert source.read_text().count("return max(0, x) * 2") == 2
    source.write_text("def _price(x):\n    return max(0, x) * 2\n\ndef retail(x):\n    return _price(x)\n\ndef wholesale(x):\n    return _price(x)\n")
    after = execute()
    assert after.returncode == 0 and "6 passed" in after.stdout
    assert source.read_text().count("return max(0, x) * 2") == 1
    assert hashlib.sha256(source.read_bytes()).hexdigest() != before
    assert hashlib.sha256(test.read_bytes()).hexdigest() == assertion_hash
    assert sorted(p.name for p in tmp_path.iterdir()) == ["price_fixture.py", "test_price_fixture.py"]


@pytest.mark.parametrize("report_exists", [True, False])
def test_refactor_actual_helper_tag_readback_not_semantic_readiness(helper_project, report_exists):
    project, state_path = helper_project
    template = json.loads((project / "x-ipe-docs/config/workflow-template.json").read_text())
    state = json.loads(state_path.read_text())
    state["shared"]["requirement"]["status"] = "completed"
    for data in state["shared"]["requirement"]["actions"].values():
        data["status"] = "done"
    feature = "FEATURE-061-A"
    folder = project / "x-ipe-docs/requirements/EPIC-061" / feature
    folder.mkdir()
    (folder / "specification.md").write_text("# Approved fixture\n" + feature)
    (folder / "technical-design.md").write_text("# Preserved fixture structure\n" + feature)
    report = folder / "refactor-report.md"
    if report_exists:
        report.write_text("# Actual disposable report\nNo production action or study completion claim.")
    record = {"feature_id": feature, "name": "Fixture"}
    for stage in ("implement", "validation", "feedback"):
        record[stage] = {"status": "completed" if stage == "implement" else "in_progress",
                         "actions": {name: {"status": "done", "deliverables": {}}
                                     for name in template["stages"][stage]["actions"]}}
    record["validation"]["actions"]["code_refactor"] = {
        "status": "pending", "deliverables": {}, "context": {
            "tech-design": (folder / "technical-design.md").relative_to(project).as_posix(),
            "specification": (folder / "specification.md").relative_to(project).as_posix()}}
    state["features"] = [record]
    state["current_stage"] = "validation"
    state_path.write_text(json.dumps(state))
    links = {"refactor-report": report.relative_to(project).as_posix()}
    result, payload = run_helper(project, "workflow_update_action.py", "--workflow", "pilot",
                                 "--action", "code_refactor", "--status", "done",
                                 "--feature-id", feature, "--deliverables", json.dumps(links))
    assert result.returncode == 0 and payload["success"]
    _, readback = run_helper(project, "workflow_get_state.py", "--workflow", "pilot")
    action = readback["features"][0]["validation"]["actions"]["code_refactor"]
    assert action["status"] == "done" and action["deliverables"] == links
    assert report.is_file() is report_exists
    assert not (project / "x-ipe-docs/planning/tasks").exists()
    assert "writer success alone is insufficient" in (REFACTOR / "references/integration.md").read_text().lower()


def test_refactor_root_metadata_schema_receipt_and_review_gate():
    text = (REFACTOR_META / "skill-meta.md").read_text()
    meta = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", text, re.S)[1])
    cases = yaml.safe_load((REFACTOR_META / "test-cases.yaml").read_text())
    receipt = validator().validate(ROOT, REFACTOR, REFACTOR_NAME, "x-ipe-task-based")
    assert current_publication(REFACTOR_NAME)["files"] == receipt["files"]
    historical = json.loads((REFACTOR_META / "validation-receipt-goal-TASK-6749.json").read_text())
    publication = json.loads((REFACTOR_META / "publication-receipt-goal-TASK-6749.json").read_text())
    assert historical["files"] == publication["files"]
    assert meta["candidate_hash"] == cases["candidate_hash"] == historical["candidate_hash"]
    assert meta["task_id"] == cases["task_id"] == "TASK-6749"
    publication_path = REFACTOR_META / "publication-receipt-goal-TASK-6749.json"
    expected_state = "published" if publication_path.exists() else "candidate_ready"
    assert meta["publication_state"] == cases["publication_state"] == expected_state
    assert meta["independent_review"] == cases["independent_review"] == "passed_final_revision_review"
    if expected_state == "published":
        assert meta["version"] == meta["planned_version"] == "2.0.0"
        assert cases["preservation"]["production_promoted"] is True
    assert {c["id"] for c in meta["acceptance_criteria"]["must"]} <= {ac for c in cases["cases"] for ac in c["covers"]}
    for item in meta["outputs"]["data"]:
        if item["name"] in ("code_quality_evaluated.quality_score_before", "code_quality_evaluated.quality_score_after"):
            assert item["type"] == "string" and "not measured" in item["description"]
    assert cases["preservation"]["original_assertions_weakened"] is False


SYNC_NAME = "x-ipe-tool-code-quality-sync"
SYNC_META = ROOT / "x-ipe-docs/skill-meta" / SYNC_NAME
SYNC = SYNC_META / "candidate"
SYNC_TRACE = ("Goal / Parent / Source", "Baseline / Target", "Docs Considered",
              "Preservation / Type", "Evidence / Limits", "Disposition")
# Frozen original declaration; identical keys, not live/candidate tautology.
ORIGINAL_SYNC_OUTPUT = {
    "success": "true | false", "result": {
        "code_quality_evaluated": {
            "requirements_alignment": {"status": "aligned", "gaps": [], "updates_made": ["<list of doc updates>"]},
            "specification_alignment": {"status": "aligned", "gaps": [], "updates_made": ["<list of spec updates>"]},
            "test_coverage": {"status": "sufficient", "line_coverage": "<XX% — should be ≥ 80>",
                              "tests_added": "<count>", "tests_updated": "<count>"},
            "code_alignment": {"status": "{from input — not modified in this phase}"},
            "overall_quality_score": "<improved score>",
            "validation_summary": {"docs_created": "<count>", "docs_updated": "<count>",
                                   "tests_added": "<count>", "ready_for_refactoring": "true | false"}},
        "refactoring_scope": "{pass-through from input}",
        "refactoring_suggestion": "{pass-through from input}",
        "refactoring_principle": "{pass-through from input}",
        "report_path": "x-ipe-docs/refactoring/validation-{context}.md"}, "errors": [],
}


def test_sync_complete_original_fields_live_parity_and_no_lifecycle():
    current = validator().validate(ROOT, SYNC, SYNC_NAME, "x-ipe-tool")
    assert current["ok"] and not current["warnings"], current
    assert set(current["files"]) == {"SKILL.md", "references/examples.md", "references/output-schema.md",
                                     "references/detailed-procedures.md", "templates/validation-report.md"}
    baseline = json.loads((SYNC_META / "baseline-goal-TASK-6749.json").read_text())
    live_bytes = validator().tree_bytes(ROOT / ".github/skills" / SYNC_NAME, ROOT)
    live = validator().manifest(live_bytes)
    expected = json.loads(json.dumps(ORIGINAL_SYNC_OUTPUT))
    q = expected["result"]["code_quality_evaluated"]
    for key in ("requirements_alignment", "specification_alignment"):
        q[key].update(status="<evidence status>", updates_made=[])
    q["test_coverage"].update(status="<evidence status>", line_coverage="<percentage string | null>")
    q["overall_quality_score"] = "<number 1-10 | null>"
    actual = analysis_output(SYNC / "SKILL.md")
    assert actual == expected and list(actual) == list(ORIGINAL_SYNC_OUTPUT)
    assert list(actual["result"]) == list(ORIGINAL_SYNC_OUTPUT["result"])
    assert list(actual["result"]["code_quality_evaluated"]) == list(q)
    publication_path = SYNC_META / "publication-receipt-goal-TASK-6749.json"
    if publication_path.exists():
        publication = json.loads(publication_path.read_text())
        assert publication["publication_state"] == "published" and publication["byte_parity"]
        assert publication["baseline_hash"] == validator().fingerprint(baseline)
        newest = current_publication(SYNC_NAME)
        assert newest["baseline_hash"] == publication["candidate_hash"]
        assert newest["candidate_hash"] == current["candidate_hash"]
        assert live == current["files"] == newest["files"]
        assert live_bytes == validator().tree_bytes(SYNC, ROOT)
        assert publication["changed"] == sorted(baseline)
        assert publication["added"] == sorted(set(publication["files"]) - set(baseline))
        assert publication["removed"] == []
        assert analysis_output(ROOT / ".github/skills" / SYNC_NAME / "SKILL.md") == expected
    else:
        assert live == baseline
        assert analysis_output(ROOT / ".github/skills" / SYNC_NAME / "SKILL.md") == ORIGINAL_SYNC_OUTPUT
    package = "\n".join(p.read_text() for p in SYNC.rglob("*.md"))
    for forbidden in ("task_completion_output:", "task_create.py", "task_update.py", "git commit",
                      "git add", "Mark test @skip", "SET status to", "weighted_average("):
        assert forbidden not in package
    operation = ET.fromstring(re.search(r'<operation name="full_sync">.*?</operation>', package, re.S)[0])
    assert len(operation.findall("action")) == 1
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", package, re.S)[0])
    assert {f.attrib["name"] for f in init} == {
        "operation", "refactoring_scope", "code_quality_evaluated", "refactoring_suggestion",
        "refactoring_principle", "refactoring_mode", "program_type", "sync_context"}


@pytest.mark.parametrize("mode,clauses", [
    ("study-only", ("read-only", "assessment", "readiness=false")),
    ("local", ("targeted", "no blanket coverage/full-suite gate", "critical")),
    ("broad", ("integration/full suite", "80%", "guideline", "authoritative")),
])
def test_sync_mode_risk_domain_goal_authority_and_threshold_contract(mode, clauses):
    text = " ".join("\n".join(p.read_text() for p in SYNC.rglob("*.md")).split())
    assert mode in text and all(c in text for c in clauses)
    for clause in ("all-required", "selected alternatives", "source/parent", "so-that", "inferred",
                   "story/GWT AC", "not measured", "trade-off", "base-to-target", "unchanged",
                   "undocumented/unimplemented/deviated", "missing/extra/deviated",
                   "structure/interface/data_model/pattern", "docs/tests", "tracing_enabled",
                   "source/test/doc/config fingerprints", "No forced new infrastructure",
                   "line_coverage", "number | null", "aligned/divergent/unavailable",
                   "actual human CR authority", "No task registration, board, Git, app writes",
                   "no repair or adding bugs to authorized refactor scope", "not proven strict-consumer compatibility"):
        assert clause in text
    assert "Coverage must reach 80% before completing" not in text
    assert "All alignment statuses must be" not in text


def sync_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def sync_evidence_fixture(tmp_path):
    """Actual disposable code/check/doc evidence, NOT a production sync engine."""
    from datetime import date
    docs = tmp_path / "docs"
    docs.mkdir()
    requirement = {"goal": "US-PRICE-01", "parent": "FR-PRICE-01", "stakeholder": "buyer",
                   "outcome": "quoted price and alias stay consistent", "constraints": ["no new discounts"],
                   "selection": "all-required", "acs": ["AC-HAPPY", "AC-EDGE", "AC-ERROR"]}
    spec = {"goal": requirement["goal"], "acs": [
        {"id": "AC-HAPPY", "type": "Unit", "gwt": "GIVEN 20 WHEN quoted THEN 18", "expected": 18},
        {"id": "AC-EDGE", "type": "Unit", "gwt": "GIVEN 0 WHEN quoted THEN 0", "expected": 0},
        {"id": "AC-ERROR", "type": "Unit", "gwt": "GIVEN string WHEN quoted THEN TypeError", "expected": "TypeError"}]}
    (docs / "requirements.yaml").write_text(yaml.safe_dump(requirement))
    (docs / "specification.yaml").write_text(yaml.safe_dump(spec))
    design = docs / "technical-design.md"
    design.write_text("# Stale descriptive design\nPublic exports: PriceService\n")
    (tmp_path / "config.json").write_text('{"tracing_enabled": false}')
    authority = {p.name: sync_hash(p) for p in docs.glob("*.yaml")}
    unused = "\ndef legacy_unused(value):\n" + "".join(
        f"    if value == {i}:\n        return {i}\n" for i in range(15)) + "    return None\n"
    base = "def price(value):\n    return value * 0.9\n\ndef price_alias(value):\n    return value * 0.9\n" + unused
    target = "def price(value):\n    return value * 0.9\n\ndef price_alias(value):\n    return price(value)\n" + unused
    runner = (
        "import json\nfrom pathlib import Path\nfrom coverage import Coverage\n"
        "cov = Coverage(data_file=None, include=[str(Path('price.py').resolve())])\n"
        "cov.start()\nfrom price import price, price_alias\n"
        "def error():\n    try:\n        price('invalid')\n    except TypeError:\n        return 'TypeError'\n"
        "observed = {'AC-HAPPY': price(20), 'AC-EDGE': price_alias(0), 'AC-ERROR': error()}\n"
        "alias_preserved = price_alias(20) == price(20)\n"
        "cov.stop()\n_, statements, _, missing, _ = cov.analysis2('price.py')\n"
        "print(json.dumps({'observed': observed, 'alias_preserved': alias_preserved,"
        " 'coverage': {'executed': len(statements)-len(missing), 'denominator': len(statements),"
        " 'method': 'coverage.py statement lines; price.py only'}}))\n"
    )
    checks = {}
    for revision, source in (("base", base), ("target", target)):
        folder = tmp_path / revision
        folder.mkdir()
        (folder / "price.py").write_text(source)
        (folder / "checks.py").write_text(runner)
        command = [sys.executable, "-B", "checks.py"]
        result = subprocess.run(command, cwd=folder, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                                capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        checks[revision] = {"date": date.today().isoformat(), "command": command, "cwd": str(folder),
            "exit": result.returncode, "source_hash": sync_hash(folder / "price.py"),
            "test_hash": sync_hash(folder / "checks.py"), "result": json.loads(result.stdout)}
        assert not (folder / ".coverage").exists() and not (folder / "__pycache__").exists()
    stale_hash = sync_hash(design)
    # Only disposable descriptive doc sync; approved intent and source remain intact.
    design.write_text("# Approved functional API\nPublic exports: price, price_alias\n"
                      "Source: price.py; behavior per US-PRICE-01 / FR-PRICE-01\n")
    assert sync_hash(design) != stale_hash
    record = {"goal": requirement["goal"], "parent": requirement["parent"],
        "source": "docs/requirements.yaml#US-PRICE-01", "acs": requirement["acs"], "type": "Unit",
        "docs_considered": ["docs/requirements.yaml", "docs/specification.yaml", "docs/technical-design.md"],
        "doc_hashes": {p.relative_to(tmp_path).as_posix(): sync_hash(p) for p in docs.iterdir()},
        "config_hash": sync_hash(tmp_path / "config.json"), "checks": checks,
        "alignment_state": "aligned", "outcome_state": "not measured",
        "score": None, "mode": "local", "mandatory_threshold": None}
    return tmp_path, authority, record


def evaluate_sync_fixture(root, authority, record):
    """Evaluate THIS fixture's source/doc/goal/check linkage; not an agent executor.

    Checks actual artifacts and runtime observations, not a fabricated 'aligned'
    flag. Every critical AC is covered at both revisions with unchanged test bytes.
    """
    from datetime import date
    assert {p.name: sync_hash(p) for p in (root / "docs").glob("*.yaml")} == authority
    requirement = yaml.safe_load((root / "docs/requirements.yaml").read_text())
    spec = yaml.safe_load((root / "docs/specification.yaml").read_text())
    assert record["goal"] == requirement["goal"] == spec["goal"]
    assert record["parent"] == requirement["parent"] and requirement["constraints"] == ["no new discounts"]
    assert record["source"] == "docs/requirements.yaml#" + requirement["goal"]
    assert set(record["acs"]) == set(requirement["acs"]) == {ac["id"] for ac in spec["acs"]}
    assert record["type"] == "Unit" and all(ac["type"] == record["type"] for ac in spec["acs"])
    assert all(all(word in ac["gwt"] for word in ("GIVEN", "WHEN", "THEN")) for ac in spec["acs"])
    expected_docs = {"docs/requirements.yaml", "docs/specification.yaml", "docs/technical-design.md"}
    assert set(record["docs_considered"]) == set(record["doc_hashes"]) == expected_docs
    assert all(sync_hash(root / p) == h for p, h in record["doc_hashes"].items())
    assert "Public exports: price, price_alias" in (root / "docs/technical-design.md").read_text()
    assert record["config_hash"] == sync_hash(root / "config.json")
    assert record["outcome_state"] == "not measured" and record["score"] is None
    assert record["alignment_state"] == "aligned"
    assert set(record["checks"]) == {"base", "target"}
    base, target = record["checks"]["base"], record["checks"]["target"]
    assert base["test_hash"] == target["test_hash"]
    for revision, evidence in record["checks"].items():
        assert evidence["date"] == date.today().isoformat()
        assert evidence["command"] == [sys.executable, "-B", "checks.py"]
        assert evidence["cwd"] == str(root / revision) and evidence["exit"] == 0
        assert evidence["source_hash"] == sync_hash(root / revision / "price.py")
        assert evidence["test_hash"] == sync_hash(root / revision / "checks.py")
        assert evidence["result"]["alias_preserved"] is True
        assert evidence["result"]["observed"] == {ac["id"]: ac["expected"] for ac in spec["acs"]}
        coverage = evidence["result"]["coverage"]
        assert coverage["method"] == "coverage.py statement lines; price.py only"
        assert 0 < coverage["executed"] <= coverage["denominator"]
    measured = 100 * target["result"]["coverage"]["executed"] / target["result"]["coverage"]["denominator"]
    threshold = record["mandatory_threshold"]
    return record["mode"] != "study-only" and (threshold is None or measured >= threshold)


def test_sync_actual_doc_alignment_and_goal_critical_mapping_at_base_target(sync_evidence_fixture):
    root, authority, record = sync_evidence_fixture
    assert evaluate_sync_fixture(root, authority, record)
    assert record["checks"]["base"]["source_hash"] != record["checks"]["target"]["source_hash"]
    for revision in ("base", "target"):
        cov = record["checks"][revision]["result"]["coverage"]
        assert 100 * cov["executed"] / cov["denominator"] < 80  # Actual measured fixture, not invented 62%.
    target = root / "validation.json"
    target.write_text(json.dumps(record))
    assert evaluate_sync_fixture(root, authority, json.loads(target.read_text()))


@pytest.mark.parametrize("defect", ["goal", "parent", "source", "critical-ac", "type", "docs-considered",
                                  "doc-hash", "config-hash", "source-hash", "test-hash", "date",
                                  "unavailable", "failed", "wrong-observation", "score", "outcome"])
def test_sync_negative_actual_evidence_mapping_rejects_false_alignment(sync_evidence_fixture, defect):
    root, authority, record = sync_evidence_fixture
    assert evaluate_sync_fixture(root, authority, record)
    if defect in ("goal", "parent", "source", "type", "date", "score", "outcome"):
        if defect == "date":
            record["checks"]["target"]["date"] = "2000-01-01"
        else:
            record[{"outcome": "outcome_state"}.get(defect, defect)] = 10 if defect == "score" else "invented"
    elif defect == "critical-ac":
        record["acs"].remove("AC-ERROR")
    elif defect == "docs-considered":
        record["docs_considered"].remove("docs/technical-design.md")
    elif defect == "doc-hash":
        (root / "docs/technical-design.md").write_text("Public exports: WrongAPI\n")
    elif defect == "config-hash":
        record["config_hash"] = "stale"
    elif defect in ("source-hash", "test-hash"):
        record["checks"]["target"][defect.replace("-", "_")] = "stale"
    elif defect in ("unavailable", "failed"):
        record["checks"]["target"]["exit"] = None if defect == "unavailable" else 3
    else:
        record["checks"]["target"]["result"]["observed"]["AC-ERROR"] = "accepted"
    with pytest.raises(AssertionError):
        evaluate_sync_fixture(root, authority, record)


@pytest.mark.parametrize("mode", ["study-only", "local", "broad"])
def test_sync_actual_below_guideline_coverage_not_arbitrary_block_or_critical_waiver(sync_evidence_fixture, mode):
    root, authority, record = sync_evidence_fixture
    record["mode"] = mode
    assert evaluate_sync_fixture(root, authority, record) is (mode != "study-only")
    # Deliberate authoritative fixture policy: unlike default guideline, binding.
    record["mandatory_threshold"] = 80
    assert evaluate_sync_fixture(root, authority, record) is False
    record["mandatory_threshold"] = None
    record["acs"].remove("AC-ERROR")
    with pytest.raises(AssertionError):
        evaluate_sync_fixture(root, authority, record)


def test_sync_bug_wrong_behavior_test_green_does_not_authorize_requirement_rewrite(tmp_path):
    source = tmp_path / "expiry.py"
    source.write_text("def valid(expiry, now):\n    return expiry >= now\n")
    requirement = tmp_path / "requirements.md"
    requirement.write_text("US-AUTH-01 / AC-AUTH-01: equality is expired; no grace period\n")
    checks = tmp_path / "checks.py"
    checks.write_text("from expiry import valid\nassert valid(10, 10) is True\n")
    source_hash, intent_hash = sync_hash(source), sync_hash(requirement)
    wrong = subprocess.run([sys.executable, "-B", str(checks)], cwd=tmp_path,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True)
    assert wrong.returncode == 0  # Green current-behavior test contradicts authoritative goal.
    expected = tmp_path / "preservation.py"
    expected.write_text("from expiry import valid\nassert valid(10, 10) is False, 'AC-AUTH-01 equality is expired'\n")
    failed = subprocess.run([sys.executable, "-B", str(expected)], cwd=tmp_path,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True)
    assert failed.returncode == 1 and "AC-AUTH-01 equality is expired" in failed.stderr
    assert sync_hash(source) == source_hash and sync_hash(requirement) == intent_hash
    assert expected.exists() and "skip" not in expected.read_text()
    gap = {"alignment_state": "divergent", "kind": "BUG_FOUND", "exit": failed.returncode,
           "ready_for_refactoring": False, "line_coverage": None, "overall_quality_score": None}
    (tmp_path / "gap.json").write_text(json.dumps(gap))
    assert json.loads((tmp_path / "gap.json").read_text()) == gap


def test_sync_authored_template_goal_docs_evidence_and_exact_concrete_pass_through(tmp_path):
    example = (SYNC / "references/examples.md").read_text()
    record, = rows(example, SYNC_TRACE)
    assert record["Goal / Parent / Source"] == "Q-USER-01; US-USER-01; FR-USER-01#AC-USER-01"
    assert record["Docs Considered"] == "requirements; specification; technical design"
    assert "Unit" in record["Preservation / Type"] and "outcome not measured" in record["Evidence / Limits"]
    rendered = render_table_from_scaffold((SYNC / "templates/validation-report.md").read_text(), SYNC_TRACE, [record])
    (tmp_path / "validation.md").write_text(rendered)
    assert rows((tmp_path / "validation.md").read_text(), SYNC_TRACE) == [record]
    analysis = {"refactoring_scope": {"files": ["skill.md"], "goals": ["maintainer safe change"],
        "refactoring_purpose": "preserve approved behavior", "opaque_extension": {"keep": True}},
        "refactoring_suggestion": {"goals": [], "target_structure": "retain skill contracts"},
        "refactoring_principle": {"primary_principles": [], "constraints": ["no new infrastructure"]},
        "code_alignment": {"status": "needs_attention", "opaque": [1, 2]},
        "legacy_coverage": {"current_percentage": 62, "method": "historical differing scope"}}
    before = json.dumps(analysis, sort_keys=True)
    payload = {"success": True, "result": {
        "code_quality_evaluated": {
            "requirements_alignment": {"status": "not_found", "gaps": ["missing intent"], "updates_made": []},
            "specification_alignment": {"status": "not_found", "gaps": [], "updates_made": []},
            "test_coverage": {"status": "not_applicable", "line_coverage": None, "tests_added": 0, "tests_updated": 0,
                              **analysis["legacy_coverage"]},
            "code_alignment": analysis["code_alignment"], "overall_quality_score": None,
            "validation_summary": {"docs_created": 0, "docs_updated": 0, "tests_added": 0,
                                   "ready_for_refactoring": False}},
        **{k: analysis[k] for k in ("refactoring_scope", "refactoring_suggestion", "refactoring_principle")},
        "report_path": "validation.md"}, "errors": []}
    (tmp_path / "operation.json").write_text(json.dumps(payload))
    actual = json.loads((tmp_path / "operation.json").read_text())
    assert list(actual["result"]) == list(ORIGINAL_SYNC_OUTPUT["result"])
    assert json.dumps(analysis, sort_keys=True) == before
    for key in ("refactoring_scope", "refactoring_suggestion", "refactoring_principle"):
        assert actual["result"][key] == analysis[key]
    quality = actual["result"]["code_quality_evaluated"]
    assert quality["code_alignment"] == analysis["code_alignment"]
    assert quality["test_coverage"]["line_coverage"] is quality["overall_quality_score"] is None
    assert quality["test_coverage"]["current_percentage"] == 62  # Historical alias, not fresh coverage claim.


def test_sync_root_metadata_current_receipt_case_mapping_and_review_boundary():
    meta = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", (SYNC_META / "skill-meta.md").read_text(), re.S)[1])
    cases = yaml.safe_load((SYNC_META / "test-cases.yaml").read_text())
    current = validator().validate(ROOT, SYNC, SYNC_NAME, "x-ipe-tool")
    assert current["ok"] and current["files"] == current_publication(SYNC_NAME)["files"]
    # Prior authoring metadata is immutable version history, not a claim about
    # the current candidate. Check it against its own original receipt.
    current = json.loads((SYNC_META / "validation-receipt-goal-TASK-6749.json").read_text())
    assert meta["skill_type"] == "x-ipe-tool" and meta["task_id"] == cases["task_id"] == "TASK-6749"
    assert meta["candidate_hash"] == cases["candidate_hash"] == current["candidate_hash"]
    publication_path = SYNC_META / "publication-receipt-goal-TASK-6749.json"
    expected_state = "published" if publication_path.exists() else "candidate_ready"
    assert meta["publication_state"] == cases["publication_state"] == expected_state
    assert meta["independent_review"] == cases["independent_review"]
    assert meta["independent_review"] in ("pending", "passed_final_revision_review")
    assert {c["id"] for c in meta["acceptance_criteria"]["must"]} <= {ac for c in cases["cases"] for ac in c["covers"]}
    assert cases["preservation"]["production_promoted"] is (expected_state == "published")
    if expected_state == "published":
        assert meta["independent_review"] == "passed_final_revision_review"
        assert meta["version"] == meta["planned_version"] == "2.0.0"
        publication = json.loads(publication_path.read_text())
        assert publication["candidate_hash"] == current["candidate_hash"]
        assert publication["byte_parity"] and publication["publication_state"] == "published"
        assert meta["version_history"][-1]["candidate_hash"] == current["candidate_hash"]
    assert set(meta) >= {"version", "status", "summary", "triggers", "not_for", "inputs", "outputs",
                        "dependencies", "test_scenarios", "evaluation"}


def test_refactor_dependency_contracts_are_revision_specific_after_migration():
    text = " ".join((REFACTOR / "references/integration.md").read_text().split())
    for clause in ("Current full_analysis/full_sync operations", "study-only/local/broad",
                   "actual operation_output", "unknown is null/explicit not measured",
                   "consumer handoff until verified integration"):
        assert clause in text


def test_refactor_nullable_coverage_concrete_handoff_not_placeholder(tmp_path):
    text = " ".join((REFACTOR / "SKILL.md").read_text().split())
    reference = " ".join((REFACTOR / "references/integration.md").read_text().split())
    for clause in ("actual YAML/JSON null", "Preserve a measured side",
                   "required missing measurement blocks that claim", "Consumers rejecting null"):
        assert clause in text
    assert "two non-comparable" in reference and "never coerce null to zero/success" in reference
    # Concrete authored output only: no claim an autonomous agent produced it.
    payload = output_contract(REFACTOR / "SKILL.md")
    quality = payload["code_quality_evaluated"]
    quality["quality_score_before"] = quality["quality_score_after"] = "not measured"
    quality["test_coverage"] = {"before": None, "after": None, "status": None}
    target = tmp_path / "handoff.json"
    target.write_text(json.dumps(payload))
    restored = json.loads(target.read_text())["code_quality_evaluated"]
    assert restored["test_coverage"] == {"before": None, "after": None, "status": None}
    assert restored["quality_score_before"] == "not measured"
    assert list(restored) == list(output_contract(REFACTOR / "SKILL.md")["code_quality_evaluated"])


@pytest.mark.parametrize("folder", [META, BUG_META, REFACTOR_META], ids=["change-request", "bug-fix", "code-refactor"])
def test_root_metadata_formatting_and_template_field_types(folder):
    """Validate current YAML only; historical snapshots remain verbatim text."""
    text = (folder / "skill-meta.md").read_text()
    meta = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", text, re.S)[1])
    assert meta["skill_name"] == folder.name and meta["skill_type"] == "x-ipe-task-based"
    assert meta["task_id"] == "TASK-6749"
    assert isinstance(meta["version"], str) and isinstance(meta["summary"], str)
    assert set(meta) >= {"triggers", "not_for", "workflow", "inputs", "outputs",
                         "acceptance_criteria", "dependencies", "test_scenarios", "evaluation"}
    for group in ("required", "optional"):
        for item in meta["inputs"][group]:
            assert isinstance(item["name"], str) and isinstance(item["type"], str)
            assert set(item) <= {"name", "type", "default", "description", "validation"}
    for group in ("state", "artifacts", "data"):
        for item in meta["outputs"][group]:
            assert isinstance(item["name"], str)
            assert set(item) <= {"name", "value", "type", "path", "description"}
            if "type" in item:
                assert isinstance(item["type"], str)
    ids = []
    for group in ("must", "should", "could", "wont"):
        for criterion in meta["acceptance_criteria"][group]:
            ids.append(criterion["id"])
            assert isinstance(criterion["criterion"], str)
            assert set(criterion) <= {"id", "category", "criterion", "test", "expected", "reason"}
            if group == "must":
                assert isinstance(criterion["test"], str)
    assert len(ids) == len(set(ids))


ANALYSIS_NAME = "x-ipe-tool-refactoring-analysis"
ANALYSIS_META = ROOT / "x-ipe-docs/skill-meta" / ANALYSIS_NAME
ANALYSIS = ANALYSIS_META / "candidate"
ANALYSIS_TRACE = ("Suggestion", "Gap / Source", "Goal / Parent", "Baseline",
                  "Success Evidence", "Preservation", "Trade-off", "Outcome State")

ORIGINAL_ANALYSIS_OUTPUT = {
    "success": "true | false", "result": {
        "quality_baseline": {"exists": "true | false", "overall_score": "<1-10>"},
        "refactoring_scope": {
            "scope_level": "feature | custom", "feature_id": "{FEATURE-XXX or null}",
            "refactoring_purpose": "<purpose>", "files": ["<expanded file list>"],
            "modules": ["<expanded module list>"], "dependencies": ["<identified dependencies>"],
            "scope_expansion_log": ["<log entries>"]},
        "code_quality_evaluated": {
            "requirements_alignment": {"score": "<1-10>", "status": "<aligned|needs_attention|critical>", "gaps": []},
            "specification_alignment": {"score": "<1-10>", "status": "<aligned|needs_attention|critical>", "gaps": []},
            "test_coverage": {"score": "<1-10>", "line_coverage": "<XX%>", "critical_gaps": []},
            "code_alignment": {"score": "<1-10>", "file_size_violations": [], "solid_assessment": {}, "kiss_assessment": {}},
            "overall_quality_score": "<1-10>"},
        "refactoring_suggestion": {
            "summary": "<high-level description>",
            "goals": [{"goal": "<specific goal>", "priority": "<high|medium|low>", "rationale": "<why>"}],
            "target_structure": "<desired end state>"},
        "refactoring_principle": {
            "primary_principles": [{"principle": "<name>", "rationale": "<why>", "applications": []}],
            "secondary_principles": [{"principle": "<name>", "rationale": "<why>"}],
            "constraints": [{"constraint": "<what>", "reason": "<why>"}]},
        "report_path": "x-ipe-docs/refactoring/analysis-{context}.md"}, "errors": [],
}


def analysis_output(path):
    text = path.read_text().split("## Output Result", 1)[1]
    return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", text, re.S)[1])["operation_output"]


def test_analysis_complete_tool_bundle_original_keys_and_no_task_logic():
    result = validator().validate(ROOT, ANALYSIS, ANALYSIS_NAME, "x-ipe-tool")
    assert result["ok"] and not result["warnings"], result
    baseline = json.loads((ANALYSIS_META / "baseline-goal-TASK-6749.json").read_text())
    assert set(result["files"]) == set(baseline)
    live = validator().manifest(validator().tree_bytes(ROOT / ".github/skills" / ANALYSIS_NAME, ROOT))
    old = ORIGINAL_ANALYSIS_OUTPUT
    new = analysis_output(ANALYSIS / "SKILL.md")
    expected = json.loads(json.dumps(old))
    expected["result"]["quality_baseline"]["overall_score"] = "<number 1-10 | null>"
    quality = expected["result"]["code_quality_evaluated"]
    for record in quality.values():
        if isinstance(record, dict):
            record["score"] = "<number 1-10 | null>"
            if "status" in record:
                record["status"] = "<evidence status>"
    quality["overall_quality_score"] = "<number 1-10 | null>"
    quality["test_coverage"]["line_coverage"] = "<percentage string | null>"
    assert new == expected
    assert list(old) == list(new) == ["success", "result", "errors"]
    assert list(old["result"]) == list(new["result"])
    for key in old["result"]:
        if isinstance(old["result"][key], dict):
            assert set(old["result"][key]) <= set(new["result"][key])
    package = "\n".join(p.read_text() for p in ANALYSIS.rglob("*.md"))
    for forbidden in ("task_completion_output:", "Output:\n", "task_create.py", "task_update.py",
                      "force-enable general", "all tools enabled", "weighted_average(",
                      "score = 10 -", "Approve to proceed", "git commit"):
        assert forbidden not in package
    for resource in baseline:
        assert (ANALYSIS / resource).is_file()
    publication_path = ANALYSIS_META / "publication-receipt-goal-TASK-6749.json"
    if publication_path.exists():
        publication = json.loads(publication_path.read_text())
        assert publication["publication_state"] == "published" and publication["byte_parity"]
        assert publication["baseline_hash"] == validator().fingerprint(baseline)
        newest = current_publication(ANALYSIS_NAME)
        assert newest["baseline_hash"] == publication["candidate_hash"]
        assert newest["candidate_hash"] == result["candidate_hash"]
        assert live == result["files"] == newest["files"]
        assert publication["changed"] == sorted(baseline)
        assert publication["added"] == publication["removed"] == []
        assert analysis_output(ROOT / ".github/skills" / ANALYSIS_NAME / "SKILL.md") == expected
    else:
        assert live == baseline
        assert analysis_output(ROOT / ".github/skills" / ANALYSIS_NAME / "SKILL.md") == old


def test_analysis_goal_risk_five_perspectives_and_missing_vs_failed():
    text = " ".join((ANALYSIS / "SKILL.md").read_text().split())
    for clause in ("refactoring_purpose", "source/parent", "all-required", "alternatives",
                   "trade-off", "not measured", "Requirements", "Features", "Tech Spec",
                   "Test Coverage", "Tracing", "not_found", "not_measured", "failed",
                   "not_applicable", "No blanket compile", "analysis-only",
                   "No source/test/config", "same scope", "No arbitrary weighted score"):
        assert clause in text
    init = ET.fromstring(re.search(r"<input_init>.*?</input_init>", (ANALYSIS / "SKILL.md").read_text(), re.S)[0])
    assert {f.attrib["name"] for f in init.findall("field")} >= {
        "operation", "scope.scope_level", "scope.feature_id", "scope.files", "scope.modules",
        "scope.refactoring_purpose", "scope.description", "quality_baseline_path"}


def test_analysis_real_configuration_progressive_matched_consultation():
    config = json.loads((ROOT / "x-ipe-docs/config/tools.json").read_text())
    assert config["stages"]["validation"]["refactoring_analysis"]["x-ipe-tool-implementation-python"] is True
    assert config["stages"]["validation"]["code_refactor"]["x-ipe-tool-implementation-python"] is True
    text = " ".join((ANALYSIS / "references/detailed-procedures.md").read_text().split())
    for clause in ("stages.validation.refactoring_analysis", "stages.validation.code_refactor",
                   "metadata first", "explicit false",
                   "missing/empty", "semantically matched", "sequentially", "consultation only",
                   "no force-enable", "not execution evidence", "not a new analysis key"):
        assert clause in text
    assert "auto-enforced by tool" not in text


def test_analysis_malformed_configuration_is_not_permissive_discovery():
    text = " ".join((ANALYSIS / "references/detailed-procedures.md").read_text().split())
    for clause in ("non-boolean tool flags return CONFIG_INVALID", "no consultation",
                   "Never treat strings, numbers or null as booleans", "metadata-only routes",
                   "An all-false tool map consults no tool", "not malformed configuration"):
        assert clause in text
    assert "`CONFIG_INVALID`" in (ANALYSIS / "SKILL.md").read_text()


def test_analysis_retains_optional_legacy_coverage_alias_and_provenance(tmp_path):
    schema = (ANALYSIS / "references/output-schema.md").read_text()
    declared = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", schema, re.S)[1])
    assert "current_percentage" in declared["operation_output"]["result"]["code_quality_evaluated"]["test_coverage"]
    assert "legacy percentage number 0-100" in declared["operation_output"]["result"]["code_quality_evaluated"]["test_coverage"]["current_percentage"]
    for clause in ("passes through when supplied", "Do not silently drop or overwrite",
                   "original method/scope/provenance", "identify conflicts", "absent alias need not be invented"):
        assert clause in " ".join(schema.split())
    # Concrete authored passthrough serialization, not an autonomous tool invocation.
    quality = {"line_coverage": "70%", "current_percentage": 60,
               "evidence": {"line_scope": "current fixture", "legacy_scope": "historical fixture"}}
    target = tmp_path / "legacy-coverage.json"
    target.write_text(json.dumps(quality))
    assert json.loads(target.read_text()) == quality


def check_analysis_trace(text):
    item, = rows(text, ANALYSIS_TRACE)
    assert item["Suggestion"] == "S-01 extract shared price decision"
    assert item["Gap / Source"] == "G-01; price.py repeated expression; fixture revision"
    assert item["Goal / Parent"] == "Q-DUP-01; US-PRICE-01; maintainer safe-change confidence"
    assert item["Baseline"] == "two repeated decisions; public results/errors unchanged"
    assert item["Success Evidence"] == "one shared decision; same public contract checks planned"
    assert item["Preservation"] == "AC-PRICE-01; Unit; keep exports/results/TypeError"
    assert item["Trade-off"] == "extra internal call; no performance claim"
    assert item["Outcome State"] == "not measured"


def test_analysis_authored_trace_report_in_temp_not_actual_skill_execution(tmp_path):
    example = (ANALYSIS / "references/examples.md").read_text()
    check_analysis_trace(example)
    target = tmp_path / "analysis.md"
    target.write_text(example)
    check_analysis_trace(target.read_text())
    assert list(tmp_path.iterdir()) == [target]
    for clause in ("API module", "legacy/payment.js", "missing documents", "not zero coverage",
                   "skills/documents", "not measured", "cap", "cycle", "src/models/user.py"):
        assert clause.lower() in " ".join(example.split()).lower()


@pytest.mark.parametrize("old,new", [
    ("G-01; price.py repeated expression; fixture revision", "size alone"),
    ("two repeated decisions; public results/errors unchanged", "uninspected baseline"),
    ("Q-DUP-01; US-PRICE-01; maintainer safe-change confidence", "invented parent"),
    ("AC-PRICE-01; Unit; keep exports/results/TypeError", "change behavior"),
    ("extra internal call; no performance claim", "automatic stakeholder gain"),
    ("not measured", "observed outcome"),
])
def test_analysis_negative_authored_trace_rejects_unsupported_claim(old, new):
    text = (ANALYSIS / "references/examples.md").read_text()
    assert old in text
    with pytest.raises(AssertionError):
        check_analysis_trace(text.replace(old, new))


def test_analysis_disposable_known_dependency_cycle_stable_and_cap_is_not_cycle_proof(tmp_path):
    """Tiny real import fixture; not a general analyzer or autonomous tool execution."""
    import ast
    fixtures = {"a.py": "import b\n", "b.py": "import a\n", "caller.py": "import a\n",
                "unrelated.py": "value = 1\n"}
    for name, content in fixtures.items():
        (tmp_path / name).write_text(content)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()}
    edges = {(p.name, node.names[0].name + ".py") for p in tmp_path.glob("*.py")
             for node in ast.walk(ast.parse(p.read_text())) if isinstance(node, ast.Import)}
    assert edges == {("a.py", "b.py"), ("b.py", "a.py"), ("caller.py", "a.py")}
    seen = {"a.py"}
    logs = []
    for iteration in range(1, 11):
        additions = {n for edge in edges if set(edge) & seen for n in edge} - seen
        logs.append((iteration, sorted(additions)))
        seen.update(additions)
        if not additions:
            break
    assert seen == {"a.py", "b.py", "caller.py"}
    assert logs == [(1, ["b.py", "caller.py"]), (2, [])]
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()} == before
    text = " ".join((ANALYSIS / "references/detailed-procedures.md").read_text().split())
    for clause in ("visited", "1 through 10", "frontier", "not proof of a cycle",
                   "inspection is not write permission", "unresolved", "no sibling inclusion by proximity"):
        assert clause in text


def test_analysis_nullable_numeric_fields_and_concrete_evidence_states(tmp_path):
    text = " ".join((ANALYSIS / "references/output-schema.md").read_text().split())
    for clause in ("number | null", "not_measured", "not_found", "not_applicable", "failed",
                   "method", "denominator", "rubric", "not measured", "not the string", "success"):
        assert clause in text
    declared = analysis_output(ANALYSIS / "SKILL.md")
    # Authored values with original keys; metadata schemas are not executable analysis.
    report = tmp_path / "analysis.md"
    report.write_text("# Authored fixture report\nAll five states explicit; numeric rubric not measured.\n")
    quality = {
        "requirements_alignment": {"score": None, "status": "not_found", "gaps": []},
        "specification_alignment": {"score": None, "status": "not_found", "gaps": []},
        "test_coverage": {"score": None, "line_coverage": None, "critical_gaps": [],
                          "status": "not_measured"},
        "code_alignment": {"score": None, "file_size_violations": [], "solid_assessment": {},
                           "kiss_assessment": {}, "status": "not_measured"},
        "overall_quality_score": None,
        "feature_alignment": {"score": None, "status": "not_found", "gaps": []},
        "technical_spec_alignment": {"score": None, "status": "not_found", "gaps": []},
        "tracing_coverage": {"score": None, "status": "not_applicable", "gaps": []},
    }
    payload = {"success": True, "result": {
        "quality_baseline": {"exists": False, "overall_score": None},
        "refactoring_scope": {"scope_level": "custom", "feature_id": None,
            "refactoring_purpose": "fixture study", "files": [report.name], "modules": [],
            "dependencies": [], "scope_expansion_log": []},
        "code_quality_evaluated": quality,
        "refactoring_suggestion": {"summary": "No evidenced structural gap", "goals": [],
                                  "target_structure": "No change recommended"},
        "refactoring_principle": {"primary_principles": [], "secondary_principles": [],
            "constraints": [{"constraint": "Preserve public behavior", "reason": "fixture scope"}]},
        "report_path": report.name}, "errors": []}
    assert list(payload["result"]) == list(declared["result"])
    target = tmp_path / "analysis.json"
    target.write_text(json.dumps(payload))
    stored = json.loads(target.read_text())
    assert stored["success"] is True and stored["errors"] == []
    assert stored["result"]["quality_baseline"] == {"exists": False, "overall_score": None}
    assert stored["result"]["code_quality_evaluated"]["overall_quality_score"] is None
    assert all(v["score"] is None for v in quality.values() if isinstance(v, dict))
    assert {quality[k]["status"] for k in ("requirements_alignment", "feature_alignment",
        "technical_spec_alignment", "test_coverage", "tracing_coverage")} == {
            "not_found", "not_measured", "not_applicable"}


def test_analysis_disposable_cap_unavailable_and_executed_failure_distinct(tmp_path):
    """Characterize actual local observations, not an instruction-agent execution."""
    source = tmp_path / "node0.py"
    source.write_text("import node1\n")
    for i in range(1, 12):
        (tmp_path / f"node{i}.py").write_text(f"import node{i + 1}\n" if i < 11 else "value = 1\n")
    frontier = {"node0.py"}
    visited = set()
    for _ in range(10):
        current = frontier - visited
        visited.update(current)
        frontier = {f"node{int(name[4:-3]) + 1}.py" for name in current} - visited
    assert frontier == {"node10.py"} and len(visited) == 10
    assert "node11.py" not in visited  # cap cannot claim complete known closure
    unavailable = tmp_path / "missing-checker"
    assert not unavailable.exists()  # not executed, not an observed check failure
    failed = subprocess.run([sys.executable, "-B", "-c", "raise SystemExit(3)"], cwd=tmp_path,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True)
    assert failed.returncode == 3  # actual attempted failure
    evidence = {"unavailable": {"status": "not_measured", "exit": None},
                "attempted": {"status": "failed", "exit": failed.returncode},
                "closure": {"state": "capped", "frontier": sorted(frontier)}}
    target = tmp_path / "evidence.json"
    target.write_text(json.dumps(evidence))
    assert json.loads(target.read_text()) == evidence
    assert source.read_text() == "import node1\n"


def test_analysis_current_receipt_metadata_cases_and_reviewed_publication_state():
    current = validator().validate(ROOT, ANALYSIS, ANALYSIS_NAME, "x-ipe-tool")
    assert current["ok"] and current["files"] == current_publication(ANALYSIS_NAME)["files"]
    current = json.loads((ANALYSIS_META / "validation-receipt-goal-TASK-6749.json").read_text())
    meta = yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", (ANALYSIS_META / "skill-meta.md").read_text(), re.S)[1])
    cases = yaml.safe_load((ANALYSIS_META / "test-cases.yaml").read_text())
    assert meta["skill_type"] == "x-ipe-tool"
    assert meta["task_id"] == cases["task_id"] == "TASK-6749"
    assert meta["candidate_hash"] == cases["candidate_hash"] == current["candidate_hash"]
    publication_path = ANALYSIS_META / "publication-receipt-goal-TASK-6749.json"
    expected_state = "published" if publication_path.exists() else "candidate_ready"
    assert meta["publication_state"] == cases["publication_state"] == expected_state
    assert meta["independent_review"] == cases["independent_review"] == "passed_final_revision_review"
    assert {c["id"] for c in meta["acceptance_criteria"]["must"]} <= {ac for c in cases["cases"] for ac in c["covers"]}
    assert cases["preservation"]["production_promoted"] is (expected_state == "published")
    if expected_state == "published":
        assert meta["version"] == meta["planned_version"] == "2.0.0"