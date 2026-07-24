"""
File: tests/runtime/test_runtime_context.py

Description:
    Unit tests for the RuntimeContext class.

Purpose:
    Verify RuntimeContext initializes correctly, stores execution metadata,
    and maintains independent execution state between instances.
"""

from datetime import UTC, datetime
from pathlib import Path

from runtime_context import RuntimeContext


class TestRuntimeContext:
    """Unit tests for RuntimeContext."""

    def test_runtime_context_initializes_with_default_values(self):
        """Verify a new RuntimeContext initializes all properties to None."""

        context = RuntimeContext()

        assert context.provider is None
        assert context.model is None

        assert context.source_file is None
        assert context.destination_file is None

        assert context.execution_time is None
        assert isinstance(context.review_date, datetime)
        assert context.lines_reviewed is None

    def test_runtime_context_stores_execution_metadata(self):
        """Verify RuntimeContext stores execution metadata correctly."""

        context = RuntimeContext()

        context.provider = "ollama"
        context.model = "qwen3-coder:480b-cloud"

        context.source_file = Path("tests/ui/test_google_search.py")
        context.destination_file = Path("reports/test_google_search_review.md")

        context.execution_time = 4.25

        review_date = datetime(2026, 7, 11, 9, 30, 0, tzinfo=UTC)

        context.review_date = review_date

        context.lines_reviewed = 143

        assert context.provider == "ollama"
        assert context.model == "qwen3-coder:480b-cloud"

        assert context.source_file == Path("tests/ui/test_google_search.py")
        assert context.destination_file == Path("reports/test_google_search_review.md")

        assert context.execution_time == 4.25
        assert context.review_date == review_date
        assert context.lines_reviewed == 143

    def test_runtime_context_updates_individual_properties(self):
        """Verify updating one property does not affect other properties."""

        context = RuntimeContext()

        context.provider = "ollama"
        context.model = "qwen3-coder:480b-cloud"

        # Update only the model
        context.model = "llama3.2:latest"

        assert context.provider == "ollama"
        assert context.model == "llama3.2:latest"

    def test_runtime_context_instances_are_independent(self):
        """Verify multiple RuntimeContext instances do not share state."""

        first = RuntimeContext()
        second = RuntimeContext()

        first.provider = "ollama"
        first.model = "model-a"

        second.provider = "openai"
        second.model = "model-b"

        assert first.provider == "ollama"
        assert first.model == "model-a"

        assert second.provider == "openai"
        assert second.model == "model-b"
