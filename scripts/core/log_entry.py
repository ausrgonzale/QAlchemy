"""
Structured log entry for QAlchemy.

A LogEntry represents a single application event. It contains only
structured data and performs no formatting or output operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class LogEntry:
    """Represents a single structured log event."""

    timestamp: datetime
    level: str
    component: str
    operation: str | None
    message: str
    exception: Exception | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
