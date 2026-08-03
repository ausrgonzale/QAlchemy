# =============================================================================
# test_exception_handling_service_construction.py
#
# Unit tests for ExceptionHandlingService construction, catalog access,
# and basic exception creation behavior.
# =============================================================================

from pathlib import Path

import pytest

from scripts.core.exception_catalog import ExceptionCatalog
from scripts.core.exception_models import (
    ExceptionDefinition,
    QAlchemyException,
)
from services.core.exception_handling_service import (
    ExceptionHandlingService,
)

# =============================================================================
# Construction
# =============================================================================


def test_constructor_uses_provided_catalog(
    exception_catalog: ExceptionCatalog,
) -> None:
    """Verify the supplied catalog instance is used."""

    service = ExceptionHandlingService(
        catalog=exception_catalog,
    )

    assert service.catalog is exception_catalog


def test_constructor_loads_catalog_from_yaml(
    exception_catalog_yaml: Path,
) -> None:
    """Verify the catalog is loaded from disk."""

    service = ExceptionHandlingService(
        catalog_path=exception_catalog_yaml,
    )

    assert isinstance(service.catalog, ExceptionCatalog)
    assert service.has_exception("CFG001")


def test_constructor_requires_catalog_or_path() -> None:
    """Verify a catalog source is required."""

    with pytest.raises(
        ValueError,
        match="Either 'catalog' or 'catalog_path' must be provided.",
    ):
        ExceptionHandlingService()


# =============================================================================
# Catalog Access
# =============================================================================


def test_catalog_property_returns_catalog(
    exception_handling_service: ExceptionHandlingService,
    exception_catalog: ExceptionCatalog,
) -> None:
    """Verify the catalog property exposes the underlying catalog."""

    assert exception_handling_service.catalog is exception_catalog


def test_has_exception_returns_true(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify known exception codes exist."""

    assert exception_handling_service.has_exception(sample_exception_code)


def test_has_exception_returns_false(
    exception_handling_service: ExceptionHandlingService,
) -> None:
    """Verify unknown exception codes return False."""

    assert not exception_handling_service.has_exception("UNKNOWN999")


def test_get_definition_returns_definition(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify a definition can be retrieved."""

    definition = exception_handling_service.get_definition(
        sample_exception_code,
    )

    assert isinstance(
        definition,
        ExceptionDefinition,
    )

    assert definition.code == sample_exception_code
    assert definition.component
    assert definition.severity
    assert definition.message


# =============================================================================
# Exception Creation
# =============================================================================


def test_create_exception_returns_qalchemy_exception(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify a runtime exception is created."""

    exception = exception_handling_service.create_exception(
        sample_exception_code,
    )

    assert isinstance(
        exception,
        QAlchemyException,
    )

    assert exception.code == sample_exception_code
    assert exception.definition.code == sample_exception_code


def test_create_exception_populates_definition(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify the definition is copied into the exception."""

    definition = exception_handling_service.get_definition(
        sample_exception_code,
    )

    exception = exception_handling_service.create_exception(
        sample_exception_code,
    )

    assert exception.definition == definition
    assert exception.code == definition.code
    assert exception.component == definition.component
    assert exception.severity == definition.severity
    assert exception.message == definition.message
    assert exception.recoverable == definition.recoverable


def test_create_exception_defaults_context(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify context defaults to an empty dictionary."""

    exception = exception_handling_service.create_exception(
        sample_exception_code,
    )

    assert exception.context == {}
    assert exception.cause is None


def test_create_exception_preserves_context(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify supplied runtime context is preserved."""

    context = {
        "file": "app.yaml",
        "line": 42,
    }

    exception = exception_handling_service.create_exception(
        sample_exception_code,
        context=context,
    )

    assert exception.context == context
    assert exception.context["file"] == "app.yaml"
    assert exception.context["line"] == 42


def test_create_exception_copies_context(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify the context dictionary is defensively copied."""

    context = {
        "file": "config.yaml",
    }

    exception = exception_handling_service.create_exception(
        sample_exception_code,
        context=context,
    )

    context["file"] = "modified.yaml"

    assert exception.context["file"] == "config.yaml"
    assert exception.context is not context


def test_create_exception_preserves_cause(
    exception_handling_service: ExceptionHandlingService,
    sample_exception_code: str,
) -> None:
    """Verify the originating exception is retained."""

    cause = ValueError("boom")

    exception = exception_handling_service.create_exception(
        sample_exception_code,
        cause=cause,
    )

    assert exception.cause is cause
