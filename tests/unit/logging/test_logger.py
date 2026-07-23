"""
Unit tests for Logger.
"""

from scripts.core.logger import Logger
from scripts.core.logger_config import LoggerConfig
from scripts.core.path_utils import relative_path

KEEP_TEST_ARTIFACTS = True


def test_logger_appends_message(logging_configuration):
    """Verify the logger writes to the configured application log."""

    log_file = logging_configuration.log_file

    print(f"Log file: {relative_path(log_file)}")

    # Clean start
    if log_file.exists():
        log_file.unlink()

    logger = Logger(LoggerConfig(logging_configuration))

    logger.append("Hello QAlchemy")
    print(f"Created: {relative_path(log_file)}")

    # Verify directory
    assert log_file.parent.exists()

    # Verify file
    assert log_file.exists()

    # Verify contents
    assert log_file.read_text(encoding="utf-8") == "Hello QAlchemy\n"

    # Optional cleanup
    if not KEEP_TEST_ARTIFACTS:
        log_file.unlink()
