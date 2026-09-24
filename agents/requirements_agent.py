"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    requirements_agent.py

Purpose:
    Provides the QAlchemy Requirements Agent.

Description:
    RequirementsAgent analyzes a requirement-related task and uses a
    configured model to determine the appropriate requirements capability
    and produce a structured requirements assessment.

    The RequirementsAgent owns requirements reasoning and decision-making
    but does not execute tools or manage workflow orchestration.

Responsibilities:
    - Provide the Agent with the requirements evaluation context and resources.
    - Build the requirements request from the supplied task and requirement.
    - Submit the request through the configured provider client.
    - Interpret the model response as a RequirementsAgentResult.

Non-Responsibilities:
    - Execute requirements tools.
    - Access external requirement systems directly.
    - Manage workflow state.
    - Orchestrate workflows.
    - Select providers or models.
    - Create clients.
    - Persist files.

Workflow:
    Requirements Task + Requirement
        ↓
    Business Analyst Role + Request
        ↓
    ProviderTransformer
        ↓
    Client
        ↓
    Configured Provider / Model
        ↓
    Requirements Decision / Assessment

Dependencies:
    - ReadFileTool
    - ProviderTransformer
    - Client
    - RequirementsAgentResult

===============================================================================
"""

import json
from pathlib import Path

from agents.contracts.res_agent_results import (
    RequirementsAgentResult,
    RequirementsCapability,
    RequirementsFindings,
    RequirementsReadiness,
    RequirementsReadinessAssessment,
    RequirementsStatus,
)
from agents.protocols.res_agent_protocol import (
    REQUIREMENTS_AGENT_RESPONSE,
)
from agents.tools.read_file_tool import ReadFileTool
from agents.tools.tool_call import ToolCall
from agents.tools.tool_definition import ToolDefinition
from clients.client import Client
from scripts.core.provider_transformer import ProviderTransformer
from scripts.utils.path_utils import agent_resource_root

AGENT_INSTRUCTIONS = """
You are a Requirements Evaluation Agent.

Your task is to evaluate the supplied requirement, not to implement or
execute the work described by the requirement.

Agent resources are organized under:
- agents/roles/
- agents/standards/
- agents/protocols/
- agents/tools/
- agents/templates/

User-provided input files are project-level resources and are separate from Agent resources. User input paths must be treated as project-relative paths and must not be prefixed with "agents/".

Use the assigned role and applicable standards to determine whether the
requirement is sufficiently clear, complete, testable, and actionable for
Development, QE, and business validation.

The assigned role is an Agent role resource located under agents/roles/.
The role value returned in the response must be the role resource name
without the path or file extension, such as "business_analyst".
Do not use a capability name as the role.

The capability selected by the route identifies the requirements action
being performed. Confirm the capability and return it separately using the
values defined by the response protocol.

Treat the requirement and its acceptance criteria as the subject of the
evaluation.

Identify ambiguity, missing information, conflicting information,
unsupported assumptions, dependencies, blockers, and other gaps that could
prevent the requirement from being ready.

Use available resources and tools to gather supporting evidence when needed.

Do not invent missing requirements or silently resolve ambiguity.

