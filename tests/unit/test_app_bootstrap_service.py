"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_app_bootstrap_service.py

Purpose:
    Unit tests for the QAlchemy application bootstrap service.

Description:
    Verifies that AppBootstrapService correctly initializes the application
    Composition Root and wires its Core Services, Agents, Feature Services,
    and Application Services.

Responsibilities:
    - Verify application configuration is initialized.
    - Verify Core Services are initialized.
    - Verify Agents are initialized.
    - Verify Feature Services are initialized.
    - Verify Application Services are initialized.
    - Verify service dependencies are wired correctly.
    - Verify the bootstrap service exposes initialized services.

Non-Responsibilities:
    - Verify Feature Service execution.
    - Verify Agent behavior.
    - Verify provider/model behavior.
    - Verify end-to-end application workflows.

===============================================================================
"""

from unittest.mock import DEFAULT, MagicMock, patch

from services.app.app_bootstrap_service import AppBootstrapService


class TestAppBootstrapService:
    """Tests for AppBootstrapService."""

    def _create_bootstrap_patches(self):
        """Create the shared Bootstrap dependency patches."""

        return patch.multiple(
            "services.app.app_bootstrap_service",
            configure_bootstrap_logging=DEFAULT,
            AppConfigurationService=DEFAULT,
            ClientService=DEFAULT,
            Logger=DEFAULT,
            LoggerConfig=DEFAULT,
            LoggerService=DEFAULT,
            ExceptionHandlingService=DEFAULT,
            AppExecutionService=DEFAULT,
            WorkOrderTransformer=DEFAULT,
            RequirementsAgent=DEFAULT,
            RouteResolver=DEFAULT,
            GenerateCodeService=DEFAULT,
            ReviewCodeService=DEFAULT,
            RequirementsEvalService=DEFAULT,
            OrchestrationService=DEFAULT,
        )

    def test_bootstrap_returns_self(self):
        """Bootstrap returns the initialized AppBootstrapService instance."""

        with self._create_bootstrap_patches():
            service = AppBootstrapService()

            result = service.bootstrap()

            assert result is service

    def test_bootstrap_initializes_configuration(self):
        """Bootstrap initializes application configuration."""

        with self._create_bootstrap_patches() as mocks:
            configuration_service = mocks["AppConfigurationService"]
            configuration_service.return_value.load.return_value = MagicMock()

            service = AppBootstrapService().bootstrap()

            configuration_service.assert_called_once()
            configuration_service.return_value.load.assert_called_once()
            assert service.configuration is (
                configuration_service.return_value.load.return_value
            )

    def test_bootstrap_initializes_client_service(self):
        """Bootstrap initializes the ClientService."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            service = AppBootstrapService().bootstrap()

            mocks["ClientService"].assert_called_once_with(
                configuration=configuration.client,
            )
            assert service.client_service is (mocks["ClientService"].return_value)

    def test_bootstrap_initializes_logger_service(self):
        """Bootstrap initializes the application LoggerService."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            service = AppBootstrapService().bootstrap()

            assert mocks["Logger"].called
            assert mocks["LoggerConfig"].called
            assert mocks["LoggerService"].called
            assert service.logger_service is (mocks["LoggerService"].return_value)

    def test_bootstrap_initializes_exception_handling_service(self):
        """Bootstrap initializes ExceptionHandlingService."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            service = AppBootstrapService().bootstrap()

            mocks["ExceptionHandlingService"].assert_called_once()
            assert service.exception_handling_service is (
                mocks["ExceptionHandlingService"].return_value
            )

    def test_bootstrap_initializes_execution_service(self):
        """Bootstrap initializes AppExecutionService with its dependencies."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            service = AppBootstrapService().bootstrap()

            mocks["AppExecutionService"].assert_called_once_with(
                configuration=configuration,
                client_service=mocks["ClientService"].return_value,
                logger_service=mocks["LoggerService"].return_value,
                exception_handling_service=(
                    mocks["ExceptionHandlingService"].return_value
                ),
            )

            assert service.execution_service is (
                mocks["AppExecutionService"].return_value
            )

    def test_bootstrap_initializes_feature_services(self):
        """Bootstrap initializes all Feature Services."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            service = AppBootstrapService().bootstrap()

            mocks["GenerateCodeService"].assert_called_once()
            mocks["ReviewCodeService"].assert_called_once()
            mocks["RequirementsEvalService"].assert_called_once()

            assert service.generate_code_service is (
                mocks["GenerateCodeService"].return_value
            )
            assert service.review_code_service is (
                mocks["ReviewCodeService"].return_value
            )

    def test_bootstrap_initializes_requirements_agent(self):
        """Bootstrap initializes the RequirementsAgent."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            AppBootstrapService().bootstrap()

            mocks["RequirementsAgent"].assert_called_once()

            # The Agent is currently an internal Bootstrap dependency.
            # Its initialization is verified here rather than through a
            # public AppBootstrapService property.
            assert mocks["RequirementsAgent"].return_value is not None

    def test_bootstrap_initializes_requirements_eval_service(
        self,
    ):
        """Bootstrap initializes RequirementsEvalService with dependencies."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            service = AppBootstrapService().bootstrap()

            mocks["RequirementsEvalService"].assert_called_once_with(
                execution_service=mocks["AppExecutionService"].return_value,
                work_order_transformer=mocks["WorkOrderTransformer"].return_value,
                requirements_agent=mocks["RequirementsAgent"].return_value,
            )

            # RequirementsEvalService will be exposed by Bootstrap in the
            # production implementation.
            assert service.requirements_eval_service is (
                mocks["RequirementsEvalService"].return_value
            )

    def test_bootstrap_initializes_orchestration_service(self):
        """Bootstrap initializes OrchestrationService with Feature Services."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            service = AppBootstrapService().bootstrap()

            mocks["OrchestrationService"].assert_called_once_with(
                execution_service=mocks["AppExecutionService"].return_value,
                generate_code_service=mocks["GenerateCodeService"].return_value,
                review_code_service=mocks["ReviewCodeService"].return_value,
                requirements_eval_service=mocks["RequirementsEvalService"].return_value,
                logger_service=mocks["LoggerService"].return_value,
                route_resolver=mocks["RouteResolver"].return_value,
            )

            assert service.orchestration_service is (
                mocks["OrchestrationService"].return_value
            )

    def test_bootstrap_initializes_work_order_transformer(self):
        """Bootstrap initializes the WorkOrderTransformer."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            AppBootstrapService().bootstrap()

            mocks["WorkOrderTransformer"].assert_called_once()

    def test_bootstrap_initializes_generate_code_service_with_dependencies(
        self,
    ):
        """Bootstrap wires GenerateCodeService dependencies."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            AppBootstrapService().bootstrap()

            mocks["GenerateCodeService"].assert_called_once_with(
                execution_service=mocks["AppExecutionService"].return_value,
                work_order_transformer=mocks["WorkOrderTransformer"].return_value,
            )

    def test_bootstrap_initializes_review_code_service_with_dependencies(
        self,
    ):
        """Bootstrap wires ReviewCodeService dependencies."""

        with self._create_bootstrap_patches() as mocks:
            configuration = MagicMock()
            mocks["AppConfigurationService"].return_value.load.return_value = (
                configuration
            )

            AppBootstrapService().bootstrap()

            mocks["ReviewCodeService"].assert_called_once_with(
                execution_service=mocks["AppExecutionService"].return_value,
                work_order_transformer=mocks["WorkOrderTransformer"].return_value,
            )
