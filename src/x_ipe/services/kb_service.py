"""
FEATURE-049-A: KB Backend & Storage Foundation

KBService: File/folder CRUD, tree building, search, frontmatter parsing, config management.
KBNode: Tree node data model (file or folder).
FrontmatterData / TagSet: Parsed YAML frontmatter models.
KBConfig: kb-config.json schema + defaults.
"""
import json
import os
import shutil
import tempfile
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
KB_CONFIG_FILE = 'kb-config.json'
INTAKE_FOLDER = '.intake'

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

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
    tags: Optional[TagSet] = None
    author: Optional[str] = None
    created: Optional[str] = None
    auto_generated: bool = False
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'title': self.title,
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
    """kb-config.json schema."""
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
    ai_librarian: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': False,
        'intake_folder': '.intake',
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tags': self.tags,
            'agent_write_allowlist': self.agent_write_allowlist,
            'ai_librarian': self.ai_librarian,
        }


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class KBService:
    """Service for managing the Knowledge Base file system and metadata."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.kb_root = self.project_root / KB_ROOT_DIR
        self._tree_cache: Optional[List[KBNode]] = None
        self._frontmatter_index: Dict[str, Optional[FrontmatterData]] = {}
        self._cache_valid = False

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def ensure_kb_root(self) -> None:
        """Create KB root directory and default kb-config.json if missing."""
        self.kb_root.mkdir(parents=True, exist_ok=True)
        config_path = self.kb_root / KB_CONFIG_FILE
        if not config_path.exists():
            default_config = KBConfig()
            self._write_json(config_path, default_config.to_dict())

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
        self._frontmatter_index.clear()

    def _ensure_file_index(self) -> None:
        """Rebuild the in-memory tree cache and frontmatter index if stale."""
        if self._cache_valid and self._tree_cache is not None:
            return
        self.ensure_kb_root()
        self._tree_cache = self._build_tree(self.kb_root, '')
        self._cache_valid = True

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

        for entry in entries:
            name = entry.name
            if name == INTAKE_FOLDER:
                continue
            if name == KB_CONFIG_FILE and rel_base == '':
                continue  # skip config from tree

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
        for entry in entries:
            if not entry.is_file():
                continue
            rel = str(entry.relative_to(self.kb_root)).replace('\\', '/')
            if entry.name == KB_CONFIG_FILE:
                continue
            stat = entry.stat()
            fm = self._frontmatter_index.get(rel) or self._parse_frontmatter_safe(entry)
            files.append(self._build_file_node(rel, entry.name, stat, fm))
        return self._sort_files(files, sort)

    # ------------------------------------------------------------------
    # File CRUD
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def get_file(self, rel_path: str) -> Dict[str, Any]:
        """Read a single file — content + frontmatter."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {rel_path}")
        stat = target.stat()
        file_type = self._determine_file_type(target.name)
        # Binary files: return metadata only (no content/frontmatter)
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
                'frontmatter': None,
                'size_bytes': stat.st_size,
                'modified_date': self._iso_mtime(stat),
                'file_type': file_type,
                'binary': True,
            }
        content = target.read_text(encoding='utf-8')
        fm = self._parse_frontmatter_safe(target)
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
        """Create a new KB file with auto-populated frontmatter."""
        target = self._resolve_safe_path(rel_path)
        self._validate_file_type(target.name)
        if target.exists():
            raise FileExistsError(f"File already exists: {rel_path}")

        # URL bookmark validation
        if target.name.endswith('.url.md'):
            if not frontmatter or not frontmatter.get('url'):
                raise ValueError("URL bookmark files require a 'url' field in frontmatter")

        fm = self._auto_populate_frontmatter(frontmatter, target.name)
        if target.suffix.lower() == '.md':
            file_content = self._serialize_frontmatter(fm, content)
        else:
            file_content = content

        self._check_size(file_content)
        self._write_file_atomic(target, file_content)
        self._invalidate_cache()
        return self.get_file(rel_path)

    @x_ipe_tracing()
    def create_binary_file(self, rel_path: str, data: bytes) -> Dict[str, Any]:
        """Create a new binary KB file (images, PDFs, etc.)."""
        target = self._resolve_safe_path(rel_path)
        self._validate_file_type(target.name)
        if target.exists():
            raise FileExistsError(f"File already exists: {rel_path}")
        if len(data) > MAX_FILE_SIZE_BYTES:
            raise ValueError("File exceeds maximum size of 10MB")
        self._write_binary_atomic(target, data)
        self._invalidate_cache()
        stat = target.stat()
        return {
            'name': target.name,
            'path': rel_path,
            'size_bytes': stat.st_size,
            'modified_date': self._iso_mtime(stat),
            'file_type': self._determine_file_type(target.name),
        }

    @x_ipe_tracing()
    def update_file(self, rel_path: str, content: Optional[str] = None,
                    frontmatter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update file content and/or frontmatter."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {rel_path}")

        existing_content = target.read_text(encoding='utf-8')
        existing_fm = self._parse_frontmatter_safe(target)

        body = content if content is not None else self._extract_body(existing_content)

        if frontmatter is not None:
            fm = self._auto_populate_frontmatter(frontmatter, target.name)
        elif existing_fm is not None:
            fm = existing_fm
        else:
            fm = self._auto_populate_frontmatter(None, target.name)

        if target.suffix.lower() == '.md':
            file_content = self._serialize_frontmatter(fm, body)
        else:
            file_content = body

        self._check_size(file_content)
        self._write_file_atomic(target, file_content)
        self._invalidate_cache()
        return self.get_file(rel_path)

    @x_ipe_tracing()
    def delete_file(self, rel_path: str) -> None:
        """Delete a file."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {rel_path}")
        target.unlink()
        self._invalidate_cache()

    @x_ipe_tracing()
    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a file to a new path."""
        src = self._resolve_safe_path(source)
        dst = self._resolve_safe_path(destination)
        if not src.is_file():
            raise FileNotFoundError(f"Source file not found: {source}")
        if not dst.parent.is_dir():
            raise FileNotFoundError(f"Destination folder not found: {str(dst.parent.relative_to(self.kb_root))}")
        if dst.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        shutil.move(str(src), str(dst))
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
        """Read and return kb-config.json."""
        self.ensure_kb_root()
        config_path = self.kb_root / KB_CONFIG_FILE
        try:
            raw = json.loads(config_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, IOError) as exc:
            raise RuntimeError(f"Invalid kb-config.json: {exc}") from exc
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

    @staticmethod
    def _validate_file_type(filename: str) -> None:
        """Raise ValueError for unsupported file types."""
        if not Path(filename).suffix:
            raise ValueError("File must have an extension")

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
