"""
===============================================================================
File Descriptor Header
===============================================================================
File: file_writer_service.py

Purpose:
    Provides a centralized service for writing generated project artifacts
    to the filesystem.

    This service is responsible for taking a collection of generated
    artifacts produced by the AI generation workflow and writing each
    artifact to its destination within a specified output directory.

Responsibilities:
    - Validate generated artifacts.
    - Create required output directories.
    - Write generated files to disk.
    - Log written artifacts.

Design Notes:
    FileWriterService performs file output only.

    It does not communicate with AI providers, parse AI responses, or modify
    generated content. Parsing AI responses is the responsibility of
    ArtifactParserService.

Dependencies:
    - pathlib.Path
    - scripts.core.generated_artifact.GeneratedArtifact

Author:
    Ron Gonzalez

Created:
    July 2026
===============================================================================
"""

import logging
from pathlib import Path

from scripts.core.generate_artifacts import GeneratedArtifact

logger = logging.getLogger(__name__)


class FileWriterService:
    """
    Writes generated project artifacts to the filesystem.

    This service accepts a collection of GeneratedArtifact objects and writes
    each artifact to its destination beneath a specified output directory.
    """

    @staticmethod
    def write(
        artifacts: list[GeneratedArtifact],
        output_directory: Path,
    ) -> None:
        """
        Write generated artifacts to the specified output directory.

        Args:
            artifacts:
                Collection of generated artifacts to write.

            output_directory:
                Root directory where generated artifacts will be written.

        Raises:
            TypeError:
                Raised when the output directory is not a Path instance.

            ValueError:
                Raised when the artifact collection is empty.
        """

        logger.info("Starting artifact write operation.")

        if not isinstance(output_directory, Path):
            raise TypeError("output_directory must be a pathlib.Path instance.")

        if not artifacts:
            raise ValueError("No generated artifacts were provided.")

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        for artifact in artifacts:
            destination = output_directory / artifact.relative_path

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination.write_text(
                artifact.content,
                encoding="utf-8",
            )

            logger.info("Generated artifact written: %s", destination)

        logger.info(
            "Artifact write operation completed successfully. Wrote %d artifact(s).",
            len(artifacts),
        )
