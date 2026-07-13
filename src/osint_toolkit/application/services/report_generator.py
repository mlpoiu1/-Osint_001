from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from osint_toolkit.domain.interfaces import IReportGenerator
from osint_toolkit.domain.models.plugin import ToolInfo


class ReportGenerator(IReportGenerator):
    async def generate_json(self, tools: list[ToolInfo], output_path: str) -> None:
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_tools": len(tools),
            "tools": [tool.to_dict() for tool in tools],
        }
        Path(output_path).write_text(json.dumps(data, indent=2, ensure_ascii=False))

    async def generate_html(self, tools: list[ToolInfo], output_path: str, template: str | None = None) -> None:
        html = self._build_html(tools, template)
        Path(output_path).write_text(html)

    async def generate_markdown(self, tools: list[ToolInfo], output_path: str) -> None:
        lines = [
            f"# OSINT Tools Report",
            f"",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Tools: {len(tools)}",
            f"",
            f"---",
            f"",
        ]

        by_category = {}
        for tool in tools:
            cat = tool.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)

        for category in sorted(by_category.keys()):
            lines.append(f"## {category.title()}")
            lines.append(f"")
            for tool in by_category[category]:
                lines.append(f"### {tool.name}")
                lines.append(f"")
                lines.append(f"**Description:** {tool.description}")
                lines.append(f"")
                lines.append(f"**Type:** {tool.tool_type.value}")
                if tool.cli_command:
                    lines.append(f"**CLI Command:** `{tool.cli_command}`")
                if tool.url:
                    lines.append(f"**URL:** {tool.url}")
                if tool.api_endpoint:
                    lines.append(f"**API Endpoint:** {tool.api_endpoint}")
                if tool.tags:
                    lines.append(f"**Tags:** {', '.join(tool.tags)}")
                lines.append(f"**Status:** {tool.status.value}")
                if tool.installed_version:
                    lines.append(f"**Installed Version:** {tool.installed_version}")
                if tool.examples:
                    lines.append(f"**Examples:**")
                    for ex in tool.examples:
                        lines.append(f"  - `{ex}`")
                lines.append(f"")
                lines.append(f"---")
                lines.append(f"")

        Path(output_path).write_text("\n".join(lines))

    def _build_html(self, tools: list[ToolInfo], template: str | None = None) -> str:
        if template and Path(template).exists():
            return Path(template).read_text().format(tools_json=json.dumps([t.to_dict() for t in tools]))

        by_category = {}
        for tool in tools:
            cat = tool.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)

        cards = []
        for category in sorted(by_category.keys()):
            cards.append(f'<div class="category"><h2>{category.title()}</h2>')
            for tool in by_category[category]:
                status_class = tool.status.value.replace("_", "-")
                cards.append(f"""
                <div class="tool-card {status_class}">
                    <h3>{tool.name}</h3>
                    <p class="description">{tool.description}</p>
                    <div class="meta">
                        <span class="type">{tool.tool_type.value}</span>
                        <span class="status {status_class}">{tool.status.value}</span>
                    </div>
                    {f'<p class="url"><a href="{tool.url}" target="_blank">{tool.url}</a></p>' if tool.url else ''}
                    {f'<p class="cli"><code>{tool.cli_command}</code></p>' if tool.cli_command else ''}
                    {f'<p class="tags">Tags: {", ".join(tool.tags)}</p>' if tool.tags else ''}
                    {f'<p class="version">Installed: {tool.installed_version}</p>' if tool.installed_version else ''}
                </div>
                """)
            cards.append('</div>')

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Tools Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #eee; }}
        h1 {{ color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px; }}
        .category {{ margin-bottom: 30px; }}
        .category h2 {{ color: #ff6b6b; border-left: 4px solid #ff6b6b; padding-left: 10px; }}
        .tool-card {{ background: #16213e; border-radius: 8px; padding: 15px; margin: 10px 0; border-left: 4px solid #00d9ff; }}
        .tool-card h3 {{ margin-top: 0; color: #fff; }}
        .description {{ color: #aaa; margin: 10px 0; }}
        .meta {{ display: flex; gap: 10px; margin: 10px 0; }}
        .type {{ background: #0f3460; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }}
        .status {{ padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }}
        .status.installed {{ background: #00ff88; color: #000; }}
        .status.not-installed {{ background: #ff6b6b; color: #fff; }}
        .status.available {{ background: #ffd93d; color: #000; }}
        .url a {{ color: #00d9ff; }}
        .cli code {{ background: #0f3460; padding: 2px 6px; border-radius: 4px; color: #00d9ff; }}
        .tags {{ color: #888; font-size: 0.9em; }}
        .version {{ color: #00ff88; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>OSINT Tools Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total Tools: {len(tools)}</p>
    {"".join(cards)}
</body>
</html>
"""