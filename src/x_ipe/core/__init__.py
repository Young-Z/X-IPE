"""
X-IPE Core Modules

Provides foundational utilities for:
- Configuration management
- File hashing
- Path resolution
- Project scaffolding
- Skills management
"""

from .config import XIPEConfig
from .hashing import hash_file, hash_directory
from .paths import resolve_path, get_project_root
from .scaffold import ScaffoldManager
from .skills import SkillInfo, SkillsManager

__all__ = [
    'XIPEConfig',
    'hash_file',
    'hash_directory',
    'resolve_path',
    'get_project_root',
    'ScaffoldManager',
    'SkillInfo',
    'SkillsManager',
]
