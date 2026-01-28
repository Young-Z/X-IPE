"""
FEATURE-022-D: UI/UX Feedback Service

Handles saving feedback entries to the file system.
"""
import base64
from pathlib import Path
from datetime import datetime


class UiuxFeedbackService:
    """Service for saving UI/UX feedback to file system"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.feedback_dir = self.project_root / 'x-ipe-docs' / 'uiux-feedback'
    
    def save_feedback(self, data: dict) -> dict:
        """
        Save feedback entry to file system.
        
        Args:
            data: dict with keys: name, url, elements, screenshot (optional), description (optional)
        
        Returns:
            dict with success, folder, name (or error on failure)
        """
        try:
            # Get unique folder name
            folder_name = self._get_unique_folder_name(data['name'])
            folder_path = self.feedback_dir / folder_name
            
            # Create folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Save feedback.md
            self._save_feedback_md(folder_path, data)
            
            # Save screenshot if present
            if data.get('screenshot'):
                self._save_screenshot(folder_path, data['screenshot'])
            
            return {
                'success': True,
                'folder': str(folder_path.relative_to(self.project_root)),
                'name': folder_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_unique_folder_name(self, name: str) -> str:
        """
        Get unique folder name, appending suffix if folder exists.
        
        Args:
            name: Base folder name
        
        Returns:
            Unique folder name (base or with -1, -2, etc.)
        """
        base_name = name
        folder_path = self.feedback_dir / base_name
        
        if not folder_path.exists():
            return base_name
        
        # Append suffix
        counter = 1
        while True:
            new_name = f"{base_name}-{counter}"
            if not (self.feedback_dir / new_name).exists():
                return new_name
            counter += 1
    
    def _save_feedback_md(self, folder_path: Path, data: dict) -> None:
        """
        Generate and save feedback.md file.
        
        Args:
            folder_path: Path to feedback folder
            data: Feedback data dict
        """
        now = datetime.now()
        
        # Build elements list
        elements_md = '\n'.join([f"- `{el}`" for el in data.get('elements', [])])
        
        # Build screenshot section
        screenshot_md = ''
        if data.get('screenshot'):
            screenshot_md = '\n## Screenshot\n\n![Screenshot](./page-screenshot.png)'
        
        # Build feedback section
        feedback_text = data.get('description', '').strip()
        if not feedback_text:
            feedback_text = '_No description provided_'
        
        content = f"""# UI/UX Feedback

**ID:** {data['name']}
**URL:** {data['url']}
**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}

## Selected Elements

{elements_md}

## Feedback

{feedback_text}
{screenshot_md}
"""
        
        (folder_path / 'feedback.md').write_text(content, encoding='utf-8')
    
    def _save_screenshot(self, folder_path: Path, base64_data: str) -> None:
        """
        Decode and save screenshot PNG.
        
        Args:
            folder_path: Path to feedback folder
            base64_data: Base64-encoded PNG data (with or without data URL prefix)
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode and save
            image_data = base64.b64decode(base64_data)
            (folder_path / 'page-screenshot.png').write_bytes(image_data)
        except Exception as e:
            # Log warning but don't fail
            print(f"Warning: Failed to save screenshot: {e}")
