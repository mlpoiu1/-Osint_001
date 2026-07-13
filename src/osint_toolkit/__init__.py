"""OSINT Toolkit - Professional OSINT Collection Management for Kali Linux"""
from __future__ import annotations

__version__ = "0.1.0"
__author__ = "OSINT Toolkit Team"
__license__ = "MIT"

from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.plugin import ToolInfo, PluginResult, PluginArgument, OutputFormat
from osint_toolkit.domain.exceptions import (
    OSINTToolkitError,
    PluginError,
    StorageError,
    ConfigurationError,
)

__all__ = [
    "ToolCategory",
    "ToolType",
    "ToolStatus",
    "ToolInfo",
    "PluginResult",
    "PluginArgument",
    "OutputFormat",
    "OSINTToolkitError",
    "PluginError",
    "StorageError",
    "ConfigurationError",
]