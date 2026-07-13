"""Domain-level enumerations.

These are pure vocabulary types with no dependency on any other layer.
Clean Architecture rule: domain/ imports nothing from application/,
infrastructure/, presentation/, or plugins/.
"""

from __future__ import annotations

from enum import Enum, unique


@unique
class Category(str, Enum):
    """Canonical classification of OSINT tools.

    Values map 1:1 onto the 20 sections of the source catalogue
    (osint_tools.md) so that automatic classification during plugin
    generation is a direct lookup rather than a heuristic.
    """

    WHOIS = "whois"
    IP_GEOLOCATION = "ip_geolocation"
    DNS_RECON = "dns_recon"
    SSL_TLS = "ssl_tls"
    EMAIL_INTEL = "email_intel"
    PEOPLE_USERNAME = "people_username"
    SOCIAL_MEDIA = "social_media"
    IMAGE_METADATA = "image_metadata"
    SEARCH_ENGINES = "search_engines"
    WEBSITE_ANALYSIS = "website_analysis"
    BREACH_DATABASES = "breach_databases"
    GOOGLE_DORKS = "google_dorks"
    PASTEBIN = "pastebin"
    DOMAIN_IP_COMBO = "domain_ip_combo"
    CLI_UTILITIES = "cli_utilities"
    OSINT_FRAMEWORKS = "osint_frameworks"
    THREAT_INTEL = "threat_intel"
    MAPS_GEOSPATIAL = "maps_geospatial"
    DATASETS_ARCHIVES = "datasets_archives"
    BROWSER_EXTENSIONS = "browser_extensions"

    @property
    def label_fa(self) -> str:
        """Persian display label for the TUI (dashboard headers, filters)."""
        return _CATEGORY_LABELS_FA[self]


_CATEGORY_LABELS_FA: dict[Category, str] = {
    Category.WHOIS: "WHOIS — اطلاعات ثبت دامنه",
    Category.IP_GEOLOCATION: "IP و موقعیت جغرافیایی",
    Category.DNS_RECON: "DNS — رکوردها و زیردامنه‌ها",
    Category.SSL_TLS: "SSL/TLS — گواهی‌های امنیتی",
    Category.EMAIL_INTEL: "ایمیل — پیدا کردن و بررسی",
    Category.PEOPLE_USERNAME: "افراد — نام کاربری",
    Category.SOCIAL_MEDIA: "شبکه‌های اجتماعی",
    Category.IMAGE_METADATA: "عکس — جستجوی معکوس و Metadata",
    Category.SEARCH_ENGINES: "موتورهای جستجو",
    Category.WEBSITE_ANALYSIS: "تحلیل وبسایت",
    Category.BREACH_DATABASES: "نشت اطلاعات و دیتابیس‌های هک",
    Category.GOOGLE_DORKS: "Google Dorks",
    Category.PASTEBIN: "Pastebin و اشتراک‌گذاری متن",
    Category.DOMAIN_IP_COMBO: "دامنه و IP — ترکیبی",
    Category.CLI_UTILITIES: "ابزارهای خط فرمان",
    Category.OSINT_FRAMEWORKS: "فریم‌ورک‌های جامع OSINT",
    Category.THREAT_INTEL: "تهدیدات و امنیت سایبری",
    Category.MAPS_GEOSPATIAL: "نقشه و مکان",
    Category.DATASETS_ARCHIVES: "دیتاست‌ها و آرشیوها",
    Category.BROWSER_EXTENSIONS: "افزونه‌های مرورگر",
}


@unique
class ToolType(str, Enum):
    """How a plugin is invoked / what kind of asset it wraps."""

    CLI = "cli"                    # local executable, detected via PATH
    ONLINE_SERVICE = "online"      # browser-based web tool, no formal API
    API_SERVICE = "api"            # has a documented HTTP API (may need a key)
    FRAMEWORK = "framework"        # multi-module platform (SpiderFoot, Maltego...)
    BROWSER_EXTENSION = "browser_extension"


@unique
class PluginStatus(str, Enum):
    """Runtime availability of a plugin, computed at discovery/startup time."""

    AVAILABLE = "available"        # CLI binary found on PATH / reachable
    UNAVAILABLE = "unavailable"    # CLI binary missing -> disabled, not deleted
    NOT_APPLICABLE = "n_a"         # online/API/framework tools: no local binary to check
    ERROR = "error"                # last invocation failed


@unique
class OutputFormat(str, Enum):
    """Formats a plugin's parsed output can be rendered/exported as."""

    TEXT = "text"
    JSON = "json"
    TABLE = "table"
    MARKDOWN = "markdown"
    HTML = "html"
