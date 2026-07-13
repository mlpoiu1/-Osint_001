from __future__ import annotations

import asyncio
from pathlib import Path

from osint_toolkit.config.dependencies import create_container
from osint_toolkit.config.settings import AppConfig
from osint_toolkit.domain.interfaces import IToolRepository
from osint_toolkit.infrastructure.di.container import ServiceContainer
from osint_toolkit.domain.models.enums import ToolCategory, ToolType, ToolStatus
from osint_toolkit.domain.models.plugin import ToolInfo
from osint_toolkit.presentation.tui.app import OSINTToolkitApp


async def initialize_database(container: ServiceContainer):
    repo = container.resolve(IToolRepository)

    predefined_tools = [
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
            description="Offers a reverse face search engine across several platforms.",
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
            tags=["crowd estimation", "map", "geolocation"],
        ),
        ToolInfo(
            name="Flight Radar 24",
            description="A tool for flight tracking that allows you to see what's flying overhead, including the aircraft model, where it's coming from, and where it's going.",
            category=ToolCategory.GEOGRAPHIC,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://www.flightradar24.com/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["flight tracking", "aircraft", "aviation"],
        ),
        ToolInfo(
            name="Wayback Machine",
            description="A service that allows you to view deleted websites and posts. You can search through screenshots made every day.",
            category=ToolCategory.DATA,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://archive.org/details/tv",
            status=ToolStatus.NOT_INSTALLED,
            tags=["web archive", "deleted content", "history"],
        ),
        ToolInfo(
            name="Jimpl",
            description="An online exif or metadata viewer.",
            category=ToolCategory.DATA,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://jimpl.com/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["exif", "metadata", "image analysis"],
        ),
        ToolInfo(
            name="Pixel Keeper",
            description="A tool that reveals camera model and date using exif data.",
            category=ToolCategory.DATA,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://pixelpeeper.com/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["exif", "camera", "photo metadata"],
        ),
        ToolInfo(
            name="ExifTool",
            description="A command line tool that reveals hidden data attached to an image.",
            category=ToolCategory.DATA,
            tool_type=ToolType.CLI,
            cli_command="exiftool",
            url="https://exiftool.org/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["exif", "cli", "metadata"],
        ),
        ToolInfo(
            name="Overpass Turbo",
            description="A tool that allows you to query the open street map database to create your own map.",
            category=ToolCategory.GEOGRAPHIC,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://overpass-turbo.eu/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["openstreetmap", "query", "map"],
        ),
        ToolInfo(
            name="Live UA Map",
            description="A tool that collects maps and events happening around the world every day. Useful for tracking major global news events.",
            category=ToolCategory.GEOGRAPHIC,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://liveuamap.com/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["news", "map", "events", "tracking"],
        ),
        ToolInfo(
            name="Open Infrastructure Map",
            description="A tool that allows you to find key infrastructure in one publicly available map. Helpful for geolocation tasks.",
            category=ToolCategory.GEOGRAPHIC,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://openinframap.org/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["infrastructure", "map", "geolocation"],
        ),
        ToolInfo(
            name="Who Posted What?",
            description="A tool that allows you to find out what was uploaded to Facebook on one specific date.",
            category=ToolCategory.SOCIAL_MEDIA,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://whopostedwhat.com/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["facebook", "date search", "social media"],
        ),
        ToolInfo(
            name="Open Measures",
            description="A tool that lets you track trends on platforms like Telegram, TikTok, VK, and more.",
            category=ToolCategory.SOCIAL_MEDIA,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://public.openmeasures.io/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["trends", "telegram", "tiktok", "vk"],
        ),
        ToolInfo(
            name="Carnet AI",
            description="An AI tool that allows you to upload an image and identify the car model.",
            category=ToolCategory.SEARCH,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://carnet.ai/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["ai", "car recognition", "vehicle"],
        ),
        ToolInfo(
            name="Suncalc",
            description="A tool that makes calculating the time based on the angle of shadows easy.",
            category=ToolCategory.GEOGRAPHIC,
            tool_type=ToolType.ONLINE_SERVICE,
            url="https://www.suncalc.org/",
            status=ToolStatus.NOT_INSTALLED,
            tags=["sun", "shadows", "time calculation", "geolocation"],
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

    for tool in predefined_tools:
        existing = await repo.get_by_name(tool.name)
        if not existing:
            await repo.create(tool)
        else:
            await repo.update(tool)

    print(f"Database initialized with {len(predefined_tools)} tools")


async def main():
    config = AppConfig()
    config.database.path = "osint_toolkit.db"
    container = create_container(config)

    await initialize_database(container)

    app = OSINTToolkitApp(
        tool_repository=container.resolve(IToolRepository),
        plugin_registry=None,
        search_service=None,
        report_generator=None,
        cli_detector=None,
        config={},
    )

    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())