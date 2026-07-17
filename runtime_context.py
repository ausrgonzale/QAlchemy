"""
runtime_context.py

Purpose:
    Carries execution state through the framework.

Version 1:
    Lightweight data object containing runtime information generated during
    execution. This intentionally contains no business logic.

Future:
    Version 1.1 may introduce RuntimeContextService for automatic timing,
    logging, execution statistics, provider metadata, and workflow support.
"""

from datetime import datetime
from pathlib import Path


class RuntimeContext:
    """Holds runtime execution metadata."""

    def __init__(self):
        self.provider: str | None = None
        self.model: str | None = None

        self.source_file: Path | None = None
        self.destination_file: Path | None = None

        self.execution_time: float | None = None
        self.review_date: datetime = datetime.now()
        self.lines_reviewed: int | None = None
