from __future__ import annotations

import asyncio
import shlex
import time
from abc import ABC, abstractmethod
from typing import Any

from osint_toolkit.domain.interfaces import IOutputParser
from osint_toolkit.domain.models.enums import ToolCategory, ToolStatus, ToolType
from osint_toolkit.domain.models.interfaces import IPlugin
from osint_toolkit.domain.models.plugin import (
    OutputFormat,
    PluginArgument,
    PluginMetadata,
    PluginResult,
)


class BasePlugin(IPlugin, ABC):
    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        tool_type: ToolType,
        version: str = "1.0.0",
        author: str = "OSINT Toolkit",
        license: str = "MIT",
        homepage: str = "",
        repository: str = "",
        tags: list[str] = None,
        arguments: list[PluginArgument] = None,
        examples: list[str] = None,
        help_text: str = "",
        supported_output_formats: list[OutputFormat] = None,
        dependencies: list[str] = None,
    ):
        self._metadata = PluginMetadata(
            name=name,
            description=description,
            category=category,
            tool_type=tool_type,
            version=version,
            author=author,
            license=license,
            homepage=homepage,
            repository=repository,
            tags=tags or [],
            arguments=arguments or [],
            examples=examples or [],
            help_text=help_text,
            supported_output_formats=supported_output_formats or [
                OutputFormat(name="text", description="Plain text output", extension="txt", mime_type="text/plain"),
                OutputFormat(name="json", description="JSON output", extension="json", mime_type="application/json"),
            ],
            dependencies=dependencies or [],
        )
        self._parser: IOutputParser | None = None

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    @abstractmethod
    async def execute(
        self,
        arguments: dict[str, Any],
        output_format: str = "text",
    ) -> PluginResult:
        pass

    async def validate_arguments(self, arguments: dict[str, Any]) -> tuple[bool, str | None]:
        for arg in self._metadata.arguments:
            if arg.required and arg.name not in arguments:
                return False, f"Required argument missing: {arg.name}"
            if arg.name in arguments:
                value = arguments[arg.name]
                if arg.choices and value not in arg.choices:
                    return False, f"Invalid value for {arg.name}: {value}. Choices: {arg.choices}"
                if arg.type == "integer" and not isinstance(value, int):
                    try:
                        arguments[arg.name] = int(value)
                    except ValueError:
                        return False, f"Argument {arg.name} must be an integer"
                elif arg.type == "float" and not isinstance(value, float):
                    try:
                        arguments[arg.name] = float(value)
                    except ValueError:
                        return False, f"Argument {arg.name} must be a float"
        return True, None

    def parse_output(self, raw_output: str, output_format: str) -> Any:
        if self._parser:
            return self._parser.parse(raw_output, output_format)
        return raw_output

    def is_available(self) -> bool:
        return True

    async def check_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self.is_available() else ToolStatus.DISABLED

    def get_help(self) -> str:
        lines = [
            f"Plugin: {self._metadata.name}",
            f"Description: {self._metadata.description}",
            f"Category: {self._metadata.category.value}",
            f"Type: {self._metadata.tool_type.value}",
            f"Version: {self._metadata.version}",
            "",
            "Arguments:",
        ]
        for arg in self._metadata.arguments:
            req = " (required)" if arg.required else ""
            default = f" [default: {arg.default}]" if arg.default is not None else ""
            choices = f" (choices: {', '.join(arg.choices)})" if arg.choices else ""
            lines.append(f"  {arg.name}: {arg.description}{req}{default}{choices}")

        if self._metadata.examples:
            lines.extend(["", "Examples:"])
            for ex in self._metadata.examples:
                lines.append(f"  {ex}")

        if self._metadata.help_text:
            lines.extend(["", "Help:", self._metadata.help_text])

        return "\n".join(lines)

    def set_parser(self, parser: IOutputParser):
        self._parser = parser


