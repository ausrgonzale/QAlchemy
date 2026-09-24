"""
===============================================================================
Unit Tests

QAlchemy Application Entry Point

Validates command-line argument parsing for the QAlchemy application.

Responsibilities Tested
-----------------------
- Required task argument
- Required role argument
- Required target argument
- Required deliverable path
- Optional reference arguments
- Multiple reference arguments
===============================================================================
"""

from __future__ import annotations

import sys

import pytest

from app import qalchemy

pytestmark = pytest.mark.application


def test_parses_required_arguments(monkeypatch) -> None:
    """Parse all required command-line arguments."""

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "qalchemy",
            "--task",
            "Create a Playwright test.",
            "--role",
            "playwright_generate",
            "--target",
            "generate-code",
            "--deliverable",
            "deliverable.md",
        ],
    )

    args = qalchemy.parse_arguments()

    assert args.task == "Create a Playwright test."
    assert args.role == "playwright_generate"
    assert args.target == "generate-code"
    assert args.deliverable == "deliverable.md"
    assert args.reference is None


def test_parses_reference_argument(monkeypatch) -> None:
    """Parse an optional reference argument."""

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "qalchemy",
            "--task",
            "Create a Playwright test.",
            "--role",
            "playwright_generate",
            "--target",
            "generate-code",
            "--deliverable",
            "deliverable.md",
            "--reference",
            "playwright.md",
        ],
    )

    args = qalchemy.parse_arguments()

    assert args.reference == ["playwright.md"]


def test_parses_multiple_reference_arguments(monkeypatch) -> None:
    """Parse multiple optional reference arguments."""

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "qalchemy",
            "--task",
            "Create a Playwright test.",
            "--role",
            "playwright_generate",
            "--target",
            "generate-code",
            "--deliverable",
            "deliverable.md",
            "--reference",
            "playwright.md",
            "--reference",
            "python.md",
        ],
    )

    args = qalchemy.parse_arguments()

    assert args.reference == [
        "playwright.md",
        "python.md",
    ]
