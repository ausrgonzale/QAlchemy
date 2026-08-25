"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    normalize_provider_response.py

Purpose:
    Normalizes raw responses returned by AI providers before downstream
    processing.

Description:
    The normalize_provider_response utility converts a raw provider response
    into clean content suitable for downstream QAlchemy processing.

    AI providers may return generated source code wrapped in Markdown code
    fences or surrounded by unnecessary whitespace. This utility removes
    provider-specific presentation artifacts while preserving the generated
    content.

Responsibilities
----------------
- Normalize raw AI provider responses.
- Remove Markdown code fences surrounding generated content.
- Remove unnecessary leading and trailing whitespace.
- Preserve the generated content itself.

Non-Responsibilities
--------------------
This utility does NOT:

- Determine artifact filenames.
- Parse artifact definitions.
- Write files.
- Create directories.
- Manage WorkSpaces.
- Modify WorkOrders.
- Invoke AI providers.
- Validate generated source code.
- Perform logging.
- Perform orchestration.

Design Principles
-----------------
The normalizer is deterministic and stateless.

Given the same provider response, the normalizer will always return the same
normalized content.

The normalizer operates only on response content and has no knowledge of
filesystem locations or application workflows.

===============================================================================
"""


def normalize_provider_response(
    response: str,
) -> str:
    """
    Normalize a raw AI provider response.

    Removes surrounding Markdown code fences and unnecessary leading or
    trailing whitespace while preserving the generated content.
    """

    content = response.strip()

    # Normalize line endings
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    if content.startswith("```"):
        lines = content.splitlines()

        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines)

    return content.strip()
