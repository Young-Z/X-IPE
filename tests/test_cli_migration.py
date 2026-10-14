"""Tests for FEATURE-027-E: CLI Migration & Upgrade.

Tests the --cli flag on the upgrade command for CLI migration:
backup, config update, and MCP redeployment.
"""

import json
import importlib
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


cli_module = importlib.import_module('x_ipe.cli.main')
cli = cli_module.cli


@pytest.fixture(autouse=True)
def isolated_upgrade_inputs(tmp_path, monkeypatch):
    """A known package skill and known CLI detection, independent of the host."""
    service_module = importlib.import_module('x_ipe.services.cli_adapter_service')
    registry = Path(__file__).resolve().parents[1] / 'x-ipe-docs/config/cli-adapters.yaml'
    service = service_module.CLIAdapterService(config_file_path=str(registry))
    assert service.get_adapter('opencode').instructions_file == 'Agents.md'
    monkeypatch.setattr(service, 'detect_installed_clis', lambda: [])
    monkeypatch.setattr(service, 'is_installed', lambda name: False)
    monkeypatch.setattr(cli_module, 'CLIAdapterService', lambda: service)
    monkeypatch.setattr(service_module, 'CLIAdapterService', lambda: service)
    package_skills = tmp_path / 'package-skills'
    skill_dir = package_skills / 'package-only-skill'
    skill_dir.mkdir(parents=True)
    (skill_dir / 'SKILL.md').write_text('# Package-only skill\n')
    monkeypatch.setattr(cli_module.SkillsManager, '_find_package_skills', lambda self: package_skills)


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
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "opencode"
            adapter.mcp_config_path = "opencode.json"
            adapter.mcp_config_format = "project"
            adapter.skills_folder = ".opencode/skills/"
            adapter.instructions_file = "Agents.md"
            old_adapter = MagicMock()
            old_adapter.name = "copilot"
            old_adapter.skills_folder = ".github/skills/"
            old_adapter.instructions_file = ".github/copilot-instructions.md"
            old_adapter.mcp_config_path = "~/.copilot/mcp-config.json"
            old_adapter.mcp_config_format = "global"
            mock_svc.get_adapter.side_effect = lambda n: adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"], input="1\n")
            assert result.exit_code == 0, (result.output, result.exception)
            assert MockService.called
            assert "opencode" in result.output.lower() or "migrat" in result.output.lower()

    def test_ac_1_2_same_cli_skips_migration(self, runner, temp_project):
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "copilot"
            mock_svc.get_adapter.return_value = adapter
            mock_svc.list_adapters.return_value = [adapter]
            before = (temp_project / '.x-ipe.yaml').read_bytes()
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "copilot", "--no-mcp"], input="1\n")
            assert result.exit_code == 0, (result.output, result.exception)
            assert "already using" in result.output.lower()
            assert (temp_project / '.x-ipe.yaml').read_bytes() == before
            assert not (temp_project / '.x-ipe/backup').exists()

    def test_ac_1_3_unknown_cli_raises_error(self, runner, temp_project):
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "copilot"
            mock_svc.list_adapters.return_value = [adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "unknown-cli", "--no-mcp"])
            assert result.exit_code == 2
            assert "Unknown CLI 'unknown-cli'. Available: copilot" in result.output
            assert not (temp_project / '.x-ipe/backup').exists()


class TestBackup:
    """AC-2: Backup Old Artifacts."""

    def test_ac_2_1_backs_up_skills_folder(self, runner, temp_project):
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
            new_adapter.instructions_file = "Agents.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"], input="1\n")
            assert result.exit_code == 0, (result.output, result.exception)
            # Check backup exists
            backup_dir = temp_project / ".x-ipe" / "backup"
            assert backup_dir.exists()
            backup_dirs = list(backup_dir.iterdir())
            assert len(backup_dirs) == 1
            assert backup_dirs[0].name.startswith("copilot-")
            assert (backup_dirs[0] / 'skills/test-skill/SKILL.md').read_text() == '# Test Skill'
            assert (backup_dirs[0] / 'copilot-instructions.md').read_text() == '# Instructions'
            assert (temp_project / '.github/skills/test-skill/SKILL.md').read_text() == '# Test Skill'
            assert (temp_project / '.github/copilot-instructions.md').read_text() == '# Instructions'

    def test_project_scoped_mcp_backup_preserves_content(self, runner, temp_project):
        """AC-2.3: current project-scoped Copilot MCP content survives backup."""
        mcp_file = temp_project / '.copilot/mcp-config.json'
        mcp_file.parent.mkdir()
        original = json.dumps({'mcpServers': {'user-server': {'command': 'local-fixture'}}}).encode()
        mcp_file.write_bytes(original)
        result = runner.invoke(
            cli, ['-p', str(temp_project), 'upgrade', '--cli', 'opencode', '--no-mcp'], input='1\n',
        )
        assert result.exit_code == 0, (result.output, result.exception)
        backups = list((temp_project / '.x-ipe/backup').iterdir())
        assert len(backups) == 1
        assert (backups[0] / 'mcp-config.json').read_bytes() == original
        assert mcp_file.read_bytes() == original
        assert (backups[0] / 'copilot-instructions.md').read_text() == '# Instructions'

    def test_ac_2_4_dry_run_no_backup(self, runner, temp_project):
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
            new_adapter.instructions_file = "Agents.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--dry-run", "--no-mcp"])
            assert result.exit_code == 0
            backup_dir = temp_project / ".x-ipe" / "backup"
            assert not backup_dir.exists()
            assert (temp_project / '.github/skills/test-skill/SKILL.md').read_text() == '# Test Skill'
            assert (temp_project / '.github/copilot-instructions.md').read_text() == '# Instructions'
            assert not (temp_project / 'Agents.md').exists()


