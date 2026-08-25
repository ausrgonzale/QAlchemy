"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_relative_path.py

Purpose:
    Unit tests for the relative_path utility.

Description:
    Verifies that project-relative paths are returned when possible and that
    paths outside the current project are returned unchanged.

===============================================================================
"""

from pathlib import Path

from scripts.utils.relative_path import relative_path


class TestRelativePath:
    """
    Unit tests for the relative_path utility.
    """

    def test_returns_relative_path_within_project(self) -> None:
        """
        Should return a project-relative path.
        """

        path = Path.cwd() / "working" / "input" / "system.md"

        result = relative_path(path)

        assert result == Path("working/input/system.md")

    def test_returns_original_path_outside_project(self) -> None:
        """
        Should return the original path when it is outside the project.
        """

        path = Path("/tmp/example.md")

        result = relative_path(path)

        assert result == path

    def test_returns_current_directory_relative(self) -> None:
        """
        Should return '.' when given the current working directory.
        """

        result = relative_path(Path.cwd())

        assert result == Path(".")
