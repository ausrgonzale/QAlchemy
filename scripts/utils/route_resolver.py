"""
QAlchemy Route Resolver
=======================

Purpose
-------
Resolves a RuntimeRequest into a QAlchemy-native route for workflow execution.

Responsibilities
----------------
- Analyze the RuntimeRequest routing context.
- Communicate with the configured model to determine the appropriate route.
- Resolve the model response into a QAlchemy route representation.
- Validate the resolved route before returning it to the caller.

Out of Scope
------------
- WorkOrder construction.
- Feature workflow execution.
- Agent execution.
- Feature-specific business logic.
- Workflow persistence.
- Application orchestration.

Flow
----
RuntimeRequest
    ↓
RouteResolver
    ↓
Model communication
    ↓
Route response
    ↓
QAlchemy route
    ↓
OrchestrationService

Design
------
The RouteResolver provides a narrow boundary between application
orchestration and model-based route resolution. The model determines
the appropriate target, capability, and role; the resolver translates
that response into a QAlchemy-native representation that can be used
throughout the execution flow.

The resolver is intentionally independent of feature execution and
should be reusable anywhere QAlchemy requires route resolution.
"""

import json
from dataclasses import dataclass

from clients.client import Client
from scripts.core.runtime_request import RuntimeRequest

ROUTE_SYSTEM_INSTRUCTIONS = """
Determine the appropriate QAlchemy route for the supplied runtime request.

Return only a valid JSON object with exactly these fields:

{
    "target": "<target>",
    "capability": "<capability>",
    "role": "<role>"
}

Definitions:

target
    The canonical QAlchemy feature target.

    Allowed values:
    - generate_code
    - review_code
    - requirements

capability
    The operation that should be performed for that target.

    Allowed values:
    - For generate_code: generate_code
    - For review_code: review_code
    - For requirements:
        - evaluate
        - generate
        - refine
        - create_acceptance_criteria
        - create_test_cases

role
    The engineering role appropriate for performing the work.

    Select the role only from the existing role resources available to QAlchemy.
    If no existing role is an appropriate match, return "unknown".

Rules:

- Determine the route from the supplied runtime request.
- Use only the canonical target values defined above.
- Use only the canonical capability values defined above.
- Never invent or create a role name.
- If no existing role matches the requested work, return "unknown".
- Do not perform the requested work.
- Do not provide explanations.
- Do not return Markdown.
- Return only the JSON object.
"""


@dataclass(frozen=True, slots=True)
class Route:
    """QAlchemy-native route resolved for a runtime request."""

    target: str
    capability: str
    role: str


class RouteResolver:
    """
    Resolves a RuntimeRequest into a QAlchemy-native Route.
    """

    def __init__(self, client: Client) -> None:
        """
        Initialize the route resolver.

        Args:
            client:
                Configured client used to communicate with the model.
        """

        self._client = client

    def resolve(
        self,
        runtime_request: RuntimeRequest,
    ) -> Route:
        """
        Resolve the route for the supplied runtime request.
        """

        prompt = self._build_prompt(runtime_request)

        response = self._client.generate(prompt)

        return self._parse_response(response)

    def _build_prompt(
        self,
        runtime_request: RuntimeRequest,
    ) -> str:
        """
        Build the routing request sent to the model.
        """

        return (
            f"{ROUTE_SYSTEM_INSTRUCTIONS}\n\n"
            "RUNTIME REQUEST\n\n"
            f"TASK:\n{runtime_request.task}\n\n"
            f"DELIVERABLE:\n{runtime_request.deliverable}\n"
        )

    def _parse_response(
        self,
        response: str,
    ) -> Route:
        """
        Parse and validate the model routing response.
        """

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Route resolver returned invalid JSON.",
            ) from exc

        if not isinstance(data, dict):
            raise TypeError(
                "Route resolver response must be a JSON object.",
            )

        required_fields = (
            "target",
            "capability",
            "role",
        )

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(
                "Route resolver response is missing required fields: "
                + ", ".join(missing_fields),
            )

        return Route(
            target=str(data["target"]),
            capability=str(data["capability"]),
            role=str(data["role"]),
        )
