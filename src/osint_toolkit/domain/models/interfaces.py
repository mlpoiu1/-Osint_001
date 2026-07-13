from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.plugin import PluginResult, ToolInfo, PluginArgument


class IPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> ToolCategory:
        pass

    @property
    @abstractmethod
    def tool_type(self) -> ToolType:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def arguments(self) -> list[PluginArgument]:
        pass

    @property
    @abstractmethod
    def examples(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def help_text(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_output_formats(self) -> list[str]:
        pass

    @abstractmethod
    async def execute(self, arguments: dict[str, Any], output_format: str = "text") -> PluginResult:
        pass

    @abstractmethod
    async def validate_arguments(self, arguments: dict[str, Any]) -> tuple[bool, str | None]:
        pass

    @abstractmethod
    def get_help(self) -> str:
        pass

    def is_available(self) -> bool:
        return True

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE


class ICLIPlugin(IPlugin):
    @property
    @abstractmethod
    def cli_command(self) -> str:
        pass

    @property
    @abstractmethod
    def cli_arguments(self) -> list[str]:
        pass


class IOnlineServicePlugin(IPlugin):
    @property
    @abstractmethod
    def service_url(self) -> str:
        pass

    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        pass

    @property
    @abstractmethod
    def api_documentation_url(self) -> str | None:
        pass


class IAPIPlugin(IPlugin):
    @property
    @abstractmethod
    def api_endpoint(self) -> str:
        pass

    @property
    @abstractmethod
    def api_key_name(self) -> str | None:
        pass

    @property
    @abstractmethod
    def rate_limit(self) -> int | None:
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        pass


class IFrameworkPlugin(IPlugin):
    @property
    @abstractmethod
    def framework_name(self) -> str:
        pass

    @property
    @abstractmethod
    def entry_point(self) -> str:
        pass