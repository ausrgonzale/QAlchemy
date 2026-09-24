"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_e2e_requirements_agent.py

Purpose:
    Validates the QAlchemy Requirements Agent workflow through the application
    orchestration boundary.

Description:
    This validation test exercises the Requirements Agent using the
    application's real configuration, AI client, orchestration, feature
    service, Agent, Tool, and report generation workflow.

Workflow:
    RuntimeRequest
        ↓
    AppBootstrapService
        ↓
    OrchestrationService
        ↓
    RoutingAgent
        ↓
    RequirementsEvalService
        ↓
    RequirementsAgent
        ↓
    ReadFileTool
        ↓
    Requirement Evaluation
        ↓
    ReportWriter

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.core.runtime_request import RuntimeRequest
from services.app.app_bootstrap_service import AppBootstrapService


@pytest.mark.requirements_agent
def test_requirements_agent_workflow() -> None:
    project_root = Path(__file__).parents[2]

    runtime_request = RuntimeRequest(
        task="Evaluate the supplied requirement for development readiness.",
        role=None,
        target="None",
        deliverable=(
            project_root / "resources" / "inputs" / "jira_googlehomepage_deliverable.md"
        ),
        source_code=[
            project_root / "resources" / "inputs" / "jira_googlehomepage_req.json"
        ],
    )

    bootstrap = AppBootstrapService().bootstrap()

    bootstrap.run(runtime_request)

    workspace_root = Path(bootstrap.configuration.workspace.root)

    report_paths = list(
        workspace_root.glob("*/output/requirements_evaluation_report.md")
    )

    assert report_paths

    report_path = max(
        report_paths,
        key=lambda path: path.stat().st_mtime,
    )

    assert report_path.is_file()
