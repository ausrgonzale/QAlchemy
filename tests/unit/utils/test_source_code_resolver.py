"""
===============================================================================
Unit Tests

SourceCodeResolver

Validates resolution of runtime source-code files and directories into
concrete source-code paths.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.utils.source_code_resolver import SourceCodeResolver


def test_resolve_single_file(tmp_path: Path) -> None:
    """Resolve a single source-code file."""

    source_file = tmp_path / "calculator.py"
    source_file.write_text(
        "print('calculator')",
        encoding="utf-8",
    )

    resolver = SourceCodeResolver()

    result = resolver.resolve([source_file])

    assert result == [source_file]


def test_resolve_multiple_files(tmp_path: Path) -> None:
    """Resolve multiple explicitly supplied source-code files."""

    first_file = tmp_path / "calculator.py"
    second_file = tmp_path / "helpers.py"

    first_file.write_text("calculator", encoding="utf-8")
    second_file.write_text("helpers", encoding="utf-8")

    resolver = SourceCodeResolver()

    result = resolver.resolve(
        [
            first_file,
            second_file,
        ],
    )

    assert result == [
        first_file,
        second_file,
    ]


def test_resolve_directory_recursively_finds_python_files(
    tmp_path: Path,
) -> None:
    """Recursively resolve Python files from a directory."""

    root = tmp_path / "src"
    nested = root / "pages"
    nested.mkdir(parents=True)

    calculator = root / "calculator.py"
    helper = nested / "helper.py"

    calculator.write_text("calculator", encoding="utf-8")
    helper.write_text("helper", encoding="utf-8")

    resolver = SourceCodeResolver()

    result = resolver.resolve([root])

    assert result == [
        calculator,
        helper,
    ]


def test_resolve_directory_returns_deterministic_order(
    tmp_path: Path,
) -> None:
    """Return discovered source files in deterministic order."""

    root = tmp_path / "src"
    root.mkdir()

    zebra = root / "zebra.py"
    alpha = root / "alpha.py"
    middle = root / "middle.py"

    zebra.write_text("zebra", encoding="utf-8")
    alpha.write_text("alpha", encoding="utf-8")
    middle.write_text("middle", encoding="utf-8")

    resolver = SourceCodeResolver()

    result = resolver.resolve([root])

    assert result == [
        alpha,
        middle,
        zebra,
    ]


def test_resolve_directory_ignores_unsupported_files(
    tmp_path: Path,
) -> None:
    """Ignore unsupported files discovered inside a directory."""

    root = tmp_path / "src"
    root.mkdir()

    python_file = root / "calculator.py"
    markdown_file = root / "README.md"
    text_file = root / "notes.txt"

    python_file.write_text("calculator", encoding="utf-8")
    markdown_file.write_text("documentation", encoding="utf-8")
    text_file.write_text("notes", encoding="utf-8")

    resolver = SourceCodeResolver()

    result = resolver.resolve([root])

    assert result == [python_file]


def test_resolve_empty_directory_returns_empty_list(
    tmp_path: Path,
) -> None:
    """Return an empty list when a directory contains no Python files."""

    root = tmp_path / "empty"
    root.mkdir()

    resolver = SourceCodeResolver()

    result = resolver.resolve([root])

    assert result == []


def test_resolve_missing_path_raises_file_not_found_error(
    tmp_path: Path,
) -> None:
    """Raise FileNotFoundError when a source path does not exist."""

    missing_path = tmp_path / "does_not_exist.py"

    resolver = SourceCodeResolver()

    with pytest.raises(
        FileNotFoundError,
        match="Source code path does not exist",
    ):
        resolver.resolve([missing_path])
