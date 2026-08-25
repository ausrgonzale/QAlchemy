"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_normalize_provider_response.py

Purpose:
    Validates normalization of raw AI provider responses before downstream
    processing.

Description:
    These tests verify that provider responses are normalized consistently
    while preserving the generated content.

Responsibilities
----------------
- Verify plain provider responses are preserved.
- Verify Markdown code fences are removed.
- Verify line endings are normalized.
- Verify leading and trailing whitespace is removed.
- Verify empty responses are handled correctly.

Non-Responsibilities
--------------------
These tests do NOT:

- Validate generated source code.
- Create GeneratedArtifacts.
- Write files.
- Manage WorkSpaces.
- Invoke AI providers.
- Test Feature Services.
- Validate WorkOrder construction.

Test Coverage
-------------
- Plain content.
- Python fenced content.
- Generic fenced content.
- Windows line endings.
- Leading and trailing whitespace.
- Empty responses.

===============================================================================
"""

from scripts.utils.normalize_provider_response import (
    normalize_provider_response,
)


def test_returns_plain_content_unchanged() -> None:
    response = "print('hello')"

    result = normalize_provider_response(response)

    assert result == "print('hello')"


def test_removes_python_code_fences() -> None:
    response = """```python
print('hello')
```"""

    result = normalize_provider_response(response)

    assert result == "print('hello')"


def test_removes_generic_code_fences() -> None:
    response = """```
print('hello')
```"""

    result = normalize_provider_response(response)

    assert result == "print('hello')"


def test_normalizes_windows_line_endings() -> None:
    response = "line one\r\nline two\r\nline three"

    result = normalize_provider_response(response)

    assert result == "line one\nline two\nline three"


def test_removes_leading_and_trailing_whitespace() -> None:
    response = "  \nprint('hello')\n  "

    result = normalize_provider_response(response)

    assert result == "print('hello')"


def test_returns_empty_string_for_empty_response() -> None:
    response = ""

    result = normalize_provider_response(response)

    assert result == ""
