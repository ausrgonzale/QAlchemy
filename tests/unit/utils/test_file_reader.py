"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_file_reader.py

Purpose:
    Unit tests for the FileReader utility.

Description:
    Verifies that FileReader correctly reads UTF-8 text files and raises
    appropriate exceptions for invalid input.

===============================================================================
"""

from pathlib import Path

import pytest

from scripts.utils.file_reader import FileReader


class TestFileReader:
    """
    Unit tests for the FileReader utility.
    """

    def test_reads_existing_file(self, tmp_path: Path) -> None:
        """
        Should read the contents of an existing file.
        """

        file = tmp_path / "sample.txt"
        file.write_text("Hello QAlchemy", encoding="utf-8")

        reader = FileReader()

        result = reader.read(file)

        assert result == "Hello QAlchemy"

    def test_reads_empty_file(self, tmp_path: Path) -> None:
        """
        Should successfully read an empty file.
        """

        file = tmp_path / "empty.txt"
        file.write_text("", encoding="utf-8")

        reader = FileReader()

        result = reader.read(file)

        assert result == ""

    def test_reads_utf8_content(self, tmp_path: Path) -> None:
        """
        Should correctly read UTF-8 encoded content.
        """

        expected = "Café • QAlchemy • ✓"

        file = tmp_path / "utf8.txt"
        file.write_text(expected, encoding="utf-8")

        reader = FileReader()

        result = reader.read(file)

        assert result == expected

    def test_missing_file_raises_file_not_found(self, tmp_path: Path) -> None:
        """
        Should raise FileNotFoundError for a missing file.
        """

        reader = FileReader()

        missing = tmp_path / "missing.txt"

        with pytest.raises(FileNotFoundError):
            reader.read(missing)

    def test_read_many_single_file(
        self,
        tmp_path: Path,
    ) -> None:
        """
        Should read a single file using read_many().
        """

        file = tmp_path / "sample.txt"
        file.write_text("Hello QAlchemy", encoding="utf-8")

        reader = FileReader()

        result = reader.read_many([file])

        assert result == "Hello QAlchemy"

    def test_read_many_multiple_files(
        self,
        tmp_path: Path,
    ) -> None:
        """
        Should concatenate multiple files in order.
        """

        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"

        file1.write_text("System", encoding="utf-8")
        file2.write_text("User", encoding="utf-8")
        file3.write_text("Context", encoding="utf-8")

        reader = FileReader()

        result = reader.read_many(
            [
                file1,
                file2,
                file3,
            ]
        )

        assert result == "System\n\nUser\n\nContext"

    def test_read_many_empty_list(self) -> None:
        """
        Should return an empty string when no files are supplied.
        """

        reader = FileReader()

        result = reader.read_many([])

        assert result == ""

    def test_read_many_missing_file_raises_file_not_found(
        self,
        tmp_path: Path,
    ) -> None:
        """
        Should raise FileNotFoundError when any file is missing.
        """

        existing = tmp_path / "existing.txt"
        existing.write_text("Hello", encoding="utf-8")

        missing = tmp_path / "missing.txt"

        reader = FileReader()

        with pytest.raises(FileNotFoundError):
            reader.read_many(
                [
                    existing,
                    missing,
                ]
            )
