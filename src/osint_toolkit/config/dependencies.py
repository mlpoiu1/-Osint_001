from __future__ import annotations

from osint_toolkit.config.settings import AppConfig
from osint_toolkit.infrastructure.di.container import ServiceContainer
from osint_toolkit.infrastructure.storage.sqlite import SQLiteToolRepository
from osint_toolkit.infrastructure.plugins.registry import PluginRegistry
from osint_toolkit.infrastructure.plugins.factory import PluginFactory
from osint_toolkit.infrastructure.cli.detector import CLIDetector
from osint_toolkit.domain.interfaces import (
    IToolRepository,
    IPluginRegistry,
    IPluginFactory,
    ICLIDetector,
)


def create_container(config: AppConfig | None = None) -> ServiceContainer:
    container = ServiceContainer()

    if config is None:
        config = AppConfig()

    container.register_instance(AppConfig, config)

    container.register(
        IToolRepository,
        lambda: SQLiteToolRepository(config.database.path),
        singleton=True,
    )

    container.register(IPluginRegistry, PluginRegistry, singleton=True)
    container.register(IPluginFactory, PluginFactory, singleton=True)
    container.register(ICLIDetector, CLIDetector, singleton=True)

    return container