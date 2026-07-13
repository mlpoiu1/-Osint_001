from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from osint_toolkit.application.usecases.base import UseCaseRequest, UseCaseResponse, IUseCase
from osint_toolkit.domain.interfaces import IPluginRegistry
from osint_toolkit.domain.models.plugin import PluginResult


@dataclass
class ExecutePluginRequest(UseCaseRequest):
    plugin_name: str
    arguments: dict[str, Any]
    output_format: str = "text"


@dataclass
class ExecutePluginResponse(UseCaseResponse):
    result: PluginResult | None = None


class ExecutePluginUseCase(IUseCase):
    def __init__(self, plugin_registry: IPluginRegistry):
        self._registry = plugin_registry

    async def execute(self, request: ExecutePluginRequest) -> ExecutePluginResponse:
        try:
            plugin = self._registry.get(request.plugin_name)
            if not plugin:
                return ExecutePluginResponse(
                    success=False, error=f"Plugin not found: {request.plugin_name}"
                )

            if not plugin.is_available():
                return ExecutePluginResponse(
                    success=False,
                    error=f"Plugin not available: {request.plugin_name}",
                )

            valid, error = await plugin.validate_arguments(request.arguments)
            if not valid:
                return ExecutePluginResponse(success=False, error=error)

            result = await plugin.execute(request.arguments, request.output_format)
            return ExecutePluginResponse(success=True, result=result)

        except Exception as e:
            return ExecutePluginResponse(success=False, error=str(e))


@dataclass
class GetPluginHelpRequest(UseCaseRequest):
    plugin_name: str


@dataclass
class GetPluginHelpResponse(UseCaseResponse):
    help_text: str | None = None


class GetPluginHelpUseCase(IUseCase):
    def __init__(self, plugin_registry: IPluginRegistry):
        self._registry = plugin_registry

    async def execute(self, request: GetPluginHelpRequest) -> GetPluginHelpResponse:
        try:
            plugin = self._registry.get(request.plugin_name)
            if not plugin:
                return GetPluginHelpResponse(
                    success=False, error=f"Plugin not found: {request.plugin_name}"
                )

            help_text = plugin.get_help()
            return GetPluginHelpResponse(success=True, help_text=help_text)
        except Exception as e:
            return GetPluginHelpResponse(success=False, error=str(e))


@dataclass
class ValidatePluginArgumentsRequest(UseCaseRequest):
    plugin_name: str
    arguments: dict[str, Any]


@dataclass
class ValidatePluginArgumentsResponse(UseCaseResponse):
    valid: bool = False
    error: str | None = None


class ValidatePluginArgumentsUseCase(IUseCase):
    def __init__(self, plugin_registry: IPluginRegistry):
        self._registry = plugin_registry

    async def execute(self, request: ValidatePluginArgumentsRequest) -> ValidatePluginArgumentsResponse:
        try:
            plugin = self._registry.get(request.plugin_name)
            if not plugin:
                return ValidatePluginArgumentsResponse(
                    success=False, error=f"Plugin not found: {request.plugin_name}"
                )

            valid, error = await plugin.validate_arguments(request.arguments)
            return ValidatePluginArgumentsResponse(success=True, valid=valid, error=error)
        except Exception as e:
            return ValidatePluginArgumentsResponse(success=False, error=str(e))