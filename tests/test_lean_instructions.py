"""Instruction policy and actual installation behavior, not model-performance claims."""
import importlib
from pathlib import Path

import pytest
from click.testing import CliRunner

from x_ipe.core.scaffold import ScaffoldManager
from x_ipe.services.cli_adapter_service import CLIAdapterService
from x_ipe.services.skill_translator import SkillTranslator


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "src/x_ipe/resources"


@pytest.mark.parametrize("language", ["en", "zh"])
@pytest.mark.parametrize("intercept", [False, True])
def test_variants_share_proportional_execution_and_preserve_authority(language, intercept):
    suffix = "" if intercept else "-no-dao"
    text = (RESOURCES / f"copilot-instructions-{language}{suffix}.md").read_text()
    assert "references/agent-loop.md" in text
    assert "task_ensure.py" in text and "goal-contract.md" in text
    assert all(mode in text for mode in (
        "interact-with-human", "dao-represent-human-to-interact",
        "dao-represent-human-to-interact-for-questions-in-skill",
    ))
    if language == "en":
        for phrase in ("one shared context", "does not spawn a subagent",
                       "one impact-based verification plan", "never weaken assertions",
                       "explicit separate authority", "human completion/route confirmation"):
            assert phrase in text
        assert ("EVERY user message MUST be processed through" in text) is intercept
        assert "most capable available model" not in text
    else:
        for phrase in ("同一上下文", "不是启动子代理", "一个影响范围验证计划",
                       "不削弱断言", "人类确认", "明确授权"):
            assert phrase in text
        assert ("每条用户消息必须先经过" in text) is intercept
        assert "最强可用模型" not in text
    assert "regardless of the skill's default" not in text
    assert len(text.splitlines()) <= 160


def test_repository_root_and_english_installation_copies_agree():
    canonical = (ROOT / ".github/copilot-instructions.md").read_bytes()
    for path in (RESOURCES / "copilot-instructions-en-no-dao.md",
                 RESOURCES / "templates/instructions-template-no-dao.md"):
        assert path.read_bytes() == canonical
    for name in ("AGENTS.md", "Agents.md", "CLAUDE.md"):
        path = ROOT / name
        if path.exists():
            assert path.read_bytes() == canonical
    assert (RESOURCES / "templates/instructions-template.md").read_bytes() == (
        RESOURCES / "copilot-instructions-en.md").read_bytes()


@pytest.mark.parametrize("cli_name", ["copilot", "opencode", "claude-code", "codex"])
@pytest.mark.parametrize("language", ["en", "zh"])
@pytest.mark.parametrize("intercept", [False, True])
def test_scaffold_installs_exact_policy_for_every_adapter(tmp_path, cli_name, language, intercept):
    adapter = CLIAdapterService().get_adapter(cli_name)
    assert adapter
    scaffold = ScaffoldManager(tmp_path)
    scaffold.copy_copilot_instructions(cli_name, language, intercept)
    suffix = "" if intercept else "-no-dao"
    expected = (RESOURCES / f"copilot-instructions-{language}{suffix}.md").read_bytes()
    target = tmp_path / adapter.instructions_file
    assert target.read_bytes() == expected
    preserved = b"# Local instructions\nDo not remove this.\n"
    target.write_bytes(preserved)
    dry = ScaffoldManager(tmp_path, dry_run=True, force=True)
    dry.copy_copilot_instructions(cli_name, language, intercept)
    assert target.read_bytes() == preserved
    upgrade = ScaffoldManager(tmp_path, force=True)
    upgrade.copy_copilot_instructions(cli_name, language, intercept)
    assert target.read_bytes() == expected
    unchanged = ScaffoldManager(tmp_path)
    unchanged.copy_copilot_instructions(cli_name, language, intercept)
    assert target.read_bytes() == expected
    assert target in unchanged.skipped