class TestSkillsMigration:
    """Skills and instructions are copied to new CLI folder during migration."""

    def _make_adapters(self):
        old = MagicMock()
        old.name = "copilot"
        old.skills_folder = ".github/skills/"
        old.instructions_file = ".github/copilot-instructions.md"
        old.mcp_config_path = "~/.copilot/mcp-config.json"
        old.mcp_config_format = "global"
        new = MagicMock()
        new.name = "opencode"
        new.mcp_config_path = ".opencode.json"
        new.mcp_config_format = "nested"
        new.skills_folder = ".opencode/skills/"
        new.instructions_file = "Agents.md"
        return old, new

    def test_skills_copied_to_new_folder(self, runner, temp_project):
        old, new = self._make_adapters()
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.get_adapter.side_effect = lambda n: new if n == "opencode" else old
            mock_svc.list_adapters.return_value = [old, new]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"], input="1\n")
            assert result.exit_code == 0, (result.output, result.exception)
            new_skills = temp_project / ".opencode" / "skills" / "test-skill" / "SKILL.md"
            assert new_skills.exists()
            assert new_skills.read_text() == "# Test Skill"

    def test_instructions_copied_to_new_location(self, runner, temp_project):
        old, new = self._make_adapters()
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.get_adapter.side_effect = lambda n: new if n == "opencode" else old
            mock_svc.list_adapters.return_value = [old, new]
            legacy = temp_project / '.opencode/instructions.md'
            legacy.parent.mkdir()
            legacy.write_text('# Do not touch the legacy path')
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"], input="1\n")
            assert result.exit_code == 0, (result.output, result.exception)
            new_instructions = temp_project / "Agents.md"
            assert new_instructions.exists()
            assert new_instructions.read_text() == "# Instructions"
            assert legacy.read_text() == '# Do not touch the legacy path'
            assert (temp_project / '.github/copilot-instructions.md').read_text() == '# Instructions'

    def test_dry_run_no_copy(self, runner, temp_project):
        old, new = self._make_adapters()
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.get_adapter.side_effect = lambda n: new if n == "opencode" else old
            mock_svc.list_adapters.return_value = [old, new]
            before = {str(p.relative_to(temp_project)): p.read_bytes() for p in temp_project.rglob('*') if p.is_file()}
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--dry-run", "--no-mcp"])
            assert result.exit_code == 0
            assert not (temp_project / ".opencode" / "skills").exists()
            assert not (temp_project / 'Agents.md').exists()
            assert 'Would copy instructions: .github/copilot-instructions.md → Agents.md' in result.output
            after = {str(p.relative_to(temp_project)): p.read_bytes() for p in temp_project.rglob('*') if p.is_file()}
            assert after == before

    def test_force_rerun_scans_other_cli_folders(self, runner, temp_project):
        """When config already says opencode but skills are in .github/skills, --force copies them."""
        import yaml
        # Simulate v1.0.29 state: cli=opencode but skills still in .github/skills
        config = {"project_name": "test", "cli": "opencode", "paths": {"skills": ".opencode/skills"}}
        (temp_project / ".x-ipe.yaml").write_text(yaml.dump(config))
        old, new = self._make_adapters()
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.get_adapter.side_effect = lambda n: new if n == "opencode" else old
            mock_svc.list_adapters.return_value = [old, new]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--force", "--no-mcp"])
            assert result.exit_code == 0
            new_skills = temp_project / ".opencode" / "skills" / "test-skill" / "SKILL.md"
            assert new_skills.exists()
            assert new_skills.read_text() == "# Test Skill"


