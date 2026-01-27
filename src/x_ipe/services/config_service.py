"""
FEATURE-010: Project Root Configuration

ConfigData: Data class for resolved config values
ConfigService: Discovery, parsing, validation of .x-ipe.yaml
"""
import os
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


CONFIG_FILE_NAME = '.x-ipe.yaml'
MAX_PARENT_LEVELS = 20


@dataclass
class ConfigData:
    """
    Resolved configuration from .x-ipe.yaml
    
    FEATURE-010: Project Root Configuration
    
    All paths are absolute after resolution.
    """
    config_file_path: str
    version: int
    project_root: str
    x_ipe_app: str
    file_tree_scope: str
    terminal_cwd: str
    
    def get_file_tree_path(self) -> str:
        """Return the path for file tree based on file_tree_scope."""
        return self.project_root if self.file_tree_scope == "project_root" else self.x_ipe_app
    
    def get_terminal_cwd(self) -> str:
        """Return the path for terminal cwd based on terminal_cwd setting."""
        return self.project_root if self.terminal_cwd == "project_root" else self.x_ipe_app
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            'config_file': self.config_file_path,
            'version': self.version,
            'project_root': self.project_root,
            'x_ipe_app': self.x_ipe_app,
            'file_tree_scope': self.file_tree_scope,
            'terminal_cwd': self.terminal_cwd
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
    
    def load(self) -> Optional[ConfigData]:
        """
        Discover, parse, and validate config file.
        
        Returns:
            ConfigData if valid config found, None otherwise.
        """
        config_path = self._discover()
        if not config_path:
            return None
        
        raw_config = self._parse(config_path)
        if not raw_config:
            return None
        
        config_data = self._validate(config_path, raw_config)
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
    
    def _validate(self, config_path: Path, raw: dict) -> Optional[ConfigData]:
        """
        Validate config content and resolve paths.
        
        Returns:
            ConfigData if valid, None on validation error.
        """
        config_dir = config_path.parent
        
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
        
        # Resolve paths relative to config file location
        project_root = (config_dir / paths['project_root']).resolve()
        
        # x_ipe_app is optional, defaults to project_root
        x_ipe_app_path = paths.get('x_ipe_app', paths['project_root'])
        x_ipe_app = (config_dir / x_ipe_app_path).resolve()
        
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
        
        # Validate scope values
        valid_scopes = ('project_root', 'x_ipe_app')
        if file_tree_scope not in valid_scopes:
            self._error = f"Invalid file_tree_scope: {file_tree_scope}. Must be one of {valid_scopes}"
            return None
        if terminal_cwd not in valid_scopes:
            self._error = f"Invalid terminal_cwd: {terminal_cwd}. Must be one of {valid_scopes}"
            return None
        
        return ConfigData(
            config_file_path=str(config_path),
            version=version,
            project_root=str(project_root),
            x_ipe_app=str(x_ipe_app),
            file_tree_scope=file_tree_scope,
            terminal_cwd=terminal_cwd
        )
    
    @property
    def error(self) -> Optional[str]:
        """Return the last error message, if any."""
        return self._error
    
    @property
    def config(self) -> Optional[ConfigData]:
        """Return the loaded config data."""
        return self._config_data
