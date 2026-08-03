# =============================================================================
# exception_catalog.py
#
# QAlchemy Community Edition
#
# Copyright (c) 2026
#
# =============================================================================
# Purpose
# -----------------------------------------------------------------------------
# The ExceptionCatalog is responsible for loading, validating, and providing
# access to the QAlchemy exception catalog defined in exceptions.yaml.
#
# The catalog is the single source of truth for all framework exception
# definitions. During initialization, this class reads the YAML catalog,
# validates its structure, converts each section into strongly typed model
# objects, and stores them in memory for fast lookup.
#
# Responsibilities
# -----------------------------------------------------------------------------
# • Load exceptions.yaml
# • Validate the catalog schema
# • Construct immutable model objects
# • Cache exception definitions
# • Provide lookup methods
#
# This class intentionally DOES NOT:
#
# • Raise runtime exceptions
# • Format exception messages
# • Perform logging
# • Contain business logic
# • Modify the catalog after loading
#
# Those responsibilities belong to ExceptionHandlingService.
#
# Architecture
# -----------------------------------------------------------------------------
#
#                     exceptions.yaml
#                            │
#                            ▼
#                   ExceptionCatalog
#                            │
#            ┌───────────────┼────────────────┐
#            ▼               ▼                ▼
#      Components        Prefixes       Exceptions
#            │               │                │
#            └───────────────┼────────────────┘
#                            ▼
#                 ExceptionHandlingService
#                            │
#                            ▼
#                    QAlchemyException
#
# Design Goals
# -----------------------------------------------------------------------------
# • Strongly typed
# • Immutable after construction
# • Single Responsibility Principle
# • Fast dictionary-based lookups
# • Easy to unit test
# • AI-friendly and self-documenting
#
# =============================================================================

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import yaml

from .exception_models import (
    CatalogMetadata,
    ComponentDefinition,
    ExceptionDefinition,
    PrefixDefinition,
)


