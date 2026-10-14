"""Authored artifacts and rendered scaffolds, not autonomous-agent behavior tests.

Parse source -> parent/subgoal -> GWT AC -> evidence mappings from real candidate
examples. Negative fixtures detect broken claims. Temporary rendering is a test
of template expressiveness, not execution of a requirement/refinement agent.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys

import pytest
import yaml

from tests.publication_recovery_6749 import recovered_publication


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "x-ipe-docs/skill-meta"
NAMES = (
    "x-ipe-workflow-task-execution",
    "x-ipe-task-based-requirement-gathering",
    "x-ipe-task-based-feature-breakdown",
    "x-ipe-task-based-feature-refinement",
)
WORKFLOW, REQUIREMENT, BREAKDOWN, REFINEMENT = [META / n / "candidate" for n in NAMES]
GOAL_COLUMNS = (
    "Goal ID", "Parent / Source", "Stakeholder", "Desired Observable Outcome",
    "Contribution / Selection", "Success Evidence", "Constraints / Non-goals",
    "AC Links", "Outcome State",
)
AC_COLUMNS = ("AC ID", "Criterion (Given/When/Then)", "Test Type")
EVIDENCE_COLUMNS = ("AC ID", "Validation Evidence", "Delivery State", "Outcome State")


def validator():
    path = ROOT / ".github/skills/x-ipe-meta-skill-creator/scripts/validate_skill.py"
    spec = importlib.util.spec_from_file_location("goal_validator", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_reviewed_live(name, live, baseline):
    """Allow only the untouched baseline or a fingerprinted goal publication."""
    path = META / name / "promotion-receipt-goal-TASK-6749.json"
    if not path.exists():
        assert live == baseline
        return
    receipt = json.loads(path.read_text())
    v = validator()
    assert receipt["publication_state"] == "published"
    assert receipt["byte_parity"] is True
    assert receipt["baseline_files"] == baseline
    assert receipt["baseline_hash"] == v.fingerprint(baseline)
    assert receipt["production_hash"] == receipt["candidate_hash"] == v.fingerprint(receipt["files"])
    assert receipt["removed"] == []
    current_path = META / name / "publication-receipt-mode-TASK-6749-R2.json"
    if name == "x-ipe-workflow-task-execution" and current_path.exists():
        current = json.loads(current_path.read_text())
        assert current["operation"] == "publish" and current["state"] == "published"
        assert current["byte_parity"] is True and current["files"] == live
        assert current["baseline_hash"] == receipt["candidate_hash"]
        assert current["candidate_hash"] == v.fingerprint(live)
        assert v.manifest(v.tree_bytes(Path(current["transaction"]) / "backup", ROOT)) == receipt["files"]
    else:
        if (META / name / "publication-receipt-TASK-6749-R2.json").exists():
            current = recovered_publication(name, live)
            assert current["baseline_hash"] == receipt["candidate_hash"]
        else:
            # Original single-publication disposable tampering fixture.
            assert live == receipt["files"]


def rows(text, columns):
    """Read a concrete Markdown table, retaining column names and order."""
    lines = text.splitlines()
    header = "| " + " | ".join(columns) + " |"
    start = lines.index(header)
    assert re.fullmatch(r"[| :\-]+", lines[start + 1])
    result = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        values = [v.strip() for v in line.strip("|").split("|")]
        assert len(values) == len(columns)
        result.append(dict(zip(columns, values)))
    assert result
    return result


@pytest.fixture(params=["new", "legacy", "delta"])
def authored_scope(request):
    text = (REFINEMENT / "references/examples.md").read_text()
    if request.param == "new":
        scope = text.split("## 2.", 1)[0]
    elif request.param == "legacy":
        scope = text.split("## 6.", 1)[1].split("## 7.", 1)[0]
    else:
        scope = text.split("## 7.", 1)[1]
    return request.param, scope


def check_chain(text, *, legacy=False):
    goals = rows(text, GOAL_COLUMNS)
    evidence = rows(text, EVIDENCE_COLUMNS)
    evidence_ids = [row["AC ID"] for row in evidence]
    assert len(evidence_ids) == len(set(evidence_ids))
    if legacy:
        # Historical criteria stay non-GWT; only explicit so-that permits inference.
        assert "so that" in text
        ac_ids = set(re.findall(r"\*\*(AC-[\w.-]+):\*\*", text))
    else:
        acs = rows(text, AC_COLUMNS)
        ac_ids = {a["AC ID"] for a in acs}
        assert len(ac_ids) == len(acs)
        for ac in acs:
            assert re.search(r"\bGIVEN\b.+\bWHEN\b.+\bTHEN\b.+", ac["Criterion (Given/When/Then)"])
            assert ac["Test Type"] in {"UI", "API", "Unit", "Integration"}
    covered = set()
    assert len({g["Goal ID"] for g in goals}) == len(goals)
    for goal in goals:
        assert all(goal[c] for c in GOAL_COLUMNS)
        assert "source" in goal["Parent / Source"].lower() or "FR-061-01" in goal["Parent / Source"] or "inferred from" in goal["Parent / Source"]
        if legacy:
            assert "inferred from" in goal["Parent / Source"]
        links = {v.strip() for v in goal["AC Links"].split(",")}
        assert links <= ac_ids and links <= set(evidence_ids)
        covered.update(links)
        # These authored fixtures have no actual stakeholder observations.
        assert goal["Outcome State"] == "not measured"
    assert covered == ac_ids == set(evidence_ids)
    for item in evidence:
        assert item["Outcome State"] == "not measured"
        assert item["Delivery State"] in {"planned", "invalidated by goal delta"}
        assert "planned" in item["Validation Evidence"]
        if item["Delivery State"] == "invalidated by goal delta":
            assert "parent delta" in item["Validation Evidence"]
    return goals, evidence


def test_authored_new_legacy_delta_goal_ac_evidence(authored_scope):
    kind, text = authored_scope
    check_chain(text, legacy=kind == "legacy")


@pytest.mark.parametrize("defect", ["orphan-ac", "missing-evidence", "false-outcome", "false-delivery", "not-gwt", "duplicate-ac", "false-source", "empty-contribution"])
def test_concrete_artifact_defects_are_rejected(defect):
    text = (REFINEMENT / "references/examples.md").read_text().split("## 2.", 1)[0]
    if defect == "orphan-ac":
        text = text.replace("AC-061-A-01, AC-061-A-02", "AC-061-A-01, AC-NOT-DEFINED", 1)
    elif defect == "missing-evidence":
        text = text.replace("| AC-061-A-02 | planned UI check of absent-state label | planned | not measured |\n", "")
    elif defect == "false-outcome":
        text = text.replace("| not measured |", "| observed stakeholder outcome |", 1)
    elif defect == "false-delivery":
        text = text.replace("| planned | not measured |", "| verified engineering delivery | not measured |", 1)
    elif defect == "not-gwt":
        text = text.replace("GIVEN operator views", "operator views", 1)
    elif defect == "duplicate-ac":
        text = text.replace("AC-061-A-02", "AC-061-A-01")
    elif defect == "false-source":
        text = text.replace("FR-061-01; explicit badge request", "unsupported assertion", 1)
    else:
        text = text.replace("FEATURE-061-A readable badge selected; all-required available and absent-state handling", "", 1)
    with pytest.raises(AssertionError):
        check_chain(text)


def test_requirement_breakdown_refinement_parent_chain_and_selected_means():
    req = rows((REQUIREMENT / "references/examples.md").read_text(), GOAL_COLUMNS)[0]
    mapping = rows((REQUIREMENT / "references/examples.md").read_text(),
                   ("Requirement ID", "Goal ID", "Source / Evidence", "Constraints"))[0]
    breakdown = (BREAKDOWN / "references/examples.md").read_text()
    subgoal = rows(breakdown, GOAL_COLUMNS)[0]
    spec = rows((REFINEMENT / "references/examples.md").read_text(), GOAL_COLUMNS)[0]
    assert req["Goal ID"] == mapping["Goal ID"] == mapping["Requirement ID"] == "FR-061-01"
    assert req["Goal ID"] in subgoal["Parent / Source"]
    assert subgoal["Goal ID"] == spec["Goal ID"] == "US-061-A-01"
    assert subgoal["AC Links"] == spec["AC Links"] == req["AC Links"].split(" (", 1)[0]
    means = rows(breakdown, ("Means", "Selection", "Bound / Rationale"))
    assert [m["Means"] for m in means if m["Selection"] == "selected"] == ["Badge"]
    features = rows(breakdown, ("Feature ID", "Epic ID", "Feature Title", "Version", "Brief Description", "Feature Dependency"))
    assert len(features) == 1 and features[0]["Feature Dependency"] == "None"
    assert "all-required" in subgoal["Contribution / Selection"]


def render_table_from_scaffold(scaffold, columns, concrete_rows):
    """Instantiate its existing columns; no invented alternate goal schema."""
    template_rows = rows(scaffold, columns)
    assert len(template_rows) >= 1
    header = "| " + " | ".join(columns) + " |"
    start = scaffold.index(header)
    end = scaffold.find("\n\n", start)
    table = header + "\n| " + " | ".join("---" for _ in columns) + " |\n"
    table += "\n".join("| " + " | ".join(row[c] for c in columns) + " |" for row in concrete_rows)
    return scaffold[:start] + table + scaffold[end:]


def test_actual_scaffolds_render_valid_goal_mapping_in_existing_artifacts(tmp_path):
    example = (REFINEMENT / "references/examples.md").read_text().split("## 2.", 1)[0]
    goals, evidence = check_chain(example)
    scaffold = (REFINEMENT / "references/specification-template.md").read_text()
    rendered = render_table_from_scaffold(scaffold, GOAL_COLUMNS, goals)
    rendered = render_table_from_scaffold(rendered, EVIDENCE_COLUMNS, evidence)
    # Replace every sample AC group with the concrete authored new-scope table.
    block = re.search(r"\| AC ID \| Criterion \(Given/When/Then\).*?(?=\n\n)", example, re.S)[0]
    rendered = re.sub(r"### AC-XXX-01:.*?(?=> \*\*Test Type Legend:)", block + "\n\n", rendered, flags=re.S)
    path = tmp_path / "specification.md"
    path.write_text(rendered)
    check_chain(path.read_text())
    for package, resource in ((REQUIREMENT, "references/requirement-details-template.md"),
                              (BREAKDOWN, "templates/requirement-details.md")):
        text = render_table_from_scaffold((package / resource).read_text(), GOAL_COLUMNS, goals)
        assert rows(text, GOAL_COLUMNS) == goals
    assert list(tmp_path.iterdir()) == [path]  # no goal database/graph produced


def test_legacy_inference_matches_actual_readonly_source_without_rewriting():
    actual = (ROOT / "x-ipe-docs/requirements/EPIC-047/FEATURE-047-A/specification.md").read_text()
    legacy = (REFINEMENT / "references/examples.md").read_text().split("## 6.", 1)[1].split("## 7.", 1)[0]
    for line in legacy.splitlines():
        if line.startswith(("- **US-1:", "- [ ] **AC-047-A.1:")):
            assert line in actual
    check_chain(legacy, legacy=True)
    with pytest.raises(AssertionError):
        check_chain(legacy.replace("so that", "because").replace("inferred from", "confirmed by"), legacy=True)


def test_delta_keeps_ids_unaffected_ac_bytes_and_invalidates_parent_evidence():
    text = (REFINEMENT / "references/examples.md").read_text()
    old = text.split("## 2.", 1)[0]
    delta = text.split("## 7.", 1)[1]
    before, after = rows(old, AC_COLUMNS), rows(delta, AC_COLUMNS)
    assert [a["AC ID"] for a in before] == [a["AC ID"] for a in after]
    assert before[1] == after[1] and before[0] != after[0]
    goals, evidence = check_chain(delta)
    assert "CR-061-01 parent goal delta" in goals[0]["Parent / Source"]
    assert evidence[0]["Delivery State"] == "invalidated by goal delta"
    assert evidence[1]["Delivery State"] == "planned"


@pytest.mark.parametrize("name", NAMES)
def test_fresh_production_baseline_complete_candidate_and_original_output(name):
    v = validator()
    production = ROOT / ".github/skills" / name
    candidate = META / name / "candidate"
    baseline = json.loads((META / name / "baseline-goal-TASK-6749.json").read_text())
    assert_reviewed_live(name, v.manifest(v.tree_bytes(production, ROOT)), baseline)
    receipt = v.validate(ROOT, candidate, name,
                         "x-ipe-workflow-orchestration" if name == NAMES[0] else "x-ipe-task-based")
    assert receipt["ok"], receipt["errors"]
    expected = set(baseline)
    if name == NAMES[0]:
        expected.add("references/goal-contract.md")
    elif name == NAMES[3]:
        expected.add("references/integration.md")
        prior = json.loads((META / name / "prework-candidate-goal-TASK-6749.json").read_text())
        assert receipt["files"]["references/integration.md"] == prior["references/integration.md"]
    assert set(receipt["files"]) == expected
    def output(path):
        part = path.read_text().split("## Output Result", 1)[1]
        return yaml.safe_load(re.search(r"```yaml\n(.*?)\n```", part, re.S)[1])
    assert output(candidate / "SKILL.md") == output(production / "SKILL.md")
    assert list(output(candidate / "SKILL.md")) == list(output(production / "SKILL.md"))


def test_adoption_guidance_has_honest_downstream_boundaries():
    # Descriptive guidance tests only; they do not prove autonomous execution.
    common = (WORKFLOW / "references/goal-contract.md").read_text()
    lifecycle = (WORKFLOW / "references/lifecycle.md").read_text()
    assert "explicitly adopting child's" in common and "Optional goal-contract adoption" in lifecycle
    domain = rows(common, ("Domain", "Goal/evidence use in its existing artifact"))
    assert {r["Domain"] for r in domain} == {"Design / implementation", "Acceptance / closing", "CR", "Bug", "Quality / refactor"}
    assert "inspected baseline" in domain[-1]["Goal/evidence use in its existing artifact"]
    assert "Restore documented expected behavior" in domain[-2]["Goal/evidence use in its existing artifact"]
    assert "invalidate affected" in domain[-3]["Goal/evidence use in its existing artifact"]
    for package in (REQUIREMENT, BREAKDOWN, REFINEMENT):
        entry = (package / "SKILL.md").read_text()
        target = re.search(r"\[goal contract\]\(([^)]+)\)", entry)[1]
        canonical = ".github/skills/x-ipe-workflow-task-execution/references/goal-contract.md"
        if (ROOT / canonical).exists():
            assert target == canonical
        else:
            # Explicit pending external dependency, not a missing-link waiver.
            assert target == "x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/candidate/references/goal-contract.md"
            assert not (META / NAMES[0] / "promotion-receipt-goal-TASK-6749.json").exists()
        assert (ROOT / target).read_text() == common
        assert "BLOCKING:" in entry[:entry.index("## Input Parameters")]


def test_shared_goal_self_reference_resolves_to_complete_candidate_before_release():
    v = validator()
    production_contract = ROOT / ".github/skills" / NAMES[0] / "references/goal-contract.md"
    assert (WORKFLOW / "references/goal-contract.md").is_file()
    # Self references map to candidate; absent production is legitimate only
    # before the reviewed workflow publication, never a child dependency waiver.
    result = v.validate(ROOT, WORKFLOW, NAMES[0], "x-ipe-workflow-orchestration")
    assert result["ok"], result["errors"]
    if not production_contract.exists():
        assert not (META / NAMES[0] / "promotion-receipt-goal-TASK-6749.json").exists()


def test_goal_promotion_tampering_is_rejected(tmp_path, monkeypatch):
    baseline = {"SKILL.md": "a" * 64}
    live = {"SKILL.md": "b" * 64}
    v = validator()
    monkeypatch.setattr(sys.modules[__name__], "META", tmp_path)
    package = tmp_path / NAMES[0]
    package.mkdir()
    receipt = {"publication_state": "published", "byte_parity": True,
               "baseline_files": baseline, "baseline_hash": v.fingerprint(baseline),
               "files": live, "production_hash": v.fingerprint(live),
               "candidate_hash": v.fingerprint(live), "removed": []}
    path = package / "promotion-receipt-goal-TASK-6749.json"
    path.write_text(json.dumps(receipt))
    assert_reviewed_live(NAMES[0], live, baseline)
    with pytest.raises(AssertionError):
        assert_reviewed_live(NAMES[0], {"SKILL.md": "c" * 64}, baseline)
    receipt["baseline_hash"] = "forged"
    path.write_text(json.dumps(receipt))
    with pytest.raises(AssertionError):
        assert_reviewed_live(NAMES[0], live, baseline)