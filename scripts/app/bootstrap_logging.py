"""
Configure Python logging during application startup.
"""

import logging
from pathlib import Path


def configure_bootstrap_logging() -> None:
    """
    Configure Python logging for application startup.
    """

    log_directory = Path("logs")
    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.basicConfig(
        filename=log_directory / "qalchemy.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
