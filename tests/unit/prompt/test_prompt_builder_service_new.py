"""
===============================================================================
Unit Tests

PromptBuilderService (Prototype)

These tests validate the prototype PromptBuilderService implementation located
under working/prototype.

The prototype is intentionally isolated from the production implementation and
serves as the regression suite for the future v1.2 PromptBuilderService.

Responsibilities Tested
-----------------------
- Service construction
- Work Order validation
- Prompt generation
- Prompt assembly
- Prompt rendering
- Logging integration
- Debug artifact generation
- Result construction
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from scripts.core.ai_work_order import AIWorkOrder
from scripts.core.exception_models import QAlchemyException
from scripts.core.prompt_debug_writer import PromptDebugWriter
from scripts.core.prompt_renderer import PromptRenderer
from services.core.app_configuration_service import AppConfigurationService
from services.core.exception_handling_service import ExceptionHandlingService
from services.core.logger_service import LoggerService
from services.core.prompt_loader_service import PromptLoaderService
from working.prototype.prompt_builder_service import PromptBuilderService


def test_generate_success(
    configuration: AppConfigurationService,
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Generate a prompt successfully."""

    logger = MagicMock(spec=LoggerService)

    prompt_loader = MagicMock(spec=PromptLoaderService)
    prompt_loader.load.side_effect = lambda filename: (f"Loaded: {filename}")

    renderer = MagicMock(spec=PromptRenderer)
    renderer.render.return_value = "# Rendered Prompt"

    debug_writer = MagicMock(spec=PromptDebugWriter)

    service = PromptBuilderService(
        configuration=configuration,
        logger_service=logger,
        exception_service=exception_handling_service,
        prompt_loader=prompt_loader,
        renderer=renderer,
        debug_writer=debug_writer,
    )

    work_order = AIWorkOrder(
        who="You are a senior Python engineer.",
        what="Generate LoggerService.",
        why="Follow project standards.",
        context="Existing logging framework.",
    )

    result = service.generate(work_order)

    assert result["success"] is True
    assert result["prompt"] == "# Rendered Prompt"

    renderer.render.assert_called_once()


def test_generate_builds_expected_prompt_model(
    configuration: AppConfigurationService,
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Build the expected prompt model."""

    logger = MagicMock(spec=LoggerService)

    prompt_loader = MagicMock(spec=PromptLoaderService)
    prompt_loader.load.side_effect = lambda filename: f"Loaded: {filename}"

    renderer = MagicMock(spec=PromptRenderer)
    renderer.render.return_value = "# Rendered Prompt"

    debug_writer = MagicMock(spec=PromptDebugWriter)

    service = PromptBuilderService(
        configuration=configuration,
        logger_service=logger,
        exception_service=exception_handling_service,
        prompt_loader=prompt_loader,
        renderer=renderer,
        debug_writer=debug_writer,
    )

    work_order = AIWorkOrder(
        who="You are a senior Python engineer.",
        what="Generate LoggerService.",
        why="Follow project standards.",
        context="Existing logging framework.",
    )

    service.generate(work_order)

    renderer.render.assert_called_once()

    prompt_model = renderer.render.call_args.kwargs["prompt_model"]

    assert prompt_model == [
        (
            "System Prompt",
            "You are a senior Python engineer.",
        ),
        (
            "Objective",
            "Generate LoggerService.",
        ),
        (
            "Instructions",
            "Follow project standards.",
        ),
        (
            "Context",
            "Existing logging framework.",
        ),
        (
            "Standards",
            f"Loaded: {configuration.prompts.code_standards}",
        ),
        (
            "Python Standards",
            f"Loaded: {configuration.prompts.python_standards}",
        ),
        (
            "Expected Deliverable",
            (
                "Produce production-ready Markdown. "
                "Generate complete implementations. "
                "Do not omit required code."
            ),
        ),
    ]


def test_generate_rejects_missing_who(
    configuration: AppConfigurationService,
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Reject a work order missing the AI persona."""

    logger = MagicMock(spec=LoggerService)

    prompt_loader = MagicMock(spec=PromptLoaderService)

    renderer = MagicMock(spec=PromptRenderer)

    debug_writer = MagicMock(spec=PromptDebugWriter)

    service = PromptBuilderService(
        configuration=configuration,
        logger_service=logger,
        exception_service=exception_handling_service,
        prompt_loader=prompt_loader,
        renderer=renderer,
        debug_writer=debug_writer,
    )

    work_order = AIWorkOrder(
        who="",
        what="Generate LoggerService.",
        why="Follow project standards.",
    )

    with pytest.raises(QAlchemyException) as exc_info:
        service.generate(work_order)

        assert exc_info.value.definition.code == "VAL-0001"
        assert exc_info.value.context["missing_fields"] == ["who"]

    renderer.render.assert_not_called()


def test_generate_rejects_missing_what(
    configuration: AppConfigurationService,
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Reject a work order missing the requested work."""

    logger = MagicMock(spec=LoggerService)

    prompt_loader = MagicMock(spec=PromptLoaderService)

    renderer = MagicMock(spec=PromptRenderer)

    debug_writer = MagicMock(spec=PromptDebugWriter)

    service = PromptBuilderService(
        configuration=configuration,
        logger_service=logger,
        exception_service=exception_handling_service,
        prompt_loader=prompt_loader,
        renderer=renderer,
        debug_writer=debug_writer,
    )

    work_order = AIWorkOrder(
        who="You are a senior Python engineer.",
        what="",
        why="Follow project standards.",
    )

    with pytest.raises(QAlchemyException) as exc_info:
        service.generate(work_order)

    assert exc_info.value.definition.code == "VAL-0001"
    assert exc_info.value.context["missing_fields"] == ["what"]

    renderer.render.assert_not_called()


def test_generate_rejects_missing_why(
    configuration: AppConfigurationService,
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Reject a work order missing the business objective."""

    logger = MagicMock(spec=LoggerService)

    prompt_loader = MagicMock(spec=PromptLoaderService)

    renderer = MagicMock(spec=PromptRenderer)

    debug_writer = MagicMock(spec=PromptDebugWriter)

    service = PromptBuilderService(
        configuration=configuration,
        logger_service=logger,
        exception_service=exception_handling_service,
        prompt_loader=prompt_loader,
        renderer=renderer,
        debug_writer=debug_writer,
    )

    work_order = AIWorkOrder(
        who="You are a senior Python engineer.",
        what="Generate LoggerService.",
        why="",
    )

    with pytest.raises(QAlchemyException) as exc_info:
        service.generate(work_order)

    assert exc_info.value.definition.code == "VAL-0001"
    assert exc_info.value.context["missing_fields"] == ["why"]

    renderer.render.assert_not_called()
