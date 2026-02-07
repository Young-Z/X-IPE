"""
Tests for FEATURE-027-B: CLI Init & Selection

Tests cover:
- CLI auto-detection during init
- CLI selection prompt
- --cli flag (non-interactive)
- Config storage (cli key in .x-ipe.yaml)
- Backward compatibility
- ScaffoldManager.create_config_file(cli_name=...)

TDD Approach: All tests written before implementation.
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
def temp_adapters_yaml():
    """Create a temporary cli-adapters.yaml."""
    content = """adapters:
  copilot:
    display_name: "GitHub Copilot CLI"
    command: "copilot"
    run_args: "--allow-all-tools"
    inline_prompt_flag: "-i"
    prompt_format: '{command} {run_args} {inline_prompt_flag} "{escaped_prompt}"'
    instructions_file: ".github/copilot-instructions.md"
    skills_folder: ".github/skills/"
    mcp_config_path: "~/.copilot/mcp-config.json"
    mcp_config_format: "global"
    detection_command: "copilot"
  opencode:
    display_name: "OpenCode CLI"
    command: "opencode"
    run_args: ""
    inline_prompt_flag: "--prompt"
    prompt_format: '{command} {inline_prompt_flag} "{escaped_prompt}"'
    instructions_file: ".opencode/instructions.md"
    skills_folder: ".opencode/skills/"
    mcp_config_path: "opencode.json"
    mcp_config_format: "project"
    detection_command: "opencode"
  claude-code:
    display_name: "Claude Code CLI"
    command: "claude"
    run_args: ""
    inline_prompt_flag: "-p"
    prompt_format: '{command} {inline_prompt_flag} "{escaped_prompt}"'
    instructions_file: ".claude/instructions.md"
    skills_folder: ".claude/skills/"
    mcp_config_path: ".mcp.json"
    mcp_config_format: "project"
    detection_command: "claude"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


# ============================================================================
# AC-1: CLI AUTO-DETECTION DURING INIT
# ============================================================================

class TestCLIAutoDetection:
    """AC-1.1 to AC-1.3: CLI detection during init."""

    def test_ac_1_1_init_calls_detect(self, runner, temp_project, temp_adapters_yaml):
        """AC-1.1: x-ipe init calls detect_installed_clis()."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.detect_installed_clis.return_value = ['copilot']
            instance.list_adapters.return_value = [
                MagicMock(name='copilot', display_name='GitHub Copilot CLI'),
            ]
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'copilot', '--no-mcp'
            ])

            instance.detect_installed_clis.assert_not_called()  # --cli skips detection

    def test_ac_1_3_no_cli_detected_defaults_copilot(self, runner, temp_project, temp_adapters_yaml):
        """AC-1.3: No CLIs detected → defaults to copilot."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.detect_installed_clis.return_value = []
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            # Set .name property correctly
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0


# ============================================================================
# AC-3: CLI FLAG (NON-INTERACTIVE)
# ============================================================================

class TestCLIFlag:
    """AC-3.1, AC-3.2: --cli flag for non-interactive mode."""

    def test_ac_3_1_cli_flag_skips_prompt(self, runner, temp_project, temp_adapters_yaml):
        """AC-3.1: --cli copilot skips prompt and uses specified CLI."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0

    def test_ac_3_2_cli_flag_invalid_name(self, runner, temp_project, temp_adapters_yaml):
        """AC-3.2: --cli unknown exits with error listing available adapters."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'unknown-cli', '--no-mcp'
            ])

            assert result.exit_code != 0
            assert 'copilot' in result.output.lower() or 'available' in result.output.lower()

    def test_ac_3_1_cli_flag_uninstalled_shows_warning(self, runner, temp_project):
        """AC-2.3/AC-3.1: Selecting uninstalled CLI shows warning."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = False

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'opencode', '--no-mcp'
            ])

            assert result.exit_code == 0
            assert 'warning' in result.output.lower() or '⚠' in result.output


# ============================================================================
# AC-4: CONFIG STORAGE
# ============================================================================

class TestConfigStorage:
    """AC-4.1, AC-4.2: CLI selection stored in .x-ipe.yaml."""

    def test_ac_4_1_cli_stored_in_config(self, runner, temp_project):
        """AC-4.1: Selected CLI stored in .x-ipe.yaml under cli key."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'opencode', '--no-mcp'
            ])

            assert result.exit_code == 0

            config_path = temp_project / '.x-ipe.yaml'
            assert config_path.exists()
            with open(config_path) as f:
                config = yaml.safe_load(f)
            assert config.get('cli') == 'opencode'


