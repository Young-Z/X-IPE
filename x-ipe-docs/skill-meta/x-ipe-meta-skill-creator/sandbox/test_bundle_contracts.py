"""Real creator bundle contracts; publication is dry-run only in temporary roots."""
import importlib.util
from pathlib import Path
import re
import sys

import pytest
import yaml

from tests.test_skill_creator_foundation import creator_dependencies, snapshot

META = Path(__file__).resolve().parents[1]
CANDIDATE = META / "candidate"
MAPPINGS = {
    "x-ipe-task-based": ("x-ipe-task-based", "x-ipe-task-based", "x-ipe-task-based-check"),
    "x-ipe-tool": ("x-ipe-tool", "x-ipe-tool", "x-ipe-tool-check"),
    "x-ipe-workflow-orchestration": ("x-ipe-workflow-orchestration", "x-ipe-task-based", "x-ipe-workflow-check"),
    "x-ipe-task-category": ("x-ipe-workflow-orchestration", "x-ipe-task-category", "x-ipe+all+check"),
    "x-ipe-meta": ("x-ipe-meta", "x-ipe-meta", "x-ipe-meta-check"),
    "x-ipe-knowledge": ("x-ipe-knowledge", "x-ipe-knowledge", "x-ipe-knowledge-extractor-check"),
    "x-ipe-assistant": ("x-ipe-assistant", "x-ipe-assistant", "x-ipe-assistant-check"),
    "x-ipe-dao": ("x-ipe-dao", "x-ipe-dao", "x-ipe-dao-check"),
}


def read(path):
    return (CANDIDATE / path).read_text()


