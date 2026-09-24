"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    read_file_tool.py

Purpose:
    Provides a common file-reading capability for QAlchemy Agents.

Description:
    ReadFileTool exposes the existing QAlchemy FileReader as an Agent-facing
    tool. It allows an Agent to retrieve the contents of a referenced file
    when additional artifact context is required to perform its task.

    The tool delegates file access to the shared FileReader infrastructure and
    returns the file contents as text. It does not interpret, parse, transform,
    or reason about the file contents.

Usage:
    An Agent provides the path to a required file:

        Agent
            ↓
        ReadFileTool
            ↓
        FileReader
            ↓
        File contents

    The returned content is then available to the Agent as input for further
    processing or model reasoning.

Responsibilities:
    - Accept filesystem paths from an Agent.
    - List files contained directly within a directory.
    - Delegate file reading to FileReader.
    - Return directory entries and file contents to the Agent.

Non-Responsibilities:
    - Parse file contents.
    - Interpret file contents.
    - Determine which files an Agent should read.
    - Determine which template an Agent should use.
    - Manage Agent workflow.
    - Access external systems.
    - Replace the shared FileReader implementation.

Dependencies:
    - FileReader

===============================================================================
"""

from pathlib import Path

from scripts.utils.file_reader import FileReader
from scripts.utils.path_utils import project_path


class ReadFileTool:
    """Provides file-reading capability to Agents."""

    def __init__(self, file_reader: FileReader | None = None) -> None:
        """Initialize the Read File Tool."""

        self._file_reader = file_reader or FileReader()

    def list_directory(
        self,
        path: Path,
    ) -> tuple[Path, ...]:
        """
        List files in a directory.

        Args:
            path:
                Directory to inspect.

        Returns:
            Files contained directly within the directory.
        """

        resolved_path = project_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(f"Path does not exist: {resolved_path}")

        if not resolved_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {resolved_path}")

        return tuple(sorted(item for item in resolved_path.iterdir() if item.is_file()))

    def read_file(self, path: Path) -> str:
        """Read and return the contents of a file."""

        resolved_path = project_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(f"Path does not exist: {resolved_path}")

        if not resolved_path.is_file():
            raise IsADirectoryError(f"Path is not a file: {resolved_path}")

        return self._file_reader.read(resolved_path)
