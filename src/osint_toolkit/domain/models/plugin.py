from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus


@dataclass
class PluginArgument:
    name: str
    description: str
    type: str = "string"
    required: bool = False
    default: Any = None
    choices: list[str] = field(default_factory=list)


@dataclass
class OutputFormat:
    name: str
    description: str
    extension: str
    mime_type: str | None = None


@dataclass
class ToolInfo:
    name: str
    description: str
    category: ToolCategory
    tool_type: ToolType
    cli_command: str | None = None
    url: str | None = None
    api_endpoint: str | None = None
    tutorial_url: str | None = None
    version: str = "1.0.0"
    author: str = "OSINT Toolkit"
    license: str = "MIT"
    tags: list[str] = field(default_factory=list)
    arguments: list[dict[str, Any]] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    help_text: str = ""
    supported_output_formats: list[str] = field(default_factory=list)
    status: ToolStatus = ToolStatus.NOT_INSTALLED
    installed_version: str | None = None
    last_checked: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "tool_type": self.tool_type.value,
            "cli_command": self.cli_command,
            "url": self.url,
            "api_endpoint": self.api_endpoint,
            "tutorial_url": self.tutorial_url,
            "version": self.version,
            "author": self.author,
            "license": self.license,
            "tags": self.tags,
            "arguments": self.arguments,
            "examples": self.examples,
            "help_text": self.help_text,
            "supported_output_formats": self.supported_output_formats,
            "status": self.status.value,
            "installed_version": self.installed_version,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolInfo:
        data = data.copy()
        data["category"] = ToolCategory(data["category"])
        data["tool_type"] = ToolType(data["tool_type"])
        data["status"] = ToolStatus(data["status"])
        if data.get("last_checked"):
            data["last_checked"] = datetime.fromisoformat(data["last_checked"])
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


@dataclass
class PluginResult:
    success: bool
    data: Any = None
    error: str | None = None
    raw_output: str = ""
    format: str = "text"
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "raw_output": self.raw_output,
            "format": self.format,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginResult:
        return cls(**data)


@dataclass
class SearchResult:
    query: str
    results: list[ToolInfo]
    total: int
    execution_time: float


@dataclass
class PluginMetadata:
    name: str
    description: str
    category: ToolCategory
    tool_type: ToolType
    version: str = "1.0.0"
    author: str = "OSINT Toolkit"
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""
    tags: list[str] = field(default_factory=list)
    arguments: list[PluginArgument] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    help_text: str = ""
    supported_output_formats: list[OutputFormat] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    cli_command: str | None = None
    api_endpoint: str | None = None
    api_key_required: bool = False
    rate_limit: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "tool_type": self.tool_type.value,
            "version": self.version,
            "author": self.author,
            "license": self.license,
            "homepage": self.homepage,
            "repository": self.repository,
            "tags": self.tags,
            "arguments": [arg.to_dict() if hasattr(arg, 'to_dict') else arg for arg in self.arguments],
            "examples": self.examples,
            "help_text": self.help_text,
            "supported_output_formats": [
                {"name": f.name, "description": f.description, "extension": f.extension, "mime_type": f.mime_type}
                for f in self.supported_output_formats
            ],
            "dependencies": self.dependencies,
            "cli_command": self.cli_command,
            "api_endpoint": self.api_endpoint,
            "api_key_required": self.api_key_required,
            "rate_limit": self.rate_limit,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }