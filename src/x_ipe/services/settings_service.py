"""
FEATURE-006: Settings & Configuration

SettingsService: Application settings with SQLite persistence
ProjectFoldersService: Multi-project folder management
"""
import os
import sqlite3
from typing import Dict, List, Optional, Any


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
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _ensure_table(self) -> None:
        """Create settings table if it doesn't exist."""
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
