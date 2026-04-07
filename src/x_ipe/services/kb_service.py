"""
FEATURE-049-A: KB Backend & Storage Foundation

KBService: File/folder CRUD, tree building, search, frontmatter parsing, config management.
KBNode: Tree node data model (file or folder).
FrontmatterData / TagSet: Parsed YAML frontmatter models.
KBConfig: knowledgebase-config.json schema + defaults.
"""
import json
import os
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from x_ipe.tracing import x_ipe_tracing

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KB_ROOT_DIR = 'x-ipe-docs/knowledge-base'
KB_CONFIG_FILE = 'knowledgebase-config.json'
KB_CONFIG_DIR = 'x-ipe-docs/config'
INTAKE_FOLDER = '.intake'
KB_INDEX_FILE = '.kb-index.json'

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

EXTENSION_TYPE_MAP = {
    '.md': 'markdown',
    '.png': 'image', '.jpg': 'image', '.jpeg': 'image',
    '.gif': 'image', '.svg': 'image', '.webp': 'image',
    '.mp4': 'video', '.mov': 'video', '.webm': 'video', '.avi': 'video',
    '.pdf': 'pdf',
    '.doc': 'document', '.docx': 'document', '.xls': 'document',
    '.xlsx': 'document', '.ppt': 'document', '.pptx': 'document',
}

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class TagSet:
    """Two-dimensional tag taxonomy."""
    lifecycle: List[str] = field(default_factory=list)
    domain: List[str] = field(default_factory=list)


