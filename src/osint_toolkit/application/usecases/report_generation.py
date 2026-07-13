from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from osint_toolkit.application.usecases.base import UseCaseRequest, UseCaseResponse, IUseCase
from osint_toolkit.domain.interfaces import IToolRepository, IReportGenerator
from osint_toolkit.domain.models.plugin import ToolInfo, ToolCategory


@dataclass
class GenerateReportRequest(UseCaseRequest):
    format: str
    output_path: str
    category: ToolCategory | None = None
    template: str | None = None


@dataclass
class GenerateReportResponse(UseCaseResponse):
    output_path: str | None = None


class GenerateReportUseCase(IUseCase):
    def __init__(
        self,
        tool_repository: IToolRepository,
        report_generator: IReportGenerator,
    ):
        self._repository = tool_repository
        self._generator = report_generator

    async def execute(self, request: GenerateReportRequest) -> GenerateReportResponse:
        try:
            if request.category:
                tools = await self._repository.get_by_category(request.category)
            else:
                tools = await self._repository.get_all()

            if request.format.lower() == "json":
                await self._generator.generate_json(tools, request.output_path)
            elif request.format.lower() == "html":
                await self._generator.generate_html(tools, request.output_path, request.template)
            elif request.format.lower() == "markdown" or request.format.lower() == "md":
                await self._generator.generate_markdown(tools, request.output_path)
            else:
                return GenerateReportResponse(
                    success=False, error=f"Unsupported format: {request.format}"
                )

            return GenerateReportResponse(success=True, output_path=request.output_path)
        except Exception as e:
            return GenerateReportResponse(success=False, error=str(e))