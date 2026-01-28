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

# Tools Config Service (FEATURE-011)
from .tools_config_service import ToolsConfigService

# Themes Service (FEATURE-012)
from .themes_service import ThemesService

# Voice Input Service (FEATURE-021)
from .voice_input_service_v2 import (
    VoiceSession,
    VoiceInputService,
    is_voice_command,
    VOICE_MAX_DURATION,
)

# Proxy Service (FEATURE-022-A)
from .proxy_service import ProxyService, ProxyResult


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
    # Tools Config
    'ToolsConfigService',
    # Themes
    'ThemesService',
    # Voice Input
    'VoiceSession',
    'VoiceInputService',
    'is_voice_command',
    'VOICE_MAX_DURATION',
    # Proxy
    'ProxyService',
    'ProxyResult',
]
