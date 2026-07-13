from __future__ import annotations

import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from osint_toolkit.domain.interfaces import IToolRepository, ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.plugin import ToolInfo


class SQLiteToolRepository(IToolRepository):
    def __init__(self, db_path: str = "osint_toolkit.db"):
        self._db_path = db_path
        self._initialized = False

    async def _initialize(self):
        if self._initialized:
            return

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tools (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tool_type TEXT NOT NULL,
                    cli_command TEXT,
                    url TEXT,
                    api_endpoint TEXT,
                    tutorial_url TEXT,
                    version TEXT DEFAULT '1.0.0',
                    author TEXT DEFAULT 'OSINT Toolkit',
                    license TEXT DEFAULT 'MIT',
                    tags TEXT DEFAULT '[]',
                    arguments TEXT DEFAULT '[]',
                    examples TEXT DEFAULT '[]',
                    help_text TEXT DEFAULT '',
                    supported_output_formats TEXT DEFAULT '["text", "json"]',
                    status TEXT DEFAULT 'not_installed',
                    installed_version TEXT,
                    last_checked TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tools_type ON tools(tool_type)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tools_name ON tools(name)
            """)
            await db.commit()

        self._initialized = True

    def _row_to_tool(self, row: tuple) -> ToolInfo:
        return ToolInfo(
            name=row[0],
            description=row[1],
            category=ToolCategory(row[2]),
            tool_type=ToolType(row[3]),
            cli_command=row[4],
            url=row[5],
            api_endpoint=row[6],
            tutorial_url=row[7],
            version=row[8],
            author=row[9],
            license=row[10],
            tags=json.loads(row[11]),
            arguments=json.loads(row[12]),
            examples=json.loads(row[13]),
            help_text=row[14],
            supported_output_formats=json.loads(row[15]),
            status=ToolStatus(row[16]),
            installed_version=row[17],
            last_checked=datetime.fromisoformat(row[18]) if row[18] else None,
            created_at=datetime.fromisoformat(row[19]),
            updated_at=datetime.fromisoformat(row[20]),
        )

    async def get_all(self) -> list[ToolInfo]:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT * FROM tools ORDER BY name") as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_tool(row) for row in rows]

    async def get_by_id(self, tool_id: str) -> ToolInfo | None:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT * FROM tools WHERE name = ?", (tool_id,)) as cursor:
                row = await cursor.fetchone()
                return self._row_to_tool(row) if row else None

    async def get_by_name(self, name: str) -> ToolInfo | None:
        return await self.get_by_id(name)

    async def get_by_category(self, category: ToolCategory) -> list[ToolInfo]:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT * FROM tools WHERE category = ? ORDER BY name", (category.value,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_tool(row) for row in rows]

    async def get_by_type(self, tool_type: ToolType) -> list[ToolInfo]:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT * FROM tools WHERE tool_type = ? ORDER BY name", (tool_type.value,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_tool(row) for row in rows]

    async def get_available(self) -> list[ToolInfo]:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT * FROM tools WHERE status = ? ORDER BY name", (ToolStatus.AVAILABLE.value,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_tool(row) for row in rows]

    async def get_installed(self) -> list[ToolInfo]:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT * FROM tools WHERE status = ? ORDER BY name", (ToolStatus.INSTALLED.value,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_tool(row) for row in rows]

    async def get_by_status(self, status: ToolStatus) -> list[ToolInfo]:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT * FROM tools WHERE status = ? ORDER BY name", (status.value,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_tool(row) for row in rows]

    async def create(self, tool: ToolInfo) -> ToolInfo:
        await self._initialize()
        now = datetime.now().isoformat()
        tool.created_at = datetime.now()
        tool.updated_at = datetime.now()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                INSERT INTO tools (
                    name, description, category, tool_type, cli_command, url, api_endpoint,
                    tutorial_url, version, author, license, tags, arguments, examples,
                    help_text, supported_output_formats, status, installed_version,
                    last_checked, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tool.name, tool.description, tool.category.value, tool.tool_type.value,
                tool.cli_command, tool.url, tool.api_endpoint, tool.tutorial_url,
                tool.version, tool.author, tool.license,
                json.dumps(tool.tags), json.dumps(tool.arguments), json.dumps(tool.examples),
                tool.help_text, json.dumps(tool.supported_output_formats),
                tool.status.value, tool.installed_version, tool.last_checked.isoformat() if tool.last_checked else None,
                now, now
            ))
            await db.commit()

        return tool

    async def update(self, tool: ToolInfo) -> ToolInfo:
        await self._initialize()
        tool.updated_at = datetime.now()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                UPDATE tools SET
                    description = ?, category = ?, tool_type = ?, cli_command = ?, url = ?,
                    api_endpoint = ?, tutorial_url = ?, version = ?, author = ?, license = ?,
                    tags = ?, arguments = ?, examples = ?, help_text = ?,
                    supported_output_formats = ?, status = ?, installed_version = ?,
                    last_checked = ?, updated_at = ?
                WHERE name = ?
            """, (
                tool.description, tool.category.value, tool.tool_type.value,
                tool.cli_command, tool.url, tool.api_endpoint, tool.tutorial_url,
                tool.version, tool.author, tool.license,
                json.dumps(tool.tags), json.dumps(tool.arguments), json.dumps(tool.examples),
                tool.help_text, json.dumps(tool.supported_output_formats),
                tool.status.value, tool.installed_version,
                tool.last_checked.isoformat() if tool.last_checked else None,
                tool.updated_at.isoformat(), tool.name
            ))
            await db.commit()

        return tool

    async def update_status(self, tool_id: str, status: ToolStatus, version: str | None = None) -> bool:
        await self._initialize()
        tool = await self.get_by_id(tool_id)
        if not tool:
            return False

        tool.status = status
        if version:
            tool.installed_version = version
        tool.last_checked = datetime.now()

        return await self.update(tool) is not None

    async def delete(self, tool_id: str) -> bool:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute("DELETE FROM tools WHERE name = ?", (tool_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def exists(self, tool_id: str) -> bool:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT 1 FROM tools WHERE name = ?", (tool_id,)) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def save(self, tool: ToolInfo) -> ToolInfo:
        existing = await self.get_by_id(tool.name)
        if existing:
            return await self.update(tool)
        return await self.create(tool)

    async def count(self) -> int:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM tools") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def count_by_category(self) -> dict[ToolCategory, int]:
        await self._initialize()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT category, COUNT(*) FROM tools GROUP BY category") as cursor:
                rows = await cursor.fetchall()
                return {ToolCategory(row[0]): row[1] for row in rows}

    async def search(self, query: str, limit: int = 20) -> list[ToolInfo]:
        await self._initialize()
        query_lower = f"%{query.lower()}%"
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("""
                SELECT * FROM tools
                WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?
                ORDER BY name
                LIMIT ?
            """, (query_lower, query_lower, limit)) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_tool(row) for row in rows]


class SQLitePluginMetadataRepository:
    def __init__(self, db_path: str = "osint_toolkit.db"):
        self._db_path = db_path
        self._initialized = False

    async def _initialize(self):
        if self._initialized:
            return

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS plugin_metadata (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tool_type TEXT NOT NULL,
                    version TEXT DEFAULT '1.0.0',
                    author TEXT DEFAULT 'OSINT Toolkit',
                    license TEXT DEFAULT 'MIT',
                    homepage TEXT DEFAULT '',
                    repository TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    arguments TEXT DEFAULT '[]',
                    examples TEXT DEFAULT '[]',
                    help_text TEXT DEFAULT '',
                    supported_output_formats TEXT DEFAULT '[]',
                    dependencies TEXT DEFAULT '[]',
                    cli_command TEXT,
                    api_endpoint TEXT,
                    api_key_required INTEGER DEFAULT 0,
                    rate_limit TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.commit()

        self._initialized = True