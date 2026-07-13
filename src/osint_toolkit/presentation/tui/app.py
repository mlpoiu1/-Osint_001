from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.widgets.tree import TreeNode
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.worker import get_current_worker

from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.plugin import ToolInfo


class ToolSelected(Message):
    def __init__(self, tool: ToolInfo):
        self.tool = tool
        super().__init__()


class ToolExecuteRequested(Message):
    def __init__(self, tool_name: str, arguments: dict[str, Any]):
        self.tool_name = tool_name
        self.arguments = arguments
        super().__init__()


class SearchRequest(Message):
    def __init__(self, query: str):
        self.query = query
        super().__init__()


class FuzzySearchRequest(Message):
    def __init__(self, query: str):
        self.query = query
        super().__init__()


class ReportRequest(Message):
    def __init__(self, format: str, output_path: str, category: ToolCategory | None = None):
        self.format = format
        self.output_path = output_path
        self.category = category
        super().__init__()


class ToolTable(DataTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_columns("Name", "Category", "Type", "Status", "Description")
        self.cursor_type = "row"

    def populate_tools(self, tools: list[ToolInfo]):
        self.clear()
        for tool in tools:
            self.add_row(
                tool.name,
                tool.category.value,
                tool.tool_type.value,
                tool.status.value,
                tool.description[:80] + "..." if len(tool.description) > 80 else tool.description,
                key=tool.name,
            )


class ToolDetailPanel(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_tool: ToolInfo | None = None
        self.can_focus = True

    def show_tool(self, tool: ToolInfo):
        self.current_tool = tool
        lines = [
            f"[bold]{tool.name}[/bold]",
            f"[dim]{tool.description}[/dim]",
            "",
            f"Category: [cyan]{tool.category.value}[/cyan]",
            f"Type: [green]{tool.tool_type.value}[/green]",
            f"Status: [yellow]{tool.status.value}[/yellow]",
        ]
        if tool.version:
            lines.append(f"Version: {tool.version}")
        if tool.cli_command:
            lines.append(f"CLI Command: [bold]{tool.cli_command}[/bold]")
        if tool.url:
            lines.append(f"URL: [link]{tool.url}[/link]")
        if tool.api_endpoint:
            lines.append(f"API Endpoint: {tool.api_endpoint}")
        if tool.tags:
            lines.append(f"Tags: {', '.join(tool.tags)}")
        if tool.examples:
            lines.append("")
            lines.append("[bold]Examples:[/bold]")
            for ex in tool.examples[:3]:
                lines.append(f"  {ex}")

        self.update("\n".join(lines))

    def clear(self):
        self.current_tool = None
        self.update("[dim]Select a tool to view details[/dim]")


class CategoryTree(Tree):
    def __init__(self, *args, **kwargs):
        super().__init__("Categories", *args, **kwargs)
        self.show_root = True

    def populate_categories(self, tools: list[ToolInfo]):
        self.clear()
        root = self.root
        categories = {}
        for tool in tools:
            cat = tool.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool)

        for cat, cat_tools in sorted(categories.items(), key=lambda x: x[0].value):
            cat_node = root.add(f"{cat.value} ({len(cat_tools)})", data=cat)
            cat_node.expand()
            for tool in sorted(cat_tools, key=lambda t: t.name):
                cat_node.add_leaf(f"  {tool.name}", data=tool)


class SearchInput(Input):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, placeholder="Search tools... (fuzzy search)", **kwargs)

    async def on_input_changed(self, event: Input.Changed) -> None:
        self.post_message(SearchRequest(event.value))


