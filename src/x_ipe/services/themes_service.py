"""
FEATURE-012: Design Themes

ThemesService: Discovery, parsing, and metadata extraction for themes

Manages themes stored in x-ipe-docs/themes/theme-*/ folders.
Each theme must have design-system.md (required) and component-visualization.html (optional).
"""
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


THEMES_DIR = 'x-ipe-docs/themes'
THEME_PREFIX = 'theme-'
REQUIRED_FILE = 'design-system.md'
VISUALIZATION_FILE = 'component-visualization.html'

# Fallback colors when parsing fails
FALLBACK_COLORS = {
    'primary': '#1a1a2e',
    'secondary': '#4a4a6a',
    'accent': '#10b981',
    'neutral': '#e5e7eb'
}


class ThemesService:
    """
    Service for discovering and parsing themes.
    
    FEATURE-012: Design Themes
    
    Themes are stored in x-ipe-docs/themes/theme-{name}/ directories.
    Each theme must have a design-system.md file for validation.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize ThemesService.
        
        Args:
            project_root: Absolute or relative path to the project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.themes_dir = self.project_root / THEMES_DIR
    
    def list_themes(self) -> List[Dict[str, Any]]:
        """
        List all valid themes with metadata.
        
        Scans x-ipe-docs/themes/theme-*/ folders for themes.
        A theme is valid if it has design-system.md file.
        
        Returns:
            List of theme metadata dictionaries with:
            - name: Theme folder name (e.g., "theme-default")
            - description: First paragraph from design-system.md
            - colors: Dict with primary, secondary, accent, neutral hex values
            - files: List of files in theme folder
            - path: Relative path to theme folder
        """
        if not self.themes_dir.exists():
            return []
        
        themes = []
        for entry in sorted(self.themes_dir.iterdir()):
            # Only scan theme-prefixed folders
            if not entry.is_dir() or not entry.name.startswith(THEME_PREFIX):
                continue
            
            # Validate theme has required file
            design_system = entry / REQUIRED_FILE
            if not design_system.exists():
                continue
            
            # Read design system content
            try:
                content = design_system.read_text(encoding='utf-8')
            except (IOError, UnicodeDecodeError):
                continue
            
            # Build metadata
            files = [f.name for f in entry.iterdir() if f.is_file()]
            themes.append({
                'name': entry.name,
                'description': self._extract_description(content),
                'colors': self._parse_color_tokens(content),
                'files': sorted(files),
                'path': str(entry.relative_to(self.project_root))
            })
        
        return themes
    
    def get_theme(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific theme.
        
        Args:
            name: Theme folder name (e.g., "theme-default")
            
        Returns:
            Theme detail dictionary with all metadata plus:
            - design_system: Full content of design-system.md
            - visualization_path: Path to component-visualization.html (if exists)
            
            Returns None if theme doesn't exist or is invalid.
        """
        theme_path = self.themes_dir / name
        
        # Validate theme exists and has required file
        if not theme_path.exists() or not theme_path.is_dir():
            return None
        
        design_system = theme_path / REQUIRED_FILE
        if not design_system.exists():
            return None
        
        # Read design system content
        try:
            content = design_system.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError):
            return None
        
        # Build detail dict
        files = [f.name for f in theme_path.iterdir() if f.is_file()]
        relative_path = str(theme_path.relative_to(self.project_root))
        
        result = {
            'name': name,
            'description': self._extract_description(content),
            'colors': self._parse_color_tokens(content),
            'files': sorted(files),
            'path': relative_path,
            'design_system': content,
        }
        
        # Add visualization path if it exists
        visualization = theme_path / VISUALIZATION_FILE
        if visualization.exists():
            result['visualization_path'] = f"{relative_path}/{VISUALIZATION_FILE}"
        
        return result
    
    def _parse_color_tokens(self, content: str) -> Dict[str, str]:
        """
        Extract first 4 hex colors from design-system.md.
        
        Looks for patterns like: #0f172a, #fff, #10b981
        
        Args:
            content: Markdown content to parse
            
        Returns:
            Dict with primary, secondary, accent, neutral hex values.
            Uses fallback colors if fewer than 4 colors found.
        """
        # Match 6-digit and 3-digit hex colors
        pattern = r'#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}\b'
        matches = re.findall(pattern, content)
        
        # Map to color roles
        colors = {
            'primary': matches[0] if len(matches) > 0 else FALLBACK_COLORS['primary'],
            'secondary': matches[1] if len(matches) > 1 else FALLBACK_COLORS['secondary'],
            'accent': matches[2] if len(matches) > 2 else FALLBACK_COLORS['accent'],
            'neutral': matches[3] if len(matches) > 3 else FALLBACK_COLORS['neutral']
        }
        return colors
    
    def _extract_description(self, content: str) -> str:
        """
        Extract first paragraph from design-system.md as description.
        
        Skips headers and empty lines, returns first non-header paragraph.
        
        Args:
            content: Markdown content to parse
            
        Returns:
            First paragraph text, or empty string if none found.
        """
        if not content:
            return ''
        
        lines = content.split('\n')
        paragraph_lines = []
        in_paragraph = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines before paragraph
            if not stripped and not in_paragraph:
                continue
            
            # Skip headers
            if stripped.startswith('#'):
                if in_paragraph:
                    break  # End paragraph on next header
                continue
            
            # Collect paragraph lines
            if stripped:
                in_paragraph = True
                paragraph_lines.append(stripped)
            elif in_paragraph:
                break  # End paragraph on empty line
        
        return ' '.join(paragraph_lines)
