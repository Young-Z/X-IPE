"""
Tests for layered .x-ipe.yaml configuration.

Covers:
- deep_merge utility
- load_package_defaults utility
- XIPEConfig layered loading (CLI path)
- ConfigService layered loading (Flask path)
"""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from x_ipe.core.config_utils import deep_merge, load_package_defaults, get_package_defaults_path
from x_ipe.core.config import XIPEConfig
from x_ipe.services.config_service import ConfigService


# ============================================================================
# deep_merge tests
# ============================================================================

class TestDeepMerge:
    """Tests for deep_merge utility."""

    def test_empty_base(self):
        result = deep_merge({}, {"a": 1})
        assert result == {"a": 1}

    def test_empty_override(self):
        result = deep_merge({"a": 1}, {})
        assert result == {"a": 1}

    def test_both_empty(self):
        result = deep_merge({}, {})
        assert result == {}

    def test_scalar_override(self):
        result = deep_merge({"a": 1, "b": 2}, {"b": 99})
        assert result == {"a": 1, "b": 99}

    def test_nested_dict_merge(self):
        base = {"server": {"host": "127.0.0.1", "port": 5858}}
        override = {"server": {"port": 9000}}
        result = deep_merge(base, override)
        assert result == {"server": {"host": "127.0.0.1", "port": 9000}}

    def test_deeply_nested_merge(self):
        base = {"a": {"b": {"c": 1, "d": 2}}}
        override = {"a": {"b": {"d": 99}}}
        result = deep_merge(base, override)
        assert result == {"a": {"b": {"c": 1, "d": 99}}}

    def test_override_adds_new_keys(self):
        base = {"a": 1}
        override = {"b": 2}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": 2}

    def test_list_replaced_not_merged(self):
        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}
        result = deep_merge(base, override)
        assert result == {"items": [4, 5]}

    def test_dict_replaced_by_scalar(self):
        base = {"a": {"nested": True}}
        override = {"a": "flat"}
        result = deep_merge(base, override)
        assert result == {"a": "flat"}

    def test_scalar_replaced_by_dict(self):
        base = {"a": "flat"}
        override = {"a": {"nested": True}}
        result = deep_merge(base, override)
        assert result == {"a": {"nested": True}}

    def test_does_not_mutate_base(self):
        base = {"a": {"b": 1}}
        override = {"a": {"b": 2}}
        deep_merge(base, override)
        assert base == {"a": {"b": 1}}

    def test_does_not_mutate_override(self):
        base = {"a": 1}
        override = {"a": 2}
        deep_merge(base, override)
        assert override == {"a": 2}


# ============================================================================
# load_package_defaults tests
# ============================================================================

class TestLoadPackageDefaults:
    """Tests for loading the package-bundled default config."""

    def test_returns_dict(self):
        result = load_package_defaults()
        assert isinstance(result, dict)

    def test_has_version(self):
        result = load_package_defaults()
        assert result.get("version") == 1

    def test_has_paths_project_root(self):
        result = load_package_defaults()
        assert result.get("paths", {}).get("project_root") == "."

    def test_has_server_defaults(self):
        result = load_package_defaults()
        server = result.get("server", {})
        assert server.get("host") == "127.0.0.1"
        assert server.get("port") == 5858
        assert server.get("debug") is False

    def test_has_language_default(self):
        result = load_package_defaults()
        assert result.get("language") == "en"

    def test_has_defaults_section(self):
        result = load_package_defaults()
        defaults = result.get("defaults", {})
        assert defaults.get("file_tree_scope") == "project_root"
        assert defaults.get("terminal_cwd") == "project_root"

    def test_has_console_section(self):
        result = load_package_defaults()
        console = result.get("console", {})
        assert console.get("auto_execute_prompt") is False

    def test_package_defaults_path_exists(self):
        assert get_package_defaults_path().exists()

    def test_returns_empty_dict_when_file_missing(self):
        with patch("x_ipe.core.config_utils._DEFAULTS_PATH", Path("/nonexistent/.x-ipe.yaml")):
            result = load_package_defaults()
            assert result == {}


# ============================================================================
# XIPEConfig layered loading tests
# ============================================================================

class TestXIPEConfigLayered:
    """Tests for XIPEConfig with layered config loading."""

    def test_loads_package_defaults_when_no_project_config(self):
        """Without project .x-ipe.yaml, package defaults should apply."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = XIPEConfig.load(Path(tmpdir))
            # Should still get sensible defaults from package
            assert config.server_host == "127.0.0.1"
            assert config.server_port == 5858
            assert config.server_debug is False
            assert config.project_root == Path(tmpdir).resolve()

    def test_project_config_overrides_package_defaults(self):
        """Project .x-ipe.yaml should override package defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            config_content = """version: 1
paths:
  project_root: "."
server:
  port: 9000
  debug: true
"""
            (project_dir / ".x-ipe.yaml").write_text(config_content)
            config = XIPEConfig.load(project_dir)
            # Overridden values
            assert config.server_port == 9000
            assert config.server_debug is True
            # Non-overridden values from package defaults
            assert config.server_host == "127.0.0.1"

    def test_partial_server_override(self):
        """Overriding only server.port should keep host from defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            config_content = """version: 1
paths:
  project_root: "."
server:
  port: 7777
