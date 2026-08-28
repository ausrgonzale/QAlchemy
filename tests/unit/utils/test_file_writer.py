"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_file_writer.py

Purpose:
    Provides unit tests for the FileWriter utility.

Description:
    Verifies that FileWriter correctly creates parent directories and writes
    UTF-8 text content to files.

===============================================================================
"""

from pathlib import Path

from scripts.utils.file_writer import FileWriter


def test_write_creates_parent_directories(
    tmp_path: Path,
) -> None:
    writer = FileWriter()

    output_path = tmp_path / "nested" / "directory" / "output.txt"

    writer.write(
        path=output_path,
        content="Hello, QAlchemy.",
    )

    assert output_path.parent.exists()


def test_write_creates_file(
    tmp_path: Path,
) -> None:
    writer = FileWriter()

    output_path = tmp_path / "output.txt"

    writer.write(
        path=output_path,
        content="Hello, QAlchemy.",
    )

    assert output_path.is_file()


def test_write_writes_expected_content(
    tmp_path: Path,
) -> None:
    writer = FileWriter()

    output_path = tmp_path / "output.txt"

    expected_content = "Hello, QAlchemy."

    writer.write(
        path=output_path,
        content=expected_content,
    )

    assert (
        output_path.read_text(
            encoding="utf-8",
        )
        == expected_content
    )


def test_write_uses_utf8_encoding(
    tmp_path: Path,
) -> None:
    writer = FileWriter()

    output_path = tmp_path / "output.txt"

    expected_content = "QAlchemy supports UTF-8: " "café, 日本語, 🚀"

    writer.write(
        path=output_path,
        content=expected_content,
    )

    assert (
        output_path.read_text(
            encoding="utf-8",
        )
        == expected_content
    )


def test_write_overwrites_existing_file(
    tmp_path: Path,
) -> None:
    writer = FileWriter()

    output_path = tmp_path / "output.txt"

    output_path.write_text(
        "Original content.",
        encoding="utf-8",
    )

    expected_content = "Replacement content."

    writer.write(
        path=output_path,
        content=expected_content,
    )

    assert (
        output_path.read_text(
            encoding="utf-8",
        )
        == expected_content
    )
