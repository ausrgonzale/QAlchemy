"""Unit tests for AppConfigurationService."""

from __future__ import annotations

from pathlib import Path

from services.app.app_configuration_service import AppConfigurationService


def test_configuration_properties_are_exposed() -> None:
    """Expose typed accessors for all supported configuration sections."""

    service = AppConfigurationService(
        configuration_file=Path(
            "config/app.yaml",
        ),
    )

    # App
    assert service.app.name == "QAlchemy"
    assert service.app.version == "1.2.0"
    assert service.app.edition == "Community"

    # Client
    assert service.client.provider == "ollama"
    assert service.client.default_model == "gpt-oss:120b-cloud"
    assert service.client.request_timeout == 120
    assert service.client.stream is False

    # Work Order
    assert service.work_order.validation.enabled is True
    assert service.work_order.validation.fail_on_missing_required_field is True
    assert service.work_order.validation.fail_on_invalid_definition is True

    assert service.work_order.runtime.allow_multiple_units_of_work is False
    assert service.work_order.runtime.stop_on_validation_failure is True
    assert service.work_order.runtime.persist_to_disk is True
    assert service.work_order.runtime.directory == "work_orders"

    # WorkSpace
    assert service.workspace.root == "work_space"

    # Templates
    assert service.templates.root == "templates"
    assert service.templates.code_review_report == "code_review_report_template.md"

    # Reports
    assert service.reports.output_root == "reports"
    assert service.reports.debug_output_root == "reports/debug"

    assert service.reports.review.fields.source_file is True
    assert service.reports.review.fields.lines_reviewed is True
    assert service.reports.review.fields.provider is True
    assert service.reports.review.fields.model is True
    assert service.reports.review.fields.execution_time is True
    assert service.reports.review.fields.review_date is True

    # Logging
    assert service.logging.level == "INFO"
    assert service.logging.output_root == "logs"
    assert service.logging.base_filename == "qalchemy"
    assert service.logging.extension == ".log"
    assert service.logging.log_file.name == "qalchemy.log"

    # Debug
    assert service.logging.debug.enabled is True
    assert service.logging.debug.save_prompt is True
    assert service.logging.debug.save_response is True
    assert service.logging.debug.overwrite_files is True

    # Exceptions
    assert service.exceptions.enabled is True
    assert service.exceptions.catalog.root == Path("config")
    assert service.exceptions.catalog.filename == "exceptions.yaml"
    assert service.exceptions.defaults.unknown_exception_code == "QAL-EX-999"
    assert service.exceptions.defaults.validation_exception_code == "QAL-EX-001"
    assert service.exceptions.defaults.internal_exception_code == "QAL-EX-999"
    assert service.exceptions.logging.log_exceptions is True
    assert service.exceptions.logging.include_stack_trace is True
    assert service.exceptions.user_messages.expose_internal_errors is False


def test_live_configuration_exposes_required_app_metadata() -> None:
    """Load the repository configuration from its production location."""

    service = AppConfigurationService()

    assert service.app.name == "QAlchemy"
    assert service.app.version == "1.2.0"
    assert service.app.edition == "Community"
