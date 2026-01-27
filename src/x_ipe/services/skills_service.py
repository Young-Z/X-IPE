"""
Skills Service: Read skills from .github/skills/ directory
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class SkillsService:
    """
    Service to read skill definitions from .github/skills/ directory.
    
    Each skill is a folder containing a SKILL.md file with YAML frontmatter
    containing 'name' and 'description' fields.
    """
    
    SKILLS_PATH = '.github/skills'
    
    def __init__(self, project_root: str):
        """
        Initialize SkillsService.
        
        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.skills_dir = self.project_root / self.SKILLS_PATH
    
    def get_all(self) -> List[Dict[str, str]]:
        """
        Get all skills with their name and description.
        
        Returns:
            List of dicts with 'name' and 'description' keys
        """
        skills = []
        
        if not self.skills_dir.exists():
            return skills
        
        for item in sorted(self.skills_dir.iterdir()):
            if item.is_dir():
                skill_md = item / 'SKILL.md'
                if skill_md.exists():
                    skill_info = self._parse_skill_md(skill_md)
                    if skill_info:
                        skills.append(skill_info)
        
        return skills
    
    def _parse_skill_md(self, skill_md_path: Path) -> Optional[Dict[str, str]]:
        """
        Parse SKILL.md file to extract name and description from frontmatter.
        
        Args:
            skill_md_path: Path to SKILL.md file
            
        Returns:
            Dict with 'name' and 'description' or None if parsing fails
        """
        try:
            content = skill_md_path.read_text(encoding='utf-8')
            
            # Check for YAML frontmatter
            if not content.startswith('---'):
                return None
            
            # Find end of frontmatter
            end_index = content.find('---', 3)
            if end_index == -1:
                return None
            
            frontmatter = content[3:end_index].strip()
            data = yaml.safe_load(frontmatter)
            
            if not isinstance(data, dict):
                return None
            
            name = data.get('name', '')
            description = data.get('description', '')
            
            if name:
                return {
                    'name': name,
                    'description': description
                }
            
            return None
            
        except Exception:
            return None
