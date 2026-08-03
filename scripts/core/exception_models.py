"""
===============================================================================
QAlchemy Exception Models
===============================================================================

Purpose
-------
This module defines the immutable data models used by the QAlchemy Exception
Management subsystem. These models represent the in-memory contract for the
exception catalog loaded from ``exceptions.yaml``.

The models provide a strongly typed representation of:

    • Catalog metadata
    • Application components
    • Exception code prefixes
    • Individual exception definitions
    • Runtime QAlchemy exceptions

Design Principles
-----------------
These classes are intentionally lightweight data models.

They:
    • Represent configuration loaded from YAML.
    • Do not perform file I/O.
    • Do not load or validate the exception catalog.
    • Do not contain business logic.
    • Remain immutable wherever practical.

Responsibilities
----------------
The surrounding exception subsystem has clearly separated responsibilities:

    exception_models.py
        Defines the object model for the exception catalog.

    exception_catalog.py
        Loads and validates the YAML catalog and constructs these models.

    exception_handling_service.py
        Creates and raises QAlchemyException instances using the catalog.

Architecture
------------
exceptions.yaml
        ↓
ExceptionCatalog
        ↓
ExceptionDefinition
        ↓
QAlchemyException
        ↓
Application Code

This separation ensures that the exception catalog serves as the single source
of truth while providing a clean, typed interface for the rest of the
application.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CatalogMetadata:
    """Metadata describing the exception catalog."""

    framework: str
    version: str
    description: str = ""


@dataclass(frozen=True)
class ComponentDefinition:
    """Defines an application component."""

    name: str
    description: str = ""


@dataclass(frozen=True)
class PrefixDefinition:
    """Defines an exception code prefix."""

    prefix: str
    component: str
    description: str = ""


@dataclass(frozen=True)
class ExceptionDefinition:
    """Defines a single exception from the exception catalog."""

    code: str
    component: str
    severity: str
    recoverable: bool
    message: str
    user_message: str = ""
    recommendation: str = ""
    category: str = ""
    documentation: str = ""


@dataclass
class QAlchemyException(Exception):
    """
    Standardized runtime exception used throughout QAlchemy.

    This exception is created by ExceptionHandlingService from an
    ExceptionDefinition loaded from the exception catalog.
    """

    definition: ExceptionDefinition
    context: dict[str, Any] = field(default_factory=dict)
    cause: Exception | None = None

    def __post_init__(self) -> None:
        """Initialize the base Exception with the formatted message."""
        super().__init__(str(self))

    @property
    def code(self) -> str:
        return self.definition.code

    @property
    def message(self) -> str:
        return self.definition.message

    @property
    def severity(self) -> str:
        return self.definition.severity

    @property
    def component(self) -> str:
        return self.definition.component

    @property
    def recoverable(self) -> bool:
        return self.definition.recoverable

    def __str__(self) -> str:
        message = f"[{self.code}] {self.message}"

        if self.context:
            message += f" | context={self.context}"

        return message
