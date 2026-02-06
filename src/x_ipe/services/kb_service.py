"""
FEATURE-025-A: KB Core Infrastructure

KBService: Core Knowledge Base operations
- Folder structure initialization
- File index management  
- Topic metadata management
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from x_ipe.tracing import x_ipe_tracing


class KBService:
    """
    Service for managing Knowledge Base infrastructure.
    
    Provides core operations for the x-ipe-docs/knowledge-base/ directory:
    - initialize_structure(): Create KB folder structure
    - get_index(): Get current file index
    - refresh_index(): Rebuild index from file system
    - get_topics(): List all topics
    - get_topic_metadata(): Get topic metadata
    """
    
    KB_PATH = 'x-ipe-docs/knowledge-base'
    
    # File type mapping
    FILE_TYPE_MAP = {
        # Documents
        '.pdf': 'pdf',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.txt': 'text',
        '.docx': 'docx',
        '.xlsx': 'xlsx',
        
        # Code
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'header',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        
        # Images
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.svg': 'image',
        '.webp': 'image',
    }
    
    def __init__(self, project_root: str):
        """
        Initialize KBService.
        
        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.kb_root = self.project_root / self.KB_PATH
        self.index_path = self.kb_root / 'index' / 'file-index.json'
    
    @x_ipe_tracing(level="INFO")
    def initialize_structure(self) -> bool:
        """
        Create KB folder structure if it doesn't exist.
        
        Creates:
        - landing/: Raw uploads
        - topics/: Organized by topic
        - processed/: AI summaries
        - index/: Search index files
        
        Returns:
            True if successful
        """
        try:
            # Create main KB directory and subfolders
            folders = [
                self.kb_root / 'landing',
                self.kb_root / 'topics',
                self.kb_root / 'processed',
                self.kb_root / 'index',
            ]
            
            for folder in folders:
                folder.mkdir(parents=True, exist_ok=True)
            
            # Create empty index if it doesn't exist
            if not self.index_path.exists():
                empty_index = {
                    "version": "1.0",
                    "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    "files": []
                }
                self._write_json(self.index_path, empty_index)
            
            return True
        except Exception as e:
            # Log error but don't raise
            return False
    
    @x_ipe_tracing(level="INFO")
    def get_index(self) -> Dict:
        """
        Get current file index.
        
        If KB folder doesn't exist, initializes structure first.
        If index is corrupted, recreates empty index.
        
        Returns:
            File index dictionary with version, last_updated, and files list
        """
        # Initialize structure if needed
        if not self.kb_root.exists():
            self.initialize_structure()
        
        # Read index
        try:
            if self.index_path.exists():
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Corrupted index - recreate
            pass
        
        # Return/create empty index
        empty_index = {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "files": []
        }
        self._write_json(self.index_path, empty_index)
        return empty_index
    
    @x_ipe_tracing(level="INFO")
    def refresh_index(self) -> Dict:
        """
        Rebuild index from file system.
        
        Scans landing/, topics/, and processed/ folders.
        Updates topic metadata files.
        
        Returns:
            Updated file index dictionary
        """
        # Initialize structure if needed
        if not self.kb_root.exists():
            self.initialize_structure()
        
        files = []
        
        # Scan landing folder
        landing_path = self.kb_root / 'landing'
        if landing_path.exists():
            files.extend(self._scan_folder(landing_path, topic=None))
        
        # Scan topics folder
        topics_path = self.kb_root / 'topics'
        if topics_path.exists():
            for topic_dir in topics_path.iterdir():
                if topic_dir.is_dir() and not topic_dir.name.startswith('.'):
                    topic_name = topic_dir.name
                    # Scan raw subfolder
                    raw_path = topic_dir / 'raw'
                    if raw_path.exists():
                        files.extend(self._scan_folder(raw_path, topic=topic_name))
                    # Update topic metadata
                    self._update_topic_metadata(topic_name)
        
        # Scan processed folder
        processed_path = self.kb_root / 'processed'
        if processed_path.exists():
            for topic_dir in processed_path.iterdir():
                if topic_dir.is_dir() and not topic_dir.name.startswith('.'):
                    topic_name = topic_dir.name
                    files.extend(self._scan_folder(topic_dir, topic=topic_name, prefix='processed'))
        
        # Build index
        index = {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "files": files
        }
        
        # Write index
        self._write_json(self.index_path, index)
        
        return index
    
    @x_ipe_tracing(level="INFO")
    def get_topics(self) -> List[str]:
        """
        Get list of all topic names.
        
        Returns:
            List of topic folder names
        """
        topics = []
        topics_path = self.kb_root / 'topics'
        
        if topics_path.exists():
            for item in topics_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    topics.append(item.name)
        
        return sorted(topics)
    
    @x_ipe_tracing(level="INFO")
    def get_topic_metadata(self, topic: str) -> Optional[Dict]:
        """
        Get metadata for a specific topic.
        
        Args:
            topic: Topic folder name
            
        Returns:
            Topic metadata dictionary or None if not found
        """
        metadata_path = self.kb_root / 'topics' / topic / 'metadata.json'
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _scan_folder(self, folder: Path, topic: Optional[str], prefix: str = None) -> List[Dict]:
        """
        Scan a folder and return file entries.
        
        Args:
            folder: Path to folder to scan
            topic: Topic name (None for landing)
            prefix: Path prefix (e.g., 'processed')
            
        Returns:
            List of file entry dictionaries
        """
        files = []
        
        try:
            for entry in folder.iterdir():
                if entry.name.startswith('.'):
                    continue  # Skip hidden files
                
                if entry.is_file():
                    # Build relative path
                    if prefix:
                        rel_path = f"{prefix}/{topic}/{entry.name}"
                    elif topic:
                        rel_path = f"topics/{topic}/raw/{entry.name}"
                    else:
                        rel_path = f"landing/{entry.name}"
                    
                    # Get file stats
                    stat = entry.stat()
                    
                    file_entry = {
                        "path": rel_path,
                        "name": entry.name,
                        "type": self._get_file_type(entry.suffix),
                        "size": stat.st_size,
                        "topic": topic,
                        "created_date": datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc
                        ).isoformat().replace('+00:00', 'Z'),
                        "keywords": self._extract_keywords(entry.name)
                    }
                    files.append(file_entry)
        except PermissionError:
            pass  # Skip folders we can't read
        
        return files
    
    def _get_file_type(self, extension: str) -> str:
        """
        Get file type from extension.
        
        Args:
            extension: File extension (e.g., '.pdf')
            
        Returns:
            File type string (e.g., 'pdf', 'unknown')
        """
        return self.FILE_TYPE_MAP.get(extension.lower(), 'unknown')
    
    def _extract_keywords(self, filename: str) -> List[str]:
        """
        Extract keywords from filename.
        
        Splits on hyphens, underscores, spaces, and removes extension.
        
        Args:
            filename: Filename to extract keywords from
            
        Returns:
            List of lowercase keyword strings
        """
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Split on common separators
        parts = re.split(r'[-_\s]+', name_without_ext)
        
        # Filter and lowercase
        keywords = [p.lower() for p in parts if p]
        
        return keywords
    
    def _update_topic_metadata(self, topic: str) -> None:
        """
        Update or create metadata.json for a topic.
        
        Args:
            topic: Topic folder name
        """
        topic_path = self.kb_root / 'topics' / topic
        metadata_path = topic_path / 'metadata.json'
        raw_path = topic_path / 'raw'
        
        # Count files in raw folder
        file_count = 0
        if raw_path.exists():
            file_count = len([f for f in raw_path.iterdir() 
                            if f.is_file() and not f.name.startswith('.')])
        
        # Load existing or create new
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except (json.JSONDecodeError, IOError):
                metadata = {}
        else:
            metadata = {}
        
        # Update fields
        metadata.update({
            "name": topic,
            "description": metadata.get("description", ""),
            "file_count": file_count,
            "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "tags": metadata.get("tags", [])
        })
        
        # Write
        self._write_json(metadata_path, metadata)
    
    def _write_json(self, path: Path, data: Dict) -> None:
        """
        Write JSON data to file with pretty formatting.
        
        Args:
            path: Path to write to
            data: Dictionary to write
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
