"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    requirements_eval_service.py

Purpose:
    Provides the Requirements Evaluation feature for the QAlchemy application.

Description:
    The RequirementsEvalService consumes a canonical WorkOrder and executes
    the Requirements Evaluation workflow.

    The service delegates requirements analysis to the RequirementsAgent,
    receives the structured RequirementsAgentResult, and returns that result
    to the calling application service.

Version 1.3
-----------
- Receives the WorkOrder from the OrchestrationService.
- Delegates requirements analysis to the RequirementsAgent.
- Receives the structured RequirementsAgentResult.
- Returns the Agent result to the caller.

Future versions will:
- Process the RequirementsAgentResult into a requirements evaluation report.
- Render the report using the configured report template.
- Persist the report through the reporting infrastructure.
- Add feature-specific exception handling as required.

===============================================================================
"""

from pathlib import Path

from agents.contracts.res_agent_results import RequirementsAgentResult
from agents.requirements_agent import RequirementsAgent
from scripts.core.work_order import WorkOrder
from scripts.core.work_order_transformer import WorkOrderTransformer
from scripts.utils.work_space import WorkSpace
from services.app.app_execution_service import AppExecutionService


class RequirementsEvalService:
    """
    Requirements Evaluation feature service.
    """

    def __init__(
        self,
        execution_service: AppExecutionService,
        work_order_transformer: WorkOrderTransformer,
        requirements_agent: RequirementsAgent,
    ) -> None:
        """
        Initialize the Requirements Evaluation service.
        """

        self._execution_service = execution_service
        self._requirements_agent = requirements_agent
        self._logger = execution_service.logger_service
        self._exception_handler = execution_service.exception_handling_service
        self._work_order_transformer = work_order_transformer

    def execute(
        self,
        work_order: WorkOrder,
        workspace: WorkSpace,
        source_code: list[Path],
        capability: str,
    ) -> RequirementsAgentResult:
        """
        Execute the Requirements Evaluation feature.
        """

        self._logger.log(
            level="INFO",
            message="Entering RequirementsEvalService.execute().",
            operation="execute",
        )

        request = self._work_order_transformer.work_order_execution(
            work_order,
            source_code="\n".join(str(path) for path in source_code),
            capability=capability,
        )

        result = self._requirements_agent.execute(
            request,
        )

        self._logger.log(
            level="INFO",
            message="Requirements Agent response received.",
            operation="execute",
        )

        return result

    def _build_report_content(
        self,
        result: RequirementsAgentResult,
    ) -> str:
        """
        Convert the Requirements Agent result into report content.
        """

        findings = result.findings
        readiness = result.readiness

        sections = [
            f"## Capability\n\n{result.capability.value}",
            f"## Status\n\n{result.status.value}",
            f"## Summary\n\n{result.summary}",
            (
                "## Findings\n\n"
                "### Strengths\n\n"
                + "\n".join(f"- {item}" for item in findings.strengths)
                + "\n\n"
                "### Gaps\n\n"
                + "\n".join(f"- {item}" for item in findings.gaps)
                + "\n\n"
                "### Ambiguities\n\n"
                + "\n".join(f"- {item}" for item in findings.ambiguities)
                + "\n\n"
                "### Assumptions\n\n"
                + "\n".join(f"- {item}" for item in findings.assumptions)
            ),
            (
                "## Readiness\n\n"
                f"- Implementation: "
                f"{readiness.implementation.value}\n"
                f"- Test Cases: "
                f"{readiness.test_cases.value}\n"
                f"- Acceptance Criteria: "
                f"{readiness.acceptance_criteria.value}"
            ),
            (
                "## Recommended Actions\n\n"
                + "\n".join(f"- {action}" for action in result.recommended_actions)
            ),
            f"## Confidence\n\n{result.confidence}",
        ]

        return "\n\n".join(sections)