def scaffold(kind):
    text = read(f"templates/{MAPPINGS[kind][0]}.md").split("```markdown\n", 1)[1]
    if "\n```\n\n---\n\n## Template Usage Notes" in text:
        return text.split("\n```\n\n---\n\n## Template Usage Notes", 1)[0]
    return text.rsplit("\n```", 1)[0]


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    modules = []
    for name in ("validate_skill", "publish_skill"):
        spec = importlib.util.spec_from_file_location(name, CANDIDATE / "scripts" / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


@pytest.mark.parametrize("kind", MAPPINGS)
def test_real_template_order_and_validator(tmp_path, api, kind):
    text = scaffold(kind)
    heads = re.findall(r"^## (.+)$", text, re.M)
    action = "Operations" if kind in ("x-ipe-tool", "x-ipe-knowledge") else "Execution Procedure"
    expected = ["Purpose", "Important Notes", "Input Parameters", "Definition of Ready", action, "Output Result", "Definition of Done"]
    if kind == "x-ipe-meta":
        expected.insert(1, "About")
    if kind in ("x-ipe-workflow-orchestration", "x-ipe-task-category"):
        expected += ["Skill Registry", "Error Handling", "Examples"]
    positions = [heads.index(head) for head in expected]
    assert positions == sorted(positions)
    order_yaml = read("references/2. reference-section-order.md").split("```yaml", 1)[1].split("```", 1)[0]
    declared = yaml.safe_load(order_yaml)[kind]["section_order"]
    normalized = [value.split(" (", 1)[0].replace("Execution Flow Summary", "Execution Flow")
                  for value in declared.values()]
    assert heads == normalized, (heads, normalized)
    _, _, name = MAPPINGS[kind]
    root = tmp_path.resolve()
    local = root / "x-ipe-docs/skill-meta" / name / "candidate"
    (local / "references").mkdir(parents=True)
    body = text.split("---", 2)[2]
    (local / "SKILL.md").write_text("---\n" + yaml.safe_dump({"name": name, "description": "Use when checking actual template contracts."}) + "---" + body)
    (local / "references/examples.md").write_text("Example resource.\n")
    creator_dependencies(root)
    receipt = api[0].validate(root, local, name, kind)
    assert receipt["ok"], receipt["errors"]
    assert (CANDIDATE / f"templates/skill-meta-{MAPPINGS[kind][1]}.md").exists()


def test_category_metadata_and_reference_contract():
    text = read("templates/skill-meta-x-ipe-task-category.md")
    assert 'skill_name: "x-ipe+{category}+{name}"' in text
    assert "completion_inputs:" in text and "workflow_output:" in text
    assert "x-ipe-tool-task-board-manager" in text
    assert "board_path:" not in text and "operations:" not in text
    order = read("references/2. reference-section-order.md").split("x-ipe-task-category:", 1)[1].split("x-ipe-workflow-orchestration:", 1)[0]
    assert "Execution Procedure" in order and "Operations" not in order
    assert "x-ipe+{category}+{name}" in read("references/skill-general-guidelines-v2.md")
    board = (META.parents[2] / ".github/skills/x-ipe-tool-task-board-manager/SKILL.md").read_text()
    # Current contract describes actual JSON stores, not the old prose label.
    assert "x-ipe-docs/planning/tasks/" in board
    assert "tasks-index.json" in board
    assert "x-ipe-docs/planning/features/features.json" in board
    board_input = yaml.safe_load(board.split("## Input Parameters", 1)[1].split("```yaml", 1)[1].split("```", 1)[0])["input"]
    assert "feature_query" in board_input["operation"].split(" | ")
    assert "feature_query.py" in board
    assert (META.parents[2] / ".github/skills/x-ipe-tool-task-board-manager/scripts/feature_query.py").is_file()
    assert "feature-board.md" not in read("references/9. example-dor-dod.md")
    assert "do not create a duplicate" in scaffold("x-ipe-task-based")
    shared = read("templates/skill-meta-x-ipe-task-based.md")
    assert "x-ipe-workflow-orchestration" in shared and "workflow_output" in shared


def test_workflow_naming_and_registry_placement():
    text = read("templates/x-ipe-workflow-orchestration.md")
    assert text.index("## Definition of Done") < text.index("## Skill Registry")
    assert "x-ipe-workflow-{name}" in text.split("### Naming Convention", 1)[1]
    assert "x-ipe+{category}+{name}" in text


def test_routing_shape_matches_existing_caller():
    caller = (META.parents[2] / ".github/skills/x-ipe-workflow-task-execution/SKILL.md").read_text()
    # YAML nesting is authoritative; a dotted prose spelling is not the schema.
    caller_input = yaml.safe_load(caller.split("## Input Parameters", 1)[1].split("```yaml", 1)[1].split("```", 1)[0])["input"]
    modes = caller_input["execution"]["process_preference"]["interaction_mode"]
    assert modes.split(" | ") == ["interact-with-human", "dao-represent-human-to-interact", "dao-represent-human-to-interact-for-questions-in-skill"]
    assert "interaction_mode" not in caller_input["execution"]
    caller_output = yaml.safe_load(caller.split("## Output Result", 1)[1].split("```yaml", 1)[1].split("```", 1)[0])["output"]
    assert "interaction_mode" in caller_output["process_preference"]
    assert "interaction_mode" not in caller_output
    for text in (read("SKILL.md"), scaffold("x-ipe-task-based")):
        output = text.split("## Output Result", 1)[1].split("```yaml", 1)[1].split("```", 1)[0]
        # Instantiate only dynamic field names, not the fixed routing contract.
        output = re.sub(r"(?m)^(\s*)\{dynamic_attr_([12])\}:", r"\1dynamic_attr_\2:", output)
        fields = yaml.safe_load(output)["task_completion_output"]
        assert "interaction_mode" in fields["process_preference"]
        assert "interaction_mode" not in fields
        assert "category" in fields and "next_task_based_skill" in fields
    meta = read("templates/skill-meta-x-ipe-task-based.md")
    assert "name: process_preference.interaction_mode" in meta
    assert "${inputs.process_preference.interaction_mode}" in meta


def test_operation_and_assistant_domain_contracts_preserved():
    knowledge = scaffold("x-ipe-knowledge")
    assert "**Input:**" in knowledge and "**Output:**" in knowledge and "**Writes To:**" in knowledge
    assert "operation_output:" in knowledge and "writes_to:" in knowledge
    assert "operation_output:" in scaffold("x-ipe-tool")
    for kind in ("x-ipe-assistant", "x-ipe-dao"):
        text = scaffold(kind)
        for phase in ("礼", "格物", "致知", "录", "示"):
            assert phase in text
    for kind in ("x-ipe-tool", "x-ipe-knowledge"):
        assert "task_completion_output:" not in scaffold(kind)


def test_creator_guidance_is_current_and_helpers_are_creator_owned():
    text = read("SKILL.md")
    assert "TASK-6749" not in text and "OLD four-round" not in text
    assert ".github/skills/x-ipe-meta-skill-creator/scripts/validate_skill.py" in text
    assert ".github/skills/x-ipe-meta-skill-creator/scripts/publish_skill.py" in text
    assert "not the target skill's candidate/scripts" in text
    examples = read("references/examples.md")
    assert len(re.findall(r"^## Example \d", examples, re.M)) >= 3
    for unsafe in ("cp -r", "incorporated", "templates/tool-skill.md", "templates/workflow-skill.md", ".github/skills/pdf/"):
        assert unsafe not in examples
    types = read("references/skill-type-comparison.md")
    assert "skill owns its execution state and manages task board entries" not in types
    assert "redirects `x-ipe-dao`" not in types
    assert "x-ipe-dao.md" in types
    assert "not yet scenario-tested" not in read("references/validation-publication.md")


def test_review_metadata_is_not_publishable_and_no_general_ignores(tmp_path, api):
    root = tmp_path.resolve()
    name = "x-ipe-meta-skill-creator"
    local = root / "x-ipe-docs/skill-meta" / name / "candidate"
    # Copy the real physical bundle; verify review artifacts cannot enter stage/receipt.
    physical = api[0].tree_bytes(CANDIDATE, META.parents[2])
    for key, data in physical.items():
        path = local / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    creator_dependencies(root)
    receipt = api[0].validate(root, local, name, "x-ipe-meta")
    assert receipt["ok"], receipt["errors"]
    assert not any(key.startswith("metadata/") for key in receipt["files"])
    before = snapshot(root)
    dry = api[1].publish(root, local, name, "x-ipe-meta", {}, {}, receipt["candidate_hash"])
    assert not any(key.startswith("metadata/") for key in dry["files"])
    assert snapshot(root) == before  # Dependency docs exist; dry-run still writes nothing.
    applied = api[1].publish(root, local, name, "x-ipe-meta", {}, {}, receipt["candidate_hash"], apply=True)
    assert applied["state"] == "published" and applied["byte_parity"]
    target = root / ".github/skills" / name
    assert api[0].manifest(api[0].tree_bytes(target, root)) == receipt["files"]
    assert not (target / "metadata").exists()
    for key in (".hidden", "references/real.txt", "metadata/real-resource.txt"):
        path = local / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("A real resource must not be silently ignored.")
    result = api[0].validate(root, local, name, "x-ipe-meta")
    assert not result["ok"] and "metadata/real-resource.txt" in " ".join(result["errors"])
    assert ".hidden" in api[0].tree_bytes(local, root)


def test_exclusion_does_not_apply_to_other_skills(tmp_path, api):
    root = tmp_path.resolve()
    name = "x-ipe-tool-check"
    local = root / "x-ipe-docs/skill-meta" / name / "candidate"
    (local / "metadata").mkdir(parents=True)
    (local / "metadata/test-cases.yaml").write_text("Real tool resource, not creator review metadata.")
    assert "metadata/test-cases.yaml" in api[0].candidate_bytes(local, root, name)


def test_metadata_exclusion_never_hides_unsafe_nodes(tmp_path, api):
    root = tmp_path.resolve()
    name = "x-ipe-meta-skill-creator"
    local = root / "x-ipe-docs/skill-meta" / name / "candidate"
    (local / "metadata").mkdir(parents=True)
    outside = root / "review.txt"
    outside.write_text("Do not bypass safety checks.")
    (local / "metadata/review-findings.md").symlink_to(outside)
    with pytest.raises(ValueError, match="Symlink prohibited"):
        api[0].candidate_bytes(local, root, name)


def test_flattened_task_mode_does_not_satisfy_caller_contract(tmp_path, api):
    root = tmp_path.resolve()
    name = "x-ipe-task-based-check"
    local = root / "x-ipe-docs/skill-meta" / name / "candidate"
    (local / "references").mkdir(parents=True)
    body = scaffold("x-ipe-task-based").split("---", 2)[2]
    body = body.replace('    interaction_mode: "{from input process_preference.interaction_mode}"',
                        '  interaction_mode: "{flattened mode}"')
    (local / "SKILL.md").write_text("---\n" + yaml.safe_dump({"name": name, "description": "Use when checking nesting."}) + "---" + body)
    (local / "references/examples.md").write_text("Example.")
    receipt = api[0].validate(root, local, name, "x-ipe-task-based")
    assert not receipt["ok"]
    assert "Task-based output requires nested process_preference.interaction_mode" in receipt["errors"]