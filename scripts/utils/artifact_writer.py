"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    artifact_writer.py

Purpose:
    Persists GeneratedArtifact objects to an output directory.

Description:
    ArtifactWriter resolves each GeneratedArtifact relative path against the
    supplied output root and delegates file persistence to FileWriter.

Responsibilities
----------------
- Resolve artifact relative paths against the output root.
- Delegate artifact content to FileWriter.
- Write multiple generated artifacts.

Non-Responsibilities
--------------------
This utility does NOT:

- Create WorkSpaces.
- Determine the output root.
- Parse Deliverables.
- Normalize provider responses.
- Invoke AI providers.
- Generate artifacts.
- Perform orchestration.

===============================================================================
"""

from pathlib import Path

from scripts.utils.create_generated_artifacts import GeneratedArtifact
from scripts.utils.file_writer import FileWriter


class ArtifactWriter:
    """
    Persists GeneratedArtifact objects to an output directory.
    """

    def __init__(
        self,
        file_writer: FileWriter | None = None,
    ) -> None:
        """
        Initialize the ArtifactWriter.
        """

        self._file_writer = file_writer or FileWriter()

    def write(
        self,
        artifacts: tuple[GeneratedArtifact, ...],
        output_root: Path,
    ) -> None:
        """
        Write generated artifacts relative to the supplied output root.
        """

        for artifact in artifacts:
            output_path = output_root / artifact.relative_path

            self._file_writer.write(
                path=output_path,
                content=artifact.content,
            )
