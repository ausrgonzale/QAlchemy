# =============================================================================
# client_service.py
#
# QAlchemy Community Edition
#
# Copyright (c) 2026
#
# =============================================================================
# Purpose
# -----------------------------------------------------------------------------
# Provides centralized construction of configured AI client instances.
#
# ClientService consumes the AppConfigurationService and returns fully
# configured Client instances for engineering workflows. This centralizes
# client creation and ensures all runtime participants use a consistent
# provider and model configuration.
#
# Responsibilities
# -----------------------------------------------------------------------------
# • Consume application client configuration.
# • Resolve provider selection.
# • Resolve model overrides.
# • Create configured Client instances.
# • Serve as the single runtime entry point for client creation.
#
# Does Not
# -----------------------------------------------------------------------------
# • Execute client requests.
# • Build prompts.
# • Perform business logic.
# • Orchestrate workflows.
# • Cache or pool clients (future enhancement).
#
# Architecture
# -----------------------------------------------------------------------------
#
#               AppConfigurationService
#                         │
#                         ▼
#                  ClientService
#                         │
#                         ▼
#                     Client
#
# =============================================================================

from __future__ import annotations

import logging

from clients.client import Client
from services.app.app_configuration_service import (
    ClientConfiguration,
)

logger = logging.getLogger(__name__)


class ClientService:
    """
    Creates configured Client instances for QAlchemy.
    """

    def __init__(
        self,
        configuration: ClientConfiguration,
    ) -> None:
        """
        Initialize the client service.

        Parameters
        ----------
        configuration:
            The application configuration used to construct clients.
        """

        self._configuration = configuration

    def create(
        self,
        model_override: str | None = None,
    ) -> Client:
        """
        Create a configured Client.

        Parameters
        ----------
        model_override:
            Optional model override supplied by the caller.

        Returns
        -------
        Client
            A fully configured AI client.
        """

        logger.info("Creating client.")

        provider = self._configuration.provider
        model = model_override or self._configuration.default_model

        if model_override is not None:
            logger.debug(
                "Using model override: %s",
                model_override,
            )

        client = Client(
            provider=provider,
            model=model,
            request_timeout=self._configuration.request_timeout,
            stream=self._configuration.stream,
        )

        logger.info("Client created successfully.")

        return client
