from __future__ import annotations

from enum import Enum


class ToolCategory(Enum):
    GEOGRAPHIC = "geographic"
    SOCIAL_MEDIA = "social_media"
    SEARCH = "search"
    DATA = "data"
    NETWORK = "network"
    CRYPTO = "crypto"
    MALWARE = "malware"
    VULNERABILITY = "vulnerability"
    PASSWORD = "password"
    WIRELESS = "wireless"
    WEB = "web"
    FORENSICS = "forensics"
    REPORTING = "reporting"
    OTHER = "other"

    @classmethod
    def from_string(cls, value: str) -> ToolCategory:
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(normalized)
        except ValueError:
            return cls.OTHER


class ToolType(Enum):
    CLI = "cli"
    ONLINE_SERVICE = "online_service"
    API = "api"
    FRAMEWORK = "framework"
    BROWSER_EXTENSION = "browser_extension"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"


class ToolStatus(Enum):
    AVAILABLE = "available"
    INSTALLED = "installed"
    DISABLED = "disabled"
    NOT_INSTALLED = "not_installed"
    OUTDATED = "outdated"
    ERROR = "error"