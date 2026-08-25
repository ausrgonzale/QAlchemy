"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    file_writer.py

Purpose:
    Provides a reusable file writing utility for QAlchemy.

Description:
    The FileWriter centralizes file output operations for the application.
    It is responsible for creating parent directories as needed and writing
    text content to disk using UTF-8 encoding.

Current Consumers:
    - OrchestrationService

Future Consumers:
    - ReportWriter
    - WorkOrderBuilderService
    - GenerateCodeService
    - ReviewCodeService
    - EvaluateRequirementService
    - GenerateTestCaseService
    - AnalyzeDefectService

===============================================================================
"""

from pathlib import Path


class FileWriter:
    """
    Utility for writing text files.

    Responsibilities:
        - Create parent directories.
        - Write UTF-8 text files.
        - Overwrite existing files.

    This class intentionally performs no formatting or business logic.
    """

    def write(
        self,
        path: Path,
        content: str,
    ) -> None:
        """
        Write text content to a file.

        Args:
            path:
                Destination file.

            content:
                Text to write.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )
