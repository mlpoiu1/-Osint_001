from __future__ import annotations

import asyncio
import shutil
from typing import Any

from osint_toolkit.domain.interfaces import ICLIDetector


class CLIDetector(ICLIDetector):
    def __init__(self):
        self._cache: dict[str, tuple[bool, str | None]] = {}

    async def detect(self, command: str) -> tuple[bool, str | None]:
        if command in self._cache:
            return self._cache[command]

        available, version = await self._check_command(command)
        self._cache[command] = (available, version)
        return available, version

    async def _check_command(self, command: str) -> tuple[bool, str | None]:
        if not shutil.which(command):
            return False, None

        version_args = ["--version", "-v", "-V", "version"]
        for arg in version_args:
            try:
                process = await asyncio.create_subprocess_exec(
                    command, arg,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
                if process.returncode == 0:
                    output = stdout.decode("utf-8", errors="replace").strip()
                    if output:
                        return True, output.split("\n")[0]
            except (asyncio.TimeoutError, FileNotFoundError, OSError):
                continue

        return True, None

    async def detect_multiple(self, commands: list[str]) -> dict[str, tuple[bool, str | None]]:
        results = {}
        for cmd in commands:
            results[cmd] = await self.detect(cmd)
        return results

    async def get_version(self, command: str) -> str | None:
        available, version = await self.detect(command)
        return version if available else None

    def clear_cache(self):
        self._cache.clear()