class CommandPalette(ModalScreen):
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "select", "Select"),
    ]

    def __init__(self, tools: list[ToolInfo], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tools = tools
        self.filtered_tools = tools

    def compose(self) -> ComposeResult:
        with Container(id="command-palette"):
            yield Input(placeholder="Type command or tool name...", id="cmd-input")
            yield ListView(id="cmd-results")

    def on_mount(self) -> None:
        self.query_one("#cmd-input").focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        self.filtered_tools = [
            t for t in self.tools
            if query in t.name.lower() or query in t.description.lower()
        ][:20]

        results = self.query_one("#cmd-results")
        results.clear()
        for tool in self.filtered_tools:
            results.append(ListItem(Label(f"{tool.name} - {tool.description[:60]}")))

    def action_select(self) -> None:
        results = self.query_one("#cmd-results")
        if results.highlighted_child:
            index = results.index(results.highlighted_child)
            if index < len(self.filtered_tools):
                tool = self.filtered_tools[index]
                self.dismiss(tool)

    def action_close(self) -> None:
        self.dismiss(None)


class ExecuteToolModal(ModalScreen):
    def __init__(self, tool: ToolInfo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool = tool

    def compose(self) -> ComposeResult:
        with Container(id="execute-modal"):
            yield Label(f"Execute: {self.tool.name}", id="modal-title")
            yield VerticalScroll(id="args-container")
            with Horizontal(id="modal-buttons"):
                yield Button("Execute", variant="primary", id="execute-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        container = self.query_one("#args-container")
        for arg in self.tool.arguments:
            arg_name = arg.get("name", "")
            arg_desc = arg.get("description", "")
            arg_required = arg.get("required", False)
            arg_default = arg.get("default", "")
            label = f"{arg_name}{'*' if arg_required else ''}: {arg_desc}"
            container.mount(Input(placeholder=label, id=f"arg-{arg_name}", value=str(arg_default) if arg_default else ""))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "execute-btn":
            arguments = {}
            container = self.query_one("#args-container")
            for arg in self.tool.arguments:
                arg_name = arg.get("name", "")
                input_widget = container.query_one(f"#arg-{arg_name}", Input)
                if input_widget.value:
                    arguments[arg_name] = input_widget.value
            self.dismiss(arguments)
        elif event.button.id == "cancel-btn":
            self.dismiss(None)


class OSINTToolkitApp(App):
    TITLE = "OSINT Toolkit"
    CSS_PATH = "osint_toolkit.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+p", "command_palette", "Command Palette"),
        Binding("ctrl+f", "focus_search", "Search"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+e", "execute", "Execute Tool"),
        Binding("ctrl+o", "open_url", "Open URL"),
        Binding("ctrl+j", "toggle_json", "JSON Export"),
        Binding("ctrl+h", "toggle_html", "HTML Report"),
        Binding("ctrl+m", "toggle_markdown", "Markdown Report"),
        Binding("f1", "help", "Help"),
    ]

    tools: reactive[list[ToolInfo]] = reactive([])

    def __init__(self, tool_repository=None, plugin_registry=None, search_service=None, report_generator=None, cli_detector=None, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tool_repository = tool_repository
        self._plugin_registry = plugin_registry
        self._search_service = search_service
        self._report_generator = report_generator
        self._cli_detector = cli_detector
        self._config = config

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield CategoryTree(id="category-tree")
            with Vertical(id="main-content"):
                with TabbedContent(id="main-tabs"):
                    with TabPane("Dashboard", id="dashboard-tab"):
                        yield ToolTable(id="tool-table")
                    with TabPane("Details", id="details-tab"):
                        yield ToolDetailPanel(id="tool-detail")
        yield SearchInput(id="search-input")
        yield Footer()

    async def on_mount(self) -> None:
        await self.load_tools()

    async def load_tools(self):
        if self._tool_repository:
            self.tools = await self._tool_repository.get_all()
        else:
            self.tools = []

        table = self.query_one("#tool-table", ToolTable)
        table.populate_tools(self.tools)

        tree = self.query_one("#category-tree", CategoryTree)
        tree.populate_categories(self.tools)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        tool_name = event.row_key.value
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if tool:
            detail = self.query_one("#tool-detail", ToolDetailPanel)
            detail.show_tool(tool)
            self.query_one("#main-tabs").active = "details-tab"

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data and isinstance(event.node.data, ToolInfo):
            tool = event.node.data
            table = self.query_one("#tool-table", ToolTable)
            # Find row index by iterating
            for row_index in range(table.row_count):
                row_key = table.get_row_at(row_index)
                if row_key and row_key[0] == tool.name:
                    table.move_cursor(row=row_index)
                    break
            detail = self.query_one("#tool-detail", ToolDetailPanel)
            detail.show_tool(tool)

    def on_search_request(self, event: SearchRequest) -> None:
        query = event.query
        if query:
            filtered = [t for t in self.tools if query.lower() in t.name.lower() or query.lower() in t.description.lower()]
        else:
            filtered = self.tools

        table = self.query_one("#tool-table", ToolTable)
        table.populate_tools(filtered)

    async def action_command_palette(self) -> None:
        def callback(tool):
            if tool:
                detail = self.query_one("#tool-detail", ToolDetailPanel)
                detail.show_tool(tool)
                self.query_one("#main-tabs").active = "details-tab"

        self.run_worker(self._command_palette_worker(callback), exclusive=True)

    async def _command_palette_worker(self, callback) -> None:
        palette = CommandPalette(self.tools)
        tool = await self.push_screen(palette)
        callback(tool)

    async def action_execute(self) -> None:
        table = self.query_one("#tool-table", ToolTable)
        if table.cursor_row >= 0:
            row_key = table.get_row_at(table.cursor_row)[0]
            tool = next((t for t in self.tools if t.name == row_key), None)
            if tool:
                modal = ExecuteToolModal(tool)
                self.run_worker(self._execute_modal_worker(tool, modal), exclusive=True)

    async def _execute_modal_worker(self, tool, modal) -> None:
        arguments = await self.push_screen(modal)
        if arguments:
            self.post_message(ToolExecuteRequested(tool.name, arguments))

    async def action_focus_search(self) -> None:
        self.query_one("#search-input", SearchInput).focus()

    async def action_open_url(self) -> None:
        import webbrowser
        # Get currently selected tool from table
        table = self.query_one("#tool-table", ToolTable)
        if table.cursor_row >= 0:
            row_key = table.get_row_at(table.cursor_row)
            if row_key:
                tool_name = row_key[0]
                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool and tool.url:
                    webbrowser.open(tool.url)
                    self.notify(f"Opened: {tool.url}")
                    return
        # Fallback: check detail panel
        detail = self.query_one("#tool-detail", ToolDetailPanel)
        if detail.current_tool and detail.current_tool.url:
            webbrowser.open(detail.current_tool.url)
            self.notify(f"Opened: {detail.current_tool.url}")
            return
        self.notify("No URL available for selected tool")

    async def action_refresh(self) -> None:
        await self.load_tools()
        self.notify("Tools refreshed")

    async def action_toggle_json(self) -> None:
        from datetime import datetime
        output_path = f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.post_message(ReportRequest("json", output_path))
        self.notify(f"JSON report requested: {output_path}")

    async def action_toggle_html(self) -> None:
        from datetime import datetime
        output_path = f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self.post_message(ReportRequest("html", output_path))
        self.notify(f"HTML report requested: {output_path}")

    async def action_toggle_markdown(self) -> None:
        from datetime import datetime
        output_path = f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self.post_message(ReportRequest("markdown", output_path))
        self.notify(f"Markdown report requested: {output_path}")

    async def action_help(self) -> None:
        help_text = """
OSINT Toolkit - Keyboard Shortcuts:
  Ctrl+Q  - Quit
  Ctrl+P  - Command Palette
  Ctrl+F  - Focus Search
  Ctrl+R  - Refresh Tools
  Ctrl+E  - Execute Selected Tool
  Ctrl+J  - JSON Export
  Ctrl+H  - HTML Report
  Ctrl+M  - Markdown Report
  F1      - This Help

Navigation:
  ↑/↓     - Navigate tool list
  Enter   - Select tool
  Tab     - Switch panels
"""
        self.notify(help_text, title="Help", timeout=10)