from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any

from rapidfuzz import fuzz, process

from osint_toolkit.domain.interfaces import IPluginRegistry, ToolCategory, ToolType
from osint_toolkit.domain.models.plugin import ToolInfo


class InMemoryPluginRegistry(IPluginRegistry):
    def __init__(self):
        self._plugins: dict[str, Any] = {}
        self._by_category: dict[ToolCategory, list[str]] = defaultdict(list)
        self._by_type: dict[ToolType, list[str]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def register(self, plugin: Any) -> None:
        async with self._lock:
            name = plugin.metadata.name
            if name in self._plugins:
                raise ValueError(f"Plugin already registered: {name}")

            self._plugins[name] = plugin
            self._by_category[plugin.metadata.category].append(name)
            self._by_type[plugin.metadata.tool_type].append(name)

    async def unregister(self, name: str) -> bool:
        async with self._lock:
            plugin = self._plugins.pop(name, None)
            if not plugin:
                return False

            category_list = self._by_category.get(plugin.metadata.category, [])
            if name in category_list:
                category_list.remove(name)

            type_list = self._by_type.get(plugin.metadata.tool_type, [])
            if name in type_list:
                type_list.remove(name)

            return True

    def get(self, name: str) -> Any | None:
        return self._plugins.get(name)

    def get_all(self) -> list[Any]:
        return list(self._plugins.values())

    def get_by_category(self, category: ToolCategory) -> list[Any]:
        names = self._by_category.get(category, [])
        return [self._plugins[name] for name in names if name in self._plugins]

    def get_by_type(self, tool_type: ToolType) -> list[Any]:
        names = self._by_type.get(tool_type, [])
        return [self._plugins[name] for name in names if name in self._plugins]

    def search(self, query: str, limit: int = 20) -> list[Any]:
        query_lower = query.lower()
        results = []

        for name, plugin in self._plugins.items():
            if query_lower in name.lower() or query_lower in plugin.metadata.description.lower():
                results.append(plugin)
            elif any(query_lower in tag.lower() for tag in plugin.metadata.tags):
                results.append(plugin)

            if len(results) >= limit:
                break

        return results

    def fuzzy_search(self, query: str, limit: int = 10) -> list[tuple[Any, float]]:
        choices = [(name, plugin) for name, plugin in self._plugins.items()]
        results = process.extract(
            query,
            choices,
            scorer=fuzz.WRatio,
            processor=lambda x: f"{x[0]} {x[1].metadata.description} {' '.join(x[1].metadata.tags)}",
            limit=limit,
        )
        return [(plugin, score / 100.0) for _, plugin, score in results]


class PluginRegistry(IPluginRegistry):
    def __init__(self):
        self._registry = InMemoryPluginRegistry()

    def register(self, plugin: Any) -> None:
        self._registry.register(plugin)

    def unregister(self, name: str) -> bool:
        return self._registry.unregister(name)

    def get(self, name: str) -> Any | None:
        return self._registry.get(name)

    def get_all(self) -> list[Any]:
        return self._registry.get_all()

    def get_by_category(self, category: ToolCategory) -> list[Any]:
        return self._registry.get_by_category(category)

    def get_by_type(self, tool_type: ToolType) -> list[Any]:
        return self._registry.get_by_type(tool_type)

    def search(self, query: str, limit: int = 20) -> list[Any]:
        return self._registry.search(query, limit)

    def fuzzy_search(self, query: str, limit: int = 10) -> list[tuple[Any, float]]:
        return self._registry.fuzzy_search(query, limit)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolInfo] = {}
        self._by_category: dict[ToolCategory, list[str]] = defaultdict(list)
        self._by_type: dict[ToolType, list[str]] = defaultdict(list)
        self._by_status: dict[Any, list[str]] = defaultdict(list)

    def add(self, tool: ToolInfo) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already exists: {tool.name}")

        self._tools[tool.name] = tool
        self._by_category[tool.category].append(tool.name)
        self._by_type[tool.tool_type].append(tool.name)
        self._by_status[tool.status].append(tool.name)

    def remove(self, name: str) -> bool:
        tool = self._tools.pop(name, None)
        if not tool:
            return False

        for category_list in self._by_category.values():
            if name in category_list:
                category_list.remove(name)

        for type_list in self._by_type.values():
            if name in type_list:
                type_list.remove(name)

        for status_list in self._by_status.values():
            if name in status_list:
                status_list.remove(name)

        return True

    def get(self, name: str) -> ToolInfo | None:
        return self._tools.get(name)

    def get_all(self) -> list[ToolInfo]:
        return list(self._tools.values())

    def get_by_category(self, category: ToolCategory) -> list[ToolInfo]:
        return [self._tools[name] for name in self._by_category.get(category, []) if name in self._tools]

    def get_by_type(self, tool_type: ToolType) -> list[ToolInfo]:
        return [self._tools[name] for name in self._by_type.get(tool_type, []) if name in self._tools]

    def get_by_status(self, status) -> list[ToolInfo]:
        return [self._tools[name] for name in self._by_status.get(status, []) if name in self._tools]

    def search(self, query: str, limit: int = 20) -> list[ToolInfo]:
        query_lower = query.lower()
        results = []

        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower() or
                any(query_lower in tag.lower() for tag in tool.tags)):
                results.append(tool)

            if len(results) >= limit:
                break

        return results

    def fuzzy_search(self, query: str, limit: int = 10) -> list[tuple[ToolInfo, float]]:
        choices = [(name, tool) for name, tool in self._tools.items()]
        results = process.extract(
            query,
            choices,
            scorer=fuzz.WRatio,
            processor=lambda x: f"{x[0]} {x[1].description} {' '.join(x[1].tags)}",
            limit=limit,
        )
        return [(tool, score / 100.0) for _, tool, score in results]

    def update_status(self, name: str, status, version: str | None = None) -> bool:
        tool = self._tools.get(name)
        if not tool:
            return False

        old_status = tool.status
        if name in self._by_status[old_status]:
            self._by_status[old_status].remove(name)

        tool.status = status
        if version:
            tool.installed_version = version
        tool.last_checked = datetime.now()

        self._by_status[status].append(name)
        return True