class CLIPlugin(BasePlugin):
    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        cli_command: str,
        cli_args_template: list[str] = None,
        version: str = "1.0.0",
        arguments: list[PluginArgument] = None,
        examples: list[str] = None,
        help_text: str = "",
        supported_output_formats: list[OutputFormat] = None,
        check_installed: bool = True,
    ):
        super().__init__(
            name=name,
            description=description,
            category=category,
            tool_type=ToolType.CLI,
            version=version,
            arguments=arguments,
            examples=examples,
            help_text=help_text,
            supported_output_formats=supported_output_formats,
        )
        self._cli_command = cli_command
        self._cli_args_template = cli_args_template or []
        self._check_installed = check_installed
        self._installed = None
        self._version = None

    async def execute(
        self,
        arguments: dict[str, Any],
        output_format: str = "text",
    ) -> PluginResult:
        start_time = time.time()
        try:
            cmd = self._build_command(arguments)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time

            raw_output = stdout.decode("utf-8", errors="replace")
            error_output = stderr.decode("utf-8", errors="replace")

            if process.returncode != 0:
                return PluginResult(
                    success=False,
                    error=error_output or f"Command failed with exit code {process.returncode}",
                    raw_output=raw_output,
                    format=output_format,
                    execution_time=execution_time,
                )

            parsed = self.parse_output(raw_output, output_format)
            return PluginResult(
                success=True,
                data=parsed,
                raw_output=raw_output,
                format=output_format,
                execution_time=execution_time,
            )
        except FileNotFoundError:
            return PluginResult(
                success=False,
                error=f"Command not found: {self._cli_command}",
                format=output_format,
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e),
                format=output_format,
                execution_time=time.time() - start_time,
            )

    def _build_command(self, arguments: dict[str, Any]) -> list[str]:
        cmd = [self._cli_command]
        for template in self._cli_args_template:
            for key, value in arguments.items():
                placeholder = f"{{{key}}}"
                if placeholder in template:
                    if isinstance(value, bool):
                        if value:
                            cmd.append(template.replace(placeholder, ""))
                    elif value is not None:
                        cmd.append(template.replace(placeholder, str(value)))
        return cmd

    def is_available(self) -> bool:
        if self._installed is not None:
            return self._installed
        if not self._check_installed:
            self._installed = True
            return True
        import shutil
        self._installed = shutil.which(self._cli_command) is not None
        return self._installed

    async def check_status(self) -> ToolStatus:
        available = self.is_available()
        if available:
            self._version = await self._get_version()
        return ToolStatus.INSTALLED if available else ToolStatus.NOT_INSTALLED

    async def _get_version(self) -> str | None:
        try:
            process = await asyncio.create_subprocess_exec(
                self._cli_command, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            if process.returncode == 0:
                return stdout.decode("utf-8", errors="replace").strip()
        except Exception:
            pass
        return None


class OnlineServicePlugin(BasePlugin):
    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        service_url: str,
        version: str = "1.0.0",
        arguments: list[PluginArgument] = None,
        examples: list[str] = None,
        help_text: str = "",
        supported_output_formats: list[OutputFormat] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            category=category,
            tool_type=ToolType.ONLINE_SERVICE,
            version=version,
            arguments=arguments,
            examples=examples,
            help_text=help_text,
            supported_output_formats=supported_output_formats,
        )
        self._service_url = service_url
        self._session = None

    @property
    def service_url(self) -> str:
        return self._service_url

    async def execute(
        self,
        arguments: dict[str, Any],
        output_format: str = "text",
    ) -> PluginResult:
        start_time = time.time()
        try:
            result = await self._make_request(arguments)
            execution_time = time.time() - start_time

            parsed = self.parse_output(str(result), output_format)
            return PluginResult(
                success=True,
                data=parsed,
                raw_output=str(result),
                format=output_format,
                execution_time=execution_time,
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e),
                format=output_format,
                execution_time=time.time() - start_time,
            )

    @abstractmethod
    async def _make_request(self, arguments: dict[str, Any]) -> Any:
        pass

    async def _get_session(self):
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None


class APIPlugin(OnlineServicePlugin):
    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        api_endpoint: str,
        api_key_required: bool = False,
        rate_limit: str | None = None,
        version: str = "1.0.0",
        arguments: list[PluginArgument] = None,
        examples: list[str] = None,
        help_text: str = "",
        supported_output_formats: list[OutputFormat] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            category=category,
            service_url=api_endpoint,
            version=version,
            arguments=arguments,
            examples=examples,
            help_text=help_text,
            supported_output_formats=supported_output_formats,
        )
        self._api_endpoint = api_endpoint
        self._api_key_required = api_key_required
        self._rate_limit = rate_limit
        self._api_key: str | None = None

    def set_api_key(self, api_key: str):
        self._api_key = api_key

    async def _make_request(self, arguments: dict[str, Any]) -> Any:
        session = await self._get_session()
        headers = {"Accept": "application/json"}
        if self._api_key_required and self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        url = f"{self._api_endpoint}{self._build_path(arguments)}"
        async with session.get(url, headers=headers, params=self._build_params(arguments)) as response:
            return await response.json()

    def _build_path(self, arguments: dict[str, Any]) -> str:
        return ""

    def _build_params(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return arguments


class FrameworkPlugin(BasePlugin):
    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        framework_name: str,
        entry_point: str,
        version: str = "1.0.0",
        arguments: list[PluginArgument] = None,
        examples: list[str] = None,
        help_text: str = "",
        supported_output_formats: list[OutputFormat] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            category=category,
            tool_type=ToolType.FRAMEWORK,
            version=version,
            arguments=arguments,
            examples=examples,
            help_text=help_text,
            supported_output_formats=supported_output_formats,
        )
        self._framework_name = framework_name
        self._entry_point = entry_point

    async def execute(
        self,
        arguments: dict[str, Any],
        output_format: str = "text",
    ) -> PluginResult:
        start_time = time.time()
        try:
            result = await self._run_framework(arguments)
            execution_time = time.time() - start_time

            parsed = self.parse_output(str(result), output_format)
            return PluginResult(
                success=True,
                data=parsed,
                raw_output=str(result),
                format=output_format,
                execution_time=execution_time,
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e),
                format=output_format,
                execution_time=time.time() - start_time,
            )

    @abstractmethod
    async def _run_framework(self, arguments: dict[str, Any]) -> Any:
        pass