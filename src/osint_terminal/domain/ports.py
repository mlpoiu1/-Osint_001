"""Ports (interfaces) that outer layers must implement.

This is the seam Clean Architecture is built on: the domain defines these
Protocols, infrastructure/ and plugins/ provide concrete implementations,
and the DI container (application/container.py, added in a later module)
wires concrete classes to these abstractions at startup. Nothing in
domain/ or application/ ever imports a concrete infrastructure class
directly — only these Protocols.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from osint_terminal.domain.entities import (
    Argument,
    ExecutionResult,
    PluginId,
    PluginMetadata,
    PluginState,
)
from osint_terminal.domain.enums import Category, OutputFormat


@runtime_checkable
class Plugin(Protocol):
    """Contract every one of the 500+ tool plugins must satisfy.

    Concrete plugins live under plugins/<category>/<tool>.py and are
    produced by the plugin generator (a later module) from the
    structured OSINT catalogue extracted from osint_tools.md.
    """

    metadata: PluginMetadata

    def build_command(self, **kwargs: Any) -> list[str] | str:
        """Build the CLI argv (CLI tools) or the target URL/query
        (online/API tools) for the given arguments."""
        ...

    def parse_output(self, raw_output: str) -> dict[str, Any] | list[Any] | str:
        """Turn raw stdout / HTTP response text into structured data."""
        ...


class PluginRepository(Protocol):
    """Persistence port for plugin metadata, state, and run history (SQLite)."""

    def save_metadata(self, metadata: PluginMetadata) -> None: ...
    def get_metadata(self, plugin_id: PluginId) -> PluginMetadata | None: ...
    def list_metadata(self, category: Category | None = None) -> list[PluginMetadata]: ...

    def save_state(self, state: PluginState) -> None: ...
    def get_state(self, plugin_id: PluginId) -> PluginState | None: ...
    def list_states(self) -> list[PluginState]: ...

    def save_execution(self, result: ExecutionResult) -> None: ...
    def list_executions(self, plugin_id: PluginId | None = None, limit: int = 100) -> list[ExecutionResult]: ...


class ToolAvailabilityChecker(Protocol):
    """Detects whether a CLI binary is installed and runnable on this host."""

    def is_available(self, binary_name: str) -> bool: ...
    def resolve_path(self, binary_name: str) -> str | None: ...
    def get_version(self, binary_name: str) -> str | None: ...


class PluginDiscovery(Protocol):
    """Finds and loads all plugin modules (scales to 500+ without an
    ever-growing manual import list)."""

    def discover(self) -> list[Plugin]: ...


class OutputParser(Protocol):
    """Named parsing strategy referenced by PluginMetadata.output_parser,
    shared across many plugins that emit similar raw formats (e.g. JSON
    APIs, whois text blocks, line-delimited scanner output)."""

    name: str

    def parse(self, raw_output: str) -> dict[str, Any] | list[Any] | str: ...


class SearchIndex(Protocol):
    """Fuzzy-search / command-palette lookup over the plugin catalogue."""

    def index(self, plugins: list[PluginMetadata]) -> None: ...
    def search(self, query: str, limit: int = 20) -> list[PluginMetadata]: ...


class ReportExporter(Protocol):
    """Renders execution results / plugin catalogue to a target format."""

    format: OutputFormat

    def export(self, data: Any, destination: str) -> str:
        """Writes the report and returns the final file path."""
        ...


class ArgumentValidator(Protocol):
    """Validates user-supplied kwargs against a plugin's declared Arguments
    before build_command() is called."""

    def validate(self, arguments: tuple[Argument, ...], values: dict[str, Any]) -> dict[str, Any]: ...
