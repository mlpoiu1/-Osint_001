from __future__ import annotations

from rapidfuzz import fuzz, process
from typing import Any

from osint_toolkit.domain.interfaces import ISearchService
from osint_toolkit.domain.models.plugin import ToolInfo


class SearchService(ISearchService):
    def __init__(self, tool_repository=None):
        self._tool_repository = tool_repository
        self._index: list[ToolInfo] = []

    async def search(self, query: str, limit: int = 20) -> list[ToolInfo]:
        if self._tool_repository:
            return await self._tool_repository.search(query, limit)
        return self._search_in_memory(query, limit)

    async def fuzzy_search(self, query: str, limit: int = 10) -> list[tuple[ToolInfo, float]]:
        if self._tool_repository:
            return await self._tool_repository.fuzzy_search(query, limit)
        return self._fuzzy_search_in_memory(query, limit)

    async def search_by_category(self, category: Any, limit: int = 50) -> list[ToolInfo]:
        if self._tool_repository:
            return await self._tool_repository.get_by_category(category)
        return [t for t in self._index if t.category == category][:limit]

    async def search_by_tag(self, tag: str, limit: int = 50) -> list[ToolInfo]:
        tag_lower = tag.lower()
        if self._tool_repository:
            all_tools = await self._tool_repository.get_all()
        else:
            all_tools = self._index

        return [t for t in all_tools if any(tag_lower in t.lower() for t in t.tags)][:limit]

    async def index_tool(self, tool: ToolInfo) -> None:
        if tool not in self._index:
            self._index.append(tool)

    async def remove_from_index(self, tool_name: str) -> None:
        self._index = [t for t in self._index if t.name != tool_name]

    def _search_in_memory(self, query: str, limit: int) -> list[ToolInfo]:
        query_lower = query.lower()
        results = []
        for tool in self._index:
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower() or
                any(query_lower in tag.lower() for tag in tool.tags)):
                results.append(tool)
                if len(results) >= limit:
                    break
        return results

    def _fuzzy_search_in_memory(self, query: str, limit: int) -> list[tuple[ToolInfo, float]]:
        choices = [(tool, f"{tool.name} {tool.description} {' '.join(tool.tags)}") for tool in self._index]
        results = process.extract(
            query,
            choices,
            scorer=fuzz.WRatio,
            processor=lambda x: x[1],
            limit=limit,
        )
        return [(tool, score / 100.0) for tool, _, score in results]

    def set_index(self, tools: list[ToolInfo]):
        self._index = tools