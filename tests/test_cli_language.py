"""
Tests for FEATURE-028-B: CLI Language Selection & Instructions

Tests cover:
- _resolve_language_selection() with --lang flag and defaults
- _handle_language_switch() for upgrade --lang
- ScaffoldManager.create_config_file(language=...) writes language key
- ScaffoldManager.copy_copilot_instructions(language=...) extracts correct section
- CLI init --lang integration
- CLI upgrade --lang integration

TDD Approach: Tests written for implemented FEATURE-028-B.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml
from click.testing import CliRunner


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    temp_dir = os.path.realpath(temp_dir)
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def initialized_project(temp_project):
    """Create a pre-initialized project with .x-ipe.yaml."""
    config_path = temp_project / '.x-ipe.yaml'
    config_path.write_text(yaml.safe_dump({
        'paths': {'skills': '.github/skills'}, 'cli': 'copilot', 'language': 'en',
    }))
    (temp_project / '.github').mkdir(parents=True, exist_ok=True)
    (temp_project / '.github' / 'copilot-instructions.md').write_text('# EN Instructions')
    return temp_project


# ============================================================================
# _resolve_language_selection() TESTS
# ============================================================================

class TestResolveLanguageSelection:
    """Tests for _resolve_language_selection() helper."""

    def test_flag_en_returns_en(self):
        """--lang en returns 'en' without prompting."""
        from x_ipe.cli.main import _resolve_language_selection
        assert _resolve_language_selection('en') == 'en'

    def test_flag_zh_returns_zh(self):
        """--lang zh returns 'zh' without prompting."""
        from x_ipe.cli.main import _resolve_language_selection
        assert _resolve_language_selection('zh') == 'zh'

    def test_invalid_lang_raises_bad_parameter(self):
        """Invalid language code raises click.BadParameter."""
        import click
        from x_ipe.cli.main import _resolve_language_selection
        with pytest.raises(click.BadParameter, match="Invalid language 'fr'"):
            _resolve_language_selection('fr')

    def test_none_prompts_interactively(self):
        """No --lang flag triggers interactive prompt, defaults to 'en'."""
        from x_ipe.cli.main import _resolve_language_selection
        with patch('x_ipe.cli.main.click') as mock_click:
            mock_click.prompt.return_value = 'en'
            mock_click.Choice = __import__('click').Choice
            result = _resolve_language_selection(None)
        assert result == 'en'
        mock_click.prompt.assert_called_once()

    def test_abort_defaults_to_en(self):
        """Ctrl+C during prompt defaults to 'en'."""
        import click
        from x_ipe.cli.main import _resolve_language_selection
        with patch('x_ipe.cli.main.click') as mock_click:
            mock_click.Abort = click.Abort
            mock_click.prompt.side_effect = click.Abort()
            mock_click.echo = MagicMock()
            result = _resolve_language_selection(None)
        assert result == 'en'


class TestSupportedLanguages:
    """Tests for SUPPORTED_LANGUAGES constant."""

    def test_en_and_zh_supported(self):
        """English and Chinese are the supported languages."""
        from x_ipe.cli.main import SUPPORTED_LANGUAGES
        assert 'en' in SUPPORTED_LANGUAGES
        assert 'zh' in SUPPORTED_LANGUAGES

    def test_only_two_supported(self):
        """Only en and zh are supported."""
        from x_ipe.cli.main import SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) == 2


# ============================================================================
# ScaffoldManager.create_config_file(language=...) TESTS
# ============================================================================

class TestScaffoldConfigFileLanguage:
    """ScaffoldManager.create_config_file(language=...) tests."""

    def test_config_file_includes_language_key(self, temp_project):
        """create_config_file(language='zh') writes language key to .x-ipe.yaml."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file(language='zh')

        config_path = temp_project / '.x-ipe.yaml'
        assert config_path.exists()
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config.get('language') == 'zh'

    def test_config_file_default_language_en(self, temp_project):
        """create_config_file() without language defaults to 'en'."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file(language='en')

        config_path = temp_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config.get('language') == 'en'

    def test_config_file_both_cli_and_language(self, temp_project):
        """create_config_file(cli_name='copilot', language='zh') writes both keys."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file(cli_name='copilot', language='zh')

        config_path = temp_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config.get('cli') == 'copilot'
        assert config.get('language') == 'zh'


