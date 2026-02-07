"""Tests for FEATURE-027-E: CLI Migration & Upgrade.

Tests the --cli flag on the upgrade command for CLI migration:
backup, config update, and MCP redeployment.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Create a project with .x-ipe.yaml and old CLI artifacts."""
    import yaml

    # .x-ipe.yaml with current CLI
    config = {"project_name": "test", "cli": "copilot"}
    (tmp_path / ".x-ipe.yaml").write_text(yaml.dump(config))

    # Old CLI skills folder
    skills = tmp_path / ".github" / "skills" / "test-skill"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text("# Test Skill")

    # Old CLI instructions
    (tmp_path / ".github").mkdir(exist_ok=True)
    (tmp_path / ".github" / "copilot-instructions.md").write_text("# Instructions")

    # MCP config source
    mcp_dir = tmp_path / ".github" / "copilot"
    mcp_dir.mkdir(parents=True, exist_ok=True)
    mcp_config = {"mcpServers": {"test-server": {"command": "test"}}}
    (mcp_dir / "mcp-config.json").write_text(json.dumps(mcp_config))

    return tmp_path


class TestCLIFlagValidation:
    """AC-1: --cli Flag on Upgrade Command."""

    def test_ac_1_1_accepts_valid_cli_name(self, runner, temp_project):
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "opencode"
            adapter.mcp_config_path = "opencode.json"
            adapter.mcp_config_format = "project"
            adapter.skills_folder = ".opencode/skills/"
            adapter.instructions_file = ".opencode/instructions.md"
            old_adapter = MagicMock()
            old_adapter.name = "copilot"
            old_adapter.skills_folder = ".github/skills/"
            old_adapter.instructions_file = ".github/copilot-instructions.md"
            old_adapter.mcp_config_path = "~/.copilot/mcp-config.json"
            old_adapter.mcp_config_format = "global"
            mock_svc.get_adapter.side_effect = lambda n: adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"])
            assert result.exit_code == 0
            assert "opencode" in result.output.lower() or "migrat" in result.output.lower()

    def test_ac_1_2_same_cli_skips_migration(self, runner, temp_project):
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "copilot"
            mock_svc.get_adapter.return_value = adapter
            mock_svc.list_adapters.return_value = [adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "copilot", "--no-mcp"])
            assert result.exit_code == 0
            assert "already using" in result.output.lower()

    def test_ac_1_3_unknown_cli_raises_error(self, runner, temp_project):
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "copilot"
            mock_svc.list_adapters.return_value = [adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "unknown-cli", "--no-mcp"])
            assert result.exit_code != 0


class TestBackup:
    """AC-2: Backup Old Artifacts."""

    def test_ac_2_1_backs_up_skills_folder(self, runner, temp_project):
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            old_adapter = MagicMock()
            old_adapter.name = "copilot"
            old_adapter.skills_folder = ".github/skills/"
            old_adapter.instructions_file = ".github/copilot-instructions.md"
            old_adapter.mcp_config_path = "~/.copilot/mcp-config.json"
            old_adapter.mcp_config_format = "global"
            new_adapter = MagicMock()
            new_adapter.name = "opencode"
            new_adapter.mcp_config_path = "opencode.json"
            new_adapter.mcp_config_format = "project"
            new_adapter.skills_folder = ".opencode/skills/"
            new_adapter.instructions_file = ".opencode/instructions.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"])
            assert result.exit_code == 0
            # Check backup exists
            backup_dir = temp_project / ".x-ipe" / "backup"
            assert backup_dir.exists()
            backup_dirs = list(backup_dir.iterdir())
            assert len(backup_dirs) == 1
            assert backup_dirs[0].name.startswith("copilot-")

    def test_ac_2_4_dry_run_no_backup(self, runner, temp_project):
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            old_adapter = MagicMock()
            old_adapter.name = "copilot"
            old_adapter.skills_folder = ".github/skills/"
            old_adapter.instructions_file = ".github/copilot-instructions.md"
            old_adapter.mcp_config_path = "~/.copilot/mcp-config.json"
            old_adapter.mcp_config_format = "global"
            new_adapter = MagicMock()
            new_adapter.name = "opencode"
            new_adapter.mcp_config_path = "opencode.json"
            new_adapter.mcp_config_format = "project"
            new_adapter.skills_folder = ".opencode/skills/"
            new_adapter.instructions_file = ".opencode/instructions.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--dry-run", "--no-mcp"])
            assert result.exit_code == 0
            backup_dir = temp_project / ".x-ipe" / "backup"
            assert not backup_dir.exists()


class TestConfigUpdate:
    """AC-3: Config Update."""

    def test_ac_3_1_updates_config_cli_key(self, runner, temp_project):
        import yaml
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            old_adapter = MagicMock()
            old_adapter.name = "copilot"
            old_adapter.skills_folder = ".github/skills/"
            old_adapter.instructions_file = ".github/copilot-instructions.md"
            old_adapter.mcp_config_path = "~/.copilot/mcp-config.json"
            old_adapter.mcp_config_format = "global"
            new_adapter = MagicMock()
            new_adapter.name = "opencode"
            new_adapter.mcp_config_path = "opencode.json"
            new_adapter.mcp_config_format = "project"
            new_adapter.skills_folder = ".opencode/skills/"
            new_adapter.instructions_file = ".opencode/instructions.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"])
            assert result.exit_code == 0
            config = yaml.safe_load((temp_project / ".x-ipe.yaml").read_text())
            assert config["cli"] == "opencode"

    def test_ac_3_2_dry_run_no_config_write(self, runner, temp_project):
        import yaml
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            old_adapter = MagicMock()
            old_adapter.name = "copilot"
            old_adapter.skills_folder = ".github/skills/"
            old_adapter.instructions_file = ".github/copilot-instructions.md"
            old_adapter.mcp_config_path = "~/.copilot/mcp-config.json"
            old_adapter.mcp_config_format = "global"
            new_adapter = MagicMock()
            new_adapter.name = "opencode"
            new_adapter.mcp_config_path = "opencode.json"
            new_adapter.mcp_config_format = "project"
            new_adapter.skills_folder = ".opencode/skills/"
            new_adapter.instructions_file = ".opencode/instructions.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--dry-run", "--no-mcp"])
            config = yaml.safe_load((temp_project / ".x-ipe.yaml").read_text())
            assert config["cli"] == "copilot"  # unchanged


class TestNoInitError:
    """EC-1: No .x-ipe.yaml exists."""

    def test_ec_1_no_config_errors(self, runner, tmp_path):
        from src.x_ipe.cli.main import cli
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "opencode"
            mock_svc.list_adapters.return_value = [adapter]
            result = runner.invoke(cli, ["-p", str(tmp_path), "upgrade", "--cli", "opencode", "--no-mcp"])
            assert result.exit_code != 0 or "init" in result.output.lower()


class TestNoCLIFlag:
    """AC-5: No-CLI-Flag Behavior."""

    def test_ac_5_1_no_cli_flag_runs_normal_upgrade(self, runner, temp_project):
        """Without --cli, upgrade runs the normal skills sync flow."""
        from src.x_ipe.cli.main import cli
        result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--no-mcp"])
        assert result.exit_code == 0
        # No migration messages
        assert "migrat" not in result.output.lower()
