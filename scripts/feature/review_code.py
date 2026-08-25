"""
Review source code using the AI code review service.
"""

import argparse
import logging
import time
from pathlib import Path

from archive.prototype.archive.code_review_service import CodeReviewService
from scripts.core.report_writer import ReportWriter
from scripts.utils.runtime_context import RuntimeContext
from services.app.app_configuration_service import (
    AppConfigurationService,
)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(description="Review source code using AI.")

    parser.add_argument(
        "source",
        help="Source code file to review.",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display review statistics.",
    )

    parser.add_argument("--model", help="Override the configured AI model.")

    parser.add_argument(
        "--output",
        help="Destination path for the generated review report.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Review the supplied source code file using AI.
    """

    logger.info("Starting code review script.")

    try:
        args = parse_arguments()

        source_path = Path(args.source)

        if not source_path.is_file():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        source_code = source_path.read_text(encoding="utf-8")

        runtime_context = RuntimeContext()

        if args.output:
            runtime_context.destination_file = Path(args.output)

        runtime_context.source_file = source_path

        start_time = time.perf_counter()

        service = CodeReviewService()

        review = service.execute(
            source_code,
            runtime_context=runtime_context,
            model_override=args.model,
        )

        runtime_context.execution_time = time.perf_counter() - start_time

        configuration = AppConfigurationService()

        writer = ReportWriter(configuration)

        writer.write(
            review=review,
            runtime_context=runtime_context,
        )

        if runtime_context.destination_file is not None:
            try:
                display_path = runtime_context.destination_file.resolve().relative_to(
                    Path.cwd()
                )
            except ValueError:
                display_path = runtime_context.destination_file.resolve()

            print(f"\n✓ Review report written to: {display_path}")

        logger.info("Code review script completed successfully.")

    except Exception:
        logger.exception("Code review script failed.")
        raise


if __name__ == "__main__":
    main()
