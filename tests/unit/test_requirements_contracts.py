"""
Requirements Agent Contract Tests
----------------------------------

Validates the typed contract used by the RequirementsAgent.

These tests verify the supported capability values, status values,
readiness values, and the construction and immutability of the
RequirementsAgent result models.
"""

import pytest

from agents.contracts.res_agent_results import (
    RequirementsAgentResult,
    RequirementsCapability,
    RequirementsFindings,
    RequirementsReadiness,
    RequirementsReadinessAssessment,
    RequirementsStatus,
)


@pytest.mark.agent
@pytest.mark.requirements
class TestRequirementsCapability:
    """Tests for RequirementsAgent capability definitions."""

    def test_capabilities_are_defined(self):
        assert RequirementsCapability.EVALUATE.value == "evaluate"
        assert RequirementsCapability.GENERATE.value == "generate"
        assert RequirementsCapability.REFINE.value == "refine"
        assert (
            RequirementsCapability.CREATE_ACCEPTANCE_CRITERIA.value
            == "create_acceptance_criteria"
        )
        assert RequirementsCapability.CREATE_TEST_CASES.value == "create_test_cases"


@pytest.mark.agent
@pytest.mark.requirements
class TestRequirementsStatus:
    """Tests for RequirementsAgent status definitions."""

    def test_statuses_are_defined(self):
        assert RequirementsStatus.READY.value == "ready"
        assert RequirementsStatus.NEEDS_REFINEMENT.value == "needs_refinement"
        assert RequirementsStatus.NEEDS_CLARIFICATION.value == "needs_clarification"
        assert RequirementsStatus.INVALID.value == "invalid"


@pytest.mark.agent
@pytest.mark.requirements
class TestRequirementsReadiness:
    """Tests for requirement readiness definitions."""

    def test_readiness_values_are_defined(self):
        assert RequirementsReadiness.READY.value == "ready"
        assert RequirementsReadiness.NOT_READY.value == "not_ready"
        assert RequirementsReadiness.UNKNOWN.value == "unknown"


@pytest.mark.agent
@pytest.mark.requirements
class TestRequirementsFindings:
    """Tests for RequirementsFindings."""

    def test_defaults_are_empty(self):
        findings = RequirementsFindings()

        assert findings.strengths == ()
        assert findings.gaps == ()
        assert findings.ambiguities == ()
        assert findings.assumptions == ()

    def test_findings_can_be_populated(self):
        findings = RequirementsFindings(
            strengths=("Clear business objective",),
            gaps=("Missing error behavior",),
            ambiguities=("User role is unclear",),
            assumptions=("User is authenticated",),
        )

        assert findings.strengths == ("Clear business objective",)
        assert findings.gaps == ("Missing error behavior",)
        assert findings.ambiguities == ("User role is unclear",)
        assert findings.assumptions == ("User is authenticated",)


@pytest.mark.agent
@pytest.mark.requirements
class TestRequirementsReadinessAssessment:
    """Tests for RequirementsReadinessAssessment."""

    def test_readiness_can_be_constructed(self):
        readiness = RequirementsReadinessAssessment(
            implementation=RequirementsReadiness.READY,
            test_cases=RequirementsReadiness.NOT_READY,
            acceptance_criteria=RequirementsReadiness.READY,
        )

        assert readiness.implementation == RequirementsReadiness.READY
        assert readiness.test_cases == RequirementsReadiness.NOT_READY
        assert readiness.acceptance_criteria == RequirementsReadiness.READY


@pytest.mark.agent
@pytest.mark.requirements
class TestRequirementsAgentResult:
    """Tests for the RequirementsAgent result contract."""

    def test_result_can_be_constructed(self):
        findings = RequirementsFindings(
            strengths=("Clear objective",),
            gaps=("Missing validation rules",),
        )

        readiness = RequirementsReadinessAssessment(
            implementation=RequirementsReadiness.NOT_READY,
            test_cases=RequirementsReadiness.READY,
            acceptance_criteria=RequirementsReadiness.READY,
        )

        result = RequirementsAgentResult(
            capability=RequirementsCapability.EVALUATE,
            status=RequirementsStatus.NEEDS_REFINEMENT,
            role="business_analyst",
            summary="The requirement needs additional detail.",
            findings=findings,
            readiness=readiness,
            recommended_actions=("Clarify validation rules",),
            confidence="HIGH",
        )

        assert result.capability == RequirementsCapability.EVALUATE
        assert result.status == RequirementsStatus.NEEDS_REFINEMENT
        assert result.summary == "The requirement needs additional detail."
        assert result.findings == findings
        assert result.readiness == readiness
        assert result.recommended_actions == ("Clarify validation rules",)
        assert result.confidence == "HIGH"

    def test_optional_fields_have_expected_defaults(self):
        result = RequirementsAgentResult(
            capability=RequirementsCapability.EVALUATE,
            status=RequirementsStatus.READY,
            role="business_analyst",
            summary="Requirement is ready.",
            findings=RequirementsFindings(),
            readiness=RequirementsReadinessAssessment(
                implementation=RequirementsReadiness.READY,
                test_cases=RequirementsReadiness.READY,
                acceptance_criteria=RequirementsReadiness.READY,
            ),
        )

        assert result.recommended_actions == ()
        assert result.confidence == "UNKNOWN"
