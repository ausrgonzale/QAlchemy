"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_requirements_eval_service.py

Purpose:
    Unit tests for the QAlchemy Requirements Evaluation feature service.

Description:
    Validates the RequirementsEvalService application boundary, including
    WorkOrder transformation, RequirementsAgent invocation, result
    propagation, and feature-level logging.

    These tests verify that the service correctly coordinates the
    Requirements Evaluation workflow without duplicating the reasoning or
    reporting responsibilities of the RequirementsAgent.

Coverage:
    - Service initialization
    - WorkOrder transformation
    - RequirementsAgent invocation
    - RequirementsAgent report propagation
    - Successful execution logging

Non-Responsibilities:
    - RequirementsAgent reasoning
    - AI provider execution
    - RequirementsAgent response parsing
    - RequirementsAgent contract validation
    - Report generation
    - Report persistence

===============================================================================
"""

from unittest.mock import Mock

import pytest

from agents.contracts.res_agent_results import (
    RequirementsAgentResult,
    RequirementsCapability,
    RequirementsFindings,
    RequirementsReadiness,
    RequirementsReadinessAssessment,
    RequirementsStatus,
)
from agents.requirements_agent import RequirementsAgent
from scripts.core.work_order import WorkOrder
from scripts.core.work_order_transformer import WorkOrderTransformer
from services.app.app_execution_service import AppExecutionService
from services.feature.requirements_eval_service import (
    RequirementsEvalService,
)

pytestmark = [
    pytest.mark.feature,
    pytest.mark.requirements,
]


@pytest.fixture
def execution_service():
    service = Mock(spec=AppExecutionService)
    service.logger_service = Mock()
    service.exception_handling_service = Mock()
    return service


@pytest.fixture
def work_order_transformer():
    return Mock(spec=WorkOrderTransformer)


@pytest.fixture
def requirements_agent():
    return Mock(spec=RequirementsAgent)


@pytest.fixture
def requirements_eval_service(
    execution_service,
    work_order_transformer,
    requirements_agent,
):
    return RequirementsEvalService(
        execution_service=execution_service,
        work_order_transformer=work_order_transformer,
        requirements_agent=requirements_agent,
    )


@pytest.fixture
def work_order():
    return WorkOrder(
        task="Evaluate the supplied requirement.",
        role="Business Analyst",
        target="evaluate_requirement",
        deliverable="Requirements evaluation report.",
        references="",
    )


@pytest.fixture
def transformed_work_order():
    return "transformed work order"


@pytest.fixture
def requirements_agent_result():
    return RequirementsAgentResult(
        role="business_analyst",
        capability=RequirementsCapability.EVALUATE,
        status=RequirementsStatus.NEEDS_CLARIFICATION,
        summary="Requirement requires clarification.",
        findings=RequirementsFindings(
            gaps=("Acceptance criteria are missing.",),
        ),
        readiness=RequirementsReadinessAssessment(
            implementation=RequirementsReadiness.NOT_READY,
            test_cases=RequirementsReadiness.NOT_READY,
            acceptance_criteria=RequirementsReadiness.NOT_READY,
        ),
        recommended_actions=("Clarify the acceptance criteria.",),
        confidence="HIGH",
        report="# Requirements Evaluation Report\n\nRequirement requires clarification.",
    )


@pytest.mark.feature
@pytest.mark.requirements
class TestRequirementsEvalService:

    def test_initializes_with_dependencies(
        self,
        execution_service,
        work_order_transformer,
        requirements_agent,
    ):
        service = RequirementsEvalService(
            execution_service=execution_service,
            work_order_transformer=work_order_transformer,
            requirements_agent=requirements_agent,
        )

        assert service._execution_service is execution_service
        assert service._work_order_transformer is work_order_transformer
        assert service._requirements_agent is requirements_agent
        assert service._logger is execution_service.logger_service
        assert (
            service._exception_handler is execution_service.exception_handling_service
        )

    def test_transforms_work_order(
        self,
        requirements_eval_service,
        work_order_transformer,
        requirements_agent,
        work_order,
        transformed_work_order,
        requirements_agent_result,
    ):
        work_order_transformer.work_order_execution.return_value = (
            transformed_work_order
        )
        requirements_agent.execute.return_value = requirements_agent_result

        requirements_eval_service.execute(
            work_order,
            Mock(),
            [],
            "evaluate",
        )

        work_order_transformer.work_order_execution.assert_called_once()

    def test_passes_transformed_work_order_to_agent(
        self,
        requirements_eval_service,
        work_order_transformer,
        requirements_agent,
        work_order,
        transformed_work_order,
        requirements_agent_result,
    ):
        work_order_transformer.work_order_execution.return_value = (
            transformed_work_order
        )
        requirements_agent.execute.return_value = requirements_agent_result

        requirements_eval_service.execute(
            work_order,
            Mock(),
            [],
            "evaluate",
        )

        requirements_agent.execute.assert_called_once_with(
            transformed_work_order,
        )

    def test_returns_agent_report(
        self,
        requirements_eval_service,
        work_order_transformer,
        requirements_agent,
        work_order,
        transformed_work_order,
        requirements_agent_result,
    ):
        work_order_transformer.work_order_execution.return_value = (
            transformed_work_order
        )
        requirements_agent.execute.return_value = requirements_agent_result

        result = requirements_eval_service.execute(
            work_order,
            Mock(),
            [],
            "evaluate",
        )

        assert result == requirements_agent_result

    def test_logs_service_entry(
        self,
        requirements_eval_service,
        execution_service,
        work_order_transformer,
        requirements_agent,
        work_order,
        transformed_work_order,
        requirements_agent_result,
    ):
        work_order_transformer.work_order_execution.return_value = (
            transformed_work_order
        )
        requirements_agent.execute.return_value = requirements_agent_result

        requirements_eval_service.execute(
            work_order,
            Mock(),
            [],
            "evaluate",
        )

        execution_service.logger_service.log.assert_any_call(
            level="INFO",
            message="Entering RequirementsEvalService.execute().",
            operation="execute",
        )

    def test_logs_agent_response(
        self,
        requirements_eval_service,
        execution_service,
        work_order_transformer,
        requirements_agent,
        work_order,
        transformed_work_order,
        requirements_agent_result,
    ):
        work_order_transformer.work_order_execution.return_value = (
            transformed_work_order
        )
        requirements_agent.execute.return_value = requirements_agent_result

        requirements_eval_service.execute(
            work_order,
            Mock(),
            [],
            "evaluate",
        )

        execution_service.logger_service.log.assert_any_call(
            level="INFO",
            message="Requirements Agent response received.",
            operation="execute",
        )
