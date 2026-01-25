"""Skills module for X-IPE skill discovery and management."""
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json
import shutil
from datetime import datetime

from .hashing import hash_directory


@dataclass
class SkillInfo:
    """Information about a skill."""
    name: str
    path: Path
    source: str  # "package" or "local"
    hash: str
    modified: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "path": str(self.path),
            "source": self.source,
            "hash": self.hash,
            "modified": self.modified,
        }


class SkillsManager:
    """Manages skill discovery and synchronization."""
    
    def __init__(self, project_root: Path, package_skills_path: Optional[Path] = None):
        """Initialize SkillsManager.
        
        Args:
            project_root: Path to the project root directory.
            package_skills_path: Path to package skills. If None, auto-detect.
        """
        self.project_root = Path(project_root).resolve()
        self.local_skills_path = self.project_root / ".github" / "skills"
        self.runtime_path = self.project_root / ".x-ipe"
        self.hash_file = self.runtime_path / "skill-hashes.json"
        
        # Package skills path (where bundled skills live)
        if package_skills_path is None:
            self.package_skills_path = self._find_package_skills()
        else:
            self.package_skills_path = Path(package_skills_path).resolve()
        
        self._cached_hashes: Dict[str, str] = {}
        self._load_cached_hashes()
    
    def _find_package_skills(self) -> Optional[Path]:
        """Find package skills path."""
        try:
            from importlib import resources
            skills_ref = resources.files("x_ipe") / "skills"
            if hasattr(skills_ref, 'is_dir') and skills_ref.is_dir():
                return Path(str(skills_ref))
        except (ImportError, TypeError, AttributeError):
            pass
        
        # Fall back to src layout for development
        dev_path = Path(__file__).parent.parent / "skills"
        if dev_path.exists():
            return dev_path
        
        return None
    
    def _load_cached_hashes(self) -> None:
        """Load cached skill hashes from disk."""
        if self.hash_file.exists():
            try:
                self._cached_hashes = json.loads(self.hash_file.read_text())
            except (json.JSONDecodeError, IOError):
                self._cached_hashes = {}
    
    def _save_cached_hashes(self) -> None:
        """Save skill hashes to disk."""
        self.runtime_path.mkdir(parents=True, exist_ok=True)
        self.hash_file.write_text(json.dumps(self._cached_hashes, indent=2))
    
    def get_package_skills(self) -> List[SkillInfo]:
        """Get skills bundled in the package.
        
        Returns:
            List of SkillInfo for package skills.
        """
        if self.package_skills_path is None or not self.package_skills_path.exists():
            return []
        
        skills = []
        for skill_dir in self.package_skills_path.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_hash = hash_directory(skill_dir)
                skills.append(SkillInfo(
                    name=skill_dir.name,
                    path=skill_dir,
                    source="package",
                    hash=skill_hash,
                ))
        
        return sorted(skills, key=lambda s: s.name)
    
    def get_local_skills(self) -> List[SkillInfo]:
        """Get skills from local project.
        
        Returns:
            List of SkillInfo for local skills.
        """
        if not self.local_skills_path.exists():
            return []
        
        skills = []
        for skill_dir in self.local_skills_path.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_hash = hash_directory(skill_dir)
                
                # Check if modified from package version
                cached_hash = self._cached_hashes.get(skill_dir.name)
                modified = cached_hash is not None and cached_hash != skill_hash
                
                skills.append(SkillInfo(
                    name=skill_dir.name,
                    path=skill_dir,
                    source="local",
                    hash=skill_hash,
                    modified=modified,
                ))
        
        return sorted(skills, key=lambda s: s.name)
    
    def get_merged_skills(self) -> List[SkillInfo]:
        """Get merged view of package and local skills.
        
        Local skills override package skills of the same name.
        
        Returns:
            List of SkillInfo with local overriding package.
        """
        skills_map: Dict[str, SkillInfo] = {}
        
        # Add package skills first
        for skill in self.get_package_skills():
            skills_map[skill.name] = skill
        
        # Local skills override package skills
        for skill in self.get_local_skills():
            skills_map[skill.name] = skill
        
        return sorted(skills_map.values(), key=lambda s: s.name)
    
    def detect_modifications(self) -> List[SkillInfo]:
        """Detect skills that have been modified from package version.
        
        Returns:
            List of SkillInfo for modified skills.
        """
        return [s for s in self.get_local_skills() if s.modified]
    
    def sync_from_package(self, skill_name: Optional[str] = None, 
                          backup: bool = True) -> List[str]:
        """Sync skills from package to local.
        
        Args:
            skill_name: Specific skill to sync. If None, sync all.
            backup: If True, backup existing skills before overwriting.
            
        Returns:
            List of synced skill names.
        """
        if self.package_skills_path is None or not self.package_skills_path.exists():
            return []
        
        synced = []
        package_skills = self.get_package_skills()
        
        for skill in package_skills:
            if skill_name is not None and skill.name != skill_name:
                continue
            
            target = self.local_skills_path / skill.name
            
            # Backup if exists and requested
            if target.exists() and backup:
                self.backup_skill(skill.name)
            
            # Copy skill
            self.local_skills_path.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(skill.path, target)
            
            # Update hash cache
            self._cached_hashes[skill.name] = skill.hash
            synced.append(skill.name)
        
        if synced:
            self._save_cached_hashes()
        
        return synced
    
    def backup_skill(self, skill_name: str) -> Optional[Path]:
        """Create backup of a local skill.
        
        Args:
            skill_name: Name of skill to backup.
            
        Returns:
            Path to backup, or None if skill doesn't exist.
        """
        skill_path = self.local_skills_path / skill_name
        if not skill_path.exists():
            return None
        
        backup_dir = self.runtime_path / "backups" / skill_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / timestamp
        
        shutil.copytree(skill_path, backup_path)
        return backup_path
    
    def get_skill_info(self, skill_name: str) -> Optional[SkillInfo]:
        """Get info for a specific skill.
        
        Args:
            skill_name: Name of the skill.
            
        Returns:
            SkillInfo or None if not found.
        """
        for skill in self.get_merged_skills():
            if skill.name == skill_name:
                return skill
        return None
    
    def calculate_skill_hash(self, skill_path: Path) -> str:
        """Calculate hash for a skill directory.
        
        Args:
            skill_path: Path to skill directory.
            
        Returns:
            SHA-256 hash string.
        """
        return hash_directory(skill_path)
