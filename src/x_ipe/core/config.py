"""
X-IPE Configuration Module

Handles loading and parsing of .x-ipe.yaml configuration files.
Provides sensible defaults when no config file exists.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


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
    server_port: int = 5959
    server_debug: bool = False
    
    @classmethod
    def load(cls, start_dir: Path = None) -> "XIPEConfig":
        """
        Load config from .x-ipe.yaml or use defaults.
        
        Args:
            start_dir: Directory to start searching for config.
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
        
        # Find config file
        config_path = cls._find_config(start_dir)
        
        if config_path is None:
            # No config file, use defaults
            return cls.defaults(start_dir)
        
        # Parse config file
        return cls._parse_config(config_path)
    
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
            server_port=5959,
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
            raw = yaml.safe_load(f)
        
        if raw is None:
            raw = {}
        
        # Validate version
        version = raw.get('version', 1)
        if version != SUPPORTED_VERSION:
            raise ValueError(f"Unsupported config version: {version}. Expected: {SUPPORTED_VERSION}")
        
        config_dir = config_path.parent
        
        # Parse paths (relative to config file location)
        paths = raw.get('paths', {})
        project_root = cls._resolve_path(config_dir, paths.get('project_root', '.'))
        docs_path = cls._resolve_path(config_dir, paths.get('docs', 'x-ipe-docs'))
        skills_path = cls._resolve_path(config_dir, paths.get('skills', '.github/skills'))
        runtime_path = cls._resolve_path(config_dir, paths.get('runtime', '.x-ipe'))
        
        # Parse server settings
        server = raw.get('server', {})
        server_host = server.get('host', '127.0.0.1')
        server_port = server.get('port', 5959)
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
