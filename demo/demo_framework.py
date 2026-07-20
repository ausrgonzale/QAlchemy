"""
QAlchemy Framework Demonstration

Purpose:
    Demonstrates the core capabilities of the QAlchemy framework by
    generating sample Python code and performing an AI code review.

Workflow:
    1. Generate sample Python code.
    2. Verify the generated file exists.
    3. Review the generated source code.
    4. Save the review report.

This script is intended as a quick introduction to the framework and
serves as a simple end-to-end demonstration.
"""

import subprocess
import sys
from pathlib import Path

DEMO_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = DEMO_ROOT.parent
SAMPLE_CODE_DIR = DEMO_ROOT / "sample_code"
OUTPUT_DIR = DEMO_ROOT / "output"

SOURCE_FILE = SAMPLE_CODE_DIR / "calculator.py"
REPORT_FILE = OUTPUT_DIR / "calculator_review.md"


def run(command: list[str]) -> None:
    """
    Run a command and fail immediately if it exits with an error.
    """

    display_command = []

    for item in command:
        try:
            display_command.append(str(Path(item).resolve().relative_to(PROJECT_ROOT)))
        except ValueError:
            display_command.append(item)

    subprocess.run(command, check=True)


def main() -> None:
    """Execute the QAlchemy demonstration."""

    print("=" * 60)
    print("QAlchemy Community Framework Demonstration")
    print("=" * 60)

    SAMPLE_CODE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Clean previous demo artifacts
    # ------------------------------------------------------------------

    if SOURCE_FILE.exists():
        SOURCE_FILE.unlink()

    if REPORT_FILE.exists():
        REPORT_FILE.unlink()

    # ------------------------------------------------------------------
    # Generate source code
    # ------------------------------------------------------------------

    print("\nGenerating sample source code...")

    run(
        [
            sys.executable,
            "-m",
            "scripts.generate_code",
            "--instructions",
            (
                "Create a Python class named Calculator with "
                "add, subtract, multiply, and divide methods."
            ),
            "--output",
            str(SOURCE_FILE),
        ]
    )

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Generated source file was not created:\n{SOURCE_FILE.resolve()}"
        )

    print("✓ Source code generated successfully.")

    # ------------------------------------------------------------------
    # Review generated source code
    # ------------------------------------------------------------------

    print("\nReviewing generated source code...")

    run(
        [
            sys.executable,
            "-m",
            "scripts.review_source_code",
            str(SOURCE_FILE),
            "--output",
            str(REPORT_FILE),
        ]
    )

    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            f"Review report was not created:\n{REPORT_FILE.resolve()}"
        )

    print("✓ Code review completed successfully.")

    # ------------------------------------------------------------------
    # Demo summary
    # ------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)

    try:
        generated_source = SOURCE_FILE.resolve().relative_to(Path.cwd())
    except ValueError:
        generated_source = SOURCE_FILE.resolve()

    try:
        review_report = REPORT_FILE.resolve().relative_to(Path.cwd())
    except ValueError:
        review_report = REPORT_FILE.resolve()

    print(f"\nGenerated Source : {generated_source}")
    print(f"Review Report    : {review_report}")

    print("\nThank you for trying QAlchemy!")
    print("Explore the generated report to see the framework in action.")


if __name__ == "__main__":
    main()
