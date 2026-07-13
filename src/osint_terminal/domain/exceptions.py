"""Domain-level exceptions. Outer layers catch/wrap these; they never leak
raw exceptions (sqlite3.Error, subprocess errors, etc.) across the boundary."""

from __future__ import annotations


class OsintTerminalError(Exception):
    """Base class for all application-specific errors."""


class PluginNotFoundError(OsintTerminalError):
    def __init__(self, plugin_id: str) -> None:
        super().__init__(f"Plugin not found: {plugin_id}")
        self.plugin_id = plugin_id


class InvalidArgumentError(OsintTerminalError):
    def __init__(self, argument_name: str, reason: str) -> None:
        super().__init__(f"Invalid argument '{argument_name}': {reason}")
        self.argument_name = argument_name


class PluginUnavailableError(OsintTerminalError):
    """Raised when attempting to execute a CLI plugin whose binary isn't installed."""

    def __init__(self, plugin_id: str, binary_name: str) -> None:
        super().__init__(
            f"Plugin '{plugin_id}' is disabled: binary '{binary_name}' not found on PATH"
        )
        self.plugin_id = plugin_id
        self.binary_name = binary_name


class PluginExecutionError(OsintTerminalError):
    def __init__(self, plugin_id: str, reason: str) -> None:
        super().__init__(f"Execution failed for '{plugin_id}': {reason}")
        self.plugin_id = plugin_id


class ParserNotRegisteredError(OsintTerminalError):
    def __init__(self, parser_name: str) -> None:
        super().__init__(f"Output parser not registered: {parser_name}")


class ReportExportError(OsintTerminalError):
    def __init__(self, destination: str, reason: str) -> None:
        super().__init__(f"Failed to export report to '{destination}': {reason}")
