"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    source_code_resolver.py

Purpose
-------
Resolves runtime source-code locations into concrete source files.

Description
-----------
SourceCodeResolver accepts files and directories supplied at runtime and
returns the concrete source files that a feature workflow should consume.

A file is returned directly.

A directory is searched recursively for supported source files.

Responsibilities
----------------
- Resolve source-code files.
- Resolve source-code directories.
- Recursively discover supported source files.
- Return deterministic file ordering.

Non-Responsibilities
--------------------
This utility does NOT:

- Read source-code contents.
- Copy source files.
- Write files.
- Modify source files.
- Create WorkSpaces.
- Build WorkOrders.
- Execute Feature Services.
- Invoke AI clients.

===============================================================================
"""

from pathlib import Path
from typing import ClassVar


class SourceCodeResolver:
    """
    Resolves runtime source-code locations into concrete source files.
    """

    _SUPPORTED_SUFFIXES: ClassVar[frozenset[str]] = frozenset(
        {".py"},
    )

    def resolve(
        self,
        paths: list[Path],
    ) -> list[Path]:
        """
        Resolve files and directories into concrete source files.
        """

        resolved: list[Path] = []

        for path in paths:
            if path.is_file():
                resolved.append(path)
                continue

            if path.is_dir():
                resolved.extend(
                    self._resolve_directory(path),
                )
                continue

            raise FileNotFoundError(
                f"Source code path does not exist: {path}",
            )

        return resolved

    def _resolve_directory(
        self,
        directory: Path,
    ) -> list[Path]:
        """
        Recursively resolve supported source files from a directory.
        """

        return sorted(
            path
            for path in directory.rglob("*")
            if path.is_file() and path.suffix.lower() in self._SUPPORTED_SUFFIXES
        )
