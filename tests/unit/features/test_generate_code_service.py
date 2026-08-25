"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_generate_code_service.py

Purpose:
    Validates the GenerateCodeService execution workflow.

Description:
    These tests verify that GenerateCodeService transforms a WorkOrder,
    invokes the configured AI client, normalizes the provider response,
    creates GeneratedArtifact objects, and persists generated artifacts to
    the execution WorkSpace.

Responsibilities
----------------
- Verify WorkOrder transformation.
- Verify AI client invocation.
- Verify provider response normalization.
- Verify GeneratedArtifact creation.
- Verify generated artifacts are written to the WorkSpace output root.
- Verify the Generate Code workflow completes successfully.

Non-Responsibilities
--------------------
These tests do NOT:

- Test AI provider implementations.
- Test WorkOrder transformation logic.
- Test provider response normalization logic.
- Test artifact creation logic.
- Create or manage WorkSpaces.
- Persist Work Orders.
- Test Work Order orchestration.

===============================================================================
"""

from pathlib import Path
from unittest.mock import Mock

from scripts.core.work_order import WorkOrder
from scripts.utils.work_space import WorkSpace
from services.feature.generate_code_service import GenerateCodeService


def test_execute_generates_artifacts(
    tmp_path: Path,
) -> None:
    """Execute the Generate Code workflow and create generated artifacts."""

    work_order = WorkOrder(
        task="Create a Playwright automation solution.",
        role="Act as a Senior Playwright Automation Architect.",
        target="generate_code",
        deliverable="""## Required Artifact

Generate exactly one file:

pages/google_search_page.py
""",
    )

    workspace = WorkSpace(
        root=tmp_path / "work_space",
        work_order_id="WO001",
    )
    workspace.create()

    transformer = Mock()
    transformer.transform.return_value = "LLM REQUEST"

    client = Mock()
    client.generate.return_value = """```python
from playwright.sync_api import Page
```"""

    client_service = Mock()
    client_service.create.return_value = client

    execution_service = Mock()
    execution_service.client_service = client_service
    execution_service.logger_service = Mock()
    execution_service.exception_handling_service = Mock()

    service = GenerateCodeService(
        execution_service=execution_service,
        work_order_transformer=transformer,
    )

    service.execute(
        work_order,
        workspace,
    )

    transformer.transform.assert_called_once_with(work_order)
    client_service.create.assert_called_once_with()
    client.generate.assert_called_once_with("LLM REQUEST")


def test_execute_normalizes_response_before_creating_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Pass the normalized provider response to artifact creation."""

    work_order = WorkOrder(
        task="Create a Playwright automation solution.",
        role="Act as a Senior Playwright Automation Architect.",
        target="generate_code",
        deliverable="""## Required Artifact

Generate exactly one file:

pages/google_search_page.py
""",
    )

    workspace = WorkSpace(
        root=tmp_path / "work_space",
        work_order_id="WO001",
    )
    workspace.create()

    transformer = Mock()
    transformer.transform.return_value = "LLM REQUEST"

    client = Mock()
    client.generate.return_value = "RAW RESPONSE"

    client_service = Mock()
    client_service.create.return_value = client

    execution_service = Mock()
    execution_service.client_service = client_service
    execution_service.logger_service = Mock()
    execution_service.exception_handling_service = Mock()

    normalize_mock = Mock()
    normalize_mock.return_value = "NORMALIZED RESPONSE"

    create_artifacts_mock = Mock()
    create_artifacts_mock.return_value = ()

    monkeypatch.setattr(
        "services.feature.generate_code_service.normalize_provider_response",
        normalize_mock,
    )
    monkeypatch.setattr(
        "services.feature.generate_code_service.create_generated_artifacts",
        create_artifacts_mock,
    )

    service = GenerateCodeService(
        execution_service=execution_service,
        work_order_transformer=transformer,
    )

    service.execute(
        work_order,
        workspace,
    )

    normalize_mock.assert_called_once_with("RAW RESPONSE")

    create_artifacts_mock.assert_called_once_with(
        work_order,
        "NORMALIZED RESPONSE",
    )


def test_execute_writes_generated_artifacts_to_workspace(
    tmp_path: Path,
) -> None:
    """Write generated artifacts to the WorkSpace output root."""

    work_order = WorkOrder(
        task="Create a Playwright automation solution.",
        role="Act as a Senior Playwright Automation Architect.",
        target="generate_code",
        deliverable="""## Required Artifact

Generate exactly one file:

pages/google_search_page.py
""",
    )

    workspace = WorkSpace(
        root=tmp_path / "work_space",
        work_order_id="WO001",
    )
    workspace.create()

    transformer = Mock()
    transformer.transform.return_value = "LLM REQUEST"

    client = Mock()
    client.generate.return_value = """```python
from playwright.sync_api import Page
```"""

    client_service = Mock()
    client_service.create.return_value = client

    execution_service = Mock()
    execution_service.client_service = client_service
    execution_service.logger_service = Mock()
    execution_service.exception_handling_service = Mock()

    service = GenerateCodeService(
        execution_service=execution_service,
        work_order_transformer=transformer,
    )

    service.execute(
        work_order,
        workspace,
    )

    expected_file = workspace.output_root / "pages" / "google_search_page.py"

    assert expected_file.is_file()
    assert "from playwright.sync_api import Page" in expected_file.read_text(
        encoding="utf-8",
    )
