from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from osint_toolkit.domain.models.plugin import ToolInfo, ToolCategory


class ISearchService(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[ToolInfo]:
        pass

    @abstractmethod
    async def fuzzy_search(self, query: str, limit: int = 10) -> list[tuple[ToolInfo, float]]:
        pass

    @abstractmethod
    async def search_by_category(self, category: ToolCategory, limit: int = 50) -> list[ToolInfo]:
        pass

    @abstractmethod
    async def search_by_tag(self, tag: str, limit: int = 50) -> list[ToolInfo]:
        pass


class IToolRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[ToolInfo]:
        pass

    @abstractmethod
    async def get_by_id(self, tool_id: str) -> ToolInfo | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> ToolInfo | None:
        pass

    @abstractmethod
    async def get_by_category(self, category: ToolCategory) -> list[ToolInfo]:
        pass

    @abstractmethod
    async def get_by_type(self, tool_type: str) -> list[ToolInfo]:
        pass

    @abstractmethod
    async def get_available(self) -> list[ToolInfo]:
        pass

    @abstractmethod
    async def get_installed(self) -> list[ToolInfo]:
        pass

    @abstractmethod
    async def create(self, tool: ToolInfo) -> ToolInfo:
        pass

    @abstractmethod
    async def update(self, tool: ToolInfo) -> ToolInfo:
        pass

    @abstractmethod
    async def update_status(self, tool_id: str, status: str, version: str | None = None) -> bool:
        pass

    @abstractmethod
    async def delete(self, tool_id: str) -> bool:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def count_by_category(self) -> dict[ToolCategory, int]:
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[ToolInfo]:
        pass


class IPluginRegistry(ABC):
    @abstractmethod
    def register(self, plugin: Any) -> None:
        pass

    @abstractmethod
    def unregister(self, plugin_name: str) -> bool:
        pass

    @abstractmethod
    def get(self, plugin_name: str) -> Any | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Any]:
        pass

    @abstractmethod
    def get_by_category(self, category: ToolCategory) -> list[Any]:
        pass

    @abstractmethod
    def get_by_type(self, tool_type: str) -> list[Any]:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 20) -> list[Any]:
        pass

    @abstractmethod
    def fuzzy_search(self, query: str, limit: int = 10) -> list[tuple[Any, float]]:
        pass


class IReportGenerator(ABC):
    @abstractmethod
    async def generate_json(self, tools: list[ToolInfo], output_path: str) -> None:
        pass

    @abstractmethod
    async def generate_html(self, tools: list[ToolInfo], output_path: str, template: str | None = None) -> None:
        pass

    @abstractmethod
    async def generate_markdown(self, tools: list[ToolInfo], output_path: str) -> None:
        pass


class ICLIDetector(ABC):
    @abstractmethod
    async def detect(self, command: str) -> tuple[bool, str | None]:
        pass

    @abstractmethod
    async def get_version(self, command: str) -> str | None:
        pass

    @abstractmethod
    async def is_available(self, command: str) -> bool:
        pass


class IConfigurationService(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def get_all(self) -> dict[str, Any]:
        pass


class IEventBus(ABC):
    @abstractmethod
    def subscribe(self, event_type: str, handler: Any) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Any) -> None:
        pass

    @abstractmethod
    async def publish(self, event_type: str, data: Any) -> None:
        pass


class IPluginFactory(ABC):
    @abstractmethod
    def create_plugin(self, tool_info: ToolInfo) -> Any:
        pass

    @abstractmethod
    def get_plugin_class(self, tool_type: Any) -> type[Any]:
        pass


class IOutputParser(ABC):
    @abstractmethod
    def parse(self, raw_output: str, format: str) -> Any:
        pass

    @abstractmethod
    def supported_formats(self) -> list[str]:
        pass
