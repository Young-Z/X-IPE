"""
Services Package

Re-exports all services for backward compatibility.
Import from this module maintains the same API as the original services.py
"""

# Config Service (FEATURE-010)
from .config_service import (
    ConfigData,
    ConfigService,
    CONFIG_FILE_NAME,
    MAX_PARENT_LEVELS,
)

# File Service (FEATURE-001)
from .file_service import (
    FileNode,
    Section,
    ProjectService,
    FileWatcherHandler,
    FileWatcher,
    ContentService,
)

# Ideas Service (FEATURE-008)
from .ideas_service import IdeasService

# Terminal Service (FEATURE-005)
from .terminal_service import (
    OutputBuffer,
    PersistentSession,
    SessionManager,
    PTYSession,
    session_manager,
    BUFFER_MAX_CHARS,
    SESSION_TIMEOUT,
    CLEANUP_INTERVAL,
)

# Settings Service (FEATURE-006)
from .settings_service import (
    SettingsService,
    ProjectFoldersService,
)

# Skills Service
from .skills_service import SkillsService


__all__ = [
    # Config
    'ConfigData',
    'ConfigService',
    'CONFIG_FILE_NAME',
    'MAX_PARENT_LEVELS',
    # File
    'FileNode',
    'Section',
    'ProjectService',
    'FileWatcherHandler',
    'FileWatcher',
    'ContentService',
    # Ideas
    'IdeasService',
    # Terminal
    'OutputBuffer',
    'PersistentSession',
    'SessionManager',
    'PTYSession',
    'session_manager',
    'BUFFER_MAX_CHARS',
    'SESSION_TIMEOUT',
    'CLEANUP_INTERVAL',
    # Settings
    'SettingsService',
    'ProjectFoldersService',
    # Skills
    'SkillsService',
]
