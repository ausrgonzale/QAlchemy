# =============================================================================
# test_exception_handling_service_raising.py
#
# Unit tests covering ExceptionHandlingService raising behavior.
# =============================================================================

import pytest

from scripts.core.exception_models import QAlchemyException
from services.core.exception_handling_service import (
    ExceptionHandlingService,
)


def test_raise_exception_raises_qalchemy_exception(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify raise_exception raises a QAlchemyException."""

    with pytest.raises(QAlchemyException) as exc_info:
        exception_handling_service.raise_exception(
            sample_exception_code,
        )

    assert exc_info.value.code == sample_exception_code


def test_raise_exception_preserves_context(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify raise_exception preserves runtime context."""

    context = {
        "filename": "config.yaml",
        "line": 27,
    }

    with pytest.raises(QAlchemyException) as exc_info:
        exception_handling_service.raise_exception(
            sample_exception_code,
            context=context,
        )

    assert exc_info.value.context == context


def test_raise_exception_applies_runtime_message(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify runtime message overrides are preserved."""

    message = "Unable to open configuration file."

    with pytest.raises(QAlchemyException) as exc_info:
        exception_handling_service.raise_exception(
            sample_exception_code,
            message=message,
        )

    assert exc_info.value.message == message


def test_raise_existing_raises_same_exception(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify raise_existing raises the supplied exception."""

    exception = exception_handling_service.create_exception(
        sample_exception_code,
    )

    with pytest.raises(QAlchemyException) as exc_info:
        exception_handling_service.raise_existing(
            exception,
        )

    assert exc_info.value is exception


def test_raise_exception_unknown_code_raises_keyerror(
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Verify unknown exception codes raise KeyError."""

    with pytest.raises(KeyError):
        exception_handling_service.raise_exception(
            "UNKNOWN999",
        )
