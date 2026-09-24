"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    agent_response.py

Purpose:
    Defines the provider-neutral response returned by an LLM during an Agent workflow.

Description:
    The AgentResponse schema represents the result of a single LLM turn.
    A response may contain normal response content, tool calls, or both.

    The schema isolates the Agent layer from provider-specific response
    structures.

Responsibilities:
    - Represent LLM response content.
    - Represent tool calls requested by the LLM.
    - Provide a provider-neutral Agent response structure.

Non-Responsibilities:
    - Communicating with an LLM provider.
    - Executing tools.
    - Selecting tools.
    - Managing the Agent execution loop.

Version 1.3
-----------
- Introduces the provider-neutral AgentResponse schema.

===============================================================================
"""

from dataclasses import dataclass

from agents.tools.tool_call import ToolCall


@dataclass(frozen=True)
class AgentResponse:
    """
    Represents a provider-neutral LLM response during an Agent workflow.
    """

    content: str
    tool_calls: tuple[ToolCall, ...] = ()
