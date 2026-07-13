from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.plugin import ToolInfo, PluginArgument


class OSINTToolParser:
    def __init__(self):
        self.category_map = {
            "geographic": ToolCategory.GEOGRAPHIC,
            "social media": ToolCategory.SOCIAL_MEDIA,
            "search": ToolCategory.SEARCH,
            "data": ToolCategory.DATA,
            "network": ToolCategory.NETWORK,
            "crypto": ToolCategory.CRYPTO,
            "malware": ToolCategory.MALWARE,
            "vulnerability": ToolCategory.VULNERABILITY,
            "password": ToolCategory.PASSWORD,
            "wireless": ToolCategory.WIRELESS,
            "web": ToolCategory.WEB,
            "forensics": ToolCategory.FORENSICS,
            "reporting": ToolCategory.REPORTING,
            "crowdtool": ToolCategory.GEOGRAPHIC,
        }

        self.type_map = {
            "command line": ToolType.CLI,
            "cli": ToolType.CLI,
            "online": ToolType.ONLINE_SERVICE,
            "online service": ToolType.ONLINE_SERVICE,
            "api": ToolType.API,
            "framework": ToolType.FRAMEWORK,
            "browser extension": ToolType.BROWSER_EXTENSION,
            "desktop app": ToolType.DESKTOP_APP,
            "mobile app": ToolType.MOBILE_APP,
            "program": ToolType.DESKTOP_APP,
            "service": ToolType.ONLINE_SERVICE,
            "tool": ToolType.ONLINE_SERVICE,
            "site": ToolType.ONLINE_SERVICE,
            "app": ToolType.ONLINE_SERVICE,
            "plug-in": ToolType.BROWSER_EXTENSION,
        }

    def parse_pdf_text(self, text: str) -> list[ToolInfo]:
        lines = text.strip().split("\n")
        tools = []
        current_tool = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Tool Name") or line.startswith("Type") or line.startswith("Tool URL"):
                continue

            if line.startswith("---"):
                if current_tool:
                    tools.append(current_tool)
                current_tool = None
                continue

            if current_tool is None:
                current_tool = self._create_tool_from_line(line)
            else:
                self._add_description_to_tool(current_tool, line)

        if current_tool:
            tools.append(current_tool)

        return tools

    def _create_tool_from_line(self, line: str) -> ToolInfo | None:
        parts = re.split(r'\s{2,}', line)
        if len(parts) < 2:
            return None

        name = parts[0].strip()
        if not name or name in ("Tool", "Name", "Allows", "Helps", "Offers", "A", "An", "The"):
            return None

        tool_type_str = "online service"
        category_str = "other"

        for part in parts[1:]:
            part_lower = part.lower()
            if part_lower in self.type_map:
                tool_type_str = part_lower
            elif part_lower in self.category_map:
                category_str = part_lower

        tool_type = self.type_map.get(tool_type_str, ToolType.ONLINE_SERVICE)
        category = self.category_map.get(category_str, ToolCategory.OTHER)

        return ToolInfo(
            name=name,
            description="",
            category=category,
            tool_type=tool_type,
            status=ToolStatus.NOT_INSTALLED,
        )

    def _add_description_to_tool(self, tool: ToolInfo, line: str):
        if tool.description:
            tool.description += " " + line
        else:
            tool.description = line

    def parse_structured_data(self, data: list[dict[str, Any]]) -> list[ToolInfo]:
        tools = []
        for item in data:
            tool = self._create_tool_from_dict(item)
            if tool:
                tools.append(tool)
        return tools

    def _create_tool_from_dict(self, data: dict[str, Any]) -> ToolInfo | None:
        name = data.get("Tool Name") or data.get("name") or data.get("tool_name")
        if not name:
            return None

        tool_type_str = (data.get("Type") or data.get("type") or "online service").lower()
        category_str = (data.get("Category") or data.get("category") or "other").lower()

        tool_type = self.type_map.get(tool_type_str, ToolType.ONLINE_SERVICE)
        category = self.category_map.get(category_str, ToolCategory.OTHER)

        url = data.get("Tool URL") or data.get("url")
        description = data.get("Description") or data.get("description") or ""
        tutorial = data.get("Tutorial") or data.get("tutorial")

        return ToolInfo(
            name=name,
            description=description,
            category=category,
            tool_type=tool_type,
            url=url,
            tutorial_url=tutorial,
            status=ToolStatus.NOT_INSTALLED,
        )

    def get_predefined_osint_tools(self) -> list[ToolInfo]:
        tools = [
            ToolInfo(
                name="ShadowMap",
                description="View shadows cast by buildings anywhere in the world and simulate where those shadows will fall at any time. Useful for figuring out the location of photos and videos in dense urban areas.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://app.shadowmap.org",
                status=ToolStatus.NOT_INSTALLED,
                tags=["geolocation", "shadows", "urban"],
            ),
            ToolInfo(
                name="TGStat",
                description="Search for Telegram channels by country, explore channels by category, and check channel and group ratings. Useful for researching specific niche topics on Telegram.",
                category=ToolCategory.SOCIAL_MEDIA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://tgstat.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["telegram", "channels", "social media"],
            ),
            ToolInfo(
                name="What's My Name App",
                description="Find out what social media platforms someone is using by entering a username. You can filter results and export URLs.",
                category=ToolCategory.SOCIAL_MEDIA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://whatsmyname.app/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["username", "social media", "osint"],
            ),
            ToolInfo(
                name="Search4Faces",
                description="Reverse face search engine across several platforms.",
                category=ToolCategory.SEARCH,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://search4faces.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["face search", "reverse image"],
            ),
            ToolInfo(
                name="PimEyes",
                description="A mix of free and paid service that provides alternative images of a person's face.",
                category=ToolCategory.SEARCH,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://pimeyes.com/en",
                status=ToolStatus.NOT_INSTALLED,
                tags=["face recognition", "facial recognition"],
            ),
            ToolInfo(
                name="GeoGuesser",
                description="A Chat GPT based app that suggests the location of an image after you upload it.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://chatgpt.com/g/g-CJ",
                status=ToolStatus.NOT_INSTALLED,
                tags=["geolocation", "ai", "image analysis"],
            ),
            ToolInfo(
                name="Google Earth Pro",
                description="A free downloadable program that allows you to view clear historical satellite imagery for anywhere in the world.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.DESKTOP_APP,
                url="https://earth.google.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["satellite", "historical imagery", "geolocation"],
            ),
            ToolInfo(
                name="YouTube GeoFind",
                description="Find geotagged YouTube videos uploaded from a specific location.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://mattw.io/youtube-geo",
                status=ToolStatus.NOT_INSTALLED,
                tags=["youtube", "geotagged", "video"],
            ),
            ToolInfo(
                name="GetDayTrends",
                description="Find out what the top trending tags are on Twitter (now called X) for any time and any location around the world.",
                category=ToolCategory.SOCIAL_MEDIA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://getdaytrends.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["twitter", "trends", "hashtags"],
            ),
            ToolInfo(
                name="Google Image Reverse Search",
                description="Upload an image to get more context, see where it's been posted, or find other versions of it online.",
                category=ToolCategory.SEARCH,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://lens.google/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["reverse image", "google", "search"],
            ),
            ToolInfo(
                name="Search by Image",
                description="A Chrome plug-in that lets you search multiple platforms in one click.",
                category=ToolCategory.SEARCH,
                tool_type=ToolType.BROWSER_EXTENSION,
                url="https://chromewebstore.google.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["chrome", "extension", "reverse image"],
            ),
            ToolInfo(
                name="Redective",
                description="Check out the stats of a Reddit group or a user's most commonly used words or active hours.",
                category=ToolCategory.SOCIAL_MEDIA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://www.redective.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["reddit", "analytics", "user stats"],
            ),
            ToolInfo(
                name="Untappd Scraper",
                description="Scrape data from Untappd - the platform where you can find out how much beer people are drinking in your area.",
                category=ToolCategory.DATA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://brandone.github.io/untappd-scraper/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["untappd", "scraper", "beer"],
            ),
            ToolInfo(
                name="Google Dorks",
                description="A method to search on Google for particular files like PDFs, documents or spreadsheets, even on a specific website.",
                category=ToolCategory.SEARCH,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://www.recordedfuture.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["google dorks", "search operators"],
            ),
            ToolInfo(
                name="MapChecking CrowdTool",
                description="Estimate the maximum number of people that can fit in a given area.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://www.mapchecking.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["crowd estimation", "area"],
            ),
            ToolInfo(
                name="Flight Radar 24",
                description="Flight tracking that allows you to see what's flying overhead, including the aircraft model, where it's coming from, and where it's going.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://www.flightradar24.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["flight tracking", "aircraft", "aviation"],
            ),
            ToolInfo(
                name="Wayback Machine",
                description="View deleted websites and posts. Search through screenshots made every day.",
                category=ToolCategory.DATA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://archive.org/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["web archive", "deleted content", "history"],
            ),
            ToolInfo(
                name="Jimpl",
                description="An online EXIF or metadata viewer.",
                category=ToolCategory.DATA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://jimpl.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["exif", "metadata", "image"],
            ),
            ToolInfo(
                name="Pixel Keeper",
                description="Reveals camera model and date using EXIF data.",
                category=ToolCategory.DATA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://pixelpeeper.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["exif", "camera", "photography"],
            ),
            ToolInfo(
                name="ExifTool",
                description="A command line tool that reveals hidden data attached to an image.",
                category=ToolCategory.DATA,
                tool_type=ToolType.CLI,
                cli_command="exiftool",
                url="https://exiftool.org/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["exif", "metadata", "cli"],
                metadata={"check_installed": True},
            ),
            ToolInfo(
                name="Overpass Turbo",
                description="Query the OpenStreetMap database to create your own map.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://overpass-turbo.eu/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["openstreetmap", "query", "mapping"],
            ),
            ToolInfo(
                name="Live UA Map",
                description="Collects maps and events happening around the world every day. Useful for tracking major global news events.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://liveuamap.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["news", "events", "map", "live"],
            ),
            ToolInfo(
                name="Open Infrastructure Map",
                description="Find key infrastructure in one publicly available map. Helpful for geolocation tasks.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://openinframap.org/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["infrastructure", "mapping", "geolocation"],
            ),
            ToolInfo(
                name="Who Posted What?",
                description="Find out what was uploaded to Facebook on one specific date.",
                category=ToolCategory.SOCIAL_MEDIA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://whopostedwhat.com/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["facebook", "posts", "date"],
            ),
            ToolInfo(
                name="Open Measures",
                description="Track trends on platforms like Telegram, TikTok, VK, and more.",
                category=ToolCategory.SOCIAL_MEDIA,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://public.openmeasures.io/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["trends", "telegram", "tiktok", "analytics"],
            ),
            ToolInfo(
                name="Carnet AI",
                description="An AI tool that allows you to upload an image and identify the car model.",
                category=ToolCategory.SEARCH,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://carnet.ai/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["car recognition", "ai", "vehicle"],
            ),
            ToolInfo(
                name="Suncalc",
                description="Calculate the time based on the angle of shadows.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://www.suncalc.org/",
                status=ToolStatus.NOT_INSTALLED,
                tags=["sun", "shadows", "time calculation"],
            ),
            ToolInfo(
                name="Google Street View",
                description="See what an area looked like in the past using old Google Street View images.",
                category=ToolCategory.GEOGRAPHIC,
                tool_type=ToolType.ONLINE_SERVICE,
                url="https://www.google.co.uk/maps",
                status=ToolStatus.NOT_INSTALLED,
                tags=["street view", "historical", "geolocation"],
            ),
        ]
        return tools


async def import_osint_tools(repository, tools: list[ToolInfo]) -> dict[str, int]:
    results = {"imported": 0, "skipped": 0, "errors": 0}
    for tool in tools:
        try:
            existing = await repository.get_by_name(tool.name)
            if existing:
                results["skipped"] += 1
                continue
            await repository.create(tool)
            results["imported"] += 1
        except Exception as e:
            results["errors"] += 1
            print(f"Error importing {tool.name}: {e}")
    return results