"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    tool_call.py

Purpose:
    Defines the provider-neutral schema used to represent tool calls
    requested by an LLM.

Description:
    The ToolCall schema represents a single tool invocation requested by
    an LLM during an Agent workflow.

    The schema provides a provider-independent representation of the
    requested tool name and its arguments. Provider-specific response
    structures are translated into this schema before being consumed by
    the Agent layer.

Responsibilities:
    - Represent an LLM-requested tool invocation.
    - Provide the tool name requested by the LLM.
    - Provide the arguments required by the requested tool.
    - Remain independent of any specific LLM provider or SDK.

Non-Responsibilities:
    - Executing tools.
    - Selecting tools.
    - Defining tool schemas exposed to the LLM.
    - Communicating directly with an LLM provider.

Version 1.3
-----------
- Introduces the provider-neutral ToolCall schema for Agent workflows.

===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolCall:
    """
    Represents a tool invocation requested by an LLM.
    """

    name: str
    arguments: dict[str, object]
