"""
Utility Functions for the Library of Jörmungandr

Shared helper functions used across multiple tools.
These functions provide common operations like file handling,
validation, and data transformation.
"""

import re
import urllib.parse
from pathlib import Path
from typing import Optional, Union

def check_file_exists(filepath: Union[str, Path]) ->bool:
    """
    Check if a file exists at the given path.

    Args:
        filepath: Path to the file (string or Path object)

    Returns:
        bool: True if file exists, False otherwise
    """

    return Path(filepath).is_file()

def get_file_size(filepath: Union[str, Path]) -> Optional[int]:
    """
    Get the size of a file in bytes.

    Args:
        filepath: Path to the file

    Returns:
        int: File size in bytes, or None if file doesn't exist
    """

    try:
        return Path(filepath).stat().st_size
    except (FileNotFoundError, OSError):
        return None

def create_directory(dirpath: Union[str, Path], exist_ok: bool = True) -> bool:
    """
    Create a directory, including parent directories if needed.

    Args:
        dirpath: Path to the directory
        exist_ok: If True, don't raise error if directory exists

    Returns:
        bool: True if successful, False otherwise
    """

    try:
        Path(dirpath).mkdir(parents=True, exist_ok=exist_ok)
        return True
    except (PermissionError, OSError):
        return False
    
def validate_path(filepath: Union[str, Path]) -> bool:
    """
    Validate that a path is well-formed (not necessarily existing).

    Args:
        filepath: Path to validate

    Returns:
        bool: True if path is valid, False otherwise
    """

    try:
        Path(filepath).resolve()
        return True
    except (ValueError, OSError):
        return False
    
def is_safe_path(filepath: Union[str, Path], base_dir: Optional[Union[str, Path]] = None) -> bool:
    """
    Check if a path is safe (doesn't escape the base directory).

    This prevents directory traversal attacks like "../../etc/passwd"

    Args:
        filepath: Path to check
        base_dir: Base directory to restrict to (default: current directory)

    Returns:
        bool: True if path is safe, False otherwise
    """
    if base_dir is None:
        base_dir = Path.cwd()

    try:
        base = Path(base_dir).resolve()
        target = (Path(base_dir) / filepath).resolve()

        # Check if the target is within base directory
        return target.is_relative_to(base)
    except (ValueError, OSError):
        return False

def validate_email(email: str) -> bool:
    """
    Validate an email address (basic check).

    Args:
        email: Email address to validate

    Returns:
        bool: True if email looks valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """
    Validate a URL (basic check).

    Args:
        url: URL to validate

    Returns:
        bool: True if URL looks valid, False otherwise
    """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def clean_string(text: str) -> str:
    """
    Clean a string by removing extra whitespace

    Args:
        text: String to clean

    Returns:
        str: Cleaned string
    """
    # Replace tabs and newlines with spaces
    text = text.replace('\t', ' ').replace('\n', ' ').replace('\r',' ')

    # Remove multiple consecutive spaces
    text = ' '.join(text.split())

    # Remove leading/trailing whitespace
    return text.strip()

def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace within lines but preserve line breaks.

    Args:
        text: String to normalize

    Returns:
        str: Normalized string
    """
    lines = text.split('\n')
    cleaned_lines = [' '.join(line.split()) for line in lines]
    return '\n'.join(cleaned_lines)

def bytes_to_human_readable(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format (KB, MB, GB, etc.).
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Human-readable size
        
    Example:
        >>> bytes_to_human_readable(1024)
        '1.00 KB'
        >>> bytes_to_human_readable(1048576)
        '1.00 MB'
    """
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"
