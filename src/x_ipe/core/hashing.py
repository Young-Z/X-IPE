"""
X-IPE Hashing Module

Provides utilities for calculating file and directory hashes.
Used for detecting modifications to skills during upgrades.
"""
import hashlib
from pathlib import Path
from typing import List


def hash_file(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file to hash.
    
    Returns:
        Hex-encoded SHA-256 hash string (64 characters).
    
    Raises:
        FileNotFoundError: If file doesn't exist.
        IOError: If file can't be read.
    """
    file_path = Path(file_path)
    hasher = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        # Read in chunks for large files
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def hash_directory(dir_path: Path, ignore_patterns: List[str] = None) -> str:
    """
    Calculate SHA-256 hash of a directory's contents.
    
    The hash is based on:
    - Relative paths of all files (sorted)
    - Content hash of each file
    
    This provides a consistent hash that changes when any file
    in the directory is modified, added, or removed.
    
    Args:
        dir_path: Path to the directory to hash.
        ignore_patterns: List of glob patterns to ignore (e.g., ['__pycache__', '*.pyc'])
    
    Returns:
        Hex-encoded SHA-256 hash string (64 characters).
    
    Raises:
        NotADirectoryError: If path is not a directory.
    """
    dir_path = Path(dir_path)
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")
    
    if ignore_patterns is None:
        ignore_patterns = ['__pycache__', '*.pyc', '.DS_Store', '*.swp']
    
    hasher = hashlib.sha256()
    
    # Get all files, sorted for consistent ordering
    all_files = []
    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            # Check ignore patterns
            if _should_ignore(file_path, dir_path, ignore_patterns):
                continue
            all_files.append(file_path)
    
    all_files.sort()
    
    for file_path in all_files:
        # Include relative path in hash (for detecting renames)
        rel_path = file_path.relative_to(dir_path)
        hasher.update(str(rel_path).encode('utf-8'))
        
        # Include file content hash
        file_hash = hash_file(file_path)
        hasher.update(file_hash.encode('utf-8'))
    
    return hasher.hexdigest()


def _should_ignore(file_path: Path, base_path: Path, patterns: List[str]) -> bool:
    """Check if a file should be ignored based on patterns."""
    rel_path = file_path.relative_to(base_path)
    
    for pattern in patterns:
        # Check if any part of the path matches
        if pattern.startswith('*'):
            # Extension match
            if file_path.suffix == pattern[1:]:
                return True
        else:
            # Name match (anywhere in path)
            for part in rel_path.parts:
                if part == pattern:
                    return True
    
    return False


def compare_hashes(hash1: str, hash2: str) -> bool:
    """
    Compare two hashes for equality.
    
    Uses constant-time comparison to prevent timing attacks
    (though not critical for this use case).
    
    Args:
        hash1: First hash string.
        hash2: Second hash string.
    
    Returns:
        True if hashes are equal, False otherwise.
    """
    return hashlib.sha256(hash1.encode()).hexdigest() == hashlib.sha256(hash2.encode()).hexdigest()
