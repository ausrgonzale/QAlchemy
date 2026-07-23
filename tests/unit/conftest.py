"""
Shared pytest fixtures for unit tests.
"""

from pathlib import Path

import pytest

from services.app_configuration_service import LoggingConfiguration


@pytest.fixture
def logging_configuration(tmp_path: Path) -> LoggingConfiguration:
    """Create a temporary logging configuration for unit tests."""

    return LoggingConfiguration(
        {
            "level": "INFO",
            "output_root": str(tmp_path),
            "base_filename": "alchemy",
            "extension": ".log",
            "debug": {
                "enabled": False,
                "save_prompt": False,
                "save_response": False,
                "overwrite_files": True,
            },
        }
    )
