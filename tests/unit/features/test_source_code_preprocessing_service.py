"""Unit tests for SourceCodePreprocessingService."""

from __future__ import annotations

import pytest

from services.core.source_code_preprocessing_service import (
    SourceCodePreprocessingService,
)


def test_remove_comments_strips_comment_tokens() -> None:
    """Remove comment tokens while preserving executable statements."""
    source = "x = 1  # keep code\n# full line comment\ny = x + 2\n"

    cleaned = SourceCodePreprocessingService.remove_comments(source)

    assert "full line comment" not in cleaned
    assert "x = 1" in cleaned
    assert "y = x + 2" in cleaned


def test_remove_docstrings_strips_module_class_and_function_docstrings() -> None:
    """Remove module, class, and function docstrings from source code."""
    source = (
        '"""module docs"""\n\n'
        "class A:\n"
        '    """class docs"""\n'
        "    def f(self):\n"
        '        """function docs"""\n'
        "        return 1\n"
    )

    cleaned = SourceCodePreprocessingService.remove_docstrings(source)

    assert "module docs" not in cleaned
    assert "class docs" not in cleaned
    assert "function docs" not in cleaned
    assert "return 1" in cleaned


def test_preprocess_can_toggle_each_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run only enabled preprocessing steps when toggles are supplied."""
    calls = []

    def fake_remove_comments(src: str) -> str:
        calls.append("comments")
        return src + "\n#comments_removed"

    def fake_remove_docstrings(src: str) -> str:
        calls.append("docstrings")
        return src + "\n#docstrings_removed"

    monkeypatch.setattr(
        SourceCodePreprocessingService,
        "remove_comments",
        staticmethod(fake_remove_comments),
    )
    monkeypatch.setattr(
        SourceCodePreprocessingService,
        "remove_docstrings",
        staticmethod(fake_remove_docstrings),
    )

    out = SourceCodePreprocessingService.preprocess(
        "print('x')",
        remove_comments=True,
        remove_docstrings=False,
    )

    assert calls == ["comments"]
    assert "comments_removed" in out
    assert "docstrings_removed" not in out
