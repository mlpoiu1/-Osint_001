from __future__ import annotations

from osint_terminal.domain.enums import Category, OutputFormat, PluginStatus, ToolType


def test_every_category_has_a_persian_label() -> None:
    for category in Category:
        assert category.label_fa, f"Missing Persian label for {category}"


def test_category_values_are_unique_and_snake_case() -> None:
    values = [c.value for c in Category]
    assert len(values) == len(set(values))
    assert all(v == v.lower() and " " not in v for v in values)


def test_tool_type_covers_required_kinds() -> None:
    names = {t.name for t in ToolType}
    assert {"CLI", "ONLINE_SERVICE", "API_SERVICE", "FRAMEWORK", "BROWSER_EXTENSION"} <= names


def test_plugin_status_covers_required_states() -> None:
    names = {s.name for s in PluginStatus}
    assert {"AVAILABLE", "UNAVAILABLE", "NOT_APPLICABLE", "ERROR"} <= names


def test_output_format_covers_required_formats() -> None:
    names = {f.name for f in OutputFormat}
    assert {"JSON", "MARKDOWN", "HTML", "TEXT"} <= names
