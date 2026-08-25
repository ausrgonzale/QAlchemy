"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_create_generated_artifacts.py

Purpose:
    Validates creation of GeneratedArtifact objects from a WorkOrder and
    normalized AI provider response.

Description:
    These tests verify that the artifact creation utility extracts the
    required artifact path from the Deliverable contained in the WorkOrder
    and combines it with the normalized provider response.

Responsibilities
----------------
- Verify artifact paths are extracted from the Deliverable.
- Verify generated content is preserved.
- Verify GeneratedArtifact objects are created correctly.
- Verify multiple requested artifacts can be represented.

Non-Responsibilities
--------------------
These tests do NOT:

- Invoke AI providers.
- Normalize provider responses.
- Write files.
- Create directories.
- Manage WorkSpaces.
- Execute Feature Services.
- Test WorkOrder construction.

===============================================================================
"""

import pytest

from scripts.core.work_order import WorkOrder
from scripts.utils.create_generated_artifacts import (
    GeneratedArtifact,
    create_generated_artifacts,
)


def test_creates_generated_artifact_from_deliverable() -> None:
    work_order = WorkOrder(
        task="Create a Playwright automation solution.",
        role="Act as a Senior Playwright Automation Architect.",
        target="generate_code",
        deliverable="""## Requirements

Create a production-ready Playwright automation solution.

## Required Artifact

Generate exactly one file:

pages/google_search_page.py
""",
    )

    response = "from playwright.sync_api import Page"

    result = create_generated_artifacts(
        work_order,
        response,
    )

    assert result == (
        GeneratedArtifact(
            relative_path="pages/google_search_page.py",
            content=response,
        ),
    )


def test_preserves_normalized_provider_response() -> None:
    work_order = WorkOrder(
        task="Create a Playwright automation solution.",
        role="Act as a Senior Playwright Automation Architect.",
        target="generate_code",
        deliverable="""## Required Artifact

Generate exactly one file:

pages/google_search_page.py
""",
    )

    response = (
        "from playwright.sync_api import Page\n\n"
        "class GoogleSearchPage:\n"
        "    pass"
    )

    result = create_generated_artifacts(
        work_order,
        response,
    )

    assert result[0].content == response


def test_raises_error_when_required_artifact_is_missing() -> None:
    work_order = WorkOrder(
        task="Create a Playwright automation solution.",
        role="Act as a Senior Playwright Automation Architect.",
        target="generate_code",
        deliverable="""## Requirements

Create a production-ready Playwright automation solution.
""",
    )

    response = "from playwright.sync_api import Page"

    with pytest.raises(
        ValueError,
        match="WorkOrder deliverable does not define a required artifact.",
    ):
        create_generated_artifacts(
            work_order,
            response,
        )
