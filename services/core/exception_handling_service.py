# =============================================================================
# exception_handling_service.py
#
# QAlchemy Community Edition
#
# Copyright (c) 2026
#
# =============================================================================
# Purpose
# -----------------------------------------------------------------------------
# The ExceptionHandlingService is the single public entry point for creating
# and raising runtime exceptions within QAlchemy.
#
# This service consumes the ExceptionCatalog and converts catalog definitions
# into QAlchemyException instances. The catalog remains the single source of
# truth for all framework exception definitions.
#
# Responsibilities
# -----------------------------------------------------------------------------
# • Create QAlchemyException instances
# • Raise framework exceptions
# • Provide a consistent runtime exception API
# • Attach optional runtime context
# • Support exception chaining
#
# This service intentionally DOES NOT:
#
# • Load YAML directly
# • Validate catalog structure
# • Perform logging
# • Format reports
# • Contain business logic
#
# Architecture
# -----------------------------------------------------------------------------
#
#                     exceptions.yaml
#                            │
#                            ▼
#                    ExceptionCatalog
#                            │
#                            ▼
#               ExceptionHandlingService
#                            │
#                            ▼
#                  QAlchemyException
#
# Design Goals
# -----------------------------------------------------------------------------
# • Single Responsibility Principle
# • Strong typing
# • Small public API
# • Easy to unit test
# • Framework agnostic
# • AI-friendly and self-documenting
#
# =============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.core.exception_catalog import ExceptionCatalog
from scripts.core.exception_models import (
    ExceptionDefinition,
    QAlchemyException,
)


class ExceptionHandlingService:
    """
    Creates and raises runtime exceptions using the centralized
    ExceptionCatalog.

    The catalog is loaded once and treated as immutable for the lifetime
    of the service.
    """

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------

    def __init__(
        self,
        catalog: ExceptionCatalog | None = None,
        catalog_path: str | Path | None = None,
    ) -> None:
        """
        Creates a new ExceptionHandlingService.

        Parameters
        ----------
        catalog:
            Existing ExceptionCatalog instance.

        catalog_path:
            Path to exceptions.yaml.

            Used only when an existing catalog is not supplied.

        Raises
        ------
        ValueError
            If neither catalog nor catalog_path is supplied.
        """

        if catalog is not None:
            self._catalog = catalog

        elif catalog_path is not None:
            self._catalog = ExceptionCatalog(catalog_path)

        else:
            raise ValueError("Either 'catalog' or 'catalog_path' must be provided.")

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------

    def _get_definition(
        self,
        code: str,
    ) -> ExceptionDefinition:
        """
        Retrieves an exception definition from the catalog.

        Parameters
        ----------
        code:
            Framework exception code.

        Raises
        ------
        KeyError
            If the exception code is unknown.
        """

        return self._catalog.get_exception(code)

    def _normalize_context(
        self,
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Returns a normalized context dictionary.

        None is converted into an empty dictionary to simplify downstream
        processing.
        """

        if context is None:
            return {}

        return dict(context)

    # -------------------------------------------------------------------------
    # Exception Creation
    # -------------------------------------------------------------------------

    def create_exception(
        self,
        code: str,
        *,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
        message: str | None = None,
    ) -> QAlchemyException:
        """
        Creates a QAlchemyException from an exception code.

        Parameters
        ----------
        code:
            Framework exception code.

        context:
            Optional runtime context.

        cause:
            Optional originating exception.

        message:
            Optional runtime message override.

        Returns
        -------
        QAlchemyException
            Newly created runtime exception.
        """

        definition = self._get_definition(code)

        if message is not None:

            definition = ExceptionDefinition(
                code=definition.code,
                component=definition.component,
                severity=definition.severity,
                recoverable=definition.recoverable,
                message=message,
                user_message=definition.user_message,
                recommendation=definition.recommendation,
                category=definition.category,
                documentation=definition.documentation,
            )

        return QAlchemyException(
            definition=definition,
            context=self._normalize_context(context),
            cause=cause,
        )

    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------

    def has_exception(
        self,
        code: str,
    ) -> bool:
        """
        Returns True if the exception code exists.
        """

        return self._catalog.has_exception(code)

    def get_definition(
        self,
        code: str,
    ) -> ExceptionDefinition:
        """
        Returns the ExceptionDefinition for a framework exception code.
        """

        return self._get_definition(code)

    @property
    def catalog(self) -> ExceptionCatalog:
        """
        Returns the underlying exception catalog.
        """

        return self._catalog

    # -------------------------------------------------------------------------
    # Exception Raising
    # -------------------------------------------------------------------------

    def raise_exception(
        self,
        code: str,
        *,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
        message: str | None = None,
    ) -> None:
        """
        Creates and raises a QAlchemyException.

        Parameters
        ----------
        code:
            Framework exception code.

        context:
            Optional runtime context.

        cause:
            Optional originating exception.

        message:
            Optional runtime message override.
        """

        raise self.create_exception(
            code,
            context=context,
            cause=cause,
            message=message,
        ) from cause

    def raise_existing(
        self,
        exception: QAlchemyException,
    ) -> None:
        """
        Raises an existing QAlchemyException.

        This method provides a consistent API for callers that have already
        constructed an exception instance.
        """

        raise exception

    # -------------------------------------------------------------------------
    # Python Convenience Methods
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Returns a concise developer representation.
        """

        version = (
            self._catalog.metadata.version
            if self._catalog.metadata is not None
            else "Unknown"
        )

        return (
            f"{self.__class__.__name__}("
            f"exceptions={len(self._catalog)}, "
            f"version='{version}')"
        )


# =============================================================================
# End of exception_handling_service.py
# =============================================================================
