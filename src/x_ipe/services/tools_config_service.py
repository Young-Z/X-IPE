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

from x_ipe.tracing import x_ipe_tracing


CONFIG_DIR = 'x-ipe-docs/config'
CONFIG_FILE = 'tools.json'
LEGACY_PATH = 'x-ipe-docs/ideas/.ideation-tools.json'

DEFAULT_CONFIG = {
    "version": "3.1",
    "stages": {
        "ideation": {
            "ideation": {"x-ipe-tool-infographic-syntax": False, "mermaid": False},
            "mockup": {"frontend-design": True},
            "architecture": {},
            "sharing": {}
        },
        "requirement": {"gathering": {}, "analysis": {}},
        "implement": {
            "technical_design": {},
            "implementation": {},
            "acceptance_testing": {}
        },
        "feedback": {
            "bug_fix": {},
            "code_refactor": {},
            "refactoring_analysis": {},
            "human_playground": {},
            "change_request": {}
        }
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
    
    @x_ipe_tracing()
    def load(self) -> Dict[str, Any]:
        """
        Load config, migrating from legacy if needed.
        
        Order of operations:
        1. If x-ipe-docs/config/tools.json exists, load and migrate if needed
        2. Else if legacy .ideation-tools.json exists, migrate it
        3. Else create default config
        
        Returns:
            Configuration dictionary with version and stages
        """
        if self.config_path.exists():
            config = self._read_config()
            version = config.get('version', '1.0')
            if version == '2.0':
                config = self._migrate_v2_to_v3(config)
                self.save(config)
            elif version == '3.0':
                config = self._migrate_v3_to_v31(config)
                self.save(config)
            changed = self._normalize_action_keys(config)
            if changed:
                self.save(config)
            return config
        
        if self.legacy_path.exists():
            return self._migrate_legacy()
        
        return self._create_default()
    
    @staticmethod
    def _normalize_action_keys(config: Dict[str, Any]) -> bool:
        """Rename legacy action keys to canonical workflow names. Returns True if changes made."""
        renames = {'code_implementation': 'implementation', 'acceptance_test': 'acceptance_testing'}
        impl = config.get('stages', {}).get('implement', {})
        changed = False
        for old_key, new_key in renames.items():
            if old_key in impl and new_key not in impl:
                impl[new_key] = impl.pop(old_key)
                changed = True
            elif old_key in impl and new_key in impl:
                impl.pop(old_key)
                changed = True
        return changed
    @x_ipe_tracing()
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
    
    def _migrate_v2_to_v3(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate v2.0 stages (feature/quality/refactoring) to v3.1 (implement/feedback).
        
        Mapping:
        - feature.consultation → implement.technical_design
        - feature.implementation → implement.implementation
        - quality.testing → implement.acceptance_testing
        - feature.bug_fix → feedback.bug_fix
        - refactoring.execution → feedback.code_refactor
        - feature.consultation → feedback.refactoring_analysis (copy)
        - feature.playground → feedback.human_playground
        - Unused phases (design, review) are dropped
        """
        stages = config.get('stages', {})
        feature = stages.pop('feature', {})
        quality = stages.pop('quality', {})
        refactoring = stages.pop('refactoring', {})
        
        implement = {}
        if 'consultation' in feature:
            implement['technical_design'] = feature['consultation']
        if 'implementation' in feature:
            implement['implementation'] = feature['implementation']
        if 'testing' in quality:
            implement['acceptance_testing'] = quality['testing']
        
        feedback = {}
        if 'bug_fix' in feature:
            feedback['bug_fix'] = feature['bug_fix']
        if 'execution' in refactoring:
            feedback['code_refactor'] = refactoring['execution']
        if 'consultation' in feature:
            feedback['refactoring_analysis'] = copy.deepcopy(feature['consultation'])
        if 'playground' in feature:
            feedback['human_playground'] = feature['playground']
        feedback.setdefault('change_request', {})
        
        stages['implement'] = implement
        stages['feedback'] = feedback
        config['stages'] = stages
        config['version'] = '3.1'
        return config
    
    def _migrate_v3_to_v31(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate v3.0 phase names to v3.1 workflow-aligned names.
        
        Mapping:
        - implement: consultation→technical_design, implementation→implementation,
          testing→acceptance_testing, design/review dropped
        - feedback: playground→human_playground, refactoring→code_refactor+refactoring_analysis
        """
        stages = config.get('stages', {})
        
        impl = stages.get('implement', {})
        new_impl = {}
        if 'consultation' in impl:
            new_impl['technical_design'] = impl['consultation']
        if 'implementation' in impl:
            new_impl['implementation'] = impl['implementation']
        if 'testing' in impl:
            new_impl['acceptance_testing'] = impl['testing']
        # Carry over if already using new names
        for key in ('technical_design', 'implementation', 'acceptance_testing'):
            if key in impl and key not in new_impl:
                new_impl[key] = impl[key]
        # Backward compat: carry over old names as canonical names
        if 'code_implementation' in impl and 'implementation' not in new_impl:
            new_impl['implementation'] = impl['code_implementation']
        if 'acceptance_test' in impl and 'acceptance_testing' not in new_impl:
            new_impl['acceptance_testing'] = impl['acceptance_test']
        stages['implement'] = new_impl
        
        fb = stages.get('feedback', {})
        new_fb = {}
        new_fb['bug_fix'] = fb.get('bug_fix', {})
        if 'refactoring' in fb:
            new_fb['code_refactor'] = fb['refactoring']
            new_fb['refactoring_analysis'] = copy.deepcopy(fb['refactoring'])
        if 'playground' in fb:
            new_fb['human_playground'] = fb['playground']
        # Carry over if already using new names
        for key in ('code_refactor', 'refactoring_analysis', 'human_playground'):
            if key in fb and key not in new_fb:
                new_fb[key] = fb[key]
        new_fb.setdefault('change_request', fb.get('change_request', {}))
        stages['feedback'] = new_fb
        
        config['stages'] = stages
        config['version'] = '3.1'
        return config
    
    def _create_default(self) -> Dict[str, Any]:
        """
        Create and save default config.
        
        Returns copy of default config.
        """
        config = copy.deepcopy(DEFAULT_CONFIG)
        self.save(config)
        return config
