"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    tool_definition.py

Purpose:
    Defines the provider-neutral schema used to describe tools available to
    an LLM during an Agent workflow.

Description:
    The ToolDefinition schema represents the information an Agent provides
    to an LLM so that the LLM can determine which tool to invoke and what
    arguments the tool accepts.

    The schema remains independent of any specific LLM provider or SDK.
    Provider-specific formatting is the responsibility of the Client.

Responsibilities:
    - Define an Agent tool's name.
    - Define an Agent tool's description.
    - Define the tool's argument schema.
    - Provide a provider-neutral representation for Client translation.

Non-Responsibilities:
    - Executing tools.
    - Selecting tools.
    - Interpreting tool calls.
    - Communicating directly with an LLM provider.

Version 1.3
-----------
- Introduces the provider-neutral ToolDefinition schema for Agent workflows.

===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDefinition:
    """
    Represents a tool made available to an LLM.
    """

    name: str
    description: str
    parameters: dict[str, object]
