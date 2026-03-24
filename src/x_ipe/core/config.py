"""
X-IPE Configuration Module

Handles loading and parsing of .x-ipe.yaml configuration files.
Package-bundled defaults are loaded first, then overridden by any
project-level .x-ipe.yaml found in the project directory.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml

from .config_utils import load_package_defaults, deep_merge


CONFIG_FILE_NAME = ".x-ipe.yaml"
SUPPORTED_VERSION = 1


@dataclass
class XIPEConfig:
    """
    Resolved X-IPE configuration.
    
    All paths are absolute after resolution.
    """
    config_path: Optional[Path] = None
    project_root: Path = field(default_factory=Path.cwd)
    docs_path: Path = field(default_factory=lambda: Path.cwd() / "x-ipe-docs")
    skills_path: Path = field(default_factory=lambda: Path.cwd() / ".github" / "skills")
    runtime_path: Path = field(default_factory=lambda: Path.cwd() / ".x-ipe")
    server_host: str = "127.0.0.1"
    server_port: int = 5858
    server_debug: bool = False
    
    @classmethod
    def load(cls, start_dir: Path = None) -> "XIPEConfig":
        """
        Load config with layered defaults.

        Resolution order (later overrides earlier):
        1. Package-bundled defaults (src/x_ipe/defaults/.x-ipe.yaml)
        2. Project-level .x-ipe.yaml (in start_dir)
        
        Args:
            start_dir: Directory to search for project config.
                       Defaults to current working directory.
        
        Returns:
            XIPEConfig instance with resolved paths.
        
        Raises:
            ValueError: If config file has unsupported version.
            yaml.YAMLError: If config file has invalid YAML.
        """
        if start_dir is None:
            start_dir = Path.cwd()
        start_dir = Path(start_dir).resolve()
        
        # Layer 1: Package defaults
        pkg_defaults = load_package_defaults()
        
        # Layer 2: Project config (if found)
        config_path = cls._find_config(start_dir)
        
        if config_path is not None:
            with open(config_path, 'r', encoding='utf-8') as f:
                project_raw = yaml.safe_load(f) or {}
            merged = deep_merge(pkg_defaults, project_raw)
            return cls._parse_raw(merged, config_path.parent, config_path)
        
        if pkg_defaults:
            return cls._parse_raw(pkg_defaults, start_dir, config_path=None)
        
        return cls.defaults(start_dir)
    
    @classmethod
    def defaults(cls, project_root: Path) -> "XIPEConfig":
        """
        Create config with sensible defaults.
        
        Args:
            project_root: Root directory of the project.
        
        Returns:
            XIPEConfig with default values.
        """
        project_root = Path(project_root).resolve()
        return cls(
            config_path=None,
            project_root=project_root,
            docs_path=project_root / "x-ipe-docs",
            skills_path=project_root / ".github" / "skills",
            runtime_path=project_root / ".x-ipe",
            server_host="127.0.0.1",
            server_port=5858,
            server_debug=False,
        )
    
    @classmethod
    def _find_config(cls, start_dir: Path) -> Optional[Path]:
        """
        Search for .x-ipe.yaml starting from start_dir.
        
        Only searches in start_dir, not parent directories.
        """
        config_path = start_dir / CONFIG_FILE_NAME
        if config_path.exists() and config_path.is_file():
            return config_path
        return None
    
    @classmethod
    def _parse_config(cls, config_path: Path) -> "XIPEConfig":
        """
        Parse config file and return XIPEConfig.
        
        Args:
            config_path: Path to .x-ipe.yaml file.
        
        Returns:
            XIPEConfig instance.
        
        Raises:
            ValueError: If version is unsupported.
            yaml.YAMLError: If YAML is invalid.
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            raw = yaml.safe_load(f) or {}
        return cls._parse_raw(raw, config_path.parent, config_path)
    
    @classmethod
    def _parse_raw(cls, raw: dict, base_dir: Path, config_path: Optional[Path] = None) -> "XIPEConfig":
        """
        Parse a raw config dict and return XIPEConfig.
        
        Args:
            raw: Parsed YAML dict (may be merged already).
            base_dir: Directory for resolving relative paths.
            config_path: Original config file path (None for package defaults only).
        """
        # Validate version
        version = raw.get('version', 1)
        if version != SUPPORTED_VERSION:
            raise ValueError(f"Unsupported config version: {version}. Expected: {SUPPORTED_VERSION}")
        
        # Parse paths (relative to base_dir)
        paths = raw.get('paths', {})
        project_root = cls._resolve_path(base_dir, paths.get('project_root', '.'))
        docs_path = cls._resolve_path(base_dir, paths.get('docs', 'x-ipe-docs'))
        skills_path = cls._resolve_path(base_dir, paths.get('skills', '.github/skills'))
        runtime_path = cls._resolve_path(base_dir, paths.get('runtime', '.x-ipe'))
        
        # Parse server settings
        server = raw.get('server', {})
        server_host = server.get('host', '127.0.0.1')
        server_port = server.get('port', 5858)
        server_debug = server.get('debug', False)
        
        return cls(
            config_path=config_path,
            project_root=project_root,
            docs_path=docs_path,
            skills_path=skills_path,
            runtime_path=runtime_path,
            server_host=server_host,
            server_port=server_port,
            server_debug=server_debug,
        )
    
    @staticmethod
    def _resolve_path(base: Path, path_str: str) -> Path:
        """Resolve a path relative to base directory."""
        path = Path(path_str)
        if path.is_absolute():
            return path.resolve()
        return (base / path).resolve()
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            'config_path': str(self.config_path) if self.config_path else None,
            'project_root': str(self.project_root),
            'docs_path': str(self.docs_path),
            'skills_path': str(self.skills_path),
            'runtime_path': str(self.runtime_path),
            'server_host': self.server_host,
            'server_port': self.server_port,
            'server_debug': self.server_debug,
        }
