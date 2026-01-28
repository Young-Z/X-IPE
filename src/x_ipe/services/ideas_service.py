"""
FEATURE-008: Workplace (Idea Management)

IdeasService: CRUD operations for idea files and folders
"""
import copy
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class IdeasService:
    """
    Service for managing idea files and folders.
    
    Provides CRUD operations for the x-ipe-docs/ideas/ directory:
    - get_tree(): List all idea folders and files
    - upload(): Upload files to a new idea folder
    - rename_folder(): Rename an idea folder
    """
    
    IDEAS_PATH = 'x-ipe-docs/ideas'
    INVALID_CHARS = r'[/\\:*?"<>|]'
    MAX_NAME_LENGTH = 255
    TOOLBOX_FILE = '.ideation-tools.json'
    DEFAULT_TOOLBOX = {
        "version": "1.0",
        "ideation": {
            "antv-infographic": False,
            "mermaid": True
        },
        "mockup": {
            "frontend-design": True
        },
        "sharing": {}
    }
    
    def __init__(self, project_root: str):
        """
        Initialize IdeasService.
        
        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.ideas_root = self.project_root / self.IDEAS_PATH
    
    def get_tree(self) -> List[Dict]:
        """
        Scan x-ipe-docs/ideas/ and return tree structure.
        Creates x-ipe-docs/ideas/ if it doesn't exist.
        
        Returns:
            List of FileNode dicts representing folder/file structure
        """
        # Create ideas directory if it doesn't exist
        self.ideas_root.mkdir(parents=True, exist_ok=True)
        
        # Build tree structure
        return self._scan_directory(self.ideas_root)
    
    def _scan_directory(self, directory: Path) -> List[Dict]:
        """Recursively scan directory and build tree structure."""
        items = []
        
        try:
            for entry in sorted(directory.iterdir()):
                if entry.name.startswith('.'):
                    continue  # Skip hidden files
                
                relative_path = str(entry.relative_to(self.project_root))
                
                if entry.is_dir():
                    item = {
                        'name': entry.name,
                        'type': 'folder',
                        'path': relative_path,
                        'children': self._scan_directory(entry)
                    }
                else:
                    item = {
                        'name': entry.name,
                        'type': 'file',
                        'path': relative_path
                    }
                
                items.append(item)
        except PermissionError:
            pass  # Skip directories we can't read
        
        return items
    
    def upload(self, files: List[tuple], date: str = None, target_folder: str = None) -> Dict[str, Any]:
        """
        Upload files to a new or existing idea folder.
        
        Args:
            files: List of (filename, content_bytes) tuples
            date: Optional datetime string (MMDDYYYY HHMMSS). Uses now if not provided.
            target_folder: Optional existing folder path to upload into (CR-002)
                          Can be relative to project root (e.g., 'x-ipe-docs/ideas/MyFolder/SubFolder')
                          or relative to ideas root (e.g., 'MyFolder/SubFolder')
        
        Returns:
            Dict with success, folder_name, folder_path, files_uploaded
        """
        if not files:
            return {
                'success': False,
                'error': 'No files provided'
            }
        
        # CR-002: Upload to existing folder if target_folder provided
        if target_folder:
            # Strip 'x-ipe-docs/ideas/' prefix if present (for paths from frontend tree)
            if target_folder.startswith(self.IDEAS_PATH + '/'):
                target_folder = target_folder[len(self.IDEAS_PATH) + 1:]
            elif target_folder.startswith(self.IDEAS_PATH):
                target_folder = target_folder[len(self.IDEAS_PATH):]
            
            folder_path = self.ideas_root / target_folder
            if not folder_path.exists():
                return {
                    'success': False,
                    'error': f"Target folder '{target_folder}' does not exist"
                }
            folder_name = target_folder
        else:
            # Original behavior: create new timestamped folder
            if date is None:
                date = datetime.now().strftime('%m%d%Y %H%M%S')
            
            base_name = f'Draft Idea - {date}'
            folder_name = self._generate_unique_name(base_name)
            
            # Create folder (files go directly in folder, not in subfolder)
            self.ideas_root.mkdir(parents=True, exist_ok=True)
            folder_path = self.ideas_root / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)
        
        # Save files directly to folder
        uploaded_files = []
        for filename, content in files:
            file_path = folder_path / filename
            file_path.write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))
            uploaded_files.append(filename)
        
        return {
            'success': True,
            'folder_name': folder_name,
            'folder_path': f'{self.IDEAS_PATH}/{folder_name}',
            'files_uploaded': uploaded_files
        }
    
    def rename_folder(self, old_name: str, new_name: str) -> Dict[str, Any]:
        """
        Rename an idea folder.
        
        Args:
            old_name: Current folder name (not path)
            new_name: New folder name (not path)
        
        Returns:
            Dict with success, old_name, new_name, new_path or error
        """
        # Strip whitespace
        new_name = new_name.strip()
        
        # Validate new name
        is_valid, error = self._validate_folder_name(new_name)
        if not is_valid:
            return {
                'success': False,
                'error': error
            }
        
        # Check old folder exists
        old_path = self.ideas_root / old_name
        if not old_path.exists():
            return {
                'success': False,
                'error': f'Folder not found: {old_name}'
            }
        
        # Generate unique name if target exists
        final_name = new_name
        if new_name != old_name:
            final_name = self._generate_unique_name(new_name)
        
        # Rename folder
        new_path = self.ideas_root / final_name
        try:
            old_path.rename(new_path)
        except OSError as e:
            return {
                'success': False,
                'error': f'Failed to rename folder: {str(e)}'
            }
        
        return {
            'success': True,
            'old_name': old_name,
            'new_name': final_name,
            'new_path': f'{self.IDEAS_PATH}/{final_name}'
        }
    
    def rename_file(self, file_path: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a file within x-ipe-docs/ideas/.
        
        Args:
            file_path: Relative path from project root (e.g., 'x-ipe-docs/ideas/folder/file.md')
            new_name: New file name (with extension)
        
        Returns:
            Dict with success, old_path, new_path, new_name or error
        """
        new_name = new_name.strip()
        
        if not new_name:
            return {
                'success': False,
                'error': 'File name is required'
            }
        
        if len(new_name) > self.MAX_NAME_LENGTH:
            return {
                'success': False,
                'error': f'File name too long (max {self.MAX_NAME_LENGTH} characters)'
            }
        
        if re.search(self.INVALID_CHARS, new_name):
            return {
                'success': False,
                'error': 'File name contains invalid characters'
            }
        
        # Validate path is within ideas directory
        full_path = self.project_root / file_path
        try:
            full_path = full_path.resolve()
            ideas_root = self.ideas_root.resolve()
            if not str(full_path).startswith(str(ideas_root)):
                return {
                    'success': False,
                    'error': 'Access denied: path outside ideas directory'
                }
        except Exception:
            return {
                'success': False,
                'error': 'Invalid path'
            }
        
        if not full_path.exists():
            return {
                'success': False,
                'error': 'File not found'
            }
        
        if not full_path.is_file():
            return {
                'success': False,
                'error': 'Path is not a file'
            }
        
        # Build new path
        new_path = full_path.parent / new_name
        
        # Check if new name already exists
        if new_path.exists() and new_path != full_path:
            return {
                'success': False,
                'error': f'A file named "{new_name}" already exists'
            }
        
        try:
            full_path.rename(new_path)
        except OSError as e:
            return {
                'success': False,
                'error': f'Failed to rename file: {str(e)}'
            }
        
        # Build relative path for response
        relative_new_path = str(new_path.relative_to(self.project_root))
        
        return {
            'success': True,
            'old_path': file_path,
            'new_path': relative_new_path,
            'new_name': new_name
        }
    
    def _validate_folder_name(self, name: str) -> tuple:
        """
        Validate folder name for filesystem.
        
        Returns:
            Tuple of (is_valid, error_message or None)
        """
        if not name:
            return (False, 'Folder name is required')
        
        if len(name) > self.MAX_NAME_LENGTH:
            return (False, f'Folder name too long (max {self.MAX_NAME_LENGTH} characters)')
        
        if re.search(self.INVALID_CHARS, name):
            return (False, 'Folder name contains invalid characters')
        
        return (True, None)
    
    def _generate_unique_name(self, base_name: str) -> str:
        """
        Generate unique folder name if base_name exists.
        Appends (2), (3), etc. until unique.
        """
        name = base_name
        counter = 2
        
        while (self.ideas_root / name).exists():
            name = f'{base_name} ({counter})'
            counter += 1
        
        return name
    
    def delete_item(self, path: str) -> Dict[str, Any]:
        """
        Delete a file or folder within x-ipe-docs/ideas/.
        
        Args:
            path: Relative path from project root (e.g., 'x-ipe-docs/ideas/folder/file.md')
        
        Returns:
            Dict with success, path, type or error
        """
        if not path:
            return {
                'success': False,
                'error': 'Path is required'
            }
        
        # Validate path is within ideas directory
        full_path = self.project_root / path
        
        try:
            # Resolve to prevent path traversal attacks
            resolved_path = full_path.resolve()
            ideas_resolved = self.ideas_root.resolve()
            
            if not str(resolved_path).startswith(str(ideas_resolved)):
                return {
                    'success': False,
                    'error': 'Path must be within x-ipe-docs/ideas/'
                }
        except Exception:
            return {
                'success': False,
                'error': 'Invalid path'
            }
        
        if not full_path.exists():
            return {
                'success': False,
                'error': f'Path not found: {path}'
            }
        
        item_type = 'folder' if full_path.is_dir() else 'file'
        
        try:
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()
            
            return {
                'success': True,
                'path': path,
                'type': item_type
            }
        except OSError as e:
            return {
                'success': False,
                'error': f'Failed to delete: {str(e)}'
            }
    
    def get_next_version_number(self, folder_path: str, base_name: str = 'idea-summary') -> int:
        """
        Get the next version number for a versioned file.
        
        Args:
            folder_path: Relative path to the idea folder
            base_name: Base name of the file (default: 'idea-summary')
        
        Returns:
            Next version number (1 if no versions exist)
        """
        full_folder = self.project_root / folder_path
        if not full_folder.exists():
            return 1
        
        # Find existing versions
        pattern = re.compile(rf'^{re.escape(base_name)}-v(\d+)\.md$')
        max_version = 0
        
        for item in full_folder.iterdir():
            if item.is_file():
                match = pattern.match(item.name)
                if match:
                    version = int(match.group(1))
                    max_version = max(max_version, version)
        
        return max_version + 1
    
    def create_versioned_summary(self, folder_path: str, content: str, base_name: str = 'idea-summary') -> Dict[str, Any]:
        """
        Create a new versioned idea summary file.
        
        Args:
            folder_path: Relative path to the idea folder (e.g., 'x-ipe-docs/ideas/MyIdea')
            content: Markdown content for the summary
            base_name: Base name of the file (default: 'idea-summary')
        
        Returns:
            Dict with success, file_path, version or error
        """
        full_folder = self.project_root / folder_path
        
        if not full_folder.exists():
            return {
                'success': False,
                'error': f'Folder not found: {folder_path}'
            }
        
        # Validate path is within ideas directory
        try:
            resolved_path = full_folder.resolve()
            ideas_resolved = self.ideas_root.resolve()
            
            if not str(resolved_path).startswith(str(ideas_resolved)):
                return {
                    'success': False,
                    'error': 'Folder must be within x-ipe-docs/ideas/'
                }
        except Exception:
            return {
                'success': False,
                'error': 'Invalid folder path'
            }
        
        # Get next version number
        version = self.get_next_version_number(folder_path, base_name)
        
        # Create the versioned file
        filename = f'{base_name}-v{version}.md'
        file_path = full_folder / filename
        
        try:
            file_path.write_text(content, encoding='utf-8')
            
            return {
                'success': True,
                'file_path': f'{folder_path}/{filename}',
                'version': version,
                'filename': filename
            }
        except OSError as e:
            return {
                'success': False,
                'error': f'Failed to create file: {str(e)}'
            }
    
    def get_toolbox(self) -> Dict:
        """
        Read toolbox configuration from JSON file.
        Returns defaults if file doesn't exist or is invalid.
        
        Returns:
            Dictionary with toolbox configuration
        """
        toolbox_path = self.ideas_root / self.TOOLBOX_FILE
        if toolbox_path.exists():
            try:
                with open(toolbox_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return copy.deepcopy(self.DEFAULT_TOOLBOX)
        return copy.deepcopy(self.DEFAULT_TOOLBOX)
    
    def save_toolbox(self, config: Dict) -> Dict:
        """
        Save toolbox configuration to JSON file.
        Creates ideas directory and file if they don't exist.
        
        Args:
            config: Dictionary with toolbox configuration
            
        Returns:
            Dictionary with success status
        """
        try:
            # Ensure ideas directory exists
            self.ideas_root.mkdir(parents=True, exist_ok=True)
            
            toolbox_path = self.ideas_root / self.TOOLBOX_FILE
            with open(toolbox_path, 'w') as f:
                json.dump(config, f, indent=2)
            return {'success': True}
        except IOError as e:
            return {'success': False, 'error': str(e)}
