from __future__ import annotations

from typing import Any

from osint_toolkit.domain.interfaces import IPluginFactory
from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.interfaces import IPlugin
from osint_toolkit.domain.models.plugin import PluginArgument, ToolInfo
from osint_toolkit.infrastructure.plugins.base import (
    BasePlugin,
    CLIPlugin,
    OnlineServicePlugin,
    APIPlugin,
    FrameworkPlugin,
)


class PluginFactory(IPluginFactory):
    def __init__(self):
        self._builders: dict[ToolType, callable] = {
            ToolType.CLI: self._build_cli_plugin,
            ToolType.ONLINE_SERVICE: self._build_online_service_plugin,
            ToolType.API: self._build_api_plugin,
            ToolType.FRAMEWORK: self._build_framework_plugin,
        }

    def create_plugin(self, tool_info: ToolInfo) -> IPlugin:
        builder = self._builders.get(tool_info.tool_type)
        if not builder:
            raise ValueError(f"No builder for tool type: {tool_info.tool_type}")
        return builder(tool_info)

    def get_plugin_class(self, tool_type: ToolType) -> type[IPlugin]:
        return self._builders.get(tool_type, BasePlugin)

    def _build_cli_plugin(self, tool_info: ToolInfo) -> CLIPlugin:
        args = []
        for arg_data in tool_info.metadata.get("arguments", []):
            args.append(PluginArgument(
                name=arg_data["name"],
                description=arg_data["description"],
                type=arg_data.get("type", "string"),
                required=arg_data.get("required", False),
                default=arg_data.get("default"),
                choices=arg_data.get("choices", []),
            ))
        return CLIPlugin(
            name=tool_info.name,
            description=tool_info.description,
            category=tool_info.category,
            cli_command=tool_info.cli_command or tool_info.name.lower().replace(" ", "-"),
            cli_args_template=tool_info.metadata.get("cli_args_template", []),
            version=tool_info.version or "1.0.0",
            arguments=args,
            examples=tool_info.metadata.get("examples", []),
            help_text=tool_info.metadata.get("help_text", tool_info.description),
            supported_output_formats=tool_info.metadata.get("supported_output_formats", ["text", "json"]),
            check_installed=tool_info.metadata.get("check_installed", True),
        )

    def _build_online_service_plugin(self, tool_info: ToolInfo) -> OnlineServicePlugin:
        args = []
        for arg_data in tool_info.metadata.get("arguments", []):
            args.append(PluginArgument(
                name=arg_data["name"],
                description=arg_data["description"],
                type=arg_data.get("type", "string"),
                required=arg_data.get("required", False),
                default=arg_data.get("default"),
                choices=arg_data.get("choices", []),
            ))
        return OnlineServicePlugin(
            name=tool_info.name,
            description=tool_info.description,
            category=tool_info.category,
            service_url=tool_info.url or "",
            version=tool_info.version or "1.0.0",
            arguments=args,
            examples=tool_info.metadata.get("examples", []),
            help_text=tool_info.metadata.get("help_text", tool_info.description),
            supported_output_formats=tool_info.metadata.get("supported_output_formats", ["text", "json"]),
        )

    def _build_api_plugin(self, tool_info: ToolInfo) -> APIPlugin:
        args = []
        for arg_data in tool_info.metadata.get("arguments", []):
            args.append(PluginArgument(
                name=arg_data["name"],
                description=arg_data["description"],
                type=arg_data.get("type", "string"),
                required=arg_data.get("required", False),
                default=arg_data.get("default"),
                choices=arg_data.get("choices", []),
            ))
        return APIPlugin(
            name=tool_info.name,
            description=tool_info.description,
            category=tool_info.category,
            api_endpoint=tool_info.api_endpoint or "",
            api_key_required=tool_info.metadata.get("api_key_required", False),
            rate_limit=tool_info.metadata.get("rate_limit"),
            version=tool_info.version or "1.0.0",
            arguments=args,
            examples=tool_info.metadata.get("examples", []),
            help_text=tool_info.metadata.get("help_text", tool_info.description),
            supported_output_formats=tool_info.metadata.get("supported_output_formats", ["text", "json"]),
        )

    def _build_framework_plugin(self, tool_info: ToolInfo) -> FrameworkPlugin:
        args = []
        for arg_data in tool_info.metadata.get("arguments", []):
            args.append(PluginArgument(
                name=arg_data["name"],
                description=arg_data["description"],
                type=arg_data.get("type", "string"),
                required=arg_data.get("required", False),
                default=arg_data.get("default"),
                choices=arg_data.get("choices", []),
            ))
        return FrameworkPlugin(
            name=tool_info.name,
            description=tool_info.description,
            category=tool_info.category,
            framework_name=tool_info.metadata.get("framework_name", tool_info.name),
            entry_point=tool_info.metadata.get("entry_point", ""),
            version=tool_info.version or "1.0.0",
            arguments=args,
            examples=tool_info.metadata.get("examples", []),
            help_text=tool_info.metadata.get("help_text", tool_info.description),
            supported_output_formats=tool_info.metadata.get("supported_output_formats", ["text", "json"]),
        )