@pytest.mark.parametrize("language", ["en", "zh"])
def test_copilot_merge_preserves_user_text_and_does_not_append_twice(tmp_path, language):
    target = tmp_path / ".github/copilot-instructions.md"
    target.parent.mkdir()
    original = "# Local team rules\nKeep public interfaces stable.\n"
    target.write_text(original)
    ScaffoldManager(tmp_path).copy_copilot_instructions(language=language)
    first = target.read_bytes()
    assert first.startswith(original.rstrip().encode())
    ScaffoldManager(tmp_path).copy_copilot_instructions(language=language)
    assert target.read_bytes() == first


@pytest.mark.parametrize("cli_name", ["opencode", "claude-code", "codex"])
def test_non_copilot_init_preserves_existing_instructions_without_force(tmp_path, cli_name):
    adapter = CLIAdapterService().get_adapter(cli_name)
    target = tmp_path / adapter.instructions_file
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("User-owned content")
    ScaffoldManager(tmp_path).copy_copilot_instructions(cli_name, "en", False)
    assert target.read_text() == "User-owned content"


def test_translator_custom_template_still_wins(tmp_path):
    adapter = CLIAdapterService().get_adapter("codex")
    custom = tmp_path / "custom.md"
    custom.write_text("Explicit custom template")
    target = SkillTranslator().generate_instructions(adapter, tmp_path, custom, language="zh")
    assert target.read_text() == "Explicit custom template"


def test_unknown_translation_language_does_not_write(tmp_path):
    adapter = CLIAdapterService().get_adapter("codex")
    with pytest.raises(ValueError, match="Unsupported instruction language"):
        SkillTranslator().generate_instructions(adapter, tmp_path, language="fr")
    assert not (tmp_path / adapter.instructions_file).exists()


@pytest.mark.parametrize("cli_name", ["copilot", "opencode", "claude-code", "codex"])
@pytest.mark.parametrize("language", ["en", "zh"])
def test_actual_init_installs_selected_policy(tmp_path, monkeypatch, cli_name, language):
    main = importlib.import_module("x_ipe.cli.main")
    monkeypatch.setattr(main, "_resolve_cli_selection", lambda root, selected: selected)
    result = CliRunner().invoke(main.cli, [
        "--project", str(tmp_path), "init", "--cli", cli_name,
        "--lang", language, "--no-skills", "--no-mcp",
    ])
    assert result.exit_code == 0, result.output
    adapter = CLIAdapterService().get_adapter(cli_name)
    assert (tmp_path / adapter.instructions_file).read_bytes() == (
        RESOURCES / f"copilot-instructions-{language}-no-dao.md").read_bytes()


@pytest.mark.parametrize("cli_name", ["opencode", "claude-code", "codex"])
def test_language_switch_updates_active_adapter_policy(tmp_path, cli_name):
    import yaml
    main = importlib.import_module("x_ipe.cli.main")
    config = tmp_path / ".x-ipe.yaml"
    config.write_text(yaml.safe_dump({"cli": cli_name, "language": "en"}))
    ScaffoldManager(tmp_path).copy_copilot_instructions(cli_name)
    main._handle_language_switch(tmp_path, "zh")
    adapter = CLIAdapterService().get_adapter(cli_name)
    assert (tmp_path / adapter.instructions_file).read_bytes() == (
        RESOURCES / "copilot-instructions-zh-no-dao.md").read_bytes()
    assert yaml.safe_load(config.read_text())["language"] == "zh"


@pytest.mark.parametrize("target", ["sdist", "wheel"])
def test_package_contains_exact_instruction_variants(target):
    from tests.test_release_packaging import manifest
    files = manifest(ROOT, target)
    prefix = "src/x_ipe/resources" if target == "sdist" else "x_ipe/resources"
    for language in ("en", "zh"):
        for suffix in ("", "-no-dao"):
            name = f"copilot-instructions-{language}{suffix}.md"
            assert files[f"{prefix}/{name}"].read_bytes() == (RESOURCES / name).read_bytes()
    for name in ("instructions-template.md", "instructions-template-no-dao.md"):
        assert files[f"{prefix}/templates/{name}"].read_bytes() == (
            RESOURCES / "templates" / name).read_bytes()
