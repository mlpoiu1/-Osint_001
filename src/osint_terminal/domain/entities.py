"""Core domain entities.

Pure data + invariants. No I/O, no SQLite, no Textual, no subprocess calls
here — those belong to infrastructure/. This is what makes the domain layer
testable in isolation and safe to import from every other layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from osint_terminal.domain.enums import Category, OutputFormat, PluginStatus, ToolType


@dataclass(slots=True, frozen=True)
class Argument:
    """A single CLI/query argument a plugin accepts."""

    name: str
    description: str
    required: bool = False
    default: str | None = None
    flag: str | None = None  # e.g. "-d" / "--domain"; None for positional args

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Argument.name must not be empty")


@dataclass(slots=True, frozen=True)
class PluginId:
    """Stable, deterministic identifier for a plugin.

    Derived from category + slugified tool name, e.g. 'whois.whoxy'.
    Kept as a dedicated value object (rather than a bare str) so call
    sites can't accidentally pass an arbitrary string where a real
    plugin identity is required.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or " " in self.value:
            raise ValueError(f"Invalid PluginId: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class PluginMetadata:
    """The contract every plugin must expose, per project requirements:

    Name, Description, Category, Arguments, Example, Help,
    Output Parser (name/id of the parser strategy to use),
    Supported Output Formats.
    """

    plugin_id: PluginId
    name: str
    description: str
    category: Category
    tool_type: ToolType
    arguments: tuple[Argument, ...] = field(default_factory=tuple)
    example: str = ""
    help_text: str = ""
    output_parser: str = "raw_text"
    supported_output_formats: tuple[OutputFormat, ...] = (OutputFormat.TEXT,)

    # Provenance / execution wiring (still metadata, not behavior)
    homepage: str | None = None
    install_hint: str | None = None          # e.g. "pip install theHarvester"
    binary_name: str | None = None           # e.g. "theHarvester" — used for PATH detection
    source_line_ref: str | None = None       # traceability back to osint_tools.md

    def requires_local_binary(self) -> bool:
        return self.tool_type is ToolType.CLI and bool(self.binary_name)


@dataclass(slots=True)
class PluginState:
    """Mutable runtime state for a plugin, tracked separately from its
    immutable metadata so re-detection never mutates the metadata object.
    """

    plugin_id: PluginId
    status: PluginStatus = PluginStatus.NOT_APPLICABLE
    last_checked: datetime | None = None
    last_error: str | None = None
    is_favorite: bool = False
    run_count: int = 0


@dataclass(slots=True)
class ExecutionResult:
    """Result of running/querying a plugin, before report formatting."""

    plugin_id: PluginId
    started_at: datetime
    finished_at: datetime
    exit_code: int | None
    raw_output: str
    parsed_output: dict[str, Any] | list[Any] | str | None = None
    success: bool = True
    error_message: str | None = None

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()
