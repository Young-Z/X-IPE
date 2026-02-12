"""
FEATURE-025-A: KB Core Infrastructure
FEATURE-025-B: KB Landing Zone

KBService: Core Knowledge Base operations
- Folder structure initialization
- File index management  
- Topic metadata management
- Landing zone: upload, delete, list
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from werkzeug.utils import secure_filename

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
    
    # Allowed extensions for upload (keys from FILE_TYPE_MAP)
    ALLOWED_EXTENSIONS = set(FILE_TYPE_MAP.keys())
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
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

    @x_ipe_tracing(level="INFO")
    def get_summary_versions(self, topic: str) -> List[Dict]:
        """Get list of summary versions for a topic, newest first (max 5)."""
        processed_dir = self.kb_root / 'processed' / topic
        if not processed_dir.exists():
            return []
        versions = []
        for f in processed_dir.glob("summary-v*.md"):
            match = re.match(r"summary-v(\d+)\.md", f.name)
            if match:
                ver = int(match.group(1))
                stat = f.stat()
                versions.append({
                    "version": ver,
                    "date": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                })
        versions.sort(key=lambda v: v["version"], reverse=True)
        if versions:
            versions[0]["current"] = True
        for v in versions[1:]:
            v["current"] = False
        return versions[:5]

    @x_ipe_tracing(level="INFO")
    def get_summary_content(self, topic: str, version: str = "latest") -> Optional[Dict]:
        """Read summary markdown content for a specific version."""
        processed_dir = self.kb_root / 'processed' / topic
        if not processed_dir.exists():
            return None
        if version == "latest":
            versions = self.get_summary_versions(topic)
            if not versions:
                return None
            version = versions[0]["version"]
        else:
            version = int(version)
        filepath = processed_dir / f"summary-v{version}.md"
        if not filepath.exists():
            return None
        content = filepath.read_text(encoding="utf-8")
        stat = filepath.stat()
        return {
            "version": version,
            "date": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "content": content,
        }

    @x_ipe_tracing(level="INFO")
    def get_topic_detail(self, topic: str) -> Optional[Dict]:
        """Get full topic detail: metadata + summaries + files + related topics."""
        metadata = self.get_topic_metadata(topic)
        if metadata is None:
            return None
        summaries = self.get_summary_versions(topic)
        raw_dir = self.kb_root / 'topics' / topic / 'raw'
        files = []
        if raw_dir.exists():
            for f in sorted(raw_dir.iterdir()):
                if f.is_file():
                    files.append({
                        "name": f.name,
                        "path": f"topics/{topic}/raw/{f.name}",
                        "size": f.stat().st_size,
                        "type": self._get_file_type(Path(f.name).suffix),
                    })
        all_topics = self.get_topics()
        related = [t for t in all_topics if t != topic]
        return {
            **metadata,
            "summary_count": len(summaries),
            "summaries": summaries,
            "files": files,
            "related_topics": related[:4],
        }
    
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
    
    # ------------------------------------------------------------------
    # FEATURE-025-B: Landing Zone operations
    # ------------------------------------------------------------------
    
    def _validate_upload(self, filename: str, size: int) -> Tuple[bool, str]:
        """
        Validate a file for upload.
        
        Args:
            filename: Original filename
            size: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        ext = Path(filename).suffix.lower()
        if not ext or ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type: '{ext or 'none'}'"
        if size > self.MAX_FILE_SIZE:
            return False, f"File exceeds 50MB size limit ({size} bytes)"
        return True, ''
    
    @x_ipe_tracing(level="INFO")
    def upload_files(self, files: List[tuple]) -> Dict[str, Any]:
        """
        Upload files to the landing directory.
        
        Args:
            files: List of (filename, data, size) tuples
            
        Returns:
            Dict with 'uploaded', 'skipped', 'errors' lists
        """
        uploaded = []
        skipped = []
        errors = []
        landing_dir = self.kb_root / 'landing'
        landing_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, data, size in files:
            safe_name = secure_filename(filename)
            if not safe_name:
                errors.append({'file': filename, 'reason': 'Invalid filename'})
                continue
            
            valid, msg = self._validate_upload(safe_name, size)
            if not valid:
                errors.append({'file': filename, 'reason': msg})
                continue
            
            dest = landing_dir / safe_name
            if dest.exists():
                skipped.append({'file': safe_name, 'reason': 'Duplicate file already exists'})
                continue
            
            try:
                dest.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))
                uploaded.append(f'landing/{safe_name}')
            except Exception as e:
                errors.append({'file': filename, 'reason': str(e)})
        
        if uploaded:
            self.refresh_index()
        
        return {'uploaded': uploaded, 'skipped': skipped, 'errors': errors}
    
    @x_ipe_tracing(level="INFO")
    def delete_files(self, paths: List[str]) -> Dict[str, Any]:
        """
        Delete files from the landing directory.
        
        Args:
            paths: List of relative paths (must start with 'landing/')
            
        Returns:
            Dict with 'deleted' and 'errors' lists
        """
        deleted = []
        errors = []
        
        for rel_path in paths:
            if not rel_path.startswith('landing/'):
                errors.append({'file': rel_path, 'reason': 'Path must be under landing/'})
                continue
            
            # Resolve and check for path traversal
            file_path = (self.kb_root / rel_path).resolve()
            landing_resolved = (self.kb_root / 'landing').resolve()
            if not str(file_path).startswith(str(landing_resolved)):
                errors.append({'file': rel_path, 'reason': 'Invalid path'})
                continue
            
            if not file_path.exists():
                errors.append({'file': rel_path, 'reason': 'File not found'})
                continue
            
            try:
                file_path.unlink()
                deleted.append(rel_path)
            except Exception as e:
                errors.append({'file': rel_path, 'reason': str(e)})
        
        if deleted:
            self.refresh_index()
        
        return {'deleted': deleted, 'errors': errors}
    
    @x_ipe_tracing(level="DEBUG")
    def get_landing_files(self) -> List[Dict[str, Any]]:
        """
        Get files in the landing directory from the index.
        
        Returns:
            List of file entries with path starting with 'landing/'
        """
        index = self.get_index()
        return [f for f in index.get('files', []) if f.get('path', '').startswith('landing/')]
    
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
