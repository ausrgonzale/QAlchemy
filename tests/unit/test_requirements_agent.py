"""
Unit tests for the QAlchemy Requirements Agent.

Responsibilities:
    - Verify RequirementsAgent initialization.
    - Verify provider transformation.
    - Verify Agent/Client interaction.
    - Verify structured model response handling.
    - Verify Agent tool execution.

Non-Responsibilities:
    - Test real model reasoning quality.
    - Test role selection.
    - Test Jira integration.
    - Test REST endpoints.
    - Test OrchestrationService integration.

Test Organization:
    - Initialization
    - Provider Transformation
    - Client Interaction
    - Response Handling
    - Tool Interaction

Pytest Markers:
    - agent
    - requirements
"""

import json
from pathlib import Path

import pytest

from agents.contracts.res_agent_response import AgentResponse
from agents.contracts.res_agent_results import (
    RequirementsAgentResult,
    RequirementsCapability,
    RequirementsReadiness,
    RequirementsStatus,
)
from agents.tools.tool_call import ToolCall

pytestmark = [
    pytest.mark.agent,
    pytest.mark.requirements,
]


@pytest.fixture
def requirements_agent_response() -> str:
    """Return a valid structured RequirementsAgent response."""
    return """
    {
        "role": "business_analyst",
        "capability": "evaluate",
        "status": "needs_clarification",
        "summary": "Requirement requires additional clarification.",
        "findings": {
            "strengths": ["Business intent is clear."],
            "gaps": ["Acceptance criteria are missing."],
            "ambiguities": ["Expected reset behavior is not defined."],
            "assumptions": []
        },
        "readiness": {
            "implementation": "not_ready",
            "test_cases": "not_ready",
            "acceptance_criteria": "not_ready"
        },
        "recommended_actions": [
            "Define the password reset workflow."
        ],
        "confidence": "HIGH",
        "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement requires additional clarification."
    }
    """


@pytest.fixture
def requirements_agent_work_order(requirements_work_order) -> str:
    """Return a Work Order containing the requirement source path."""
    return (
        requirements_work_order
        + "\nSOURCE CODE\n\n"
        + "**-------------------------------------------------------------------------------**\n\n"
        + "resources/requirements/requirement.json\n"
    )


def _agent_response(content: str) -> AgentResponse:
    """Create a final Agent response containing structured result content."""
    return AgentResponse(
        content=content,
        tool_calls=(),
    )


class TestRequirementsAgentProviderTransformation:
    """Tests RequirementsAgent provider transformation."""

    def test_provider_transformer_receives_work_order(
        self,
        requirements_agent,
        requirements_agent_work_order,
        provider_transformer,
        client,
        requirements_agent_response,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            requirements_agent_response,
        )

        requirements_agent.execute(
            requirements_agent_work_order,
        )

        provider_transformer.transform.assert_called_once()


class TestRequirementsAgentClientInteraction:
    """Tests RequirementsAgent Client interaction."""

    def test_client_receives_transformed_request(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            """
            {
                "role": "business_analyst",
                "capability": "evaluate",
                "status": "needs_clarification",
                "summary": "Requirement requires additional clarification.",
                "findings": {
                    "strengths": ["Business intent is clear."],
                    "gaps": ["Acceptance criteria are missing."],
                    "ambiguities": ["Expected reset behavior is not defined."],
                    "assumptions": []
                },
                "readiness": {
                    "implementation": "not_ready",
                    "test_cases": "not_ready",
                    "acceptance_criteria": "not_ready"
                },
                "recommended_actions": [
                    "Define the password reset workflow."
                ],
                "confidence": "HIGH",
                    "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement requires additional clarification."
            }
            """,
        )

        result = requirements_agent.execute(
            requirements_agent_work_order,
        )

        provider_transformer.transform.assert_called_once()
        client.agent_turn.assert_called()
        assert isinstance(result, RequirementsAgentResult)


