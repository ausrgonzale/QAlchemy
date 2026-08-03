"""
Generate source code using the AI code generation service.
"""

import argparse
import logging
from pathlib import Path

from services.feature.code_generation_service import CodeGenerationService

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(description="Generate source code using AI.")

    parser.add_argument(
        "--instructions",
        required=True,
        help="Instructions describing the code to generate.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Target output file.",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the default AI model configured for the application.",
    )

    return parser.parse_args()


def normalize_response(response: str) -> str:
    """
    Normalize AI-generated source code before writing it to disk.

    Removes Markdown code fences and surrounding whitespace.
    """

    response = response.strip()

    lines = response.splitlines()

    # Remove opening Markdown fence (``` or ```python)
    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    # Remove closing Markdown fence
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def main() -> None:
    """
    Generate source code from the supplied instructions and write it
    to the requested output file or output directory.
    """

    logger.info("Starting code generation script.")

    try:
        args = parse_arguments()

        service = CodeGenerationService()

        output_path = Path(args.output)

        response = service.generate(
            task=args.instructions,
            model_override=args.model,
        )

        response = normalize_response(response)

        # Support either an output directory or a specific output file.
        if output_path.suffix == "":
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / "response.md"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(
            response.rstrip() + "\n",
            encoding="utf-8",
        )

        try:
            display_path = output_path.resolve().relative_to(Path.cwd())
        except ValueError:
            display_path = output_path.resolve()

        logger.info("Code generation script completed successfully.")
        print(f"Code written to: {display_path}")

    except Exception:
        logger.exception("Code generation script failed.")
        raise


if __name__ == "__main__":
    main()
