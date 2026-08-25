"""
Path utilities.

Provides helper functions for working with project-relative filesystem paths.
These helpers are intended for display, logging, reporting, and validation
output where relative paths are preferred over absolute paths.

The functions in this module are stateless and may be used throughout the
QAlchemy application.
"""

from pathlib import Path


def relative_path(path: Path) -> Path:
    """
    Return a project-relative path when possible.

    Falls back to the absolute path when the supplied path
    is outside the project directory.
    """
    try:
        return path.relative_to(Path.cwd())
    except ValueError:
        return path