class TestRequirementsAgentResponseHandling:
    """Tests RequirementsAgent response handling."""

    def test_model_response_is_converted_to_result(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            """
            {
                "role": "business_analyst",
                "capability": "evaluate",
                "status": "needs_clarification",
                "summary": "Requirement requires additional clarification.",
                "findings": {
                    "strengths": ["Business intent is clear."],
                    "gaps": ["Acceptance criteria are missing."],
                    "ambiguities": ["Expected reset behavior is not defined."],
                    "assumptions": []
                },
                "readiness": {
                    "implementation": "not_ready",
                    "test_cases": "not_ready",
                    "acceptance_criteria": "not_ready"
                },
                "recommended_actions": [
                    "Define the password reset workflow."
                ],
                "confidence": "HIGH",
                    "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement requires additional clarification."
            }
            """,
        )

        result = requirements_agent.execute(
            requirements_agent_work_order,
        )

        assert isinstance(result, RequirementsAgentResult)
        assert result.capability == RequirementsCapability.EVALUATE
        assert result.status == RequirementsStatus.NEEDS_CLARIFICATION
        assert result.summary == "Requirement requires additional clarification."
        assert result.findings.strengths == ("Business intent is clear.",)
        assert result.findings.gaps == ("Acceptance criteria are missing.",)
        assert result.findings.ambiguities == (
            "Expected reset behavior is not defined.",
        )
        assert result.findings.assumptions == ()
        assert result.readiness.implementation == RequirementsReadiness.NOT_READY
        assert result.readiness.test_cases == RequirementsReadiness.NOT_READY
        assert result.readiness.acceptance_criteria == RequirementsReadiness.NOT_READY
        assert result.recommended_actions == ("Define the password reset workflow.",)
        assert result.confidence == "HIGH"

    def test_invalid_model_response_raises_json_error(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            "This is not valid JSON.",
        )

        with pytest.raises(json.JSONDecodeError):
            requirements_agent.execute(
                requirements_agent_work_order,
            )

    def test_missing_required_response_field_raises_key_error(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            """
            {
                "status": "needs_clarification",
                "summary": "Requirement needs clarification.",
                "findings": {
                    "strengths": [],
                    "gaps": [],
                    "ambiguities": [],
                    "assumptions": []
                },
                "readiness": {
                    "implementation": "not_ready",
                    "test_cases": "not_ready",
                    "acceptance_criteria": "not_ready"
                },
                "recommended_actions": [],
                "confidence": "HIGH",
                    "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."
            }
            """,
        )

        with pytest.raises(KeyError):
            requirements_agent.execute(
                requirements_agent_work_order,
            )

    def test_invalid_capability_raises_value_error(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            """
            {
                "role": "business_analyst",
                "capability": "analyze_requirement",
                "status": "needs_clarification",
                "summary": "Requirement needs clarification.",
                "findings": {
                    "strengths": [],
                    "gaps": [],
                    "ambiguities": [],
                    "assumptions": []
                },
                "readiness": {
                    "implementation": "not_ready",
                    "test_cases": "not_ready",
                    "acceptance_criteria": "not_ready"
                },
                "recommended_actions": [],
                "confidence": "HIGH",
                    "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."
            }
            """,
        )

        with pytest.raises(ValueError):
            requirements_agent.execute(
                requirements_agent_work_order,
            )

    def test_invalid_status_raises_value_error(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            """
            {
                "role": "business_analyst",
                "capability": "evaluate",
                "status": "complete",
                "summary": "Requirement assessment.",
                "findings": {
                    "strengths": [],
                    "gaps": [],
                    "ambiguities": [],
                    "assumptions": []
                },
                "readiness": {
                    "implementation": "not_ready",
                    "test_cases": "not_ready",
                    "acceptance_criteria": "not_ready"
                },
                "recommended_actions": [],
                "confidence": "HIGH",
                    "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."
            }
            """,
        )

        with pytest.raises(ValueError):
            requirements_agent.execute(
                requirements_agent_work_order,
            )

    def test_invalid_readiness_raises_value_error(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            """
            {
                "role": "business_analyst",
                "capability": "evaluate",
                "status": "needs_clarification",
                "summary": "Requirement needs clarification.",
                "findings": {
                    "strengths": [],
                    "gaps": [],
                    "ambiguities": [],
                    "assumptions": []
                },
                "readiness": {
                    "implementation": "maybe",
                    "test_cases": "not_ready",
                    "acceptance_criteria": "not_ready"
                },
                "recommended_actions": [],
                "confidence": "HIGH",
                    "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."
            }
            """,
        )

        with pytest.raises(ValueError):
            requirements_agent.execute(
                requirements_agent_work_order,
            )

    def test_invalid_summary_type_raises_type_error(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
    ):
        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.return_value = _agent_response(
            """
            {
                "role": "business_analyst",
                "capability": "evaluate",
                "status": "needs_clarification",
                "summary": 123,
                "findings": {
                    "strengths": [],
                    "gaps": [],
                    "ambiguities": [],
                    "assumptions": []
                },
                "readiness": {
                    "implementation": "not_ready",
                    "test_cases": "not_ready",
                    "acceptance_criteria": "not_ready"
                },
                "recommended_actions": [],
                "confidence": "HIGH",
                    "report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."
            }
            """,
        )

        with pytest.raises(TypeError):
            requirements_agent.execute(
                requirements_agent_work_order,
            )


