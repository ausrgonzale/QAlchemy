# =============================================================================
# test_exception_handling_service_behavior.py
#
# Unit tests covering advanced ExceptionHandlingService behavior.
# =============================================================================

import pytest

from scripts.core.exception_models import QAlchemyException
from services.core.exception_handling_service import (
    ExceptionHandlingService,
)

# =============================================================================
# Runtime Message Override
# =============================================================================


def test_create_exception_overrides_message(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify a runtime message override is applied."""

    runtime_message = "Unable to load customer configuration."

    exception = exception_handling_service.create_exception(
        sample_exception_code,
        message=runtime_message,
    )

    assert exception.message == runtime_message
    assert exception.definition.message == runtime_message


def test_create_exception_override_does_not_modify_catalog(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify overriding a message does not mutate the catalog."""

    original_definition = exception_handling_service.get_definition(
        sample_exception_code,
    )

    original_message = original_definition.message

    exception_handling_service.create_exception(
        sample_exception_code,
        message="Temporary runtime override",
    )

    refreshed_definition = exception_handling_service.get_definition(
        sample_exception_code,
    )

    assert refreshed_definition.message == original_message


# =============================================================================
# Unknown Exception Codes
# =============================================================================


def test_create_exception_unknown_code_raises_keyerror(
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Verify unknown exception codes raise KeyError."""

    with pytest.raises(KeyError):
        exception_handling_service.create_exception(
            "UNKNOWN999",
        )


def test_get_definition_unknown_code_raises_keyerror(
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Verify get_definition raises KeyError."""

    with pytest.raises(KeyError):
        exception_handling_service.get_definition(
            "UNKNOWN999",
        )


# =============================================================================
# __repr__
# =============================================================================


def test_repr_contains_summary(
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Verify __repr__ returns useful diagnostic information."""

    representation = repr(
        exception_handling_service,
    )

    assert "ExceptionHandlingService" in representation
    assert "exceptions=" in representation
    assert "version=" in representation


# =============================================================================
# Exception Model Integration
# =============================================================================


def test_created_exception_string_contains_code_and_message(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify __str__() formatting."""

    exception = exception_handling_service.create_exception(
        sample_exception_code,
    )

    text = str(exception)

    assert exception.code in text
    assert exception.message in text


def test_created_exception_preserves_definition_reference(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify the runtime exception contains a definition."""

    exception = exception_handling_service.create_exception(
        sample_exception_code,
    )

    assert isinstance(
        exception,
        QAlchemyException,
    )

    assert exception.definition is not None


def test_multiple_exceptions_are_independent(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify multiple created exceptions do not share context."""

    first = exception_handling_service.create_exception(
        sample_exception_code,
        context={"value": 1},
    )

    second = exception_handling_service.create_exception(
        sample_exception_code,
        context={"value": 2},
    )

    assert first is not second
    assert first.context["value"] == 1
    assert second.context["value"] == 2
