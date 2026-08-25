"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_artifact_writer.py

Purpose:
    Validates persistence of GeneratedArtifact objects.

Description:
    These tests verify that ArtifactWriter resolves GeneratedArtifact relative
    paths against an output root and delegates file persistence to FileWriter.

Responsibilities
----------------
- Verify GeneratedArtifact content is written.
- Verify relative artifact paths are preserved.
- Verify parent directories are created.
- Verify multiple artifacts can be written.

Non-Responsibilities
--------------------
These tests do NOT:

- Create WorkSpaces.
- Determine WorkSpace locations.
- Parse Deliverables.
- Normalize provider responses.
- Invoke AI providers.
- Test FileWriter implementation.

===============================================================================
"""

from pathlib import Path

from scripts.utils.artifact_writer import ArtifactWriter
from scripts.utils.create_generated_artifacts import GeneratedArtifact


def test_writes_generated_artifact_to_output_root(
    tmp_path: Path,
) -> None:
    """Write a generated artifact relative to the output root."""

    artifact = GeneratedArtifact(
        relative_path="pages/google_search_page.py",
        content="print('Google Search')",
    )

    output_root = tmp_path / "WO001" / "output"

    writer = ArtifactWriter()

    writer.write(
        artifacts=(artifact,),
        output_root=output_root,
    )

    output_file = output_root / "pages/google_search_page.py"

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == ("print('Google Search')")


def test_writes_multiple_generated_artifacts(
    tmp_path: Path,
) -> None:
    """Write multiple generated artifacts under the output root."""

    artifacts = (
        GeneratedArtifact(
            relative_path="pages/google_search_page.py",
            content="class GoogleSearchPage:\n    pass",
        ),
        GeneratedArtifact(
            relative_path="tests/test_google_search.py",
            content="def test_google_search():\n    pass",
        ),
    )

    output_root = tmp_path / "WO001" / "output"

    writer = ArtifactWriter()

    writer.write(
        artifacts=artifacts,
        output_root=output_root,
    )

    assert (output_root / "pages/google_search_page.py").read_text(
        encoding="utf-8"
    ) == ("class GoogleSearchPage:\n    pass")

    assert (output_root / "tests/test_google_search.py").read_text(
        encoding="utf-8"
    ) == ("def test_google_search():\n    pass")