class TestRequirementsAgentToolInteraction:
    """Tests RequirementsAgent tool interaction."""

    def test_agent_executes_tool_requested_by_model(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
        read_file_tool,
    ):
        read_file_tool.read_file.return_value = (
            '{"key": "PROJ-123", "description": "Password Reset"}'
        )

        provider_transformer.transform.return_value = "transformed request"

        client.agent_turn.side_effect = [
            AgentResponse(
                content="",
                tool_calls=(
                    ToolCall(
                        name="read_file",
                        arguments={
                            "path": "resources/requirements/requirement.json",
                        },
                    ),
                ),
            ),
            AgentResponse(
                content=(
                    '{"role": "business_analyst",'
                    '"capability": "evaluate",'
                    '"status": "needs_clarification",'
                    '"summary": "Requirement requires additional clarification.",'
                    '"findings": {'
                    '"strengths": [],'
                    '"gaps": [],'
                    '"ambiguities": [],'
                    '"assumptions": []'
                    "},"
                    '"readiness": {'
                    '"implementation": "not_ready",'
                    '"test_cases": "not_ready",'
                    '"acceptance_criteria": "not_ready"'
                    "},"
                    '"recommended_actions": [],'
                    '"confidence": "HIGH",'
                    '"report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."}'
                ),
                tool_calls=(),
            ),
        ]

        result = requirements_agent.execute(
            requirements_agent_work_order,
        )

        assert isinstance(result, RequirementsAgentResult)

        read_file_tool.read_file.assert_called_once_with(
            Path(
                "resources/requirements/requirement.json",
            ),
        )

        assert client.agent_turn.call_count == 2

    def test_agent_lists_directory_when_requested_by_model(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
        read_file_tool,
    ):
        provider_transformer.transform.return_value = "transformed request"

        read_file_tool.list_directory.return_value = (
            Path("templates/requirements_evaluation_report_template.md"),
            Path("agent/templates/code_review_report_template.md"),
        )

        client.agent_turn.side_effect = [
            AgentResponse(
                content="",
                tool_calls=(
                    ToolCall(
                        name="list_directory",
                        arguments={
                            "path": "templates",
                        },
                    ),
                ),
            ),
            AgentResponse(
                content=(
                    '{"role": "business_analyst",'
                    '"capability": "evaluate",'
                    '"status": "needs_clarification",'
                    '"summary": "Requirement requires additional clarification.",'
                    '"findings": {'
                    '"strengths": [],'
                    '"gaps": [],'
                    '"ambiguities": [],'
                    '"assumptions": []'
                    "},"
                    '"readiness": {'
                    '"implementation": "not_ready",'
                    '"test_cases": "not_ready",'
                    '"acceptance_criteria": "not_ready"'
                    "},"
                    '"recommended_actions": [],'
                    '"confidence": "HIGH",'
                    '"report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."}'
                ),
                tool_calls=(),
            ),
        ]

        result = requirements_agent.execute(
            requirements_agent_work_order,
        )

        assert isinstance(result, RequirementsAgentResult)

        read_file_tool.list_directory.assert_called_once_with(
            Path("templates"),
        )

        assert client.agent_turn.call_count == 2

    def test_agent_reads_template_selected_by_model(
        self,
        requirements_agent,
        client,
        provider_transformer,
        requirements_agent_work_order,
        read_file_tool,
    ):
        provider_transformer.transform.return_value = "transformed request"

        read_file_tool.list_directory.return_value = (
            Path("templates/requirements_evaluation_report_template.md"),
            Path("templates/code_review_report_template.md"),
        )

        read_file_tool.read_file.return_value = (
            "# Requirements Evaluation Report\n\n"
            "## Evaluation Information\n"
            "{{ evaluation_information }}\n\n"
            "## Assessment\n"
            "{{ assessment }}\n"
        )

        client.agent_turn.side_effect = [
            AgentResponse(
                content="",
                tool_calls=(
                    ToolCall(
                        name="list_directory",
                        arguments={
                            "path": "templates",
                        },
                    ),
                ),
            ),
            AgentResponse(
                content="",
                tool_calls=(
                    ToolCall(
                        name="read_file",
                        arguments={
                            "path": (
                                "templates/requirements_evaluation_report_template.md"
                            ),
                        },
                    ),
                ),
            ),
            AgentResponse(
                content=(
                    '{"role": "business_analyst",'
                    '"capability": "evaluate",'
                    '"status": "needs_clarification",'
                    '"summary": "Requirement requires additional clarification.",'
                    '"findings": {'
                    '"strengths": [],'
                    '"gaps": [],'
                    '"ambiguities": [],'
                    '"assumptions": []'
                    "},"
                    '"readiness": {'
                    '"implementation": "not_ready",'
                    '"test_cases": "not_ready",'
                    '"acceptance_criteria": "not_ready"'
                    "},"
                    '"recommended_actions": [],'
                    '"confidence": "HIGH",'
                    '"report": "# Requirements Evaluation Report\\n\\n## Assessment\\n\\nRequirement needs clarification."}'
                ),
                tool_calls=(),
            ),
        ]

        result = requirements_agent.execute(
            requirements_agent_work_order,
        )

        assert isinstance(result, RequirementsAgentResult)

        read_file_tool.list_directory.assert_called_once_with(
            Path("templates"),
        )

        read_file_tool.read_file.assert_called_once_with(
            Path(
                "templates/requirements_evaluation_report_template.md",
            ),
        )

        assert client.agent_turn.call_count == 3
