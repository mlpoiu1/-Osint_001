from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from osint_toolkit.application.usecases.base import UseCaseRequest, UseCaseResponse, IUseCase
from osint_toolkit.domain.interfaces import IToolRepository, ISearchService
from osint_toolkit.domain.models.plugin import ToolInfo, ToolCategory, ToolStatus, ToolType


@dataclass
class ListToolsRequest(UseCaseRequest):
    category: ToolCategory | None = None
    tool_type: ToolType | None = None
    status: ToolStatus | None = None
    limit: int = 100
    offset: int = 0


@dataclass
class ListToolsResponse(UseCaseResponse):
    tools: list[ToolInfo] | None = None
    total: int = 0


class ListToolsUseCase(IUseCase):
    def __init__(self, tool_repository: IToolRepository):
        self._repository = tool_repository

    async def execute(self, request: ListToolsRequest) -> ListToolsResponse:
        try:
            if request.category:
                tools = await self._repository.get_by_category(request.category)
            elif request.tool_type:
                tools = await self._repository.get_by_type(request.tool_type)
            elif request.status:
                tools = await self._repository.get_by_status(request.status)
            else:
                tools = await self._repository.get_all()

            total = len(tools)
            tools = tools[request.offset : request.offset + request.limit]

            return ListToolsResponse(success=True, tools=tools, total=total)
        except Exception as e:
            return ListToolsResponse(success=False, error=str(e))


@dataclass
class GetToolRequest(UseCaseRequest):
    name: str


@dataclass
class GetToolResponse(UseCaseResponse):
    tool: ToolInfo | None = None


class GetToolUseCase(IUseCase):
    def __init__(self, tool_repository: IToolRepository):
        self._repository = tool_repository

    async def execute(self, request: GetToolRequest) -> GetToolResponse:
        try:
            tool = await self._repository.get_by_id(request.name)
            if tool:
                return GetToolResponse(success=True, tool=tool)
            return GetToolResponse(success=False, error=f"Tool not found: {request.name}")
        except Exception as e:
            return GetToolResponse(success=False, error=str(e))


@dataclass
class SearchToolsRequest(UseCaseRequest):
    query: str
    limit: int = 20


@dataclass
class SearchToolsResponse(UseCaseResponse):
    tools: list[ToolInfo] | None = None


class SearchToolsUseCase(IUseCase):
    def __init__(self, search_service: ISearchService):
        self._search_service = search_service

    async def execute(self, request: SearchToolsRequest) -> SearchToolsResponse:
        try:
            tools = await self._search_service.search(request.query, request.limit)
            return SearchToolsResponse(success=True, tools=tools)
        except Exception as e:
            return SearchToolsResponse(success=False, error=str(e))


@dataclass
class FuzzySearchToolsRequest(UseCaseRequest):
    query: str
    limit: int = 10


@dataclass
class FuzzySearchToolsResponse(UseCaseResponse):
    results: list[tuple[ToolInfo, float]] | None = None


class FuzzySearchToolsUseCase(IUseCase):
    def __init__(self, search_service: ISearchService):
        self._search_service = search_service

    async def execute(self, request: FuzzySearchToolsRequest) -> FuzzySearchToolsResponse:
        try:
            results = await self._search_service.fuzzy_search(request.query, request.limit)
            return FuzzySearchToolsResponse(success=True, results=results)
        except Exception as e:
            return FuzzySearchToolsResponse(success=False, error=str(e))


@dataclass
class RefreshToolStatusRequest(UseCaseRequest):
    name: str | None = None
    category: ToolCategory | None = None


@dataclass
class RefreshToolStatusResponse(UseCaseResponse):
    updated: int = 0
    failed: int = 0


class RefreshToolStatusUseCase(IUseCase):
    def __init__(
        self,
        tool_repository: IToolRepository,
        cli_detector: Any,
    ):
        self._repository = tool_repository
        self._cli_detector = cli_detector

    async def execute(self, request: RefreshToolStatusRequest) -> RefreshToolStatusResponse:
        try:
            if request.name:
                tool = await self._repository.get_by_id(request.name)
                if not tool:
                    return RefreshToolStatusResponse(
                        success=False, error=f"Tool not found: {request.name}"
                    )
                tools = [tool]
            elif request.category:
                tools = await self._repository.get_by_category(request.category)
            else:
                tools = await self._repository.get_all()

            updated = 0
            failed = 0

            for tool in tools:
                if tool.cli_command:
                    is_available, version = await self._cli_detector.detect(tool.cli_command)
                    new_status = ToolStatus.INSTALLED if is_available else ToolStatus.NOT_INSTALLED
                    await self._repository.update_status(tool.name, new_status, version)
                    updated += 1
                else:
                    failed += 1

            return RefreshToolStatusResponse(success=True, updated=updated, failed=failed)
        except Exception as e:
            return RefreshToolStatusResponse(success=False, error=str(e))