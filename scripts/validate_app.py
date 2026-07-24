#!/usr/bin/env python3
"""
QAlchemy Project Validator

Internal developer validation utility.

This script performs fast validation checks intended to be run
frequently during development.

Usage:
    python -m scripts.validate_app
    python scripts/validate_app.py
"""

from __future__ import annotations

import logging
import subprocess
import sys
import time
from pathlib import Path

# Support direct script execution as well as module execution.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.app_configuration_service import AppConfigurationService

logger = logging.getLogger(__name__)


class ValidationError(RuntimeError):
    """Raised when project validation fails."""


class Validator:
    """Internal project validator."""

    def __init__(self):
        self.repo = Path(__file__).resolve().parents[1]

        self.python = (
            self.repo
            / ".venv"
            / ("Scripts/python.exe" if sys.platform.startswith("win") else "bin/python")
        )

        self.config = AppConfigurationService().load()

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def status(message: str):
        logger.info(message)
        print(f"✓ {message}")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_environment(self):
        print("\nEnvironment")

        if not self.repo.exists():
            raise ValidationError("Repository not found.")

        if not self.python.exists():
            raise ValidationError("Virtual environment not found.")

        self.status("Repository")
        self.status("Virtual Environment")
        self.status(
            f"Configuration ({self.config.app.name} " f"v{self.config.app.version})"
        )

    def validate_project_structure(self):
        print("\nProject Structure")

        required_paths = [
            "clients",
            "demo",
            "prompts",
            "reports",
            "scripts",
            "services",
            "templates",
            "tests",
        ]

        for path in required_paths:
            full_path = self.repo / path

            if not full_path.exists():
                raise ValidationError(f"Missing required path: {path}")

            self.status(path)

    def validate_unit_tests(self):
        print("\nUnit Tests")

        result = subprocess.run(
            [
                str(self.python),
                "-m",
                "pytest",
                "tests/unit",
            ],
            cwd=self.repo,
            check=False,
        )

        if result.returncode != 0:
            raise ValidationError("Unit tests failed.")

        self.status("All unit tests passed")

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self):
        start = time.perf_counter()

        logger.info("Starting project validation.")

        try:
            self.validate_environment()
            self.validate_project_structure()
            self.validate_unit_tests()

            elapsed = time.perf_counter() - start

            logger.info("Project validation completed successfully.")
            print(f"\nProject Validation PASSED ({elapsed:.2f}s)")
            return 0

        except Exception as exc:
            logger.exception("Project validation failed.")
            print(f"\nProject Validation FAILED: {exc}")
            return 1


def main():
    return Validator().run()


if __name__ == "__main__":
    raise SystemExit(main())
