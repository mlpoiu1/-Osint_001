from __future__ import annotations

from osint_toolkit.config.settings import AppConfig
from osint_toolkit.config.dependencies import create_container
from osint_toolkit.domain.interfaces import IToolRepository


TOOL_URLS = {
    "ShadowMap": "https://app.shadowmap.org/?lat=51.50918&lng=-0.10267&zoom=15.00&azimuth=0.00000&basemap=map&elevation=nextzen&f=29.0&hud=true&polar=0.52360&time=1728388751509&vq=2",
    "TGStat": "https://tgstat.com/",
    "What's My Name App": "https://whatsmyname.app/",
    "Search4Faces": "https://search4faces.com/en/index.html",
    "PimEyes": "https://pimeyes.com/en",
    "GeoGuesser": "https://chatgpt.com/g/g-CJcEkxOw8-geo-guesser",
    "Google Earth Pro": "https://earth.google.com/intl/earth/versions/#earth-pro",
    "YouTube GeoFind": "https://mattw.io/youtube-geofind/location",
    "GetDayTrends": "https://getdaytrends.com/",
    "Google Image Reverse Search": "https://lens.google/",
    "Search by Image": "https://chromewebstore.google.com/detail/search-by-image/cnojnbdhbhnkbcieeekonklommdnndci?hl=en",
    "Redective": "https://www.redective.com/",
    "Untappd Scraper": "https://brandone.github.io/untappd-scraper-web/",
    "Google Dorks": "https://www.recordedfuture.com/threat-intelligence-101/threat-analysis-techniques/google-dorks",
    "MapChecking CrowdTool": "https://www.mapchecking.com/#bAADAP3VuQ0JV1RJAAACQQehuQ0Le7BJAsm5DQnnoEkCSbkNCBusSQNJuQ0Lb7xJA",
    "Flight Radar 24": "https://www.flightradar24.com/multiview/34.8,27.73/6",
    "Wayback Machine": "https://archive.org/details/tv?q=cats%20and%20dogs",
    "Jimpl": "https://jimpl.com/",
    "Pixel Keeper": "https://pixelpeeper.com/app/01hqb8gcxgfhkbththy5qqygbm",
    "ExifTool": "https://exiftool.org/",
    "Overpass Turbo": "https://overpass-turbo.eu/",
    "Live UA Map": "https://liveuamap.com/",
    "Open Infrastructure Map": "https://openinframap.org/#6.54/20.79/78.415/L,O,P,S,T,W",
    "Who Posted What?": "https://whopostedwhat.com/",
    "Open Measures": "https://public.openmeasures.io/timeline?searchTerm=qanon&startDate=2023-08-16&endDate=2024-02-15&websites=gab&numberOf=10&interval=day&limit=10000&changepoint=false&esquery=content&hostRegex=true",
    "Carnet AI": "https://carnet.ai/",
    "Suncalc": "https://www.suncalc.org/#/27.6936,-97.5195,3/2024.10.19/13:32/1/1",
    "Google Street View": "https://www.google.co.uk/maps/@52.9527203,-1.184662,3a,75y,108.26h,101.52t/data=!3m6!1e1!3m4!1sQZLUJjAiyqlfws9MT9lQFw!2e0!7i13312!",
}


async def update_tool_urls():
    config = AppConfig()
    config.database.path = "osint_toolkit.db"
    container = create_container(config)
    repo = container.resolve(IToolRepository)

    updated = 0
    not_found = 0

    for name, url in TOOL_URLS.items():
        tool = await repo.get_by_name(name)
        if tool:
            tool.url = url
            await repo.update(tool)
            updated += 1
            print(f"✅ Updated: {name}")
        else:
            not_found += 1
            print(f"❌ Not found: {name}")

    print(f"\nUpdated: {updated}, Not found: {not_found}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(update_tool_urls())