"""
Tool protocol used by Agents and the application.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDefinition:
    """Defines a tool exposed to an Agent."""

    name: str
    description: str
    parameters: dict


@dataclass(frozen=True)
class ToolCall:
    """Represents a tool invocation requested by an Agent."""

    name: str
    arguments: dict