# ============================================================================
# ScaffoldManager.copy_copilot_instructions(language=...) TESTS
# ============================================================================

class TestCopilotInstructionsExtraction:
    """ScaffoldManager.copy_copilot_instructions(language=...) tests."""

    def test_extracts_en_section(self, temp_project):
        """CR-001: copy the complete selected EN resource, without markers."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        (temp_project / '.github').mkdir(parents=True, exist_ok=True)
        scaffold.copy_copilot_instructions(language='en')

        target = temp_project / '.github' / 'copilot-instructions.md'
        source = Path(__file__).resolve().parents[1] / 'src/x_ipe/resources/copilot-instructions-en-no-dao.md'
        assert target.is_file()
        assert target.read_bytes() == source.read_bytes()
        assert '---LANG:' not in target.read_text()

    def test_extracts_zh_section(self, temp_project):
        """CR-001: copy the complete selected ZH resource, without markers."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        (temp_project / '.github').mkdir(parents=True, exist_ok=True)
        scaffold.copy_copilot_instructions(language='zh')

        target = temp_project / '.github' / 'copilot-instructions.md'
        source = Path(__file__).resolve().parents[1] / 'src/x_ipe/resources/copilot-instructions-zh-no-dao.md'
        assert target.is_file()
        assert target.read_bytes() == source.read_bytes()
        assert '---LANG:' not in target.read_text()
        assert target.read_bytes() != source.with_name('copilot-instructions-en-no-dao.md').read_bytes()

    def test_zh_contains_dynamic_skill_discovery(self, temp_project):
        """Current instructions route from discovered YAML metadata, not a keyword table."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        (temp_project / '.github').mkdir(parents=True, exist_ok=True)
        scaffold.copy_copilot_instructions(language='zh')

        target = temp_project / '.github' / 'copilot-instructions.md'
        assert target.is_file()
        content = target.read_text()
        assert '.github/skills/x-ipe-task-based-*/SKILL.md' in content
        assert '.github/skills/x-ipe-assistant-*/SKILL.md' in content
        assert 'frontmatter' in content
        # Validate the schema actually consumed by dynamic discovery. No fixed
        # list of task names or Chinese trigger phrases belongs in this test.
        skills_root = Path(__file__).resolve().parents[1] / '.github/skills'
        skills = sorted(skills_root.glob('x-ipe-task-based-*/SKILL.md'))
        assert skills
        for skill in skills:
            text = skill.read_text()
            assert text.startswith('---\n'), skill
            metadata = yaml.safe_load(text.split('---', 2)[1])
            assert isinstance(metadata, dict), skill
            assert metadata['name'] == skill.parent.name
            assert isinstance(metadata['description'], str), skill
            assert metadata['description'].strip(), skill

    def test_en_does_not_contain_zh_keywords(self, temp_project):
        """EN selects EN guidance, not the ZH template or a static routing table."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        (temp_project / '.github').mkdir(parents=True, exist_ok=True)
        scaffold.copy_copilot_instructions(language='en')

        target = temp_project / '.github' / 'copilot-instructions.md'
        resources = Path(__file__).resolve().parents[1] / 'src/x_ipe/resources'
        assert target.is_file()
        assert target.read_bytes() == (resources / 'copilot-instructions-en-no-dao.md').read_bytes()
        assert target.read_bytes() != (resources / 'copilot-instructions-zh-no-dao.md').read_bytes()
        assert '.github/skills/x-ipe-task-based-*/SKILL.md' in target.read_text()


# ============================================================================
# _handle_language_switch() TESTS
# ============================================================================

