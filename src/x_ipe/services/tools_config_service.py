"""
FEATURE-011: Stage Toolbox

ToolsConfigService: CRUD operations for tools configuration

Manages stage toolbox configuration stored in x-ipe-docs/config/tools.json.
Supports migration from legacy .ideation-tools.json format.
"""
import json
import copy
from pathlib import Path
from typing import Dict, Any


CONFIG_DIR = 'x-ipe-docs/config'
CONFIG_FILE = 'tools.json'
LEGACY_PATH = 'x-ipe-docs/ideas/.ideation-tools.json'

DEFAULT_CONFIG = {
    "version": "2.0",
    "stages": {
        "ideation": {
            "ideation": {"antv-infographic": False, "mermaid": False},
            "mockup": {"frontend-design": True},
            "sharing": {}
        },
        "requirement": {"gathering": {}, "analysis": {}},
        "feature": {"design": {}, "implementation": {}},
        "quality": {"testing": {}, "review": {}},
        "refactoring": {"analysis": {}, "execution": {}}
    }
}


class ToolsConfigService:
    """
    Service for managing Stage Toolbox configuration.
    
    FEATURE-011: Stage Toolbox
    
    Configuration is stored in x-ipe-docs/config/tools.json with nested structure:
    stage > phase > tool: boolean
    
    Supports automatic migration from legacy .ideation-tools.json format.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize ToolsConfigService.
        
        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.config_dir = self.project_root / CONFIG_DIR
        self.config_path = self.config_dir / CONFIG_FILE
        self.legacy_path = self.project_root / LEGACY_PATH
    
    def load(self) -> Dict[str, Any]:
        """
        Load config, migrating from legacy if needed.
        
        Order of operations:
        1. If x-ipe-docs/config/tools.json exists, load it
        2. Else if legacy .ideation-tools.json exists, migrate it
        3. Else create default config
        
        Returns:
            Configuration dictionary with version and stages
        """
        if self.config_path.exists():
            return self._read_config()
        
        if self.legacy_path.exists():
            return self._migrate_legacy()
        
        return self._create_default()
    
    def save(self, config: Dict[str, Any]) -> bool:
        """
        Save config to file.
        
        Creates x-ipe-docs/config/ directory if it doesn't exist.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            True on success
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    
    def _read_config(self) -> Dict[str, Any]:
        """
        Read existing config file.
        
        Returns default config if file is corrupted or empty.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    return self._create_default()
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return self._create_default()
    
    def _migrate_legacy(self) -> Dict[str, Any]:
        """
        Migrate from .ideation-tools.json to new format.
        
        Maps legacy structure to new 3-level hierarchy:
        - legacy.ideation -> stages.ideation.ideation
        - legacy.mockup -> stages.ideation.mockup
        - legacy.sharing -> stages.ideation.sharing
        
        Deletes legacy file after successful migration.
        """
        try:
            with open(self.legacy_path, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
            
            # Build new config preserving legacy tool states
            config = copy.deepcopy(DEFAULT_CONFIG)
            
            # Migrate ideation section
            if 'ideation' in legacy:
                for tool, enabled in legacy['ideation'].items():
                    config['stages']['ideation']['ideation'][tool] = enabled
            
            # Migrate mockup section
            if 'mockup' in legacy:
                for tool, enabled in legacy['mockup'].items():
                    config['stages']['ideation']['mockup'][tool] = enabled
            
            # Migrate sharing section
            if 'sharing' in legacy:
                config['stages']['ideation']['sharing'] = legacy['sharing']
            
            # Save new config
            self.save(config)
            
            # Delete legacy file
            self.legacy_path.unlink()
            
            return config
        except (json.JSONDecodeError, IOError):
            return self._create_default()
    
    def _create_default(self) -> Dict[str, Any]:
        """
        Create and save default config.
        
        Returns copy of default config.
        """
        config = copy.deepcopy(DEFAULT_CONFIG)
        self.save(config)
        return config