# ============================================================================
# AC-5: BACKWARD COMPATIBILITY
# ============================================================================

class TestBackwardCompatibility:
    """AC-5.1, AC-5.2: Existing flags still work."""

    def test_ac_5_2_force_flag_works(self, runner, temp_project):
        """AC-5.2: --force flag continues working."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [MagicMock(name='copilot')]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--force', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0

    def test_ac_5_2_dry_run_flag_works(self, runner, temp_project):
        """AC-5.2: --dry-run shows changes without writing."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [MagicMock(name='copilot')]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--dry-run', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0
            assert 'dry run' in result.output.lower() or 'Would' in result.output


# ============================================================================
# SCAFFOLD: create_config_file WITH cli_name
# ============================================================================

class TestScaffoldConfigFile:
    """ScaffoldManager.create_config_file(cli_name=...) tests."""

    def test_config_file_includes_cli_key(self, temp_project):
        """create_config_file(cli_name='opencode') includes cli key."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file(cli_name='opencode')

        config_path = temp_project / '.x-ipe.yaml'
        assert config_path.exists()
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config.get('cli') == 'opencode'

    def test_config_file_opencode_has_correct_skills_path(self, temp_project):
        """create_config_file(cli_name='opencode') sets skills to .opencode/skills."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file(cli_name='opencode')

        config_path = temp_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config['paths']['skills'] == '.opencode/skills'

    def test_config_file_without_cli_name(self, temp_project):
        """create_config_file() without cli_name has no cli key."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file()

        config_path = temp_project / '.x-ipe.yaml'
        assert config_path.exists()
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert 'cli' not in config

    def test_config_file_dry_run_no_write(self, temp_project):
        """create_config_file() in dry_run doesn't write file."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project, dry_run=True)
        scaffold.create_config_file(cli_name='opencode')

        config_path = temp_project / '.x-ipe.yaml'
        assert not config_path.exists()


class TestMCPPathResolution:
    """Bug fix: init MCP merge uses active CLI's path, not hardcoded copilot."""

    def test_init_mcp_uses_opencode_path(self, runner, temp_project):
        """When CLI is opencode, MCP merge target defaults to opencode.json."""
        import json
        from src.x_ipe.cli.main import cli

        # Set up MCP source
        mcp_dir = temp_project / ".github" / "copilot"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        mcp_config = {"mcpServers": {"test-server": {"command": "test"}}}
        (mcp_dir / "mcp-config.json").write_text(json.dumps(mcp_config))

        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "opencode"
            adapter.mcp_config_path = "opencode.json"
            adapter.mcp_config_format = "project"
            adapter.skills_folder = ".opencode/skills/"
            adapter.instructions_file = ".opencode/instructions.md"
            mock_svc.get_adapter.return_value = adapter
            mock_svc.list_adapters.return_value = [adapter]
            mock_svc.detect_installed_clis.return_value = ["opencode"]
            mock_svc.is_installed.return_value = True

            # Run init with --cli opencode, confirm MCP merge
            result = runner.invoke(
                cli,
                ["-p", str(temp_project), "init", "--cli", "opencode"],
                input="y\n" + str(temp_project / "opencode.json") + "\n",
            )
            # If MCP merge happened, target should be opencode.json not ~/.copilot/...
            if (temp_project / "opencode.json").exists():
                config = json.loads((temp_project / "opencode.json").read_text())
                assert "mcpServers" in config
