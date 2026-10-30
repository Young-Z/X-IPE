"""Static authoring contracts, not live-agent evaluations or performance evidence."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit
from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest
import yaml

from tests.skill_validation_harness_6749 import copy_resources


ROOT = Path(__file__).resolve().parents[1]
NAME = "x-ipe-meta-skill-creator"
CANDIDATE = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
SKILLS = next(
    path for path in (ROOT / ".github/skills", ROOT / ".github_to_be_refactor/skills")
    if (path / NAME / "SKILL.md").is_file()
)
TEMPLATES = {
    "x-ipe-task-based": "x-ipe-task-based.md",
    "x-ipe-tool": "x-ipe-tool.md",
    "x-ipe-workflow-orchestration": "x-ipe-workflow-orchestration.md",
    "x-ipe-task-category": "x-ipe-workflow-orchestration.md",
    "x-ipe-meta": "x-ipe-meta.md",
    "x-ipe-knowledge": "x-ipe-knowledge.md",
    "x-ipe-assistant": "x-ipe-assistant.md",
    "x-ipe-dao": "x-ipe-dao.md",
}
MODES = (
    "interact-with-human",
    "dao-represent-human-to-interact",
    "dao-represent-human-to-interact-for-questions-in-skill",
)


def read(relative):
    return (CANDIDATE / relative).read_text(encoding="utf-8")


def load_validator():
    path = SKILLS / NAME / "scripts/validate_skill.py"
    spec = importlib.util.spec_from_file_location("single_loop_validator", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Execute source directly so validation never writes caches into a package.
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


@pytest.mark.parametrize("kind", TEMPLATES)
def test_every_subtype_defaults_to_same_loop(kind):
    template = read(f"templates/{TEMPLATES[kind]}")
    assert "Default to one model/context open-ended loop" in template
    assert "apply tool skills in the same loop" in template
    assert "single-loop-authoring.md" in template
    assert "risk-triggered independent review" in template
    assert "schedule_dod_checks_with_sub_agent" not in template
    assert "<sub-agent-planning>" not in template
    assert "Best-Model Requirement" not in template
    if kind == "x-ipe-task-category":
        assert "task-category skills" in template
        assert "x-ipe+{category}+{name}" in template
    if kind in ("x-ipe-tool", "x-ipe-knowledge"):
        assert "## Operations" in template
        assert "<operation" in template
    else:
        assert "## Execution Procedure" in template


def test_root_review_is_conditional_not_artifact_type_gate():
    entry = read("SKILL.md")
    procedure = ET.fromstring(re.search(r"```xml\n(<procedure.*?</procedure>)", entry, re.S)[1])
    scope = procedure.find("step_1/action").text
    verify = procedure.find("step_3/action").text
    for trigger in ("security/trust/permission", "destructive", "explicit user review",
                    "ambiguity/observed failures"):
        assert trigger in scope
    assert "artifact type alone is not a trigger" in scope
    assert "ordinary workflow, executable, and public-contract edits" in scope
    assert "same-loop deterministic checks and self-review by default" in scope
    assert "only for a documented Step 1 trigger" in verify
    assert "unavailable required review blocks promotion, not drafting" in verify


@pytest.mark.parametrize(
    ("scenario", "fragments"),
    [
        ("sequential_draft", ("one model/context open-ended loop", "sequential planning")),
        ("tool_invocation", ("same loop does not spawn an agent", "selected subtype templates")),
        ("context_degradation", ("Measurable context degradation", "repeated lost constraints")),
        ("independent_parallel_work", ("Substantial independent parallel work", "no shared writes")),
        ("isolation", ("Conflicting instructions", "genuine permission", "does not enforce permissions")),
        ("ordinary_contract_edit", ("Artifact type alone never requires", "same-loop self-review")),
        ("risky_or_requested_review", ("security/trust/permission", "destructive change", "explicit user review")),
        ("unresolved_failures", ("ambiguity/observed", "promotion blocker honestly")),
        ("approvals_and_publication", ("all three interaction modes", "concurrency checks", "byte parity")),
        ("honest_evaluation", ("about 10 golden outcome scenarios", "transitions", "unmeasured token/latency")),
    ],
)
def test_golden_authoring_contract_scenarios(scenario, fragments):
    """Ten representative policy checks; none execute or grade an LLM."""
    policy = " ".join(read("references/single-loop-authoring.md").split())
    for fragment in fragments:
        assert fragment in policy, scenario


def test_no_hidden_scheduling_or_numeric_review_gates():
    paths = [CANDIDATE / "SKILL.md"]
    paths += list((CANDIDATE / "templates").glob("*.md"))
    paths += list((CANDIDATE / "references").glob("*.md"))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for forbidden in (
            "schedule_dod_checks_with_sub_agent",
            "<sub-agent-planning>",
            "judge_agent:",
            "sub_agent_dag:",
            "must_pass_rate:",
            "should_pass_rate:",
            "Best-Model Requirement",
        ):
            assert forbidden not in text, (path.name, forbidden)
        assert not re.search(r"coverage\s*>=\s*\d+|80% must pass", text), path


def test_retained_interaction_task_and_goal_contracts():
    entry = read("SKILL.md")
    task = read("templates/x-ipe-task-based.md")
    consumer = read("references/consumer-integration.md")
    for mode in MODES:
        assert mode in entry and mode in task and mode in consumer
    for field in ("category:", "next_task_based_skill:", "process_preference:",
                  "interaction_mode:", "task_output_links:"):
        assert field in entry and field in task
    for contract in ("Given/When/Then", "not measured", "all-required", "selected bounded alternatives"):
        assert contract in " ".join(task.split())
    assert "Explicit domain human approval binds in every mode" in consumer
    assert "do not create a duplicate" in entry


def test_safe_publication_and_owned_lesson_evidence_remain():
    entry = read("SKILL.md")
    publication = read("references/validation-publication.md")
    consumer = read("references/consumer-integration.md")
    for safeguard in (
        "1,000 lines", "candidate/", "baseline", "managed", "fingerprints",
        "reviewed deletion", "--recover", "byte parity", "candidate_ready",
    ):
        assert safeguard in entry
    for safeguard in (
        "link/escaping", "1000/1001", "Dirty/unmanaged", "rechecks", "reviewed deletion",
        "Unexpected concurrent", "a passing receipt",
    ):
        assert safeguard.lower() in publication.lower()
    for contract in (
        "expected_revision", "primary_skill", 'status": "planned"',
        "actual role", "not compatible receipts", "reading/drafting never applies a lesson",
    ):
        assert contract in consumer.replace("**", "")


def test_validator_and_publisher_sources_unchanged():
    for script in ("validate_skill.py", "publish_skill.py"):
        assert (CANDIDATE / "scripts" / script).read_bytes() == (
            SKILLS / NAME / "scripts" / script
        ).read_bytes()


def test_complete_candidate_preserves_all_existing_resources():
    source = SKILLS / NAME
    before = {path.relative_to(source) for path in source.rglob("*") if path.is_file()}
    after = {path.relative_to(CANDIDATE) for path in CANDIDATE.rglob("*") if path.is_file()}
    assert before <= after
    assert after - before <= {
        Path("references/single-loop-authoring.md"),
        Path("metadata/review-findings.md"),
        Path("metadata/test-cases.yaml"),
    }


@pytest.mark.parametrize("filename", sorted(set(TEMPLATES.values())))
def test_subtype_output_contracts_and_section_order_are_retained(filename):
    template = read(f"templates/{filename}")
    baseline = (SKILLS / NAME / "templates" / filename).read_text(encoding="utf-8")
    assert re.findall(r"^## .+$", template, re.M) == re.findall(r"^## .+$", baseline, re.M)
    def output(text):
        return text.split("## Output Result", 1)[1].split("## Definition of Done", 1)[0]

    assert output(template) == output(baseline)


def test_metadata_no_longer_prescribes_judges_or_scores():
    for name in ("meta", "task-based"):
        text = read(f"templates/skill-meta-x-ipe-{name}.md")
        assert "independent_review:" in text
        assert "otherwise same-loop self-review" in text
        assert "no aggregate score gate" in text
    assert "execution: single_loop" in read("templates/skill-meta-x-ipe-meta.md")


def test_real_candidate_passes_unchanged_deterministic_validator():
    """Validate a disposable project-local copy, never the production directory."""
    validator = load_validator()
    workspace = ROOT / ".working" / f"task-6750-authoring-{uuid4().hex}"
    copied = workspace / CANDIDATE.relative_to(ROOT)
    try:
        # Reuse the exact source-bound interpreter-cache fixture contract.
        # Unknown files are still copied and inspected by the real validator.
        copy_resources(CANDIDATE, copied)
        for path in CANDIDATE.rglob("*.md"):
            for link in validator.markdown_targets(path.read_text(encoding="utf-8")):
                parsed = urlsplit(link)
                resource = unquote(parsed.path)
                if parsed.scheme or parsed.netloc or not resource or "{" in resource:
                    continue
                if resource.startswith("/") or ".." in Path(resource).parts:
                    continue
                own = f".github/skills/{NAME}"
                if resource == own or resource.startswith(own + "/"):
                    continue
                if resource.startswith(".github/skills/"):
                    source = SKILLS / resource.removeprefix(".github/skills/")
                else:
                    source = ROOT / resource
                target = workspace / resource
                if source.exists() and not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if source.is_dir():
                        copy_resources(source, target)
                    else:
                        shutil.copy2(source, target, follow_symlinks=False)
        receipt = validator.validate(workspace, copied, NAME, "x-ipe-meta")
        assert receipt["ok"], receipt["errors"]
        assert receipt["body_lines"] <= 1000
        assert "references/single-loop-authoring.md" in receipt["files"]
        assert not any(path.startswith("metadata/") for path in receipt["files"])
        entry = read("SKILL.md")
        output = yaml.safe_load(
            re.search(r"## Output Result\s+```yaml\n(.*?)```", entry, re.S)[1]
        )["task_completion_output"]
        assert output["publication_state"] == "candidate_ready | published | blocked | recovery_required"
    finally:
        if workspace.exists():
            shutil.rmtree(workspace)