class TestConfigUpdate:
    """AC-3: Config Update."""

    def test_ac_3_1_updates_config_cli_key(self, runner, temp_project):
        import yaml
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
            new_adapter.instructions_file = "Agents.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"], input="1\n")
            assert result.exit_code == 0, (result.output, result.exception)
            config = yaml.safe_load((temp_project / ".x-ipe.yaml").read_text())
            assert config["cli"] == "opencode"

    def test_ac_3_3_migration_updates_skills_path(self, runner, temp_project):
        """Migration to opencode updates paths.skills to .opencode/skills."""
        import yaml
        # Set up config with paths.skills
        config = {"project_name": "test", "cli": "copilot", "paths": {"skills": ".github/skills"}}
        (temp_project / ".x-ipe.yaml").write_text(yaml.dump(config))
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
            new_adapter.instructions_file = "Agents.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"], input="1\n")
            assert result.exit_code == 0, (result.output, result.exception)
            config = yaml.safe_load((temp_project / ".x-ipe.yaml").read_text())
            assert config["paths"]["skills"] == ".opencode/skills"

    def test_ac_3_2_dry_run_no_config_write(self, runner, temp_project):
        import yaml
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
            new_adapter.instructions_file = "Agents.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            before = (temp_project / '.x-ipe.yaml').read_bytes()
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--dry-run", "--no-mcp"])
            assert result.exit_code == 0, (result.output, result.exception)
            assert (temp_project / '.x-ipe.yaml').read_bytes() == before
            config = yaml.safe_load((temp_project / ".x-ipe.yaml").read_text())
            assert config["cli"] == "copilot"  # unchanged


class TestNoInitError:
    """EC-1: No .x-ipe.yaml exists."""

    def test_ec_1_no_config_errors(self, runner, tmp_path):
        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "opencode"
            mock_svc.list_adapters.return_value = [adapter]
            result = runner.invoke(cli, ["-p", str(tmp_path), "upgrade", "--cli", "opencode", "--no-mcp"])
            assert result.exit_code == 1
            assert 'No .x-ipe.yaml found. Run `x-ipe init` first.' in result.output


class TestNoCLIFlag:
    """AC-5: No-CLI-Flag Behavior."""

    def test_ac_5_1_no_cli_flag_runs_normal_upgrade(self, runner, temp_project):
        """Without --cli, upgrade runs the normal skills sync flow when CLI unchanged."""
        result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--no-mcp"], input="\n2\n")
        assert result.exit_code == 0, (result.output, result.exception)
        # No migration messages (same CLI selected = no migration)
        assert "migrat" not in result.output.lower()
        assert (temp_project / '.github/skills/package-only-skill/SKILL.md').read_text() == '# Package-only skill\n'

    def test_upgrade_prompts_cli_selection_triggers_migration(self, runner, temp_project):
        """Without --cli, selecting another CLI triggers migration."""
        with patch.object(cli_module, "_resolve_cli_selection", return_value="opencode"):
            with patch.object(cli_module, "_handle_cli_migration") as mock_migrate:
                result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--no-mcp"], input="1\n")
                assert result.exit_code == 0, (result.output, result.exception)
                mock_migrate.assert_called_once()
                assert mock_migrate.call_args.args[1] == "opencode"

    def test_upgrade_continues_after_migration(self, runner, temp_project):
        """After CLI migration, upgrade continues with skills sync (no early return)."""
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
            new_adapter.instructions_file = "Agents.md"
            mock_svc.get_adapter.side_effect = lambda n: new_adapter if n == "opencode" else old_adapter
            mock_svc.list_adapters.return_value = [old_adapter, new_adapter]
            result = runner.invoke(cli, ["-p", str(temp_project), "upgrade", "--cli", "opencode", "--no-mcp"], input="2\n")
            assert result.exit_code == 0, (result.output, result.exception)
            # After migration, the normal upgrade flow should continue
            assert "upgrading x-ipe skills" in result.output.lower()
            assert 'Synced 1 skill(s)' in result.output
            assert (temp_project / '.github/skills/package-only-skill/SKILL.md').read_text() == '# Package-only skill\n'


class TestConfigRouteFields:
    """Bug fix: /api/config/cli-adapter returns run_args and inline_prompt_flag."""

    def test_api_returns_run_args_and_prompt_flag(self):
        """Config route includes run_args and inline_prompt_flag in response."""
        import importlib
        from unittest.mock import MagicMock
        from flask import Flask

        app = Flask(__name__)
        from x_ipe.routes.config_routes import config_bp
        app.register_blueprint(config_bp)

        mock_service = MagicMock()
        adapter = MagicMock()
        adapter.name = "opencode"
        adapter.display_name = "OpenCode CLI"
        adapter.command = "opencode"
        adapter.run_args = ""
        adapter.inline_prompt_flag = "--prompt"
        adapter.prompt_format = '{command} {inline_prompt_flag} "{escaped_prompt}"'
        mock_service.get_active_adapter.return_value = adapter
        mock_service.is_installed.return_value = True
        app.config['CLI_ADAPTER_SERVICE'] = mock_service

        with app.test_client() as client:
            resp = client.get('/api/config/cli-adapter')
            data = resp.get_json()
            assert data['success'] is True
            assert 'run_args' in data
            assert 'inline_prompt_flag' in data
            assert data['inline_prompt_flag'] == '--prompt'
            assert data['command'] == 'opencode'
