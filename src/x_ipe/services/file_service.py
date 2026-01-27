"""
FEATURE-001: Project Navigation

FileNode: Represents a file or folder in the project structure
Section: Represents a top-level section in the sidebar
ProjectService: Scans project directory and returns structure
FileWatcherHandler: Handler for file system events
FileWatcher: Monitors file system changes and emits WebSocket events
ContentService: Reads file content and detects file types
"""
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


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
    - Project Plan -> x-ipe-docs/planning/
    - Requirements -> x-ipe-docs/requirements/
    - Code -> src/
    """

    # Default section configuration
    DEFAULT_SECTIONS = [
        {
            'id': 'workplace',
            'label': 'Workplace',
            'path': 'x-ipe-docs/ideas',
            'icon': 'bi-lightbulb'
        },
        {
            'id': 'themes',
            'label': 'Themes',
            'path': 'x-ipe-docs/themes',
            'icon': 'bi-palette'
        },
        {
            'id': 'planning',
            'label': 'Project Plan',
            'path': 'x-ipe-docs/planning',
            'icon': 'bi-kanban'
        },
        {
            'id': 'requirements',
            'label': 'Requirements',
            'path': 'x-ipe-docs/requirements',
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
