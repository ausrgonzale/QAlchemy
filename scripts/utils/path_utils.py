"""
Path utilities.

Provides helper functions for resolving and displaying
QAlchemy project-relative filesystem paths.

These helpers are stateless and may be used throughout
the QAlchemy application.
"""

from pathlib import Path


def project_root() -> Path:
    """
    Return the QAlchemy project root directory.
    """
    return Path(__file__).parents[2]


def agent_resource_root() -> Path:
    """
    Return the QAlchemy Agent Resource Root directory.
    """
    return project_root() / "agents"


def project_path(path: str | Path) -> Path:
    """
    Resolve a QAlchemy project-relative or application-relative path.
    """
    path = str(path).replace("\u200b", "").strip()
    path = Path(path)

    if path.is_absolute():
        return path

    return project_root() / path
