"""
Services for Document Viewer Application

FEATURE-001: Project Navigation
- ProjectService: Scans project directory and returns structure
- FileWatcher: Monitors file system changes and emits WebSocket events

FEATURE-005: Interactive Console v4.0
- OutputBuffer: Circular buffer for terminal output (10KB)
- PersistentSession: PTY wrapper with session persistence
- SessionManager: Session lifecycle management
- PTYSession: PTY process wrapper

FEATURE-008: Workplace (Idea Management)
- IdeasService: CRUD operations for idea files and folders

FEATURE-010: Project Root Configuration
- ConfigData: Data class for resolved config values
- ConfigService: Discovery, parsing, validation of .x-ipe.yaml
"""
import os
import threading
import time
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


# ============================================================================
# FEATURE-010: Project Root Configuration
# ============================================================================

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
        if not paths.get('x_ipe_app'):
            self._error = "Missing required field: paths.x_ipe_app"
            return None
        
        # Resolve paths relative to config file location
        project_root = (config_dir / paths['project_root']).resolve()
        x_ipe_app = (config_dir / paths['x_ipe_app']).resolve()
        
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


# ============================================================================
# FEATURE-001: Project Navigation
# ============================================================================


@dataclass
class FileNode:
    """Represents a file or folder in the project structure"""
    name: str
    type: str  # 'file' or 'folder'
    path: str
    children: Optional[List['FileNode']] = None
    mtime: Optional[float] = None  # Modification time for files (FEATURE-009 bug fix)

    def to_dict(self) -> Dict:
        result = {
            'name': self.name,
            'type': self.type,
            'path': self.path
        }
        if self.children is not None:
            result['children'] = [c.to_dict() for c in self.children]
        if self.mtime is not None:
            result['mtime'] = self.mtime
        return result


@dataclass
class Section:
    """Represents a top-level section in the sidebar"""
    id: str
    label: str
    path: str
    icon: str
    children: List[FileNode]
    exists: bool = True

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'label': self.label,
            'path': self.path,
            'icon': self.icon,
            'children': [c.to_dict() for c in self.children],
            'exists': self.exists
        }


class ProjectService:
    """
    Service to scan and return project folder structure.
    
    Maps three fixed sections to project directories:
    - Project Plan -> docs/planning/
    - Requirements -> docs/requirements/
    - Code -> src/
    """

    # Default section configuration
    DEFAULT_SECTIONS = [
        {
            'id': 'workplace',
            'label': 'Workplace',
            'path': 'docs/ideas',
            'icon': 'bi-lightbulb'
        },
        {
            'id': 'planning',
            'label': 'Project Plan',
            'path': 'docs/planning',
            'icon': 'bi-kanban'
        },
        {
            'id': 'requirements',
            'label': 'Requirements',
            'path': 'docs/requirements',
            'icon': 'bi-file-text'
        },
        {
            'id': 'code',
            'label': 'Code',
            'path': 'src',
            'icon': 'bi-code-slash'
        }
    ]

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.md', '.txt', '.json', '.yaml', '.yml',  # Documents
        '.py', '.js', '.ts', '.html', '.css', '.jsx', '.tsx'  # Code
    }

    def __init__(self, project_root: str, sections: Optional[List[Dict]] = None):
        """
        Initialize ProjectService.
        
        Args:
            project_root: Absolute path to the project root directory
            sections: Optional custom section configuration
        """
        self.project_root = Path(project_root).resolve()
        self.sections_config = sections or self.DEFAULT_SECTIONS

    def get_structure(self) -> Dict[str, Any]:
        """
        Get the complete project structure for sidebar navigation.
        
        Returns:
            Dict with 'project_root' and 'sections' containing the tree structure
        """
        sections = []
        
        for section_config in self.sections_config:
            section_path = self.project_root / section_config['path']
            
            if section_path.exists() and section_path.is_dir():
                children = self._scan_directory(section_path, section_config['path'])
                exists = True
            else:
                children = []
                exists = False
            
            section = Section(
                id=section_config['id'],
                label=section_config['label'],
                path=section_config['path'],
                icon=section_config['icon'],
                children=children,
                exists=exists
            )
            sections.append(section.to_dict())
        
        return {
            'project_root': str(self.project_root),
            'sections': sections
        }

    def _scan_directory(self, directory: Path, relative_base: str) -> List[FileNode]:
        """
        Recursively scan a directory and build file tree.
        
        Args:
            directory: Absolute path to directory to scan
            relative_base: Relative path from project root for building paths
            
        Returns:
            List of FileNode objects representing directory contents
        """
        items = []
        
        try:
            entries = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return items
        
        for entry in entries:
            # Skip hidden files and directories
            if entry.name.startswith('.'):
                continue
            
            relative_path = f"{relative_base}/{entry.name}"
            
            if entry.is_dir():
                children = self._scan_directory(entry, relative_path)
                node = FileNode(
                    name=entry.name,
                    type='folder',
                    path=relative_path,
                    children=children
                )
                items.append(node)
            elif entry.is_file():
                # Only include supported file types
                if entry.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    # Include mtime for content change detection (FEATURE-009 bug fix)
                    mtime = entry.stat().st_mtime
                    node = FileNode(
                        name=entry.name,
                        type='file',
                        path=relative_path,
                        mtime=mtime
                    )
                    items.append(node)
        
        return items