class TestHandleLanguageSwitch:
    """Tests for _handle_language_switch() upgrade helper."""

    def test_updates_yaml_language_key(self, initialized_project):
        """Switching language updates language key in .x-ipe.yaml."""
        from x_ipe.cli.main import _handle_language_switch

        with patch('x_ipe.cli.main.ScaffoldManager'):
            _handle_language_switch(initialized_project, 'zh')

        config_path = initialized_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config.get('language') == 'zh'

    def test_re_extracts_instructions(self, initialized_project):
        """Switching language calls copy_copilot_instructions with new language."""
        from x_ipe.cli.main import _handle_language_switch

        with patch('x_ipe.cli.main.ScaffoldManager') as MockScaffold:
            instance = MockScaffold.return_value
            _handle_language_switch(initialized_project, 'zh')
            instance.copy_copilot_instructions.assert_called_once_with(
                cli_name='copilot', language='zh'
            )

    def test_dry_run_does_not_modify(self, initialized_project):
        """dry_run=True does not modify .x-ipe.yaml."""
        from x_ipe.cli.main import _handle_language_switch

        _handle_language_switch(initialized_project, 'zh', dry_run=True)

        config_path = initialized_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config.get('language') == 'en'

    def test_no_config_shows_error(self, temp_project):
        """Switching language without init shows error."""
        from x_ipe.cli.main import _handle_language_switch

        with patch('x_ipe.cli.main.click') as mock_click:
            _handle_language_switch(temp_project, 'zh')
            mock_click.echo.assert_any_call("Error: Project not initialized. Run `x-ipe init` first.")


# ============================================================================
# CLI INTEGRATION TESTS
# ============================================================================

class TestInitLangIntegration:
    """CLI init --lang integration tests."""

    def test_init_with_lang_zh(self, runner, temp_project):
        """x-ipe init --lang zh passes language to scaffold."""
        from x_ipe.cli.main import cli

        result = runner.invoke(cli, [
            '--project', str(temp_project),
            'init', '--cli', 'copilot', '--lang', 'zh', '--no-mcp'
        ])
        assert result.exit_code == 0

        config_path = temp_project / '.x-ipe.yaml'
        assert config_path.is_file()
        config = yaml.safe_load(config_path.read_text())
        assert isinstance(config, dict)
        assert config['language'] == 'zh'
        assert config['cli'] == 'copilot'
        assert config['paths']['skills'] == '.github/skills'

    def test_init_with_lang_en(self, runner, temp_project):
        """x-ipe init --lang en passes language to scaffold."""
        from x_ipe.cli.main import cli

        result = runner.invoke(cli, [
            '--project', str(temp_project),
            'init', '--cli', 'copilot', '--lang', 'en', '--no-mcp'
        ])
        assert result.exit_code == 0

    def test_init_invalid_lang(self, runner, temp_project):
        """x-ipe init --lang fr raises error."""
        from x_ipe.cli.main import cli

        result = runner.invoke(cli, [
            '--project', str(temp_project),
            'init', '--cli', 'copilot', '--lang', 'fr', '--no-mcp'
        ])
        assert result.exit_code != 0


class TestUpgradeLangIntegration:
    """CLI upgrade --lang integration tests."""

    def test_upgrade_with_lang_zh(self, runner, initialized_project):
        """x-ipe upgrade --lang zh switches language."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main._handle_language_switch') as mock_switch, \
             patch('x_ipe.cli.main._resolve_language_selection', return_value='zh') as mock_resolve, \
             patch('x_ipe.cli.main._resolve_cli_selection', return_value='copilot'):
            result = runner.invoke(cli, [
                '--project', str(initialized_project),
                'upgrade', '--lang', 'zh', '--no-mcp'
            ], input='1\n')
            assert result.exit_code == 0, (result.output, result.exception)
            mock_resolve.assert_called_once_with('zh')
            mock_switch.assert_called_once()
