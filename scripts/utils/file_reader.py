"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    file_reader.py

Purpose:
    Provides a reusable file reading utility for QAlchemy.

Description:
    The FileReader centralizes file input operations for the application.
    It is responsible for reading UTF-8 text files from disk and returning
    their contents.

Current Consumers:
    - WorkOrderBuilderService

Future Consumers:
    - OrchestrationService
    - GenerateCodeService
    - ReviewCodeService
    - EvaluateRequirementService
    - GenerateTestCaseService
    - AnalyzeDefectService

===============================================================================
"""

from pathlib import Path


class FileReader:
    """
    Utility for reading text files.

    Responsibilities:
        - Read UTF-8 text files.
        - Return file contents.

    This class intentionally performs no parsing or business logic.
    """

    def read(
        self,
        path: Path,
    ) -> str:
        """
        Read the contents of a text file.

        Args:
            path:
                Source file.

        Returns:
            The contents of the file.
        """

        return path.read_text(
            encoding="utf-8",
        )

    def read_many(
        self,
        paths: list[Path],
    ) -> str:
        """
        Read multiple UTF-8 text files.

        Args:
            paths:
                Source files.

        Returns:
            The concatenated contents of the files separated by blank lines.
        """

        return "\n\n".join(self.read(path) for path in paths)
