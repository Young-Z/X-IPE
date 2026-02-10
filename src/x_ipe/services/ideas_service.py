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

from x_ipe.tracing import x_ipe_tracing


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
            "x-ipe-tool-infographic-syntax": False,
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
    
    @x_ipe_tracing()
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
    
    @x_ipe_tracing()
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
    
    @x_ipe_tracing()
    def create_folder(self, folder_name: str, parent_folder: str = None) -> Dict[str, Any]:
        """
        Create an empty folder in ideas directory.
        
        Args:
            folder_name: Name for the new folder
            parent_folder: Optional parent folder path (relative to ideas root)
        
        Returns:
            Dict with success, folder_name, folder_path or error
        """
        # Validate folder name
        folder_name = folder_name.strip()
        is_valid, error = self._validate_folder_name(folder_name)
        if not is_valid:
            return {
                'success': False,
                'error': error
            }
        
        # Determine base path
        if parent_folder:
            # Strip 'x-ipe-docs/ideas/' prefix if present
            if parent_folder.startswith(self.IDEAS_PATH + '/'):
                parent_folder = parent_folder[len(self.IDEAS_PATH) + 1:]
            elif parent_folder.startswith(self.IDEAS_PATH):
                parent_folder = parent_folder[len(self.IDEAS_PATH):]
            
            base_path = self.ideas_root / parent_folder
            if not base_path.exists():
                return {
                    'success': False,
                    'error': f"Parent folder '{parent_folder}' does not exist"
                }
        else:
            base_path = self.ideas_root
        
        # Ensure ideas root exists
        self.ideas_root.mkdir(parents=True, exist_ok=True)
        
        # Generate unique name if folder exists
        final_name = self._generate_unique_name(folder_name, base_path)
        
        # Create the folder
        folder_path = base_path / final_name
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return {
                'success': False,
                'error': f'Failed to create folder: {str(e)}'
            }
        
        # Build relative path for response
        if parent_folder:
            relative_path = f'{self.IDEAS_PATH}/{parent_folder}/{final_name}'
        else:
            relative_path = f'{self.IDEAS_PATH}/{final_name}'
        
        return {
            'success': True,
            'folder_name': final_name,
            'folder_path': relative_path
        }
    
    @x_ipe_tracing()
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
    
    @x_ipe_tracing()
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
    
    def _generate_unique_name(self, base_name: str, base_path: Path = None) -> str:
        """
        Generate unique folder name if base_name exists.
        Appends (2), (3), etc. until unique.
        
        Args:
            base_name: Base name for the folder
            base_path: Optional base path to check existence (defaults to ideas_root)
        """
        if base_path is None:
            base_path = self.ideas_root
        
        name = base_name
        counter = 2
        
        while (base_path / name).exists():
            name = f'{base_name} ({counter})'
            counter += 1
        
        return name
    
    @x_ipe_tracing()
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
    
    @x_ipe_tracing()
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
    
    @x_ipe_tracing()
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
    
    @x_ipe_tracing()
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
    
    @x_ipe_tracing()
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
    
    # =========================================================================
    # CR-006: Folder Tree UX Enhancement
    # =========================================================================
    
    @x_ipe_tracing()
    def move_item(self, source_path: str, target_folder: str) -> Dict[str, Any]:
        """
        Move file or folder to target folder.
        
        Args:
            source_path: Path (relative to project root or ideas root)
            target_folder: Target folder path (relative to project root or ideas root)
            
        Returns:
            {success: bool, new_path: str, error?: str}
        """
        if not source_path:
            return {'success': False, 'error': 'Source path is required'}
        if target_folder is None:
            return {'success': False, 'error': 'Target folder is required'}
        
        # Normalize source path - handle both x-ipe-docs/ideas/... and relative paths
        if source_path.startswith(self.IDEAS_PATH + '/'):
            source_rel = source_path[len(self.IDEAS_PATH) + 1:]
        elif source_path.startswith(self.IDEAS_PATH):
            source_rel = source_path[len(self.IDEAS_PATH):]
        else:
            source_rel = source_path
        source_full = self.ideas_root / source_rel
        
        # Normalize target path
        if target_folder == '' or target_folder == self.IDEAS_PATH:
            target_full = self.ideas_root
            target_rel = ''
        elif target_folder.startswith(self.IDEAS_PATH + '/'):
            target_rel = target_folder[len(self.IDEAS_PATH) + 1:]
            target_full = self.ideas_root / target_rel
        elif target_folder.startswith(self.IDEAS_PATH):
            target_rel = target_folder[len(self.IDEAS_PATH):]
            target_full = self.ideas_root / target_rel
        else:
            target_rel = target_folder
            target_full = self.ideas_root / target_folder
        
        # Validate source exists
        if not source_full.exists():
            return {'success': False, 'error': f'Source not found: {source_path}'}
        
        # Validate target exists
        if not target_full.exists():
            return {'success': False, 'error': f'Target folder not found: {target_folder}'}
        
        # Validate target is a folder
        if not target_full.is_dir():
            return {'success': False, 'error': 'Target is not a folder'}
        
        # Validate not moving into self or child (use normalized paths)
        if not self.is_valid_drop_target(source_rel, target_rel):
            return {'success': False, 'error': 'Cannot move folder into itself or its children'}
        
        # Determine destination path
        dest_path = target_full / source_full.name
        
        # Handle name collision
        if dest_path.exists():
            dest_path = self._get_unique_path(dest_path)
        
        try:
            shutil.move(str(source_full), str(dest_path))
            # Return path relative to ideas root
            new_path = str(dest_path.relative_to(self.ideas_root))
            return {'success': True, 'new_path': new_path}
        except OSError as e:
            return {'success': False, 'error': f'Failed to move: {str(e)}'}
    
    @x_ipe_tracing()
    def duplicate_item(self, path: str) -> Dict[str, Any]:
        """
        Duplicate file or folder with -copy suffix.
        
        Creates: filename-copy.ext or foldername-copy/
        If exists: filename-copy-2.ext, etc.
        """
        if not path:
            return {'success': False, 'error': 'Path is required'}
        
        # Normalize path
        if path.startswith(self.IDEAS_PATH + '/'):
            path_rel = path[len(self.IDEAS_PATH) + 1:]
        elif path.startswith(self.IDEAS_PATH):
            path_rel = path[len(self.IDEAS_PATH):]
        else:
            path_rel = path
        
        full_path = self.ideas_root / path_rel
        
        if not full_path.exists():
            return {'success': False, 'error': f'Path not found: {path}'}
        
        # Validate path is within ideas directory
        try:
            resolved_path = full_path.resolve()
            ideas_resolved = self.ideas_root.resolve()
            
            if not str(resolved_path).startswith(str(ideas_resolved)):
                return {'success': False, 'error': 'Path must be within x-ipe-docs/ideas/'}
        except Exception:
            return {'success': False, 'error': 'Invalid path'}
        
        # Generate copy name
        if full_path.is_file():
            stem = full_path.stem
            suffix = full_path.suffix
            copy_name = f"{stem}-copy{suffix}"
            copy_path = full_path.parent / copy_name
            
            # Handle collisions
            counter = 2
            while copy_path.exists():
                copy_name = f"{stem}-copy-{counter}{suffix}"
                copy_path = full_path.parent / copy_name
                counter += 1
            
            try:
                shutil.copy2(str(full_path), str(copy_path))
            except OSError as e:
                return {'success': False, 'error': f'Failed to duplicate: {str(e)}'}
        else:
            # Folder
            copy_name = f"{full_path.name}-copy"
            copy_path = full_path.parent / copy_name
            
            # Handle collisions
            counter = 2
            while copy_path.exists():
                copy_name = f"{full_path.name}-copy-{counter}"
                copy_path = full_path.parent / copy_name
                counter += 1
            
            try:
                shutil.copytree(str(full_path), str(copy_path))
            except OSError as e:
                return {'success': False, 'error': f'Failed to duplicate: {str(e)}'}
        
        # Return path relative to ideas root
        new_path = str(copy_path.relative_to(self.ideas_root))
        return {'success': True, 'new_path': new_path}
    
    @x_ipe_tracing()
    def get_folder_contents(self, folder_path: str) -> Dict[str, Any]:
        """
        Get contents of a specific folder for folder view panel.
        
        Args:
            folder_path: Path (relative to project root or ideas root)
            
        Returns:
            {success: bool, items: [...], error?: str}
        """
        # Normalize path
        if not folder_path:
            folder_path_rel = ''
        elif folder_path.startswith(self.IDEAS_PATH + '/'):
            folder_path_rel = folder_path[len(self.IDEAS_PATH) + 1:]
        elif folder_path.startswith(self.IDEAS_PATH):
            folder_path_rel = folder_path[len(self.IDEAS_PATH):]
        else:
            folder_path_rel = folder_path
        
        if folder_path_rel:
            full_path = self.ideas_root / folder_path_rel
        else:
            full_path = self.ideas_root
        
        if not full_path.exists():
            return {'success': False, 'error': f'Folder not found: {folder_path}'}
        
        if not full_path.is_dir():
            return {'success': False, 'error': 'Path is not a folder'}
        
        # Validate path is within ideas directory
        try:
            resolved_path = full_path.resolve()
            ideas_resolved = self.ideas_root.resolve()
            
            if not str(resolved_path).startswith(str(ideas_resolved)):
                return {'success': False, 'error': 'Path must be within x-ipe-docs/ideas/'}
        except Exception:
            return {'success': False, 'error': 'Invalid path'}
        
        items = []
        try:
            for entry in sorted(full_path.iterdir()):
                if entry.name.startswith('.'):
                    continue
                
                # Return path relative to project root (consistent with get_tree)
                relative_path = str(entry.relative_to(self.project_root))
                item = {
                    'name': entry.name,
                    'type': 'folder' if entry.is_dir() else 'file',
                    'path': relative_path
                }
                if entry.is_dir():
                    item['children'] = []  # Lazy load
                items.append(item)
        except PermissionError:
            return {'success': False, 'error': 'Permission denied'}
        
        # Return folder_path relative to project root
        folder_path_result = str(full_path.relative_to(self.project_root)) if full_path != self.ideas_root else self.IDEAS_PATH
        return {'success': True, 'items': items, 'folder_path': folder_path_result}
    
    @x_ipe_tracing()
    def is_valid_drop_target(self, source_path: str, target_folder: str) -> bool:
        """
        Validate that target is not source or child of source.
        
        Args:
            source_path: Path of item being dragged (relative to ideas root)
            target_folder: Path of drop target folder (relative to ideas root)
        """
        if not source_path:
            return False
        
        # Normalize paths (remove x-ipe-docs/ideas/ prefix if present)
        if source_path.startswith(self.IDEAS_PATH + '/'):
            source_norm = source_path[len(self.IDEAS_PATH) + 1:].rstrip('/')
        elif source_path.startswith(self.IDEAS_PATH):
            source_norm = source_path[len(self.IDEAS_PATH):].lstrip('/').rstrip('/')
        else:
            source_norm = source_path.rstrip('/')
        
        if not target_folder:
            return True  # Root is always valid
        
        if target_folder.startswith(self.IDEAS_PATH + '/'):
            target_norm = target_folder[len(self.IDEAS_PATH) + 1:].rstrip('/')
        elif target_folder.startswith(self.IDEAS_PATH):
            target_norm = target_folder[len(self.IDEAS_PATH):].lstrip('/').rstrip('/')
        else:
            target_norm = target_folder.rstrip('/')
        
        # Cannot drop onto self
        if source_norm == target_norm:
            return False
        
        # Check if source is a folder
        source_full = self.ideas_root / source_norm
        if not source_full.exists() or not source_full.is_dir():
            return True  # Files can be dropped anywhere, non-existent is handled elsewhere
        
        # Cannot drop folder into its own children
        if target_norm.startswith(source_norm + '/'):
            return False
        
        return True
    
    @x_ipe_tracing()
    def filter_tree(self, query: str) -> List[Dict]:
        """
        Filter tree by search query, returning matching items with parent context.
        
        Args:
            query: Search string to match against item names
            
        Returns:
            Flat list of matching items and their parent folders
        """
        if not query or not query.strip():
            return self.get_tree()
        
        query_lower = query.lower().strip()
        tree = self.get_tree()
        
        # Collect all matching items plus their parents
        results = []
        self._collect_matches(tree, query_lower, results)
        return results
    
    def _collect_matches(self, items: List[Dict], query: str, results: List[Dict], include_all: bool = False) -> bool:
        """Recursively collect matching items and parents into flat results list.
        
        Returns True if any child matches (to include parent in results).
        """
        any_match = False
        
        for item in items:
            item_copy = copy.copy(item)
            name_matches = query in item['name'].lower()
            
            if item['type'] == 'folder' and 'children' in item:
                # Check if any children match
                child_results = []
                has_child_match = self._collect_matches(item['children'], query, child_results, include_all=name_matches)
                
                if name_matches or has_child_match:
                    item_copy['_matches'] = name_matches
                    item_copy['children'] = []  # Don't include nested children in flat result
                    results.append(item_copy)
                    results.extend(child_results)
                    any_match = True
            else:
                # File - include if name matches or parent matched
                if name_matches or include_all:
                    item_copy['_matches'] = name_matches
                    results.append(item_copy)
                    if name_matches:
                        any_match = True
        
        return any_match
    
    @x_ipe_tracing()
    def get_download_info(self, path: str) -> Dict[str, Any]:
        """
        Get file content and mime type for download.
        
        Args:
            path: Path (relative to project root or ideas root)
            
        Returns:
            {success: bool, content: bytes, filename: str, mime_type: str}
        """
        if not path:
            return {'success': False, 'error': 'Path is required'}
        
        # Normalize path
        if path.startswith(self.IDEAS_PATH + '/'):
            path_rel = path[len(self.IDEAS_PATH) + 1:]
        elif path.startswith(self.IDEAS_PATH):
            path_rel = path[len(self.IDEAS_PATH):]
        else:
            path_rel = path
        
        full_path = self.ideas_root / path_rel
        
        if not full_path.exists():
            return {'success': False, 'error': f'File not found: {path}'}
        
        if not full_path.is_file():
            return {'success': False, 'error': 'Cannot download a folder'}
        
        # Validate path is within ideas directory
        try:
            resolved_path = full_path.resolve()
            ideas_resolved = self.ideas_root.resolve()
            
            if not str(resolved_path).startswith(str(ideas_resolved)):
                return {'success': False, 'error': 'Path must be within x-ipe-docs/ideas/'}
        except Exception:
            return {'success': False, 'error': 'Invalid path'}
        
        # Determine mime type
        suffix = full_path.suffix.lower()
        mime_types = {
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.html': 'text/html',
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
        }
        mime_type = mime_types.get(suffix, 'application/octet-stream')
        
        try:
            content = full_path.read_bytes()
            # For text files, decode to string for easier testing
            text_types = ['.md', '.txt', '.json', '.html', '.css', '.js']
            if suffix in text_types:
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    pass  # Keep as bytes if decode fails
            return {
                'success': True,
                'content': content,
                'filename': full_path.name,
                'mime_type': mime_type
            }
        except OSError as e:
            return {'success': False, 'error': f'Failed to read file: {str(e)}'}
    
    @x_ipe_tracing()
    def get_delete_info(self, path: str) -> Dict[str, Any]:
        """
        Get item info for delete confirmation dialog.
        
        Returns item type and count of children for folders.
        """
        if not path:
            return {'success': False, 'error': 'Path is required'}
        
        # Normalize path
        if path.startswith(self.IDEAS_PATH + '/'):
            path_rel = path[len(self.IDEAS_PATH) + 1:]
        elif path.startswith(self.IDEAS_PATH):
            path_rel = path[len(self.IDEAS_PATH):]
        else:
            path_rel = path
        
        full_path = self.ideas_root / path_rel
        
        if not full_path.exists():
            return {'success': False, 'error': f'Path not found: {path}'}
        
        item_type = 'folder' if full_path.is_dir() else 'file'
        item_count = 1
        
        if full_path.is_dir():
            # Count all items recursively
            item_count = sum(1 for _ in full_path.rglob('*') if not _.name.startswith('.'))
        
        return {
            'success': True,
            'path': path,
            'name': full_path.name,
            'type': item_type,
            'item_count': item_count
        }
    
    def _get_unique_path(self, path: Path) -> Path:
        """Generate unique path if target exists."""
        if not path.exists():
            return path
        
        parent = path.parent
        if path.is_file() or not path.exists():
            stem = path.stem
            suffix = path.suffix
            counter = 2
            while True:
                new_name = f"{stem}-{counter}{suffix}"
                new_path = parent / new_name
                if not new_path.exists():
                    return new_path
                counter += 1
        else:
            name = path.name
            counter = 2
            while True:
                new_name = f"{name}-{counter}"
                new_path = parent / new_name
                if not new_path.exists():
                    return new_path
                counter += 1