"""
            (project_dir / ".x-ipe.yaml").write_text(config_content)
            config = XIPEConfig.load(project_dir)
            assert config.server_port == 7777
            assert config.server_host == "127.0.0.1"  # from package defaults

    def test_config_path_set_when_project_config_found(self):
        """config_path should reference the project config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir).resolve()
            config_content = """version: 1
paths:
  project_root: "."
"""
            (project_dir / ".x-ipe.yaml").write_text(config_content)
            config = XIPEConfig.load(project_dir)
            assert config.config_path == project_dir / ".x-ipe.yaml"

    def test_config_path_none_when_only_package_defaults(self):
        """config_path should be None when no project config found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = XIPEConfig.load(Path(tmpdir))
            assert config.config_path is None


# ============================================================================
# ConfigService layered loading tests
# ============================================================================

class TestConfigServiceLayered:
    """Tests for ConfigService with layered config loading."""

    def test_loads_package_defaults_when_no_project_config(self):
        """Without project .x-ipe.yaml, package defaults should apply."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ConfigService(start_dir=tmpdir)
            config_data = service.load()
            assert config_data is not None
            assert config_data.language == "en"
            assert config_data.file_tree_scope == "project_root"
            assert config_data.terminal_cwd == "project_root"
            assert config_data.auto_execute_prompt is False

    def test_config_file_path_shows_package_defaults(self):
        """When using only package defaults, config_file_path should indicate that."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ConfigService(start_dir=tmpdir)
            config_data = service.load()
            assert config_data is not None
            assert config_data.config_file_path == "package-defaults"

    def test_project_config_overrides_package_defaults(self):
        """Project .x-ipe.yaml should override package defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            config_content = """version: 1
paths:
  project_root: "."
language: "zh"
console:
  auto_execute_prompt: true
"""
            (project_dir / ".x-ipe.yaml").write_text(config_content)
            service = ConfigService(start_dir=tmpdir)
            config_data = service.load()
            assert config_data is not None
            # Overridden values
            assert config_data.language == "zh"
            assert config_data.auto_execute_prompt is True
            # Non-overridden values from package defaults
            assert config_data.file_tree_scope == "project_root"

    def test_partial_defaults_override(self):
        """Overriding only defaults.file_tree_scope should keep terminal_cwd."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            # Create x-ipe subdir so x_ipe_app scope is valid
            (project_dir / "x-ipe").mkdir()
            config_content = """version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe"
defaults:
  file_tree_scope: "x_ipe_app"
"""
            (project_dir / ".x-ipe.yaml").write_text(config_content)
            service = ConfigService(start_dir=tmpdir)
            config_data = service.load()
            assert config_data is not None
            assert config_data.file_tree_scope == "x_ipe_app"
            assert config_data.terminal_cwd == "project_root"  # from package defaults

    def test_project_root_resolves_to_start_dir_with_defaults_only(self):
        """Package defaults project_root '.' should resolve to start_dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ConfigService(start_dir=tmpdir)
            config_data = service.load()
            assert config_data is not None
            assert config_data.project_root == str(Path(tmpdir).resolve())

    def test_config_file_path_set_when_project_config_found(self):
        """config_file_path should reference the project config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            config_content = """version: 1
paths:
  project_root: "."
"""
            (project_dir / ".x-ipe.yaml").write_text(config_content)
            service = ConfigService(start_dir=tmpdir)
            config_data = service.load()
            assert config_data is not None
            assert ".x-ipe.yaml" in config_data.config_file_path
            assert config_data.config_file_path != "package-defaults"

    def test_parse_error_returns_none(self):
        """Parse errors on project config should still return None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / ".x-ipe.yaml").write_text(": invalid: yaml: [[[")
            service = ConfigService(start_dir=tmpdir)
            config_data = service.load()
            assert config_data is None
            assert service.error is not None


# ============================================================================
# Integration: deep merge with real config scenarios
# ============================================================================

class TestLayeredConfigIntegration:
    """End-to-end layered config scenarios."""

    def test_full_override_scenario(self):
        """Project config overrides every section of package defaults."""
        pkg = {
            "version": 1,
            "paths": {"project_root": "."},
            "defaults": {"file_tree_scope": "project_root", "terminal_cwd": "project_root"},
            "language": "en",
            "console": {"auto_execute_prompt": False},
            "server": {"host": "127.0.0.1", "port": 5858, "debug": False},
        }
        project = {
            "version": 1,
            "paths": {"project_root": ".", "x_ipe_app": "./app"},
            "defaults": {"file_tree_scope": "x_ipe_app"},
            "language": "zh",
            "console": {"auto_execute_prompt": True},
            "server": {"host": "0.0.0.0", "port": 9000, "debug": True},
        }
        merged = deep_merge(pkg, project)
        assert merged["language"] == "zh"
        assert merged["server"]["host"] == "0.0.0.0"
        assert merged["server"]["port"] == 9000
        assert merged["defaults"]["file_tree_scope"] == "x_ipe_app"
        # terminal_cwd NOT in project override — kept from package defaults
        assert merged["defaults"]["terminal_cwd"] == "project_root"
        assert merged["paths"]["x_ipe_app"] == "./app"

    def test_minimal_project_override(self):
        """Project specifies only version + paths (minimum required)."""
        pkg = load_package_defaults()
        project = {"version": 1, "paths": {"project_root": "."}}
        merged = deep_merge(pkg, project)
        # All defaults preserved
        assert merged["language"] == "en"
        assert merged["server"]["host"] == "127.0.0.1"
        assert merged["defaults"]["file_tree_scope"] == "project_root"