@dataclass
class FrontmatterData:
    """Parsed YAML frontmatter from a markdown file."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[TagSet] = None
    author: Optional[str] = None
    created: Optional[str] = None
    auto_generated: bool = False
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'title': self.title,
            'description': self.description,
            'tags': {
                'lifecycle': self.tags.lifecycle,
                'domain': self.tags.domain,
            } if self.tags else None,
            'author': self.author,
            'created': self.created,
            'auto_generated': self.auto_generated,
        }
        if self.url is not None:
            result['url'] = self.url
        return result


@dataclass
class KBNode:
    """A node in the KB file tree (file or folder)."""
    name: str
    path: str
    type: str  # "folder" | "file"
    children: Optional[List['KBNode']] = None
    size_bytes: Optional[int] = None
    modified_date: Optional[str] = None
    file_type: Optional[str] = None
    frontmatter: Optional[FrontmatterData] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'name': self.name,
            'path': self.path,
            'type': self.type,
        }
        if self.children is not None:
            result['children'] = [c.to_dict() for c in self.children]
        if self.size_bytes is not None:
            result['size_bytes'] = self.size_bytes
        if self.modified_date is not None:
            result['modified_date'] = self.modified_date
        if self.file_type is not None:
            result['file_type'] = self.file_type
        if self.frontmatter is not None:
            result['frontmatter'] = self.frontmatter.to_dict()
        return result


@dataclass
class KBConfig:
    """knowledgebase-config.json schema."""
    tags: Dict[str, List[str]] = field(default_factory=lambda: {
        'lifecycle': [
            'Ideation', 'Requirement', 'Design', 'Implementation',
            'Testing', 'Deployment', 'Maintenance',
        ],
        'domain': [
            'API', 'Authentication', 'UI-UX', 'Database',
            'Infrastructure', 'Security', 'Performance',
            'Integration', 'Documentation', 'Analytics',
        ],
    })
    agent_write_allowlist: List[str] = field(default_factory=list)
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.tsv',
        '.html', '.htm', '.css', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
        '.xml', '.toml', '.ini', '.cfg', '.env', '.sh', '.bat', '.ps1',
        '.py', '.rb', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.hpp', '.cs',
        '.swift', '.kt', '.scala', '.r', '.m', '.sql', '.graphql',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff',
        '.mp3', '.mp4', '.wav', '.ogg', '.webm',
        '.zip', '.7z', '.tar', '.gz',
        '.woff', '.woff2', '.ttf', '.otf', '.eot',
        '.msg',
    ])
    ai_librarian: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': False,
        'intake_folder': '.intake',
        'skill': 'x-ipe-tool-kb-librarian',
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tags': self.tags,
            'agent_write_allowlist': self.agent_write_allowlist,
            'allowed_extensions': self.allowed_extensions,
            'ai_librarian': self.ai_librarian,
        }


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class KBService:
    """Service for managing the Knowledge Base file system and metadata."""

    CACHE_TTL = 2.0  # seconds — detect external filesystem changes

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.kb_root = self.project_root / KB_ROOT_DIR
        self.config_path = self.project_root / KB_CONFIG_DIR / KB_CONFIG_FILE
        self._tree_cache: Optional[List[KBNode]] = None
        self._frontmatter_index: Dict[str, Optional[FrontmatterData]] = {}
        self._cache_valid = False
        self._cache_built_at: float = 0.0

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def ensure_kb_root(self) -> None:
        """Create KB root directory and default knowledgebase-config.json if missing."""
        self.kb_root.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            default_config = KBConfig()
            self._write_json(self.config_path, default_config.to_dict())

    # ------------------------------------------------------------------
    # Path safety
    # ------------------------------------------------------------------

    def _resolve_safe_path(self, rel_path: str) -> Path:
        """Resolve a user-provided relative path safely within KB root.

        Raises ``ValueError`` on traversal attempts.
        """
        clean = rel_path.replace('\\', '/').strip('/')
        if not clean:
            return self.kb_root.resolve()
        resolved = (self.kb_root / clean).resolve()
        if not resolved.is_relative_to(self.kb_root.resolve()):
            raise ValueError(f"Path traversal attempt: {rel_path}")
        return resolved

    # ------------------------------------------------------------------
    # Atomic I/O helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _write_file_atomic(target: Path, content: str) -> None:
        """Write *content* to *target* atomically (temp → rename)."""
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                fh.write(content)
            os.replace(tmp_path, str(target))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    @staticmethod
    def _write_json(target: Path, data: Any) -> None:
        """Write JSON data atomically."""
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.write('\n')
            os.replace(tmp_path, str(target))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    @staticmethod
    def _write_binary_atomic(target: Path, data: bytes) -> None:
        """Write binary *data* to *target* atomically (temp → rename)."""
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
        try:
            with os.fdopen(fd, 'wb') as fh:
                fh.write(data)
            os.replace(tmp_path, str(target))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------

    def _invalidate_cache(self) -> None:
        self._cache_valid = False
        self._tree_cache = None
        self._cache_built_at = 0.0
        self._frontmatter_index.clear()
        if hasattr(self, '_allowed_ext_cache'):
            del self._allowed_ext_cache

    def _ensure_file_index(self) -> None:
        """Rebuild the in-memory tree cache and metadata index if stale."""
        if self._cache_valid and self._tree_cache is not None:
            if time.time() - self._cache_built_at <= self.CACHE_TTL:
                return
            self._invalidate_cache()
        self.ensure_kb_root()
        self._tree_cache = self._build_tree(self.kb_root, '')
        self._cache_valid = True
        self._cache_built_at = time.time()

    # ------------------------------------------------------------------
    # Tree building
    # ------------------------------------------------------------------

    def _build_tree(self, dir_path: Path, rel_base: str) -> List[KBNode]:
        """Recursively build a ``KBNode`` tree for *dir_path*."""
        nodes: List[KBNode] = []
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return nodes

        # Read the folder's index for metadata
        index = self._read_kb_index(dir_path)
        index_entries = index.get('entries', {})

        for entry in entries:
            name = entry.name
            if name.startswith('.'):
                continue

            rel_path = f"{rel_base}/{name}".lstrip('/')

            if entry.is_dir():
                children = self._build_tree(entry, rel_path)
                nodes.append(KBNode(
                    name=name,
                    path=rel_path,
                    type='folder',
                    children=children,
                ))
            elif entry.is_file():
                stat = entry.stat()
                idx_entry = index_entries.get(name)
                if idx_entry:
                    fm = self._index_entry_to_frontmatter(idx_entry)
                else:
                    fm = self._parse_frontmatter_safe(entry)
                self._frontmatter_index[rel_path] = fm
                nodes.append(self._build_file_node(rel_path, name, stat, fm))
        return nodes

    # ------------------------------------------------------------------
    # Frontmatter
    # ------------------------------------------------------------------

    def _parse_frontmatter_safe(self, file_path: Path) -> Optional[FrontmatterData]:
        """Parse frontmatter; return ``None`` for non-md or on errors."""
        if not file_path.suffix.lower() == '.md':
            return None
        try:
            return self._parse_frontmatter(file_path)
        except Exception:
            return None

    @staticmethod
    def _parse_frontmatter(file_path: Path) -> Optional[FrontmatterData]:
        """Parse YAML frontmatter from a markdown file."""
        content = file_path.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return None
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        try:
            raw = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            return None
        if not isinstance(raw, dict):
            return None
        tags_raw = raw.get('tags', {})
        if isinstance(tags_raw, dict):
            lc = tags_raw.get('lifecycle', [])
            dm = tags_raw.get('domain', [])
            lc = [lc] if isinstance(lc, str) else (lc or [])
            dm = [dm] if isinstance(dm, str) else (dm or [])
        else:
            lc, dm = [], []
        tags = TagSet(lifecycle=lc, domain=dm)
        return FrontmatterData(
            title=raw.get('title'),
            tags=tags,
            author=raw.get('author'),
            created=str(raw.get('created', '')) or None,
            auto_generated=bool(raw.get('auto_generated', False)),
            url=raw.get('url'),
        )

    @staticmethod
    def _serialize_frontmatter(fm_data: FrontmatterData, body: str) -> str:
        """Combine frontmatter + markdown body into a single string."""
        fm_dict: Dict[str, Any] = {}
        if fm_data.title is not None:
            fm_dict['title'] = fm_data.title
        if fm_data.tags is not None:
            fm_dict['tags'] = {
                'lifecycle': fm_data.tags.lifecycle,
                'domain': fm_data.tags.domain,
            }
        if fm_data.author is not None:
            fm_dict['author'] = fm_data.author
        if fm_data.created is not None:
            fm_dict['created'] = fm_data.created
        fm_dict['auto_generated'] = fm_data.auto_generated
        if fm_data.url is not None:
            fm_dict['url'] = fm_data.url
        yaml_str = yaml.safe_dump(fm_dict, default_flow_style=False, allow_unicode=True).rstrip('\n')
        return f"---\n{yaml_str}\n---\n{body}"

    @staticmethod
    def _auto_populate_frontmatter(fm: Optional[Dict[str, Any]], filename: str) -> FrontmatterData:
        """Fill in missing frontmatter fields with sensible defaults."""
        if fm is None:
            fm = {}
        stem = Path(filename).stem
        if filename.endswith('.url.md'):
            stem = filename[:-len('.url.md')]
        title = fm.get('title') or stem.replace('-', ' ').replace('_', ' ').title()
        tags_raw = fm.get('tags', {})
        if isinstance(tags_raw, dict):
            lc = tags_raw.get('lifecycle', [])
            dm = tags_raw.get('domain', [])
            lc = [lc] if isinstance(lc, str) else (lc or [])
            dm = [dm] if isinstance(dm, str) else (dm or [])
            tags = TagSet(lifecycle=lc, domain=dm)
        else:
            tags = TagSet()
        author = fm.get('author') or 'unknown'
        created = str(fm.get('created', '')) or str(date.today())
        auto_generated = bool(fm.get('auto_generated', False))
        url = fm.get('url')
        return FrontmatterData(
            title=title, tags=tags, author=author,
            created=created, auto_generated=auto_generated, url=url,
        )

    @staticmethod
    def _extract_body(content: str) -> str:
        """Return the markdown body (everything after the second ``---``)."""
        if not content.startswith('---'):
            return content
        parts = content.split('---', 2)
        if len(parts) < 3:
            return content
        return parts[2].lstrip('\n')

    # ------------------------------------------------------------------
    # KB Index (.kb-index.json)
    # ------------------------------------------------------------------

    KB_INDEX_VERSION = '1.0'

    def _read_kb_index(self, folder_path: Path) -> Dict[str, Any]:
        """Read .kb-index.json from folder. Returns empty entries dict if missing/corrupted.
        
        Handles both formats:
        - Canonical: {"version": "1.0", "entries": {"file.md": {...}}}
        - Flat (legacy): {"file.md": {...}} — auto-wrapped into canonical form
        """
        index_path = folder_path / KB_INDEX_FILE
        if not index_path.exists():
            return {'version': self.KB_INDEX_VERSION, 'entries': {}}
        try:
            with open(index_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                return {'version': self.KB_INDEX_VERSION, 'entries': {}}
            if 'entries' in data:
                return data
            # Flat format: all top-level keys are entry names
            # (exclude 'version' if present at top level)
            entries = {k: v for k, v in data.items()
                       if k != 'version' and isinstance(v, dict)}
            return {'version': data.get('version', self.KB_INDEX_VERSION), 'entries': entries}
        except (json.JSONDecodeError, OSError):
            import logging
            logging.getLogger(__name__).warning(
                'Corrupted %s — returning empty index', index_path,
            )
            return {'version': self.KB_INDEX_VERSION, 'entries': {}}

    def _write_kb_index(self, folder_path: Path, index_data: Dict[str, Any]) -> None:
        """Atomic write .kb-index.json to folder."""
        index_path = folder_path / KB_INDEX_FILE
        self._write_json(index_path, index_data)

    def _get_index_entry(self, folder_path: Path, name: str) -> Optional[Dict[str, Any]]:
        """Get a single entry from folder's .kb-index.json."""
        index = self._read_kb_index(folder_path)
        return index['entries'].get(name)

    def _set_index_entry(self, folder_path: Path, name: str, entry: Dict[str, Any]) -> None:
        """Set/update a single entry in folder's .kb-index.json."""
        index = self._read_kb_index(folder_path)
        index['entries'][name] = entry
        self._write_kb_index(folder_path, index)

    def _remove_index_entry(self, folder_path: Path, name: str) -> None:
        """Remove an entry from folder's .kb-index.json. No-op if missing."""
        index = self._read_kb_index(folder_path)
        if name in index['entries']:
            del index['entries'][name]
            self._write_kb_index(folder_path, index)

    @staticmethod
    def _detect_kb_file_type(filename: str) -> str:
        """Map file extension to knowledge base type category."""
        ext = Path(filename).suffix.lower()
        return EXTENSION_TYPE_MAP.get(ext, 'other')

    def _auto_populate_index_entry(self, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a default index entry with sensible defaults.

        If metadata is provided, its values take precedence over defaults.
        """
        if metadata is None:
            metadata = {}
        stem = Path(filename).stem
        if filename.endswith('.url.md'):
            stem = filename[:-len('.url.md')]

        tags_raw = metadata.get('tags', {})
        if isinstance(tags_raw, dict):
            lc = tags_raw.get('lifecycle', [])
            dm = tags_raw.get('domain', [])
            lc = [lc] if isinstance(lc, str) else (lc or [])
            dm = [dm] if isinstance(dm, str) else (dm or [])
        else:
            lc, dm = [], []

        entry = {
            'title': metadata.get('title') or stem.replace('-', ' ').replace('_', ' ').title(),
            'description': metadata.get('description') or '',
            'tags': {'lifecycle': lc, 'domain': dm},
            'author': metadata.get('author') or 'unknown',
            'created': str(metadata.get('created', '')) or str(date.today()),
            'type': self._detect_kb_file_type(filename),
            'auto_generated': bool(metadata.get('auto_generated', False)),
        }
        if metadata.get('url') is not None:
            entry['url'] = metadata['url']
        return entry

    def _index_entry_to_frontmatter(self, entry: Dict[str, Any]) -> FrontmatterData:
        """Convert an index entry dict to a FrontmatterData object for API compatibility."""
        tags_raw = entry.get('tags', {})
        if isinstance(tags_raw, dict):
            tags = TagSet(
                lifecycle=tags_raw.get('lifecycle', []),
                domain=tags_raw.get('domain', []),
            )
        else:
            tags = TagSet()
        return FrontmatterData(
            title=entry.get('title'),
            description=entry.get('description'),
            tags=tags,
            author=entry.get('author'),
            created=entry.get('created'),
            auto_generated=bool(entry.get('auto_generated', False)),
            url=entry.get('url'),
        )

    def _migrate_frontmatter_to_index(self, folder_path: Path) -> None:
        """One-time migration: read YAML frontmatter from .md files, write to .kb-index.json.

        Only migrates if .kb-index.json doesn't already exist for the folder.
        Does NOT remove frontmatter from the .md files (non-destructive).
        """
        index_path = folder_path / KB_INDEX_FILE
        if index_path.exists():
            return  # already migrated

        index = {'version': self.KB_INDEX_VERSION, 'entries': {}}
        has_entries = False

        try:
            for entry in folder_path.iterdir():
                if entry.name.startswith('.'):
                    continue
                if entry.is_dir():
                    continue
                if entry.is_file():
                    if entry.suffix.lower() == '.md':
                        fm = self._parse_frontmatter_safe(entry)
                        if fm:
                            idx_entry = fm.to_dict()
                            idx_entry['type'] = 'markdown'
                            if 'description' not in idx_entry or idx_entry['description'] is None:
                                idx_entry['description'] = ''
                            index['entries'][entry.name] = idx_entry
                            has_entries = True
                        else:
                            index['entries'][entry.name] = self._auto_populate_index_entry(entry.name)
                            has_entries = True
                    else:
                        index['entries'][entry.name] = self._auto_populate_index_entry(entry.name)
                        has_entries = True
        except PermissionError:
            pass

        if has_entries:
            self._write_kb_index(folder_path, index)

    # ------------------------------------------------------------------
    # Tree / listing
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def get_tree(self) -> List[KBNode]:
        """Return the full KB folder/file tree (cached)."""
        self._ensure_file_index()
        assert self._tree_cache is not None
        return self._tree_cache

    @x_ipe_tracing()
    def list_files(self, folder: str = '', sort: str = 'modified',
                   recursive: bool = False) -> List[KBNode]:
        """List files in *folder* with optional sorting.
        When *recursive* is True, walk all subdirectories."""
        self._ensure_file_index()
        target = self._resolve_safe_path(folder)
        if not target.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder}")

        files: List[KBNode] = []
        entries = target.rglob('*') if recursive else target.iterdir()
        # Cache indexes per folder for efficiency
        _index_cache: Dict[Path, Dict[str, Any]] = {}
        for entry in entries:
            if not entry.is_file():
                continue
            if entry.name.startswith('.'):
                continue
            rel = str(entry.relative_to(self.kb_root)).replace('\\', '/')
            stat = entry.stat()
            # Read the index for this file's parent folder (cached)
            parent = entry.parent
            if parent not in _index_cache:
                idx = self._read_kb_index(parent)
                _index_cache[parent] = idx.get('entries', {})
            idx_entry = _index_cache[parent].get(entry.name)
            if idx_entry:
                fm = self._index_entry_to_frontmatter(idx_entry)
            else:
                fm = self._frontmatter_index.get(rel) or self._parse_frontmatter_safe(entry)
            files.append(self._build_file_node(rel, entry.name, stat, fm))
        return self._sort_files(files, sort)

    # ------------------------------------------------------------------
    # File CRUD
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def get_file(self, rel_path: str) -> Dict[str, Any]:
        """Read a single file — content + metadata from .kb-index.json."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {rel_path}")
        stat = target.stat()
        file_type = self._determine_file_type(target.name)

        # Read metadata from folder's index
        folder_path = target.parent
        idx_entry = self._get_index_entry(folder_path, target.name)
        if idx_entry:
            fm = self._index_entry_to_frontmatter(idx_entry)
        else:
            # Fallback: parse frontmatter from file (backwards compat)
            fm = self._parse_frontmatter_safe(target)

        # Binary files: return metadata only (no content)
        TEXT_EXTS = {'.md', '.txt', '.json', '.yaml', '.yml', '.csv',
                     '.html', '.htm', '.css', '.js', '.ts', '.xml',
                     '.toml', '.ini', '.cfg', '.sh', '.bat', '.py',
                     '.rb', '.java', '.go', '.rs', '.c', '.cpp', '.h'}
        ext = target.suffix.lower()
        if ext not in TEXT_EXTS:
            return {
                'name': target.name,
                'path': rel_path,
                'content': None,
                'frontmatter': fm.to_dict() if fm else None,
                'size_bytes': stat.st_size,
                'modified_date': self._iso_mtime(stat),
                'file_type': file_type,
                'binary': True,
            }
        content = target.read_text(encoding='utf-8')
        body = self._extract_body(content)
        return {
            'name': target.name,
            'path': rel_path,
            'content': body,
            'frontmatter': fm.to_dict() if fm else None,
            'size_bytes': stat.st_size,
            'modified_date': self._iso_mtime(stat),
            'file_type': file_type,
        }

    @x_ipe_tracing()
    def create_file(self, rel_path: str, content: str,
                    frontmatter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new KB file with metadata in .kb-index.json."""
        target = self._resolve_safe_path(rel_path)
        self._validate_file_type(target.name)
        if target.exists():
            raise FileExistsError(f"File already exists: {rel_path}")

        # URL bookmark validation
        if target.name.endswith('.url.md'):
            if not frontmatter or not frontmatter.get('url'):
                raise ValueError("URL bookmark files require a 'url' field in frontmatter")

        # Write file content (no frontmatter injection)
        self._check_size(content)
        self._write_file_atomic(target, content)

        # Write metadata to folder's .kb-index.json
        entry = self._auto_populate_index_entry(target.name, frontmatter)
        self._set_index_entry(target.parent, target.name, entry)

        self._invalidate_cache()
        return self.get_file(rel_path)

    @x_ipe_tracing()
    def create_binary_file(self, rel_path: str, data: bytes,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new binary KB file (images, PDFs, etc.) with index entry."""
        target = self._resolve_safe_path(rel_path)
        self._validate_file_type(target.name)
        if target.exists():
            raise FileExistsError(f"File already exists: {rel_path}")
        if len(data) > MAX_FILE_SIZE_BYTES:
            raise ValueError("File exceeds maximum size of 10MB")
        self._write_binary_atomic(target, data)

        # Write metadata to folder's .kb-index.json
        entry = self._auto_populate_index_entry(target.name, metadata)
        self._set_index_entry(target.parent, target.name, entry)

        self._invalidate_cache()
        stat = target.stat()
        fm = self._index_entry_to_frontmatter(entry)
        return {
            'name': target.name,
            'path': rel_path,
            'size_bytes': stat.st_size,
            'modified_date': self._iso_mtime(stat),
            'file_type': self._determine_file_type(target.name),
            'frontmatter': fm.to_dict(),
        }

    @x_ipe_tracing()
    def update_file(self, rel_path: str, content: Optional[str] = None,
                    frontmatter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update file content and/or metadata in .kb-index.json."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {rel_path}")

        if content is not None:
            self._check_size(content)
            self._write_file_atomic(target, content)

        if frontmatter is not None:
            # Read existing index entry, merge with provided metadata
            existing_entry = self._get_index_entry(target.parent, target.name) or {}
            new_entry = self._auto_populate_index_entry(target.name, {**existing_entry, **frontmatter})
            self._set_index_entry(target.parent, target.name, new_entry)

        self._invalidate_cache()
        return self.get_file(rel_path)

    @x_ipe_tracing()
    def delete_file(self, rel_path: str) -> None:
        """Delete a file and its index entry."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {rel_path}")
        # Remove index entry
        self._remove_index_entry(target.parent, target.name)
        target.unlink()
        self._invalidate_cache()

    @x_ipe_tracing()
    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a file to a new path, transferring its index entry."""
        src = self._resolve_safe_path(source)
        dst = self._resolve_safe_path(destination)
        if not src.is_file():
            raise FileNotFoundError(f"Source file not found: {source}")
        if not dst.parent.is_dir():
            raise FileNotFoundError(f"Destination folder not found: {str(dst.parent.relative_to(self.kb_root))}")
        if dst.exists():
            raise FileExistsError(f"Destination already exists: {destination}")

        # Transfer index entry from source folder to destination folder
        old_entry = self._get_index_entry(src.parent, src.name)
        shutil.move(str(src), str(dst))
        if old_entry:
            self._remove_index_entry(src.parent, src.name)
            self._set_index_entry(dst.parent, dst.name, old_entry)

        self._invalidate_cache()
        return {'old_path': source, 'new_path': destination}

    # ------------------------------------------------------------------
    # Folder CRUD
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def create_folder(self, rel_path: str) -> Dict[str, Any]:
        """Create a new folder."""
        target = self._resolve_safe_path(rel_path)
        if target.exists():
            raise FileExistsError(f"Folder already exists: {rel_path}")
        target.mkdir(parents=True)
        self._invalidate_cache()
        return {'name': target.name, 'path': rel_path, 'type': 'folder'}

    @x_ipe_tracing()
    def rename_folder(self, rel_path: str, new_name: str) -> Dict[str, Any]:
        """Rename a folder (same parent, new name)."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_dir():
            raise FileNotFoundError(f"Folder not found: {rel_path}")
        new_target = target.parent / new_name
        if new_target.exists():
            raise FileExistsError(f"A folder named '{new_name}' already exists")
        target.rename(new_target)
        new_rel = str(new_target.relative_to(self.kb_root)).replace('\\', '/')
        self._invalidate_cache()
        return {'name': new_name, 'path': new_rel, 'type': 'folder'}

    @x_ipe_tracing()
    def move_folder(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a folder to a new parent."""
        src = self._resolve_safe_path(source)
        dst_parent = self._resolve_safe_path(destination)
        if not src.is_dir():
            raise FileNotFoundError(f"Source folder not found: {source}")
        if not dst_parent.is_dir():
            raise FileNotFoundError(f"Destination folder not found: {destination}")
        dst = dst_parent / src.name
        # Prevent moving into self or descendant
        if dst.resolve().is_relative_to(src.resolve()):
            raise ValueError("Cannot move a folder into itself or a descendant")
        if dst.exists():
            raise FileExistsError(f"Destination already exists: {dst.name}")
        shutil.move(str(src), str(dst))
        new_rel = str(dst.relative_to(self.kb_root)).replace('\\', '/')
        self._invalidate_cache()
        return {'old_path': source, 'new_path': new_rel}

    @x_ipe_tracing()
    def delete_folder(self, rel_path: str) -> Dict[str, Any]:
        """Delete a folder and its contents recursively."""
        if not rel_path or rel_path == '' or rel_path == '.':
            raise PermissionError("Cannot delete KB root folder")
        target = self._resolve_safe_path(rel_path)
        if target.resolve() == self.kb_root.resolve():
            raise PermissionError("Cannot delete KB root folder")
        if not target.is_dir():
            raise FileNotFoundError(f"Folder not found: {rel_path}")
        count = sum(1 for _ in target.rglob('*') if _.is_file())
        shutil.rmtree(target)
        self._invalidate_cache()
        return {'deleted': rel_path, 'deleted_count': count}

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def get_config(self) -> Dict[str, Any]:
        """Read and return knowledgebase-config.json."""
        self.ensure_kb_root()
        try:
            raw = json.loads(self.config_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, IOError) as exc:
            raise RuntimeError(f"Invalid {KB_CONFIG_FILE}: {exc}") from exc
        return raw

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def search(self, query: str = '', tag: str = '',
               tag_type: str = '') -> List[KBNode]:
        """Search KB files by filename + frontmatter fields and/or tag."""
        self._ensure_file_index()
        results: List[KBNode] = []
        q = query.lower()

        for rel_path, fm in self._frontmatter_index.items():
            if self._matches(rel_path, fm, q, tag, tag_type):
                target = self.kb_root / rel_path
                if not target.is_file():
                    continue
                stat = target.stat()
                results.append(self._build_file_node(rel_path, target.name, stat, fm))
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_file_type(name: str) -> str:
        """Return the file type string for a given filename."""
        if name.endswith('.url.md'):
            return 'url_bookmark'
        return Path(name).suffix.lower()

    def _build_file_node(self, path: str, name: str,
                         stat: os.stat_result,
                         frontmatter: Optional[FrontmatterData]) -> KBNode:
        """Construct a KBNode for a file entry."""
        return KBNode(
            name=name,
            path=path,
            type='file',
            size_bytes=stat.st_size,
            modified_date=self._iso_mtime(stat),
            file_type=self._determine_file_type(name),
            frontmatter=frontmatter,
        )

    @staticmethod
    def _matches(rel_path: str, fm: Optional[FrontmatterData],
                 query: str, tag: str, tag_type: str) -> bool:
        """Return True if file matches the search criteria."""
        # Tag filter
        if tag and tag_type:
            if fm is None or fm.tags is None:
                return False
            tag_list = fm.tags.lifecycle if tag_type == 'lifecycle' else fm.tags.domain
            if tag not in tag_list:
                return False

        # Query filter (empty query matches all)
        if not query:
            return True

        filename = Path(rel_path).name.lower()
        if query in filename:
            return True
        if fm:
            if fm.title and query in fm.title.lower():
                return True
            if fm.author and query in fm.author.lower():
                return True
            if fm.tags:
                all_tags = [t.lower() for t in fm.tags.lifecycle + fm.tags.domain]
                if any(query in t for t in all_tags):
                    return True
        return False

    @staticmethod
    def _sort_files(files: List[KBNode], sort: str) -> List[KBNode]:
        if sort == 'name':
            return sorted(files, key=lambda f: f.name.lower())
        elif sort == 'created':
            return sorted(files, key=lambda f: (
                f.frontmatter.created if f.frontmatter and f.frontmatter.created else '',
            ), reverse=True)
        elif sort == 'untagged':
            def _untagged_key(f: KBNode) -> tuple:
                has_tags = bool(
                    f.frontmatter is not None
                    and f.frontmatter.tags is not None
                    and (len(f.frontmatter.tags.lifecycle) > 0
                         or len(f.frontmatter.tags.domain) > 0)
                )
                return (has_tags, f.name.lower())
            return sorted(files, key=_untagged_key)
        else:  # 'modified' (default)
            return sorted(files, key=lambda f: f.modified_date or '', reverse=True)

    @staticmethod
    def _iso_mtime(stat: os.stat_result) -> str:
        from datetime import datetime
        return datetime.fromtimestamp(stat.st_mtime).isoformat(timespec='seconds')

    def _validate_file_type(self, filename: str) -> None:
        """Raise ValueError for unsupported file types."""
        ext = Path(filename).suffix.lower()
        if not ext:
            raise ValueError("File must have an extension")
        allowed = self._get_allowed_extensions()
        if ext not in allowed:
            raise ValueError(f"Unsupported file type: {ext}")

    def _get_allowed_extensions(self) -> set:
        """Return allowed extensions from config (cached)."""
        if not hasattr(self, '_allowed_ext_cache'):
            try:
                raw = self.get_config()
                exts = raw.get('allowed_extensions', [])
                self._allowed_ext_cache = {e.lower() for e in exts} if exts else None
            except Exception:
                self._allowed_ext_cache = None
        return self._allowed_ext_cache or {e for e in KBConfig().allowed_extensions}

    @staticmethod
    def _check_size(content: str) -> None:
        if len(content.encode('utf-8')) > MAX_FILE_SIZE_BYTES:
            raise ValueError("File exceeds maximum size of 10MB")

    def _extract_archive_entries(self, entries, dest_folder, get_name, get_data, is_dir=None):
        """Shared loop for archive extraction (zip/7z).

        Args:
            entries: iterable of archive entries
            dest_folder: KB-relative destination folder
            get_name: callable(entry) -> str filename within archive
            get_data: callable(entry) -> bytes raw file content
            is_dir: callable(entry) -> bool (optional, skips dirs if provided)
        """
        results = []
        skip_exts = {'.zip', '.7z'}
        TEXT_EXTS = {'.md', '.txt', '.json', '.yaml', '.yml', '.csv',
                     '.html', '.htm', '.css', '.js', '.ts', '.xml',
                     '.toml', '.ini', '.cfg', '.sh', '.bat', '.py',
                     '.rb', '.java', '.go', '.rs', '.c', '.cpp', '.h'}
        for entry in entries:
            if is_dir and is_dir(entry):
                continue
            name = get_name(entry)
            ext = os.path.splitext(name)[1].lower()
            if ext in skip_exts:
                continue
            try:
                raw_data = get_data(entry)
                rel_path = f'{dest_folder}/{name}' if dest_folder else name
                parent = os.path.dirname(rel_path)
                if parent:
                    try:
                        self.create_folder(parent)
                    except FileExistsError:
                        pass
                if ext in TEXT_EXTS:
                    result = self.create_file(rel_path, raw_data.decode('utf-8', errors='replace'))
                else:
                    result = self.create_binary_file(rel_path, raw_data)
                results.append(result)
            except (FileExistsError, ValueError):
                pass
        return results

    @x_ipe_tracing()
    def extract_zip(self, zip_bytes: bytes, dest_folder: str = '') -> list:
        """Extract a .zip archive into the KB, preserving folder structure.
        Skips nested .zip/.7z archives within the ZIP."""
        import zipfile
        import io

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            return self._extract_archive_entries(
                entries=zf.infolist(),
                dest_folder=dest_folder,
                get_name=lambda info: info.filename,
                get_data=lambda info: zf.read(info.filename),
                is_dir=lambda info: info.is_dir(),
            )

    @x_ipe_tracing()
    def extract_7z(self, sevenz_bytes: bytes, dest_folder: str = '') -> list:
        """Extract a .7z archive into the KB, preserving folder structure.
        Skips nested .zip/.7z archives. Requires py7zr."""
        try:
            import py7zr
            import io
            with py7zr.SevenZipFile(io.BytesIO(sevenz_bytes), mode='r') as z:
                items = z.readall().items()
                return self._extract_archive_entries(
                    entries=items,
                    dest_folder=dest_folder,
                    get_name=lambda item: item[0],
                    get_data=lambda item: item[1].read(),
                )
        except ImportError:
            raise ValueError(".7z extraction requires py7zr library")

    # ------------------------------------------------------------------
    # Intake status management (FEATURE-049-F)
    # ------------------------------------------------------------------

    INTAKE_STATUS_FILE = '.intake-status.json'

    def _read_intake_status(self) -> Dict[str, Any]:
        """Read .intake-status.json from .intake/ folder.

        Returns empty dict on missing or corrupted file.
        """
        status_path = self.kb_root / INTAKE_FOLDER / self.INTAKE_STATUS_FILE
        if not status_path.exists():
            return {}
        try:
            with open(status_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                return {}
            return data
        except (json.JSONDecodeError, OSError):
            import logging
            logging.getLogger(__name__).warning(
                'Corrupted %s — treating all intake files as pending',
                status_path,
            )
            return {}

    def _write_intake_status(self, data: Dict[str, Any]) -> None:
        """Write intake status dict atomically."""
        status_path = self.kb_root / INTAKE_FOLDER / self.INTAKE_STATUS_FILE
        self._write_json(status_path, data)

    def _build_intake_tree(
        self, dir_path: Path, status_data: Dict[str, Any], depth: int = 0,
    ) -> List[Dict[str, Any]]:
        """Recursively build nested tree of .intake/ items (CR-005).

        Files get status from *status_data*; folders derive status from children.
        """
        intake_root = self.kb_root / INTAKE_FOLDER
        items: List[Dict[str, Any]] = []
        try:
            entries = sorted(
                dir_path.iterdir(),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            return items

        for entry in entries:
            if entry.name.startswith('.'):
                continue
            rel_path = str(entry.relative_to(intake_root))
            if entry.is_dir():
                children = self._build_intake_tree(entry, status_data, depth + 1)
                items.append({
                    'name': entry.name,
                    'path': rel_path,
                    'type': 'folder',
                    'item_count': len(children),
                    'status': self._derive_folder_status(children),
                    'children': children,
                })
            elif entry.is_file():
                stat = entry.stat()
                entry_status = status_data.get(rel_path, {})
                items.append({
                    'name': entry.name,
                    'path': rel_path,
                    'type': 'file',
                    'size_bytes': stat.st_size,
                    'modified_date': date.fromtimestamp(stat.st_mtime).isoformat(),
                    'file_type': entry.suffix.lstrip('.') if entry.suffix else '',
                    'status': entry_status.get('status', 'pending'),
                    'destination': entry_status.get('destination'),
                })
        return items

    @staticmethod
    def _derive_folder_status(children: List[Dict[str, Any]]) -> str:
        """Derive folder status from children: pending > processing > filed (CR-005)."""
        statuses: set[str] = set()
        for child in children:
            statuses.add(child.get('status', 'pending'))
        if 'pending' in statuses:
            return 'pending'
        if 'processing' in statuses:
            return 'processing'
        if 'filed' in statuses:
            return 'filed'
        return 'pending'  # empty folder defaults to pending

    def _count_pending_deep(self, items: List[Dict[str, Any]]) -> int:
        """Count all pending files across nested tree (CR-005)."""
        count = 0
        for item in items:
            if item.get('type') == 'file' and item.get('status') == 'pending':
                count += 1
            elif item.get('type') == 'folder':
                count += self._count_pending_deep(item.get('children', []))
        return count

    @x_ipe_tracing()
    def get_intake_files(self) -> Dict[str, Any]:
        """List .intake/ items as nested tree merged with status (CR-005).

        Returns ``{"items": [...], "stats": {...}, "pending_deep_count": N}``.
        """
        empty = {
            'items': [], 'stats': {'total': 0, 'pending': 0, 'processing': 0, 'filed': 0},
            'pending_deep_count': 0,
        }
        intake_dir = self.kb_root / INTAKE_FOLDER
        if not intake_dir.is_dir():
            return empty

        status_data = self._read_intake_status()
        items = self._build_intake_tree(intake_dir, status_data)

        stats = {
            'total': len(items),
            'pending': sum(1 for i in items if i['status'] == 'pending'),
            'processing': sum(1 for i in items if i['status'] == 'processing'),
            'filed': sum(1 for i in items if i['status'] == 'filed'),
        }
        return {
            'items': items,
            'stats': stats,
            'pending_deep_count': self._count_pending_deep(items),
        }

    @x_ipe_tracing()
    def update_intake_status(
        self, filename: str, status: str, destination: str | None = None
    ) -> Dict[str, Any]:
        """Update a file or folder's status in .intake-status.json (CR-005).

        *filename* may be a relative path (e.g. ``subfolder/file.md``).
        If *filename* points to a directory, cascades the update to all child
        files recursively.

        Raises ``ValueError`` if the path does not exist in ``.intake/``.
        """
        intake_dir = self.kb_root / INTAKE_FOLDER
        target_path = intake_dir / filename
        if not target_path.resolve().is_relative_to(intake_dir.resolve()):
            raise ValueError(f'Path not in .intake/: {filename}')
        if not target_path.exists():
            raise ValueError(f'Path not in .intake/: {filename}')

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        data = self._read_intake_status()

        if target_path.is_dir():
            # Cascade to all child files
            for child in target_path.rglob('*'):
                if child.is_file() and not child.name.startswith('.'):
                    rel = str(child.relative_to(intake_dir))
                    data[rel] = {
                        'status': status,
                        'destination': destination,
                        'updated_at': now,
                    }
        else:
            rel = str(target_path.relative_to(intake_dir))
            data[rel] = {
                'status': status,
                'destination': destination,
                'updated_at': now,
            }

        self._write_intake_status(data)
        self._invalidate_cache()
        return {'ok': True, 'filename': filename, 'status': status, 'destination': destination}
