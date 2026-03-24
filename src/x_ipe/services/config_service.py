"""
FEATURE-010: Project Root Configuration

ConfigData: Data class for resolved config values
ConfigService: Discovery, parsing, validation of .x-ipe.yaml

Supports layered configuration:
  1. Package-bundled defaults (src/x_ipe/defaults/.x-ipe.yaml)
  2. Project-level .x-ipe.yaml overrides (discovered from start_dir upwards)
"""
import os
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from x_ipe.tracing import x_ipe_tracing
from x_ipe.core.config_utils import load_package_defaults, deep_merge


CONFIG_FILE_NAME = '.x-ipe.yaml'
MAX_PARENT_LEVELS = 20


@dataclass
class ConfigData:
    """
    Resolved configuration from .x-ipe.yaml
    
    FEATURE-010: Project Root Configuration
    FEATURE-028-D: Language field for Settings Language Switch
    
    All paths are absolute after resolution.
    """
    config_file_path: str
    version: int
    project_root: str
    x_ipe_app: str
    file_tree_scope: str
    terminal_cwd: str
    language: str = "en"
    auto_execute_prompt: bool = False
    
    @x_ipe_tracing()
    def get_file_tree_path(self) -> str:
        """Return the path for file tree based on file_tree_scope."""
        return self.project_root if self.file_tree_scope == "project_root" else self.x_ipe_app
    
    @x_ipe_tracing()
    def get_terminal_cwd(self) -> str:
        """Return the path for terminal cwd based on terminal_cwd setting."""
        return self.project_root if self.terminal_cwd == "project_root" else self.x_ipe_app
    
    @x_ipe_tracing()
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            'config_file': self.config_file_path,
            'version': self.version,
            'project_root': self.project_root,
            'x_ipe_app': self.x_ipe_app,
            'file_tree_scope': self.file_tree_scope,
            'terminal_cwd': self.terminal_cwd,
            'language': self.language,
            'auto_execute_prompt': self.auto_execute_prompt,
        }


class ConfigService:
    """
    Service for discovering and parsing .x-ipe.yaml configuration.
    
    FEATURE-010: Project Root Configuration
    
    Discovers config file by traversing from start_dir up to 20 parent levels.
    Parses YAML content and validates required fields.
    Resolves relative paths to absolute based on config file location.
    """
    
    def __init__(self, start_dir: Optional[str] = None):
        """
        Initialize ConfigService.
        
        Args:
            start_dir: Starting directory for config discovery.
                       Defaults to current working directory.
        """
        self.start_dir = Path(start_dir or os.getcwd()).resolve()
        self._config_data: Optional[ConfigData] = None
        self._error: Optional[str] = None
    
    @x_ipe_tracing()
    def load(self) -> Optional[ConfigData]:
        """
        Discover, parse, and validate config with layered defaults.

        Resolution order (later overrides earlier):
        1. Package-bundled defaults (src/x_ipe/defaults/.x-ipe.yaml)
        2. Project-level .x-ipe.yaml (discovered from start_dir upwards)
        
        Returns:
            ConfigData if valid config produced, None otherwise.
        """
        # Layer 1: Package defaults
        pkg_defaults = load_package_defaults()
        
        # Layer 2: Project config (if discovered)
        config_path = self._discover()
        project_raw = None
        if config_path:
            project_raw = self._parse(config_path)
            if project_raw is None:
                return None
        
        # Merge layers
        if project_raw is not None:
            merged = deep_merge(pkg_defaults, project_raw)
            config_data = self._validate(config_path, merged)
        elif pkg_defaults:
            merged = pkg_defaults
            config_data = self._validate(None, merged)
        else:
            return None
        
        if config_data:
            self._config_data = config_data
        return config_data
    
    def _discover(self) -> Optional[Path]:
        """
        Search for .x-ipe.yaml from start_dir up to 20 parent levels.
        
        Returns:
            Path to config file if found, None otherwise.
        """
        current = self.start_dir
        
        for _ in range(MAX_PARENT_LEVELS):
            config_path = current / CONFIG_FILE_NAME
            if config_path.exists() and config_path.is_file():
                return config_path
            
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        
        return None
    
    def _parse(self, config_path: Path) -> Optional[dict]:
        """
        Parse YAML content from config file.
        
        Returns:
            Parsed dict if successful, None on error.
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                result = yaml.safe_load(f)
                if result is None:
                    self._error = "Config file is empty"
                    return None
                return result
        except yaml.YAMLError as e:
            self._error = f"YAML parse error: {e}"
            return None
        except IOError as e:
            self._error = f"Cannot read config file: {e}"
            return None
    
    def _validate(self, config_path: Optional[Path], raw: dict,
                  base_dir: Optional[Path] = None) -> Optional[ConfigData]:
        """
        Validate config content and resolve paths.
        
        Args:
            config_path: Path to the discovered project config file, or None
                         when using package defaults only.
            raw: Merged config dict to validate.
            base_dir: Directory for resolving relative paths. Defaults to
                      config_path.parent if config_path is given, else
                      self.start_dir.
        
        Returns:
            ConfigData if valid, None on validation error.
        """
        if base_dir is None:
            base_dir = config_path.parent if config_path else self.start_dir
        
        config_file_display = str(config_path) if config_path else "package-defaults"
        
        # Check version
        version = raw.get('version')
        if version != 1:
            self._error = f"Unsupported config version: {version}"
            return None
        
        # Check required paths
        paths = raw.get('paths', {})
        if not paths.get('project_root'):
            self._error = "Missing required field: paths.project_root"
            return None
        
        # Resolve paths relative to base directory
        project_root = (base_dir / paths['project_root']).resolve()
        
        # x_ipe_app is optional, defaults to project_root
        x_ipe_app_path = paths.get('x_ipe_app', paths['project_root'])
        x_ipe_app = (base_dir / x_ipe_app_path).resolve()
        
        # Validate paths exist and are directories
        if not project_root.exists() or not project_root.is_dir():
            self._error = f"project_root path does not exist or is not a directory: {project_root}"
            return None
        if not x_ipe_app.exists() or not x_ipe_app.is_dir():
            self._error = f"x_ipe_app path does not exist or is not a directory: {x_ipe_app}"
            return None
        
        # Get defaults with fallbacks
        defaults = raw.get('defaults', {})
        file_tree_scope = defaults.get('file_tree_scope', 'project_root')
        terminal_cwd = defaults.get('terminal_cwd', 'project_root')
        
        # Language (FEATURE-028-D)
        language = raw.get('language', 'en')
        
        # Console settings
        console = raw.get('console', {})
        auto_execute_prompt = console.get('auto_execute_prompt', False)
        
        # Validate scope values
        valid_scopes = ('project_root', 'x_ipe_app')
        if file_tree_scope not in valid_scopes:
            self._error = f"Invalid file_tree_scope: {file_tree_scope}. Must be one of {valid_scopes}"
            return None
        if terminal_cwd not in valid_scopes:
            self._error = f"Invalid terminal_cwd: {terminal_cwd}. Must be one of {valid_scopes}"
            return None
        
        return ConfigData(
            config_file_path=config_file_display,
            version=version,
            project_root=str(project_root),
            x_ipe_app=str(x_ipe_app),
            file_tree_scope=file_tree_scope,
            terminal_cwd=terminal_cwd,
            language=language,
            auto_execute_prompt=auto_execute_prompt,
        )
    
    @property
    def error(self) -> Optional[str]:
        """Return the last error message, if any."""
        return self._error
    
    @property
    def config(self) -> Optional[ConfigData]:
        """Return the loaded config data."""
        return self._config_data
