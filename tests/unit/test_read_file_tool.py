"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_read_file_tool.py

Purpose:
    Provides unit tests for the QAlchemy ReadFileTool.

Description:
    Validates the common Agent-facing file-reading capability provided by
    ReadFileTool.

    These tests verify that ReadFileTool correctly delegates file access to
    the shared FileReader infrastructure and returns the file contents
    unchanged.

    The tests focus on the Tool boundary and do not test the internal
    implementation of FileReader.

Responsibilities:
    - Verify ReadFileTool can be initialized with a FileReader.
    - Verify the requested file path is passed to FileReader.
    - Verify file contents returned by FileReader are returned unchanged.

Non-Responsibilities:
    - Test FileReader implementation details.
    - Test JSON parsing.
    - Test file content interpretation.
    - Test RequirementsAgent behavior.
    - Test model interaction.
    - Test external systems.

Test Organization:
    - File Reading
    - Response Handling

Pytest Markers:
    - agent

===============================================================================
"""

from unittest.mock import Mock

import pytest

from agents.tools.read_file_tool import ReadFileTool

pytestmark = [pytest.mark.agent, pytest.mark.tools]


class TestReadFileTool:
    """Tests for ReadFileTool."""

    def test_lists_files_in_directory(self, tmp_path):
        templates_path = tmp_path / "templates"
        templates_path.mkdir()

        template_one = templates_path / "template_one.md"
        template_two = templates_path / "template_two.md"
        templates_path.joinpath("subdirectory").mkdir()

        template_one.write_text("template one")
        template_two.write_text("template two")

        tool = ReadFileTool()

        result = tool.list_directory(templates_path)

        assert result == (
            template_one,
            template_two,
        )

    def test_lists_files_only(self, tmp_path):
        templates_path = tmp_path / "templates"
        templates_path.mkdir()

        template = templates_path / "template.md"
        subdirectory = templates_path / "subdirectory"

        template.write_text("template")
        subdirectory.mkdir()

        tool = ReadFileTool()

        result = tool.list_directory(templates_path)

        assert result == (template,)

    def test_reads_file_using_file_reader(self, tmp_path):
        file_reader = Mock()
        file_reader.read.return_value = "file contents"

        tool = ReadFileTool(file_reader=file_reader)

        path = tmp_path / "requirement.json"
        path.write_text("file contents")

        result = tool.read_file(path)

        file_reader.read.assert_called_once_with(path)
        assert result == "file contents"