class ExceptionCatalog:
    """
    Loads and manages the QAlchemy exception catalog.

    The catalog is loaded once during construction and remains read-only for
    the lifetime of the application.

    Every exception definition contained within the catalog is converted into a
    strongly typed ExceptionDefinition object.

    Lookup operations are dictionary based and execute in constant time.

    Parameters
    ----------
    catalog_path:
        Path to exceptions.yaml.
    """

    REQUIRED_SECTIONS = (
        "metadata",
        "origins",
        "severities",
        "categories",
        "components",
        "prefixes",
        "errors",
    )

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------

    def __init__(self, catalog_path: str | Path):

        self._catalog_path = Path(catalog_path)

        self.metadata: CatalogMetadata | None = None

        self._components: dict[str, ComponentDefinition] = {}
        self._prefixes: dict[str, PrefixDefinition] = {}
        self._exceptions: dict[str, ExceptionDefinition] = {}
        self._origins: tuple[str, ...] = ()
        self._severities: tuple[str, ...] = ()
        self._categories: tuple[str, ...] = ()

        self._load_catalog()

    # -------------------------------------------------------------------------
    # Catalog Loading
    # -------------------------------------------------------------------------

    def _load_catalog(self) -> None:
        """
        Loads the YAML catalog from disk and constructs the in-memory object
        model.

        Raises
        ------
        FileNotFoundError
            If the catalog file cannot be located.

        ValueError
            If the catalog is malformed.
        """

        if not self._catalog_path.exists():
            raise FileNotFoundError(
                f"Exception catalog not found: {self._catalog_path}"
            )

        with self._catalog_path.open(
            "r",
            encoding="utf-8",
        ) as stream:

            data = yaml.safe_load(stream) or {}

        self._validate_catalog(data)

        self._build_metadata(data["metadata"])
        self._build_reference_data(data)
        self._build_components(data["components"])
        self._build_prefixes(data["prefixes"])
        self._build_exceptions(data["errors"])

    # -------------------------------------------------------------------------
    # Catalog Validation
    # -------------------------------------------------------------------------

    def _validate_catalog(self, data: dict) -> None:
        """
        Validates the top-level catalog structure.

        Parameters
        ----------
        data:
            Raw YAML dictionary.

        Raises
        ------
        ValueError
            If required sections are missing.
        """

        for section in self.REQUIRED_SECTIONS:

            if section not in data:
                raise ValueError(f"Missing required catalog section '{section}'.")

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    def _build_metadata(self, metadata: dict) -> None:
        """
        Constructs the catalog metadata model.
        """

        self.metadata = CatalogMetadata(
            framework=metadata.get("framework", ""),
            version=metadata.get("version", ""),
            description=metadata.get("description", ""),
        )

    # -------------------------------------------------------------------------
    # Reference Data
    # -------------------------------------------------------------------------

    def _build_reference_data(self, data: dict) -> None:
        """
        Stores the catalog reference lists.

        These collections define the valid values used throughout the catalog.
        They are retained for future validation, reporting, and diagnostics.
        """

        self._origins = tuple(data.get("origins", ()))
        self._severities = tuple(data.get("severities", ()))
        self._categories = tuple(data.get("categories", ()))

    # -------------------------------------------------------------------------
    # Components
    # -------------------------------------------------------------------------

    def _build_components(self, components: dict) -> None:
        """
        Builds all ComponentDefinition objects.
        """

        self._components.clear()

        for name, value in components.items():

            self._components[name] = ComponentDefinition(
                name=name,
                description=value.get("description", ""),
            )

    # -------------------------------------------------------------------------
    # Prefixes
    # -------------------------------------------------------------------------

    def _build_prefixes(self, prefixes: dict) -> None:
        """
        Builds all PrefixDefinition objects.
        """

        self._prefixes.clear()

        for prefix, value in prefixes.items():

            self._prefixes[prefix] = PrefixDefinition(
                prefix=prefix,
                component=value.get("component", ""),
                description=value.get("description", ""),
            )

    # -------------------------------------------------------------------------
    # Exceptions
    # -------------------------------------------------------------------------

    def _build_exceptions(self, errors: dict) -> None:
        """
        Builds all ExceptionDefinition objects.
        """

        self._exceptions.clear()

        for code, value in errors.items():

            self._exceptions[code] = ExceptionDefinition(
                code=code,
                component=value.get("component", ""),
                severity=value.get("severity", ""),
                recoverable=bool(value.get("recoverable", False)),
                message=value.get("message", ""),
                user_message=value.get("user_message", ""),
                recommendation=value.get("recommendation", ""),
                category=value.get("category", ""),
                documentation=value.get("documentation", ""),
            )

    # -------------------------------------------------------------------------
    # Exception Lookup
    # -------------------------------------------------------------------------

    def get_exception(self, code: str) -> ExceptionDefinition:
        """
        Returns an exception definition by its exception code.

        Raises
        ------
        KeyError
            If the exception code does not exist.
        """
        return self._exceptions[code]

    def has_exception(self, code: str) -> bool:
        """
        Returns True if the exception exists.
        """
        return code in self._exceptions

    # -------------------------------------------------------------------------
    # Component Lookup
    # -------------------------------------------------------------------------

    def get_component(self, name: str) -> ComponentDefinition:
        """
        Returns a component definition.

        Raises
        ------
        KeyError
            If the component does not exist.
        """
        return self._components[name]

    def has_component(self, name: str) -> bool:
        """
        Returns True if the component exists.
        """
        return name in self._components

    # -------------------------------------------------------------------------
    # Prefix Lookup
    # -------------------------------------------------------------------------

    def get_prefix(self, prefix: str) -> PrefixDefinition:
        """
        Returns a prefix definition.

        Raises
        ------
        KeyError
            If the prefix does not exist.
        """
        return self._prefixes[prefix]

    def has_prefix(self, prefix: str) -> bool:
        """
        Returns True if the prefix exists.
        """
        return prefix in self._prefixes

    # -------------------------------------------------------------------------
    # Collection Access
    # -------------------------------------------------------------------------

    @property
    def components(self) -> tuple[ComponentDefinition, ...]:
        """
        Returns all registered components.
        """
        return tuple(self._components.values())

    @property
    def prefixes(self) -> tuple[PrefixDefinition, ...]:
        """
        Returns all registered prefixes.
        """
        return tuple(self._prefixes.values())

    @property
    def exceptions(self) -> tuple[ExceptionDefinition, ...]:
        """
        Returns all registered exception definitions.
        """
        return tuple(self._exceptions.values())

    @property
    def origins(self) -> tuple[str, ...]:
        """
        Returns all supported exception origins.
        """
        return self._origins

    @property
    def severities(self) -> tuple[str, ...]:
        """
        Returns all supported severities.
        """
        return self._severities

    @property
    def categories(self) -> tuple[str, ...]:
        """
        Returns all supported exception categories.
        """
        return self._categories

    # -------------------------------------------------------------------------
    # Python Convenience Methods
    # -------------------------------------------------------------------------

    def __contains__(self, code: object) -> bool:
        """
        Supports:

            if "CFG001" in catalog:
                ...
        """
        if not isinstance(code, str):
            return False

        return code in self._exceptions

    def __len__(self) -> int:
        """
        Returns the number of exception definitions.
        """
        return len(self._exceptions)

    def __iter__(self) -> Iterator[ExceptionDefinition]:
        """
        Iterates over every exception definition.

        Example
        -------
            for exception in catalog:
                ...
        """
        return iter(self._exceptions.values())

    def __repr__(self) -> str:
        """
        Returns a concise developer representation.
        """
        version = self.metadata.version if self.metadata else "Unknown"

        return (
            f"{self.__class__.__name__}("
            f"version='{version}', "
            f"exceptions={len(self)}, "
            f"components={len(self._components)})"
        )


# =============================================================================
# End of exception_catalog.py
# =============================================================================