class FileWatcherHandler(FileSystemEventHandler):
    """Handler for file system events with debouncing and gitignore support"""

    def __init__(self, callback, debounce_seconds: float = 0.1, ignore_patterns: List[str] = None, project_root: str = None):
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.ignore_patterns = ignore_patterns or []
        self.project_root = Path(project_root) if project_root else None
        self._pending_events: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None

    def _should_ignore(self, path: str) -> bool:
        """Check if path matches any gitignore pattern."""
        if not self.ignore_patterns:
            return False
        
        # Get relative path from project root
        try:
            if self.project_root:
                rel_path = Path(path).relative_to(self.project_root)
            else:
                rel_path = Path(path)
        except ValueError:
            rel_path = Path(path)
        
        path_str = str(rel_path)
        path_parts = rel_path.parts
        
        for pattern in self.ignore_patterns:
            # Strip trailing slash for directory patterns
            clean_pattern = pattern.rstrip('/')
            
            # Check if any part of the path matches the pattern
            for part in path_parts:
                if part == clean_pattern:
                    return True
            
            # Also check if path starts with the pattern
            if path_str.startswith(clean_pattern + '/') or path_str == clean_pattern:
                return True
        
        return False

    def _schedule_callback(self):
        """Schedule debounced callback"""
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._emit_events)
            self._timer.start()

    def _emit_events(self):
        """Emit all pending events"""
        with self._lock:
            events = list(self._pending_events.values())
            self._pending_events.clear()
        
        for event in events:
            self.callback(event)

    def _add_event(self, event_type: str, src_path: str):
        """Add event to pending queue if not ignored"""
        # Skip if path matches gitignore pattern
        if self._should_ignore(src_path):
            return
        
        with self._lock:
            self._pending_events[src_path] = {
                'type': 'structure_changed',
                'action': event_type,
                'path': src_path
            }
        self._schedule_callback()

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self._add_event('created', event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            self._add_event('deleted', event.src_path)

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self._add_event('modified', event.src_path)

    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory:
            self._add_event('deleted', event.src_path)
            self._add_event('created', event.dest_path)


class FileWatcher:
    """
    Watches project directories for changes and emits WebSocket events.
    
    Uses watchdog library for cross-platform file system monitoring.
    Respects .gitignore patterns to avoid monitoring ignored directories.
    """

    def __init__(self, project_root: str, socketio=None, debounce_seconds: float = 0.1):
        """
        Initialize FileWatcher.
        
        Args:
            project_root: Absolute path to the project root directory
            socketio: Flask-SocketIO instance for emitting events
            debounce_seconds: Debounce time for rapid file changes
        """
        self.project_root = Path(project_root).resolve()
        self.socketio = socketio
        self.debounce_seconds = debounce_seconds
        self.observer: Optional[Observer] = None
        self._running = False
        self.ignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> List[str]:
        """Load and parse .gitignore patterns."""
        gitignore_path = self.project_root / '.gitignore'
        patterns = []
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception:
                pass  # Ignore read errors
        
        return patterns

    def _emit_event(self, event_data: Dict):
        """Emit file system event via WebSocket"""
        if self.socketio:
            # Convert absolute path to relative
            try:
                abs_path = Path(event_data['path'])
                rel_path = abs_path.relative_to(self.project_root)
                event_data['path'] = str(rel_path)
            except ValueError:
                pass  # Keep original path if not relative to project root
            
            # Emit structure_changed for sidebar updates (FEATURE-001)
            self.socketio.emit('structure_changed', event_data)
            
            # Emit content_changed for live refresh (FEATURE-004)
            content_event = {
                'type': 'content_changed',
                'path': event_data['path'],
                'action': event_data.get('action', 'modified')
            }
            self.socketio.emit('content_changed', content_event)

    def start(self):
        """Start watching project directories"""
        if self._running:
            return
        
        handler = FileWatcherHandler(
            self._emit_event, 
            self.debounce_seconds,
            ignore_patterns=self.ignore_patterns,
            project_root=str(self.project_root)
        )
        self.observer = Observer()
        
        # Watch the entire project root
        self.observer.schedule(handler, str(self.project_root), recursive=True)
        self.observer.start()
        self._running = True

    def stop(self):
        """Stop watching"""
        if self.observer and self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False

    @property
    def is_running(self) -> bool:
        return self._running


class ContentService:
    """
    Service for reading file content and detecting file types.
    
    Provides file content with metadata for rendering in the viewer.
    """

    # File extension to type mappings
    FILE_TYPES = {
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.txt': 'text',
    }

    def __init__(self, project_root: str):
        """
        Initialize ContentService.
        
        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root).resolve()

    def detect_file_type(self, extension: str) -> str:
        """
        Detect file type from extension.
        
        Args:
            extension: File extension including dot (e.g., '.py')
            
        Returns:
            File type string for syntax highlighting
        """
        return self.FILE_TYPES.get(extension.lower(), 'text')

    def get_content(self, relative_path: str) -> Dict[str, Any]:
        """
        Get file content with metadata.
        
        Args:
            relative_path: Path relative to project root
            
        Returns:
            Dict with content, path, type, extension, size
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If path is outside project root
        """
        # Construct full path
        full_path = (self.project_root / relative_path).resolve()
        
        # Security check: ensure path is within project root
        if not str(full_path).startswith(str(self.project_root)):
            raise PermissionError("Access denied: path outside project root")
        
        # Check file exists
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        
        # Read content
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get file info
        extension = full_path.suffix
        file_type = self.detect_file_type(extension)
        size = full_path.stat().st_size
        
        return {
            'path': relative_path,
            'content': content,
            'type': file_type,
            'extension': extension,
            'size': size
        }

    def _validate_path_for_write(self, relative_path: str) -> tuple:
        """
        Validate a path for write operations.
        
        Args:
            relative_path: Path relative to project root
            
        Returns:
            Tuple of (is_valid, full_path or error_message)
        """
        # Check empty path
        if not relative_path or not relative_path.strip():
            return (False, "Path is required")
        
        # Check for path traversal attempts
        if '..' in relative_path:
            return (False, "Path traversal not allowed")
        
        # Check for absolute paths
        if relative_path.startswith('/') or (len(relative_path) > 1 and relative_path[1] == ':'):
            return (False, "Invalid path: absolute paths not allowed")
        
        # Check for null bytes
        if '\x00' in relative_path:
            return (False, "Invalid path: null bytes not allowed")
        
        # Construct full path
        try:
            full_path = (self.project_root / relative_path).resolve()
        except Exception:
            return (False, "Invalid path")
        
        # Security check: ensure resolved path is within project root
        if not str(full_path).startswith(str(self.project_root)):
            return (False, "Invalid path: outside project root")
        
        # Check file exists (v1.0: no create new files)
        try:
            if not full_path.exists():
                return (False, "File not found")
        except OSError:
            # Path too long or other OS-level issues
            return (False, "Invalid path")
        
        # Check it's not a directory
        if full_path.is_dir():
            return (False, "Cannot write to directory")
        
        # Check for symlinks pointing outside project
        if full_path.is_symlink():
            real_path = full_path.resolve()
            if not str(real_path).startswith(str(self.project_root)):
                return (False, "Invalid path: symlink outside project root")
        
        return (True, full_path)

    def save_content(self, relative_path: str, content: str) -> Dict[str, Any]:
        """
        Save content to a file.
        
        Args:
            relative_path: Path relative to project root
            content: Content to write to the file
            
        Returns:
            Dict with success, message, path or error
        """
        # Validate path
        is_valid, result = self._validate_path_for_write(relative_path)
        
        if not is_valid:
            return {
                'success': False,
                'error': result
            }
        
        full_path = result
        
        try:
            # Write content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'message': f'File saved successfully',
                'path': relative_path
            }
        except PermissionError:
            return {
                'success': False,
                'error': 'Permission denied: cannot write to file'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to save file: {str(e)}'
            }


# =============================================================================
# FEATURE-008: Workplace (Idea Management)
# IdeasService for managing idea files and folders
# =============================================================================

import re

class IdeasService:
    """
    Service for managing idea files and folders.
    
    Provides CRUD operations for the docs/ideas/ directory:
    - get_tree(): List all idea folders and files
    - upload(): Upload files to a new idea folder
    - rename_folder(): Rename an idea folder
    """
    
    IDEAS_PATH = 'docs/ideas'
    INVALID_CHARS = r'[/\\:*?"<>|]'
    MAX_NAME_LENGTH = 255
    
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
        Scan docs/ideas/ and return tree structure.
        Creates docs/ideas/ if it doesn't exist.
        
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
    
    def upload(self, files: List[tuple], date: str = None) -> Dict[str, Any]:
        """
        Upload files to a new idea folder.
        
        Args:
            files: List of (filename, content_bytes) tuples
            date: Optional datetime string (MMDDYYYY HHMMSS). Uses now if not provided.
        
        Returns:
            Dict with success, folder_name, folder_path, files_uploaded
        """
        if not files:
            return {
                'success': False,
                'error': 'No files provided'
            }
        
        # Generate folder name with datetime
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
        Delete a file or folder within docs/ideas/.
        
        Args:
            path: Relative path from project root (e.g., 'docs/ideas/folder/file.md')
        
        Returns:
            Dict with success, path, type or error
        """
        import shutil
        
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
                    'error': 'Path must be within docs/ideas/'
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
            folder_path: Relative path to the idea folder (e.g., 'docs/ideas/MyIdea')
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
                    'error': 'Folder must be within docs/ideas/'
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


# =============================================================================
# FEATURE-005: Interactive Console v4.0
# Session-persistent terminal with xterm.js frontend
# =============================================================================

from collections import deque
import uuid

# Constants for session management
BUFFER_MAX_CHARS = 10240  # 10KB limit for output buffer
SESSION_TIMEOUT = 3600   # 1 hour in seconds
CLEANUP_INTERVAL = 300   # 5 minutes for cleanup task


class OutputBuffer:
    """
    Circular buffer for terminal output.
    Uses deque with maxlen for automatic circular behavior.
    Stores up to 10KB of output for replay on reconnection.
    """
    
    def __init__(self, max_chars: int = BUFFER_MAX_CHARS):
        self._buffer: deque = deque(maxlen=max_chars)
    
    def append(self, data: str) -> None:
        """Append data character by character to maintain limit."""
        for char in data:
            self._buffer.append(char)
    
    def get_contents(self) -> str:
        """Get all buffered content as string."""
        return ''.join(self._buffer)
    
    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer.clear()
    
    def __len__(self) -> int:
        return len(self._buffer)


class PersistentSession:
    """
    Terminal session that persists across WebSocket disconnections.
    
    Wraps PTYSession with:
    - Output buffer for replay on reconnection
    - State tracking (connected/disconnected)
    - Expiry tracking for 1-hour timeout
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pty_session: Optional[Any] = None
        self.output_buffer = OutputBuffer()
        self.socket_sid: Optional[str] = None
        self.emit_callback: Optional[Callable[[str], None]] = None
        self.disconnect_time: Optional[datetime] = None
        self.state = 'disconnected'
        self.created_at = datetime.now()
        self._lock = threading.Lock()
    
    def start_pty(self, rows: int = 24, cols: int = 80) -> None:
        """Start the underlying PTY process."""
        def buffered_emit(data: str) -> None:
            # Always buffer output
            self.output_buffer.append(data)
            # Only emit if connected
            if self.emit_callback and self.state == 'connected':
                self.emit_callback(data)
        
        self.pty_session = PTYSession(self.session_id, buffered_emit)
        self.pty_session.start(rows, cols)
    
    def attach(self, socket_sid: str, emit_callback: Callable[[str], None]) -> None:
        """Attach a WebSocket connection to this session."""
        with self._lock:
            self.socket_sid = socket_sid
            self.emit_callback = emit_callback
            self.state = 'connected'
            self.disconnect_time = None
    
    def detach(self) -> None:
        """Detach WebSocket, keeping PTY alive for reconnection."""
        with self._lock:
            self.socket_sid = None
            self.emit_callback = None
            self.state = 'disconnected'
            self.disconnect_time = datetime.now()
    
    def get_buffer(self) -> str:
        """Get buffered output for replay."""
        return self.output_buffer.get_contents()
    
    def write(self, data: str) -> None:
        """Write input to PTY."""
        if self.pty_session:
            self.pty_session.write(data)
    
    def resize(self, rows: int, cols: int) -> None:
        """Resize the PTY."""
        if self.pty_session:
            self.pty_session._set_size(rows, cols)
    
    def is_expired(self, timeout_seconds: int = SESSION_TIMEOUT) -> bool:
        """Check if session has expired (1hr after disconnect)."""
        if self.state == 'connected':
            return False
        if self.disconnect_time is None:
            return False
        elapsed = datetime.now() - self.disconnect_time
        return elapsed.total_seconds() > timeout_seconds
    
    def close(self) -> None:
        """Close session and cleanup resources."""
        if self.pty_session:
            self.pty_session.close()
            self.pty_session = None
        self.output_buffer.clear()


class SessionManager:
    """
    Manages persistent terminal sessions.
    Singleton pattern - one instance per application.
    """
    
    def __init__(self):
        self.sessions: Dict[str, PersistentSession] = {}
        self._lock = threading.Lock()
        self._cleanup_timer: Optional[threading.Timer] = None
        self._running = False
    
    def create_session(self, emit_callback: Callable[[str], None],
                       rows: int = 24, cols: int = 80) -> str:
        """Create new persistent session, returns session_id."""
        session_id = str(uuid.uuid4())
        session = PersistentSession(session_id)
        session.start_pty(rows, cols)
        session.attach(session_id, emit_callback)
        
        with self._lock:
            self.sessions[session_id] = session
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[PersistentSession]:
        """Get session by ID."""
        with self._lock:
            return self.sessions.get(session_id)
    
    def has_session(self, session_id: str) -> bool:
        """Check if session exists."""
        with self._lock:
            return session_id in self.sessions
    
    def remove_session(self, session_id: str) -> None:
        """Remove and close a session."""
        with self._lock:
            session = self.sessions.pop(session_id, None)
        if session:
            session.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count removed."""
        expired_ids = []
        with self._lock:
            for session_id, session in self.sessions.items():
                if session.is_expired():
                    expired_ids.append(session_id)
        
        for session_id in expired_ids:
            self.remove_session(session_id)
        
        return len(expired_ids)
    
    def start_cleanup_task(self) -> None:
        """Start background cleanup task (every 5 minutes)."""
        self._running = True
        self._schedule_cleanup()
    
    def stop_cleanup_task(self) -> None:
        """Stop the cleanup task."""
        self._running = False
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
    
    def _schedule_cleanup(self) -> None:
        if not self._running:
            return
        self._cleanup_timer = threading.Timer(
            CLEANUP_INTERVAL, self._cleanup_and_reschedule
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _cleanup_and_reschedule(self) -> None:
        try:
            self.cleanup_expired()
        finally:
            self._schedule_cleanup()


class PTYSession:
    """
    PTY session using native pty.fork() approach.
    
    Based on working sample-root implementation.
    Manages a single pseudo-terminal process with:
    - Background reader thread for output
    - Write method for input
    - Resize support
    """
    
    def __init__(self, session_id: str, output_callback: Callable[[str], None]):
        self.session_id = session_id
        self.output_callback = output_callback
        self.fd: Optional[int] = None
        self.pid: Optional[int] = None
        self._running = False
        self._reader_thread: Optional[threading.Thread] = None
        self.rows = 24
        self.cols = 80
    
    def start(self, rows: int = 24, cols: int = 80) -> None:
        """Spawn PTY with shell and start output reader."""
        import pty
        import select
        
        self.rows = rows
        self.cols = cols
        
        # Fork a new process with a PTY
        pid, fd = pty.fork()
        
        if pid == 0:
            # Child process - execute shell
            env = os.environ.copy()
            env['TERM'] = 'xterm-256color'
            env['LC_ALL'] = 'en_US.UTF-8'
            env['LANG'] = 'en_US.UTF-8'
            
            # Try to find shell
            shell = os.environ.get('SHELL', '/bin/zsh')
            if not os.path.exists(shell):
                shell = '/bin/zsh'
            if not os.path.exists(shell):
                shell = '/bin/bash'
            
            os.execvpe(shell, [shell], env)
        else:
            # Parent process
            self.fd = fd
            self.pid = pid
            self._running = True
            
            # Set terminal size
            self._set_size(rows, cols)
            
            # Start background thread to read output
            self._reader_thread = threading.Thread(
                target=self._read_loop,
                daemon=True
            )
            self._reader_thread.start()
    
    def _read_loop(self) -> None:
        """Background thread to read PTY output."""
        import select
        import codecs
        
        # Use incremental decoder to properly handle multi-byte UTF-8 sequences
        # that may be split across read() calls
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        while self._running and self.fd is not None:
            try:
                # Use select to wait for data with timeout
                r, _, _ = select.select([self.fd], [], [], 0.1)
                if self.fd in r:
                    data = os.read(self.fd, 4096)
                    if data:
                        # Use incremental decoder - it buffers incomplete sequences
                        text = decoder.decode(data)
                        if text:
                            # Emit output to client
                            self.output_callback(text)
                    else:
                        # EOF - process exited
                        self._running = False
                        break
            except (OSError, IOError):
                # FD closed or error
                self._running = False
                break
        
        # Flush any remaining bytes in the decoder
        try:
            final = decoder.decode(b'', final=True)
            if final:
                self.output_callback(final)
        except Exception:
            pass
    
    def write(self, data: str) -> None:
        """Write input to PTY."""
        if self.fd is not None:
            os.write(self.fd, data.encode('utf-8'))
    
    def _set_size(self, rows: int, cols: int) -> None:
        """Set the terminal size using ioctl."""
        if self.fd is not None:
            import fcntl
            import struct
            import termios
            
            # Ensure rows and cols are integers with defaults (may come as None or strings)
            self.rows = int(rows) if rows is not None else 24
            self.cols = int(cols) if cols is not None else 80
            winsize = struct.pack('HHHH', self.rows, self.cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)
    
    def close(self) -> None:
        """Terminate PTY session and cleanup."""
        import signal
        
        self._running = False
        
        # Close file descriptor
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None
        
        # Kill child process
        if self.pid is not None:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, os.WNOHANG)
            except (OSError, ChildProcessError):
                pass
            self.pid = None
    
    def isalive(self) -> bool:
        """Check if the PTY process is still running."""
        return self._running and self.fd is not None


# Global singleton
session_manager = SessionManager()


class SettingsService:
    """
    Service for managing application settings with SQLite persistence.
    
    FEATURE-006: Settings & Configuration
    
    Provides CRUD operations for settings stored in SQLite database.
    Primary setting: project_root - the root directory for project navigation.
    """
    
    DEFAULT_SETTINGS = {
        'project_root': '.'
    }
    
    def __init__(self, db_path: str = 'instance/settings.db'):
        """
        Initialize SettingsService with database path.
        
        Creates database file and table if they don't exist.
        Applies default settings for any missing keys.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_directory()
        self._ensure_table()
        self._apply_defaults()
    
    def _ensure_directory(self) -> None:
        """Ensure the directory for the database file exists."""
        import os
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _ensure_table(self) -> None:
        """Create settings table if it doesn't exist."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def _apply_defaults(self) -> None:
        """Apply default settings for any missing keys."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            for key, value in self.DEFAULT_SETTINGS.items():
                cursor.execute(
                    'INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)',
                    (key, value)
                )
            conn.commit()
        finally:
            conn.close()
    
    def get(self, key: str, default: Any = None) -> Optional[str]:
        """
        Get a single setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default
        finally:
            conn.close()
    
    def get_all(self) -> Dict[str, str]:
        """
        Get all settings as dictionary.
        
        Returns:
            Dictionary of all settings {key: value}
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM settings')
            return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            conn.close()
    
    def set(self, key: str, value: str) -> None:
        """
        Set a single setting value.
        
        Creates the key if it doesn't exist, updates if it does.
        
        Args:
            key: Setting key
            value: Setting value
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            ''', (key, value))
            conn.commit()
        finally:
            conn.close()
    
    def validate_project_root(self, path: str) -> Dict[str, str]:
        """
        Validate project root path.
        
        Checks:
        - Path is not empty
        - Path exists on filesystem
        - Path is a directory
        - Path is readable
        
        Args:
            path: Path to validate
            
        Returns:
            Empty dict if valid, or {'project_root': 'error message'} if invalid
        """
        errors = {}
        
        # Check empty
        if not path or not path.strip():
            errors['project_root'] = 'Project root path is required'
            return errors
        
        path = path.strip()
        
        # Check exists
        if not os.path.exists(path):
            errors['project_root'] = 'The specified path does not exist'
            return errors
        
        # Check is directory
        if not os.path.isdir(path):
            errors['project_root'] = 'The specified path is not a directory'
            return errors
        
        # Check readable
        if not os.access(path, os.R_OK):
            errors['project_root'] = 'The application does not have read access to this directory'
            return errors
        
        return errors


class ProjectFoldersService:
    """
    Service for managing project folders with SQLite persistence.
    
    FEATURE-006 v2.0: Multi-Project Folder Support
    
    Provides CRUD operations for project folders stored in SQLite database.
    Each project has: id, name, path, created_at, updated_at
    """
    
    def __init__(self, db_path: str = 'instance/settings.db'):
        """
        Initialize ProjectFoldersService with database path.
        
        Creates database file and tables if they don't exist.
        Ensures default project folder exists.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_directory()
        self._ensure_table()
        self._ensure_settings_table()
        self._ensure_default_project()
    
    def _ensure_directory(self) -> None:
        """Ensure the directory for the database file exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _ensure_table(self) -> None:
        """Create project_folders table if it doesn't exist."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def _ensure_settings_table(self) -> None:
        """Ensure settings table exists for active_project_id."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def _ensure_default_project(self) -> None:
        """Ensure default project folder exists."""
        if not self.get_all():
            self._add_default_project()
    
    def _add_default_project(self) -> None:
        """Add the default project folder."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO project_folders (name, path) VALUES (?, ?)',
                ('Default Project Folder', '.')
            )
            # Set active_project_id to 1 if not set
            cursor.execute(
                'INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)',
                ('active_project_id', '1')
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_all(self) -> List[Dict]:
        """
        Get all project folders.
        
        Returns:
            List of project dictionaries with id, name, path
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, path FROM project_folders ORDER BY id')
            return [{'id': r[0], 'name': r[1], 'path': r[2]} for r in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_by_id(self, project_id: int) -> Optional[Dict]:
        """
        Get project folder by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project dict or None if not found
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, path FROM project_folders WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            return {'id': row[0], 'name': row[1], 'path': row[2]} if row else None
        finally:
            conn.close()
    
    def add(self, name: str, path: str) -> Dict:
        """
        Add a new project folder.
        
        Args:
            name: Project name
            path: Project path
            
        Returns:
            Dict with success status and project or errors
        """
        import sqlite3
        
        # Validate
        errors = self._validate(name, path)
        if errors:
            return {'success': False, 'errors': errors}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO project_folders (name, path) VALUES (?, ?)',
                (name.strip(), path.strip())
            )
            conn.commit()
            project_id = cursor.lastrowid
            return {
                'success': True,
                'project': {'id': project_id, 'name': name.strip(), 'path': path.strip()}
            }
        except sqlite3.IntegrityError:
            return {'success': False, 'errors': {'name': 'A project with this name already exists'}}
        finally:
            conn.close()
    
    def update(self, project_id: int, name: str = None, path: str = None) -> Dict:
        """
        Update an existing project folder.
        
        Args:
            project_id: Project ID to update
            name: New name (optional)
            path: New path (optional)
            
        Returns:
            Dict with success status and project or errors
        """
        import sqlite3
        
        existing = self.get_by_id(project_id)
        if not existing:
            return {'success': False, 'error': 'Project not found'}
        
        new_name = name.strip() if name else existing['name']
        new_path = path.strip() if path else existing['path']
        
        # Validate
        errors = self._validate(new_name, new_path, exclude_id=project_id)
        if errors:
            return {'success': False, 'errors': errors}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE project_folders SET name = ?, path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (new_name, new_path, project_id)
            )
            conn.commit()
            return {
                'success': True,
                'project': {'id': project_id, 'name': new_name, 'path': new_path}
            }
        except sqlite3.IntegrityError:
            return {'success': False, 'errors': {'name': 'A project with this name already exists'}}
        finally:
            conn.close()
    
    def delete(self, project_id: int, active_project_id: int = None) -> Dict:
        """
        Delete a project folder.
        
        Args:
            project_id: Project ID to delete
            active_project_id: Current active project ID (to prevent deletion)
            
        Returns:
            Dict with success status or error
        """
        import sqlite3
        
        # Check if only one project
        all_projects = self.get_all()
        if len(all_projects) <= 1:
            return {'success': False, 'error': 'Cannot remove the last project folder'}
        
        # Check if trying to delete active project
        if active_project_id and project_id == active_project_id:
            return {'success': False, 'error': 'Switch to another project before deleting this one'}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM project_folders WHERE id = ?', (project_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return {'success': False, 'error': 'Project not found'}
            return {'success': True}
        finally:
            conn.close()
    
    def _validate(self, name: str, path: str, exclude_id: int = None) -> Dict:
        """
        Validate project name and path.
        
        Args:
            name: Project name
            path: Project path
            exclude_id: Project ID to exclude from duplicate check (for updates)
            
        Returns:
            Dict of field errors or empty dict if valid
        """
        errors = {}
        
        # Name validation
        if not name or not name.strip():
            errors['name'] = 'Project name is required'
        
        # Path validation - strip whitespace before checks
        if not path or not path.strip():
            errors['path'] = 'Project path is required'
        else:
            clean_path = path.strip()
            if not os.path.exists(clean_path):
                errors['path'] = 'The specified path does not exist'
            elif not os.path.isdir(clean_path):
                errors['path'] = 'The specified path is not a directory'
            elif not os.access(clean_path, os.R_OK):
                errors['path'] = 'The application does not have read access to this directory'
        
        return errors
    
    def get_active_id(self) -> int:
        """
        Get the active project ID from settings.
        
        Returns:
            Active project ID (defaults to 1)
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'active_project_id'")
            row = cursor.fetchone()
            return int(row[0]) if row else 1
        finally:
            conn.close()
    
    def set_active(self, project_id: int) -> Dict:
        """
        Set the active project ID.
        
        Args:
            project_id: Project ID to set as active
            
        Returns:
            Dict with success status, active_project_id, and project details
        """
        import sqlite3
        
        # Verify project exists
        project = self.get_by_id(project_id)
        if not project:
            return {'success': False, 'error': 'Project not found'}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO settings (key, value, updated_at)
                VALUES ('active_project_id', ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP
            ''', (str(project_id), str(project_id)))
            conn.commit()
            return {'success': True, 'active_project_id': project_id, 'project': project}
        finally:
            conn.close()

