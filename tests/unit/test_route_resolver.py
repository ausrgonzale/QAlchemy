"""
QAlchemy Route Resolver Tests
=============================

Purpose
-------
Validate RouteResolver behavior and its contract for converting runtime
requests into QAlchemy-native routes.

Coverage
--------
- Route resolution from valid model responses.
- Routing prompt construction.
- Model response parsing.
- Invalid JSON handling.
- Invalid response type handling.
- Missing route field validation.

Test Organization
-----------------
Tests are grouped under the ``route`` pytest marker.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from clients.client import Client
from scripts.core.runtime_request import RuntimeRequest
from scripts.utils.route_resolver import Route, RouteResolver


@pytest.mark.route
class TestRouteResolver:
    """Tests for RouteResolver."""

    def test_resolve_returns_route_from_valid_response(self) -> None:
        client = Mock(spec=Client)
        client.generate.return_value = """
        {
            "target": "requirements",
            "capability": "evaluate",
            "role": "business_analyst"
        }
        """

        runtime_request = RuntimeRequest(
            task="Evaluate the supplied requirement.",
            role=None,
            target="",
            deliverable=Path("resources/deliverable/requirement.md"),
        )

        resolver = RouteResolver(client)

        route = resolver.resolve(runtime_request)

        assert isinstance(route, Route)
        assert route.target == "requirements"
        assert route.capability == "evaluate"
        assert route.role == "business_analyst"

    def test_resolve_sends_runtime_request_to_client(self) -> None:
        client = Mock(spec=Client)
        client.generate.return_value = """
        {
            "target": "requirements",
            "capability": "evaluate",
            "role": "business_analyst"
        }
        """

        runtime_request = RuntimeRequest(
            task="Evaluate the supplied requirement.",
            role=None,
            target="",
            deliverable=Path("resources/deliverable/requirement.md"),
        )

        resolver = RouteResolver(client)

        resolver.resolve(runtime_request)

        client.generate.assert_called_once()

        prompt = client.generate.call_args.args[0]

        assert "RUNTIME REQUEST" in prompt
        assert "Evaluate the supplied requirement." in prompt
        assert "resources/deliverable/requirement.md" in prompt

    def test_resolve_raises_value_error_for_invalid_json(self) -> None:
        client = Mock(spec=Client)
        client.generate.return_value = "not valid json"

        runtime_request = RuntimeRequest(
            task="Evaluate the supplied requirement.",
            role=None,
            target="",
            deliverable=Path("resources/deliverable/requirement.md"),
        )

        resolver = RouteResolver(client)

        with pytest.raises(ValueError, match="invalid JSON"):
            resolver.resolve(runtime_request)

    def test_resolve_raises_type_error_for_non_object_response(self) -> None:
        client = Mock(spec=Client)
        client.generate.return_value = (
            '["requirements", "evaluate", "business_analyst"]'
        )

        runtime_request = RuntimeRequest(
            task="Evaluate the supplied requirement.",
            role=None,
            target="",
            deliverable=Path("resources/deliverable/requirement.md"),
        )

        resolver = RouteResolver(client)

        with pytest.raises(TypeError, match="must be a JSON object"):
            resolver.resolve(runtime_request)

    def test_resolve_raises_value_error_for_missing_route_fields(self) -> None:
        client = Mock(spec=Client)
        client.generate.return_value = """
        {
            "target": "requirements",
            "capability": "evaluate"
        }
        """

        runtime_request = RuntimeRequest(
            task="Evaluate the supplied requirement.",
            role=None,
            target="",
            deliverable=Path("resources/deliverable/requirement.md"),
        )

        resolver = RouteResolver(client)

        with pytest.raises(
            ValueError,
            match="missing required fields: role",
        ):
            resolver.resolve(runtime_request)
