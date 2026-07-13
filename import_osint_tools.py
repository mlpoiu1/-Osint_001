from __future__ import annotations

import re
import sys
from pathlib import Path

from osint_toolkit.config.settings import AppConfig
from osint_toolkit.config.dependencies import create_container
from osint_toolkit.domain.interfaces import IToolRepository
from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.plugin import ToolInfo


CATEGORY_MAP = {
    "whois": ToolCategory.DATA,
    "اطلاعات ip": ToolCategory.NETWORK,
    "dns": ToolCategory.NETWORK,
    "ssl/tls": ToolCategory.DATA,
    "ایمیل": ToolCategory.SEARCH,
    "افراد": ToolCategory.SEARCH,
    "شبکه‌های اجتماعی": ToolCategory.SOCIAL_MEDIA,
    "عکس": ToolCategory.SEARCH,
    "موتورهای جستجوی": ToolCategory.SEARCH,
    "تحلیل وبسایت": ToolCategory.WEB,
    "نشت اطلاعات": ToolCategory.DATA,
    "google dorks": ToolCategory.SEARCH,
    "pastebin": ToolCategory.DATA,
    "دامنه و ip": ToolCategory.NETWORK,
    "ابزارهای خط فرمان": ToolCategory.OTHER,
    "فریم‌ورک‌های جامع": ToolCategory.OTHER,
    "تهدیدات": ToolCategory.VULNERABILITY,
    "نقشه و مکان": ToolCategory.GEOGRAPHIC,
    "دیتاست‌ها": ToolCategory.DATA,
    "افزونه‌های مرورگر": ToolCategory.OTHER,
}

TYPE_MAP = {
    "api": ToolType.API,
    "cli": ToolType.CLI,
    "خط فرمان": ToolType.CLI,
    "extension": ToolType.BROWSER_EXTENSION,
    "افزونه": ToolType.BROWSER_EXTENSION,
    "framework": ToolType.FRAMEWORK,
    "فریم‌ورک": ToolType.FRAMEWORK,
    "online": ToolType.ONLINE_SERVICE,
    "سرویس آنلاین": ToolType.ONLINE_SERVICE,
}


def parse_osint_tools(file_path: str) -> list[ToolInfo]:
    """Parse the osint_tools.txt file and extract tools."""
    content = Path(file_path).read_text(encoding="utf-8")
    tools = []

    # Split by category sections (┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
    sections = re.split(r'┏━+┓', content)

    for section in sections[1:]:  # Skip first empty
        # Extract category name
        cat_match = re.search(r'┃\s+(\d+)\.\s+([^┃]+)┃', section)
        if not cat_match:
            continue

        category_name = cat_match.group(2).strip()
        category_key = category_name.lower().split("—")[0].strip()
        category = CATEGORY_MAP.get(category_key, ToolCategory.OTHER)

        # Extract tools (🔗 lines)
        tool_blocks = re.findall(r'🔗\s+([^\n]+)\n\s+📎\s+([^\n]+)\n\s+📝\s+([^\n]+)', section)

        for name, url, desc in tool_blocks:
            name = name.strip()
            url = url.strip()
            desc = desc.strip()

            # Determine tool type from description
            tool_type = ToolType.ONLINE_SERVICE
            desc_lower = desc.lower()
            for key, ttype in TYPE_MAP.items():
                if key in desc_lower:
                    tool_type = ttype
                    break

            # Generate tags from description
            tags = []
            if "api" in desc_lower:
                tags.append("api")
            if "free" in desc_lower or "رایگان" in desc_lower:
                tags.append("free")
            if "reverse" in desc_lower or "معکوس" in desc_lower:
                tags.append("reverse")
            if "bulk" in desc_lower:
                tags.append("bulk")

            tool = ToolInfo(
                name=name,
                description=desc,
                category=category,
                tool_type=tool_type,
                url=url if url.startswith("http") else None,
                status=ToolStatus.NOT_INSTALLED,
                tags=tags,
            )
            tools.append(tool)

    return tools


async def import_tools():
    config = AppConfig()
    config.database.path = "osint_toolkit.db"
    container = create_container(config)
    repo = container.resolve(IToolRepository)

    file_path = sys.argv[1] if len(sys.argv) > 1 else "osint_tools.txt"
    if not Path(file_path).exists():
        print(f"Error: OSINT tools text file not found at: {file_path}")
        print("Usage: python import_osint_tools.py [path_to_osint_tools.txt]")
        return

    tools = parse_osint_tools(file_path)
    print(f"Parsed {len(tools)} tools from file")

    imported = 0
    skipped = 0
    for tool in tools:
        existing = await repo.get_by_name(tool.name)
        if existing:
            skipped += 1
            continue
        await repo.create(tool)
        imported += 1

    print(f"Imported: {imported}, Skipped: {skipped}")

    # Show category stats
    stats = await repo.count_by_category()
    for cat, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat.value}: {count}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(import_tools())
