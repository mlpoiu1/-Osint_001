from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from osint_terminal.domain.entities import (
    Argument,
    ExecutionResult,
    PluginId,
    PluginMetadata,
    PluginState,
)
from osint_terminal.domain.enums import Category, OutputFormat, PluginStatus, ToolType


def make_metadata(**overrides) -> PluginMetadata:
    defaults: dict = dict(
        plugin_id=PluginId("whois.whoxy"),
        name="Whoxy",
        description="WHOIS with free API and reverse whois lookup.",
        category=Category.WHOIS,
        tool_type=ToolType.API_SERVICE,
        arguments=(Argument(name="domain", description="Target domain", required=True, flag="-d"),),
        example="whoxy -d example.com",
        help_text="Query WHOIS data for a domain via the Whoxy API.",
        output_parser="whois_text",
        supported_output_formats=(OutputFormat.JSON, OutputFormat.TEXT),
        homepage="https://www.whoxy.com",
    )
    defaults.update(overrides)
    return PluginMetadata(**defaults)


class TestPluginId:
    def test_valid_id(self) -> None:
        assert str(PluginId("dns_recon.amass")) == "dns_recon.amass"

    @pytest.mark.parametrize("bad", ["", "has space", " "])
    def test_rejects_invalid(self, bad: str) -> None:
        with pytest.raises(ValueError):
            PluginId(bad)


class TestArgument:
    def test_requires_name(self) -> None:
        with pytest.raises(ValueError):
            Argument(name="", description="x")

    def test_defaults(self) -> None:
        arg = Argument(name="timeout", description="seconds")
        assert arg.required is False
        assert arg.default is None
        assert arg.flag is None


class TestPluginMetadata:
    def test_requires_local_binary_true_for_cli_with_binary(self) -> None:
        meta = make_metadata(tool_type=ToolType.CLI, binary_name="amass")
        assert meta.requires_local_binary() is True

    def test_requires_local_binary_false_for_online_service(self) -> None:
        meta = make_metadata(tool_type=ToolType.ONLINE_SERVICE, binary_name=None)
        assert meta.requires_local_binary() is False

    def test_requires_local_binary_false_when_cli_but_no_binary_name(self) -> None:
        meta = make_metadata(tool_type=ToolType.CLI, binary_name=None)
        assert meta.requires_local_binary() is False


class TestPluginState:
    def test_defaults_to_not_applicable(self) -> None:
        state = PluginState(plugin_id=PluginId("dns_recon.amass"))
        assert state.status is PluginStatus.NOT_APPLICABLE
        assert state.is_favorite is False
        assert state.run_count == 0


class TestExecutionResult:
    def test_duration_seconds(self) -> None:
        start = datetime(2026, 1, 1, 12, 0, 0)
        end = start + timedelta(seconds=3, milliseconds=500)
        result = ExecutionResult(
            plugin_id=PluginId("dns_recon.amass"),
            started_at=start,
            finished_at=end,
            exit_code=0,
            raw_output="ok",
        )
        assert result.duration_seconds == pytest.approx(3.5)

    def test_defaults(self) -> None:
        now = datetime.now()
        result = ExecutionResult(
            plugin_id=PluginId("whois.whoxy"),
            started_at=now,
            finished_at=now,
            exit_code=0,
            raw_output="",
        )
        assert result.success is True
        assert result.error_message is None
