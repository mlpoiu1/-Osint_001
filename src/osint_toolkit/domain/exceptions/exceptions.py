from __future__ import annotations

class OSINTToolkitError(Exception):
    pass


class PluginError(OSINTToolkitError):
    pass


class PluginNotFoundError(PluginError):
    pass


class PluginNotAvailableError(PluginError):
    pass


class PluginValidationError(PluginError):
    pass


class PluginExecutionError(PluginError):
    pass


class StorageError(OSINTToolkitError):
    pass


class ToolNotFoundError(StorageError):
    pass


class ToolAlreadyExistsError(StorageError):
    pass


class ConfigurationError(OSINTToolkitError):
    pass


class CLIError(OSINTToolkitError):
    pass


class ReportGenerationError(OSINTToolkitError):
    pass


class SearchError(OSINTToolkitError):
    pass