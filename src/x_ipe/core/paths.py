"""
X-IPE Path Utilities

Provides utilities for path resolution and project root detection.
"""
from pathlib import Path
from typing import Optional


def resolve_path(path: str, base: Path = None) -> Path:
    """
    Resolve a path, making it absolute.
    
    Args:
        path: Path string to resolve (can be relative or absolute).
        base: Base directory for relative paths. Defaults to cwd.
    
    Returns:
        Absolute Path object.
    """
    path_obj = Path(path)
    
    if path_obj.is_absolute():
        return path_obj.resolve()
    
    if base is None:
        base = Path.cwd()
    
    return (base / path_obj).resolve()


def get_project_root(start_dir: Path = None) -> Optional[Path]:
    """
    Find the project root by looking for indicator files.
    
    Searches for:
    1. .x-ipe.yaml (X-IPE config)
    2. .x-ipe/ directory
    3. .git/ directory (fallback)
    
    Args:
        start_dir: Directory to start searching from. Defaults to cwd.
    
    Returns:
        Project root Path, or None if not found.
    """
    if start_dir is None:
        start_dir = Path.cwd()
    
    start_dir = Path(start_dir).resolve()
    current = start_dir
    
    # Search up to 20 levels (prevent infinite loop)
    for _ in range(20):
        # Check for X-IPE indicators
        if (current / ".x-ipe.yaml").exists():
            return current
        if (current / ".x-ipe").is_dir():
            return current
        
        # Fallback to git root
        if (current / ".git").is_dir():
            return current
        
        # Move up one level
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    
    return None


def is_initialized(project_root: Path) -> bool:
    """
    Check if a directory has X-IPE initialized.
    
    A directory is considered initialized if it has:
    - .x-ipe/ directory, OR
    - .x-ipe.yaml file
    
    Args:
        project_root: Directory to check.
    
    Returns:
        True if initialized, False otherwise.
    """
    project_root = Path(project_root)
    
    return (
        (project_root / ".x-ipe").is_dir() or
        (project_root / ".x-ipe.yaml").is_file()
    )


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists.
    
    Returns:
        The path (for chaining).
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
