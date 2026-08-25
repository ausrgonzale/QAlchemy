"""
Unit tests for services.core.client_service.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from services.app.app_configuration_service import AppConfigurationService
from services.core.client_service import ClientService


@pytest.fixture
def configuration() -> AppConfigurationService:
    """
    Returns the test application configuration.
    """

    return AppConfigurationService(
        configuration_file=Path(
            "tests/resources/app/app.yaml",
        ),
    )


def test_create_uses_default_model(
    configuration: AppConfigurationService,
) -> None:
    """
    Should create a Client using the configured default model.
    """

    service = ClientService(
        configuration=configuration.client,
    )

    with patch(
        "services.core.client_service.Client",
    ) as mock_client:

        service.create()

        mock_client.assert_called_once_with(
            provider="ollama",
            model="gpt-oss:120b-cloud",
            request_timeout=120,
            stream=False,
        )


def test_create_uses_model_override(
    configuration: AppConfigurationService,
) -> None:
    """
    Should create a Client using the supplied model override.
    """

    service = ClientService(
        configuration=configuration.client,
    )

    with patch(
        "services.core.client_service.Client",
    ) as mock_client:

        service.create(
            model_override="override-model",
        )

        mock_client.assert_called_once_with(
            provider="ollama",
            model="override-model",
            request_timeout=120,
            stream=False,
        )


def test_create_returns_client_instance(
    configuration: AppConfigurationService,
) -> None:
    """
    Should return the constructed Client instance.
    """

    service = ClientService(
        configuration=configuration.client,
    )

    with patch(
        "services.core.client_service.Client",
    ) as mock_client:

        instance = object()

        mock_client.return_value = instance

        client = service.create()

        assert client is instance


def test_create_propagates_client_construction_exception(
    configuration: AppConfigurationService,
) -> None:
    """
    Should propagate exceptions raised while constructing the Client.
    """

    service = ClientService(
        configuration=configuration.client,
    )

    with (
        patch(
            "services.core.client_service.Client",
            side_effect=RuntimeError("Construction failed"),
        ),
        pytest.raises(
            RuntimeError,
            match="Construction failed",
        ),
    ):
        service.create()
