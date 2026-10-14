"""Review regressions; temporary helper execution is not stakeholder evidence."""
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "x-ipe-docs/skill-meta"
WORKFLOW = META / "x-ipe-workflow-task-execution/candidate"
CREATOR = META / "x-ipe-meta-skill-creator/candidate"
RESOURCES = ROOT / "src/x_ipe/resources"
INSTRUCTIONS = [ROOT / ".github/copilot-instructions.md", *[
    RESOURCES / name for name in (
        "copilot-instructions-en.md", "copilot-instructions-en-no-dao.md",
        "copilot-instructions-zh.md", "copilot-instructions-zh-no-dao.md",
        "templates/instructions-template.md", "templates/instructions-template-no-dao.md")]]


def test_hybrid_policy_follows_current_spec_ui_and_transport_not_review_claim():
    spec = (ROOT / "x-ipe-docs/requirements/EPIC-044/FEATURE-044-E/specification.md").read_text()
    ui = (ROOT / "src/x_ipe/static/js/features/workflow.js").read_text()
    transport = (ROOT / "tests/frontend-js/action-execution-modal-cr001.test.js").read_text()
    assert "DAO represents human for inner-skill questions only" in spec
    assert "DAO Inner-Skill Only" in ui and "DAO inner-skill only" in transport
    common = (WORKFLOW / "references/lifecycle.md").read_text()
    row = next(s for s in common.splitlines() if s.startswith(
        "| dao-represent-human-to-interact-for-questions-in-skill |"))
    assert "DAO bounded answer/guidance" in row
    assert "Human review and route confirmation" in row
    assert "requested policy supersedes" not in common
    assert "not authorized by the current user" in " ".join(common.split())
    entry = (WORKFLOW / "SKILL.md").read_text()
    assert "full DAO and hybrid use the representative" in entry
    assert "hybrid uses DAO within skill, then waits for human" in entry


def test_task_template_routes_only_actual_questions_for_both_dao_modes():
    template = (CREATOR / "templates/x-ipe-task-based.md").read_text()
    action = template.split('<phase_2 name=', 1)[1].split('</phase_2>', 1)[0]
    assert '"dao-represent-human-to-interact-for-questions-in-skill"' in action
    assert "No actual question" in action
    assert "human completion/route confirmation" in template
    assert 'type: "routing"' not in template and "<phase_6" not in template


@pytest.mark.parametrize("path", INSTRUCTIONS, ids=lambda p: p.name)
def test_instruction_single_owner_modes_goals_and_selective_learning(path):
    text = path.read_text()
    for token in ("x-ipe-workflow-task-execution", "task_ensure.py", "goal-contract.md",
                  "message_context", "interact-with-human", "dao-represent-human-to-interact",
                  "dao-represent-human-to-interact-for-questions-in-skill"):
        assert token in text
    if "使用指南" in text:
        for token in ("DAO 处理技能内部问题", "人类确认完成及后续路由", "未测量",
                      "阅读不等于应用", "选择性准入", "用户明确授权"):
            assert token in text
    else:
        for token in ("DAO handles within-skill questions", "human completion/route confirmation",
                      "not measured", "reading is not application", "selective admission",
                      "explicit user authority"):
            assert token in text
    for forbidden in ("Phase 0:", "Phase 0：", "in its Phase 0", "在其 Phase 0",
                      "regardless of the skill's default", "增加完成计数"):
        assert forbidden not in text
    assert not re.search(r"(Create task|Created a task|创建任务).*\n", text)


def test_canonical_english_no_dao_and_cli_core_byte_parity():
    canonical = INSTRUCTIONS[0].read_bytes()
    assert (RESOURCES / "copilot-instructions-en-no-dao.md").read_bytes() == canonical
    assert (RESOURCES / "templates/instructions-template-no-dao.md").read_bytes() == canonical
    en = (RESOURCES / "copilot-instructions-en.md").read_bytes()
    assert (RESOURCES / "templates/instructions-template.md").read_bytes() == en
    def without_gateway(text, heading, next_heading):
        start = text.index(heading)
        end = text.index(next_heading, start)
        return text[:start] + text[end:]
    assert without_gateway(en.decode(), "## DAO-First", "## Before You Start") == canonical.decode()
    zh = (RESOURCES / "copilot-instructions-zh.md").read_text()
    assert without_gateway(zh, "## DAO优先", "## 开始之前") == (
        RESOURCES / "copilot-instructions-zh-no-dao.md").read_text()


def test_representative_only_existing_inputs_no_goal_transport_contract():
    candidate = META / "x-ipe-assistant-user-representative-Engineer/candidate"
    entry = (candidate / "SKILL.md").read_text()
    boundary = (candidate / "references/decision-boundaries.md").read_text()
    assert "message_context" in boundary and "operation_output" in boundary
    assert "No new required input" in boundary
    assert "approval as guidance only" in boundary and "not measured" in boundary
    assert "fallback_required = true ONLY if human_shadow AND confidence < threshold" in entry
    assert "MUST NOT expand downstream task scope" in entry


@pytest.mark.parametrize("language", ["en", "zh"])
@pytest.mark.parametrize("intercept", [False, True])
def test_actual_scaffold_new_and_forced_upgrade_exact_variant(tmp_path, language, intercept):
    from x_ipe.core.scaffold import ScaffoldManager
    suffix = "" if intercept else "-no-dao"
    source = RESOURCES / f"copilot-instructions-{language}{suffix}.md"
    scaffold = ScaffoldManager(tmp_path)
    scaffold.copy_copilot_instructions(language=language, dao_intercept=intercept)
    target = tmp_path / ".github/copilot-instructions.md"
    assert target.read_bytes() == source.read_bytes()
    target.write_text("Local prior instructions\n")
    upgrade = ScaffoldManager(tmp_path, force=True)
    upgrade.copy_copilot_instructions(language=language, dao_intercept=intercept)
    assert target.read_bytes() == source.read_bytes()


@pytest.mark.parametrize("intercept", [False, True])
def test_actual_cli_instruction_translation_exact_template(tmp_path, intercept):
    from types import SimpleNamespace
    from x_ipe.services.skill_translator import SkillTranslator
    adapter = SimpleNamespace(name="codex", instructions_file="AGENTS.md")
    target = SkillTranslator().generate_instructions(adapter, tmp_path, dao_intercept=intercept)
    name = "instructions-template.md" if intercept else "instructions-template-no-dao.md"
    assert target.read_bytes() == (RESOURCES / "templates" / name).read_bytes()