"""
QAlchemy Application Entry Point

Purpose
-------
QAlchemy is the executable entry point into the application.

Responsibilities
----------------
1. Parse command-line arguments.
2. Validate command-line arguments.
3. Create a RuntimeRequest.
4. Bootstrap the application.
5. Hand the RuntimeRequest to the OrchestrationService.

This module intentionally contains no business logic.
"""

import argparse
from pathlib import Path

from scripts.core.runtime_request import RuntimeRequest
from services.app.app_bootstrap_service import (
    AppBootstrapService,
)


def parse_arguments() -> argparse.Namespace:
    """Parse QAlchemy command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="qalchemy",
        description="QAlchemy AI Engineering Application",
    )

    parser.add_argument(
        "--task",
        required=True,
        help="Engineering task to perform.",
    )

    parser.add_argument(
        "--role",
        required=False,
        help="Engineering role to perform the task.",
    )

    parser.add_argument(
        "--target",
        required=False,
        help="Target engineering capability.",
    )

    parser.add_argument(
        "--deliverable",
        required=True,
        help="Path to a deliverable document.",
    )

    parser.add_argument(
        "--source_code",
        action="append",
        help=(
            "Path to source code file or directory. " "May be specified multiple times."
        ),
    )

    parser.add_argument(
        "--reference",
        action="append",
        help="Path to optional reference material. May be specified multiple times.",
    )

    return parser.parse_args()


def main() -> int:
    """
    Application entry point.
    """

    args = parse_arguments()

    runtime_request = RuntimeRequest(
        task=args.task,
        role=Path(args.role) if args.role else None,
        target=args.target,
        deliverable=Path(args.deliverable),
        source_code=[Path(p) for p in (args.source_code or [])],
        references=[Path(p) for p in (args.reference or [])],
    )

    bootstrap = AppBootstrapService().bootstrap()

    orchestration = bootstrap.orchestration_service

    orchestration.execute(runtime_request)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