Complete the evaluation according to the assigned task and return the
required result using the response protocol.
"""


class RequirementsAgent:
    """
    Reasons about software requirements and confirms the appropriate
    requirements capability.
    """

    def __init__(
        self,
        client: Client,
        provider_transformer: ProviderTransformer,
        read_file_tool: ReadFileTool,
    ) -> None:
        """Initialize the Requirements Agent."""

        self._client = client
        self._provider_transformer = provider_transformer
        self._read_file_tool = read_file_tool

    def execute(self, work_order: str) -> RequirementsAgentResult:
        """
        Execute the requirements evaluation and confirm the capability.

        The LLM determines when a tool is required. The Agent executes the
        requested tool and returns the tool result to the LLM until the LLM
        produces a final response.
        """

        resource_root = agent_resource_root()
        available_roles = self._available_roles()

        request = (
            f"AGENT INSTRUCTIONS\n{AGENT_INSTRUCTIONS}\n\n"
            f"AGENT RESOURCE ROOT\n{resource_root}\n\n"
            f"AVAILABLE ROLE RESOURCES\n{', '.join(available_roles)}\n\n"
            f"RESPONSE PROTOCOL\n{REQUIREMENTS_AGENT_RESPONSE}\n\n"
            f"WORK ORDER\n{work_order}"
        )

        transformed_request = self._provider_transformer.transform(
            request,
        )

        messages: list[dict[str, object]] = [
            {
                "role": "user",
                "content": transformed_request,
            },
        ]

        tools = (
            ToolDefinition(
                name="list_directory",
                description="List the files directly within a directory.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the directory to list.",
                        },
                    },
                    "required": ["path"],
                },
            ),
            ToolDefinition(
                name="read_file",
                description="Read the contents of a file.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read.",
                        },
                    },
                    "required": ["path"],
                },
            ),
        )

        while True:
            response = self._client.agent_turn(
                messages,
                tools,
            )

            if not response.tool_calls:
                print("\n" + "=" * 79)
                print("REQUIREMENTS AGENT FINAL RESPONSE")
                print("=" * 79)
                print(response.content)
                print("=" * 79)
                return self._create_result(response.content)

            messages.append(
                {
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": response.tool_calls,
                },
            )

            for tool_call in response.tool_calls:
                tool_result = self._execute_tool(tool_call)

                messages.append(
                    {
                        "role": "tool",
                        "content": tool_result,
                    },
                )

    def _execute_tool(self, tool_call: ToolCall) -> str:
        """
        Execute a tool requested by the LLM.
        """
        if tool_call.name == "read_file":
            path = Path(str(tool_call.arguments["path"]))

            try:
                return self._read_file_tool.read_file(path)
            except FileNotFoundError:
                return f"Tool error: file not found: {path}"

        if tool_call.name == "list_directory":
            path = Path(str(tool_call.arguments["path"]))
            entries = self._read_file_tool.list_directory(path)

            return "\n".join(str(entry) for entry in entries)

        raise ValueError(
            f"Unsupported Requirements Agent tool: {tool_call.name}",
        )

    def _available_roles(self) -> tuple[str, ...]:
        roles_root = agent_resource_root() / "roles"

        return tuple(
            sorted(path.stem for path in roles_root.glob("*.md") if path.is_file())
        )

    def _create_result(self, response: str) -> RequirementsAgentResult:
        data = json.loads(response)

        self._validate_response(data)
        role = data["role"]
        if role not in self._available_roles():
            role = "unknown"

        return RequirementsAgentResult(
            role=role,
            capability=RequirementsCapability(data["capability"]),
            status=RequirementsStatus(data["status"]),
            summary=data["summary"],
            findings=RequirementsFindings(
                strengths=tuple(data["findings"]["strengths"]),
                gaps=tuple(data["findings"]["gaps"]),
                ambiguities=tuple(data["findings"]["ambiguities"]),
                assumptions=tuple(data["findings"]["assumptions"]),
            ),
            readiness=RequirementsReadinessAssessment(
                implementation=RequirementsReadiness(
                    data["readiness"]["implementation"]
                ),
                test_cases=RequirementsReadiness(data["readiness"]["test_cases"]),
                acceptance_criteria=RequirementsReadiness(
                    data["readiness"]["acceptance_criteria"]
                ),
            ),
            recommended_actions=tuple(data["recommended_actions"]),
            confidence=data["confidence"],
            report=data["report"],
        )

    def _validate_response(self, data: dict) -> None:
        if not isinstance(data["summary"], str):
            raise TypeError("Requirements Agent response 'summary' must be a string.")
        if not isinstance(data["report"], str):
            raise TypeError("Requirements Agent response 'report' must be a string.")

    def _extract_source_code_path(self, work_order: str) -> Path:
        lines = work_order.splitlines()

        for index, line in enumerate(lines):
            if line.strip() != "SOURCE CODE":
                continue

            for candidate in lines[index + 1 :]:
                candidate = candidate.strip()

                if not candidate:
                    continue

                if candidate.startswith("**"):
                    continue

                if set(candidate) == {"-"}:
                    continue

                if candidate.startswith("DELIVERABLE"):
                    break

                return Path(candidate)

        raise ValueError("Work Order does not contain a source code path.")
