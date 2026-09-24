"""
Requirements Agent Contract

Defines the typed contract between the RequirementsAgent and the
QAlchemy application.

This module contains data contracts only. It does not implement Agent
reasoning, requirement evaluation, tool execution, or external-system
integration.
"""

from dataclasses import dataclass
from enum import StrEnum


class RequirementsCapability(StrEnum):
    """Capabilities supported by the Requirements Agent."""

    EVALUATE = "evaluate"
    GENERATE = "generate"
    REFINE = "refine"
    CREATE_ACCEPTANCE_CRITERIA = "create_acceptance_criteria"
    CREATE_TEST_CASES = "create_test_cases"


class RequirementsStatus(StrEnum):
    """Possible outcomes of Requirements Agent processing."""

    READY = "ready"
    NEEDS_REFINEMENT = "needs_refinement"
    NEEDS_CLARIFICATION = "needs_clarification"
    INVALID = "invalid"


class RequirementsReadiness(StrEnum):
    """Readiness values used by the Requirements Agent assessment."""

    READY = "ready"
    NOT_READY = "not_ready"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RequirementsFindings:
    """Structured findings produced during requirements analysis."""

    strengths: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    ambiguities: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequirementsReadinessAssessment:
    """Readiness assessment for downstream requirements activities."""

    implementation: RequirementsReadiness
    test_cases: RequirementsReadiness
    acceptance_criteria: RequirementsReadiness


@dataclass(frozen=True)
class RequirementsAgentResult:
    """Typed result returned by the Requirements Agent."""

    role: str
    capability: RequirementsCapability
    status: RequirementsStatus
    summary: str
    findings: RequirementsFindings
    readiness: RequirementsReadinessAssessment
    recommended_actions: tuple[str, ...] = ()
    confidence: str = "UNKNOWN"
    report: str = ""
