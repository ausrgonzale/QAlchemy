"""
Review source code using the AI code review service.
"""

import argparse
import time
from pathlib import Path

from reporting import ReportWriter
from runtime_context import RuntimeContext
from services.code_review_service import CodeReviewService
from services.framework_configuration_service import (
    FrameworkConfigurationService,
)


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

    configuration = FrameworkConfigurationService()

    writer = ReportWriter(configuration)

    writer.write(
        review=review,
        runtime_context=runtime_context,
    )

    print(f"\n✓ Review report written to: {runtime_context.destination_file}")


if __name__ == "__main__":
    main()
