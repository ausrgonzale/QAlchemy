"""
Logger

Purpose
-------
Provides low-level file persistence for the QAlchemy logging subsystem.

The Logger is responsible only for creating the configured logging directory,
creating the log file when necessary, and appending text to the configured log
file. It intentionally contains no business logic, formatting, timestamps,
log-level processing, or exception handling.

Architecture
------------
The Logger is a low-level infrastructure component responsible solely for file
I/O. Higher-level services determine what should be logged and delegate file
persistence to the Logger.

Application Services
        │
        ▼
     (Future)
   LoggerService
        │
        ▼
      Logger
        │
        ▼
    File System

For complete application architecture and component relationships, see:

    docs/architecture.md

Responsibilities
----------------
- Create the configured logging directory.
- Create the configured log file when necessary.
- Append messages to the configured log file.
- Allow file system exceptions to propagate to the caller.

Dependencies
------------
- LoggingConfiguration
- pathlib.Path

Used By
-------
- Future LoggerService
- Infrastructure components requiring direct log persistence

Does Not
---------
The Logger intentionally does NOT perform any of the following:

- Determine whether a message should be logged.
- Assign or filter log levels.
- Add timestamps.
- Format log entries.
- Capture or process exceptions.
- Rotate or archive log files.
- Make application-level logging decisions.

Future Enhancements
-------------------
- Support alternate storage providers.
- Support dependency injection for testing.
- Integrate with LoggerService for application-level logging.
"""

from pathlib import Path

from scripts.core.logger_config import LoggerConfig


class Logger:
    """Writes log messages to the configured log file."""

    def __init__(self, configuration: LoggerConfig) -> None:
        """Initializes the logger."""

        self._log_file: Path = configuration.log_file

        self._log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def append(self, message: str) -> None:
        """Appends a message to the configured log file."""

        with self._log_file.open(
            mode="a",
            encoding="utf-8",
        ) as log_file:
            log_file.write(f"{message}\n")
